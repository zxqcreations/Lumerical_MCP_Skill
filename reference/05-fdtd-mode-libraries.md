# Lumerical FDTD & MODE Libraries Reference

> Source: `D:\ENV\Lumerical\v202\Resources\fdtd-library\` and `mode-library\`

## Overview

Lumerical ships with built-in example libraries (`*.fsp` for FDTD, `*.lms` for MODE)
that demonstrate common simulation workflows. These are valuable for:
- Learning simulation setup patterns
- Using as templates for new projects
- Testing the MCP server's load/run/result pipeline

## FDTD Library Examples

Path: `D:\ENV\Lumerical\v202\Resources\fdtd-library\`

| File | Description |
|------|-------------|
| `180_bend_wg.fsp` | 180-degree waveguide bend |
| `90_bend_wg.fsp` | 90-degree waveguide bend |
| `4s_pyr.fsp` | 4-sided pyramid structure |
| `CW_generation.fsp` | Continuous wave generation |
| `ChargeToIndex_Drude.fsp` | Drude model charge-to-index |
| `Qanalysis.fsp` | Q-factor / cavity analysis |
| `angled_monitor.fsp` | Angled monitor setup |
| `bandstructure.fsp` | Photonic band structure calculation |
| `bcc_pc.fsp` | BCC photonic crystal |
| `blaze_grating.fsp` | Blazed grating simulation |
| `bragg_grating.fsp` | Bragg grating simulation |
| `bsdf.fsp` | Bidirectional scattering distribution |
| `cc_bragg_fiber.fsp` | Coupled-cavity Bragg fiber |
| `cc_fiber.fsp` | Coupled-cavity fiber |
| `cc_vert_fiber.fsp` | Vertical coupled-cavity fiber |

## MODE Library Examples

Path: `D:\ENV\Lumerical\v202\Resources\mode-library\`

Waveguide mode solvers, EME propagation, and varFDTD examples.

## Using Library Files with MCP

```python
# In MCP workflow:
lumerical_open("fdtd") → session_id
lumerical_load(session_id, "D:/ENV/Lumerical/v202/Resources/fdtd-library/bragg_grating.fsp")
lumerical_run(session_id)
lumerical_get_result(session_id, "monitor_name", "T")
```

## Discovery via MCP

```python
# List available examples
lumerical_list_examples("fdtd")  # Returns all FDTD examples with metadata
lumerical_list_examples("mode")  # Returns all MODE examples with metadata
```

## Catalog File

Each library contains a `catalog.xml` file that indexes the examples with
metadata (title, description, thumbnail path, tags).

```xml
<!-- Structure from catalog.xml -->
<catalog>
  <item>
    <title>Bragg Grating</title>
    <description>Simulates reflection from a Bragg grating structure</description>
    <file>bragg_grating.fsp</file>
    <thumbnail>bragg_grating.png</thumbnail>
    <tags>grating, bragg, reflection</tags>
  </item>
  ...
</catalog>
```
