"""CML Compiler tools for Lumerical MCP Server.

Wraps the v261 CML Compiler CLI for photonic foundry PDK development.
The CML Compiler converts compact model specifications into simulation-ready
INTERCONNECT elements. Includes 25+ pre-built photonic models.
"""

import logging
import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP

from ..session_manager import get_cml_compiler_path, get_lumerical_api_path

logger = logging.getLogger(__name__)

# 25+ pre-built photonic models in the CML compiler
_CML_MODELS = {
    "compound_element": "Generic compound element (hierarchical composition)",
    "container_element": "Container element for grouping sub-elements",
    "directional_coupler_parameterized": "Parameterized directional coupler",
    "electro_absorption_modulator": "Electro-absorption modulator (EAM)",
    "fiber_array": "Fiber array coupler",
    "grating_coupler": "Grating coupler for fiber-to-chip coupling",
    "mach_zehnder_modulator": "Mach-Zehnder modulator (MZM)",
    "mach_zehnder_modulator_2x2": "2x2 MZM with balanced outputs",
    "phase_shifter_electrical": "Electrical phase shifter (carrier depletion/injection)",
    "phase_shifter_thermal": "Thermal phase shifter (heater-based)",
    "photodetector_avalanche": "Avalanche photodetector (APD)",
    "photodetector_pcell": "Parameterized cell photodetector",
    "photodetector_simple": "Simple photodetector model",
    "ring_modulator": "Ring resonator modulator",
    "ring_modulator_parameterized": "Parameterized ring modulator",
    "scripted_element": "User-scripted custom element",
    "spar_fixed": "Fixed S-parameter element (from file)",
    "sparsweep_pcell": "S-parameter sweep parameterized cell",
    "time_variant_spar": "Time-variant S-parameter element",
    "tunable_ring_switch": "Tunable ring resonator switch",
    "veriloga_scripted_element": "Verilog-A scripted element",
    "waveguide_back_annotation": "Waveguide with back-annotation support",
    "waveguide_connector": "Waveguide connector element",
    "waveguide_simple": "Simple waveguide model",
    "wg_parameterized": "Parameterized waveguide",
}


def _find_cml_exe() -> str | None:
    """Find the cml-compiler executable."""
    # Check PATH first
    import shutil
    exe = shutil.which("cml-compiler")
    if exe:
        return exe

    # Check v261 CML Compiler directory
    cml_path = get_cml_compiler_path()
    if cml_path:
        exe = Path(cml_path) / "cml-compiler.exe"
        if exe.exists():
            return str(exe)
        # Linux
        exe = Path(cml_path) / "cml-compiler"
        if exe.exists():
            return str(exe)

    # Check default ANSYS Inc path
    api_path = get_lumerical_api_path()
    if api_path:
        default_cml = (
            Path(api_path).parent.parent / "CML_Compiler" / "bin" / "cml-compiler.exe"
        )
        if default_cml.exists():
            return str(default_cml)

    return None


def register_cml_compiler_tools(mcp: FastMCP) -> None:
    """Register CML compiler tools."""

    @mcp.tool()
    def lumerical_cml_list_models() -> dict:
        """List all 25+ pre-built photonic models in the CML compiler.

        Each model can be compiled into an INTERCONNECT-compatible
        compact model element for photonic circuit simulation.

        Returns:
            dict with model names and descriptions
        """
        return {
            "success": True,
            "model_count": len(_CML_MODELS),
            "models": _CML_MODELS,
        }

    @mcp.tool()
    def lumerical_cml_status() -> dict:
        """Check CML Compiler availability and version.

        Returns:
            dict with CML compiler status
        """
        exe = _find_cml_exe()
        if exe is None:
            return {
                "success": True,
                "available": False,
                "message": (
                    "CML Compiler not found. Install v261 in the default "
                    "location or add CML_Compiler/bin to PATH."
                ),
            }

        try:
            result = subprocess.run(
                [exe, "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            version_info = result.stdout[:500] if result.stdout else ""
        except Exception as e:
            version_info = f"Could not get version: {e}"

        return {
            "success": True,
            "available": True,
            "executable": exe,
            "version_info": version_info,
        }

    @mcp.tool()
    def lumerical_cml_deploy(directory: str) -> dict:
        """Deploy the lumfoundry template for a new PDK project.

        Creates a new CML library directory with the lumfoundry template
        containing example models and build scripts.

        Args:
            directory: Target directory for the new foundry project

        Returns:
            dict with deployment status
        """
        exe = _find_cml_exe()
        if exe is None:
            return {
                "success": False,
                "error": "CML Compiler not found. Install v261 first.",
            }

        try:
            import os
            target = Path(directory)
            target.mkdir(parents=True, exist_ok=True)

            result = subprocess.run(
                [exe, "template"],
                cwd=str(target),
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"CML template deployment failed: {result.stderr}",
                }

            return {
                "success": True,
                "message": f"Deployed lumfoundry template to {directory}",
                "output": result.stdout,
            }
        except Exception as e:
            return {"success": False, "error": f"Deployment failed: {e}"}

    @mcp.tool()
    def lumerical_cml_build(directory: str) -> dict:
        """Build and install the CML library.

        Compiles all compact models in the library and generates
        QA test files for verification.

        Args:
            directory: Path to the CML library directory (with lumfoundry_template)

        Returns:
            dict with build status
        """
        exe = _find_cml_exe()
        if exe is None:
            return {
                "success": False,
                "error": "CML Compiler not found.",
            }

        try:
            result = subprocess.run(
                [exe, "all"],
                cwd=str(directory),
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"CML build failed: {result.stderr}",
                    "partial_output": result.stdout,
                }

            return {
                "success": True,
                "message": "CML library built and installed successfully.",
                "output": result.stdout,
            }
        except Exception as e:
            return {"success": False, "error": f"Build failed: {e}"}

    @mcp.tool()
    def lumerical_cml_validate(directory: str) -> dict:
        """Validate a CML library.

        Checks the library for errors, missing dependencies, and
        compliance with the CML specification.

        Args:
            directory: Path to the CML library directory

        Returns:
            dict with validation results
        """
        exe = _find_cml_exe()
        if exe is None:
            return {
                "success": False,
                "error": "CML Compiler not found.",
            }

        try:
            result = subprocess.run(
                [exe, "validate"],
                cwd=str(directory),
                capture_output=True,
                text=True,
                timeout=120,
            )
            return {
                "success": result.returncode == 0,
                "message": (
                    "Validation passed." if result.returncode == 0
                    else "Validation failed."
                ),
                "output": result.stdout,
                "errors": result.stderr if result.returncode != 0 else "",
            }
        except Exception as e:
            return {"success": False, "error": f"Validation failed: {e}"}

    @mcp.tool()
    def lumerical_cml_compile_element(
        directory: str,
        element_name: str,
    ) -> dict:
        """Compile a single CML element.

        Args:
            directory: Path to the CML library directory
            element_name: Name of the element to compile

        Returns:
            dict with compilation status
        """
        exe = _find_cml_exe()
        if exe is None:
            return {
                "success": False,
                "error": "CML Compiler not found.",
            }

        try:
            result = subprocess.run(
                [exe, "compile", element_name],
                cwd=str(directory),
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Compilation of '{element_name}' failed: {result.stderr}",
                }
            return {
                "success": True,
                "message": f"Compiled element: {element_name}",
                "output": result.stdout,
            }
        except Exception as e:
            return {"success": False, "error": f"Compilation failed: {e}"}

    logger.info("Registered CML compiler tools")
