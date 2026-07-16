# MCP Server Architecture — Design Decisions

> Documents the key architectural decisions made during development.

## Decision 1: FastMCP over raw mcp Server

**Choice**: `mcp.server.fastmcp.FastMCP` (the COMSOL MCP pattern)

**Rationale**:
- `@mcp.tool()` decorator pattern is cleaner than manual handler registration
- Automatic JSON schema generation from type hints + docstrings
- Consistent with the COMSOL MCP reference implementation
- Less boilerplate per tool

**Trade-off**: Magic behavior of FastMCP can hide issues. We use explicit
`register_all_tools()` pattern rather than auto-discovery.

## Decision 2: Singleton SessionManager

**Choice**: Thread-safe singleton with per-session locks

```python
class SessionManager:
    _instance = None
    _lock = threading.Lock()
    _sessions: dict[str, SessionInfo] = {}
```

**Rationale**:
- Lumerical sessions are stateful, long-lived objects
- Multiple MCP tool calls may arrive concurrently
- Each session gets its own `threading.Lock` for thread safety
- Singleton ensures global session visibility across all tool modules

**Trade-off**: Singleton pattern is global state, which makes testing harder.
Mitigated by making the Singleton replaceable in tests.

## Decision 3: Direct lumapi vs pyLumerical

**Choice**: Use legacy `lumapi.py` from Lumerical installation directly

**Rationale**:
- No additional pip dependency (lumapi ships with Lumerical)
- Zero version mismatch risk between lumapi and installed Lumerical
- pyLumerical (`ansys-lumerical-core`) is essentially a thin wrapper
  that re-exports lumapi anyway
- The MCP server handles path auto-discovery itself

**Trade-off**: Manual sys.path manipulation at startup. Mitigated by
robust auto-discovery with fallback paths and clear error messages.

## Decision 4: Two-Level Tool Architecture

**Choice**: Structured tools (e.g., `lumerical_add_source`) PLUS
direct eval (e.g., `lumerical_eval`) for full coverage

**Rationale**:
- Structured tools: better UX, self-documenting, type-safe for common operations
- `lumerical_eval`: escape hatch for any operation not covered by structured tools
- `lumerical_call`: structured variant for calling by command name with args
- Together they cover 100% of Lumerical's ~480 commands

**Coverage**:
- Structured tools: ~40 tools covering ~80% of common workflows
- `lumerical_eval`/`lumerical_call`: covers the remaining 20% (and all 480+ commands)

## Decision 5: Per-Session Locking (not Global Lock)

**Choice**: Each session has its own `threading.Lock()`

**Rationale**:
- Multiple sessions can run in parallel (FDTD + MODE simultaneously)
- Only concurrent access to the SAME session is serialized
- This maximizes throughput for multi-session workflows

```python
with info.lock:
    info.handle.eval(code)
```

## Decision 6: Graceful Degradation Without Lumerical

**Choice**: All tools return structured `{"success": False, "error": "..."}`
responses when Lumerical is unavailable

**Rationale**:
- The MCP server can be developed and tested without Lumerical installed
- Documentation tools (lumerical_list_commands, etc.) work offline
- Clear error messages guide users to fix configuration
- The Skill provides troubleshooting guidance

## Decision 7: Documentation Integration

**Choice**: Hybrid documentation from two sources:
1. `docs.json` (bundled with Lumerical): always available, 480+ entries
2. `lumerical-docs/` Markdown files: richer content, 727 entries

**Rationale**:
- docs.json is guaranteed to match the installed Lumerical version
- Markdown docs provide much more detail (syntax, examples, see-also)
- Fallback to docs.json-only when Markdown repo is not cloned
- Search across both sources via `lumerical_search_commands`

## Decision 8: JSON Serialization for Complex Arguments

**Choice**: Tool parameters that accept structured data use JSON strings

**Example**:
```python
def lumerical_add(object_type: str, properties: str = "{}") -> dict:
    props = json.loads(properties)
```

**Rationale**:
- MCP tool parameters must be JSON-serializable primitives
- Nested dicts/lists can't be passed directly as tool arguments
- JSON strings provide a clean serialization boundary
- Error handling catches malformed JSON

**Trade-off**: Less ergonomic than native dicts. Mitigated by detailed
docstrings showing exact JSON format.

## Decision 9: Tool Naming Convention

**Choice**: All tools prefixed with `lumerical_`

**Rationale**:
- Prevents name collisions with other MCP servers
- Clear namespace in Claude Code tool listings
- Consistent with COMSOL MCP pattern (`comsol_` prefix)
- Easy to discover: user can search for all Lumerical tools at once

## Decision 10: No Asynchronous Lumerical Operations

**Choice**: All lumapi calls are synchronous, wrapped in thread locks

**Rationale**:
- lumapi uses ctypes and is inherently synchronous
- The C interop DLL does not support async operations
- Async wrappers would add complexity without benefit
- Long-running operations (simulations) run in Lumerical's own thread pool

## Tool Count Rationale

| Tool Domain | Count | Why This Number |
|-------------|-------|----------------|
| Session | 4 | Open, Close, List, CloseAll — minimal viable set |
| Script | 4 | Eval, GetVar, SetVar, Call — covers all 480 commands |
| Simulation | 6 | Full lifecycle: Load→Run→Save→Reset→Switch→Cd |
| Geometry | 10 | CRUD + transforms for all object types |
| Material | 6 | Add, Set, Get, Import, Index query, Transmission calc |
| Source/Monitor | 4 | Add source, add monitor, global configs |
| Solver | 4 | Solver creation, mesh, boundary, analysis config |
| Results | 6 | Results, raw data, fields, export, far-field, transmission |
| Optimization | 6 | Sweep config, run, results, optimization, parallel |
| Docs | 6 | List, categories, help, search, markdown, examples |
| **Total** | **56** | |
