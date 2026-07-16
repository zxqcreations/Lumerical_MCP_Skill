# Lumerical Skill — Complete Reference Guide

> The Skill is installed at `~/.claude/skills/lumerical.md`
> Invoked via `/lumerical` in Claude Code

## What the Skill Provides

The Skill gives Claude Code context about:
1. All 56 MCP tools and their purposes
2. Common simulation workflow patterns with step-by-step examples
3. Product-specific commands and when to use each product
4. Best practices for photonic simulation automation
5. Troubleshooting guidance

## Skill Structure

```markdown
# Lumerical Photonic Simulation Skill

## Description
[One-line purpose statement]

## When to Use
[Decision triggers for invoking the skill]

## MCP Tools Available
[Full tool catalog organized by domain]

## Workflow Patterns
[Common task patterns with code examples]

## Best Practices
[10 best practices for simulation workflow]

## Product-Specific Commands
[FDTD / MODE / DEVICE / INTERCONNECT command references]

## Troubleshooting
[Common error scenarios and solutions]
```

## Workflow Patterns (Detailed)

### Pattern 1: New FDTD Simulation from Scratch
```
Objective: Create a waveguide transmission simulation
Products: FDTD
Typical duration: 5-10 min setup, 1-60 min simulation

Steps:
1. lumerical_open("fdtd")
   → Gets session_id for all subsequent calls

2. lumerical_add_solver(session_id, "fdtd", {
     "dimension": 2,
     "simulation_time": 5000e-15,
     "x": 0, "x_span": 4e-6,
     "y": 0, "y_span": 4e-6,
     "mesh_accuracy": 3,
     "auto_shutoff_min": 1e-5,
     "boundary_conditions": {
       "x_min_bc": "PML", "x_max_bc": "PML",
       "y_min_bc": "PML", "y_max_bc": "PML"
     }
   })

3. lumerical_set_global_source(session_id, {
     "wavelength_start": 1.5e-6,
     "wavelength_stop": 1.6e-6,
     "number_of_wavelength_points": 101
   })

4. lumerical_add(session_id, "rect", {
     "name": "waveguide",
     "x": 0, "x_span": 4e-6,
     "y": 0, "y_span": 0.22e-6,
     "z": 0, "z_span": 0.22e-6,
     "material": "Si (Silicon) - Palik"
   })

5. lumerical_add_source(session_id, "mode", {
     "name": "source",
     "injection_axis": "x",
     "x": -1.5e-6,
     "y": 0,
     "mode_selection": "fundamental mode"
   })

6. lumerical_add_monitor(session_id, "power", {
     "name": "transmission",
     "monitor_type": "2D X-normal",
     "x": 1.5e-6
   })

7. lumerical_run(session_id)
   → Wait for simulation completion

8. lumerical_get_result(session_id, "transmission", "T")
   → Returns transmission vs wavelength

9. lumerical_close(session_id)
```

### Pattern 2: MODE Waveguide Mode Analysis
```
Objective: Calculate supported modes of a waveguide
Products: MODE
Duration: <1 minute

1. lumerical_open("mode")
2. lumerical_add_solver(session_id, "fde", {
     "solver_type": "2D X normal",
     "wavelength": 1.55e-6,
     "number_of_trial_modes": 10,
     "search": "max_index"
   })
3. lumerical_add(session_id, "rect", {
     "name": "core", "x_span": 0.5e-6, "y_span": 0.22e-6,
     "material": "Si (Silicon) - Palik"
   })
4. lumerical_add(session_id, "rect", {
     "name": "clad", "x_span": 4e-6, "y_span": 2e-6,
     "material": "SiO2 (Glass) - Palik"
   })
5. lumerical_run(session_id)
6. lumerical_get_var(session_id, "neff")
   → Returns effective indices of all found modes
7. lumerical_close(session_id)
```

