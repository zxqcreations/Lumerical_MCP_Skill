# pyLumerical (ansys-lumerical-core) — Documentation Reference

> Source: https://lumerical.docs.pyansys.com/version/stable/

## Overview

**pyLumerical** is the official Ansys Python package for Lumerical automation,
distributed as `ansys-lumerical-core` on PyPI. It provides a modern, pip-installable
wrapper around the legacy `lumapi` module.

## Package Structure

```
ansys.lumerical.core
├── lumapi          # Re-exports the legacy lumapi module
│   ├── FDTD()      # FDTD session
│   ├── MODE()      # MODE session
│   ├── DEVICE()    # DEVICE session
│   └── INTERCONNECT()  # INTERCONNECT session
└── lumopt2         # Inverse design module (2026 R1.2+)
    └── (optimization classes)
```

## Installation

```bash
python -m pip install ansys-lumerical-core
```

Requirements:
- Python 3.8+
- Ansys Lumerical 2022 R1 or later installed locally
- Lumerical GUI license
- The Lumerical installation path is auto-discovered, or set `LUMERICAL_HOME`

## API Classes

### Interface Classes (lumapi)

| Class | Description |
|-------|-------------|
| `FDTD(filename=None, key=None, hide=False, serverArgs={})` | FDTD simulation session |
| `MODE(filename=None, key=None, hide=False, serverArgs={})` | MODE simulation session |
| `DEVICE(filename=None, key=None, hide=False, serverArgs={})` | Multiphysics simulation session |
| `INTERCONNECT(filename=None, key=None, hide=False, serverArgs={})` | Photonic circuit session |

All classes support context manager pattern:
```python
import ansys.lumerical.core as lumapi

with lumapi.FDTD() as session:
    session.eval("run;")
```

### Auxiliary Classes

| Class | Description |
|-------|-------------|
| `SimObject` | Represents a simulation object in the object tree |
| `SimObjectResults` | Access to simulation results of an object |
| `SimObjectId` | Weak reference identifier for objects |

### Autodiscovery

```python
from ansys.lumerical.core import autodiscovery
# Automatically finds Lumerical installation on import
```

The autodiscovery logic:
1. Checks `LUMERICAL_HOME` environment variable
2. Searches common installation paths
3. Configures `sys.path` and environment for `lumapi` import
4. Raises error if Lumerical is not found

## Key Usage Examples

### FDTD: Thin Film Transmission
```python
import ansys.lumerical.core as lumapi
import numpy as np
import matplotlib.pyplot as plt

with lumapi.FDTD() as session:
    # Get gold refractive index
    n_Au = session.getfdtdindex("Au (Gold) - Johnson and Christy", 3e14, 1e14, 1e15)

    # Calculate thin film transmission
    T = session.stackrt(
        np.array([1.0, n_Au, 1.0]),  # index profile
        np.array([0, 50e-9, 0]),      # thicknesses
        np.linspace(1e14, 1e15, 100)  # frequencies
    )
```

### MODE: Waveguide Mode Analysis
```python
with lumapi.MODE() as session:
    session.addfde()
    session.set("wavelength", 1.55e-6)
    # ... setup waveguide geometry ...
    session.findmodes()
    neff = session.getv("neff")
```

### INTERCONNECT: Ring Resonator
```python
with lumapi.INTERCONNECT() as session:
    # Setup ring resonator circuit
    # Run simulation
    # Get S-parameters
    pass
```

## lumopt2 — Inverse Design

The `lumopt2` module provides photonic inverse design capabilities:
- Adjoint-based optimization
- Topology optimization
- Shape optimization
- Requires Ansys Lumerical 2026 R1.2+

```python
import ansys.lumerical.core.lumopt2 as lmpt
# Use for advanced inverse design workflows
```

## Comparison: lumapi vs pyLumerical

| Feature | lumapi (legacy) | pyLumerical |
|---------|----------------|-------------|
| Installation | Bundled with Lumerical | pip install |
| API | Identical | Identical (re-exports lumapi) |
| Auto-discovery | Manual sys.path | Automatic |
| Version management | Fixed to installation | Can upgrade independently |
| IDE support | Manual config | Works out of the box |
| lumopt2 | Separate (lumopt) | Bundled (lumopt2) |

For the MCP server, we use the legacy `lumapi` directly because:
1. It's always available when Lumerical is installed
2. No additional pip dependency needed
3. The MCP server's auto-discovery handles path resolution
4. All functionality is identical
