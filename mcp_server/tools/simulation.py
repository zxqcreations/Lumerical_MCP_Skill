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

    @mcp.tool()
    def lumerical_stop(session_id: str) -> dict:
        """Gracefully stop a running simulation.

        Stops the current simulation without closing the project.
        Partial results up to the stop point are preserved.

        Args:
            session_id: The session ID from lumerical_open

        Returns:
            dict with status
        """
        session_mgr = SessionManager()
        return session_mgr.eval(session_id, "stop;")

    @mcp.tool()
    def lumerical_get_status(session_id: str) -> dict:
        """Get the current simulation running status.

        Returns progress percentage, time elapsed, and
        estimated remaining time for an active simulation.

        Args:
            session_id: The session ID from lumerical_open

        Returns:
            dict with simulation status
        """
        session_mgr = SessionManager()
        code = "temp_status = getstatus;"
        eval_result = session_mgr.eval(session_id, code)
        if not eval_result.get("success"):
            return eval_result
        result = session_mgr.get_var(session_id, "temp_status")
        session_mgr.eval(session_id, "clear(temp_status);")
        return result

    @mcp.tool()
    def lumerical_get_resource(session_id: str) -> dict:
        """Get compute resource configuration (threads, processes, GPU).

        Args:
            session_id: The session ID from lumerical_open

        Returns:
            dict with resource configuration
        """
        session_mgr = SessionManager()
        code = "temp_res = getresource;"
        eval_result = session_mgr.eval(session_id, code)
        if not eval_result.get("success"):
            return eval_result
        result = session_mgr.get_var(session_id, "temp_res")
        session_mgr.eval(session_id, "clear(temp_res);")
        return result

    @mcp.tool()
    def lumerical_set_resource(
        session_id: str,
        properties: str = "{}",
    ) -> dict:
        """Set compute resource configuration.

        Configure threads, parallel processes, and solver-specific
        resource options.

        Args:
            session_id: The session ID from lumerical_open
            properties: JSON object of resource settings.
                E.g., '{"number of threads": 8, "FDTD": {"use GPU": 1}}'

        Returns:
            dict with status
        """
        import json

        try:
            props = json.loads(properties)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON: {properties}"}

        session_mgr = SessionManager()
        script_lines = []
        for key, value in props.items():
            key = key.replace("_", " ")
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    sub_key = sub_key.replace("_", " ")
                    if isinstance(sub_value, str):
                        script_lines.append(
                            f'setresource("{key}", "{sub_key}", "{sub_value}");'
                        )
                    else:
                        script_lines.append(
                            f'setresource("{key}", "{sub_key}", {sub_value});'
                        )
            else:
                if isinstance(value, str):
                    script_lines.append(
                        f'setresource("{key}", "{value}");'
                    )
                else:
                    script_lines.append(
                        f'setresource("{key}", {value});'
                    )

        return session_mgr.eval(session_id, "\n".join(script_lines))

    @mcp.tool()
    def lumerical_mesh_order(
        session_id: str,
        order: int = 1,
    ) -> dict:
        """Set global mesh order for the simulation.

        Controls how overlapping mesh regions are resolved.
        Higher values = higher priority.

        Args:
            session_id: The session ID from lumerical_open
            order: Global mesh order (default 1)

        Returns:
            dict with status
        """
        session_mgr = SessionManager()
        return session_mgr.eval(session_id, f'set("mesh order", {order});')

    logger.info("Registered simulation lifecycle tools")
