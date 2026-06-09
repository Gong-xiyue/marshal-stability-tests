# Marshal 模块稳定性测试项目

本项目旨在研究 Python `marshal` 模块的稳定性和正确性，验证相同输入是否总是产生相同的（hash-identical）序列化输出。

## 研究问题

> 相同的输入是否总是产生相同的（序列化）输出？

我们定义"相同的输入和输出"为 **hash-identical**（逻辑等价是不够的）。这意味着输入必须在所有情况下都产生相同的 marshal 字节流。

## 团队分工

| 成员 | 负责模块 | 测试文件 | 测试理论 |
|------|----------|----------|----------|
| **成员 A** | 基础类型 & 边界值 | `test_basic_types.py`、`test_boundaries.py` | 等价类划分、边界值分析、重复性稳定性测试 |
| **成员 B** | 浮点 & 集合顺序 | `test_float_specials.py`、`test_collections.py`、`test_cross_process.py`、`scripts/run_hashseed_case.py` | 特殊值测试、跨进程/随机化测试 |
| **成员 C** | 递归 & 代码对象 | `test_recursive.py`、`test_code_objects.py` | 鲁棒性测试、白盒/实现知识启发 |
| **成员 D** | Fuzzing & 自动化 & 报告整合 | `test_fuzzing.py`、`scripts/run_matrix.py`、`docs/final_report_draft.md`、`docs/traceability_matrix.md` | Fuzzing/属性基测试、环境矩阵/跨平台测试 |

## 测试维度（13项）

| 编号 | 测试维度 | 测试技术 | 状态 |
|------|----------|----------|------|
| 1 | 基本类型确定性（None, bool, int, float, complex, str, bytes, bytearray） | 等价类划分 | ✅ |
| 2 | 空/大容器边界值分析（empty collections, boundary collection sizes） | 边界值分析 | ✅ |
| 3 | 递归容器（self-referential containers） | 鲁棒性测试 | ✅ |
| 4 | 共享引用（shared references） | 白盒引用处理 | ✅ |
| 5 | 特殊浮点数（NaN, Infinity, -0.0） | 特殊值测试 | ✅ |
| 6 | 不支持输入类型（unsupported types raise exception） | 负测试 | ✅ |
| 7 | 随机嵌套结构模糊测试（random fuzzed structures） | Fuzzing | ✅ |
| 8 | 跨解释器运行脚本 | 环境矩阵测试 | ✅ |
| 9 | 跨版本探测（Python 3.9/3.11/3.12） | 跨版本测试 | ✅ |
| 10 | 跨平台测试（Kali Linux vs Windows PowerShell） | 跨平台测试 | ✅ |
| 11 | bytearray 与 bytes 的类型标识差异 | 类型比较测试 | ✅ |
| 12 | 跨版本反序列化测试 | 兼容性测试 | ✅ |
| 13 | 跨平台同一 Python 版本哈希差异 | 跨平台对比 | ✅ |

## 项目结构

```text
marshal-stability-tests/
├── src/marshal_stability/      # 工具函数库
│   ├── __init__.py
│   ├── comparators.py          # 等价比较器（处理NaN等特殊情况）
│   ├── generators.py           # Hypothesis测试数据生成器
│   ├── hash_utils.py           # Hash工具函数
│   └── cases.py                # 测试用例数据
├── tests/                      # 测试文件目录
│   ├── test_basic_types.py     # 基础类型测试（等价类划分）
│   ├── test_boundaries.py      # 边界值测试（整数/容器/字符串边界）
│   ├── test_float_specials.py  # 浮点特殊值测试（NaN、Inf、-0.0等）
│   ├── test_collections.py     # 集合测试（dict/set/frozenset）
│   ├── test_recursive.py       # 递归结构测试（循环引用、深度嵌套）
│   ├── test_code_objects.py    # 代码对象测试（函数/Lambda/方法）
│   ├── test_cross_process.py   # 跨进程测试（PYTHONHASHSEED影响）
│   ├── test_fuzzing.py         # Fuzzing测试（随机生成测试用例）
│   ├── test_cross_version_enhanced.py  # 增强版跨版本测试
│   ├── run_cross_version_tests.py      # 跨版本测试驱动脚本
│   ├── marshal_cross_version_test.py   # 单版本测试脚本
│   ├── detect_differences.py   # 差异检测脚本
│   └── compare_cross_platform.py       # 跨平台对比脚本
├── scripts/                    # 脚本目录
│   ├── run_matrix.py           # 环境矩阵测试脚本
│   └── run_hashseed_case.py    # Hash seed测试脚本
├── docs/                       # 文档目录
│   ├── final_report_draft.md   # 最终报告
│   └── traceability_matrix.md  # 可追溯性矩阵
├── results/                    # 测试结果目录
└── requirements.txt            # 依赖清单
```

