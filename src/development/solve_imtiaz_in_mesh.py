from mpi4py import MPI
import dolfinx
import shutil
import dolfinx.fem.petsc
import ufl
import numpy as np
from src.assets.cellml import imtiaz_2002d_noTstart_COR as model

# --- Mesh ---
mesh_data = dolfinx.io.gmsh.read_from_msh("../assets/mesh/tube.msh", MPI.COMM_WORLD)
mesh = mesh_data.mesh

# --- Function space ---
V = dolfinx.fem.functionspace(mesh, ("P", 1))

# --- Functions ---
v_h = dolfinx.fem.Function(V)
v_n = dolfinx.fem.Function(V)
u = ufl.TrialFunction(V)
phi = ufl.TestFunction(V)

v_index = model.state_index("V_m")
v_h.x.array[:] = model.init_state_values()[v_index]
v_n.x.array[:] = model.init_state_values()[v_index]

# --- ODE states and parameters (per node) ---
n_nodes = V.dofmap.index_map.size_local
states = np.tile(model.init_state_values(), (n_nodes, 1))
parameters = np.tile(model.init_parameter_values(), (n_nodes, 1))

# --- Weak form ---
dt = 0.1
C_m = 1.0
M = 0.01

dx = ufl.Measure("dx", domain=mesh)
I_ion = dolfinx.fem.Function(V)

a = C_m * ufl.inner(u, phi) * dx + dt * M * ufl.inner(ufl.grad(u), ufl.grad(phi)) * dx
L = C_m * ufl.inner(v_n, phi) * dx + dt * ufl.inner(I_ion, phi) * dx

problem = dolfinx.fem.petsc.LinearProblem(a, L, u=v_h,
                                          petsc_options_prefix="test",
                                          petsc_options={"ksp_type": "cg", "pc_type": "hypre"})

# --- Output ---
shutil.rmtree("imtiaz_mesh.bp", ignore_errors=True)
vtx = dolfinx.io.VTXWriter(MPI.COMM_WORLD, "imtiaz_mesh.bp", [v_h], engine="BP4")

# --- Time loop ---
T = 10000.0
t = 0.0
i = 0

while t < T:
    # Step 1: ODE step
    states[:, v_index] = v_n.x.array
    v_old = v_n.x.array.copy()

    for node in range(n_nodes):
        states[node, :] = model.generalized_rush_larsen(
            states[node, :], t, dt, parameters[node, :]
        )

    I_ion.x.array[:] = (states[:, v_index] - v_old) / dt

    # Step 2: PDE step
    problem.solve()
    v_n.x.array[:] = v_h.x.array
    states[:, v_index] = v_h.x.array

    if i % 1000 == 0:
        print(f"t={t:.1f} ms  V_max={v_h.x.array.max():.2f}  V_min={v_h.x.array.min():.2f}")
        vtx.write(t)

    t += dt
    i += 1

vtx.close()
