"""Results and analysis tools for Lumerical MCP Server."""

import logging
from mcp.server.fastmcp import FastMCP

from ..session_manager import SessionManager

logger = logging.getLogger(__name__)


def register_results_tools(mcp: FastMCP) -> None:
    """Register results and analysis tools."""

    @mcp.tool()
    def lumerical_get_result(
        session_id: str,
        monitor_name: str,
        result_name: str = "",
    ) -> dict:
        """Get simulation results from a monitor or analysis group.

        Retrieves calculated data from monitors after simulation has run.
        Common result names depend on the monitor type:

        For power monitors: 'T' (transmission), 'R' (reflection), 'S'
        For profile monitors: 'E', 'Ex', 'Ey', 'Ez', 'H', 'Hx', 'Hy', 'Hz'
        For index monitors: 'index', 'index_x', 'index_y', 'index_z'
        For mode expansion: 'expansion for port', 'S', 'a', 'b'
        For time monitors: 'E', 'Ex', 'Ey', 'Ez', 't'

        If result_name is empty, lists all available results for the monitor.

        Args:
            session_id: The session ID from lumerical_open
            monitor_name: Name of the monitor or analysis group
            result_name: Specific result to retrieve (empty = list all)

        Returns:
            dict with result data
        """
        session_mgr = SessionManager()

        if not result_name:
            # List available results
            code = f'temp_results = getresult("{monitor_name}");'
            eval_result = session_mgr.eval(session_id, code)
            if not eval_result.get("success"):
                return eval_result
            result = session_mgr.get_var(session_id, "temp_results")
            session_mgr.eval(session_id, "clear(temp_results);")
            return result

        # Get specific result
        code = f'temp_data = getresult("{monitor_name}", "{result_name}");'
        eval_result = session_mgr.eval(session_id, code)
        if not eval_result.get("success"):
            return eval_result
        result = session_mgr.get_var(session_id, "temp_data")
        session_mgr.eval(session_id, "clear(temp_data);")
        return result

    @mcp.tool()
    def lumerical_get_data(
        session_id: str,
        monitor_name: str,
        attribute: str,
    ) -> dict:
        """Get raw data directly from a monitor or analysis group.

        Uses the direct lumapi handle.getdata() API call, which bypasses
        eval entirely. This is more reliable than eval-based approaches
        for MODE analysis-mode data (e.g., FDE mode profiles, sweep results).

        Common attributes:
        - FDE modes: 'neff', 'x', 'y', 'z', 'Ex', 'Ey', 'Ez', 'Hx', 'Hy', 'Hz'
        - INTERCONNECT sweeps: use lumerical_interconnect_get_sweep_data
        - Field monitors: 'E', 'H', 'P', 'T', 'index', 'n', 'k', 'epsilon'

        Example: lumerical_get_data("lum_1", "FDE::data::mode1", "neff")

        Args:
            session_id: The session ID from lumerical_open
            monitor_name: Name of the monitor or analysis group
                (e.g., 'FDE::data::mode1', 'power_monitor')
            attribute: Data attribute to retrieve
                (e.g., 'neff', 'Ex', 'T')

        Returns:
            dict with data array/value
        """
        session_mgr = SessionManager()
        return session_mgr.get_data(session_id, monitor_name, attribute)

    @mcp.tool()
    def lumerical_get_field(
        session_id: str,
        monitor_name: str,
        field_component: str = "E",
    ) -> dict:
        """Get electromagnetic field data from a field monitor.

        Retrieves the complex field values for post-processing.

        Args:
            session_id: The session ID from lumerical_open
            monitor_name: Name of the field/profile monitor
            field_component: Field component ('E', 'Ex', 'Ey', 'Ez', 'H', etc.)

        Returns:
            dict with complex field data
        """
        session_mgr = SessionManager()
        code = f'temp_field = getelectric("{monitor_name}");'
        if field_component.startswith("H") or field_component.startswith("h"):
            code = f'temp_field = getmagnetic("{monitor_name}");'

        eval_result = session_mgr.eval(session_id, code)
        if not eval_result.get("success"):
            return eval_result
        result = session_mgr.get_var(session_id, "temp_field")
        session_mgr.eval(session_id, "clear(temp_field);")
        return result

    @mcp.tool()
    def lumerical_export_data(
        session_id: str,
        monitor_name: str,
        output_path: str,
        attribute: str = "",
    ) -> dict:
        """Export simulation data to a file.

        Exports monitor data for external analysis. Supports CSV and other formats.

        Args:
            session_id: The session ID from lumerical_open
            monitor_name: Name of the monitor
            output_path: Output file path (e.g., 'C:/data/transmission.csv')
            attribute: Specific attribute to export (empty = export all)

        Returns:
            dict with export status
        """
        session_mgr = SessionManager()
        if attribute:
            code = f'exportcsvresults("{monitor_name}", "{attribute}", "{output_path}");'
        else:
            code = f'exportcsvresults("{monitor_name}", "{output_path}");'
        return session_mgr.eval(session_id, code)

    @mcp.tool()
    def lumerical_farfield(
        session_id: str,
        monitor_name: str,
        projection: str = "3d",
    ) -> dict:
        """Calculate far-field projection from a near-field monitor.

        Computes far-field radiation patterns from near-field data.

        Args:
            session_id: The session ID from lumerical_open
            monitor_name: Name of the monitor for far-field calculation
            projection: Type of projection ('3d', '2d', 'polar', 'spherical', 'ux', 'uy')

        Returns:
            dict with far-field data
        """
        session_mgr = SessionManager()
        if projection == "3d":
            code = f'temp_ff = farfield3d("{monitor_name}");'
        elif projection == "2d":
            code = f'temp_ff = farfield2d("{monitor_name}");'
        elif projection == "polar":
            code = f'temp_ff = farfieldpolar3d("{monitor_name}");'
        elif projection == "spherical":
            code = f'temp_ff = farfieldspherical("{monitor_name}");'
        else:
            code = f'temp_ff = farfield{projection}("{monitor_name}");'

        eval_result = session_mgr.eval(session_id, code)
        if not eval_result.get("success"):
            return eval_result
        result = session_mgr.get_var(session_id, "temp_ff")
        session_mgr.eval(session_id, "clear(temp_ff);")
        return result

    @mcp.tool()
    def lumerical_transmission(
        session_id: str,
        monitor_name: str = "",
    ) -> dict:
        """Get transmission results from the simulation.

        If monitor_name is empty, retrieves from the last power monitor.

        Args:
            session_id: The session ID from lumerical_open
            monitor_name: Power monitor name (empty = auto-detect)

        Returns:
            dict with transmission spectrum
        """
        session_mgr = SessionManager()
        if monitor_name:
            code = f'temp_T = transmission("{monitor_name}");'
        else:
            code = "temp_T = transmission;"

        eval_result = session_mgr.eval(session_id, code)
        if not eval_result.get("success"):
            return eval_result
        result = session_mgr.get_var(session_id, "temp_T")
        session_mgr.eval(session_id, "clear(temp_T);")
        return result

    @mcp.tool()
    def lumerical_get_s_parameters(
        session_id: str,
        monitor_name: str = "",
    ) -> dict:
        """Get S-parameters from INTERCONNECT simulations.

        Retrieves the full S-parameter matrix.

        Args:
            session_id: The session ID from lumerical_open
            monitor_name: Monitor/port name (empty = all ports)

        Returns:
            dict with S-parameter matrix
        """
        session_mgr = SessionManager()
        code = "temp_spar = getresult("
        if monitor_name:
            code += f'"{monitor_name}", '
        code += '"S matrix");'
        eval_result = session_mgr.eval(session_id, code)
        if not eval_result.get("success"):
            return eval_result
        result = session_mgr.get_var(session_id, "temp_spar")
        session_mgr.eval(session_id, "clear(temp_spar);")
        return result

    @mcp.tool()
    def lumerical_get_field_components(
        session_id: str,
        monitor_name: str,
    ) -> dict:
        """List all available field components for a monitor.

        Args:
            session_id: The session ID from lumerical_open
            monitor_name: Field/profile monitor name

        Returns:
            dict with list of available components (Ex, Ey, Ez, Hx, Hy, Hz)
        """
        session_mgr = SessionManager()
        code = (
            f'temp_comps = getdata("{monitor_name}", "Ex");'
            f'switch (haskey(temp_comps, "Ex")) {{ case 1: temp_comps_list = '
            f'["Ex", "Ey", "Ez", "Hx", "Hy", "Hz"]; }}'
        )
        session_mgr.eval(session_id, code)
        result = session_mgr.get_var(session_id, "temp_comps_list")
        session_mgr.eval(session_id, "clear(temp_comps, temp_comps_list);")
        return result

    @mcp.tool()
    def lumerical_get_convergence(
        session_id: str,
        monitor_name: str = "",
    ) -> dict:
        """Get solver convergence history.

        Returns the auto-shutoff convergence data showing
        how the field energy decayed during simulation.

        Args:
            session_id: The session ID from lumerical_open
            monitor_name: Optional monitor name filter

        Returns:
            dict with convergence data
        """
        session_mgr = SessionManager()
        code = "temp_conv = getautoshutoffdata;"
        eval_result = session_mgr.eval(session_id, code)
        if not eval_result.get("success"):
            return eval_result
        result = session_mgr.get_var(session_id, "temp_conv")
        session_mgr.eval(session_id, "clear(temp_conv);")
        return result

    logger.info("Registered results and analysis tools")
