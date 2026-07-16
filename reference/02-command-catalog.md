# Lumerical Scripting Commands — Complete Catalog

> Source: `D:\ENV\Lumerical\v202\api\python\docs.json` (480+ commands)
> Supplemented by: `lumerical-docs/docs/lsf-script/en/` (727 documented commands)

## Overview

All Lumerical script commands are dynamically registered as Python methods on
session objects (FDTD, MODE, DEVICE, INTERCONNECT). Each command can be called
via `session.<command>()` or through `lumerical_eval`/`lumerical_call` MCP tools.

## Command Count by Source

| Source | Count | Format |
|--------|-------|--------|
| docs.json (from Lumerical API) | ~480 | Name + link + summary |
| lumerical-docs repo | 727 | Full Markdown documentation |
| Dynamically registered as methods | ~480 | Python methods on session |

## Command Categories

### 1. Solvers & Simulation Setup (~50 commands)

| Command | Description | Product |
|---------|-------------|---------|
| `addfdtd` | Add FDTD solver region | FDTD |
| `addfde` | Add FDE solver (waveguide mode) | MODE |
| `addeme` | Add EME solver (propagation) | MODE |
| `addvarfdtd` | Add varFDTD solver | MODE |
| `adddgtdsolver` | Add DGTD solver | FDTD |
| `addchargesolver` | Add charge transport solver | DEVICE |
| `addheatsolver` | Add heat transport solver | DEVICE |
| `addfeemsolver` | Add FEEM solver | DEVICE |
| `addmesh` | Add mesh override region | FDTD, MODE |
| `addpml` | Add PML boundary | FDTD, MODE |
| `addperiodic` | Add periodic BC | FDTD, MODE |
| `addpec` | Add PEC boundary | FDTD |
| `addpmc` | Add PMC boundary | FDTD |
| `addabsorbing` | Add absorbing BC | FDTD |
| `addtfsf` | Add TFSF source region | FDTD |
| `setanalysis` | Set analysis parameters | FDTD, MODE |
| `getactivesolver` | Get active solver name | All |
| `setactivesolver` | Set active solver | All |
| `clearanalysis` | Clear analysis settings | All |

### 2. Geometry & Structures (~80 commands)

| Command | Description | Product |
|---------|-------------|---------|
| `addrect` | Add rectangle | All |
| `addsphere` | Add sphere | All |
| `addcircle` | Add circle/cylinder | All |
| `addring` | Add ring/torus | All |
| `addtriangle` | Add triangle | All |
| `addpolygon` | Add polygon (via addpoly) | All |
| `add2dpoly` | Add 2D polygon | All |
| `add2drect` | Add 2D rectangle | All |
| `addpyramid` | Add pyramid | All |
| `addplanarsolid` | Add planar solid | All |
| `addsurface` | Add surface object | All |
| `addwaveguide` | Add waveguide | MODE |
| `addstructuregroup` | Add structure group | All |
| `addanalysisgroup` | Add analysis group | All |
| `addgroup` | Add group | All |
| `addimport` | Add import object | All |
| `addlayer` | Add layer | All |
| `addlayerbuilder` | Add layer builder | All |
| `addcustom` | Add custom object | All |
| `adduserprop` | Add user property | All |
| `addparameter` | Add parameter | All |
| `addattribute` | Add attribute | All |
| `addproperty` | Add material property | All |
| `addtolibrary` | Add to library | All |
| `copy` | Copy selected object | All |
| `move` | Move/translate object | All |
| `rotate` | Rotate object | All |
| `delete` | Delete object | All |
| `deleteall` | Delete all objects | All |
| `select` | Select object | All |
| `selectall` | Select all | All |
| `shiftselect` | Shift-select object | All |
| `unselectall` | Deselect all | All |
| `groupscope` | Set/get group scope | All |
| `addtogroup` | Add object to group | All |

### 3. Sources & Excitation (~20 commands)

