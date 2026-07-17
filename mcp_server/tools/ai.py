"""AI-assisted simulation tools for Lumerical MCP Server.

Integrates with the AALI (Ansys AI) local AI toolkit when installed.
AALI provides local LLM inference, embeddings, and vector search (Qdrant)
for AI-assisted photonic simulation design, setup, and analysis.

All tools gracefully degrade when AALI is not installed.
"""

import logging
import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Known AALI installation paths (in priority order)
_AALI_SEARCH_PATHS = [
    Path(r"D:\ENV\Lumerical\ANSYS Inc\AI Tools\AALI\v1\installed"),
    Path(r"C:\Program Files\Ansys\AALI"),
    Path(r"C:\ProgramData\ansys-aali"),
]

# Env var that may point to AALI installation
_AALI_ENV_VAR = "AALI_HOME"


def _find_aali() -> dict | None:
    """Search for AALI installation.

    Returns:
        dict with 'path', 'cli_exe', 'manager_exe', 'installed' keys,
        or None if not found.
    """
    import os
    import shutil

    # Check environment variable
    aali_home = os.environ.get(_AALI_ENV_VAR)
    if aali_home:
        p = Path(aali_home)
        if p.exists():
            cli = p / "aali-cli.exe"
            mgr = p / "aali-local-manager.exe"
            return {
                "path": str(p),
                "cli_exe": str(cli) if cli.exists() else None,
                "manager_exe": str(mgr) if mgr.exists() else None,
                "installed": cli.exists(),
                "source": f"env:{_AALI_ENV_VAR}",
            }

    # Check known paths
    for search_path in _AALI_SEARCH_PATHS:
        if search_path.exists():
            cli = search_path / "aali-cli.exe"
            # Manager binary may have arch suffix or not
            mgr_candidates = [
                search_path / "aali-local-manager.exe",
                search_path / "aali-local-manager-windows-amd64.exe",
            ]
            mgr = None
            for mc in mgr_candidates:
                if mc.exists():
                    mgr = mc
                    break

            # Also check for files matching pattern
            if mgr is None:
                import glob
                mgr_patterns = list(search_path.glob("aali-local-manager*"))
                if mgr_patterns:
                    mgr = mgr_patterns[0]

            if cli.exists() or mgr is not None:
                return {
                    "path": str(search_path),
                    "cli_exe": str(cli) if cli.exists() else None,
                    "manager_exe": str(mgr) if mgr else None,
                    "installed": cli.exists(),
                    "source": str(search_path),
                }

    # Check PATH
    cli_path = shutil.which("aali-cli")
    if cli_path:
        p = Path(cli_path).parent
        return {
            "path": str(p),
            "cli_exe": cli_path,
            "manager_exe": str(p / "aali-local-manager.exe"),
            "installed": True,
            "source": "PATH",
        }

    return None


