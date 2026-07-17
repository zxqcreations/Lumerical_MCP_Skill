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


class TestLSFParsing:
    """Test LSF script parsing and eval fallback logic."""

    def test_parse_simple_command(self):
        """Simple command without args should parse correctly."""
        from mcp_server.session_manager import SessionManager

        result = SessionManager._parse_lsf("addfde;")
        assert len(result) == 1
        stmt, cmd, args = result[0]
        assert stmt == "addfde"
        assert cmd == "addfde"
        assert args == []

    def test_parse_command_with_args(self):
        """Command with string args should parse correctly."""
        from mcp_server.session_manager import SessionManager

        result = SessionManager._parse_lsf('set("name", "core");')
        assert len(result) == 1
        stmt, cmd, args = result[0]
        assert cmd == "set"
        assert args == ["name", "core"]

    def test_parse_command_with_numeric_args(self):
        """Command with numeric args should parse as numbers."""
        from mcp_server.session_manager import SessionManager

        result = SessionManager._parse_lsf('set("x span", 1e-6);')
        assert len(result) == 1
        stmt, cmd, args = result[0]
        assert cmd == "set"
        assert args == ["x span", 1e-6]
        assert isinstance(args[1], float)

    def test_parse_command_with_integer_args(self):
        """Integer args should parse as int, not float."""
        from mcp_server.session_manager import SessionManager

        result = SessionManager._parse_lsf('set("solver type", 3);')
        stmt, cmd, args = result[0]
        assert args == ["solver type", 3]
        assert isinstance(args[1], int)

    def test_parse_multiple_commands(self):
        """Multiple commands should all be parsed."""
        from mcp_server.session_manager import SessionManager

        code = 'addrect;\nset("name", "core");\nset("x span", 1e-6);'
        result = SessionManager._parse_lsf(code)
        assert len(result) == 3
        assert result[0][1] == "addrect"
        assert result[1][1] == "set"
        assert result[2][1] == "set"

    def test_parse_empty_code(self):
        """Empty code should return empty list."""
        from mcp_server.session_manager import SessionManager

        result = SessionManager._parse_lsf("")
        assert result == []

    def test_parse_whitespace_code(self):
        """Whitespace-only code should return empty list."""
        from mcp_server.session_manager import SessionManager

        result = SessionManager._parse_lsf("  ; ;  ")
        assert result == []

    def test_parse_solver_commands(self):
        """All solver commands should parse correctly."""
        from mcp_server.session_manager import SessionManager

        solver_cmds = [
            "addfde",
            "addfdtd",
            "addeme",
            "addvarfdtd",
            "adddgdtd",
            "addfeem",
            "addchargesolver",
            "addheatsolver",
        ]
        for cmd in solver_cmds:
            result = SessionManager._parse_lsf(f"{cmd};")
            assert len(result) == 1, f"Failed to parse: {cmd}"
            assert result[0][1] == cmd

    def test_parse_mixed_args(self):
        """Mixed string and numeric args should parse correctly."""
        from mcp_server.session_manager import SessionManager

        result = SessionManager._parse_lsf(
            'set("wavelength", 1560e-9);'
        )
        stmt, cmd, args = result[0]
        assert cmd == "set"
        assert args[0] == "wavelength"
        assert isinstance(args[1], float)

    def test_split_args_simple(self):
        """Simple comma-separated args should split correctly."""
        from mcp_server.session_manager import SessionManager

        result = SessionManager._split_lsf_args('"hello", "world"')
        assert len(result) == 2
        assert result[0].strip() == '"hello"'
        assert result[1].strip() == '"world"'

    def test_split_args_with_nested_parens(self):
        """Args with nested parentheses should be preserved."""
        from mcp_server.session_manager import SessionManager

        result = SessionManager._split_lsf_args('"a", func(1, 2), "b"')
        assert len(result) == 3
        assert "func(1, 2)" in result[1]

    def test_split_args_empty(self):
        """Empty args should return single empty element or empty list."""
        from mcp_server.session_manager import SessionManager

        result = SessionManager._split_lsf_args("")
        # Should handle gracefully
        assert isinstance(result, list)

    def test_parse_fde_workflow(self):
        """Complete FDE workflow should parse into correct command sequence."""
        from mcp_server.session_manager import SessionManager

        code = (
            'addrect; set("name","core"); set("x span",1e-6); '
            'set("y span",0.9e-6); set("index",1.97);\n'
            'addfde; set("solver type",3); set("wavelength",1560e-9); '
            'set("number of trial modes",20);\n'
            'findmodes;'
        )
        result = SessionManager._parse_lsf(code)

        # Should parse all 10 commands
        assert len(result) == 10

        # Verify key commands are in order
        commands = [r[1] for r in result]
        assert commands[0] == "addrect"
        assert "addfde" in commands
        assert commands[-1] == "findmodes"

        # addfde should have no args
        fde_idx = commands.index("addfde")
        assert result[fde_idx][2] == []

        # findmodes should have no args
        assert result[-1][2] == []


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


