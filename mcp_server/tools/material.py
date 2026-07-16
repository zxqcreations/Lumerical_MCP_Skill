"""Material tools for Lumerical MCP Server."""

import logging
from mcp.server.fastmcp import FastMCP

from ..session_manager import SessionManager

logger = logging.getLogger(__name__)


def register_material_tools(mcp: FastMCP) -> None:
    """Register material-related tools."""

    @mcp.tool()
    def lumerical_add_material(
        session_id: str,
        material_name: str,
        properties: str = "{}",
    ) -> dict:
        """Add or modify a material in the material database.

        Material types available:
        - '<Object> dielectric': Dielectric with constant refractive index
        - 'Au (Gold) - Johnson <n,k>': Sampled n,k data material
        - 'Si (Silicon) - Palik': Sampled n,k from handbook
        - Custom materials with arbitrary properties

        Properties for dielectrics:
        - 'index': Refractive index (e.g., 1.5)
        - 'color': Display color

        Properties for sampled data:
        - 'nk_data': n,k vs wavelength/frequency data
        - 'conductivity': Electrical conductivity

        Args:
            session_id: The session ID from lumerical_open
            material_name: Material name (can include base material in parentheses)
            properties: JSON object of material properties

        Returns:
            dict with status
        """
        import json

        try:
            props = json.loads(properties)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON in properties: {properties}"}

        session_mgr = SessionManager()

        script_lines = [f'addmaterial("{material_name}");']
        for key, value in props.items():
            key = key.replace("_", " ")
            if isinstance(value, str):
                script_lines.append(f'set("{key}", "{value}");')
            elif isinstance(value, bool):
                script_lines.append(f'set("{key}", {1 if value else 0});')
            else:
                script_lines.append(f'set("{key}", {value});')

        code = "\n".join(script_lines)
        return session_mgr.eval(session_id, code)

    @mcp.tool()
    def lumerical_set_material(session_id: str, material_name: str) -> dict:
        """Set the material of the currently selected object.

        Args:
            session_id: The session ID from lumerical_open
            material_name: Name of the material to assign

        Returns:
            dict with status
        """
        session_mgr = SessionManager()
        return session_mgr.eval(session_id, f'set("material", "{material_name}");')

    @mcp.tool()
    def lumerical_get_material(session_id: str, material_name: str = "") -> dict:
        """Get material data from the database.

        If material_name is provided, gets that material's properties.
        If empty, gets properties of the selected object's material.

        Args:
            session_id: The session ID from lumerical_open
            material_name: Material name to query (empty = current object's material)

        Returns:
            dict with material data
        """
        session_mgr = SessionManager()
        if material_name:
            return session_mgr.call(session_id, "getmaterial", material_name)
        else:
            return session_mgr.eval(session_id, 'temp_mat = get("material");')

    @mcp.tool()
    def lumerical_get_index(
        session_id: str,
        material_name: str,
        frequency: float = 3e14,
    ) -> dict:
        """Get the complex refractive index of a material at a given frequency.

        Args:
            session_id: The session ID from lumerical_open
            material_name: Material name (e.g., 'Si (Silicon) - Palik')
            frequency: Frequency in Hz (default: 3e14 Hz ≈ 1000 nm)

        Returns:
            dict with complex refractive index
        """
        session_mgr = SessionManager()
        code = f'temp_n = getfdtdindex("{material_name}", {frequency});'
        eval_result = session_mgr.eval(session_id, code)
        if not eval_result.get("success"):
            return eval_result
        result = session_mgr.get_var(session_id, "temp_n")
        session_mgr.eval(session_id, "clear(temp_n);")
        return result

    @mcp.tool()
    def lumerical_import_nk(
        session_id: str,
        material_name: str,
        filepath: str,
    ) -> dict:
        """Import n,k material data from a file.

        Supports various formats for refractive index data files.

        Args:
            session_id: The session ID from lumerical_open
            material_name: Name for the imported material
            filepath: Path to the n,k data file

        Returns:
            dict with status
        """
        session_mgr = SessionManager()
        return session_mgr.eval(
            session_id,
            f'addmaterial("{material_name}");\n'
            f'importnk("{material_name}", "{filepath}");',
        )

    @mcp.tool()
    def lumerical_get_transmission(
        session_id: str,
        material_name: str,
        thickness: float = 100e-9,
        f_min: float = 1e14,
        f_max: float = 1e15,
        nf: int = 100,
    ) -> dict:
        """Calculate transmission through a thin film of material.

        Uses the stackrt function to compute thin-film transmission.

        Args:
            session_id: The session ID from lumerical_open
            material_name: Material name
            thickness: Film thickness in meters (default: 100e-9 = 100 nm)
            f_min: Minimum frequency in Hz
            f_max: Maximum frequency in Hz
            nf: Number of frequency points

        Returns:
            dict with transmission data (wavelengths, T, R)
        """
        session_mgr = SessionManager()
        code = (
            f"f = linspace({f_min}, {f_max}, {nf});\n"
            f"temp_T = stackrt(refractiveindex(\"{material_name}\", f), {thickness}, f);"
        )
        eval_result = session_mgr.eval(session_id, code)
        if not eval_result.get("success"):
            return eval_result
        return session_mgr.get_var(session_id, "temp_T")

    logger.info("Registered material tools")
