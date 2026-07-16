# Lumerical MCP Server & Skill - Architecture Design

## 1. Overview

A comprehensive MCP (Model Context Protocol) server that provides full access to
Ansys Lumerical photonic simulation tools (FDTD, MODE, DEVICE, INTERCONNECT)
through Claude Code. Accompanied by a Skill that enables natural language
interaction with all MCP tools.

## 2. Resource Analysis Summary

### lumapi.py (1310 lines)
- Core Python API using ctypes to interface with `interopapi.dll`
- Base class `Lumerical` with subclasses: `FDTD`, `MODE`, `DEVICE`, `INTERCONNECT`
- Dynamically registers ALL Lumerical script commands (~480+) as Python methods
- Key methods: `eval()`, `getv()`, `putv()`, `appCall()`, `appCallWithConstructor()`
- Object model: `SimObject`, `SimObjectResults`, `GetSetHelper`
- Session management: `open()`, `close()`, context manager support

### docs.json (480+ commands)
- Complete mapping of all Lumerical script commands to documentation URLs

### lumerical-docs (727 commands, 100% scraped)
- Full Markdown documentation for every LSF command
- Categorized and alphabetical command lists
- Located at `lumerical-docs/docs/lsf-script/en/`

### pyLumerical (ansys-lumerical-core)
- Modern pip-installable wrapper providing `ansys.lumerical.core`
- Same interface as legacy lumapi
- Auto-discovery of Lumerical installation

## 3. MCP Tool Architecture

### 3.1 Session Management Tools
| Tool | Description |
|------|-------------|
| `lumerical_open` | Open a Lumerical session (fdtd/mode/device/interconnect) |
| `lumerical_close` | Close a specific session |
| `lumerical_list_sessions` | List all active sessions |
| `lumerical_close_all` | Close all active sessions |

### 3.2 Script Execution Tools
| Tool | Description |
|------|-------------|
| `lumerical_eval` | Execute arbitrary Lumerical script code |
| `lumerical_get_var` | Get a variable value from the session |
| `lumerical_set_var` | Set a variable value in the session |
| `lumerical_call` | Call a specific Lumerical script command by name |

### 3.3 Simulation Lifecycle Tools
| Tool | Description |
|------|-------------|
| `lumerical_run` | Run the current simulation |
| `lumerical_load` | Load a project file (.fsp, .lms, .icp) |
| `lumerical_save` | Save the current project |
| `lumerical_reset` | Reset the simulation |
| `lumerical_switch_to_layout` | Switch to layout mode |

### 3.4 Geometry & Object Tools
| Tool | Description |
|------|-------------|
| `lumerical_add` | Add a simulation object (rect, sphere, polygon, etc.) |
| `lumerical_set` | Set property of the selected object |
| `lumerical_get` | Get property of the selected object |
| `lumerical_select` | Select an object by name |
| `lumerical_delete` | Delete an object by name |
| `lumerical_copy` | Copy an object |
| `lumerical_move` | Move/translate an object |
| `lumerical_rotate` | Rotate an object |
| `lumerical_groupscope` | Set/get the group scope |

### 3.5 Material Tools
| Tool | Description |
|------|-------------|
| `lumerical_add_material` | Add or modify a material |
| `lumerical_set_material` | Set material of selected object |
| `lumerical_get_material` | Get material data |
| `lumerical_get_index` | Get refractive index of a material |
| `lumerical_import_nk` | Import n,k material data from file |

### 3.6 Source & Monitor Tools
| Tool | Description |
|------|-------------|
| `lumerical_add_source` | Add a source (dipole, mode, gaussian, etc.) |
| `lumerical_add_monitor` | Add a monitor (power, profile, index, etc.) |
| `lumerical_set_global_source` | Set global source properties |
| `lumerical_set_global_monitor` | Set global monitor properties |

### 3.7 Solver Configuration Tools
| Tool | Description |
|------|-------------|
| `lumerical_add_solver` | Add a solver region (FDTD, FDE, EME, varFDTD, etc.) |
| `lumerical_add_mesh` | Add a mesh override region |
| `lumerical_add_boundary` | Add boundary condition (PML, periodic, etc.) |
| `lumerical_set_analysis` | Set analysis parameters |