| Command | Description | Product |
|---------|-------------|---------|
| `adddipole` | Add dipole source | FDTD |
| `addmode` | Add mode source | FDTD, MODE |
| `addmodesource` | Add mode source (varFDTD) | MODE |
| `addgaussian` | Add Gaussian beam | FDTD |
| `addplane` | Add plane wave source | FDTD |
| `addtfsf` | Add TFSF source | FDTD |
| `addimportedsource` | Add imported source | FDTD |
| `setglobalsource` | Set global source settings | FDTD, MODE |
| `getglobalsource` | Get global source settings | FDTD, MODE |
| `setsourcesignal` | Set source signal | All |
| `updatesourcemode` | Update source mode profile | FDTD, MODE |

### 4. Monitors & Data Collection (~30 commands)

| Command | Description | Product |
|---------|-------------|---------|
| `addpower` | Add power monitor | FDTD, MODE |
| `addprofile` | Add field profile monitor | FDTD, MODE |
| `addindex` | Add index monitor | FDTD, MODE |
| `addtime` | Add time monitor | FDTD, MODE |
| `addmovie` | Add movie monitor | FDTD |
| `addemfieldmonitor` | Add EM field monitor | FDTD |
| `addemfieldtimemonitor` | Add EM field time monitor | FDTD |
| `addemabsorptionmonitor` | Add absorption monitor | FDTD |
| `addmodeexpansion` | Add mode expansion monitor | FDTD, MODE |
| `addbandstructuremonitor` | Add bandstructure monitor | FDTD |
| `addport` | Add port (S-parameter) | FDTD, MODE |
| `addeffectiveindex` | Add effective index monitor | FDTD, MODE |
| `addemeport` | Add EME port | MODE |
| `addemeprofile` | Add EME field monitor | MODE |
| `addemeindex` | Add EME index monitor | MODE |
| `adddgtdmesh` | Add DGTD mesh | FDTD |
| `addchargemonitor` | Add charge monitor | DEVICE |
| `addtemperaturemonitor` | Add temperature monitor | DEVICE |
| `addjfluxmonitor` | Add J-flux monitor | DEVICE |
| `addheatfluxmonitor` | Add heat flux monitor | DEVICE |
| `setglobalmonitor` | Set global monitor settings | FDTD, MODE |
| `getglobalmonitor` | Get global monitor settings | FDTD, MODE |

### 5. Materials (~25 commands)

| Command | Description | Product |
|---------|-------------|---------|
| `addmaterial` | Add/modify material | All |
| `setmaterial` | Set object material | All |
| `getmaterial` | Get material data | All |
| `deletematerial` | Delete material | All |
| `copymaterial` | Copy material | All |
| `materialexists` | Check if material exists | All |
| `addmaterialproperties` | Add material properties | All |
| `addmodelmaterial` | Add model material | All |
| `getindex` | Get refractive index | All |
| `getfdtdindex` | Get FDTD-compatible index | FDTD |
| `getnumericalpermittivity` | Get numerical permittivity | All |
| `getsurfaceconductivity` | Get surface conductivity | All |
| `getfdtdsurfaceconductivity` | Get FDTD surface conductivity | FDTD |
| `importnk` | Import n,k from file | All |
| `importnk2` | Import n,k v2 | All |
| `importnkobfuscated` | Import obfuscated n,k | All |
| `importsurface` | Import surface material | All |

### 6. Simulation Control (~15 commands)

| Command | Description | Product |
|---------|-------------|---------|
| `run` | Run simulation | All |
| `runanalysis` | Run analysis | All |
| `runinitialize` | Run initialization | All |
| `runsetup` | Run setup | All |
| `runstep` | Run single step | All |
| `runfinalize` | Run finalization | All |
| `waituntildone` | Wait for completion | All |
| `simulationdiverged` | Check if diverged | All |
| `save` | Save project | All |
| `load` | Load project | All |
| `close` | Close project | All |
| `newproject` | New project | All |
| `switchtodesign` | Switch to design mode | All |
| `switchtolayout` | Switch to layout mode | All |
| `layoutmode` | Layout mode operations | All |

### 7. Results & Post-Processing (~40 commands)

