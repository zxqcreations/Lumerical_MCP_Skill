# lumerical-docs Repository Reference

> Source: `D:\ENV\claude\Lumerical_MCP\lumerical-docs\` (local clone)
> Status: 727 commands documented (100% complete)

## Repository Overview

This is a Python-based web scraping project that downloaded complete Lumerical
Scripting Language (LSF) command documentation from the Ansys Optics knowledge base
and converted it to local Markdown files for offline reference.

## Key Statistics

- **Total commands**: 727
- **Scraped**: 727 (100%)
- **Documentation format**: Markdown
- **Source**: https://optics.ansys.com/hc/en-us/

## Project Structure

```
lumerical-docs/
├── docs/
│   ├── lsf-script/
│   │   ├── en/               # 727 English Markdown docs
│   │   │   ├── abs.md
│   │   │   ├── addfdtd.md
│   │   │   ├── addrect.md
│   │   │   ├── ...           # (727 files total)
│   │   │   └── zeros.md
│   │   └── cn/               # Chinese translations (in progress)
│   ├── script-commands-alphabetical.md    # A-Z command index
│   ├── script-commands-by-category.md     # Category-indexed commands
│   ├── missing-lsf-script-docs.md         # Missing docs tracking
│   └── translation-progress.json          # Translation status
├── scripts/
│   ├── scrape_one_command.py      # Single command scraper
│   ├── update_lsf_docs.py         # Batch updater
│   ├── scrape_missing_lsf_docs.py # Missing docs scraper
│   ├── update_lsf_docs_resume.py  # Resume interrupted scrapes
│   ├── analyze_missing_commands.py # Analysis tools
│   ├── batch_scrape_fast.py       # Fast parallel scraper
│   └── translation_helper.py      # EN→CN translation workflow
├── pyproject.toml
├── AGENTS.md
├── README.md
└── uv.lock
```

## Tech Stack

- **Python**: 3.12+
- **Package Manager**: UV
- **Dependencies**: cloudscraper, beautifulsoup4, html2text, lxml, selenium, requests, tqdm
- **Dev**: pytest, ruff
- **Linter/Formatter**: Ruff

## Documentation Format

Each command doc follows this structure:

```markdown
# commandname

Brief description of what the command does.

## Syntax
| addfdtd;              | Basic usage description |
| addfdtd(struct_data); | With struct argument    |

## Example
\[code example\]

## See Also
\[related commands\]
```

Example from `addfdtd.md`:
```markdown
# addfdtd

Adds an FDTD solver region to the simulation environment.

**Syntax:**
addfdtd;              - Basic: adds FDTD solver region
addfdtd(struct_data); - With property struct

**Example:**
addfdtd;
set("dimension", 2);   # 1 = 2D, 2 = 3D
set("x", 0);
set("x span", 2e-6);
run;

**See Also:**
set, run
```

## Command Categories (from docs)

The `script-commands-by-category.md` file organizes commands into:

1. **Simulation Setup & Solvers** — addfdtd, addfde, addeme, addvarfdtd, addheat, setanalysis
2. **Geometry & Structures** — addrect, addsphere, addcircle, addring, addwaveguide, addpoly, copy, move
3. **Sources & Excitation** — addmode, adddipole, addgaussian, addtfsf, setglobalsource
4. **Monitors & Results** — addpower, addprofile, addindex, addtime, addmovie
5. **Materials** — addmaterial, setmaterial, getmaterial, importnk
6. **Mesh & Boundaries** — addmesh, addpml, addperiodic
7. **Optimization & Sweeps** — addsweep, runsweep, runoptimization
8. **Scripting Language** — variables, control flow, functions, I/O
9. **Math & Utility** — sin, cos, fft, interp, integrate
10. **Visualization** — plot, image, vectorplot, farfield

## Integration with MCP Server

The MCP server's `command_docs.py` module directly reads from this repository:

```python
# Priority 1: docs.json from Lumerical API (480+ commands, always available)
# Priority 2: lumerical-docs Markdown files (727 commands, richer content)

# Search paths (in order):
candidates = [
    Path(r"D:\ENV\claude\Lumerical_MCP\lumerical-docs\docs\lsf-script\en"),
    Path("./lumerical-docs/docs/lsf-script/en"),
    Path("../lumerical-docs/docs/lsf-script/en"),
]
```

When a user calls `lumerical_get_command_help("addfdtd")`, the server:
1. Gets basic info from docs.json (name, link, summary)
2. Loads the full Markdown from `lumerical-docs/docs/lsf-script/en/addfdtd.md`
3. Returns both in the response

## Branch Structure

- `main`: English LSF documentation scraping (this branch)
- `translation`: Chinese translation work
- `lumapi`: Lumapi documentation archive

## Key Scripts for Reference

### scrape_one_command.py
```bash
python scripts/scrape_one_command.py --list    # List all known commands
python scripts/scrape_one_command.py "addmaterial"  # Scrape specific command
python scripts/scrape_one_command.py --next    # Scrape next unscraped command
```

### translation_helper.py
```bash
python scripts/translation_helper.py --stats   # Translation statistics
python scripts/translation_helper.py --list    # Untranslated commands
python scripts/translation_helper.py --prepare addmaterial  # Create translation template
python scripts/translation_helper.py --report  # Detailed progress report
```
