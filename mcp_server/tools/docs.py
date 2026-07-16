"""Documentation and discovery tools for Lumerical MCP Server."""

import logging
from mcp.server.fastmcp import FastMCP

from ..command_docs import CommandDocs

logger = logging.getLogger(__name__)

_docs = CommandDocs()


def register_docs_tools(mcp: FastMCP) -> None:
    """Register documentation and discovery tools."""

    @mcp.tool()
    def lumerical_list_commands(
        category: str = "",
        limit: int = 100,
    ) -> dict:
        """List all available Lumerical script commands.

        Returns the hundreds of commands available through the lumerical_eval
        and lumerical_call tools. You can filter by category or get a subset.

        Categories: 'solver', 'geometry', 'source', 'monitor', 'material',
        'simulation', 'results', 'utility', 'scripting', 'interconnect', 'device'

        Args:
            category: Filter by category (empty = all commands)
            limit: Maximum number to return (default 100, max 500)

        Returns:
            dict with command list
        """
        _docs.load()

        if category:
            categories = _docs.get_commands_by_category()
            cat_data = categories.get("categories", {}).get(category)
            if cat_data:
                return {
                    "success": True,
                    "category": cat_data["name"],
                    "count": cat_data["count"],
                    "commands": cat_data["commands"][:min(limit, 500)],
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown category '{category}'. Use lumerical_get_categories to see options.",
                }

        commands = _docs.get_all_commands()
        total = len(commands)
        commands = commands[:min(limit, 500)]

        # Get info for each command
        result = []
        for cmd in commands:
            info = _docs.get_command_info(cmd)
            result.append({
                "name": cmd,
                "summary": info.get("text", "") if info else "",
                "link": info.get("link", "") if info else "",
            })

        return {
            "success": True,
            "command_count": total,
            "returned": len(result),
            "commands": result,
        }

    @mcp.tool()
    def lumerical_get_categories() -> dict:
        """List all command categories with counts.

        Returns the functional categories that commands are organized into,
        with the number of commands in each category.

        Returns:
            dict with category names and counts
        """
        _docs.load()
        categories = _docs.get_commands_by_category()
        result = {}
        for key, cat in categories.get("categories", {}).items():
            result[key] = {
                "name": cat["name"],
                "count": cat["count"],
            }
        return {"success": True, "categories": result}

    @mcp.tool()
    def lumerical_get_command_help(command: str) -> dict:
        """Get detailed help and documentation for a Lumerical command.

        Returns comprehensive documentation including syntax, description,
        examples, and links to full reference docs. When available, also
        includes Markdown documentation from the local lumerical-docs repository.

        Args:
            command: Command name (e.g., 'addfdtd', 'addrect', 'set', 'run')

        Returns:
            dict with command documentation
        """
        _docs.load()
        return _docs.get_command_help(command)

    @mcp.tool()
    def lumerical_search_commands(
        query: str,
        max_results: int = 30,
    ) -> dict:
        """Search for Lumerical commands by keyword.

        Searches command names and documentation summaries. Returns the most
        relevant matches sorted by relevance score.

        Examples:
        - Search 'waveguide' → finds addwaveguide, bentwaveguide, etc.
        - Search 'source' → finds all source-related commands
        - Search 'farfield' → finds far-field projection commands
        - Search 'mesh' → finds mesh and grid-related commands

        Args:
            query: Search keyword(s)
            max_results: Maximum number of results (default 30)

        Returns:
            dict with matching commands sorted by relevance
        """
        _docs.load()
        return _docs.search_commands(query, max_results)

    @mcp.tool()
    def lumerical_get_script_help(command: str) -> dict:
        """Get detailed Markdown help for a script command.

        Returns the full Markdown documentation file from the lumerical-docs
        repository, which includes comprehensive syntax, parameter descriptions,
        examples, and related commands.

        Args:
            command: Command name (e.g., 'addfdtd', 'addrect', 'run')

        Returns:
            dict with full Markdown documentation
        """
        _docs.load()
        return _docs.get_command_help(command)

    @mcp.tool()
    def lumerical_list_examples(category: str = "") -> dict:
        """List available example simulation files.

        Shows the built-in example files from Lumerical's FDTD and MODE libraries.

        Categories: 'fdtd', 'mode', 'device', 'interconnect'

        Args:
            category: Filter by product category

        Returns:
            dict with example file list
        """
        from pathlib import Path

        examples = {
            "fdtd": {
                "path": r"D:\ENV\Lumerical\v202\Resources\fdtd-library",
                "files": [],
            },
            "mode": {
                "path": r"D:\ENV\Lumerical\v202\Resources\mode-library",
                "files": [],
            },
        }

        for key, info in examples.items():
            if category and key != category:
                continue
            p = Path(info["path"])
            if p.exists():
                for f in sorted(p.glob("*.fsp")) + sorted(p.glob("*.lms")):
                    info["files"].append({
                        "name": f.name,
                        "product": key,
                        "size": f.stat().st_size,
                    })

        if category:
            data = examples.get(category)
            if data and data["files"]:
                return {
                    "success": True,
                    "category": category,
                    "count": len(data["files"]),
                    "files": data["files"],
                }
            else:
                return {"success": False, "error": f"No examples found for '{category}'."}

        total = sum(len(v["files"]) for v in examples.values())
        return {
            "success": True,
            "total": total,
            "examples": examples,
        }

    logger.info("Registered documentation and discovery tools")
