"""Solver configuration tools for Lumerical MCP Server."""

import logging
from mcp.server.fastmcp import FastMCP

from ..session_manager import SessionManager

logger = logging.getLogger(__name__)

_SOLVER_TYPES = {
    "fdtd": "addfdtd",
    "fde": "addfde",
    "eme": "addeme",
    "varfdtd": "addvarfdtd",
    "dgt": "adddgtdsolver",
    "charge": "addchargesolver",
    "heat": "addheatsolver",
    "feem": "addfeemsolver",
}

_BOUNDARY_TYPES = {
    "pml": "addpml",
    "periodic": "addperiodic",
    "metal": "addpec",
    "pmc": "addpmc",
    "absorbing": "addabsorbing",
}


def register_solver_tools(mcp: FastMCP) -> None:
    """Register solver configuration tools."""

    @mcp.tool()
    def lumerical_add_solver(
        session_id: str,
        solver_type: str,
        properties: str = "{}",
    ) -> dict:
        """Add a solver region to the simulation.

        Solver types:
        - 'fdtd': FDTD solver (finite-difference time-domain)
        - 'fde': FDE solver (finite-difference eigenmode) - MODE
        - 'eme': EME solver (eigenmode expansion) - MODE
        - 'varfdtd': varFDTD solver (variational FDTD) - MODE
        - 'dgt': DGTD solver (discontinuous Galerkin time-domain)
        - 'charge': Charge transport solver - DEVICE
        - 'heat': Heat transport solver - DEVICE
        - 'feem': FEEM solver (finite element eigenmode)

        Common FDTD properties:
        - dimension (1=2D, 2=3D), x, y, z, x_span, y_span, z_span
        - simulation_time, auto_shutoff_min, auto_shutoff_max
        - mesh_accuracy, mesh_refinement
        - boundary_conditions (x_min_bc, x_max_bc, etc.)
        - dt_stability_factor

        Args:
            session_id: The session ID from lumerical_open
            solver_type: Type of solver to add
            properties: JSON object of solver properties

        Returns:
            dict with status
        """
        import json

        try:
            props = json.loads(properties)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON: {properties}"}

        cmd = _SOLVER_TYPES.get(solver_type, solver_type)

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
    def lumerical_add_mesh(
        session_id: str,
        properties: str = "{}",
    ) -> dict:
        """Add a mesh override region for refined simulation grid.

        Mesh override properties:
        - name, x, y, z, x_span, y_span, z_span
        - dx, dy, dz (target mesh step sizes)
        - override_x_mesh, override_y_mesh, override_z_mesh
        - set_maximum_mesh_step

        Args:
            session_id: The session ID from lumerical_open
            properties: JSON object of mesh properties

        Returns:
            dict with status
        """
        import json

        try:
            props = json.loads(properties)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON: {properties}"}

        session_mgr = SessionManager()
        script_lines = ["addmesh;"]
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
    def lumerical_add_boundary(
        session_id: str,
        boundary_type: str,
        properties: str = "{}",
    ) -> dict:
        """Add a boundary condition to the simulation.

        Boundary types:
        - 'pml': Perfectly matched layer (absorbing boundary)
        - 'periodic': Periodic boundary condition (Bloch/Floquet)
        - 'metal': Perfect electric conductor (PEC)
        - 'pmc': Perfect magnetic conductor
        - 'absorbing': Absorbing boundary condition

        PML properties: name, x_min, x_max, y_min, y_max, z_min, z_max,
        number_of_layers, kappa, sigma

        Periodic properties: name, x_min_bc, y_min_bc, z_min_bc,
        use_bloch, bloch_vector

        Args:
            session_id: The session ID from lumerical_open
            boundary_type: Type of boundary condition
            properties: JSON object of boundary properties

        Returns:
            dict with status
        """
        import json

        try:
            props = json.loads(properties)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON: {properties}"}

        cmd = _BOUNDARY_TYPES.get(boundary_type, boundary_type)

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
    def lumerical_set_analysis(
        session_id: str,
        properties: str = "{}",
    ) -> dict:
        """Set analysis parameters for the simulation.

        Configures solver-specific analysis settings.

        Args:
            session_id: The session ID from lumerical_open
            properties: JSON object of analysis parameters

        Returns:
            dict with status
        """
        import json

        try:
            props = json.loads(properties)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON: {properties}"}

        session_mgr = SessionManager()
        script_lines = ["setanalysis("]
        for key, value in props.items():
            key = key.replace("_", " ")
            if isinstance(value, str):
                script_lines.append(f'"{key}", "{value}", ')
            else:
                script_lines.append(f'"{key}", {value}, ')
        script_lines.append(");")

        return session_mgr.eval(session_id, "".join(script_lines))

    logger.info("Registered solver configuration tools")
