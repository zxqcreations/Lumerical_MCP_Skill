"""Tests for Lumerical MCP Server.

These tests verify the server can be imported, all tools register correctly,
and the documentation system works without requiring an active Lumerical session.
"""

import pytest


class TestServerImport:
    """Test that the MCP server imports and initializes correctly."""

    def test_import_server(self):
        """Server module should import without errors."""
        from mcp_server.server import mcp

        assert mcp is not None
        assert mcp.name == "Lumerical MCP"

    def test_register_all_tools(self):
        """All tools should register without errors."""
        from mcp_server.server import mcp, register_all_tools

        register_all_tools()

        # FastMCP stores tools in a ToolManager
        # Access via internal attribute for testing
        tools = mcp._tool_manager._tools if hasattr(mcp, '_tool_manager') else {}
        assert len(tools) > 0, "No tools were registered"
        # v2.0 has 14 modules, ~70+ tools
        assert len(tools) >= 60, f"Expected at least 60 tools, got {len(tools)}"

    def test_v261_modules_registered(self):
        """New v261 modules should register their tools."""
        from mcp_server.server import mcp, register_all_tools

        register_all_tools()

        tools = mcp._tool_manager._tools if hasattr(mcp, '_tool_manager') else {}
        tool_names = list(tools.keys())

        # v261-specific tools should exist
        v261_tools = [
            "lumerical_opt_list_methods",
            "lumerical_opt_setup",
            "lumerical_opt_check_setup",
            "lumerical_cml_list_models",
            "lumerical_cml_status",
            "lumerical_mpi_get_config",
            "lumerical_set_threads",
            "lumerical_ai_status",
            "lumerical_use_gpu",
            "lumerical_get_s_parameters",
            "lumerical_get_convergence",
            "lumerical_get_status",
        ]
        found = [t for t in v261_tools if t in tool_names]
        missing = [t for t in v261_tools if t not in tool_names]

        assert len(found) >= 8, (
            f"Expected at least 8 v261 tools, found {len(found)}. "
            f"Missing: {missing}"
        )

    def test_all_tool_names_prefixed(self):
        """All tools should use lumerical_ prefix."""
        from mcp_server.server import mcp

        tools = mcp._tool_manager._tools if hasattr(mcp, '_tool_manager') else {}
        for name in tools:
            assert name.startswith("lumerical_"), f"Tool {name} missing lumerical_ prefix"


class TestSessionManager:
    """Test session manager without Lumerical."""

    def test_singleton(self):
        """SessionManager should be a singleton."""
        from mcp_server.session_manager import SessionManager

        mgr1 = SessionManager()
        mgr2 = SessionManager()
        assert mgr1 is mgr2

    def test_list_sessions_empty(self):
        """Listing sessions should work with no active sessions."""
        from mcp_server.session_manager import SessionManager

        mgr = SessionManager()
        result = mgr.list_sessions()
        assert result["success"] is True
        assert result["count"] == 0

    def test_invalid_product(self):
        """Opening invalid product should fail gracefully."""
        from mcp_server.session_manager import SessionManager

        mgr = SessionManager()
        result = mgr.open("invalid_product")
        assert result["success"] is False
        assert "Invalid product" in result.get("error", "")

    def test_close_nonexistent_session(self):
        """Closing non-existent session should fail gracefully."""
        from mcp_server.session_manager import SessionManager

        mgr = SessionManager()
        result = mgr.close("nonexistent_id")
        assert result["success"] is False
        assert "not found" in result.get("error", "")

    def test_is_connected_nonexistent(self):
        """is_connected should report session not found."""
        from mcp_server.session_manager import SessionManager

        mgr = SessionManager()
        result = mgr.is_connected("nonexistent_id")
        assert result["success"] is False
        assert result["connected"] is False

    def test_get_api_version_nonexistent(self):
        """get_api_version should report session not found."""
        from mcp_server.session_manager import SessionManager

        mgr = SessionManager()
        result = mgr.get_api_version("nonexistent_id")
        assert result["success"] is False

    def test_path_helpers(self):
        """Path helper functions should be importable and return values."""
        from mcp_server.session_manager import (
            get_lumerical_api_path,
            get_lumerical_bin_path,
            get_lumerical_python_path,
            get_cml_compiler_path,
            get_intel_mpi_path,
        )
        # These should either return a valid path or raise/return None
        # At minimum, they should be callable without crashing
        try:
            api = get_lumerical_api_path()
            assert api is not None, "API path should be found with v261 installed"
        except RuntimeError:
            # Acceptable if no Lumerical installation is available
            pass

    def test_path_discovery_v261_primary(self):
        """v261 ANSYS Inc path should be discovered or old paths as fallback."""
        from mcp_server.session_manager import _find_lumerical_api
        from pathlib import Path

        path = _find_lumerical_api()
        if path:
            # If found, verify it points to a valid directory
            assert Path(path).exists()
            # With v261 installed, should find the ANSYS Inc path
            assert "v261" in path or "Lumerical" in path


class TestCommandDocs:
    """Test documentation system."""

    def test_load_docs(self):
        """Docs should load without errors."""
        from mcp_server.command_docs import CommandDocs

        docs = CommandDocs()
        docs.load()
        # Should have loaded docs.json from the Lumerical installation
        # Or at least be functional with empty commands

    def test_get_command_help_unknown(self):
        """Getting help for unknown command should return error."""
        from mcp_server.command_docs import CommandDocs

        docs = CommandDocs()
        result = docs.get_command_help("nonexistent_command_xyz")
        assert result.get("success") is False

    def test_search_commands(self):
        """Search should work."""
        from mcp_server.command_docs import CommandDocs

        docs = CommandDocs()
        result = docs.search_commands("fdtd")
        assert result.get("success") is True
        assert "query" in result
        assert "count" in result

    def test_get_categories(self):
        """Categories should be returned."""
        from mcp_server.command_docs import CommandDocs

        docs = CommandDocs()
        result = docs.get_commands_by_category()
        assert result.get("success") is True
        assert "categories" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
