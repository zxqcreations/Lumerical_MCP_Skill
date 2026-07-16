"""Geometry and object manipulation tools for Lumerical MCP Server."""

import logging
from mcp.server.fastmcp import FastMCP

from ..session_manager import SessionManager

logger = logging.getLogger(__name__)

# Map of common geometry objects to their add commands and properties
_GEOMETRY_TYPES = {
    "rect": "addrect",
    "rectangle": "addrect",
    "sphere": "addsphere",
    "circle": "addcircle",
    "ring": "addring",
    "triangle": "addtriangle",
    "polygon": "addpoly",
    "pyramid": "addpyramid",
    "planar_solid": "addplanarsolid",
    "waveguide": "addwaveguide",
    "structure_group": "addstructuregroup",
    "analysis_group": "addanalysisgroup",
    "surface": "addsurface",
    "import": "addimport",
    "user_prop": "adduserprop",
    "custom": "addcustom",
}


def register_geometry_tools(mcp: FastMCP) -> None:
    """Register geometry and object manipulation tools."""

    @mcp.tool()
    def lumerical_add(
        session_id: str,
        object_type: str,
        properties: str = "{}",
    ) -> dict:
        """Add a geometric object or simulation element to the project.

        Creates any supported Lumerical object type with specified properties.

        Common object types and their key properties:
        - 'rect': Rectangle (x, y, z, x_span, y_span, z_span, material, name)
        - 'sphere': Sphere (x, y, z, radius, material, name)
        - 'circle': Circle (x, y, z, radius, material, name)
        - 'ring': Ring (x, y, z, inner_radius, outer_radius, material, name)
        - 'triangle': Triangle (vertices, z, z_span, material, name)
        - 'polygon': Polygon (vertices, z, z_span, material, name)
        - 'waveguide': Waveguide (x, y, z, width, height, material, name)
        - 'planar_solid': Planar solid from layer builder
        - 'structure_group': Group of structures
        - 'analysis_group': Analysis group
        - 'surface': Surface object for importing surfaces
        - 'import': Import from external file

        Properties are specified as a JSON object with property name/value pairs.
        Underscores in property names are converted to spaces (e.g., x_span -> "x span").

        Args:
            session_id: The session ID from lumerical_open
            object_type: Type of object to add (rect, sphere, circle, etc.)
            properties: JSON object of properties (e.g., '{"x": 0, "y": 0, "x_span": 1e-6, "material": "Si"}')

        Returns:
            dict with status
        """
        import json

        try:
            props = json.loads(properties)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON in properties: {properties}"}

        cmd = _GEOMETRY_TYPES.get(object_type, object_type)

        session_mgr = SessionManager()

        # Ensure command exists
        info = session_mgr.get_session(session_id)
        if info is None:
            return {"success": False, "error": f"Session '{session_id}' not found."}

        # Build the script to add and configure the object
        script_lines = [f"{cmd};"]
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
    def lumerical_set(session_id: str, property_name: str, value: str) -> dict:
        """Set a property of the currently selected object.

        Modifies the selected object's property. All standard Lumerical
        properties are accessible: geometry (x, y, z, x_span, etc.),
        material, name, and type-specific properties.

        Args:
            session_id: The session ID from lumerical_open
            property_name: Property name (underscores converted to spaces)
            value: Property value

        Returns:
            dict with status
        """
        session_mgr = SessionManager()
        prop = property_name.replace("_", " ")
        return session_mgr.eval(session_id, f'set("{prop}", {value});')

    @mcp.tool()
    def lumerical_get(session_id: str, property_name: str) -> dict:
        """Get a property value of the currently selected object.

        Args:
            session_id: The session ID from lumerical_open
            property_name: Property name (underscores converted to spaces)

        Returns:
            dict with property value
        """
        prop = property_name.replace("_", " ")
        # Use a temp variable to retrieve the value
        code = f'temp_var_get = get("{prop}");'
        session_mgr = SessionManager()
        eval_result = session_mgr.eval(session_id, code)
        if not eval_result.get("success"):
            return eval_result
        result = session_mgr.get_var(session_id, "temp_var_get")
        # Clean up temp variable
        session_mgr.eval(session_id, "clear(temp_var_get);")
        return result

    @mcp.tool()
    def lumerical_select(session_id: str, object_name: str) -> dict:
        """Select an object by name in the simulation.

        After selection, you can use lumerical_set and lumerical_get
        to modify/read the object's properties.

        Use fully qualified names for nested objects:
        '::model::group::object_name'

        Args:
            session_id: The session ID from lumerical_open
            object_name: Name of the object to select

        Returns:
            dict with status
        """
        session_mgr = SessionManager()
        return session_mgr.eval(session_id, f'select("{object_name}");')

    @mcp.tool()
    def lumerical_select_all(session_id: str) -> dict:
        """Select all objects in the current group scope.

        Args:
            session_id: The session ID from lumerical_open

        Returns:
            dict with status
        """
        session_mgr = SessionManager()
        return session_mgr.eval(session_id, "selectall;")

    @mcp.tool()
    def lumerical_delete(session_id: str, object_name: str = "") -> dict:
        """Delete an object or the currently selected object.

        Args:
            session_id: The session ID from lumerical_open
            object_name: Name of the object to delete. If empty, deletes selected.

        Returns:
            dict with status
        """
        session_mgr = SessionManager()
        if object_name:
            return session_mgr.eval(session_id, f'delete("{object_name}");')
        else:
            return session_mgr.eval(session_id, "delete;")

    @mcp.tool()
    def lumerical_copy(session_id: str, x: float = 0, y: float = 0, z: float = 0) -> dict:
        """Copy the selected object with optional offset.

        Args:
            session_id: The session ID from lumerical_open
            x: X offset for the copy (default 0)
            y: Y offset for the copy (default 0)
            z: Z offset for the copy (default 0)

        Returns:
            dict with status
        """
        session_mgr = SessionManager()
        return session_mgr.eval(session_id, f"copy({x}, {y}, {z});")

    @mcp.tool()
    def lumerical_move(session_id: str, x: float = 0, y: float = 0, z: float = 0) -> dict:
        """Move (translate) the selected object.

        Args:
            session_id: The session ID from lumerical_open
            x: X translation distance
            y: Y translation distance
            z: Z translation distance

        Returns:
            dict with status
        """
        session_mgr = SessionManager()
        return session_mgr.eval(session_id, f"move({x}, {y}, {z});")

    @mcp.tool()
    def lumerical_rotate(session_id: str, axis: str = "z", angle: float = 0) -> dict:
        """Rotate the selected object.

        Args:
            session_id: The session ID from lumerical_open
            axis: Rotation axis ('x', 'y', or 'z')
            angle: Rotation angle in degrees

        Returns:
            dict with status
        """
        session_mgr = SessionManager()
        return session_mgr.eval(session_id, f'rotate("{axis}", {angle});')

    @mcp.tool()
    def lumerical_groupscope(session_id: str, scope: str = "") -> dict:
        """Set or get the current group scope.

        Args:
            session_id: The session ID from lumerical_open
            scope: Group scope path (e.g., '::model::group_name'). If empty, gets current scope.

        Returns:
            dict with scope info
        """
        session_mgr = SessionManager()
        if scope:
            return session_mgr.eval(session_id, f'groupscope("{scope}");')
        else:
            return session_mgr.eval(session_id, "temp_scope = groupscope;")

    logger.info("Registered geometry tools")
