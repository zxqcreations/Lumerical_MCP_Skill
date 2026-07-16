# lumapi.py — Lumerical Python API Reference

> Source: `D:\ENV\Lumerical\v202\api\python\lumapi.py` (1310 lines)
> This is the CORE Python API for all Lumerical automation.

## Architecture

lumapi.py uses **ctypes** to interface with Lumerical's native C library (`interopapi.dll` on Windows).
It dynamically registers ALL Lumerical script commands (~480+) as Python methods on session objects.

### Key C Functions (via ctypes CDLL)

| Function | Purpose |
|----------|---------|
| `appOpen(url, key)` | Opens a Lumerical application session |
| `appClose(handle)` | Closes a session |
| `appOpened(handle)` | Checks if session is valid |
| `appEvalScript(handle, code)` | Evaluates LSF script code |
| `appGetVar(handle, name, &value)` | Gets a variable value |
| `appPutVar(handle, name, &value)` | Sets a variable value |
| `appGetLastError()` | Gets last error message |
| `allocateLumDouble/LumString/LumMatrix/etc.` | Memory allocation for data types |
| `freeAny(ptr)` | Frees allocated memory |

### Data Types (ctypes Structures)

| Type | C Type | Python Equivalent |
|------|--------|-------------------|
| `LumString` | struct {len, *char} | Python str |
| `LumMat` | struct {mode, dim, *dimlst, *data} | numpy.ndarray |
| `LumStruct` | struct {size, **elements} | Python dict |
| `LumList` | struct {size, **elements} | Python list |
| `LumNameValuePair` | struct {name, *value} | dict key-value pair |
| `Any` | union {doubleVal, strVal, matrixVal, structVal, listVal} | Any type |

## Product URLs

When opening a session, lumapi constructs a URL:
```
fdtd://localhost?server=true       → FDTD
mode://localhost?server=true       → MODE
device://localhost?server=true     → DEVICE
interconnect://localhost?server=true → INTERCONNECT
```

Optional parameters:
- `&hide` — hide the GUI
- `&feature=<key>` — license feature key
- `&threads=N` — number of threads (via serverArgs dict)

## Class Hierarchy

```
Lumerical (base class)
├── FDTD(Lumerical)
├── MODE(Lumerical)
├── DEVICE(Lumerical)
└── INTERCONNECT(Lumerical)
```

### Lumerical Base Class Methods

| Method | Signature | Purpose |
|--------|-----------|---------|
| `__init__` | `(product, filename, key, hide, serverArgs, **kwargs)` | Open session |
| `close()` | `()` | Close session |
| `eval(code)` | `(code: str)` | Execute LSF script |
| `getv(varname)` | `(name: str) -> Any` | Get variable value |
| `putv(varname, value)` | `(name: str, value: Any)` | Set variable value |
| `getObjectById(id)` | `(id: str) -> SimObject` | Get simulation object |
| `getObjectBySelection()` | `() -> SimObject` | Get selected object |
| `getAllSelectedObjects()` | `() -> list[SimObject]` | Get all selected |

### Context Manager Support
```python
with lumapi.FDTD() as session:
    session.eval("run;")
# Auto-closes on exit
```

### Dynamic Method Registration

All Lumerical script commands (~480+) are dynamically added as methods.
Commands like `addfdtd`, `addrect`, `set`, `get`, `run`, etc. become
`session.addfdtd()`, `session.addrect()`, `session.set()` etc.

**Constructor commands** (that create objects) use `appCallWithConstructor`:
```python
# In lumapi.py, these are listed in addScriptCommands:
addScriptCommands = [
    'add2drect', 'add2dpoly', 'addabsorbing', 'addanalysisgroup',
    'addcircle', 'adddipole', 'addelement', 'addfdtd', 'addfde',
    'addgaussian', 'addgroup', 'addmesh', 'addmode', 'addplanarsolid',
    'addpoly', 'addpower', 'addprofile', 'addpyramid', 'addrect',
    'addring', 'addsphere', 'addstructuregroup', 'addsurface',
    'addtriangle', 'addwaveguide', ...  # ~80 commands total
]
```

