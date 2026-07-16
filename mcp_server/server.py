"""Lumerical MCP Server - Main entry point.

Provides a comprehensive MCP (Model Context Protocol) server for Ansys Lumerical
photonic simulation tools. Supports FDTD, MODE, DEVICE, and INTERCONNECT products.

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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP("Lumerical MCP")


def register_all_tools() -> None:
    """Register all MCP tools."""
    register_session_tools(mcp)
    register_script_tools(mcp)
    register_simulation_tools(mcp)
    register_geometry_tools(mcp)
    register_material_tools(mcp)
    register_source_monitor_tools(mcp)
    register_solver_tools(mcp)
    register_results_tools(mcp)
    register_optimization_tools(mcp)
    register_docs_tools(mcp)
    logger.info("Registered all Lumerical MCP tools")


def main() -> None:
    """Run the MCP server with stdio transport."""
    logger.info("Starting Lumerical MCP Server...")
    logger.info(
        "Products: FDTD, MODE, DEVICE, INTERCONNECT | "
        "Commands: 480+ | Transport: stdio"
    )

    register_all_tools()

    # Run the server (stdio transport by default)
    mcp.run()


if __name__ == "__main__":
    main()
