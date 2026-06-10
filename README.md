# Stability and Correctness Testing of Python's `marshal` Module

This repository contains a test suite for investigating the stability and correctness
of Python's internal `marshal` serialization module.

The main research question is:

> Does the same input always produce the same hash-identical marshal byte stream?

The project tests repeated serialization, round-trip correctness, floating-point
special values, recursive objects, hash randomization, boundary cases, fuzzing,
and cross-environment behavior.

## Repository structure

```text
marshal-stability-tests/
├── src/marshal_stability/
│   ├── __init__.py
│   ├── comparators.py
│   ├── generators.py
│   ├── hash_utils.py
│   └── cases.py
├── tests/
│   ├── test_basic_types.py
│   ├── test_boundaries.py
│   ├── test_float_specials.py
│   ├── test_collections.py
│   ├── test_recursive.py
│   ├── test_code_objects.py
│   ├── test_fuzzing.py
│   └── test_cross_process.py
├── scripts/
│   ├── run_matrix.py
│   └── run_hashseed_case.py
├── docs/
│   ├── final_report_draft.md
│   └── traceability_matrix.md
└── results/
```

## Installation

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Git Bash / Linux / macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run tests

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src --cov=tests
```

Run style check:

```bash
ruff check .
```

## Cross-process hash seed experiment

```bash
python scripts/run_hashseed_case.py
```

This script starts child Python processes with different `PYTHONHASHSEED` values
and compares the SHA-256 digest of `marshal.dumps(obj)`.

## Cross-version / cross-platform experiment

### 方法1: 基础跨版本测试

运行 `test_cross_version.py` 测试不同 marshal 版本的输出差异：

```bash
# Windows
.\.venv\Scripts\python.exe test_cross_version.py

# macOS / Linux
python3 test_cross_version.py
```

**输出文件**: `marshal_test_result_{Python版本}_{平台}.json`

**测试内容**:
- 基础类型稳定性（int, float, str, list, dict, set, tuple等）
- 不同 marshal 版本（0-4）的输出差异
- 环境信息记录（Python版本、OS、marshal版本）

---

### 方法2: 增强版跨平台测试（推荐）

运行 `test_cross_version_enhanced.py` 进行全面测试：

```bash
# Windows
.\.venv\Scripts\python.exe test_cross_version_enhanced.py

# macOS / Linux
python3 test_cross_version_enhanced.py
```

**输出文件**: `marshal_enhanced_{Python版本}_{平台}_{hash_seed}.json`

**测试内容**:
1. **基礎类型测试**: int, float, str, bytes, list, dict, tuple, bool, None
2. **浮点特殊值测试**: NaN, Inf, -Inf, -0.0, 极大/极小浮点数
3. **集合顺序测试**: 字符串集合的序列化顺序（受PYTHONHASHSEED影响）
4. **代码对象测试**: 函数字节码的序列化（依赖平台/版本）
5. **复杂嵌套结构测试**: 包含集合的嵌套结构
6. **跨进程集合变化测试**: 10个进程的集合序列化结果对比

---

### 方法3: 跨平台结果对比

将不同平台的测试结果文件放到同一目录，然后运行：

```bash
.\.venv\Scripts\python.exe compare_cross_platform.py
```

**对比内容**:
- 各平台环境信息
- 基础类型 Hash 对比（跨平台应该一致）
- 字符串集合 Hash 对比（跨平台通常不同）
- 代码对象 Hash 对比（跨平台/版本通常不同）
- 跨进程集合变化对比

---

### 测试结果总结

#### ✅ 稳定的情况
- **同一进程内**: 相同输入 → 相同输出（marshal保证）
- **基礎类型**: int, float, str, bytes, list, dict, tuple 跨平台一致
- **简单容器**: 不包含集合的容器跨平台一致

#### ❌ 不稳定的情况
- **集合 (set/frozenset)**: 
  - 字符串集合的序列化顺序受 `PYTHONHASHSEED` 影响
  - 跨进程测试发现：10个进程 → 10种不同输出
  - 原因：Python 默认随机化 hash seed
  
- **代码对象 (code objects)**:
  - 函数字节码依赖 Python 版本和编译环境
  - 不同版本/平台产生不同输出
  
- **不同 marshal 版本**:
  - 版本 0/1/2: 旧格式
  - 版本 3: 较新格式
  - 版本 4: 最新格式（Python 3.4+）

---

### 完整测试流程示例

```bash
# 步骤1: 在 Windows 上运行测试
.\.venv\Scripts\python.exe test_cross_version_enhanced.py
# 输出: marshal_enhanced_3.8.6_win32_random.json

# 步骤2: 在 macOS 上运行测试（组员执行）
python3 test_cross_version_enhanced.py
# 输出: marshal_enhanced_3.9.6_darwin_random.json

# 步骤3: 将两个结果文件放到同一目录

# 步骤4: 运行对比脚本
.\.venv\Scripts\python.exe compare_cross_platform.py

# 步骤5: 查看对比结果，截图保存
```

---

### 环境矩阵测试

运行 `scripts/run_matrix.py` 自动收集环境信息并运行所有测试：

```bash
.\.venv\Scripts\python.exe scripts/run_matrix.py
```

**输出文件** (保存在 `results/` 目录):
- `environment_metadata_run_{id}.json` - 环境元数据
- `pytest_stdout_run_{id}.txt` - pytest输出
- `pytest_stderr_run_{id}.txt` - 错误输出
- `test_stats_run_{id}.json` - 测试统计
- `summary_run_{id}.json` - 结果汇总

---

### 差异检测脚本

运行 `detect_differences.py` 快速检测 marshal 输出差异：

```bash
.\.venv\Scripts\python.exe detect_differences.py
```

**检测内容**:
- 不同 marshal 版本的输出差异
- 跨进程集合顺序变化
- 浮点精度边界情况

---

## Notes

The official Python documentation says that `marshal` is not a general
persistence module. It exists mainly for `.pyc` files, and the format may change
between Python versions. Therefore, cross-version byte differences should be
classified as documented limitations rather than necessarily as bugs.
