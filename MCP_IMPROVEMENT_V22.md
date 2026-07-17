# Lumerical MCP v2.2 改进规范

> 基于 Phase 4 (COMSOL+Lumerical 联合仿真) 的系统性测试发现
> 日期: 2026-07-18
> 测试版本: Lumerical v261 (ANSYS Inc), MCP v2.1

---

## 一、发现概述

在完整的 MODE / INTERCONNECT / FDTD 联合仿真工作流中，发现 MCP 存在三个层面的改进空间：

| 层面 | 影响范围 | 优先级 |
|------|------|:--:|
| eval fallback 不完整 | MODE 部分命令, INTERCONNECT 全部 | 🔴 高 |
| 产品间 API 差异未适配 | INTERCONNECT vs MODE vs FDTD | 🔴 高 |
| 求解器配置知识缺失 | FDE 参数错误导致错误结果 | 🟡 中 |

---

## 二、改进项详细说明

### 2.1 扩展 eval fallback 命令列表

**现状**: v2.1 的 eval fallback 已支持 `addfde`, `addfdtd` 等求解器命令，但以下命令仍失败：

**MODE 产品**:
```
addeme          — EME solver
addvarfdtd      — VarFDTD solver  
adddgdtd        — DGTD solver
addfeem         — FEEM solver
```

**INTERCONNECT 产品** (全部 eval 不支持，且无直接 API):
```
addwaveguide
addcwlaser
addopticalamplifier
addpoweranalyzer
addosnranalyzer
addwdm
connect
addsweep
addsweepparameter
addsweepresult
runsweep
getsweepdata
```

**FDTD 产品**:
```
addmovie
addimportedsource
adddgtcsolver
```

### 2.2 INTERCONNECT 独立方案: `run()` 脚本执行

**问题**: INTERCONNECT Python API 没有元素级直接方法 (如 `addwaveguide()`)。`addelement()` 是通用方法，需要特定参数。

**建议方案**: 为 INTERCONNECT 增加 `lumerical_run_script` 工具，使用 `handle.run(script_path)` 执行完整 LSF 脚本：

```python
# 新工具: lumerical_run_script
def run_script(session_id: str, script_path: str) -> dict:
    """Execute a .lsf script file in the session."""
    info = _get_session(session_id)
    try:
        info.handle.run(script_path)
        return {"success": True}
    except LumApiError as e:
        if "Analysis Mode" in str(e):
            # Script ran successfully — it just ended in analysis mode
            return {"success": True, "note": "Script completed (ended in analysis mode)"}
        return {"success": False, "error": str(e)}
```

**前置条件**: INTERCONNECT 进程残留需自动清理：
```python
import subprocess, os
if os.name == 'nt':
    subprocess.run(['taskkill', '/F', '/IM', 'INTERCONNECT.exe'], 
                   capture_output=True)
```

### 2.3 FDE 求解器最佳实践 — 自动应用

**问题**: Phase 4 发现 FDE 求解器的正确配置需要三个关键设置，缺少任一个都会导致错误结果。用户不应需要知道这些细节。

**发现 1: `search=1` (near_n) 必须使用**

`search=2` (max_index) 在 v261 MODE 中有 bug，产生泄漏模 (n_eff < n_clad) 而非导模。

**发现 2: 求解器区域必须显式设置**

FDE 默认自动裁剪窗口可能切掉芯层。需根据波导几何自动计算合理区域。

**发现 3: 信号/泵浦需独立会话**

`findmodes()` 后进入分析模式，无法在同一会话中修改材料折射率。

**建议方案**: 在 `lumerical_add_solver` 工具中增加智能默认值：

```python
def add_fde_solver(session_id, wavelength, core_y_center=None, core_span=None):
    """Smart FDE solver setup with validated defaults."""
    
    # 1. Always use search=1 (near_n) — search=2 is buggy in v261
    props = {
        "solver type": 3,
        "wavelength": wavelength,
        "number of trial modes": 30,
        "search": 1,          # ← CRITICAL: near_n, not max_index
    }
    
    # 2. Auto-compute solver region if geometry info available
    if core_y_center and core_span:
        margin = max(core_span * 0.8, 0.5e-6)
        props["y"] = core_y_center
        props["y span"] = core_span + 2 * margin
        props["x"] = 0
        props["x span"] = core_span + 2 * margin
    
    # 3. Warn if user will need separate sessions for multi-wavelength
    ...
```

### 2.4 `lumapi.getv()` 封装

**问题**: 用户脚本中 `x = getdata(...)` 结果无法通过 MCP 直接获取。`lumerical_get_var` 需要脚本预先执行 `x = ...` 赋值。

**建议方案**: 增加 `lumerical_get_data` 工具的直接调用路径，封装 `handle.getdata()`:

```python
def get_data(session_id, dataset, attribute):
    """Direct getdata call — bypasses eval entirely."""
    info = _get_session(session_id)
    result = info.handle.getdata(dataset, attribute)
    return {"success": True, "data": _to_serializable(result)}
```

### 2.5 工作目录管理

**问题**: `fopen("results.txt")` 保存的文件位置不确定（取决于 INTERCONNECT 进程工作目录）。

**建议方案**: 在每个 session 打开时设置工作目录到项目路径。

---

## 三、改进优先级与工作量估计

| # | 改进项 | 文件 | 工作量 | 优先级 |
|---|------|------|:--:|:--:|
| 2.1 | 扩展 eval fallback 列表 | `tools/script.py` | 15 min | 🔴 |
| 2.2 | INTERCONNECT `run()` 工具 | 新工具 `tools/interconnect.py` | 30 min | 🔴 |
| 2.3 | FDE 智能默认值 | `tools/solver.py` | 20 min | 🟡 |
| 2.4 | `getdata` 直接封装 | `tools/results.py` | 15 min | 🟡 |
| 2.5 | 工作目录管理 | `session_manager.py` | 10 min | 🟢 |

---

## 四、测试用例

改进后，以下完整工作流应在所有产品中通过：

### MODE FDE 工作流
```
1. lumerical_open("mode")
2. lumerical_eval("geometry setup script")
3. lumerical_add_solver("fde", {wavelength: 1560e-9})  ← 自动 search=1 + 区域
4. lumerical_eval("findmodes;")
5. lumerical_get_data("FDE::data::mode1", "neff")       ← 新工具
6. lumerical_get_data("FDE::data::mode1", "x")           ← 新工具
```

### INTERCONNECT 工作流
```
1. lumerical_open("interconnect")
2. lumerical_run_script("circuit_setup.lsf")              ← 新工具
3. lumerical_get_data("Pump Power Sweep", "Output Power") ← 新工具
```

---

## 五、已记录的完整问题清单

详见 `TROUBLESHOOTING.md`，包含 7 个已解决问题：
1. MCP 无法启动 (`pip install -e .`)
2. 多配置冲突
3. `interopapi.dll` 路径 (v202)
4. eval fallback for solver commands (v2.1 已修复)
5. License.ini (`ansysserver\host`)
6. FDE 关键参数 (search=1, solver region, separate sessions)
7. INTERCONNECT eval + API 限制