## 安装方法

```bash
# 创建虚拟环境
python -m venv .venv
```

**Windows PowerShell**:
```bash
.venv\Scripts\Activate.ps1
```

**Linux / macOS**:
```bash
source .venv/bin/activate
```

**安装依赖**:
```bash
pip install -r requirements.txt
```

## 运行测试

### 1. 运行所有基础测试

```bash
# Windows
.\.venv\Scripts\python.exe -m pytest tests/test_basic_types.py tests/test_boundaries.py tests/test_float_specials.py tests/test_collections.py tests/test_recursive.py tests/test_code_objects.py tests/test_cross_process.py tests/test_fuzzing.py -v

# Linux / macOS
python -m pytest tests/test_basic_types.py tests/test_boundaries.py tests/test_float_specials.py tests/test_collections.py tests/test_recursive.py tests/test_code_objects.py tests/test_cross_process.py tests/test_fuzzing.py -v
```

### 2. 运行跨版本测试

```bash
# 运行增强版跨版本测试
python test_cross_version_enhanced.py

# 运行多版本对比测试（需要conda环境）
python run_cross_version_tests.py
```

### 3. 运行跨平台对比

```bash
# 先在各平台运行 test_cross_version_enhanced.py，然后将结果文件放在同一目录
python compare_cross_platform.py
```

### 4. 运行差异检测

```bash
python detect_differences.py
```

### 5. 运行环境矩阵测试

```bash
python scripts/run_matrix.py
```

### 6. 运行 Hash Seed 跨进程测试

```bash
python scripts/run_hashseed_case.py
```

## 测试结果汇总

### 测试统计

| 类别 | 测试数 | 通过 | 失败 | 跳过 |
|------|--------|------|------|------|
| 基础类型 | 48 | 48 | 0 | 0 |
| 边界值 | 34 | 34 | 0 | 0 |
| 浮点特殊值 | 18 | 18 | 0 | 0 |
| 集合 | 4 | 4 | 0 | 0 |
| 跨进程 | 2 | 2 | 0 | 0 |
| 递归结构 | 3 | 3 | 0 | 0 |
| 代码对象 | 3 | 2 | 0 | 1 |
| Fuzzing | 9 | 7 | 2 | 0 |
| 跨版本 | 15 | 14 | 1 | 0 |
| 跨平台对比 | 8 | 8 | 0 | 0 |
| **总计** | **164** | **159** | **3** | **1** |

### 关键发现

#### ✅ 稳定行为
- **基本类型**：int、float、str、bytes、list、tuple、dict 在同一进程内完全稳定
- **浮点特殊值**：NaN、Inf、-Inf、-0.0 处理正确
- **递归结构**：正确抛出 ValueError，不会导致崩溃
- **共享引用**：同一对象多次引用序列化一致

#### ❌ 不稳定行为（预期）
1. **marshal 版本差异**：不同格式版本（0-4）产生不同输出
2. **集合顺序**：字符串集合受 `PYTHONHASHSEED` 影响，跨进程可能不同
3. **代码对象**：跨版本不兼容，跨平台可能不同

## 测试技术说明

### 1. 等价类划分
- 将输入域划分为等价类（int、float、bool、str、bytes、bytearray、tuple、list、dict、set、frozenset、None、Ellipsis）
- 为每个等价类选取代表性值进行测试