def register_ai_tools(mcp: FastMCP) -> None:
    """Register AI-assisted simulation tools."""

    @mcp.tool()
    def lumerical_ai_status() -> dict:
        """Check AALI AI toolkit installation and service status.

        AALI (Ansys AI) provides local LLM inference, embeddings,
        and vector search for AI-assisted photonic simulation.

        Returns:
            dict with AALI availability and service health
        """
        aali = _find_aali()

        if aali is None or not aali.get("installed"):
            return {
                "success": True,
                "installed": False,
                "message": (
                    "AALI AI toolkit is not installed. To enable AI-assisted "
                    "simulation features, install AALI from the Unextracted "
                    "Artifacts using install-aali.ps1."
                ),
                "install_help": (
                    "Run: .\\install-aali.ps1 -location "
                    "\"D:\\ENV\\Lumerical\\ANSYS Inc\\AI Tools\\AALI\\v1\\installed\" "
                    "-sevenZipExe \"C:\\Program Files\\7-Zip\\7z.exe\""
                ),
            }

        # Check if manager is running
        manager_running = False
        manager_exe = aali.get("manager_exe")
        if manager_exe:
            try:
                mgr_name = Path(manager_exe).name
                result = subprocess.run(
                    ["tasklist", "/FI", f"IMAGENAME eq {mgr_name}"],
                    capture_output=True, text=True, timeout=5,
                )
                manager_running = "aali-local-manager" in result.stdout
            except Exception:
                pass

        return {
            "success": True,
            "installed": True,
            "path": aali["path"],
            "cli_exe": aali.get("cli_exe"),
            "manager_exe": manager_exe,
            "manager_running": manager_running,
            "components": {
                "llm": "Local LLM inference (aali-llm)",
                "embedding": "BGE-M3 embeddings (aali-embedding)",
                "vector_db": "Qdrant vector database (aali-qdrant)",
                "graph_db": "Graph database (aali-graphdb)",
                "kv_store": "Key-value store (aali-kvdb)",
                "agent": "Agent framework (aali-agent)",
            },
            "usage_note": (
                "Start AALI services with aali-local-manager.exe, "
                "then use lumerical_ai_chat and lumerical_ai_search."
            ),
        }

    @mcp.tool()
    def lumerical_ai_chat(prompt: str) -> dict:
        """Ask the AALI AI for simulation design guidance.

        Sends a query to the local AALI AI agent for help with photonic
        simulation design, setup, and troubleshooting.

        Requires AALI services to be running (aali-local-manager started).

        Args:
            prompt: Question or description of what you need help with.
                E.g., "How do I design a grating coupler for 1550nm?"
                or "What mesh settings should I use for a plasmonic structure?"

        Returns:
            dict with AI response or error if AALI not available
        """
        aali = _find_aali()
        if aali is None or not aali.get("installed"):
            return {
                "success": False,
                "error": (
                    "AALI AI toolkit is not installed. "
                    "Use lumerical_ai_status for details."
                ),
            }

        cli = aali.get("cli_exe")
        if cli is None:
            return {
                "success": False,
                "error": "aali-cli.exe not found.",
            }

        try:
            # AALI CLI uses --aali-agent flag with workflow for Q&A
            result = subprocess.run(
                [
                    cli,
                    "--base-dir", aali["path"],
                    "--aali-agent",
                    "--transfer-workflow",
                ],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=120,
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            if stdout:
                return {"success": True, "response": stdout}
            elif stderr:
                return {"success": True, "response": stderr, "note": "Response from stderr"}
            else:
                return {
                    "success": True,
                    "response": "AALI processed the query but returned no output. "
                    "The services may need to be fully initialized.",
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "AALI request timed out (120s). The model may still be loading.",
            }
        except Exception as e:
            return {"success": False, "error": f"AALI request failed: {e}"}

    @mcp.tool()
    def lumerical_ai_search(
        query: str,
        top_k: int = 5,
    ) -> dict:
        """Semantic search over Lumerical simulation knowledge base.

        Uses AALI's Qdrant vector database with BGE-M3 embeddings
        to find relevant simulation documentation and examples.

        Args:
            query: Search query describing what you're looking for
            top_k: Number of results to return (default 5)

        Returns:
            dict with search results
        """
        aali = _find_aali()
        if aali is None or not aali.get("installed"):
            return {
                "success": False,
                "error": "AALI AI toolkit is not installed.",
            }

        cli = aali.get("cli_exe")
        if cli is None:
            return {
                "success": False,
                "error": "aali-cli.exe not found.",
            }

        try:
            result = subprocess.run(
                [
                    cli,
                    "--base-dir", aali["path"],
                    "--load-context-stores",
                ],
                input=query,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return {
                "success": True,
                "query": query,
                "results": result.stdout.strip() or result.stderr.strip(),
            }
        except Exception as e:
            return {"success": False, "error": f"Search failed: {e}"}

    @mcp.tool()
    def lumerical_ai_suggest_material(target_properties: str) -> dict:
        """AI-recommend materials based on target optical/electrical properties.

        Args:
            target_properties: Description of desired material properties.
                E.g., "high refractive index > 3.0 at 1550nm, low loss"
                or "electro-optic coefficient for modulation at 1310nm"

        Returns:
            dict with material recommendations
        """
        aali = _find_aali()
        if aali is None or not aali.get("installed"):
            return {
                "success": False,
                "error": (
                    "AALI AI toolkit is not installed. "
                    "Use lumerical_get_index and lumerical_list_commands('material') "
                    "for manual material exploration."
                ),
            }

        cli = aali.get("cli_exe")
        if cli is None:
            return {
                "success": False,
                "error": "aali-cli.exe not found.",
            }

        prompt = (
            f"Recommend Lumerical-compatible materials with these properties: "
            f"{target_properties}. List material names, approximate refractive "
            f"index values, and common uses in photonic integrated circuits."
        )
        try:
            result = subprocess.run(
                [
                    cli,
                    "--base-dir", aali["path"],
                    "--aali-agent",
                    "--transfer-workflow",
                ],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60,
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            return {
                "success": True,
                "query": target_properties,
                "recommendations": stdout or stderr or "No detailed output from AALI.",
            }
        except Exception as e:
            return {"success": False, "error": f"Material suggestion failed: {e}"}

    @mcp.tool()
    def lumerical_ai_setup_simulation(description: str) -> dict:
        """AI-generate a simulation setup script from a natural language description.

        Describes your simulation needs in plain language, and the AI
        generates the corresponding Lumerical script code.

        Args:
            description: Natural language description of the simulation.
                E.g., "2D FDTD simulation of a silicon waveguide with
                a square cross-section, TE mode source at 1550nm,
                with power and field profile monitors"

        Returns:
            dict with generated script code
        """
        aali = _find_aali()
        if aali is None or not aali.get("installed"):
            return {
                "success": False,
                "error": (
                    "AALI AI toolkit is not installed. "
                    "Use lumerical_eval with manual LSF scripting instead."
                ),
            }

        cli = aali.get("cli_exe")
        if cli is None:
            return {
                "success": False,
                "error": "aali-cli.exe not found.",
            }

        prompt = (
            f"Generate a complete Lumerical script (LSF) code for this simulation "
            f"description: {description}. Provide the full runnable LSF code with "
            f"all necessary commands in logical order: (1) solver/addfdtd setup, "
            f"(2) geometry/structures, (3) sources/excitation, (4) monitors/data "
            f"collection, (5) run command. Use standard material names from the "
            f"Lumerical database. Add clear comments for each section. "
            f"Use SI units (meters) for all dimensions."
        )
        try:
            result = subprocess.run(
                [
                    cli,
                    "--base-dir", aali["path"],
                    "--aali-agent",
                    "--transfer-workflow",
                ],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=120,
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            return {
                "success": True,
                "description": description,
                "generated_code": stdout or stderr or "No code generated.",
                "note": (
                    "Review the generated code before executing. "
                    "Use lumerical_eval to run it."
                ),
            }
        except Exception as e:
            return {"success": False, "error": f"Script generation failed: {e}"}

    logger.info("Registered AI-assisted simulation tools")
