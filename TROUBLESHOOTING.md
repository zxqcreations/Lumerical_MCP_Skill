# Lumerical MCP 安装故障排除指南

> 最后更新: 2026-07-17
> 基于在 Er/Yb/Ce:LaAlO 脊形波导放大器项目中实际部署遇到的问题和解决方案

---

## 问题 1: Claude Code 无法连接 MCP 服务器 (错误 -32000)

### 症状
```json
Failed to reconnect to lumerical: -32000
```
尽管手动运行 `python -m mcp_server.server` 完全正常（10 个模块注册成功，MCP 握手机制正常）。

### 根因
**Lumerical MCP 包未通过 `pip install -e .` 安装到 Python site-packages。**

当从项目目录内手动运行 `python -m mcp_server.server` 时，Python 自动将当前目录加入 `sys.path`，因此能找到 `mcp_server` 包。但 Claude Code 通过进程生成启动服务器时，工作目录和 Python 路径解析方式不同，需要包已正式安装。

对比：COMSOL MCP 服务器早已通过 `pip install -e .` 安装（`pip show comsol-mcp` 可见），因此能正常工作。

### 解决方案

#### Step 1: 修复 pyproject.toml

原始 `pyproject.toml` 缺少两个关键配置段，导致 `pip install -e .` 失败：

**缺失的配置 1** — `[project.scripts]` 入口点：
```toml
[project.scripts]
lumerical-mcp = "mcp_server.server:main"
```

**缺失的配置 2** — `[tool.hatch.build.targets.wheel]` 构建目标：
```toml
[tool.hatch.build.targets.wheel]
packages = ["mcp_server"]
```

修复后的完整配置（在 `[build-system]` 段之后添加）：
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.scripts]
lumerical-mcp = "mcp_server.server:main"

[tool.hatch.build.targets.wheel]
packages = ["mcp_server"]
```

不加 `[tool.hatch.build.targets.wheel]` 时的构建错误：
```
ValueError: Unable to determine which files to ship inside the wheel
using the following heuristics...
The most likely cause of this is that there is no directory that matches
the name of your project (lumerical_mcp).
```

#### Step 2: 安装包
```bash
cd D:/ENV/claude/Lumerical_MCP
pip install -e .
```

验证安装：
```bash
pip show lumerical-mcp
# 应输出: Name: lumerical-mcp, Version: 1.0.0, ...
```

#### Step 3: 验证从任意目录可运行
```bash
cd /tmp
python -m mcp_server.server
# 应正常启动，注册 10 个工具模块
```

---

## 问题 2: Claude Code MCP 配置冲突

### 症状
安装完成后 `/mcp` 中仍然看不到 Lumerical，或连接失败。

### 根因
MCP 配置存在于多个层级：
- `~/.claude/mcp.json` — 用户级全局配置
- `~/.claude/.mcp.json` — 用户级（dotfile 格式，含 `type` 字段）
- `<project>/.mcp.json` — 项目级配置

如果多个文件定义了同名服务器，可能发生冲突。

### 解决方案

1. **清空用户级不必要的条目** — `~/.claude/mcp.json` 中只保留非项目特定的服务器
2. **在项目级 `.mcp.json` 中配置** — 使用与正常工作的 COMSOL MCP 相同的格式：

```json
{
  "mcpServers": {
    "lumerical": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "D:/ENV/claude/Lumerical_MCP"
    }
  }
}
```

3. **避免在 `command` 中使用完整 Windows 路径和反斜杠转义** — 使用简单的 `"python"`（前提是 Python 在 PATH 中），目录路径使用正斜杠。

4. **运行 `/reload-plugins`** 使配置生效。

---

## 问题 3: interopapi.dll 加载失败

### 症状
```
FileNotFoundError: Could not find module 'interopapi.dll' (or one of its dependencies).
Try using the full path with constructor syntax.
```

尽管 `interopapi.dll` 确实存在于 `D:/ENV/Lumerical/v202/api/python/interopapi.dll`。

### 根因
`lumapi.py` 第 41 行使用 `INTEROPLIB = "interopapi.dll"`（仅文件名，无路径）。Python ctypes 的 `CDLL("interopapi.dll")` 在 Windows 上的 DLL 搜索顺序与 Unix 不同，即使 `ENVIRONPATH` 包含了正确目录，`LoadLibrary` Win32 API 也可能找不到依赖的 Qt5 DLL。

### 解决方案

修改 `D:\ENV\Lumerical\v202\api\python\lumapi.py` 第 41 行，使用完整路径：

```python
# 修改前
INTEROPLIB = "interopapi.dll"

# 修改后
INTEROPLIB = INTEROPLIBDIR + "/interopapi.dll"
```

## 问题 4: MODE 产品中 addfde 命令失败

### 症状
在 MODE session 中执行 `addfde;` 及其变体均返回：
```
Script execution failed: 'Failed to evaluate code'
```

但 `addrect;`, `switchtolayout;`, `?"hello"` 等命令正常工作。

### 根因
Lumerical 2020 R2 的 Python API (`lumapi`) 在 MODE 产品中对 FDE solver 的添加命令存在兼容性问题。`addfde` 命令需要通过 Lumerical GUI 环境或 `.lsf` 脚本文件运行，而 Python interop API 无法正确执行该命令。

### 解决方案
使用 Lumerical MODE GUI 直接运行 `.lsf` 脚本文件（File → Run Script），或编写完整的脚本文件通过命令行加载：

```bash
# 在 Lumerical MODE GUI 中
File → Run Script → 选择 .lsf 文件
```

## 问题 5: 用户级与项目级配置重复

### 症状
Claude Code 加载时不确定使用哪个配置，导致连接不稳定。

### 解决方案
**只在项目级 `.mcp.json` 中保留 Lumerical 配置**，从用户级 `~/.claude/mcp.json` 中移除。

### 检查清单
```bash
# 检查用户级
cat ~/.claude/mcp.json
# 确保 "lumerical" 不在 mcpServers 中（或整个文件为空）

# 检查项目级
cat <project>/.mcp.json
# 确保 "lumerical" 在 mcpServers 中
```

---

## 部署检查清单

在新项目中使用 Lumerical MCP 时，按以下顺序操作：

- [ ] `pip install -e .` 已执行且成功
- [ ] `pip show lumerical-mcp` 可见
- [ ] `python -m mcp_server.server` 从任意目录可启动
- [ ] `pyproject.toml` 包含 `[project.scripts]` 和 `[tool.hatch.build.targets.wheel]`
- [ ] 项目 `.mcp.json` 中 Lumerical 条目格式正确
- [ ] 用户级 `mcp.json` 无冲突条目
- [ ] `/reload-plugins` 后 `/mcp` 中可见 Lumerical
- [ ] `lumerical_list_sessions` 返回 `{"success": true}`

---

## 技术摘要

| 问题 | 难度 | 修复文件 | 操作 |
|------|:--:|------|------|
| pip install 失败 | 🔴 | `pyproject.toml` | 添加 `[tool.hatch.build.targets.wheel]` |
| Claude Code 找不到服务 | 🔴 | `pyproject.toml` | `pip install -e .` |
| 多配置冲突 | 🟡 | `.mcp.json` + `mcp.json` | 去重，仅保留项目级 |
| Windows 路径转义 | 🟢 | `.mcp.json` | 用 `"python"` 代替完整路径 |
