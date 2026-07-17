# Lumerical Photonic Simulation Skill (v261)

## Description

Complete access to Ansys Lumerical v261 photonic simulation and design tools through
the Lumerical MCP server v2.0. Supports FDTD, MODE, DEVICE, INTERCONNECT with 665+
scripting commands. New v261 capabilities: inverse design optimization (lumopt),
CML compiler for foundry PDK, local MPI parallel processing, and AALI AI assistance.

## When to Use

Invoke this skill when the user wants to:
- Run photonic/electromagnetic simulations (FDTD, RCWA, DGTD, MODE, DEVICE, INTERCONNECT)
- Design photonic devices (waveguides, couplers, resonators, gratings, etc.)
- Analyze simulation results (transmission, field profiles, S-parameters, far-field)
- Create and manipulate simulation geometry with the v261 SimObject API
- Work with materials (add, modify, query refractive index)
- Set up parameter sweeps, optimization, or inverse design
- Automate Lumerical workflows via scripting
- Build foundry PDK libraries with the CML Compiler
- Run parallel simulations with local MPI
- Get AI-assisted simulation guidance (AALI, if installed)
- Query the Lumerical scripting command documentation (665 commands)

## MCP Tools Available

All tools are prefixed with `lumerical_` to avoid name collisions. Each tool
requires a `session_id` obtained from `lumerical_open`.

### Session Management
| Tool | Purpose |
|------|---------|
| `lumerical_open` | Open FDTD/MODE/DEVICE/INTERCONNECT session (v261: +remote_args, +keep_cad_opened, +script, +project) |
| `lumerical_close` | Close a specific session |
| `lumerical_close_all` | Close all sessions |
| `lumerical_list_sessions` | List active sessions with API version info |

### Script Execution
| Tool | Purpose |
|------|---------|
| `lumerical_eval` | Execute Lumerical script code (665 commands available) |
| `lumerical_get_var` | Get variable value from workspace |
| `lumerical_set_var` | Set variable in workspace |
| `lumerical_call` | Call specific command by name with args |

### Simulation Control
| Tool | Purpose |
|------|---------|
| `lumerical_run` | Run the simulation |
| `lumerical_load` | Load project file (.fsp, .lms, .icp, .dsp, .lsf) |
| `lumerical_save` | Save current project |
| `lumerical_reset` | Reset simulation to initial state |
| `lumerical_switch_to_layout` | Switch to layout mode |
| `lumerical_cd` | Change working directory |
| `lumerical_stop` | Gracefully stop running simulation |
| `lumerical_get_status` | Get simulation progress and status |
| `lumerical_get_resource` | Get compute resource config (threads, processes) |
| `lumerical_set_resource` | Set compute resource config |
| `lumerical_mesh_order` | Set global mesh order |

### Geometry & Objects
| Tool | Purpose |
|------|---------|
| `lumerical_add` | Add geometry/simulation object (v261: +field_region, +simulation_region, +assembly_group) |
| `lumerical_set` | Set property of selected object |
| `lumerical_get` | Get property of selected object |
| `lumerical_select` | Select object by name |
| `lumerical_select_all` | Select all objects |
| `lumerical_delete` | Delete object |
| `lumerical_copy` | Copy selected object |
| `lumerical_move` | Move selected object |
| `lumerical_rotate` | Rotate selected object |
| `lumerical_groupscope` | Set/get group scope |

### Materials
| Tool | Purpose |
|------|---------|
| `lumerical_add_material` | Add/modify material |
| `lumerical_set_material` | Set material on selected object |
| `lumerical_get_material` | Get material properties |
| `lumerical_get_index` | Get complex refractive index at frequency |
| `lumerical_import_nk` | Import n,k data from file |
| `lumerical_get_transmission` | Calculate thin-film transmission |

### Sources & Monitors
| Tool | Purpose |
|------|---------|
| `lumerical_add_source` | Add source (v261: +delta_charge, +electrical_contact, +uniform_heat) |
| `lumerical_add_monitor` | Add monitor (v261: +rcwa_field, +dft, +charge, +heat_flux, +temperature, +jflux) |
| `lumerical_set_global_source` | Configure global source settings |
| `lumerical_set_global_monitor` | Configure global monitor settings |

