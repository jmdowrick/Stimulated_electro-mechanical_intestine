from mpi4py import MPI
import dolfinx
import shutil
import dolfinx.fem.petsc
import basix
import basix.ufl
import ufl
import numpy as np
from petsc4py import PETSc
from src.assets.cellml import imtiaz_2002d_noTstart_COR as model
import os

os.environ["NUMBA_CACHE_DIR"] = f"/tmp/numba_rank_{MPI.COMM_WORLD.rank}"
import numba
from datetime import datetime

comm = MPI.COMM_WORLD

# --- Mesh ---
mesh_data = dolfinx.io.gmsh.read_from_msh("../assets/mesh/tube_refined.msh", comm)
mesh = mesh_data.mesh

# --- Function spaces ---
element = basix.ufl.element("Lagrange", mesh.basix_cell(), 1)
mixed_element = basix.ufl.mixed_element([element, element])
W = dolfinx.fem.functionspace(mesh, mixed_element)

# Scalar space for ODE and V_m_star
V_m_space = dolfinx.fem.functionspace(mesh, element)

# --- Boundary condition ---
#V_m_collapsed, V_m_dofs = W.sub(0).collapse()
V_e_collapsed, _ = W.sub(1).collapse()

dofs_W, dofs_collapsed = dolfinx.fem.locate_dofs_geometrical(
    (W.sub(1), V_e_collapsed),
    lambda x: np.isclose(x[0], 0.0)
)
bc = dolfinx.fem.dirichletbc(
    dolfinx.fem.Constant(mesh, PETSc.ScalarType(0.0)),
    dofs_W,
    W.sub(1)
)

# --- Functions ---
w_h = dolfinx.fem.Function(W)

V_m_star = dolfinx.fem.Function(V_m_space)
V_m_n = dolfinx.fem.Function(V_m_space)

(V_m, V_e) = ufl.TrialFunctions(W)
(phi_m, phi_e) = ufl.TestFunctions(W)

# Initialise
v_idx = model.state_index("V_m")
V_m0 = model.init_state_values()[v_idx]
w_h.sub(0).x.array[:] = V_m0
w_h.sub(1).x.array[:] = 0.0
w_h.x.scatter_forward()

# w_n.x.array[:] = w_h.x.array
V_m_n.x.array[:] = V_m0

# --- ODE states and parameters ---
imap = V_m_space.dofmap.index_map
n_nodes = imap.size_local

states = np.tile(model.init_state_values(), (n_nodes, 1))
parameters = np.tile(model.init_parameter_values(), (n_nodes, 1))

# Spatially varying beta
beta_func = dolfinx.fem.Function(V_m_space)
beta_func.interpolate(lambda x: 0.000975 - 0.0001 * (x[2] / 100))
parameters[:, model.parameter_index("beta_")] = beta_func.x.array[:n_nodes]

# Stimulator
I_stim_idx = model.parameter_index("I_stim")
stim_amp = 100
stim_start = 10000
stim_duration = 200
stim_period = 18000

local_coords = V_m_space.tabulate_dof_coordinates()[:n_nodes]
stim_mask = (local_coords[:, 2] >= 50) & (local_coords[:, 2] <= 55)

# --- Weak form ---
dt = 1.0
C_m = 1.0
sigma_i = dolfinx.fem.Constant(mesh, 0.1)
sigma_e = dolfinx.fem.Constant(mesh, 0.2)
stim_start_step = int(stim_start / dt)
stim_duration_step = int(stim_duration / dt)
stim_period_step = int(stim_period / dt)

dx = ufl.Measure("dx", domain=mesh)

a = (
        C_m * ufl.inner(V_m, phi_m) * dx
        + dt * ufl.inner(sigma_i * ufl.grad(V_m + V_e), ufl.grad(phi_m)) * dx
        + dt * ufl.inner(sigma_i * ufl.grad(V_m + V_e), ufl.grad(phi_e)) * dx
        + dt * ufl.inner(sigma_e * ufl.grad(V_e), ufl.grad(phi_e)) * dx
)

L = C_m * ufl.inner(V_m_star, phi_m) * dx

problem = dolfinx.fem.petsc.LinearProblem(
    a, L, u=w_h, bcs=[bc],
    petsc_options_prefix="bidomain",
    petsc_options={"ksp_type": "gmres", "pc_type": "hypre"},
)

# --- Output ---
run_id = datetime.now().strftime("%Y%m%d %H%M%S")
run_id = comm.bcast(run_id, root=0)
output_path = f"../results/{run_id} bidomain.bp"

V_m_out = dolfinx.fem.Function(V_m_space, name="V_m")
V_e_out = dolfinx.fem.Function(V_m_space, name="V_e")

if comm.rank == 0:
    shutil.rmtree(output_path, ignore_errors=True)
comm.Barrier()

vtx = dolfinx.io.VTXWriter(comm, output_path, [V_m_out, V_e_out], engine="BP4")

# --- Numba ---
jit_rush_larsen = numba.njit(model.generalized_rush_larsen)

@numba.njit
def solve_all_odes(states, t, dt, parameters, n_nodes):
    for node in range(n_nodes):
        states[node, :] = jit_rush_larsen(states[node, :], t, dt, parameters[node, :])
    return states

# --- Time stepping ---
T = 20000.0
t = 0.0
i = 0

while t < T:
    # Stimulation
    if i >= stim_start_step and (i - stim_start_step) % stim_period_step <= stim_duration_step:
        parameters[stim_mask, I_stim_idx] = stim_amp
    else:
        parameters[stim_mask, I_stim_idx] = 0.0

    # ODE step
    states[:, v_idx] = V_m_n.x.array[:n_nodes]
    states = solve_all_odes(states, t, dt, parameters, n_nodes)

    V_m_star.x.array[:n_nodes] = states[:, v_idx]
    V_m_star.x.scatter_forward()

    # PDE step
    problem.solve()

    V_m_n.interpolate(w_h.sub(0))
    V_m_n.x.scatter_forward()

    states[:, v_idx] = V_m_n.x.array[:n_nodes]

    if i % 100 == 0:
        global_max = comm.allreduce(V_m_n.x.array.max(), op=MPI.MAX)
        global_min = comm.allreduce(V_m_n.x.array.min(), op=MPI.MIN)
        if comm.rank == 0:
            print(f"t={t:.1f} ms  V_max={global_max:.2f}  V_min={global_min:.2f}")
        V_m_out.interpolate(w_h.sub(0))
        V_e_out.interpolate(w_h.sub(1))

        V_m_out.x.scatter_forward()
        V_e_out.x.scatter_forward()
        vtx.write(t)

    t += dt
    i += 1

vtx.close()
