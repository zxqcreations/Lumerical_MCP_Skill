"""Session manager for Lumerical MCP Server.

Manages lifecycle of Lumerical product sessions (FDTD, MODE, DEVICE, INTERCONNECT).
Each session wraps a lumapi.Lumerical instance and supports concurrent access
via per-session locks.

v261 Update: Supports ANSYS Inc v261 installation path, remoteArgs for remote
Interop Server connections, keepCADOpened for persistent CAD, script/project
startup kwargs, and API version detection.
"""

import logging
import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Locate Lumerical API path
# Priority: LUMERICAL_HOME env var > v261 ANSYS Inc paths > legacy paths
_LUMERICAL_API_PATH: Optional[str] = None


def _find_lumerical_api() -> Optional[str]:
    """Auto-discover Lumerical Python API path.

    Search order:
    1. LUMERICAL_HOME environment variable
    2. ANSYS Inc v261 (2026R1) — primary
    3. ANSYS Inc v261 alternate location
    4. Legacy Lumerical paths (v202–v251) — backward compatibility

    Returns:
        str path to api/python directory, or None
    """
    global _LUMERICAL_API_PATH
    if _LUMERICAL_API_PATH:
        return _LUMERICAL_API_PATH

    # Check LUMERICAL_HOME environment variable
    lumerical_home = os.environ.get("LUMERICAL_HOME")
    if lumerical_home:
        candidate = Path(lumerical_home) / "api" / "python"
        if candidate.exists():
            _LUMERICAL_API_PATH = str(candidate)
            logger.info(f"Lumerical API found via LUMERICAL_HOME: {_LUMERICAL_API_PATH}")
            return _LUMERICAL_API_PATH

    # Check installation paths — v261 first, then legacy fallbacks
    candidates = [
        # v261 (2026R1) — ANSYS Inc unified installation
        Path(r"D:\ENV\Lumerical\ANSYS Inc\v261\Lumerical\api\python"),
        Path(r"C:\Program Files\ANSYS Inc\v261\Lumerical\api\python"),
        # Legacy Lumerical standalone installations
        Path(r"D:\ENV\Lumerical\v251\api\python"),
        Path(r"C:\Program Files\Lumerical\v251\api\python"),
        Path(r"D:\ENV\Lumerical\v242\api\python"),
        Path(r"C:\Program Files\Lumerical\v242\api\python"),
        Path(r"D:\ENV\Lumerical\v241\api\python"),
        Path(r"C:\Program Files\Lumerical\v241\api\python"),
        Path(r"D:\ENV\Lumerical\v232\api\python"),
        Path(r"C:\Program Files\Lumerical\v232\api\python"),
        Path(r"D:\ENV\Lumerical\v231\api\python"),
        Path(r"C:\Program Files\Lumerical\v231\api\python"),
        Path(r"D:\ENV\Lumerical\v222\api\python"),
        Path(r"C:\Program Files\Lumerical\v222\api\python"),
        Path(r"D:\ENV\Lumerical\v221\api\python"),
        Path(r"C:\Program Files\Lumerical\v221\api\python"),
        Path(r"D:\ENV\Lumerical\v202\api\python"),
        Path(r"C:\Program Files\Lumerical\v202\api\python"),
    ]
    for candidate in candidates:
        if candidate.exists():
            _LUMERICAL_API_PATH = str(candidate)
            logger.info(f"Lumerical API found at: {_LUMERICAL_API_PATH}")
            return _LUMERICAL_API_PATH

    return None


def get_lumerical_api_path() -> str:
    """Get the Lumerical Python API path, raising if not found."""
    path = _find_lumerical_api()
    if not path:
        raise RuntimeError(
            "Cannot find Lumerical installation. Please ensure:\n"
            "  1. Lumerical v261+ is installed (ANSYS Inc suite), or\n"
            "  2. Set LUMERICAL_HOME environment variable to the root directory.\n"
            "     e.g., set LUMERICAL_HOME=D:\\ENV\\Lumerical\\ANSYS Inc\\v261\n"
            "     (point to the v261 root, NOT api/python)"
        )
    return path


def get_lumerical_bin_path() -> Optional[str]:
    """Get the Lumerical binary directory path (v261+).

    Returns:
        Path to Lumerical/bin/ directory, or None if not found.
    """
    api_path = _find_lumerical_api()
    if api_path:
        bin_path = Path(api_path).parent.parent / "bin"
        if bin_path.exists():
            return str(bin_path)
    return None


