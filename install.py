#!/usr/bin/env python
"""Installation script for Lumerical MCP Server and Skill.

Installs the MCP server configuration in Claude Code and copies the Skill
to the appropriate directory for Claude Code to discover.

Usage:
    python install.py [--mcp-only] [--skill-only] [--check]

Options:
    --mcp-only    Only install the MCP server configuration
    --skill-only  Only install the Skill
    --check       Check if Lumerical is properly installed and accessible
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


def check_lumerical() -> dict:
    """Check if Lumerical is properly installed and accessible."""
    api_path = os.environ.get("LUMERICAL_HOME", "")
    if not api_path:
        candidates = [
            r"D:\ENV\Lumerical\v202",
            r"C:\Program Files\Lumerical\v202",
            r"C:\Program Files\Lumerical\v221",
            r"C:\Program Files\Lumerical\v222",
            r"C:\Program Files\Lumerical\v231",
        ]
        for c in candidates:
            if Path(c).exists():
                api_path = c
                break

    results = {"lumerical_found": False, "api_path": api_path, "products": []}

    if api_path:
        api_python = Path(api_path) / "api" / "python"
        if api_python.exists():
            results["lumerical_found"] = True
            results["api_path"] = str(api_python)

            # Check for lumapi.py
            lumapi = api_python / "lumapi.py"
            results["lumapi_found"] = lumapi.exists()

            # Check for docs.json
            docs = api_python / "docs.json"
            results["docs_found"] = docs.exists()

            # Check for product executables
            bin_dir = Path(api_path) / "bin"
            products = {
                "fdtd": "fdtd-engine.exe",
                "mode": "mode-engine.exe",
                "device": "device-engine.exe",
            }
            for prod, exe in products.items():
                if (bin_dir / exe).exists():
                    results["products"].append(prod)

    return results


def install_mcp(project_dir: Path) -> dict:
    """Install MCP server configuration for Claude Code."""
    claude_config_path = Path.home() / ".claude"
    mcp_config_file = claude_config_path / "mcp.json"

    claude_config_path.mkdir(parents=True, exist_ok=True)

    # Read existing config or create new
    config = {}
    if mcp_config_file.exists():
        try:
            with open(mcp_config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError:
            config = {}

    # Ensure mcpServers key exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Add Lumerical MCP configuration
    server_dir = project_dir / "mcp_server"
    config["mcpServers"]["lumerical"] = {
        "command": sys.executable,
        "args": ["-m", "mcp_server.server"],
        "cwd": str(project_dir),
        "description": (
            "Lumerical MCP Server - FDTD, MODE, DEVICE, INTERCONNECT "
            "photonic simulation tools"
        ),
    }

    with open(mcp_config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    return {"success": True, "config_file": str(mcp_config_file)}


def install_skill(project_dir: Path) -> dict:
    """Install the Skill for Claude Code."""
    skill_src = project_dir / "skill" / "lumerical.md"
    skill_dest = Path.home() / ".claude" / "skills" / "lumerical.md"

    skill_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(skill_src, skill_dest)

    return {"success": True, "skill_file": str(skill_dest)}


def main():
    parser = argparse.ArgumentParser(
        description="Install Lumerical MCP Server and Skill for Claude Code"
    )
    parser.add_argument("--mcp-only", action="store_true", help="Only install MCP config")
    parser.add_argument("--skill-only", action="store_true", help="Only install Skill")
    parser.add_argument("--check", action="store_true", help="Check Lumerical installation")
    args = parser.parse_args()

    project_dir = Path(__file__).parent.resolve()

    print("=" * 60)
    print("  Lumerical MCP Server & Skill - Installation")
    print("=" * 60)
    print()

    # Check
    if args.check or (not args.mcp_only and not args.skill_only):
        print("[Check] Verifying Lumerical installation...")
        check = check_lumerical()
        if check["lumerical_found"]:
            print(f"  [OK] Lumerical found at: {check['api_path']}")
            print(f"  [OK] lumapi.py: {'Found' if check['lumapi_found'] else 'Missing!'}")
            print(f"  [OK] docs.json: {'Found' if check['docs_found'] else 'Missing!'}")
            if check["products"]:
                print(f"  [OK] Products: {', '.join(check['products'])}")
        else:
            print("  [WARNING] Lumerical not auto-detected.")
            print("    Set LUMERICAL_HOME environment variable pointing to your Lumerical installation.")
            print("    Example: set LUMERICAL_HOME=D:\\ENV\\Lumerical\\v202")
        print()

    if args.check:
        return

    # Install MCP
    if not args.skill_only:
        print("[Install] Configuring MCP server...")
        result = install_mcp(project_dir)
        if result["success"]:
            print(f"  [OK] MCP config written to: {result['config_file']}")
            print("  [OK] Restart Claude Code to load the MCP server.")
        else:
            print(f"  [ERROR] Failed: {result.get('error', 'Unknown error')}")
        print()

    # Install Skill
    if not args.mcp_only:
        print("[Install] Installing Skill...")
        result = install_skill(project_dir)
        if result["success"]:
            print(f"  [OK] Skill installed to: {result['skill_file']}")
            print("  [OK] Use /lumerical in Claude Code to invoke the skill.")
        else:
            print(f"  [ERROR] Failed: {result.get('error', 'Unknown error')}")
        print()

    print("Installation complete!")
    print()
    print("Next steps:")
    print("  1. Make sure LUMERICAL_HOME is set correctly.")
    print("  2. Restart Claude Code.")
    print("  3. Use /lumerical to start using the Skill.")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