### Pattern 3: MODE EME Propagation
```
Objective: Simulate light propagation through a varying waveguide
Products: MODE (EME solver)

1. lumerical_open("mode")
2. lumerical_add_solver(session_id, "eme", {
     "wavelength": 1.55e-6,
     "number_of_modes": 5,
     "x": 0, "x_span": 10e-6,
     "y": 0, "y_span": 2e-6,
     "z": 0, "z_span": 2e-6
   })
3. lumerical_eval(session_id, """
   # Define waveguide sections
   # Setup ports at input/output
   # Define cell groups for EME
   """)
4. lumerical_run(session_id)
5. lumerical_get_result(session_id, "port_2", "S")
   → S-parameters
```

### Pattern 4: Parameter Sweep for Waveguide Width
```
Objective: Find optimal waveguide width for minimum loss
Products: FDTD or MODE
Duration: N × simulation time

1. lumerical_open("fdtd")
2. lumerical_load(session_id, "waveguide.fsp")
3. lumerical_add_sweep(session_id, "width_sweep", {
     "parameters": ["width"],
     "ranges": [[0.3e-6, 0.8e-6, 11]],
     "results": ["transmission::T"]
   })
4. lumerical_run_sweep(session_id, "width_sweep")
5. result = lumerical_get_sweep_result(session_id, "width_sweep", "T")
   → 11 transmission values, one per width
```

### Pattern 5: Far-Field Radiation Pattern
```
Objective: Calculate far-field from near-field monitor
Products: FDTD

1. lumerical_open("fdtd")
2. lumerical_load(session_id, "project.fsp")
3. lumerical_run(session_id)
4. lumerical_farfield(session_id, "near_field_monitor", "3d")
   → Far-field E(theta, phi) data
5. # Or 2D projection at specific angles
6. lumerical_farfield(session_id, "near_field_monitor", "polar")
```

### Pattern 6: Using Direct Script for Complex Setup
```
Objective: Execute a complete LSF script for complex geometry
Products: Any

1. lumerical_open("fdtd")
2. lumerical_eval(session_id, """
   # Full Lumerical script
   newproject;
   addfdtd;
   set("dimension", 3);
   set("x span", 4e-6);
   set("y span", 4e-6);
   set("z span", 4e-6);

   # Ring resonator geometry
   addring;
   set("name", "ring");
   set("x", 0); set("y", 0); set("z", 0);
   set("inner radius", 2.5e-6);
   set("outer radius", 3.0e-6);
   set("material", "Si (Silicon) - Palik");

   # Bus waveguide
   addrect;
   set("name", "bus");
   set("x span", 6e-6);
   set("y span", 0.3e-6);
   set("z span", 0.3e-6);

   # Source and monitors...
   run;
   """)
3. lumerical_get_result(session_id, "drop", "T")
```

### Pattern 7: Material Database Exploration
```
Objective: Explore material optical properties
Products: FDTD or MODE
Duration: Seconds (no simulation needed)

1. lumerical_open("fdtd")
2. lumerical_get_index(session_id, "Au (Gold) - Johnson and Christy", 3e14)
   → Returns complex n,k at 300 THz (~1000 nm)

3. lumerical_get_transmission(session_id,
     "Au (Gold) - Johnson and Christy",
     thickness=50e-9,
     f_min=1e14, f_max=1e15, nf=200
   )
   → Returns T(λ) for 50nm gold film

4. lumerical_add_material(session_id, "Custom Polymer", {
     "index": 1.48,
     "color": "#FF6600"
   })
   → Creates custom dielectric material

5. lumerical_close(session_id)
```

## Product Selection Guide