### 3.8 Results & Analysis Tools
| Tool | Description |
|------|-------------|
| `lumerical_get_result` | Get simulation result by name |
| `lumerical_get_data` | Get raw monitor data |
| `lumerical_get_field` | Get field data from a monitor |
| `lumerical_export_data` | Export data to file (CSV, MATLAB, etc.) |
| `lumerical_plot` | Generate a plot in Lumerical |

### 3.9 Optimization Tools (lumopt)
| Tool | Description |
|------|-------------|
| `lumerical_run_optimization` | Run an inverse design optimization |
| `lumerical_get_optimization_status` | Get optimization progress |

### 3.10 Sweep & Parameterization Tools
| Tool | Description |
|------|-------------|
| `lumerical_add_sweep` | Add a parameter sweep |
| `lumerical_run_sweep` | Run a parameter sweep |
| `lumerical_get_sweep_result` | Get sweep results |

### 3.11 Documentation & Discovery Tools
| Tool | Description |
|------|-------------|
| `lumerical_list_commands` | List all available script commands |
| `lumerical_get_command_help` | Get detailed help for a command |
| `lumerical_search_commands` | Search commands by keyword/category |
| `lumerical_list_examples` | List available example simulation files |
| `lumerical_get_example_info` | Get info about a specific example |

## 4. Technical Implementation

### 4.1 Technology Stack
- **Language**: Python 3.10+
- **MCP SDK**: `mcp` (official Python SDK)
- **Transport**: stdio
- **Lumerical API**: `lumapi` (bundled with Lumerical installation)
- **Async**: asyncio with thread pool for blocking lumapi calls

### 4.2 File Structure
```
Lumerical_MCP/
├── mcp_server/
│   ├── __init__.py
│   ├── server.py              # Main MCP server entry point
│   ├── session_manager.py     # Session lifecycle management
│   ├── command_docs.py        # Load and query command documentation
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── session.py         # Session management tools
│   │   ├── script.py          # Script execution tools
│   │   ├── simulation.py      # Simulation lifecycle tools
│   │   ├── geometry.py        # Geometry & object tools
│   │   ├── material.py        # Material tools
│   │   ├── source_monitor.py  # Source & monitor tools
│   │   ├── solver.py          # Solver configuration tools
│   │   ├── results.py         # Results & analysis tools
│   │   ├── optimization.py    # Optimization tools
│   │   ├── sweep.py           # Sweep & parameterization tools
│   │   └── docs.py            # Documentation & discovery tools
│   └── utils.py               # Utility functions
├── skill/
│   └── lumerical.md           # Claude Code Skill definition
├── pyproject.toml
├── install.py                 # Installation script
├── README.md
└── DESIGN.md                  # This file
```

### 4.3 Session Lifecycle
```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  MCP Server  │────▶│ SessionManager    │────▶│ lumapi.FDTD()   │
│  (stdio)     │     │  (session pool)   │     │ lumapi.MODE()   │
│              │     │                   │     │ lumapi.DEVICE() │
│              │     │  {id: {handle,    │     │ lumapi.INTERCONNECT()│
│              │     │   product,        │     └─────────────────┘
│              │     │   created_at}}    │
└──────────────┘     └──────────────────┘
```

### 4.4 Thread Safety
- All lumapi calls run in a dedicated thread pool
- Each session has its own lock to prevent concurrent access
- MCP request handling is async but delegates to sync lumapi

### 4.5 Error Handling Strategy
- Wrap all lumapi exceptions in structured error responses
- Connection checks before every operation
- Graceful degradation if Lumerical is not installed
- Timeout protection for long-running operations

## 5. Skill Design

The Skill (`lumerical.md`) will provide:
1. Context about Lumerical products and capabilities
2. Workflow guidance for common simulation tasks
3. Mapping from natural language requests to MCP tool calls
4. Best practices for simulation setup
5. Troubleshooting guidance

Skill structure:
```markdown
# Lumerical Simulation Skill

## Description
Complete access to Ansys Lumerical photonic simulation tools.

## Capabilities
- FDTD, MODE, DEVICE, INTERCONNECT simulation
- Scripting automation
- Geometry creation
- Result analysis
- Inverse design optimization
- Parameter sweeps

## Usage Patterns
[examples and workflows]
```