### Solver Configuration
| Tool | Purpose |
|------|---------|
| `lumerical_add_solver` | Add solver (v261: +rcwa, +dgt_d) |
| `lumerical_add_mesh` | Add mesh override |
| `lumerical_add_boundary` | Add boundary condition |
| `lumerical_set_analysis` | Set solver analysis parameters |
| `lumerical_use_gpu` | Enable/disable GPU acceleration |
| `lumerical_set_mesh_order` | Per-object mesh order priority |
| `lumerical_add_conformal_mesh` | Conformal meshing for interfaces |

### Results & Analysis
| Tool | Purpose |
|------|---------|
| `lumerical_get_result` | Get monitor results |
| `lumerical_get_data` | Get raw monitor data |
| `lumerical_get_field` | Get EM field data |
| `lumerical_export_data` | Export to CSV |
| `lumerical_farfield` | Far-field projection |
| `lumerical_transmission` | Get transmission spectrum |
| `lumerical_get_s_parameters` | Get S-parameter matrix (INTERCONNECT) |
| `lumerical_get_field_components` | List available field components |
| `lumerical_get_convergence` | Get auto-shutoff convergence data |

### Optimization & Sweeps
| Tool | Purpose |
|------|---------|
| `lumerical_add_sweep` | Create parameter sweep |
| `lumerical_run_sweep` | Run sweep |
| `lumerical_get_sweep_result` | Get sweep results |
| `lumerical_add_optimization` | Set up optimization |
| `lumerical_run_optimization` | Run optimization |
| `lumerical_run_parallel` | Parallel job execution |

### Inverse Design (v261 new — lumopt)
| Tool | Purpose |
|------|---------|
| `lumerical_opt_list_methods` | List FOMs, geometries, optimizers available |
| `lumerical_opt_setup` | Configure adjoint optimization |
| `lumerical_opt_check_setup` | Check lumopt availability and modules |
| `lumerical_opt_set_fabrication` | Apply Gaussian lithography constraints |

### CML Compiler (v261 new — Foundry PDK)
| Tool | Purpose |
|------|---------|
| `lumerical_cml_list_models` | List 25+ pre-built photonic models |
| `lumerical_cml_status` | Check CML compiler availability |
| `lumerical_cml_deploy` | Deploy lumfoundry template |
| `lumerical_cml_build` | Build and install CML library |
| `lumerical_cml_validate` | Validate CML library |
| `lumerical_cml_compile_element` | Compile single element |

### MPI Parallel Processing (v261 new — Intel MPI)
| Tool | Purpose |
|------|---------|
| `lumerical_mpi_get_config` | Get MPI and CPU configuration |
| `lumerical_set_threads` | Set OpenMP thread count |
| `lumerical_set_processes` | Set parallel process count |
| `lumerical_mpi_run_sweep` | Run sweep with parallel processes |
| `lumerical_mpi_run_batch` | Batch process multiple project files |

### AI Assistance (v261 new — AALI)
| Tool | Purpose |
|------|---------|
| `lumerical_ai_status` | Check AALI installation and service health |
| `lumerical_ai_chat` | AI-assisted simulation guidance |
| `lumerical_ai_search` | Semantic search over simulation knowledge base |
| `lumerical_ai_suggest_material` | AI-recommend materials |
| `lumerical_ai_setup_simulation` | AI-generate simulation script from description |

### Documentation & Discovery
| Tool | Purpose |
|------|---------|
| `lumerical_list_commands` | List 665 available commands |
| `lumerical_get_categories` | Get command categories |
| `lumerical_get_command_help` | Get detailed command help |
| `lumerical_search_commands` | Search commands by keyword |
| `lumerical_get_script_help` | Get Markdown command reference |
| `lumerical_list_examples` | List example simulation files |

## Installation & Setup

### Requirements
- **Lumerical v261** (2026R1, ANSYS Inc) installed at `D:\ENV\Lumerical\ANSYS Inc\v261`
- Python 3.10+ (v261 bundles Python 3.13.1)
- Dependencies: `mcp>=1.0.0`, `numpy>=1.24.0`

### Optional
- **scipy** — for lumopt inverse design optimizers
- **AALI** — local AI toolkit for AI-assisted simulation