| Task | Product | Reason |
|------|---------|--------|
| 3D/2D EM wave propagation | FDTD | Most general, broadband |
| Waveguide mode calculation | MODE (FDE) | Dedicated eigensolver |
| Propagation in varying cross-section | MODE (EME) | Much faster than FDTD |
| Broadband planar structures | MODE (varFDTD) | Reduced 2.5D simulation |
| Photonic circuit simulation | INTERCONNECT | S-parameter based, fast |
| Semiconductor charge transport | DEVICE | Drift-diffusion solver |
| Thermal analysis | DEVICE | Heat transport solver |
| Coupled electro-thermal | DEVICE | Multiphysics coupling |
| Inverse design / optimization | FDTD + lumopt2 | Adjoint-based gradient |

## Key Material Names (Lumerical Database)

```
"Si (Silicon) - Palik"                    → Silicon, 0.2-2 μm
"SiO2 (Glass) - Palik"                   → Fused silica
"Si3N4 (Silicon Nitride) - Phillip"      → SiN
"Au (Gold) - Johnson and Christy"        → Gold, 0.2-2 μm
"Ag (Silver) - Johnson and Christy"      → Silver
"Al (Aluminum) - Palik"                  → Aluminum
"Cu (Copper) - Palik"                    → Copper
"Ti (Titanium) - Palik"                  → Titanium
"TiO2 (Titanium Dioxide) - Devore"       → TiO2
"InP (Indium Phosphide) - Palik"         → InP
"GaAs (Gallium Arsenide) - Palik"        → GaAs
"Al2O3 (Alumina) - Palik"               → Sapphire/Alumina
"H2O (Water) - Palik"                    → Water
"Air"                                    → n = 1.0
"etch"                                   → Placeholder for etching
```

## Troubleshooting Checklist

### Session Issues
- [ ] Is LUMERICAL_HOME set? Run `lumerical_open` first to check.
- [ ] Is the Lumerical GUI license valid?
- [ ] Are there leftover sessions? Run `lumerical_close_all`.
- [ ] Is the product name correct? Must be: fdtd, mode, device, interconnect.

### Simulation Issues
- [ ] Does the solver region encompass all geometry?
- [ ] Are the mesh settings appropriate for feature sizes? (At least 8-10 cells per wavelength)
- [ ] Are boundary conditions appropriate? (PML for radiating, periodic for infinite arrays)
- [ ] Is the simulation time long enough? Check auto_shutoff settings.
- [ ] Are sources configured with the correct wavelength range?

### Result Issues
- [ ] Did the simulation actually run? Check `lumerical_run` return.
- [ ] Is the monitor positioned to capture the fields of interest?
- [ ] Does the monitor's frequency range cover the source bandwidth?
- [ ] For S-parameters: are mode expansion monitors properly aligned with ports?

### Performance
- [ ] Is mesh_accuracy ≤ 5? Higher values exponentially increase runtime.
- [ ] Can you reduce simulation volume? Trim unused space.
- [ ] Use symmetry boundaries when applicable (PEC/PMC for symmetric problems).
- [ ] For sweeps: use `lumerical_run_parallel` for multi-core execution.
- [ ] For large sweeps: consider using Lumerical's built-in job manager.

## Common LSF Script Patterns (for lumerical_eval)

### Select and modify an object
```lua
select("waveguide");
set("x span", 1e-6);
set("material", "Si (Silicon) - Palik");
```

### Create variables and use them
```lua
wavelength = 1.55e-6;
frequency = c / wavelength;
width = 0.5e-6;
```

### Loop over parameter
```lua
for (i=1:10) {
  select("wg");
  set("width", 0.3e-6 + (i-1) * 0.05e-6);
  run;
  T = getresult("monitor", "T");
  # process result
}
```

### Access complex field data
```lua
E = getresult("profile", "E");
Ex = getresult("profile", "Ex");
Ey = getresult("profile", "Ey");
Ez = getresult("profile", "Ez");
# Each is complex: real(E), imag(E), abs(E), angle(E)
```

### Get S-parameters from mode expansion
```lua
# After simulation:
S = getresult("expansion_monitor", "S");
# S is an NxN complex matrix for N ports
```
