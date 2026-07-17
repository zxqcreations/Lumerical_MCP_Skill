"""Command documentation loader for Lumerical MCP Server.

Loads and queries Lumerical scripting command documentation from:
1. The bundled docs.json (from Lumerical installation, v261: 665 commands)
2. The lumerical-docs Markdown repository (if available)
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CommandDocs:
    """Load and query Lumerical command documentation."""

    def __init__(self) -> None:
        self._commands: dict[str, dict] = {}
        self._loaded = False

    def load(self) -> None:
        """Load command documentation from available sources."""
        if self._loaded:
            return

        # Try to load from Lumerical API path
        from .session_manager import _find_lumerical_api

        api_path = _find_lumerical_api()
        if api_path:
            docs_json = Path(api_path) / "docs.json"
            if docs_json.exists():
                try:
                    with open(docs_json, "r", encoding="utf-8") as f:
                        self._commands = json.load(f)
                    logger.info(
                        f"Loaded {len(self._commands)} commands from {docs_json}"
                    )
                except Exception as e:
                    logger.warning(f"Failed to load docs.json: {e}")

        # Try to load from lumerical-docs repo (for detailed Markdown docs)
        candidates = [
            Path(r"D:\ENV\claude\Lumerical_MCP\lumerical-docs\docs\lsf-script\en"),
            Path("./lumerical-docs/docs/lsf-script/en"),
            Path("../lumerical-docs/docs/lsf-script/en"),
        ]
        self._markdown_docs_dir: Optional[Path] = None
        for candidate in candidates:
            if candidate.exists() and candidate.is_dir():
                self._markdown_docs_dir = candidate
                logger.info(f"Found Markdown docs at: {candidate}")
                break

        self._loaded = True

    @property
    def command_count(self) -> int:
        """Total number of known commands."""
        return len(self._commands)

    def get_all_commands(self) -> list[str]:
        """Get all command names."""
        self.load()
        return sorted(self._commands.keys())

    def get_command_info(self, command: str) -> Optional[dict]:
        """Get basic info for a command."""
        self.load()
        return self._commands.get(command.lower())

    def get_command_help(self, command: str) -> dict:
        """Get detailed help for a command.

        Returns:
            dict with 'name', 'link', 'text' (from docs.json),
            and 'markdown' (from .md file)
        """
        self.load()
        cmd = command.lower().strip()
        info = self._commands.get(cmd)

        if not info:
            return {
                "success": False,
                "error": (
                    f"No documentation found for command '{command}'. "
                    f"Use lumerical_list_commands to see available commands."
                ),
            }

        result = {
            "success": True,
            "name": cmd,
            "link": info.get("link", ""),
            "summary": info.get("text", ""),
        }

        # Try to load detailed Markdown documentation
        if self._markdown_docs_dir:
            md_file = self._markdown_docs_dir / f"{cmd}.md"
            if md_file.exists():
                try:
                    content = md_file.read_text(encoding="utf-8")
                    result["markdown"] = content
                except Exception as e:
                    logger.warning(f"Failed to read {md_file}: {e}")

        return result

    def search_commands(self, query: str, max_results: int = 30) -> dict:
        """Search for commands matching a query.

        Searches command names and documentation text.

        Args:
            query: Search query string
            max_results: Maximum number of results

        Returns:
            dict with matching commands
        """
        self.load()
        query_lower = query.lower()
        results = []

        for name, info in self._commands.items():
            score = 0
            if query_lower in name.lower():
                score = 100
            elif query_lower in info.get("text", "").lower():
                score = 50

            if score > 0:
                results.append({
                    "name": name,
                    "summary": info.get("text", ""),
                    "link": info.get("link", ""),
                    "score": score,
                })

        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:max_results]

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "commands": results,
        }

    def get_commands_by_category(self) -> dict:
        """Get commands organized by functional category.

        v261 categories include new RCWA, DGTD, device physics,
        and inverse design command groupings.
        """
        self.load()

        categories = {
            "solver": {
                "name": "Solvers & Simulation Setup",
                "keywords": [
                    "solver", "fdtd", "fde", "eme", "varfdtd", "dgt",
                    "rcwa", "analysis", "mesh", "boundary", "pml",
                    "periodic", "simulation region", "feem",
                ],
                "commands": [],
            },
            "geometry": {
                "name": "Geometry & Structures",
                "keywords": [
                    "rect", "sphere", "circle", "ring", "polygon",
                    "waveguide", "plane", "triangle", "pyramid",
                    "surface", "planarsolid", "structure", "group",
                    "layer", "path", "import", "stl", "gds",
                    "field region", "assembly group",
                ],
                "commands": [],
            },
            "source": {
                "name": "Sources & Excitation",
                "keywords": [
                    "source", "dipole", "mode", "gaussian", "beam",
                    "tfsf", "importedsource", "global source",
                    "delta charge", "electrical contact",
                ],
                "commands": [],
            },
            "monitor": {
                "name": "Monitors & Data Collection",
                "keywords": [
                    "monitor", "power", "profile", "index", "field",
                    "time", "movie", "frequency", "transmission",
                    "absorption", "farfield", "mode expansion", "port",
                    "rcwa field", "dft", "charge", "heat flux",
                    "temperature", "jflux", "bandstructure",
                ],
                "commands": [],
            },
            "material": {
                "name": "Materials",
                "keywords": [
                    "material", "index", "nk", "conductivity",
                    "permittivity", "model", "sampled", "property",
                    "ct material", "ht material", "em material",
                ],
                "commands": [],
            },
            "simulation": {
                "name": "Simulation Control",
                "keywords": [
                    "run", "simulation", "sweep", "optimize",
                    "parameter", "job", "parallel", "convergence",
                    "resource",
                ],
                "commands": [],
            },
            "results": {
                "name": "Results & Post-Processing",
                "keywords": [
                    "result", "data", "get", "export", "visualize",
                    "plot", "field", "transmission", "farfield",
                    "mode", "sweep result", "dataset",
                ],
                "commands": [],
            },
            "utility": {
                "name": "Utility & Math",
                "keywords": [
                    "select", "set", "delete", "copy", "move",
                    "rotate", "group", "scope", "save", "load",
                    "clear", "matlab", "system", "file", "cd",
                    "pwd", "ls", "abs", "sin", "cos", "log",
                    "exp", "fft", "matrix", "interp", "integrate",
                ],
                "commands": [],
            },
            "scripting": {
                "name": "Scripting Language",
                "keywords": [
                    "eval", "script", "function", "variable",
                    "if", "for", "while", "break", "return",
                    "struct", "cell", "matrix", "string",
                    "format", "sprintf", "print",
                ],
                "commands": [],
            },
            "interconnect": {
                "name": "INTERCONNECT Specific",
                "keywords": [
                    "element", "netlist", "schematic", "port",
                    "analyzer", "transmission line",
                    "optical network",
                ],
                "commands": [],
            },
            "device": {
                "name": "DEVICE Specific",
                "keywords": [
                    "charge", "heat", "thermal", "electrical",
                    "doping", "contact", "voltage", "current",
                    "semiconductor", "diffusion", "generation",
                    "recombination", "implant", "bulk gen",
                ],
                "commands": [],
            },
            "inverse_design": {
                "name": "Inverse Design & Optimization",
                "keywords": [
                    "optimization", "adjoint", "gradient",
                    "figure of merit", "topology", "fabrication",
                    "inverse design",
                ],
                "commands": [],
            },
        }

        # Classify each command
        for name, info in self._commands.items():
            text = (name + " " + info.get("text", "")).lower()
            best_category = "utility"  # default
            best_score = 0

            for cat_key, cat_info in categories.items():
                score = sum(
                    1 for kw in cat_info["keywords"] if kw in text
                )
                if score > best_score:
                    best_score = score
                    best_category = cat_key

            categories[best_category]["commands"].append({
                "name": name,
                "summary": info.get("text", ""),
                "link": info.get("link", ""),
            })

        # Remove empty categories, sort commands alphabetically
        result = {}
        for key, cat in categories.items():
            if cat["commands"]:
                cat["commands"].sort(key=lambda x: x["name"])
                cat["count"] = len(cat["commands"])
                result[key] = cat

        return {"success": True, "categories": result}
