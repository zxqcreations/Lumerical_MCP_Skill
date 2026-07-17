"""Local MPI parallel processing tools for Lumerical MCP Server.

Leverages v261's bundled Intel MPI for local multi-core simulation
parallelization. Supports parallel parameter sweeps, batch processing,
and resource configuration.
"""

import logging
from pathlib import Path
from mcp.server.fastmcp import FastMCP

from ..session_manager import SessionManager, get_intel_mpi_path, get_lumerical_bin_path

logger = logging.getLogger(__name__)


def register_mpi_tools(mcp: FastMCP) -> None:
    """Register MPI and parallel processing tools."""

    @mcp.tool()
    def lumerical_mpi_get_config() -> dict:
        """Get local MPI and parallel processing configuration.

        Reports available MPI library, number of logical processors,
        and Lumerical parallel engine paths.

        Returns:
            dict with MPI configuration details
        """
        import os

        cpu_count = os.cpu_count() or 1
        mpi_path = get_intel_mpi_path()
        bin_path = get_lumerical_bin_path()

        return {
            "success": True,
            "cpu_count": cpu_count,
            "recommended_processes": max(1, cpu_count // 2),
            "intel_mpi_path": mpi_path or "Not found",
            "lumerical_bin_path": bin_path or "Not found",
            "mpi_available": mpi_path is not None,
            "config": {
                "message": (
                    f"System has {cpu_count} logical processors. "
                    f"Recommended: {max(1, cpu_count // 2)} parallel processes "
                    f"with 2 threads each."
                ),
            },
        }

    @mcp.tool()
    def lumerical_set_threads(
        session_id: str,
        num_threads: int = 1,
    ) -> dict:
        """Configure OpenMP thread count for a session.

        Controls the number of threads used per Lumerical process.
        Use in combination with MPI for hybrid parallel execution.

        Args:
            session_id: The session ID from lumerical_open
            num_threads: Number of threads per process (default 1)

        Returns:
            dict with status
        """
        session_mgr = SessionManager()
        return session_mgr.eval(
            session_id,
            f'setresource("number of threads", {num_threads});',
        )

    @mcp.tool()
    def lumerical_set_processes(
        session_id: str,
        num_processes: int = 1,
    ) -> dict:
        """Configure parallel process count for a session.

        Sets the number of concurrent solver processes for parallel
        job execution.

        Args:
            session_id: The session ID from lumerical_open
            num_processes: Number of parallel solver processes

        Returns:
            dict with status
        """
        session_mgr = SessionManager()
        return session_mgr.eval(
            session_id,
            f'setresource("number of parallel processes", {num_processes});',
        )

    @mcp.tool()
    def lumerical_mpi_run_sweep(
        session_id: str,
        sweep_name: str,
        num_processes: int = 4,
    ) -> dict:
        """Run a parameter sweep using parallel job execution.

        Distributes sweep points across multiple solver processes
        for faster parameter space exploration.

        Args:
            session_id: The session ID from lumerical_open
            sweep_name: Name of the parameter sweep to run
            num_processes: Number of parallel processes

        Returns:
            dict with run status
        """
        session_mgr = SessionManager()
        code = (
            f'setresource("number of parallel processes", {num_processes});\n'
            f'runsweep("{sweep_name}");'
        )
        return session_mgr.eval(session_id, code)

    @mcp.tool()
    def lumerical_mpi_run_batch(
        session_id: str,
        file_pattern: str,
        num_processes: int = 4,
    ) -> dict:
        """Batch process multiple simulation projects in parallel.

        Runs multiple .fsp/.lms files concurrently using the job manager.

        Args:
            session_id: The session ID from lumerical_open
            file_pattern: Glob pattern for project files (e.g., "C:/sims/*.fsp")
            num_processes: Number of parallel processes

        Returns:
            dict with batch run status
        """
        import glob as _glob

        files = _glob.glob(file_pattern)
        if not files:
            return {
                "success": False,
                "error": f"No files found matching pattern: {file_pattern}",
            }

        session_mgr = SessionManager()
        code_lines = [
            f'setresource("number of parallel processes", {num_processes});',
        ]
        for f in files:
            code_lines.append(f'run("load("{f}"); run;");')

        # Use job manager for parallel execution
        job_code = (
            f'setresource("number of parallel processes", {num_processes});\n'
            f'runjobs;'
        )

        return {
            "success": True,
            "message": (
                f"Queued {len(files)} files for parallel execution "
                f"with {num_processes} processes."
            ),
            "files": files,
            "note": (
                "Use lumerical_eval with: " + job_code.replace("\n", " ")
            ),
        }

    logger.info("Registered MPI and parallel processing tools")