| Command | Description | Product |
|---------|-------------|---------|
| `getresult` | Get result data | All |
| `getresultdata` | Get result data array | All |
| `haveresult` | Check if result exists | All |
| `setresult` | Set result value | All |
| `getdata` | Get raw monitor data | All |
| `getelectric` | Get electric field | FDTD, MODE |
| `getmagnetic` | Get magnetic field | FDTD, MODE |
| `getfield` | Get field data | All |
| `setfield` | Set field data | All |
| `getindex` | Get refractive index | FDTD, MODE |
| `getdgtdindex` | Get DGTD index | FDTD |
| `transmission` | Calculate transmission | FDTD, MODE |
| `farfield3d` | 3D far-field projection | FDTD |
| `farfield2d` | 2D far-field projection | FDTD |
| `farfieldpolar3d` | 3D polar far-field | FDTD |
| `farfieldspherical` | Spherical far-field | FDTD |
| `farfieldexact` | Exact far-field | FDTD |
| `farfieldfilter` | Filtered far-field | FDTD |
| `farfieldangle` | Far-field angle data | FDTD |
| `grating` | Grating analysis | FDTD, MODE |
| `gratingorders` | Grating order analysis | FDTD, MODE |
| `sourcenorm` | Source normalization | FDTD |
| `sourcepower` | Source power | FDTD |
| `sourceintensity` | Source intensity | FDTD |
| `dipolepower` | Dipole power | FDTD |
| `stackrt` | Stack RT calculation | FDTD |
| `stackfield` | Stack field | FDTD |
| `stackdipole` | Stack dipole | FDTD |
| `stackpurcell` | Stack Purcell | FDTD |
| `overlap` | Mode overlap | FDTD, MODE |
| `bestoverlap` | Best mode overlap | MODE |
| `coupling` | Coupling coefficient | MODE |
| `propagate` | Mode propagation | MODE |
| `emepropagate` | EME propagation | MODE |

### 8. Sweeps & Parameterization (~15 commands)

| Command | Description | Product |
|---------|-------------|---------|
| `addsweep` | Add parameter sweep | All |
| `addsweepparameter` | Add sweep parameter | All |
| `addsweepresult` | Add sweep result | All |
| `runsweep` | Run sweep | All |
| `getsweep` | Get sweep definition | All |
| `setsweep` | Set sweep parameters | All |
| `getsweepdata` | Get sweep data | All |
| `getsweepresult` | Get sweep results | All |
| `havesweepdata` | Check sweep data exists | All |
| `havesweepresult` | Check sweep result exists | All |
| `copysweep` | Copy sweep | All |
| `deletesweep` | Delete sweep | All |
| `exportsweep` | Export sweep data | All |
| `loadsweep` | Load sweep | All |
| `savesweep` | Save sweep | All |

### 9. Optimization (~10 commands)

| Command | Description | Product |
|---------|-------------|---------|
| `runoptimization` | Run optimization | All |
| `optimizeposition` | Optimize position | All |
| `addsweep` | Sweep (used for optimization) | All |

### 10. INTERCONNECT-Specific (~20 commands)

| Command | Description | Product |
|---------|-------------|---------|
| `addelement` | Add circuit element | INTERCONNECT |
| `addport` | Add port | INTERCONNECT |
| `addoptical` | Add optical connection | INTERCONNECT |
| `importnetlist` | Import netlist | INTERCONNECT |
| `exportnetlist` | Export netlist | INTERCONNECT |
| `importschematic` | Import schematic | INTERCONNECT |
| `exportschematic` | Export schematic | INTERCONNECT |
| `setconnectionrouting` | Set connection routing | INTERCONNECT |
| `cascadedsmatrix` | Cascade S-matrices | INTERCONNECT |
| `setsparameter` | Set S-parameter | INTERCONNECT |
| `getports` | Get port list | INTERCONNECT |

### 11. DEVICE-Specific (~20 commands)

