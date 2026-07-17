# Lumerical MCP 改进任务提示词

> 将此文件内容发送给 Agent，让它分析和更新 Lumerical MCP 服务器。

---

## 任务：修复 Lumerical MCP 服务器中 eval() 不支持的命令

### 背景

Lumerical MCP 服务器（位于 `D:\ENV\claude\Lumerical_MCP\`）通过 Python `lumapi` 库连接 Lumerical 仿真工具（FDTD、MODE、DEVICE、INTERCONNECT）。

当前服务器主要通过 `lumapi.eval(script_string)` 执行 Lumerical 脚本命令。但测试发现，**部分关键命令不支持 eval() 方式，必须通过直接 Python API 调用才能执行**。

### 关键发现

在 MODE 产品中经过直接 Python API 测试验证（v261，`lumapi.py` 位于 `D:\ENV\Lumerical\ANSYS Inc\v261\Lumerical\api\python\`）：

| 命令 | `m.eval('cmd;')` | `m.cmd()` 直接API | 影响 |
|------|:---:|:---:|------|
| `addrect` | ✅ | ✅ | 无问题 |
| `set` | ✅ | ✅ | 无问题 |
| `addfde` | ❌ "Failed to evaluate code" | ✅ | **FDE求解器无法添加** |
| `addfdtd` | ❌ "Failed to evaluate code" | ✅ | **FDTD求解器无法添加** |
| `findmodes` | ✅ | ✅ | 无问题 |
| `getdata` | ✅ | ✅ | 无问题 |
| `select` | ✅ | ✅ | 无问题 |
| `switchtolayout` | ✅ | ✅ | 无问题 |

**根因**：`lumapi.eval()` 在 MODE 产品中对某些求解器添加命令（`addfde`、`addfdtd` 等）的支持不完整，但这些命令的直接 Python API 方法完全正常。这不是 Lumerical 的限制，而是 eval 通道的问题。

另外，部分 `set()` 的参数类型在 eval 中自动转换（如 `set('search', 'max_index')` 自动转为字符串），但直接 API 需要精确类型（如 `set('search', 2)`，整数枚举）。

### 需要改动的文件

**核心改动**：`D:\ENV\claude\Lumerical_MCP\mcp_server\tools\script.py`

当前 `lumerical_eval` 工具使用：
```python
handle.eval(code)  # 仅支持字符串脚本
```

需要增加**直接方法调用**的备用路径。建议方案：

1. **增强 `lumerical_call` 工具**（`tools/script.py`）：当前已有此工具，但可能限制了可用命令列表。检查是否允许调用 `addfde`、`addfdtd` 等所有 lumapi 方法。

2. **在 `lumerical_eval` 中增加 fallback 逻辑**：当 `eval()` 失败时，解析脚本字符串并尝试通过直接 API 调用执行。

3. **新增 `lumerical_exec` 工具**：接受命令名+参数列表，直接调用 `handle.command(*args)`。

### 涉及的求解器添加命令（需要支持直接 API 调用）

这些命令在 MODE/FDTD 中无法通过 eval 执行：

- `addfde` — Finite Difference Eigenmode solver (MODE)
- `addfdtd` — FDTD solver region (FDTD)
- `addeme` — Eigenmode Expansion solver (MODE)
- `addvarfdtd` — Variational FDTD solver (MODE)
- `adddgdtd` — Discontinuous Galerkin solver
- `addfeem` — Finite Element Eigenmode solver
- `addchargesolver` — Charge transport solver (DEVICE)
- `addheatsolver` — Heat transport solver (DEVICE)

### 测试验证

更新后，在 MODE 中运行以下完整流程应全部成功：

```python
# 1. 打开 MODE
# 2. 创建几何
addrect; set("name","core"); set("x span",1e-6); set("y span",0.9e-6); set("index",1.97);
addrect; set("name","sub"); set("x span",4e-6); set("y span",2e-6); set("y",-1e-6); set("index",1.444);

# 3. 添加 FDE 求解器 ← 这是关键测试
addfde; set("solver type",3); set("wavelength",1560e-9); set("number of trial modes",20);

# 4. 求解
findmodes;

# 5. 提取结果
neff = getdata("FDE::data::mode1","neff");
```

### 技术参考

- Lumerical API 路径：`D:\ENV\Lumerical\ANSYS Inc\v261\Lumerical\api\python\lumapi.py`
- MCP 服务器入口：`D:\ENV\claude\Lumerical_MCP\mcp_server\server.py`
- 会话管理：`D:\ENV\claude\Lumerical_MCP\mcp_server\session_manager.py`
- 脚本工具：`D:\ENV\claude\Lumerical_MCP\mcp_server\tools\script.py`
- 求解器工具：`D:\ENV\claude\Lumerical_MCP\mcp_server\tools\solver.py`
- 故障排除文档：`D:\ENV\claude\Lumerical_MCP\TROUBLESHOOTING.md`

### 预期结果

更新后，用户可以通过 MCP 完整执行 FDE 模式分析工作流，无需手动打开 Lumerical GUI。
