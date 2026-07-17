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

## 问题 4: MODE 产品中 addfde/addfdtd 等求解器命令失败 (已修复 ✅)

### 症状
在 MODE session 中通过 `lumerical_eval` 执行 `addfde;` / `addfdtd;` 等命令返回：
```
Script execution failed: 'Failed to evaluate code'
```

但 `addrect;`, `switchtolayout;`, `set(...)` 等命令正常工作。

### 根因
`lumapi.eval()` 在 MODE 产品中对某些求解器添加命令（`addfde`、`addfdtd`、`addeme` 等）的支持不完整。这些命令通过 eval 通道执行会失败，但通过直接 Python API 调用（`handle.addfde()`）完全正常。这不是 Lumerical 本身的限制，而是 eval 通道的问题。

### 解决方案 (v2.1 已修复)

MCP 服务器 v2.1+ 在 `session_manager.py` 中实现了 **eval() 自动 fallback 机制**：

1. 首先尝试 `lumapi.eval(code)` 执行脚本
2. 如果 eval 失败，自动将脚本解析为独立命令，通过直接 Python API (`getattr(handle, command)(*args)`) 逐个执行
3. 返回每个命令的执行结果，标注 `"method": "direct_api_fallback"`

**受影响的命令**（现在全部通过 fallback 支持）：
- `addfde` — Finite Difference Eigenmode solver (MODE)
- `addfdtd` — FDTD solver region (FDTD)
- `addeme` — Eigenmode Expansion solver (MODE)
- `addvarfdtd` — Variational FDTD solver (MODE)
- `adddgdtd` — Discontinuous Galerkin solver
- `addfeem` — Finite Element Eigenmode solver
- `addchargesolver` — Charge transport solver (DEVICE)
- `addheatsolver` — Heat transport solver (DEVICE)

**备选方案**：使用 `lumerical_call` 工具直接调用命令（绕过 eval 通道）：
```json
{"session_id": "lum_1", "command": "addfde", "args": "[]"}
{"session_id": "lum_1", "command": "set", "args": "[\"solver type\", 3]"}
```

### 验证
在 MODE 中运行以下完整流程应全部成功：
```python
# 1. lumerical_eval: 创建几何
addrect; set("name","core"); set("x span",1e-6); set("y span",0.9e-6); set("index",1.97);
addrect; set("name","sub"); set("x span",4e-6); set("y span",2e-6); set("y",-1e-6); set("index",1.444);

# 2. lumerical_eval: 添加 FDE 求解器 ← 自动 fallback 到直接 API
addfde; set("solver type",3); set("wavelength",1560e-9); set("number of trial modes",20);

# 3. lumerical_eval: 求解并提取结果
findmodes;
neff = getdata("FDE::data::mode1","neff");
```

## 问题 6: FDE 求解器关键参数设置 (search + solver region)

### 症状
FDE 只找到泄漏模 (n_eff < n_clad) 或 Gamma 值严重偏离 COMSOL/理论值。

### 根因 (2026-07-18 通过系统排查确认)

**根因 A**: `search=2` (max_index) 在 MODE v261 中行为异常。该搜索方法在 waveguide 结构中不能正确找到导模，返回泄漏模 (n_eff=1.2955 < n_clad=1.444)。应使用 `search=1` (near_n)。

**根因 B**: FDE 求解器默认自动裁剪计算窗口。对于位置不在 y=0 中心的芯层（如 y=[0, 0.9]μm），默认窗口 y=[-0.85, +0.85]μm 会切掉芯层顶部 0.05μm，导致 Γ 偏高 ~14% (0.94 vs 0.83)。

### 解决方案

**1. 始终使用 `search=1` (near_n)**:
```python
m.set('search', 1)  # near_n — 正确找到导模
# 不要使用 m.set('search', 2)  # max_index — v261 中有 bug
```

**2. 显式设置 FDE 求解器区域**:
```python
m.addfde()
m.set('solver type', 3)
m.set('wavelength', 1560e-9)
m.set('number of trial modes', 30)
m.set('search', 1)          # ← 关键: near_n
m.set('y', 0.45e-6)         # ← 关键: 芯层 y 中心
m.set('y span', 2.0e-6)     # ← 关键: 足够覆盖芯层+包层
m.set('x', 0)               # ← 关键: 芯层 x 中心
m.set('x span', 2.5e-6)     # ← 关键: 足够覆盖芯层+包层
```

**3. 信号/泵浦用独立会话**: `findmodes()` 后进入 analysis mode，无法修改材料折射率。分别开两个 MODE 会话求解信号和泵浦波长。

### 验证结果 (2026-07-18)

修复后 Lumerical MODE FDE 与 COMSOL Phase 2 交叉验证：

| 参数 | Lumerical | COMSOL P2 | 偏差 |
|------|:---:|:---:|:---:|
| n_eff,s | 1.7267 | 1.7264 | 0.02% |
| Γ_s | 0.8286 | 0.8251 | 0.42% |
| n_eff,p | 1.8935 | 1.8934 | 0.01% |
| Γ_p | 0.9564 | 0.9598 | 0.36% |

**结论: COMSOL Phase 2 结果被独立仿真工具验证，所有参数偏差 <0.5%。**

## 问题 5: 许可证服务器连接失败 (v261)

### 症状
```
Could not connect to Ansys license server specified at 
1055@D:\ENV\ANSYS Inc\Shared Files\Licensing\license_files\ansyslmd.lic
```

许可证服务器在 `localhost:1055` 正常运行，但 Lumerical 无法连接。

### 根因
`%APPDATA%\Lumerical\License.ini` 中的 `ansysserver\host` 键指向了错误格式的路径：
```ini
ansysserver\host=1055@D:\\ENV\\ANSYS Inc\\Shared Files\\Licensing\\license_files\\ansyslmd.lic
```

这是 `port@host` 和文件路径的混合体，FlexNet 无法正确解析。应为 `1055@localhost`。

### 解决方案
编辑 `%APPDATA%\Lumerical\License.ini`：
```ini
[license]
default=user
domain=0
type=flex
flexserver\host=27011@localhost
ansysserver\host=1055@localhost    # ← 修复此行
```

### 验证
```bash
python -c "import lumapi; m=lumapi.MODE(hide=True); print('OK'); m.close()"
```

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

## 问题 7: INTERCONNECT — eval 不支持且无直接 API fallback

### 症状
`lumerical_eval('addwaveguide;')` 和 `lumerical_eval('addopticalamplifier;')` 均返回 "Failed to evaluate code"。

### 根因
INTERCONNECT 的 Python API 与 MODE/FDTD 不同：
- 没有 `addwaveguide()`、`addopticalamplifier()` 等直接方法
- 只有通用的 `addelement()` 方法（需指定元素类型字符串）
- eval 通道同样不支持这些命令

**与 MODE 的关键区别**：MODE 的 `addfde()` 有直接 Python API 方法可 fallback；INTERCONNECT 没有。

### 解决方案
使用 `lumapi.INTERCONNECT.run('script.lsf')` 执行完整 LSF 脚本文件：

```python
m = lumapi.INTERCONNECT(hide=True)
m.run('path/to/circuit_setup.lsf')
```

**注意事项**：
1. LSF 脚本中的 `newproject; switchtolayout;` 确保干净启动
2. 脚本运行后 INTERCONNECT 进入分析模式，下次 `run()` 需先 `switchtodesign`
3. 旧的 INTERCONNECT 进程可能残留，需 `taskkill /F /IM INTERCONNECT.exe`
4. 光学放大器等元件的参数设置需在 GUI 中确认属性名

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
