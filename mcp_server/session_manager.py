"""Session manager for Lumerical MCP Server.

Manages lifecycle of Lumerical product sessions (FDTD, MODE, DEVICE, INTERCONNECT).
Each session wraps a lumapi.Lumerical instance and supports concurrent access
via per-session locks.
"""

import logging
import sys
import threading
import time
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Locate Lumerical API path
# Priority: LUMERICAL_HOME env var > default installation paths
_LUMERICAL_API_PATH = None


def _find_lumerical_api() -> Optional[str]:
    """Auto-discover Lumerical Python API path."""
    global _LUMERICAL_API_PATH
    if _LUMERICAL_API_PATH:
        return _LUMERICAL_API_PATH

    import os

    # Check LUMERICAL_HOME environment variable
    lumerical_home = os.environ.get("LUMERICAL_HOME")
    if lumerical_home:
        candidate = Path(lumerical_home) / "api" / "python"
        if candidate.exists():
            _LUMERICAL_API_PATH = str(candidate)
            return _LUMERICAL_API_PATH

    # Check common installation paths
    candidates = [
        Path(r"D:\ENV\Lumerical\v202\api\python"),
        Path(r"C:\Program Files\Lumerical\v202\api\python"),
        Path(r"C:\Program Files\Lumerical\v221\api\python"),
        Path(r"C:\Program Files\Lumerical\v222\api\python"),
        Path(r"C:\Program Files\Lumerical\v231\api\python"),
        Path(r"C:\Program Files\Lumerical\v232\api\python"),
        Path(r"C:\Program Files\Lumerical\v241\api\python"),
        Path(r"C:\Program Files\Lumerical\v242\api\python"),
        Path(r"C:\Program Files\Lumerical\v251\api\python"),
    ]
    for candidate in candidates:
        if candidate.exists():
            _LUMERICAL_API_PATH = str(candidate)
            return _LUMERICAL_API_PATH

    return None


def get_lumerical_api_path() -> str:
    """Get the Lumerical Python API path, raising if not found."""
    path = _find_lumerical_api()
    if not path:
        raise RuntimeError(
            "Cannot find Lumerical installation. "
            "Set LUMERICAL_HOME environment variable to the Lumerical root directory, "
            "e.g., D:\\ENV\\Lumerical\\v202."
        )
    return path


class SessionInfo:
    """Information about an active Lumerical session."""

    def __init__(self, session_id: str, product: str, handle: Any) -> None:
        self.session_id = session_id
        self.product = product  # 'fdtd', 'mode', 'device', 'interconnect'
        self.handle = handle  # lumapi.FDTD(), lumapi.MODE(), etc.
        self.created_at = time.time()
        self.lock = threading.Lock()  # Per-session lock for thread safety
        self.file_loaded: Optional[str] = None

    @property
    def age_seconds(self) -> float:
        return time.time() - self.created_at

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "product": self.product,
            "created_at": self.created_at,
            "age_seconds": round(self.age_seconds, 1),
            "file_loaded": self.file_loaded,
        }


class SessionManager:
    """Singleton manager for Lumerical sessions.

    Supports multiple concurrent sessions to different Lumerical products.
    Thread-safe via per-session locks.
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

    def open(self, product: str, hide: bool = False,
             server_args: Optional[dict] = None) -> dict:
        """Open a new Lumerical session.

        Args:
            product: One of 'fdtd', 'mode', 'device', 'interconnect'
            hide: Whether to hide the Lumerical GUI
            server_args: Additional server arguments as dict

        Returns:
            dict with session info or error
        """
        product = product.lower().strip()
        valid_products = ["fdtd", "mode", "device", "interconnect"]
        if product not in valid_products:
            return {
                "success": False,
                "error": f"Invalid product '{product}'. Must be one of: {', '.join(valid_products)}",
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

        try:
            if product == "fdtd":
                handle = lumapi.FDTD(hide=hide, serverArgs=server_args)
            elif product == "mode":
                handle = lumapi.MODE(hide=hide, serverArgs=server_args)
            elif product == "device":
                handle = lumapi.DEVICE(hide=hide, serverArgs=server_args)
            elif product == "interconnect":
                handle = lumapi.INTERCONNECT(hide=hide, serverArgs=server_args)
            else:
                return {"success": False, "error": f"Unknown product: {product}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to open {product} session: {e}"}

        info = SessionInfo(session_id, product, handle)
        self._sessions[session_id] = info
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
        sessions = [
            info.to_dict() for info in self._sessions.values()
        ]
        return {
            "success": True,
            "count": len(sessions),
            "sessions": sessions,
        }

    def _verify_session(self, session_id: str) -> SessionInfo:
        """Get session, raising error if not found."""
        info = self._sessions.get(session_id)
        if info is None:
            raise ValueError(f"Session '{session_id}' not found. Active sessions: {list(self._sessions.keys())}")
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
            return {"success": False, "error": f"Failed to get variable '{var_name}': {e}"}

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
            return {"success": False, "error": f"Failed to set variable '{var_name}': {e}"}

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
                        "error": f"Unknown command '{command}'. Use lumerical_list_commands to see available commands.",
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
            filepath: Path to .fsp, .lms, .icp, or .lsf file

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
            return {"success": True, "message": f"Project saved."}
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Failed to save: {e}"}
