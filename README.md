# Bidomain Electrophysiology–Mechanics Simulation

A coupled bidomain electrophysiology and mechanical model of smooth muscle tissue, implemented using [FEniCSx](https://fenicsproject.org/) (DOLFINx). The model simulates transmembrane and extracellular potentials, along with active-tension-driven radial contraction within a tubular mesh.

---

## Overview

The simulation solves the bidomain equations on a 3D tubular mesh, coupled to:

- **Cellular electrophysiology** — ODEs from the [Imtiaz 2002](https://doi.org/10.1529/biophysj.102.026914) ICC model.
- **Active mechanics** — intracellular Ca<sup>2+</sup>  concentration drives active tension ([Du et al. 2011](https://doi.org/10.1109/TBME.2011.2166155), which is used to compute radial strain and diameter change along the tube.

---

## Repository Structure (Main Items)

```
.
├── assets/
│   └── mesh/
│       └── tube_refined.msh        # Gmsh mesh file
├── src/
│   └── assets/
│       └── cellml/
│           └── imtiaz_2002d_noTstart_COR.py   # CellML-derived ODE model
├── results/                         # Simulation output (auto-created)
├── bidomain_ephys_mechanical.py     # Main simulation script
├── environment.yml                  # Conda environment specification
└── README.md
```

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/jmdowrick/Stimulated_electro-mechanical_intestine.git
cd Stimulated_electro-mechanical_intestine
```

### 2. Create the Conda Environment

The environment requires [conda](https://docs.conda.io/en/latest/) or [mamba](https://mamba.readthedocs.io/) (recommended for faster solving).

**Using mamba (recommended):**
```bash
mamba env create -f environment.yml
```

**Using conda:**
```bash
conda env create -f environment.yml
```

This will create an environment named `fenicsx-beat-env` with all required dependencies.

### 3. Activate the Environment

```bash
conda activate fenicsx-beat-env
```

---

## Running the Simulation

### Serial

```bash
python bidomain_ephys_mechanical.py
```

### Parallel (MPI) - not functional currently

```bash
mpirun -n <N> python bidomain_ephys_mechanical.py
```

Replace `<N>` with the number of MPI processes (e.g., `4`).

> **Note:** Ensure the mesh file `assets/mesh/tube_refined.msh` exists before running. The `results/` directory will be created automatically.

---

## Configuration

Key simulation parameters are set near the top of `bidomain_ephys_mechanical.py`:

| Parameter | Default | Description |
|---|---|---|
| `dt` | `1.0` ms | Time step |
| `T` | `10000.0` ms | Total simulation time |
| `C_m` | `1.0` µF/cm<sup>2</sup> | Membrane capacitance |
| `sigma_i` | `0.1` S/m | Intracellular conductivity |
| `sigma_e` | `0.2` S/m | Extracellular conductivity |
| `stim_amp` | `100` µA/cm<sup>2</sup>  | Stimulus amplitude |
| `stim_start` | `10000` ms | Stimulus start time |
| `stim_duration` | `200` ms | Stimulus duration |
| `stim_period` | `18000` ms | Stimulus period |
| `D0` | `2.5` mm | Initial tube diameter |
| `k_passive` | `0.2` | Passive stiffness coefficient |

The stimulus is applied to nodes with z-coordinate between 50 and 55 mm. Conductivity `beta_` varies spatially along z to ensure propagation.

---

## Output

Results are written to `results/<timestamp> bidomain.bp` in ADIOS2 BP4 format every 100 time steps. The output contains three fields:

- `V_m` — transmembrane potential (mV)
- `V_e` — extracellular potential (mV)
- `diameter` — local tube diameter (mm)

Output can be visualised with [ParaView](https://www.paraview.org/) (v5.10+ with ADIOS2 support) or [PyVista](https://pyvista.org/).

---

### Visualising in ParaView
 
Because `diameter` is stored as a scalar field, a few steps are needed to warp the mesh geometry to reflect the physical contraction.
 
#### Step 1 — Import the ADIOS2 output
 
Open the `.bp` folder via **File > Open** and select the `.bp` results folder. Click **Apply** in the Properties panel (lower left). Your simulation fields will now be loaded into the workspace. You can set the surface colouring in the same panel — for example, colouring by `V_m` to visualise membrane voltage across the tube.
 
#### Step 2 — Convert scalar diameter to a radial displacement vector
 
The `diameter` field is a scalar. To deform the mesh radially, it must be converted into a 3D displacement vector using the **Calculator** filter:
 
```
Filters > Alphabetical > Calculator
```
 
Enter the following expression:
 
```
((diameter - 2.5) / 2) * (coordsX / sqrt(coordsX^2 + coordsY^2)) * iHat +
((diameter - 2.5) / 2) * (coordsY / sqrt(coordsX^2 + coordsY^2)) * jHat +
0 * kHat
```
 
This computes the radial displacement from the baseline diameter of 2.5 mm and projects it onto the X–Y plane using the normalised radial direction. The z-component is set to zero (no axial displacement).
 
> `diameter` must match the variable name in your output exactly. Assign a name to the result — e.g., `r_disp`.
 
#### Step 3 — Warp the mesh by the displacement vector
 
Apply the **WarpByVector** filter to deform the mesh:
 
```
Filters > Alphabetical > WarpByVector
```
 
In the Properties panel, set **Vectors** to the calculator output from Step 2 (e.g., `r_disp`). The mesh will now deform over time to reflect the simulated contraction. You can independently set the surface colouring to any variable — for example, colouring by `V_m` while the geometry is warped by `diameter` gives a combined electromechanical visualisation.

---

## Converting CellML Models to Python with gotranx
 
The cell model used in this simulation (`imtiaz_2002d_noTstart_COR.py`) is generated from a CellML source file using [gotranx](https://github.com/finsberg/gotranx). Follow the steps below to reproduce this file or to substitute a different CellML model.
 
### Files Generated
 
| File | Description |
|---|---|
| `imtiaz_2002d_noTstart_COR.ode` | Intermediate gotranx ODE format |
| `imtiaz_2002d_noTstart_COR.py` | Pure Python (numpy) solver |
 
### Step-by-Step Workflow
 
#### 1. Install dependencies
 
`gotranx` is already included in the `fenicsx-beat-env` environment. If needed, it can be installed separately:
 
```bash
pip install gotranx
```
 
#### 2. Convert CellML -> ODE
 
```bash
gotranx cellml2ode imtiaz_2002d_noTstart_COR.cellml
```
 
#### 3. Generate Python versions
 
```bash
gotranx ode2py imtiaz_2002d_noTstart_COR.ode \
    --scheme generalized_rush_larsen \
    -o imtiaz_2002d_noTstart_COR.py
```
 
#### 4. Use the Python model directly
 
The generated `.py` file exposes `init_state_values()`, `init_parameter_values()`, and `generalized_rush_larsen()`, which are used directly by the simulation script:
 
```python
import imtiaz_2002d_noTstart_COR as model
import numpy as np
 
init_states = model.init_state_values()
parameters = model.init_parameter_values()
 
# Optional: modify parameters
# parameters[model.parameter_index("I_stim")] = 0.0
 
# Advance one time step
dt = 0.05  # ms
t = 0.0
new_states = model.generalized_rush_larsen(init_states, t, dt, parameters)
```

---

## Dependencies

Core packages (managed via `environment.yml`):

- `fenics-dolfinx` >= 0.10.0
- `petsc` / `petsc4py`
- `mpi4py`
- `numba`
- `numpy`
- `gotranx` (CellML -> Python ODE transpiler)
- `gmsh` (mesh generation)
- `adios2` (BP4 I/O)

## License

[MIT](LICENSE).

## Citation

If you use this code in your research, please cite the underlying models:

- Imtiaz MS et al. (2002). *Inositol 1,4,5-trisphosphate-induced Ca²⁺ oscillations...* Biophys J.
- Du P et al. (2011). *A Preliminary Model of Gastrointestinal Electromechanical Coupling.* Biophys J.