def get_lumerical_python_path() -> Optional[str]:
    """Get the bundled Python path (v261+ bundles Python 3.13.1).

    Returns:
        Path to python.exe in the bundled Python, or None.
    """
    api_path = _find_lumerical_api()
    if api_path:
        # v261: .../v261/Lumerical/api/python -> .../v261/Lumerical/python-3.13.1/python.exe
        python_dir = Path(api_path).parent.parent / "python-3.13.1"
        if python_dir.exists():
            python_exe = python_dir / "python.exe"
            if python_exe.exists():
                return str(python_exe)
        # Also check the 'python' symlink
        python_symlink = Path(api_path).parent.parent / "python"
        if python_symlink.exists():
            python_exe = python_symlink / "python.exe"
            if python_exe.exists():
                return str(python_exe)
    return None


def get_cml_compiler_path() -> Optional[str]:
    """Get the CML Compiler binary directory path (v261+).

    Returns:
        Path to CML_Compiler/bin/ directory, or None.
    """
    api_path = _find_lumerical_api()
    if api_path:
        cml_bin = Path(api_path).parent.parent / "CML_Compiler" / "bin"
        if cml_bin.exists():
            return str(cml_bin)
    return None


def get_intel_mpi_path() -> Optional[str]:
    """Get the Intel MPI binary directory path (v261+).

    Returns:
        Path to intel_mpi/bin/ directory, or None.
    """
    api_path = _find_lumerical_api()
    if api_path:
        mpi_bin = Path(api_path).parent.parent / "intel_mpi" / "bin"
        if mpi_bin.exists():
            return str(mpi_bin)
    return None


class SessionInfo:
    """Information about an active Lumerical session."""

    def __init__(self, session_id: str, product: str, handle: Any) -> None:
        self.session_id = session_id
        self.product = product  # 'fdtd', 'mode', 'device', 'interconnect'
        self.handle = handle  # lumapi.FDTD(), lumapi.MODE(), etc.
        self.created_at = time.time()
        self.lock = threading.Lock()  # Per-session lock for thread safety
        self.file_loaded: Optional[str] = None
        self.api_version: Optional[tuple] = None

    @property
    def age_seconds(self) -> float:
        return time.time() - self.created_at

    def to_dict(self) -> dict:
        result = {
            "session_id": self.session_id,
            "product": self.product,
            "created_at": self.created_at,
            "age_seconds": round(self.age_seconds, 1),
            "file_loaded": self.file_loaded,
        }
        if self.api_version:
            result["api_version"] = f"{self.api_version[0]}.{self.api_version[1]}"
        return result