### LUMERICAL_HOME
Set to the v261 root directory (NOT api/python):
```powershell
set LUMERICAL_HOME=D:\ENV\Lumerical\ANSYS Inc\v261
```

## Workflow Patterns

### 1. Basic FDTD Simulation (from scratch)
```
1. lumerical_open("fdtd")
2. lumerical_add_solver(session_id, "fdtd", {"dimension": 2, "simulation_time": 1000e-15, "x_span": 4e-6, "y_span": 4e-6})
3. lumerical_add(session_id, "rect", {"x": 0, "y": 0, "x_span": 2e-6, "y_span": 0.22e-6, "material": "Si (Silicon) - Palik"})
4. lumerical_add_source(session_id, "mode", {"wavelength_start": 1.5e-6, "wavelength_stop": 1.6e-6, "injection_axis": "x"})
5. lumerical_add_monitor(session_id, "power", {"monitor_type": "2D Z-normal", "x": 1e-6})
6. lumerical_run(session_id)
7. lumerical_transmission(session_id)
8. lumerical_close(session_id)
```

### 2. Loading an Existing Project
```
1. lumerical_open("fdtd")
2. lumerical_load(session_id, "C:/projects/waveguide.fsp")
3. lumerical_run(session_id)
4. lumerical_get_result(session_id, "monitor_name")
```

### 3. GPU-Accelerated Simulation (v261)
```
1. lumerical_open("fdtd")
2. lumerical_use_gpu(session_id, True)  # Enable GPU
3. lumerical_load(session_id, "large_project.fsp")
4. lumerical_set_resource(session_id, '{"number of threads": 8}')
5. lumerical_run(session_id)
```

### 4. Inverse Design with lumopt (v261)
```
1. lumerical_open("fdtd")
2. lumerical_opt_check_setup(session_id)  # Verify lumopt available
3. lumerical_opt_list_methods()  # See available FOMs, geometries, optimizers
4. lumerical_opt_setup(session_id, fom_type="transmission", optimizer_type="adaptive_gradient", geometry_type="topology", config='{"wavelength": 1.55e-6, "max_iterations": 100, "design_region": {"x": 0, "x_span": 2e-6}}')
5. lumerical_opt_set_fabrication(session_id, sigma=20e-9, threshold=0.5)
6. lumerical_run_optimization(session_id)
```

### 5. Foundry PDK with CML Compiler (v261)
```
1. lumerical_cml_list_models()  # Browse 25+ pre-built models
2. lumerical_cml_status()  # Check CML compiler ready
3. lumerical_cml_deploy("C:/my_pdk")  # Deploy template
4. lumerical_cml_build("C:/my_pdk")  # Build library
5. lumerical_cml_validate("C:/my_pdk")  # Validate
```

### 6. Multi-core Parallel Sweep (v261 — Intel MPI)
```
1. lumerical_open("fdtd")
2. lumerical_mpi_get_config()  # Check CPU cores and MPI status
3. ... set up simulation geometry, sources, monitors ...
4. lumerical_set_threads(session_id, 2)  # 2 threads per process
5. lumerical_add_sweep(session_id, "width_sweep", "ranges", '{"parameters": ["wg_width"], "ranges": [[200e-9, 500e-9, 10]], "results": ["T"]}')
6. lumerical_mpi_run_sweep(session_id, "width_sweep", num_processes=4)
7. lumerical_get_sweep_result(session_id, "width_sweep", "T")
```

### 7. AI-Assisted Simulation (v261 — AALI)
```
1. lumerical_ai_status()  # Check AALI is installed and running
2. lumerical_ai_chat("How do I design a grating coupler for 1550nm wavelength with 70% coupling efficiency?")
3. lumerical_ai_setup_simulation("2D FDTD of ring resonator with radius 5um, Si waveguide on SiO2, TE mode at 1550nm")
4. lumerical_eval(session_id, result["generated_code"])  # Run AI-generated script
```

### 8. Material Exploration
```
1. lumerical_open("fdtd")
2. lumerical_get_index(session_id, "Si (Silicon) - Palik", 1.94e14)  # n,k at 1550nm
3. lumerical_get_transmission(session_id, "Si (Silicon) - Palik", thickness=220e-9)
4. lumerical_ai_suggest_material("high refractive index > 3.0 at 1550nm, low optical loss")  # AI-assisted
```