These support an additional `properties` keyword argument:
```python
session.addrect(properties=OrderedDict([("x", 0), ("y", 0), ("x span", 1e-6)]))
```

**Regular commands** use `appCall`:
All other commands (math, utility, etc.) take positional args:
```python
session.sin(0.5)  # calls sin(0.5) in Lumerical
session.abs(-5)   # calls abs(-5) in Lumerical
```

### Keyword Exclusions (Python reserved words)
```
for, if, else, exit, break, del, eval, try, catch, assert, end, true, false, isnull
```
These Lumerical keywords are excluded from method creation.

### Deprecated Commands (excluded)
```
addbc, addcontact, addeigenmode, addpropagator, deleteallbc, deletebc,
getasapdata, getbc, getcompositionfraction, getcontact, getglobal,
importdoping, lum2mat, monitors, new2d, new3d, newmode,
removepropertydependency, setbc, setcompositionfraction, setcontact,
setglobal, setsolver, setparallel, showdata, skewness, sources, structures
```

## Object Model

### SimObject
Represents a simulation object in the object tree:
```python
obj = session.getObjectById("::model::rect1")
obj.x       # Get property "x"
obj.y       # Get property "y"
obj.x = 0.5 # Set property "x"
obj.results # Access simulation results
obj.getParent()  # Get parent object
obj.getChildren() # Get child objects
```

### SimObjectResults
Access results of a simulation object:
```python
obj.results.T          # Transmission result
obj.results.transmission # Same (underscore → space conversion)
```

### GetSetHelper
For nested properties with dot notation:
```python
obj.x_span              # Property "x span"
obj.material            # Material property
```

## Key Translator Classes

### PutTranslator
Converts Python types → Lumerical native types:
- `float/int` → `allocateLumDouble`
- `str` → `allocateLumString`
- `numpy.ndarray` → `allocateLumMatrix` (or Complex)
- `dict` → struct via `allocateLumStruct`
- `list` → cell array via `allocateLumList`

### GetTranslator
Converts Lumerical native types → Python types:
- `LumString` → Python str
- `LumMat` → numpy.ndarray
- `LumStruct` → Python dict
- `LumList` → Python list

### Dataset Translators
Handle the complex data structures returned by monitors:
- `MatrixDatasetTranslator` — Matrix result data
- `RectilinearDatasetTranslator` — Spatially rectilinear results
- `UnstructuredDatasetTranslator` — Unstructured mesh results
- `PointDatasetTranslator` — Point cloud data

## Environment & Path Resolution

### Windows
```python
INTEROPLIBDIR = <api/python directory>
LUMERICALDIR  = <api/python>/../../
MODERN_LUMLDIR = <LUMERICALDIR>/bin
LEGACY_FDTDDIR = <LUMERICALDIR>/../fdtd/bin
LEGACY_MODEDIR = <LUMERICALDIR>/../mode/bin
LEGACY_DEVCDIR = <LUMERICALDIR>/../device/bin
LEGACY_INTCDIR = <LUMERICALDIR>/../interconnect/bin
INTEROPLIB = "interopapi.dll"
```

DLLs from all these directories are added to PATH temporarily when
opening a session, using the `environ()` context manager.

## Error Handling

```python
class LumApiError(Exception):
    """Base exception for all Lumerical API errors."""
```

Common error sources:
- `verifyConnection(handle)` — checks `appOpened()` before operations
- `appEvalScript` return < 0 → "Failed to evaluate code"
- `appGetVar` return < 0 → "Failed to get variable"
- `appPutVar` return < 0 → "Failed to put variable"
- `appOpen` → reads error from `appGetLastError()`

Error message cleanup:
```python
def removePromptLineNo(strval):
    # Removes "prompt line N:" prefix from error messages
```

## Important Notes

1. **32-bit Python is not supported** — the module checks `sys.maxsize > 2**32`
2. **Complex numbers** use a special `allocateComplexLumMatrix` for imaginary data
3. **numpy** is required — all matrix data is converted to/from numpy arrays
4. **Fortran order** arrays — matrices use column-major (Fortran) ordering
5. **The `open` builtin** is shadowed — saved as `biopen` before redefinition
6. **Thread safety** — there is NO built-in thread safety; concurrent access to the same session requires external locking