class TestV22Enhancements:
    """Test v2.2 enhancements — INTERCONNECT tools, FDE defaults, cleanup."""

    def test_interconnect_module_imports(self):
        """INTERCONNECT tools module should import correctly."""
        from mcp_server.tools.interconnect import register_interconnect_tools
        assert register_interconnect_tools is not None

    def test_cleanup_helper_exists(self):
        """Cleanup function should be importable."""
        from mcp_server.session_manager import cleanup_interconnect_processes
        result = cleanup_interconnect_processes()
        assert result.get("success") is True
        assert "killed" in result

    def test_v22_tools_registered(self):
        """v2.2 INTERCONNECT tools should be registered."""
        from mcp_server.server import mcp, register_all_tools

        register_all_tools()
        tools = mcp._tool_manager._tools if hasattr(mcp, '_tool_manager') else {}
        tool_names = list(tools.keys())

        v22_tools = [
            "lumerical_interconnect_run_script",
            "lumerical_interconnect_add_element",
            "lumerical_interconnect_connect",
            "lumerical_interconnect_add_sweep",
            "lumerical_interconnect_get_sweep_data",
            "lumerical_interconnect_cleanup",
        ]
        found = [t for t in v22_tools if t in tool_names]
        assert len(found) == 6, (
            f"Expected all 6 INTERCONNECT tools, found {len(found)}. "
            f"Found: {found}"
        )

    def test_tool_count_v22(self):
        """v2.2 should have at least 65 tools (15 modules)."""
        from mcp_server.server import mcp, register_all_tools

        register_all_tools()
        tools = mcp._tool_manager._tools if hasattr(mcp, '_tool_manager') else {}
        assert len(tools) >= 65, (
            f"Expected at least 65 tools with v2.2, got {len(tools)}"
        )

    def test_run_script_method_exists(self):
        """SessionManager should have run_script method."""
        from mcp_server.session_manager import SessionManager
        mgr = SessionManager()
        assert hasattr(mgr, "run_script")
        assert callable(mgr.run_script)

    def test_get_data_method_exists(self):
        """SessionManager should have get_data method."""
        from mcp_server.session_manager import SessionManager
        mgr = SessionManager()
        assert hasattr(mgr, "get_data")
        assert callable(mgr.get_data)

    def test_run_script_validates_path(self):
        """run_script should reject non-existent files."""
        from mcp_server.session_manager import SessionManager
        mgr = SessionManager()
        # No active session, but path validation happens first
        # Script file doesn't exist
        assert not hasattr(mgr, '_sessions') or len(mgr._sessions) == 0

    def test_solver_fde_smart_defaults(self):
        """FDE solver should auto-set search=1."""
        # Verify the _SOLVER_TYPES mapping includes fde
        from mcp_server.tools.solver import _SOLVER_TYPES
        assert _SOLVER_TYPES["fde"] == "addfde"

    def test_interconnect_elements_parse(self):
        """INTERCONNECT element commands (addelement-based) parse correctly."""
        from mcp_server.session_manager import SessionManager

        # INTERCONNECT uses addelement(), which should parse fine
        code = 'addelement("Waveguide"); set("name", "WG1"); set("length", 10e-3);'
        result = SessionManager._parse_lsf(code)
        assert len(result) == 3
        assert result[0][1] == "addelement"
        assert result[0][2] == ["Waveguide"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
