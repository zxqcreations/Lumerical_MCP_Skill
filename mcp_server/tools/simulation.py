"""Simulation lifecycle tools for Lumerical MCP Server."""

import logging
from mcp.server.fastmcp import FastMCP

from ..session_manager import SessionManager

logger = logging.getLogger(__name__)


def register_simulation_tools(mcp: FastMCP) -> None:
    """Register simulation lifecycle tools."""

    @mcp.tool()
    def lumerical_run(session_id: str) -> dict:
        """Run the current simulation.

        Executes the solver(s) configured in the current project.
        For FDTD: runs the FDTD solver region
        For MODE: runs the active solver (FDE, EME, varFDTD)
        For DEVICE: runs the coupled multiphysics solver
        For INTERCONNECT: runs the circuit simulation

        This may take significant time depending on simulation complexity.
        Use lumerical_get_result to retrieve results after completion.

        Args:
            session_id: The session ID from lumerical_open

        Returns:
            dict with run status
        """
        session_mgr = SessionManager()
        return session_mgr.eval(session_id, "run;")

    @mcp.tool()
    def lumerical_load(session_id: str, filepath: str) -> dict:
        """Load a project file into the session.

        Supports Lumerical project files:
        - .fsp (FDTD project)
        - .lms (MODE project)
        - .icp (INTERCONNECT project)
        - .dsp (DEVICE project)
        - .lsf (Lumerical script file - will be executed)
        - .lsfx (encrypted script file)

        Args:
            session_id: The session ID from lumerical_open
            filepath: Path to the file to load

        Returns:
            dict with load status
        """
        session_mgr = SessionManager()
        return session_mgr.load(session_id, filepath)

    @mcp.tool()
    def lumerical_save(session_id: str, filepath: str = "") -> dict:
        """Save the current project.

        Saves the current simulation project. If filepath is provided,
        saves to that path. Otherwise saves to the current file.

        Args:
            session_id: The session ID from lumerical_open
            filepath: Optional path to save to. If empty, saves to current file.

        Returns:
            dict with save status
        """
        session_mgr = SessionManager()
        if filepath:
            return session_mgr.save(session_id, filepath)
        else:
            return session_mgr.eval(session_id, "save;")

    @mcp.tool()
    def lumerical_reset(session_id: str) -> dict:
        """Reset the simulation to initial state.

        Clears the current simulation data, keeping the simulation setup.
        Equivalent to closing and reopening the project.

        Args:
            session_id: The session ID from lumerical_open

        Returns:
            dict with status
        """
        session_mgr = SessionManager()
        return session_mgr.eval(session_id, "clear;")

    @mcp.tool()
    def lumerical_switch_to_layout(session_id: str) -> dict:
        """Switch to layout mode (for photonic circuit design).

        In layout mode, you can place components from libraries,
        create waveguides, and design integrated photonic circuits.

        Args:
            session_id: The session ID from lumerical_open

        Returns:
            dict with status
        """
        session_mgr = SessionManager()
        return session_mgr.eval(session_id, "switchtolayout;")

    @mcp.tool()
    def lumerical_cd(session_id: str, path: str) -> dict:
        """Change the working directory of the Lumerical session.

        Args:
            session_id: The session ID from lumerical_open
            path: New working directory path

        Returns:
            dict with status
        """
        session_mgr = SessionManager()
        return session_mgr.eval(session_id, f'cd("{path}");')

    logger.info("Registered simulation lifecycle tools")
