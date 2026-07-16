# Lumerical Photonic Simulation Skill

## Description

Complete access to Ansys Lumerical photonic simulation and design tools through
the Lumerical MCP server. Supports FDTD (finite-difference time-domain),
MODE (waveguide/fiber mode solvers), DEVICE (multiphysics), and INTERCONNECT
(photonic circuit simulation) with 480+ scripting commands.

## When to Use

Invoke this skill when the user wants to:
- Run photonic/electromagnetic simulations (FDTD, MODE, DEVICE, INTERCONNECT)
- Design photonic devices (waveguides, couplers, resonators, gratings, etc.)
- Analyze simulation results (transmission, field profiles, S-parameters, far-field)
- Create and manipulate simulation geometry
- Work with materials (add, modify, query refractive index)
- Set up parameter sweeps or optimization
- Automate Lumerical workflows via scripting
- Load, modify, or save Lumerical project files (.fsp, .lms, .icp)
- Query the Lumerical scripting command documentation

## MCP Tools Available

All tools are prefixed with `lumerical_` to avoid name collisions. Each tool
requires a `session_id` obtained from `lumerical_open`.

### Session Management
| Tool | Purpose |
|------|---------|
| `lumerical_open` | Start a Lumerical session (fdtd/mode/device/interconnect) |
| `lumerical_close` | Close a specific session |
| `lumerical_list_sessions` | List all active sessions |
| `lumerical_close_all` | Close all sessions |

### Script Execution
| Tool | Purpose |
|------|---------|
| `lumerical_eval` | Execute arbitrary Lumerical script (LSF) |
| `lumerical_get_var` | Get variable value from session |
| `lumerical_set_var` | Set variable in session |
| `lumerical_call` | Call a specific Lumerical command by name |

### Simulation Control
| Tool | Purpose |
|------|---------|
| `lumerical_run` | Run the current simulation |
| `lumerical_load` | Load a project file |
| `lumerical_save` | Save the current project |
| `lumerical_reset` | Reset simulation state |
| `lumerical_switch_to_layout` | Switch to layout mode |
| `lumerical_cd` | Change working directory |

### Geometry & Objects
| Tool | Purpose |
|------|---------|
| `lumerical_add` | Add geometry objects (rect, sphere, circle, etc.) |
| `lumerical_set` | Set selected object property |
| `lumerical_get` | Get selected object property |
| `lumerical_select` | Select object by name |
| `lumerical_select_all` | Select all objects |
| `lumerical_delete` | Delete object |
| `lumerical_copy` | Copy selected object |
| `lumerical_move` | Translate selected object |
| `lumerical_rotate` | Rotate selected object |
| `lumerical_groupscope` | Set/get group scope |

### Materials
| Tool | Purpose |
|------|---------|
| `lumerical_add_material` | Add/modify material |
| `lumerical_set_material` | Set object material |
| `lumerical_get_material` | Get material data |
| `lumerical_get_index` | Get refractive index at frequency |
| `lumerical_import_nk` | Import n,k data from file |
| `lumerical_get_transmission` | Calculate thin film transmission |

### Sources & Monitors
| Tool | Purpose |
|------|---------|
| `lumerical_add_source` | Add source (dipole, mode, gaussian, etc.) |
| `lumerical_add_monitor` | Add monitor (power, profile, index, etc.) |
| `lumerical_set_global_source` | Set global source properties |
| `lumerical_set_global_monitor` | Set global monitor properties |

### Solver Configuration
| Tool | Purpose |
|------|---------|
| `lumerical_add_solver` | Add solver region (FDTD, FDE, EME, etc.) |
| `lumerical_add_mesh` | Add mesh override region |
| `lumerical_add_boundary` | Add boundary condition |
| `lumerical_set_analysis` | Set analysis parameters |

### Results & Analysis
| Tool | Purpose |
|------|---------|
| `lumerical_get_result` | Get simulation result from monitor |
| `lumerical_get_data` | Get raw monitor data |
| `lumerical_get_field` | Get EM field data |
| `lumerical_export_data` | Export data to file |
| `lumerical_farfield` | Calculate far-field projection |
| `lumerical_transmission` | Get transmission results |

### Optimization & Sweeps
| Tool | Purpose |
|------|---------|
| `lumerical_add_sweep` | Create parameter sweep |
| `lumerical_run_sweep` | Run parameter sweep |
| `lumerical_get_sweep_result` | Get sweep results |
| `lumerical_add_optimization` | Set up inverse design optimization |
| `lumerical_run_optimization` | Run optimization |
| `lumerical_run_parallel` | Run jobs in parallel |

### Documentation & Discovery
| Tool | Purpose |
|------|---------|
| `lumerical_list_commands` | List all available commands |
| `lumerical_get_categories` | List command categories |
| `lumerical_get_command_help` | Get detailed command help |
| `lumerical_search_commands` | Search commands by keyword |
| `lumerical_get_script_help` | Get detailed Markdown documentation |
| `lumerical_list_examples` | List available example files |

## Workflow Patterns

### Pattern 1: Creating and Running a Simple FDTD Simulation

```
1. lumerical_open("fdtd") → get session_id
2. lumerical_add_solver(session_id, "fdtd", {"dimension": 2, "x_span": 4e-6, "y_span": 4e-6})
3. lumerical_add(session_id, "rect", {"name": "wg", "x_span": 4e-6, "y_span": 0.5e-6, "material": "Si (Silicon) - Palik"})
4. lumerical_add_source(session_id, "mode", {"injection_axis": "x", "wavelength_start": 1.5e-6, "wavelength_stop": 1.6e-6})
5. lumerical_add_monitor(session_id, "power", {"name": "T", "monitor_type": "2D X-normal"})
6. lumerical_run(session_id)
7. lumerical_get_result(session_id, "T", "T") → analyze transmission
8. lumerical_close(session_id)
```

