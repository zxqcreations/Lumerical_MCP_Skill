"""Optimization and sweep tools for Lumerical MCP Server."""

import logging
from mcp.server.fastmcp import FastMCP

from ..session_manager import SessionManager

logger = logging.getLogger(__name__)


def register_optimization_tools(mcp: FastMCP) -> None:
    """Register optimization tools."""

    @mcp.tool()
    def lumerical_add_sweep(
        session_id: str,
        sweep_name: str,
        sweep_type: str = "ranges",
        properties: str = "{}",
    ) -> dict:
        """Add a parameter sweep to the simulation.

        Creates a sweep that varies one or more parameters and collects results.

        Args:
            session_id: The session ID from lumerical_open
            sweep_name: Name for the sweep
            sweep_type: Type of sweep ('ranges', 'points', 'user_specified')
            properties: JSON object with sweep configuration:
                - parameters: list of parameter names to vary
                - ranges: list of [start, stop, num_points] for each parameter
                - results: list of result names to collect

        Returns:
            dict with status
        """
        import json

        try:
            props = json.loads(properties)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON: {properties}"}

        if not sweep_name:
            return {"success": False, "error": "sweep_name is required."}

        session_mgr = SessionManager()
        # Create the sweep
        code = f'addsweep(0); set("name", "{sweep_name}");'
        session_mgr.eval(session_id, code)

        # Add parameters
        for param in props.get("parameters", []):
            code = f'addsweepparameter("{sweep_name}", "{param}");'
            session_mgr.eval(session_id, code)

        # Configure ranges
        for i, (param, rng) in enumerate(zip(
            props.get("parameters", []),
            props.get("ranges", [])
        )):
            if len(rng) >= 3:
                code = (
                    f'setsweep("{sweep_name}", "parameter {i+1}", '
                    f'"type", "{sweep_type}");\n'
                    f'setsweep("{sweep_name}", "parameter {i+1}", '
                    f'"start", {rng[0]});\n'
                    f'setsweep("{sweep_name}", "parameter {i+1}", '
                    f'"stop", {rng[1]});\n'
                    f'setsweep("{sweep_name}", "parameter {i+1}", '
                    f'"number of points", {rng[2]});\n'
                )
                session_mgr.eval(session_id, code)

        # Add results to collect
        for result_name in props.get("results", []):
            code = f'addsweepresult("{sweep_name}", "{result_name}");'
            session_mgr.eval(session_id, code)

        return {"success": True, "message": f"Sweep '{sweep_name}' created."}

    @mcp.tool()
    def lumerical_run_sweep(
        session_id: str,
        sweep_name: str,
    ) -> dict:
        """Run a configured parameter sweep.

        Executes all simulations in the sweep. May take significant time for
        large sweeps. Consider using runjobs for parallel execution.

        Args:
            session_id: The session ID from lumerical_open
            sweep_name: Name of the sweep to run

        Returns:
            dict with run status
        """
        session_mgr = SessionManager()
        return session_mgr.eval(session_id, f'runsweep("{sweep_name}");')

    @mcp.tool()
    def lumerical_get_sweep_result(
        session_id: str,
        sweep_name: str,
        result_name: str,
    ) -> dict:
        """Get results from a completed parameter sweep.

        Args:
            session_id: The session ID from lumerical_open
            sweep_name: Name of the sweep
            result_name: Name of the result to retrieve

        Returns:
            dict with sweep data
        """
        session_mgr = SessionManager()
        code = f'temp_sweep = getsweepresult("{sweep_name}", "{result_name}");'
        eval_result = session_mgr.eval(session_id, code)
        if not eval_result.get("success"):
            return eval_result
        result = session_mgr.get_var(session_id, "temp_sweep")
        session_mgr.eval(session_id, "clear(temp_sweep);")
        return result

    @mcp.tool()
    def lumerical_add_optimization(
        session_id: str,
        optimization_name: str,
        properties: str = "{}",
    ) -> dict:
        """Set up an inverse design optimization.

        Configures adjoint-based optimization for photonic inverse design.
        Requires the lumopt/lumopt2 module.

        Properties:
        - figure_of_merit: FOM type (e.g., 'transmission', 'modematch', 'field')
        - optimization_algorithm: 'gradient_descent', 'adaptive_gradient', 'basin_hopping'
        - max_iterations, tolerance
        - design_variables: list of parameter names and bounds

        Args:
            session_id: The session ID from lumerical_open
            optimization_name: Name for the optimization
            properties: JSON object of optimization configuration

        Returns:
            dict with status
        """
        import json

        try:
            props = json.loads(properties)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON: {properties}"}

        session_mgr = SessionManager()

        # Create optimization setup in Lumerical
        code = [
            f'newwizard("optimization");',
            f'set("name", "{optimization_name}");',
        ]
        for key, value in props.items():
            key = key.replace("_", " ")
            if isinstance(value, str):
                code.append(f'set("{key}", "{value}");')
            elif isinstance(value, bool):
                code.append(f'set("{key}", {1 if value else 0});')
            else:
                code.append(f'set("{key}", {value});')

        return session_mgr.eval(session_id, "\n".join(code))

    @mcp.tool()
    def lumerical_run_optimization(
        session_id: str,
        optimization_name: str = "",
    ) -> dict:
        """Run an inverse design optimization.

        Starts the optimization process. May take significant time depending on
        complexity and iteration count.

        Args:
            session_id: The session ID from lumerical_open
            optimization_name: Name of the optimization to run

        Returns:
            dict with run status
        """
        session_mgr = SessionManager()
        if optimization_name:
            code = f'runoptimization("{optimization_name}");'
        else:
            code = "runoptimization;"
        return session_mgr.eval(session_id, code)

    @mcp.tool()
    def lumerical_run_parallel(
        session_id: str,
        sweep_name: str = "",
        num_processes: int = 4,
    ) -> dict:
        """Run simulation jobs in parallel.

        Uses Lumerical's built-in parallel processing for sweeps and
        independent simulations.

        Args:
            session_id: The session ID from lumerical_open
            sweep_name: Name of the sweep to run in parallel
            num_processes: Number of parallel processes

        Returns:
            dict with run status
        """
        session_mgr = SessionManager()
        code = [
            f'setresource("number of threads", {num_processes});',
        ]
        if sweep_name:
            code.append(f'runjobs("{sweep_name}");')
        else:
            code.append("runjobs;")

        return session_mgr.eval(session_id, "\n".join(code))

    logger.info("Registered optimization and sweep tools")