class SessionManager:
    """Singleton manager for Lumerical sessions.

    Supports multiple concurrent sessions to different Lumerical products.
    Thread-safe via per-session locks.

    v261 features:
    - remoteArgs for remote Interop Server connections
    - keepCADOpened for persistent CAD across scripts
    - script/project kwargs for startup execution
    - API version detection
    """

    _instance: Optional["SessionManager"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "SessionManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._sessions: dict[str, SessionInfo] = {}
                    cls._instance._counter = 0
        return cls._instance

    def _next_id(self) -> str:
        self._counter += 1
        return f"lum_{self._counter}"

    @property
    def session_count(self) -> int:
        return len(self._sessions)

    def _ensure_api_in_path(self) -> None:
        """Add Lumerical API to sys.path if not already present."""
        api_path = get_lumerical_api_path()
        if api_path not in sys.path:
            sys.path.insert(0, api_path)
            logger.info(f"Added {api_path} to sys.path")

    def open(
        self,
        product: str,
        hide: bool = False,
        server_args: Optional[dict] = None,
        remote_args: Optional[dict] = None,
        keep_cad_opened: bool = False,
        script: Optional[str] = None,
        project: Optional[str] = None,
    ) -> dict:
        """Open a new Lumerical session.

        Args:
            product: One of 'fdtd', 'mode', 'device', 'interconnect'
            hide: Whether to hide the Lumerical GUI
            server_args: Additional server arguments as dict
                (e.g., {'threads': 4, 'use-solve': True})
            remote_args: Remote Interop Server connection info as dict
                (e.g., {'hostname': '192.168.1.100', 'port': 8989})
            keep_cad_opened: If True, CAD remains open after Python exits
            script: Path to script file (.lsf or .py) to execute on startup
            project: Path to project file (.fsp, .lms, etc.) to load on startup

        Returns:
            dict with session info or error
        """
        product = product.lower().strip()
        valid_products = ["fdtd", "mode", "device", "interconnect"]
        if product not in valid_products:
            return {
                "success": False,
                "error": (
                    f"Invalid product '{product}'. "
                    f"Must be one of: {', '.join(valid_products)}"
                ),
            }

        self._ensure_api_in_path()

        try:
            import lumapi
        except ImportError as e:
            return {
                "success": False,
                "error": (
                    f"Cannot import lumapi. Tried path: {get_lumerical_api_path()}. "
                    f"Error: {e}. Ensure Lumerical is installed and LUMERICAL_HOME is set."
                ),
            }

        session_id = self._next_id()
        server_args = server_args or {}
        remote_args = remote_args or {}

        # Add keepCADOpened to server_args if requested
        if keep_cad_opened:
            server_args["keepCADOpened"] = True

        try:
            # Determine the lumapi class to use
            product_class_map = {
                "fdtd": lumapi.FDTD,
                "mode": lumapi.MODE,
                "device": lumapi.DEVICE,
                "interconnect": lumapi.INTERCONNECT,
            }
            product_class = product_class_map[product]

            # Build kwargs for constructor
            kwargs = {
                "hide": hide,
                "serverArgs": server_args,
            }

            # Add remoteArgs if specified (v261+ feature)
            if remote_args:
                kwargs["remoteArgs"] = remote_args

            # Add project/script if specified (v261+ feature)
            if project:
                kwargs["project"] = project
            if script:
                kwargs["script"] = script

            handle = product_class(**kwargs)

        except TypeError as e:
            # Handle case where remoteArgs/project/script kwargs
            # aren't supported (older lumapi versions)
            if "remoteArgs" in str(e) or "project" in str(e) or "script" in str(e):
                logger.warning(
                    f"v261 kwargs not supported by this lumapi version: {e}. "
                    f"Falling back to base arguments."
                )
                try:
                    if product == "fdtd":
                        handle = lumapi.FDTD(hide=hide, serverArgs=server_args)
                    elif product == "mode":
                        handle = lumapi.MODE(hide=hide, serverArgs=server_args)
                    elif product == "device":
                        handle = lumapi.DEVICE(hide=hide, serverArgs=server_args)
                    elif product == "interconnect":
                        handle = lumapi.INTERCONNECT(
                            hide=hide, serverArgs=server_args
                        )
                    else:
                        return {
                            "success": False,
                            "error": f"Unknown product: {product}",
                        }
                except Exception as fallback_e:
                    return {
                        "success": False,
                        "error": f"Failed to open {product} session: {fallback_e}",
                    }
            else:
                return {
                    "success": False,
                    "error": f"Failed to open {product} session: {e}",
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to open {product} session: {e}",
            }

        info = SessionInfo(session_id, product, handle)
        self._sessions[session_id] = info

        # Detect API version
        try:
            import lumapi as lm
            info.api_version = lm.getApiVersion(info.handle.handle)
        except Exception:
            pass

        logger.info(f"Opened {product} session: {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "product": product,
            "message": f"Opened {product.upper()} session: {session_id}",
        }

    def close(self, session_id: str) -> dict:
        """Close a specific Lumerical session.

        Args:
            session_id: The session ID to close

        Returns:
            dict with result
        """
        info = self._sessions.get(session_id)
        if info is None:
            return {"success": False, "error": f"Session '{session_id}' not found."}

        try:
            with info.lock:
                info.handle.close()
        except Exception as e:
            logger.warning(f"Error closing session {session_id}: {e}")
        finally:
            del self._sessions[session_id]

        logger.info(f"Closed session: {session_id}")
        return {"success": True, "message": f"Closed session: {session_id}"}

    def close_all(self) -> dict:
        """Close all active sessions.

        Returns:
            dict with result
        """
        session_ids = list(self._sessions.keys())
        results = []
        for sid in session_ids:
            result = self.close(sid)
            results.append(result)
        return {
            "success": True,
            "message": f"Closed {len(results)} session(s)",
            "results": results,
        }

    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session info by ID."""
        return self._sessions.get(session_id)

    def list_sessions(self) -> dict:
        """List all active sessions.

        Returns:
            dict with sessions list
        """
        sessions = [info.to_dict() for info in self._sessions.values()]
        return {
            "success": True,
            "count": len(sessions),
            "sessions": sessions,
        }

    def is_connected(self, session_id: str) -> dict:
        """Check if a session is still connected and responsive.

        Args:
            session_id: Session ID

        Returns:
            dict with connection status
        """
        info = self._sessions.get(session_id)
        if info is None:
            return {
                "success": False,
                "connected": False,
                "error": f"Session '{session_id}' not found.",
            }

        try:
            import lumapi
            with info.lock:
                lumapi.verifyConnection(info.handle.handle)
            return {
                "success": True,
                "connected": True,
                "message": f"Session '{session_id}' is connected.",
            }
        except Exception as e:
            return {
                "success": True,
                "connected": False,
                "message": f"Session '{session_id}' appears disconnected: {e}",
            }

    def get_api_version(self, session_id: str) -> dict:
        """Get the lumapi API version for a session.

        Args:
            session_id: Session ID

        Returns:
            dict with major, minor version
        """
        info = self._sessions.get(session_id)
        if info is None:
            return {"success": False, "error": f"Session '{session_id}' not found."}

        if info.api_version:
            return {
                "success": True,
                "major": info.api_version[0],
                "minor": info.api_version[1],
                "version_string": f"{info.api_version[0]}.{info.api_version[1]}",
            }

        try:
            import lumapi
            with info.lock:
                major, minor = lumapi.getApiVersion(info.handle.handle)
                info.api_version = (major, minor)
            return {
                "success": True,
                "major": major,
                "minor": minor,
                "version_string": f"{major}.{minor}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get API version: {e}",
            }

    def _verify_session(self, session_id: str) -> SessionInfo:
        """Get session, raising error if not found."""
        info = self._sessions.get(session_id)
        if info is None:
            raise ValueError(
                f"Session '{session_id}' not found. "
                f"Active sessions: {list(self._sessions.keys())}"
            )
        return info

    def eval(self, session_id: str, code: str) -> dict:
        """Execute Lumerical script code in a session.

        Args:
            session_id: Session ID
            code: Lumerical script code to execute

        Returns:
            dict with result
        """
        try:
            info = self._verify_session(session_id)
            with info.lock:
                info.handle.eval(code)
            return {"success": True, "message": "Script executed successfully."}
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Script execution failed: {e}"}

    def get_var(self, session_id: str, var_name: str) -> dict:
        """Get a variable value from a session.

        Args:
            session_id: Session ID
            var_name: Variable name

        Returns:
            dict with value/error
        """
        try:
            info = self._verify_session(session_id)
            with info.lock:
                value = info.handle.getv(var_name)
            return {"success": True, "variable": var_name, "value": value}
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get variable '{var_name}': {e}",
            }

    def set_var(self, session_id: str, var_name: str, value: Any) -> dict:
        """Set a variable value in a session.

        Args:
            session_id: Session ID
            var_name: Variable name
            value: Value to set (scalar, array, string, dict, list)

        Returns:
            dict with result
        """
        try:
            info = self._verify_session(session_id)
            with info.lock:
                info.handle.putv(var_name, value)
            return {"success": True, "message": f"Set variable '{var_name}'."}
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to set variable '{var_name}': {e}",
            }

    def call(self, session_id: str, command: str, *args: Any) -> dict:
        """Call a Lumerical script command directly.

        Args:
            session_id: Session ID
            command: Command name (e.g., 'addfdtd', 'addrect')
            *args: Positional arguments

        Returns:
            dict with result
        """
        try:
            info = self._verify_session(session_id)
            with info.lock:
                # Use the dynamically-added method on the handle
                method = getattr(info.handle, command, None)
                if method is None:
                    return {
                        "success": False,
                        "error": (
                            f"Unknown command '{command}'. "
                            f"Use lumerical_list_commands to see available commands."
                        ),
                    }
                result = method(*args)
            return {
                "success": True,
                "command": command,
                "result": str(result) if result is not None else None,
            }
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Command '{command}' failed: {e}"}

    def load(self, session_id: str, filepath: str) -> dict:
        """Load a project file into the session.

        Args:
            session_id: Session ID
            filepath: Path to .fsp, .lms, .icp, .dsp, or .lsf file

        Returns:
            dict with result
        """
        try:
            info = self._verify_session(session_id)
            path = Path(filepath)
            if not path.exists():
                return {"success": False, "error": f"File not found: {filepath}"}

            with info.lock:
                info.handle.load(str(path))
                info.file_loaded = filepath
            return {"success": True, "message": f"Loaded file: {filepath}"}
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Failed to load file: {e}"}

    def save(self, session_id: str, filepath: Optional[str] = None) -> dict:
        """Save the current project.

        Args:
            session_id: Session ID
            filepath: Optional path to save to

        Returns:
            dict with result
        """
        try:
            info = self._verify_session(session_id)
            with info.lock:
                if filepath:
                    info.handle.save(filepath)
                else:
                    info.handle.save()
            return {"success": True, "message": "Project saved."}
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Failed to save: {e}"}
