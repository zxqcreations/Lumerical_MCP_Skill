# Lumerical MCP Server & Skill

Complete MCP (Model Context Protocol) server and Claude Code Skill for Ansys Lumerical photonic simulation tools — **FDTD**, **MODE**, **DEVICE**, and **INTERCONNECT**.

## What This Provides

- **MCP Server** with **40+ structured tools** covering the full Lumerical workflow
- **480+ script commands** accessible via `lumerical_eval` and `lumerical_call`
- **Claude Code Skill** for natural-language-driven simulation automation
- **Documentation search** across all Lumerical scripting commands

## Capabilities

| Domain | Coverage |
|--------|----------|
| Session Management | Open/close/list sessions for FDTD, MODE, DEVICE, INTERCONNECT |
| Script Execution | Execute arbitrary LSF, get/set variables, call any command |
| Simulation Control | Run, load, save, reset, layout mode |
| Geometry | Add rect/sphere/circle/polygon/waveguide + select/copy/move/rotate/delete |
| Materials | Add/modify/get materials, import nk data, query refractive index, thin-film T/R |
| Sources | Dipole, mode, gaussian, plane wave, TFSF, imported |
| Monitors | Power, profile, index, time, movie, field, absorption, mode expansion, bandstructure |
| Solvers | FDTD, FDE, EME, varFDTD, DGTD, Charge, Heat, FEEM |
| Boundaries | PML, Periodic, PEC, PMC, Absorbing |
| Results | Get result/data, field extraction, far-field projection, transmission spectra, CSV export |
| Optimization | Parameter sweeps, adjoint inverse design, parallel job execution |
| Documentation | List/search/help for 480+ commands, categorized browsing, example discovery |

## Quick Install

```bash
cd D:\ENV\claude\Lumerical_MCP

# Check your Lumerical installation
python install.py --check

# Install both MCP server config and Skill
python install.py
```

### Manual MCP Configuration

Add to `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "lumerical": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "D:\\ENV\\claude\\Lumerical_MCP",
      "description": "Lumerical MCP - FDTD, MODE, DEVICE, INTERCONNECT"
    }
  }
}
```

## Environment Setup

```bash
# Required: Point to your Lumerical installation
set LUMERICAL_HOME=D:\ENV\Lumerical\v202

# Install Python dependencies
pip install mcp numpy
```

## Usage

In Claude Code, type `/lumerical` to invoke the Skill, or use MCP tools directly:

```
lumerical_open("fdtd")  →  {"session_id": "lum_1", "product": "fdtd"}
lumerical_eval("lum_1", "addfdtd;\nset('dimension',2);\nset('x span',2e-6);\nrun;")
lumerical_close("lum_1")
```

## Project Structure

```
Lumerical_MCP/
├── mcp_server/
│   ├── server.py              # Main MCP server entry point (FastMCP)
│   ├── session_manager.py     # Session lifecycle (open/close/eval/var)
│   ├── command_docs.py        # Load & query 480+ command docs
│   └── tools/
│       ├── session.py         # Session management (5 tools)
│       ├── script.py          # Script execution (4 tools)
│       ├── simulation.py      # Simulation lifecycle (6 tools)
│       ├── geometry.py        # Geometry & objects (10 tools)
│       ├── material.py        # Materials (6 tools)
│       ├── source_monitor.py  # Sources & monitors (4 tools)
│       ├── solver.py          # Solver config (4 tools)
│       ├── results.py         # Results & analysis (6 tools)
│       ├── optimization.py    # Sweeps & optimization (6 tools)
│       └── docs.py            # Documentation & discovery (7 tools)
├── skill/
│   └── lumerical.md           # Claude Code Skill definition
├── lumerical-docs/            # Local documentation repository (727 cmd docs)
├── install.py                 # One-step installer
├── pyproject.toml
├── README.md
└── DESIGN.md                  # Architecture design document
```

## Requirements

- **Python 3.10+** with `mcp` and `numpy`
- **Ansys Lumerical** v202 (or later) installed locally
- **Lumerical GUI license**
- **Windows** (primary; Linux/macOS supported via lumapi)

## License

MIT
