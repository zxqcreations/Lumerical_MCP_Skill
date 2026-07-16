"""Source and monitor tools for Lumerical MCP Server."""

import logging
from mcp.server.fastmcp import FastMCP

from ..session_manager import SessionManager

logger = logging.getLogger(__name__)

_SOURCE_TYPES = {
    "dipole": "adddipole",
    "mode": "addmode",
    "gaussian": "addgaussian",
    "tfsf": "addtfsf",
    "plane": "addplane",
    "imported": "addimportedsource",
    "modesource": "addmodesource",
}

_MONITOR_TYPES = {
    "power": "addpower",
    "profile": "addprofile",
    "index": "addindex",
    "time": "addtime",
    "movie": "addmovie",
    "field_time": "addemfieldtimemonitor",
    "field": "addemfieldmonitor",
    "absorption": "addemabsorptionmonitor",
    "mode_expansion": "addmodeexpansion",
    "bandstructure": "addbandstructuremonitor",
    "port": "addport",
    "effective_index": "addeffectiveindex",
}


def register_source_monitor_tools(mcp: FastMCP) -> None:
    """Register source and monitor tools."""

    @mcp.tool()
    def lumerical_add_source(
        session_id: str,
        source_type: str,
        properties: str = "{}",
    ) -> dict:
        """Add a source to the simulation.

        Source types:
        - 'dipole': Point dipole source (electric/magnetic)
        - 'mode': Mode source (waveguide excitation)
        - 'gaussian': Gaussian beam source
        - 'tfsf': Total-field scattered-field source
        - 'plane': Plane wave source
        - 'imported': Imported source from file

        Common properties: name, x, y, z, wavelength_start, wavelength_stop,
        injection_axis, direction, polarization_angle, amplitude

        Args:
            session_id: The session ID from lumerical_open
            source_type: Type of source (dipole, mode, gaussian, tfsf, plane)
            properties: JSON object of source properties

        Returns:
            dict with status
        """
        import json

        try:
            props = json.loads(properties)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON: {properties}"}

        cmd = _SOURCE_TYPES.get(source_type, source_type)

        session_mgr = SessionManager()
        script_lines = [f"{cmd};"]
        for key, value in props.items():
            key = key.replace("_", " ")
            if isinstance(value, str):
                script_lines.append(f'set("{key}", "{value}");')
            elif isinstance(value, bool):
                script_lines.append(f'set("{key}", {1 if value else 0});')
            else:
                script_lines.append(f'set("{key}", {value});')

        return session_mgr.eval(session_id, "\n".join(script_lines))

    @mcp.tool()
    def lumerical_add_monitor(
        session_id: str,
        monitor_type: str,
        properties: str = "{}",
    ) -> dict:
        """Add a monitor to collect simulation data.

        Monitor types:
        - 'power': Power transmission monitor
        - 'profile': Field profile monitor (frequency domain)
        - 'index': Refractive index monitor
        - 'time': Time domain field monitor
        - 'movie': Movie monitor (animation frames)
        - 'field_time': EM field time monitor
        - 'field': EM field frequency monitor
        - 'absorption': Absorption monitor
        - 'mode_expansion': Mode expansion monitor
        - 'port': Port for S-parameter extraction
        - 'bandstructure': Band structure analysis
        - 'effective_index': Effective index monitor

        Common properties: name, monitor_type, x, y, z, x_span, y_span, z_span,
        frequency_points, wavelength_center, wavelength_span

        Args:
            session_id: The session ID from lumerical_open
            monitor_type: Type of monitor
            properties: JSON object of monitor properties

        Returns:
            dict with status
        """
        import json

        try:
            props = json.loads(properties)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON: {properties}"}

        cmd = _MONITOR_TYPES.get(monitor_type, monitor_type)

        session_mgr = SessionManager()
        script_lines = [f"{cmd};"]
        for key, value in props.items():
            key = key.replace("_", " ")
            if isinstance(value, str):
                script_lines.append(f'set("{key}", "{value}");')
            elif isinstance(value, bool):
                script_lines.append(f'set("{key}", {1 if value else 0});')
            else:
                script_lines.append(f'set("{key}", {value});')

        return session_mgr.eval(session_id, "\n".join(script_lines))

    @mcp.tool()
    def lumerical_set_global_source(session_id: str, properties: str = "{}") -> dict:
        """Set global source properties.

        Controls wavelength/frequency range used across all sources.

        Properties:
        - wavelength_start, wavelength_stop, wavelength_center, wavelength_span
        - frequency_start, frequency_stop, frequency_center, frequency_span
        - number_of_wavelength_points (or frequency_points)

        Args:
            session_id: The session ID from lumerical_open
            properties: JSON object of global source settings

        Returns:
            dict with status
        """
        import json

        try:
            props = json.loads(properties)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON: {properties}"}

        session_mgr = SessionManager()
        script_lines = ["setglobalsource("]
        for key, value in props.items():
            key = key.replace("_", " ")
            if isinstance(value, str):
                script_lines.append(f'"{key}", "{value}", ')
            else:
                script_lines.append(f'"{key}", {value}, ')
        script_lines.append(");")

        return session_mgr.eval(session_id, "".join(script_lines))

    @mcp.tool()
    def lumerical_set_global_monitor(session_id: str, properties: str = "{}") -> dict:
        """Set global monitor properties.

        Configure default frequency points and other settings for all monitors.

        Properties:
        - frequency_points, use_source_limits, use_wavelength_spacing
        - wavelength_center, wavelength_span

        Args:
            session_id: The session ID from lumerical_open
            properties: JSON object of global monitor settings

        Returns:
            dict with status
        """
        import json

        try:
            props = json.loads(properties)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON: {properties}"}

        session_mgr = SessionManager()
        script_lines = ["setglobalmonitor("]
        for key, value in props.items():
            key = key.replace("_", " ")
            if isinstance(value, str):
                script_lines.append(f'"{key}", "{value}", ')
            else:
                script_lines.append(f'"{key}", {value}, ')
        script_lines.append(");")

        return session_mgr.eval(session_id, "".join(script_lines))

    logger.info("Registered source and monitor tools")
