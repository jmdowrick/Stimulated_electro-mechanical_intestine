from dolfinx import io, plot
from mpi4py import MPI
import pyvista as pv

mesh = io.gmsh.read_from_msh("../assets/mesh/tube.msh", MPI.COMM_WORLD)

topology, cell_types, geometry = plot.vtk_mesh(mesh.mesh, 2)
grid = pv.UnstructuredGrid(topology, cell_types, geometry)

p = pv.Plotter()
p.add_mesh(grid, show_edges=True)
p.view_isometric()
p.show_axes()
p.show()
