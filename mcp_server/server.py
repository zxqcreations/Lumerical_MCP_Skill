"""Lumerical MCP Server - Main entry point.

Provides a comprehensive MCP (Model Context Protocol) server for Ansys Lumerical
photonic simulation tools. Supports FDTD, MODE, DEVICE, and INTERCONNECT products
with v261 features: inverse design (lumopt), CML compiler, Intel MPI, AALI AI.

Usage:
    python -m mcp_server.server
    Or via the CLI entry point: lumerical-mcp
"""

import logging
import sys

from mcp.server.fastmcp import FastMCP

from .tools.session import register_session_tools
from .tools.script import register_script_tools
from .tools.simulation import register_simulation_tools
from .tools.geometry import register_geometry_tools
from .tools.material import register_material_tools
from .tools.source_monitor import register_source_monitor_tools
from .tools.solver import register_solver_tools
from .tools.results import register_results_tools
from .tools.optimization import register_optimization_tools
from .tools.docs import register_docs_tools
from .tools.inverse_design import register_inverse_design_tools
from .tools.cml_compiler import register_cml_compiler_tools
from .tools.interconnect import register_interconnect_tools
from .tools.mpi import register_mpi_tools
from .tools.ai import register_ai_tools

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP("Lumerical MCP")


def register_all_tools() -> None:
    """Register all MCP tools across 14 tool modules."""
    # Core session and scripting
    register_session_tools(mcp)
    register_script_tools(mcp)

    # Simulation lifecycle
    register_simulation_tools(mcp)

    # Geometry and materials
    register_geometry_tools(mcp)
    register_material_tools(mcp)

    # Sources, monitors, solvers
    register_source_monitor_tools(mcp)
    register_solver_tools(mcp)

    # Results and analysis
    register_results_tools(mcp)

    # Optimization and sweeps
    register_optimization_tools(mcp)

    # Documentation and discovery
    register_docs_tools(mcp)

    # v261 new modules
    register_inverse_design_tools(mcp)
    register_cml_compiler_tools(mcp)
    register_interconnect_tools(mcp)
    register_mpi_tools(mcp)
    register_ai_tools(mcp)

    logger.info("Registered all Lumerical MCP v2.2 tools (15 modules)")


def main() -> None:
    """Run the MCP server with stdio transport."""
    logger.info("Starting Lumerical MCP Server v2.2...")
    logger.info(
        "Products: FDTD, MODE, DEVICE, INTERCONNECT | "
        "Commands: 665+ | Transport: stdio | "
        "v2.2: eval fallback, INTERCONNECT scripts, FDE smart defaults, direct getdata"
    )

    register_all_tools()

    # Run the server (stdio transport by default)
    mcp.run()


if __name__ == "__main__":
    main()
