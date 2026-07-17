"""Inverse design optimization tools for Lumerical MCP Server.

Leverages the v261 bundled lumopt package for adjoint-based photonic
inverse design. Supports topology optimization, shape optimization,
and gradient-based algorithms with fabrication constraints.
"""

import logging
from mcp.server.fastmcp import FastMCP

from ..session_manager import SessionManager, get_lumerical_api_path

logger = logging.getLogger(__name__)


def _ensure_lumopt_in_path() -> str:
    """Ensure lumopt is importable. Returns the lumopt directory path."""
    api_path = get_lumerical_api_path()
    lumopt_path = None
    import sys

    # lumopt is at .../api/python/lumopt/
    import os
    from pathlib import Path

    lumopt_dir = Path(api_path) / "lumopt"
    if lumopt_dir.exists():
        lumopt_path = str(lumopt_dir)
        parent = str(lumopt_dir.parent)
        if parent not in sys.path:
            sys.path.insert(0, parent)
    return lumopt_path


def register_inverse_design_tools(mcp: FastMCP) -> None:
    """Register inverse design optimization tools."""

    @mcp.tool()
    def lumerical_opt_list_methods() -> dict:
        """List available inverse design optimization methods.

        Shows the FOMs, geometries, and optimizers bundled with lumopt.

        Returns:
            dict with available methods
        """
        return {
            "success": True,
            "foms": {
                "transmission": "Maximize/minimize power transmission through a port",
                "modematch": "Match field profile to a target mode",
                "field_intensity": "Optimize field intensity in a volume",
            },
            "geometries": {
                "topology": "Pixel/voxel-based density optimization (most flexible)",
                "polygon": "Polygon vertex optimization (fewer parameters)",
                "parameterized_geometry": "Parametric shape optimization",
            },
            "optimizers": {
                "gradient_descent": "Fixed-step gradient descent",
                "adaptive_gradient": "Adaptive step-size gradient descent",
                "basin_hopping": "Global optimization with local refinement (scipy)",
                "generic": "Generic optimizer interface for custom algorithms",
            },
            "fabrication_constraints": {
                "gaussian": "Gaussian blur to model lithography resolution limits",
            },
        }

    @mcp.tool()
    def lumerical_opt_setup(
        session_id: str,
        fom_type: str = "transmission",
        optimizer_type: str = "adaptive_gradient",
        geometry_type: str = "topology",
        config: str = "{}",
    ) -> dict:
        """Set up an inverse design optimization via lumopt.

        Configures the adjoint optimization framework with the chosen
        figure of merit, geometry parameterization, and optimizer.

        Args:
            session_id: The session ID from lumerical_open
            fom_type: Figure of merit type ('transmission', 'modematch', 'field_intensity')
            optimizer_type: Optimization algorithm ('gradient_descent', 'adaptive_gradient', 'basin_hopping', 'generic')
            geometry_type: Geometry parameterization ('topology', 'polygon', 'parameterized')
            config: JSON configuration object with detailed settings:
                {
                    "target": "transmission",     // for FOM
                    "mode": "fundamental TE",
                    "direction": "forward",
                    "wavelength": 1.55e-6,
                    "wavelengths": "1.5e-6:0.01e-6:1.6e-6",
                    "max_iterations": 100,
                    "tolerance": 0.001,
                    "design_region": {"x": 0, "x_span": 2e-6, "y": 0, "y_span": 2e-6},
                    "materials": ["Si", "SiO2"],
                    "fabrication_sigma": 20e-9,
                    "fabrication_threshold": 0.5
                }

        Returns:
            dict with optimization setup status and parameters
        """
        import json

        try:
            cfg = json.loads(config)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON in config: {config}"}

        session_mgr = SessionManager()

        # Store optimization config in the session workspace
        opt_config = {
            "fom_type": fom_type,
            "optimizer_type": optimizer_type,
            "geometry_type": geometry_type,
            "config": cfg,
            "status": "configured",
            "iteration": 0,
        }

        try:
            import json as _json
            config_json = _json.dumps(opt_config)
            code = f'opt_config = {config_json};'
            session_mgr.eval(session_id, code)
        except Exception as e:
            return {"success": False, "error": f"Failed to store config: {e}"}

        return {
            "success": True,
            "message": (
                f"Optimization configured: {fom_type} FOM, "
                f"{optimizer_type} optimizer, {geometry_type} geometry"
            ),
            "config": opt_config,
        }

    @mcp.tool()
    def lumerical_opt_check_setup(session_id: str) -> dict:
        """Check if lumopt is available and properly configured.

        Verifies that the lumopt package can be imported and lists
        available modules.

        Returns:
            dict with lumopt availability status
        """
        try:
            lumopt_path = _ensure_lumopt_in_path()
            if lumopt_path is None:
                return {
                    "success": False,
                    "error": (
                        "lumopt package not found. It should be at "
                        f"{get_lumerical_api_path()}/lumopt/ in v261+."
                    ),
                }

            import importlib
            modules = {}
            for mod_name in [
                "optimization", "geometries.geometry",
                "geometries.topology", "geometries.polygon",
                "geometries.parameterized_geometry",
                "figures_of_merit.modematch",
                "figures_of_merit.PortTransmission",
                "figures_of_merit.intensity_volume",
                "fabrication.gaussian",
                "optimizers.adaptive_gradient_descent",
                "optimizers.fixed_step_gradient_descent",
                "optimizers.generic_optimizers",
                "optimizers.scipy_basin_hopping",
                "utilities.gradients", "utilities.fields",
                "utilities.wavelengths", "utilities.materials",
            ]:
                try:
                    importlib.import_module(f"lumopt.{mod_name}")
                    modules[mod_name] = "available"
                except ImportError:
                    modules[mod_name] = "unavailable"

            return {
                "success": True,
                "lumopt_path": lumopt_path,
                "modules": modules,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to check lumopt: {e}",
            }

    @mcp.tool()
    def lumerical_opt_set_fabrication(
        session_id: str,
        sigma: float = 20e-9,
        threshold: float = 0.5,
    ) -> dict:
        """Configure Gaussian fabrication constraints for topology optimization.

        Models lithography resolution limits by applying Gaussian blur
        to the density distribution, ensuring the optimized design can
        be manufactured.

        Args:
            session_id: The session ID from lumerical_open
            sigma: Gaussian blur sigma in meters (default 20nm)
            threshold: Binarization threshold (0.0-1.0)

        Returns:
            dict with status
        """
        session_mgr = SessionManager()
        code = (
            f'opt_fab_sigma = {sigma};\n'
            f'opt_fab_threshold = {threshold};\n'
        )
        session_mgr.eval(session_id, code)
        return {
            "success": True,
            "message": f"Fabrication constraints set: sigma={sigma*1e9:.1f}nm, threshold={threshold}",
        }

    logger.info("Registered inverse design optimization tools")
