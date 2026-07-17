"""Script execution tools for Lumerical MCP Server."""

import logging
from mcp.server.fastmcp import FastMCP

from ..session_manager import SessionManager

logger = logging.getLogger(__name__)


def register_script_tools(mcp: FastMCP) -> None:
    """Register script execution tools."""

    @mcp.tool()
    def lumerical_eval(session_id: str, code: str) -> dict:
        """Execute Lumerical script code directly.

        This is the most powerful tool - you can run ANY Lumerical script command
        or sequence of commands using the native Lumerical Scripting Language (LSF).
        This includes commands like addfdtd, addrect, set, get, run, etc.

        **Automatic fallback**: If lumapi.eval() fails (which happens for certain
        solver commands like addfde, addfdtd, addeme in MODE product), this tool
        automatically falls back to direct Python API calls. Each command in the
        script is parsed and executed via getattr(handle, command)(*args).

        Use this when:
        - You need to run a sequence of commands together
        - The specific operation isn't available as a dedicated tool
        - You want to script a complete simulation workflow

        Note: For solver addition commands (addfde, addfdtd, addeme, etc.),
        you can also use lumerical_call for explicit direct API execution.

        Example code:
            addfdtd;
            set("dimension", 2);
            set("x", 0); set("x span", 2e-6);
            run;

        Args:
            session_id: The session ID from lumerical_open
            code: Lumerical script code to execute (one or more commands)

        Returns:
            dict with execution status. On eval failure, includes
            "method": "direct_api_fallback" and per-statement "results".
        """
        session_mgr = SessionManager()
        return session_mgr.eval(session_id, code)

    @mcp.tool()
    def lumerical_get_var(session_id: str, var_name: str) -> dict:
        """Get the value of a variable from the Lumerical session.

        Retrieves the current value of any variable in the Lumerical workspace.
        Supports scalar numbers, strings, arrays (numpy), structs, and cell arrays.

        Args:
            session_id: The session ID from lumerical_open
            var_name: Name of the variable to retrieve

        Returns:
            dict with variable name and its value
        """
        session_mgr = SessionManager()
        return session_mgr.get_var(session_id, var_name)

    @mcp.tool()
    def lumerical_set_var(session_id: str, var_name: str, value: str) -> dict:
        """Set a variable in the Lumerical session.

        Creates or updates a variable in the Lumerical workspace.
        The value is parsed as JSON for numbers, arrays, and objects,
        or treated as a string if not valid JSON.

        Examples of value strings:
        - "1.55e-6" (a number - wavelength in meters)
        - "3.14" (a number)
        - "[1, 2, 3]" (an array)
        - '{"x": 0, "y": 10}' (a struct/object)
        - '"hello"' (a string)

        Args:
            session_id: The session ID from lumerical_open
            var_name: Name of the variable to create/update
            value: Value to assign. JSON for structured data, otherwise string.

        Returns:
            dict with status
        """
        import json

        # Try to parse as JSON first for structured data
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            # Treat as plain string
            parsed = value

        session_mgr = SessionManager()
        return session_mgr.set_var(session_id, var_name, parsed)

    @mcp.tool()
    def lumerical_call(session_id: str, command: str, args: str = "[]") -> dict:
        """Call a specific Lumerical script command by name via direct Python API.

        This tool calls commands as direct Python methods on the Lumerical handle
        (e.g., handle.addfde()), which is more reliable than eval() for certain
        solver commands in MODE and other products.

        **Use this for solver commands** that may fail with lumerical_eval:
        - addfde, addfdtd, addeme, addvarfdtd (MODE/FDTD solvers)
        - addchargesolver, addheatsolver (DEVICE solvers)
        - addfeem, adddgdtd (other solvers)

        All ~665+ commands from the Lumerical scripting language are available.

        Commands include things like:
        - addfdtd, addrect, addcircle, addsphere (geometry)
        - addpower, addprofile, addindex (monitors)
        - addmode, adddipole, addgaussian (sources)
        - addmesh, addpml (simulation setup)
        - set, get, select (object manipulation)
        - run, save, load (simulation control)

        Args:
            session_id: The session ID from lumerical_open
            command: The Lumerical command name (e.g., 'addfdtd', 'addrect')
            args: JSON array of positional arguments (e.g., '[1, 2, "text"]')

        Returns:
            dict with command result
        """
        import json

        try:
            parsed_args = json.loads(args)
            if not isinstance(parsed_args, list):
                parsed_args = [parsed_args]
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON in args: {args}"}

        session_mgr = SessionManager()
        return session_mgr.call(session_id, command, *parsed_args)

    logger.info("Registered script execution tools")