### Pattern 2: Loading an Existing Project

```
1. lumerical_open("fdtd") → get session_id
2. lumerical_load(session_id, "C:/path/to/project.fsp")
3. lumerical_run(session_id)
4. lumerical_get_result(session_id, "monitor_name", "T")
5. lumerical_close(session_id)
```

### Pattern 3: Material Exploration

```
1. lumerical_open("fdtd") → get session_id
2. lumerical_get_index(session_id, "Au (Gold) - Johnson", frequency=3e14)
3. lumerical_get_transmission(session_id, "Au (Gold) - Johnson", thickness=50e-9)
4. lumerical_close(session_id)
```

### Pattern 4: Using Direct Script Evaluation

```
1. lumerical_open("fdtd") → get session_id
2. lumerical_eval(session_id, """
   addfdtd;
   set("dimension", 3);
   set("x span", 2e-6);
   set("y span", 2e-6);
   set("z span", 2e-6);
   addsphere;
   set("radius", 100e-9);
   set("material", "Au (Gold) - Johnson");
   addtfsf;
   set("wavelength start", 400e-9);
   set("wavelength stop", 800e-9);
   addpower;
   set("name", "absorption");
   run;
   """)
3. lumerical_get_result(session_id, "absorption", "T")
4. lumerical_close(session_id)
```

### Pattern 5: Parameter Sweep

```
1. lumerical_open("fdtd") → get session_id
2. lumerical_load(session_id, "project.fsp")
3. lumerical_add_sweep(session_id, "wg_width_sweep", properties={
     "parameters": ["width"],
     "ranges": [[0.3e-6, 0.8e-6, 11]],
     "results": ["T::transmission"]
   })
4. lumerical_run_sweep(session_id, "wg_width_sweep")
5. lumerical_get_sweep_result(session_id, "wg_width_sweep", "T")
6. lumerical_close(session_id)
```

## Best Practices

1. **Always track sessions**: Keep the session_id from `lumerical_open`. All operations need it.

2. **Close sessions when done**: Use `lumerical_close` or `lumerical_close_all` to free resources.

3. **Check for help first**: Use `lumerical_search_commands` to find the right commands before coding.

4. **Use lumerical_eval for complex scripts**: When multiple operations depend on each other,
   use `lumerical_eval` with a full script rather than many individual tool calls.

5. **Set up simulation in correct order**:
   - Solver region first
   - Then geometry structures
   - Then sources
   - Then monitors
   - Then run

6. **Material naming**: Use exact material names from the Lumerical database.
   Common examples: "Si (Silicon) - Palik", "SiO2 (Glass) - Palik",
   "Au (Gold) - Johnson and Christy", "Air", "H2O (Water) - Palik".

7. **Coordinate system**: Lumerical uses meters for length units by default.
   Common scales: waveguide width ~500e-9 (500nm), wavelength ~1.55e-6 (1550nm).

8. **For MODE simulations**: Use the FDE solver for waveguide/fiber mode analysis,
   EME solver for propagation in varying cross-sections, varFDTD for broadband planar structures.

9. **For DEVICE simulations**: Use for charge transport (semiconductor devices),
   heat transport, or coupled electro-thermal simulations.

10. **For INTERCONNECT**: Use for photonic integrated circuit (PIC) simulation
    with S-parameter based models.

## Product-Specific Commands

### FDTD-specific
- `addfdtd`: FDTD solver region
- `adddipole`, `addtfsf`, `addgaussian`: Specialized FDTD sources
- `addpower`, `addprofile`, `addindex`: Common FDTD monitors
- `addmesh`, `addpml`: Mesh override and PML boundaries
- `addmodeexpansion`: Mode expansion for S-parameters

### MODE-specific
- `addfde`: FDE solver (waveguide/fiber mode calculation)
- `addeme`: EME solver (propagation in varying waveguides)
- `addvarfdtd`: varFDTD solver (broadband planar simulation)
- `addwaveguide`: Waveguide geometry
- `addmode`: Mode source
- `addemeprofile`: EME field monitor

### DEVICE-specific
- `addchargesolver`, `addheatsolver`: Multiphysics solvers
- `addchargemonitor`, `addtemperaturemonitor`: Device monitors
- `adddope`, `addimportdope`: Doping profiles
- `addelectricalcontact`, `addvoltagebc`: Electrical boundary conditions

### INTERCONNECT-specific
- `addelement`: Circuit element
- `addport`: Optical/electrical port
- `addoptical`: Optical connection
- `addanalyzer`: Signal analyzer
- `importnetlist`, `exportnetlist`: Netlist operations

## Troubleshooting

- **"Session not found"**: The session_id may have expired. Use `lumerical_list_sessions` to check.
- **"Failed to evaluate code"**: Check your LSF syntax. Use `lumerical_get_command_help` for reference.
- **"Cannot import lumapi"**: Lumerical not installed or LUMERICAL_HOME not set.
  Set `LUMERICAL_HOME` environment variable (e.g., `D:\ENV\Lumerical\v202`).
- **Simulation hangs**: Check that the solver region dimensions cover all geometry.
  Check that AutoShutOff thresholds are reasonable.
- **Results are empty**: Ensure the monitor covers the region of interest spatially and spectrally.