| Command | Description | Product |
|---------|-------------|---------|
| `addchargesolver` | Add charge solver | DEVICE |
| `addheatsolver` | Add heat solver | DEVICE |
| `addchargemesh` | Add charge mesh | DEVICE |
| `addheatmesh` | Add heat mesh | DEVICE |
| `addchargemonitor` | Add charge monitor | DEVICE |
| `addtemperaturemonitor` | Add temperature monitor | DEVICE |
| `adddope` | Add doping | DEVICE |
| `addimportdope` | Import doping profile | DEVICE |
| `addelectricalcontact` | Add electrical contact | DEVICE |
| `addvoltagebc` | Add voltage BC | DEVICE |
| `addconvectionbc` | Add convection BC | DEVICE |
| `addheatfluxbc` | Add heat flux BC | DEVICE |
| `addthermalinsulatingbc` | Add thermal insulating BC | DEVICE |
| `addthermalpowerbc` | Add thermal power BC | DEVICE |
| `addtemperaturebc` | Add temperature BC | DEVICE |
| `addsurfacerecombinationbc` | Add surface recombination BC | DEVICE |
| `addradiationbc` | Add radiation BC | DEVICE |
| `addbulkgen` | Add bulk generation | DEVICE |
| `adddeltachargesource` | Add delta charge source | DEVICE |
| `adddiffusion` | Add diffusion | DEVICE |
| `adduniformheat` | Add uniform heat source | DEVICE |

### 12. Math & Utility (~100 commands)

| Category | Commands |
|----------|----------|
| Trigonometry | `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2` |
| Exponential | `exp`, `log`, `log10`, `sqrt` |
| Complex | `real`, `imag`, `conj`, `abs`, `angle` |
| Rounding | `ceil`, `floor`, `round`, `sign`, `mod` |
| Statistics | `min`, `max`, `mean`, `std`, `var`, `sum`, `prod` |
| Matrix | `matrix`, `ones`, `zeros`, `eye`, `transpose`, `ctranspose`, `inv`, `eig`, `svd`, `chol`, `det` |
| Signal | `fft`, `invfft`, `fftw`, `fftk`, `czt` |
| Interpolation | `interp`, `interptri`, `interptet`, `spline` |
| Integration | `integrate`, `integrate2` |
| Polynomial | `polyfit`, `polydiff`, `polydft` |
| Special | `besselj`, `bessely`, `besseli`, `besselk`, `erf`, `erfc`, `erfinv`, `erfcinv` |
| Random | `rand`, `randn`, `randmatrix`, `randnmatrix`, `randreset` |
| String | `num2str`, `str2num`, `format`, `substring`, `replace`, `replacestring`, `splitstring`, `upper`, `lower`, `findstring` |
| File I/O | `read`, `write`, `readdata`, `savedata`, `loaddata`, `fileexists`, `filebasename`, `filedirectory`, `fileextension`, `fileexpand` |
| Path | `cd`, `pwd`, `ls`, `cp`, `mv`, `rm`, `mkdir` |
| Variable | `clear`, `exist`, `length`, `size`, `which`, `global` |
| Flow | `if/elseif/else/endif`, `for/next`, `while/end`, `break`, `switch/case` |
| Other | `system`, `pause`, `now`, `version`, `help` |

### 13. Visualization & Export (~20 commands)

| Command | Description |
|---------|-------------|
| `plot` | Create 2D line plot |
| `plotxy` | Create XY plot |
| `polar` | Create polar plot |
| `polar2` | Create 2D polar plot |
| `polarimage` | Create polar image |
| `image` | Create image plot |
| `vectorplot` | Create vector plot |
| `bar` | Create bar chart |
| `histogram` | Create histogram |
| `legend` | Add legend to plot |
| `holdon`/`holdoff` | Control plot overlays |
| `selectfigure` | Select figure |
| `exportfigure` | Export figure |
| `exportimage` | Export image |
| `exportcsvresults` | Export CSV data |
| `exporthtml` | Export HTML report |
| `visualize` | Visualize data |
| `animate` | Create animation |
| `movie` | Create movie |
| `copytoclipboard` | Copy to clipboard |
| `pastefromclipboard` | Paste from clipboard |

## Method Calling Conventions

### Constructor Commands (objects)
```python
# Supports 'properties' keyword for initialization
session.addrect(properties=OrderedDict([("x", 0), ("x span", 1e-6)]))
```

### Regular Commands
```python
# Positional arguments only
session.sin(0.5)
session.abs(-5)
session.exp(2.0)
```

### Script-only Commands (via eval)
Python reserved words and deprecated commands must be called via eval:
```python
session.eval("for(i=0:10) { ... }")
session.eval("if(x > 0) { ... }")
session.eval("clear;")  # 'clear' is registered but eval is universal
```
