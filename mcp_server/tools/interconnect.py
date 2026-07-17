"""INTERCONNECT-specific tools for Lumerical MCP Server.

INTERCONNECT (photonic circuit simulator) has a fundamentally different API
from FDTD/MODE/DEVICE. Element-level commands like addwaveguide, connect, etc.
cannot be called via eval() OR as direct Python methods. Instead, INTERCONNECT
workflows rely on:

1. Running .lsf script files via handle.run()
2. Generic addelement() for adding circuit elements
3. Sweep/analysis commands for parameter studies

This module provides tools tailored to INTERCONNECT's workflow patterns.
"""

import logging
from mcp.server.fastmcp import FastMCP

from ..session_manager import SessionManager, cleanup_interconnect_processes

logger = logging.getLogger(__name__)


def register_interconnect_tools(mcp: FastMCP) -> None:
    """Register INTERCONNECT-specific tools."""

    @mcp.tool()
    def lumerical_interconnect_run_script(
        session_id: str,
        script_path: str,
    ) -> dict:
        """Execute a .lsf script file in an INTERCONNECT session.

        This is the PRIMARY way to set up and run INTERCONNECT simulations.
        Unlike FDTD/MODE, INTERCONNECT does not expose element-level commands
        (addwaveguide, connect, etc.) as direct Python API methods. Instead,
        write a complete .lsf script and execute it with this tool.

        The script can include:
        - Circuit element creation (addwaveguide, addcwlaser, etc.)
        - Element connections (connect)
        - Analyzer setup (addpoweranalyzer, addosnranalyzer)
        - Sweep configuration (addsweep, addsweepparameter)
        - Run and data export commands

        Note: If the script ends in analysis mode, "Analysis Mode" errors
        are automatically treated as success.

        Example .lsf script content:
            # Create elements
            addcwlaser;
            set("name", "Pump Laser");
            set("wavelength", 980e-9);
            set("power", 100e-3);

            addwaveguide;
            set("name", "EDFA");
            set("length", 10e-3);
            set("model", "Er_Yb_WG");

            addpoweranalyzer;
            set("name", "Output");

            # Connect elements
            connect("Pump Laser", "output", "EDFA", "input");
            connect("EDFA", "output", "Output", "input");

            # Run sweep
            addsweep;
            set("name", "Pump Power Sweep");
            addsweepparameter;
            set("parameter", "Pump Laser::power");
            set("start", 10e-3);
            set("stop", 200e-3);
            set("number of points", 20);
            addsweepresult;
            set("name", "Output Power");
            set("result", "Output::total power");
            runsweep;

        Args:
            session_id: The session ID from lumerical_open("interconnect")
            script_path: Absolute path to .lsf script file

        Returns:
            dict with execution status
        """
        session_mgr = SessionManager()
        return session_mgr.run_script(session_id, script_path)

    @mcp.tool()
    def lumerical_interconnect_add_element(
        session_id: str,
        element_type: str,
        properties: str = "{}",
    ) -> dict:
        """Add a circuit element to an INTERCONNECT session.

        Uses the generic addelement() command which is the programmatic way
        to add elements. After adding, use lumerical_eval to set properties.

        Common element types:
        - Waveguide elements: 'Waveguide', 'Straight Waveguide',
          'Spiral Waveguide', 'Ring Resonator'
        - Active elements: 'Optical Amplifier', 'CW Laser', 'Modulator'
        - Passive elements: 'Coupler', 'Splitter', 'Y Branch',
          'MMI Coupler', 'Directional Coupler'
        - Analyzers: 'Power Analyzer', 'OSNR Analyzer',
          'Eye Diagram Analyzer', 'Spectrum Analyzer'
        - Sources: 'Optical Source', 'Electrical Source'
        - Signal processing: 'Filter', 'Delay', 'Attenuator'

        Args:
            session_id: The session ID from lumerical_open("interconnect")
            element_type: Type of element to add (e.g., 'Waveguide',
                          'CW Laser', 'Power Analyzer')
            properties: JSON object of initial element properties
                (e.g., '{"name": "Pump", "wavelength": 980e-9}')

        Returns:
            dict with status and element info
        """
        import json

        try:
            props = json.loads(properties)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON: {properties}"}

        session_mgr = SessionManager()

        # Build script to add and configure the element
        script_lines = [f'addelement("{element_type}");']

        name = props.pop("name", None)
        if name:
            script_lines.append(f'set("name", "{name}");')

        for key, value in props.items():
            key_clean = key.replace("_", " ")
            if isinstance(value, str):
                script_lines.append(f'set("{key_clean}", "{value}");')
            elif isinstance(value, bool):
                script_lines.append(
                    f'set("{key_clean}", {1 if value else 0});'
                )
            else:
                script_lines.append(f'set("{key_clean}", {value});')

        return session_mgr.eval(session_id, "\n".join(script_lines))

    @mcp.tool()
    def lumerical_interconnect_connect(
        session_id: str,
        connections: str = "[]",
    ) -> dict:
        """Connect INTERCONNECT circuit elements.

        Creates connections between ports of circuit elements. Each connection
        is a dict with source_element, source_port, target_element, target_port.

        Args:
            session_id: The session ID from lumerical_open("interconnect")
            connections: JSON array of connection objects, each with:
                - from_element: Source element name
                - from_port: Source port name (e.g., 'output')
                - to_element: Target element name
                - to_port: Target port name (e.g., 'input')
                Example:
                '[{"from_element":"Laser","from_port":"output",
                   "to_element":"WG","to_port":"input"}]'

        Returns:
            dict with status
        """
        import json

        try:
            conns = json.loads(connections)
            if not isinstance(conns, list):
                return {
                    "success": False,
                    "error": "connections must be a JSON array",
                }
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON: {connections}"}

        session_mgr = SessionManager()
        script_lines = []
        for i, conn in enumerate(conns):
            from_el = conn.get("from_element", "")
            from_port = conn.get("from_port", "output")
            to_el = conn.get("to_element", "")
            to_port = conn.get("to_port", "input")

            if not from_el or not to_el:
                return {
                    "success": False,
                    "error": (
                        f"Connection #{i}: both from_element and "
                        f"to_element are required"
                    ),
                }

            script_lines.append(
                f'connect("{from_el}", "{from_port}", '
                f'"{to_el}", "{to_port}");'
            )

        return session_mgr.eval(session_id, "\n".join(script_lines))

    @mcp.tool()
    def lumerical_interconnect_add_sweep(
        session_id: str,
        sweep_name: str,
        parameter: str,
        start: float,
        stop: float,
        num_points: int = 20,
        result_expressions: str = "[]",
    ) -> dict:
        """Configure and run a parameter sweep in INTERCONNECT.

        Sets up a sweep over a circuit parameter and collects specified
        results at each sweep point.

        Args:
            session_id: The session ID from lumerical_open("interconnect")
            sweep_name: Name for the sweep
            parameter: Parameter expression to sweep
                (e.g., 'Pump Laser::power', 'WG::length')
            start: Start value
            stop: Stop value
            num_points: Number of sweep points
            result_expressions: JSON array of result expressions
                (e.g., '["Output::total power", "Output::signal power"]')

        Returns:
            dict with sweep status
        """
        import json

        try:
            results = json.loads(result_expressions)
            if not isinstance(results, list):
                return {
                    "success": False,
                    "error": "result_expressions must be a JSON array",
                }
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON: {result_expressions}"}

        session_mgr = SessionManager()

        script_lines = [
            "addsweep;",
            f'set("name", "{sweep_name}");',
            "addsweepparameter;",
            f'set("parameter", "{parameter}");',
            f'set("start", {start});',
            f'set("stop", {stop});',
            f'set("number of points", {num_points});',
        ]

        for expr in results:
            script_lines.append("addsweepresult;")
            script_lines.append(f'set("result", "{expr}");')

        script_lines.append("runsweep;")

        return session_mgr.eval(session_id, "\n".join(script_lines))

    @mcp.tool()
    def lumerical_interconnect_get_sweep_data(
        session_id: str,
        sweep_name: str,
        result_name: str,
    ) -> dict:
        """Get data from a completed INTERCONNECT sweep.

        Retrieves the sweep parameter values and corresponding results.

        Args:
            session_id: The session ID from lumerical_open("interconnect")
            sweep_name: Name of the sweep
            result_name: Name of the sweep result to retrieve
                (e.g., 'Output Power')

        Returns:
            dict with sweep parameter values and result data
        """
        session_mgr = SessionManager()

        # Get the sweep data via eval + getv
        code = (
            f'_mcp_sweep = getsweepdata("{sweep_name}", "{result_name}");'
        )
        eval_result = session_mgr.eval(session_id, code)
        if not eval_result.get("success"):
            return eval_result

        return session_mgr.get_var(session_id, "_mcp_sweep")

    @mcp.tool()
    def lumerical_interconnect_cleanup() -> dict:
        """Kill zombie INTERCONNECT processes.

        INTERCONNECT.exe processes can persist after sessions end,
        blocking new connections. Call this before opening a new
        INTERCONNECT session if you encounter connection errors.

        This is safe to call at any time — it only affects orphaned
        INTERCONNECT processes, not active sessions.

        Returns:
            dict with count of killed processes
        """
        return cleanup_interconnect_processes()

    logger.info("Registered INTERCONNECT tools")