### 9. Direct Script for Complex Setups
```
1. lumerical_open("fdtd")
2. lumerical_eval(session_id, """
    # Full LSF script for complex grating coupler
    addfdtd; set("dimension", 2);
    # ... complex setup ...
    run;
""")
```

## Best Practices

1. **Session tracking**: Store `session_id` from `lumerical_open` and use it consistently.
2. **Close sessions**: Always close sessions with `lumerical_close` when done.
3. **Documentation first**: Use `lumerical_search_commands("keyword")` to find the right command before scripting.
4. **Use eval for complex scripts**: For multi-step workflows, build the full LSF script and execute with `lumerical_eval`.
5. **Setup order**: Solver → Geometry → Sources → Monitors → Run.
6. **Material names**: Use exact names from the Lumerical material database: `"Si (Silicon) - Palik"`, `"SiO2 (Glass) - Palik"`.
7. **Coordinate systems**: Lumerical uses meters. 1.55 µm = 1.55e-6.
8. **v261 SimObject API**: When available, use object-oriented property access through eval: `?obj.mesh_settings.dx` returns nested properties.
9. **GPU Acceleration**: Enable `lumerical_use_gpu` for large FDTD/DGTD projects — significant speedup.
10. **MPI**: Use `lumerical_mpi_run_sweep` for parameter sweeps — near-linear scaling with process count.
11. **AI Assistance**: Use `lumerical_ai_setup_simulation` to generate initial scripts, then refine manually.

## Product-Specific Commands

### FDTD (addfdtd solver)
- `addfdtd`, `addrect`, `addcircle`, `addsphere`, `addring`, `addpolygon`
- `addmesh`, `addpml`, `addperiodic`, `addabsorbing`
- `adddipole`, `addmode`, `addgaussian`, `addtfsf`, `addplane`
- `addpower`, `addprofile`, `addindex`, `addtime`, `addmovie`
- `addemfieldmonitor`, `addemfieldtimemonitor`, `addemabsorptionmonitor`
- `addmodeexpansion`, `addfarfield`
- SETUP: `setglobalsource`, `setglobalmonitor`, `setresource`

### MODE (FDE/EME/varFDTD solvers)
- `addfde`, `addeme`, `addvarfdtd`
- `addwaveguide`, `addbentwaveguide`
- `addemeport`, `addemeindex`, `addemeprofile`

### RCWA (v261 new)
- `addrcwa`, `addrcwafieldmonitor`

### DGTD (v261 enhanced)
- `adddgtdsolver`, `adddgtdmesh`
- GPU acceleration supported

### DEVICE (charge/heat/FEEM)
- `addchargesolver`, `addheatsolver`, `addfeemsolver`
- `adddope`, `addimplant`, `addimportdope`
- `addelectricalcontact`, `addvoltagebc`
- `addtemperaturebc`, `addthermalpowerbc`, `addthermalinsulatingbc`
- `addheatfluxbc`, `addradiationbc`, `addsurfacerecombinationbc`

### INTERCONNECT
- `addelement`, `addport`, `addanalyzer`, `importnetlist`
- `addwaveguide`, `addmodulator`, `adddetector`
- CML Compiler: `lumerical_cml_build` generates INTERCONNECT elements

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cannot find Lumerical installation" | Set `LUMERICAL_HOME` to `D:\ENV\Lumerical\ANSYS Inc\v261` |
| "Cannot import lumapi" | Ensure v261 is installed and LUMERICAL_HOME points to the root directory |
| Session not found | List sessions with `lumerical_list_sessions` — sessions auto-close on timeout |
| Script execution fails | Check LSF syntax; use `lumerical_search_commands` to verify command names |
| Empty results | Use `lumerical_get_field_components` to check available data; ensure simulation completed |
| GPU not available | Check GPU drivers; FDTD/DGTD only; use `lumerical_get_resource` to verify |
| CML compiler not found | Install v261 in default location or add `CML_Compiler/bin` to PATH |
| AALI not installed | Run `install-aali.ps1 -location "D:\ENV\Lumerical\ANSYS Inc\AI Tools\AALI\v1\installed"` |
| AALI services not running | Start `aali-local-manager.exe` first, then use AI tools |
