from mpi4py import MPI
import dolfinx
import shutil
import dolfinx.fem.petsc
import ufl
import numpy as np
from src.assets.cellml import imtiaz_2002d_noTstart_COR as model

import os
os.environ["NUMBA_CACHE_DIR"] = f"/tmp/numba_rank_{MPI.COMM_WORLD.rank}"
import numba
from datetime import datetime

# --- Mesh ---
mesh_data = dolfinx.io.gmsh.read_from_msh("./assets/mesh/tube_refined.msh", MPI.COMM_WORLD)
mesh = mesh_data.mesh

# --- Function space ---
V = dolfinx.fem.functionspace(mesh, ("P", 1))

# --- Functions ---
v_h = dolfinx.fem.Function(V)
v_n = dolfinx.fem.Function(V)
v_star = dolfinx.fem.Function(V)
u = ufl.TrialFunction(V)
phi = ufl.TestFunction(V)

v_index = model.state_index("V_m")
v_h.x.array[:] = model.init_state_values()[v_index]
v_n.x.array[:] = model.init_state_values()[v_index]

# --- ODE states and parameters ---
n_nodes = V.dofmap.index_map.size_local
states = np.tile(model.init_state_values(), (n_nodes, 1))
parameters = np.tile(model.init_parameter_values(), (n_nodes, 1))

# beta - sets rate of depolarisation
beta_func = dolfinx.fem.Function(V)
beta_func.interpolate(lambda x: 0.000975 - 0.0001 * (x[2] / 100))

beta_idx = model.parameter_index("beta_")
parameters[:, beta_idx] = beta_func.x.array

# stimulator
I_stim_idx = model.parameter_index("I_stim")
stim_amp = 100
stim_start = 20000
stim_duration = 200
stim_period = 18000

local_coords = V.tabulate_dof_coordinates()[:n_nodes]
stim_mask = (local_coords[:, 2] >= 50) & (local_coords[:, 2] <= 55)

# --- Weak form ---
dt = 1
C_m = 1
M = 1

dx = ufl.Measure("dx", domain=mesh)

a = C_m * ufl.inner(u, phi) * dx + dt * M * ufl.inner(ufl.grad(u), ufl.grad(phi)) * dx
L = C_m * ufl.inner(v_star, phi) * dx

problem = dolfinx.fem.petsc.LinearProblem(a, L, u=v_h,
                                          petsc_options_prefix="test",
                                          petsc_options={"ksp_type": "cg", "pc_type": "hypre"})

# --- Output ---
run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
run_id = MPI.COMM_WORLD.bcast(run_id, root=0)
output_path = f"../results/electro_{run_id}.bp"
if MPI.COMM_WORLD.rank == 0:
    shutil.rmtree(output_path, ignore_errors=True)
MPI.COMM_WORLD.Barrier()
vtx = dolfinx.io.VTXWriter(MPI.COMM_WORLD, output_path, [v_h], engine="BP4")

# --- Time loop ---
T = 50000.0
t = 0.0
i = 0

jit_rush_larsen = numba.njit(model.generalized_rush_larsen)

@numba.njit
def solve_all_odes(states, t, dt, parameters, n_nodes):
    for node in range(n_nodes):
        states[node, :] = jit_rush_larsen(
            states[node, :], t, dt, parameters[node, :]
        )
    return states

while t < T:
    # Stimulator
    if t >= stim_start and (t - stim_start) % stim_period <= stim_duration:
        parameters[stim_mask, I_stim_idx] = stim_amp
    else:
        parameters[stim_mask, I_stim_idx] = 0.0

    # ODE step
    v_old = v_n.x.array.copy()
    states[:, v_index] = v_old

    states = solve_all_odes(states, t, dt, parameters, n_nodes)

    v_star.x.array[:] = states[:, v_index]
    v_star.x.scatter_forward()

    # PDE step
    problem.solve()
    v_n.x.array[:] = v_h.x.array
    states[:, v_index] = v_h.x.array

    if i % 100 == 0:
        global_max = MPI.COMM_WORLD.allreduce(v_h.x.array.max(), op=MPI.MAX)
        global_min = MPI.COMM_WORLD.allreduce(v_h.x.array.min(), op=MPI.MIN)
        if MPI.COMM_WORLD.rank == 0:
            print(f"t={t:.1f} ms  V_max={global_max:.2f}  V_min={global_min:.2f}")
        vtx.write(t)

    t += dt
    i += 1

vtx.close()