### 2. 边界值分析
- 整数边界：32位/64位极限、大整数（10^100）
- 容器大小：0、1、255、256、1024
- 字符串长度：0、1、255、256、1024

### 3. 特殊值测试
- 浮点特殊值：NaN、Inf、-Inf、-0.0
- 精度边界：2.0 ± 2^-52、最大/最小浮点数

### 4. 负测试
- 不支持的类型：object()、lambda、自定义类实例、文件对象、socket对象

### 5. 鲁棒性测试
- 递归结构：自引用列表/字典
- 深度嵌套：2000层列表、500层元组
- 循环引用：对象间相互引用

### 6. 白盒启发式测试
- 基于 marshal 源代码知识设计测试
- 代码对象的版本敏感性测试
- 共享引用的序列化处理

### 7. Fuzzing/属性基测试
- 使用 Hypothesis 自动生成随机测试用例
- 测试深度嵌套（8层）、跨版本兼容性

### 8. 跨进程测试
- 在不同 `PYTHONHASHSEED` 值的子进程中测试
- 记录序列化结果的 SHA-256 摘要

### 9. 跨版本测试
- 在多个 Python 版本（3.8、3.9、3.10、3.11、3.12）上运行测试
- 测试跨版本反序列化兼容性

### 10. 跨平台测试
- 在不同操作系统（Windows、Kali Linux、macOS）上运行测试
- 对比各平台的序列化结果

### 11. 环境矩阵测试
- 自动记录 Python 版本、操作系统、marshal 版本、硬件信息
- 确保测试可追溯和可复现

## 运行示例

### 示例1：运行基础类型测试

```bash
PS D:\study\软件测试\marshal-stability-tests> .\.venv\Scripts\python.exe -m pytest tests/test_basic_types.py -v
======================================= test session starts =======================================
platform win32 -- Python 3.8.6, pytest-7.4.0, pluggy
rootdir: D:\study\software_testing\marshal-stability-tests
collected 48 items

tests/test_basic_types.py::test_representatives_are_stable[none[0]] PASSED
tests/test_basic_types.py::test_representatives_are_stable[ellipsis[0]] PASSED
tests/test_basic_types.py::test_representatives_are_stable[bool[0]] PASSED
...
======================================= 48 passed in 0.12s ========================================
```

### 示例2：运行跨版本测试

```bash
PS D:\study\software_testing\marshal-stability-tests> .\.venv\Scripts\python.exe test_cross_version_enhanced.py
[INFO] Python 3.8.6 (Windows)
[INFO] Testing basic types...
[INFO] Testing float specials...
[INFO] Testing set ordering...
[INFO] Testing code objects...
[INFO] Testing cross-process set variations...
[INFO] Results saved to: marshal_enhanced_3.8.6_win32_random.json
```

### 示例3：运行跨平台对比

```bash
PS D:\study\software_testing\marshal-stability-tests> .\.venv\Scripts\python.exe compare_cross_platform.py
======================================================================
【跨平台结果详细对比】
======================================================================
找到 3 个结果文件:
  - marshal_enhanced_3.11.5_win32_random.json
  - marshal_enhanced_3.11.4_linux_random.json
  - marshal_enhanced_3.12.1_darwin_random.json

======================================================================
【各平台环境信息】
======================================================================
...
```

## 测试结果文件

测试结果保存在 `results/` 目录：

| 文件 | 描述 |
|------|------|
| `environment_metadata_run_{id}.json` | 环境元数据（Python版本、OS、marshal版本等） |
| `pytest_stdout_run_{id}.txt` | pytest 输出日志 |
| `summary_run_{id}.json` | 测试统计汇总 |
| `marshal_enhanced_{version}_{platform}_{hashseed}.json` | 跨平台测试详细结果 |

## 代码规范

本项目遵循 **PEP 8** 编码规范，可以使用以下命令检查：

```bash
ruff check .
```

## 报告文档

完整的测试报告和可追溯性矩阵位于 `docs/` 目录：

- `docs/final_report_draft.md` - 最终测试报告（包含所有13项测试维度）
- `docs/traceability_matrix.md` - 可追溯性矩阵

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！