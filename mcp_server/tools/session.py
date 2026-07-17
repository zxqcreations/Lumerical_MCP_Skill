"""Session management tools for Lumerical MCP Server."""

import logging
from mcp.server.fastmcp import FastMCP

from ..session_manager import SessionManager

logger = logging.getLogger(__name__)


def register_session_tools(mcp: FastMCP) -> None:
    """Register session management tools."""

    @mcp.tool()
    def lumerical_open(
        product: str,
        hide: bool = False,
        server_args: str = "{}",
        cwd: str = "",
    ) -> dict:
        """Open a new Lumerical simulation session.

        Opens a connection to one of the Lumerical products. Each session is
        identified by a unique session_id that must be used in subsequent calls.

        Available products:
        - 'fdtd': FDTD Solutions (3D/2D finite-difference time-domain)
        - 'mode': MODE Solutions (waveguide mode solving, EME, varFDTD)
        - 'device': DEVICE Multiphysics (charge transport, heat, FEEM)
        - 'interconnect': INTERCONNECT (photonic circuit simulation)

        Args:
            product: Product to open ('fdtd', 'mode', 'device', 'interconnect')
            hide: If true, hide the Lumerical GUI window
            server_args: JSON string of additional server arguments
                (e.g., '{"threads": 4}')
            cwd: Working directory for file I/O (fopen, exportcsvresults, etc.).
                Defaults to the current working directory.

        Returns:
            dict with session_id, product, and status message
        """
        import json

        try:
            parsed_args = json.loads(server_args) if server_args else {}
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Invalid JSON in server_args: {e}"}

        session_mgr = SessionManager()
        kwargs = {"product": product, "hide": hide, "server_args": parsed_args}
        if cwd:
            kwargs["cwd"] = cwd
        return session_mgr.open(**kwargs)

    @mcp.tool()
    def lumerical_close(session_id: str) -> dict:
        """Close a specific Lumerical session.

        Closes the connection to Lumerical and frees resources.
        The session_id becomes invalid after this call.

        Args:
            session_id: The session ID returned by lumerical_open

        Returns:
            dict with status message
        """
        session_mgr = SessionManager()
        return session_mgr.close(session_id)

    @mcp.tool()
    def lumerical_close_all() -> dict:
        """Close all active Lumerical sessions.

        Use this to clean up all connections at once.

        Returns:
            dict with count of closed sessions
        """
        session_mgr = SessionManager()
        return session_mgr.close_all()

    @mcp.tool()
    def lumerical_list_sessions() -> dict:
        """List all active Lumerical sessions.

        Shows product type, session age, and loaded files for each session.

        Returns:
            dict with list of active sessions and their details
        """
        session_mgr = SessionManager()
        return session_mgr.list_sessions()

    logger.info("Registered session management tools")
