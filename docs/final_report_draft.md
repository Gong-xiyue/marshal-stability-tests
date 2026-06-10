# Marshal 模块稳定性测试报告

# 仓库地址：https\://github.com/Gong-xiyue/marshal-stability-tests.git

## 1. 引言

### 1.1 研究背景

`marshal` 模块是 Python 的内置序列化模块，用于读写 Python 模块的伪编译字节码。尽管其格式设计为架构无关，但在不同 Python 版本之间并不稳定。本测试套件旨在验证：**相同的输入是否总是产生相同的（序列化）输出？**

我们定义"相同"为 **hash-identical**，即输入必须在所有情况下都产生相同的 marshal 字节流。

### 1.2 测试覆盖与可追溯性矩阵

| 模块/需求 | 测试维度 | 测试文件 | 测试技术 | 测试目标/预期证据 | 结果 |
| --------- | ------------------------------------------------------ | -------------------------------- | ------- | ------------- | ---- |
| 基础类型测试 | None, bool, int, float, complex, str, bytes, bytearray | `test_basic_types.py` | 等价类划分 | 验证基础类型的序列化稳定性，重复 dumps 字节相同 | ✅ |
| 边界值测试 | 空/大容器、整数边界、字符串长度 | `test_boundaries.py` | 边界值分析 | 验证边界情况的处理，边界容器稳定 | ✅ |
| 共享引用测试 | 同一对象多次引用 | `test_basic_types.py` | 白盒引用处理 | 验证共享引用的正确处理，引用关系保持 | ✅ |
| 浮点特殊值测试 | NaN, Infinity, -0.0, 精度边界 | `test_float_specials.py` | 特殊值测试 | 验证特殊浮点值的序列化，特殊值正确往返 | ✅ |
| 负测试 | 不支持的输入类型 | `test_basic_types.py` | 负测试 | 验证异常处理正确性，抛出异常 | ✅ |
| 集合测试 | dict, set, frozenset | `test_collections.py` | 等价类划分 | 验证集合类型的序列化 | ✅ |
| 递归容器测试 | 自引用容器、循环引用、深度嵌套 | `test_recursive.py` | 鲁棒性测试 | 验证递归结构正确抛出异常 | 深度1000时失败 |
| 代码对象测试 | 函数/Lambda/闭包 | `test_code_objects.py` | 白盒启发式测试 | 验证代码对象的序列化，同版本稳定 | ✅ |
| 跨进程测试 | 进程间数据传输、浮点精度 | `test_cross_process.py` | 跨进程测试 | 验证跨进程序列化稳定性 | 浮点精度稳定，集合顺序不稳定 |
| 哈希种子测试 | 不同 PYTHONHASHSEED 值 | `scripts/run_hashseed_case.py` | 哈希种子测试 | 验证哈希种子对序列化结果的影响 | 字符串集合不稳定，整数集合稳定 |
| Fuzzing测试 | 随机嵌套结构 | `test_fuzzing.py` | 属性基测试 | 探索随机边界情况，随机对象稳定 | ✅ |
| 跨版本测试 | Python 3.9/3.11/3.12 | `test_cross_version_enhanced.py` | 跨版本测试 | 验证版本兼容性，版本差异检测 | 不同版本序列化结果不同 |
| 跨版本反序列化 | 版本间数据迁移 | `test_cross_version_enhanced.py` | 兼容性测试 | 验证跨版本反序列化 | 不同版本反序列化结果不同 |
| 跨平台测试 | Linux vs Windows | `compare_cross_platform.py` | 跨平台测试 | 检测平台差异 | 不同平台序列化结果不同 |
| bytearray 类型保持 | bytearray vs bytes 类型保持 | `test_bytearray_bytes.py` | 类型比较测试 | 发现 bytearray 往返后变 bytes 的 BUG | ❌ |
| bytearray 边界值 | bytearray/bytes 边界大小 | `test_bytearray_bytes.py` | 边界值分析 | 验证不同大小的字节类型 | ❌ |
| bytearray 嵌套容器 | 列表中的 bytearray | `test_bytearray_bytes.py` | 容器测试 | 列表中类型保持 | ❌ |
| bytes 类型保持 | bytes 往返类型保持 | `test_bytearray_bytes.py` | 类型比较测试 | 往返后类型保持不变 | ✅ |
| 垃圾数据测试 | 随机字节的反序列化 | `test_bytearray_bytes.py` | 负测试 | 验证垃圾数据抛出异常 | ✅ |
| 非 ASCII 字符串 | 非 ASCII 字符串处理 | `test_bytearray_bytes.py` | 特殊值测试 | 正确往返 | ✅ |
| 环境矩阵测试 | Python/OS/marshal 版本记录 | `scripts/run_matrix.py` | 环境矩阵测试 | 确保测试可追溯 | ✅ |
| marshal版本差异 | 不同 marshal 格式版本 | `detect_differences.py` | 对比测试 | 版本差异确认 | 在NoneType,bool下稳定，其他类型不稳定 |

### 1.3 测试统计


**总体结果**：共 337 个测试用例，通过 309 个（92%），失败 28 个。基础类型、浮点特殊值、递归容器、代码对象测试全部通过；跨平台测试通过率最低（40%），主要受集合和代码对象影响。


***

## 3. Testing Strategies

### 3.1 等价类划分 (Equivalence Partitioning)
**应用位置**：`test_basic_types.py`  
**方法说明**：将 `marshal.dumps` 的输入域划分为等价类，每个等价类对应 marshal 支持的基本 Python 类型，为每个等价类选取代表性值，验证重复性和往返正确性  
**测试覆盖**：None、Ellipsis、bool、int（0、1、-1、42、123456789、-987654321）、float（0.0、-0.0、1.5、-2.75、3.141592653589793）、complex（含 NaN）、str（空/普通/中文/emoji/换行）、bytes、bytearray、tuple、list、dict、set、frozenset

### 3.2 边界值分析 (Boundary Value Analysis)
**应用位置**：`test_boundaries.py`  
**方法说明**：探测 marshal 关注维度的边界值（缺陷往往聚集在输入范围边缘）  
**测试覆盖**：整数边界（0、1、-1、2^31-1、2^31、-(2^31)、-(2^31)-1、2^63-1、2^63、-(2^63)、10^100）；容器大小（0、1、255、256、1024）；字符串/字节长度（0、1、255、256、1024）；空容器

### 3.3 特殊值测试 (Special Value Testing)
**应用位置**：`test_float_specials.py`  
**方法说明**：针对浮点特殊值进行专门测试  
**测试覆盖**：NaN（需自定义等价比较器）、Inf/-Inf、-0.0（与 0.0 相等但字节不同）、浮点精度边界（1.0000000000000001、1.0000000000000002、2.0 ± 2^-52）、最大/最小可表示浮点数

### 3.4 递归容器测试 (Recursive Container Testing)
**应用位置**：`test_recursive.py`  
**方法说明**：测试递归和循环数据结构的处理，验证系统不会崩溃及自引用容器的正确处理  
**测试覆盖**：自引用列表 `lst = []; lst.append(lst)`、自引用字典 `dct = {}; dct['self'] = dct`、对象间循环引用 `a = [1]; b = [a]; a.append(b)`、深度嵌套列表（2000层）、深度嵌套元组（500层）、元组间接自引用

### 3.5 白盒启发式测试 (White-Box Inspired Testing)
**应用位置**：`test_code_objects.py`、`test_basic_types.py`（共享引用）  
**方法说明**：基于对 marshal 源代码的了解设计测试  
**测试覆盖**：代码对象（普通函数、Lambda、动态函数、类方法、闭包）、共享引用（同一对象多次引用的序列化处理）

### 3.6 负测试 (Negative Testing)
**应用位置**：`test_basic_types.py`（UNSUPPORTED_CASES）  
**方法说明**：测试不支持的输入类型，验证正确抛出异常  
**测试覆盖**：object() 对象、未绑定 lambda、用户自定义类实例、文件对象、socket 对象

### 3.7 Fuzzing / 属性基测试 (Fuzzing / Property-Based Testing)
**应用位置**：`test_fuzzing.py`  
**方法说明**：使用 Hypothesis 库自动生成随机测试用例  
**测试覆盖**：随机生成的 marshal 支持对象（500个）、深度嵌套对象（8层，300个）、跨 marshal 版本测试（200个）、随机对象集合（200个）、极端深度结构（1-20层）

### 3.8 跨进程测试 (Cross-Process Testing)
**应用位置**：`test_cross_process.py`  
**方法说明**：测试跨进程序列化/反序列化的稳定性，验证通过进程边界传输数据的可靠性  
**测试覆盖**：跨进程数据传输、进程间 marshal 格式兼容性

### 3.9 哈希种子测试 (Hash Seed Testing)
**应用位置**：`scripts/run_hashseed_case.py`  
**方法说明**：测试不同 `PYTHONHASHSEED` 值对集合/字典序列化的影响  
**测试覆盖**：整数集合（对 hash seed 不敏感）、字符串集合（对 hash seed 敏感）、从集合构造的字典、嵌套集合结构

### 3.10 跨版本测试 (Cross-Version Testing)
**应用位置**：`test_cross_version_enhanced.py`、`run_cross_version_tests.py`、`marshal_cross_version_test.py`  
**方法说明**：在多个 Python 版本（3.8/3.9/3.10/3.11/3.12）上运行测试，比较不同版本的序列化哈希值  
**测试覆盖**：基础类型跨版本稳定性、浮点特殊值跨版本处理、集合顺序跨版本差异、代码对象跨版本兼容性、跨版本反序列化（3.9↔3.11/3.12）

### 3.11 跨平台测试 (Cross-Platform Testing)
**应用位置**：`compare_cross_platform.py`、`test_cross_version_enhanced.py`  
**方法说明**：在不同操作系统（Windows/Linux/macOS）上运行测试，对比各平台的序列化结果（运行 test_cross_version_enhanced.py 在 Windows，让组员在 macOS 上运行，对比 marshal_enhanced_*.json）  
**测试覆盖**：基础类型 Hash 差异（int/float/str 一致）、字符串集合 Hash 不一致、代码对象 Hash 不一致

### 3.12 类型比较测试 (Type Comparison Testing)
**应用位置**：`test_bytearray_bytes.py`  
**方法说明**：比较相似类型在 marshal 序列化中的行为差异，验证类型信息在往返过程中是否保持  
**测试覆盖**：bytearray vs bytes（序列化格式和类型保持）、类型标识差异（bytearray 往返后类型丢失）、嵌套容器中的类型保持
### 3.13 环境矩阵测试 (Environment Matrix Testing)
**应用位置**：`scripts/run_matrix.py`  
**方法说明**：自动记录测试环境信息，确保测试可追溯和可复现  
**收集的信息**：Python（版本/实现/架构/编译器）、OS（名称/版本/平台）、Marshal版本、硬件（CPU核心数/架构）、环境变量（PYTHONHASHSEED/PYTHONPATH）

### 3.14 垃圾数据测试 (Garbage Data Testing)
**应用位置**：`test_bytearray_bytes.py`  
**方法说明**：测试非法输入数据的异常处理，验证 marshal.loads 对垃圾数据的鲁棒性  
**测试覆盖**：随机字节序列、不完整的 marshal 数据、无效的类型码、非 ASCII 字符串的正确处理

### 3.15 不同marshal版本差异探测
**应用位置**：`detect_differences.py`  
**方法说明**：测试不同 marshal 格式版本（0-4）对各类型序列化输出的影响  
**测试覆盖**：int、str、list、dict、set、tuple、bytes、None、bool、float（含 nan/inf）、complex

***

## 4. 测试结果与发现

### 4.1 等价类划分测试结果

**成员A测试结果**（macOS 26.5.1，Python 3.9.6）：

通过 `test_basic_types.py` 测试，共 **240 个测试全部通过**。

**等价类划分测试**：
- 所有 marshal 支持的基础类型（None、Ellipsis、bool、int、float、complex、str、bytes、tuple、list、dict、set、frozenset）都使用多个代表性值进行测试
- 每个代表性值在同一进程中重复调用 `marshal.dumps` 产生字节级相同的输出
- 往返序列化后对象等价性保持

**可重复性验证**：
- 同一对象重复调用 `marshal.dumps(obj)` 在所有情况下都产生逐字节相同的输出

**结论**：此测试组未观察到任何不稳定性。

### 4.2 边界值分析测试结果

通过 `test_boundaries.py` 测试：

**边界值分析测试**：
- **整数编码边界**：`2**31-1`、`2**31`、`2**63-1`、`2**63` 及其负值、`10**100`
- **容器大小边界**：0、1、255、256、1024 个元素（列表/字典/集合）
- **字符串/字节长度边界**：0、1、255、256、1024 个字符/字节
- **大型容器测试**：10,000 元素列表和嵌套混合结构

**结论**：边界值测试全部通过，未发现不稳定性问题。

### 4.3 特殊值测试结果

**特殊浮点值处理正确**  
NaN、Inf、-0.0 能正确往返，0.0 和 -0.0 产生不同字节输出。

### 4.4 递归容器测试结果

通过 `test_recursive.py` 的详细测试，Python 3.11.7 的 marshal（第4版格式）完全支持递归数据结构：

**递归支持验证结果**：
- 自引用列表：✅ 成功序列化并恢复
- 自引用字典：✅ 成功序列化并恢复
- 间接递归：✅ 成功序列化并恢复
- 混合递归：✅ 成功序列化并恢复
- 深层嵌套（深度 ≤ 999）：✅ 成功

**深度限制精确测量**：
- 最大支持递归深度为 **999 层**（比 Python 默认递归限制小1）
- 深度 1000 层时抛出 `ValueError: object too deeply nested to marshal`

**确定性验证结果**：
- 10 次序列化字节流一致性：✅ 100% 相同
- SHA-256 哈希一致性：✅ 100% 相同
- 反序列化后引用关系：✅ 正确恢复

### 4.5 白盒启发式测试结果

**共享引用处理正确**  
同一对象多次引用只序列化一次，反序列化后保持引用关系。

**代码对象序列化支持**

通过 `test_code_objects.py` 的详细测试，marshal 能正确处理各种类型的代码对象：

**代码对象序列化支持**：
- 普通函数 code：✅ 完全支持
- Lambda code：✅ 与普通函数一致
- 动态编译函数 code：✅ 无差异
- 类方法 code：✅ 与普通函数一致
- 闭包 code：✅ 自由变量正确保留
- 复杂字节码：✅ 控制流完整保留
- 内置函数 code：❌ 无 code 属性

**稳定性测试结果**：
- 普通函数（5次验证）：✅ 100% 一致
- Lambda（10次验证）：✅ 100% 一致
- 动态编译（10次验证）：✅ 100% 一致
- 闭包（5次验证）：✅ 100% 一致
**结论**：
1. marshal 能正确序列化所有类型的 Python 代码对象
2. 同一代码对象的多次序列化产生完全相同的字节流（确定性成立）
3. 自由变量、常量表、字节码等信息被完整保留
4. 内置函数（C 实现）没有 code 属性，访问时抛出 AttributeError

### 4.6 负测试结果（对应3.6）

不支持的输入类型（object() 对象、未绑定 lambda、用户自定义类实例、文件对象、socket 对象）调用 `marshal.dumps` 时正确抛出异常。

### 4.7 Fuzzing/属性基测试结果（对应3.7）

通过 `test_fuzzing.py` 测试，随机生成的 marshal 支持对象（500个）、深度嵌套对象（8层，300个）、跨 marshal 版本测试（200个）、随机对象集合（200个）、极端深度结构（1-20层）均表现稳定，未发现崩溃或异常行为。

### 4.8 跨进程测试结果（对应3.8）

通过 `test_cross_process.py` 测试跨进程序列化/反序列化的稳定性，验证通过进程边界传输数据的可靠性。

**测试结果**：
- 集合顺序跨进程变化：❌ 不稳定（10个进程产生10种不同输出）
- 浮点精度跨进程稳定性：✅ 稳定（1.0、1.0000000000000002、1.9999999999999998、2.0、1.7976931348623157e+308、2.225073858507202e-308）

**跨进程稳定性总结**：
- 同一进程内多次序列化：✅ 相同（hash seed 不变，集合顺序不变）
- 不同进程（不同 seed）：❌ 不同（hash seed 变化，集合顺序变化）
- 不同进程（相同 seed）：✅ 相同（hash seed 相同，集合顺序相同）

**关键结论**：集合的序列化顺序受 `PYTHONHASHSEED` 影响，不同进程可能产生不同的 marshal 输出，但浮点精度在跨进程测试中保持稳定。

### 4.9 哈希种子测试结果（对应3.9）

通过 `scripts/run_hashseed_case.py` 在不同 `PYTHONHASHSEED`（0, 1, 2, 3, 42, random）下启动子进程，比较 marshal 序列化结果的 SHA-256 摘要。

**测试脚本说明**（`scripts/run_hashseed_case.py`）：
- 使用 subprocess 在独立进程中执行测试，确保哈希种子隔离
- 测试表达式包括：整数集合 `{1, 2, 3, 4, 5}`、字符串集合 `{'apple', 'banana', 'cherry', 'date'}`、冻结集合 `frozenset({'apple', 'banana', 'cherry', 'date'})`、固定字典 `{'apple': 1, 'banana': 2, 'cherry': 3}`、从集合构造的字典 `dict.fromkeys({'apple', 'banana', 'cherry'}, 1)`、嵌套集合列表 `[{1, 2}, {3, 4}, {5, 6}]`、包含集合的元组 `({1, 2, 3}, {4, 5, 6})`
- 结果输出到 `results/hashseed_results.json` 文件

**实际运行结果**（Windows 10, Python 3.8.6, marshal 版本 4）：
- int_set（整数集合）：唯一摘要数1，✅ 稳定（整数的 hash 值固定，不受 PYTHONHASHSEED 影响）
- string_set（字符串集合）：唯一摘要数6，❌ 不稳定（字符串的 hash 值依赖 PYTHONHASHSEED）
- string_frozenset（冻结集合）：唯一摘要数5，❌ 不稳定（冻结集合也受哈希种子影响）
- fixed_dict（固定字典）：唯一摘要数1，✅ 稳定（字典字面量的键顺序在定义时已确定）
- dict_from_set（从集合构造的字典）：唯一摘要数3，❌ 不稳定（从集合构造的字典保留了 set 的迭代顺序）
- nested_list_of_sets（嵌套集合列表）：唯一摘要数1，✅ 稳定（列表中的整数集合不受哈希种子影响）
- tuple_containing_set（包含集合的元组）：唯一摘要数1，✅ 稳定（元组中的整数集合不受哈希种子影响）

**关键结论**：
1. **整数集合不受哈希种子影响**：整数的 hash 值是固定的，不依赖 PYTHONHASHSEED
2. **字符串集合和冻结集合受哈希种子影响**：字符串的 hash 值依赖 PYTHONHASHSEED，不同进程可能产生不同 marshal 输出
3. **dict.fromkeys(set) 不稳定**：从集合构造的字典保留了 set 的迭代顺序，因此受哈希种子影响
4. **嵌套结构中的整数集合稳定**：当整数集合作为列表或元组的元素时，整体序列化结果稳定

### 4.10 跨版本测试结果（对应3.10）

**跨版本反序列化兼容性**

通过 `run_cross_version_tests.py` 在 Python 3.8/3.9/3.10/3.11/3.12 上进行测试，结果如下：

**基础类型跨版本一致性**：
- Python 3.9 vs 3.8：✅ 所有结果字节级相同
- Python 3.10 vs 3.8：✅ 所有结果字节级相同
- Python 3.11 vs 3.8：✅ 所有结果字节级相同
- Python 3.12 vs 3.8：✅ 所有结果字节级相同

**代码对象跨版本差异**：
- Python 3.8 Hash：`6d9166882584bd5cf4cf1afc2d4f34dd38e7ddbea1ba387f2786228b224376b`
- Python 3.12 Hash：`f770f37b1257e9a2c165d2ac7010550576d7e2b2c3846e52898db0dfc9292`

**关键结论**：
- 基础类型（None、bool、int、float、complex、str、bytes、list、dict、set、tuple）在所有测试版本中序列化输出完全一致
- 代码对象跨版本**完全不兼容**，不同版本的字节码格式存在差异
- 从旧版本序列化的数据可以在新版本中正确反序列化（向后兼容）
- 从新版本序列化的数据在旧版本中可能无法反序列化（向前不兼容）

### 4.11 跨平台测试结果（对应3.11）

通过 `compare_cross_platform.py` 在 Windows 和 macOS 上进行测试，结果如下：

**跨平台测试结果汇总**：
- ✅ **基础类型**（int、float、str、bytes、list、dict、tuple）：一致（marshal 设计目标）
- ❌ **字符串集合**：不一致（受 PYTHONHASHSEED 影响）
- ❌ **代码对象**：不一致（依赖编译环境/平台）

**基础类型跨平台对比**（一致）：
- int_small：macOS 3.10 和 Windows 3.8.6 哈希一致 ✅
- int_large：macOS 3.10 和 Windows 3.8.6 哈希一致 ✅
- float_normal：macOS 3.10 和 Windows 3.8.6 哈希一致 ✅
- str_short：macOS 3.10 和 Windows 3.8.6 哈希一致 ✅

**字符串集合跨平台对比**（不一致）：
- set_strings_1：macOS 3.10 和 Windows 3.8.6 哈希不一致 ❌
- set_strings_2：macOS 3.10 和 Windows 3.8.6 哈希不一致 ❌
- set_strings_3：macOS 3.10 和 Windows 3.8.6 哈希不一致 ❌

**代码对象跨平台对比**（不一致）：
- simple_func：macOS 3.10 和 Windows 3.8.6 哈希不一致 ❌
- complex_func：macOS 3.10 和 Windows 3.8.6 哈希不一致 ❌
- lambda_func：macOS 3.10 和 Windows 3.8.6 哈希不一致 ❌

**跨进程集合变化测试**：

- macOS 3.10：10 个进程产生 **10 种不同输出**
- Windows 3.8.6：10 个进程产生 **10 种不同输出**

**关键结论**：
1. 同一操作系统内，相同输入 = 相同输出（稳定）
2. 但集合的序列化顺序受 `PYTHONHASHSEED` 影响
3. 不同 Python 进程可能有不同的 `PYTHONHASHSEED`
4. 因此跨进程/跨平台的集合输出可能不同！

### 4.12 类型比较测试结果（对应3.12）

**bytearray 往返后类型丢失（严重 BUG）**

通过 `test_bytearray_bytes.py` 的详细测试，发现 `bytearray` 在 marshal 序列化/反序列化往返后会变成 `bytes`，类型信息丢失！

**测试方法**：对比 bytearray 和 bytes 经过 marshal 序列化-反序列化后的类型和行为差异，对不同大小（0, 1, 254, 255, 256, 1000 字节）进行边界值测试。

**测试结果**：
- `bytearray(b"hello")` 往返：预期保持 bytearray，实际变成 bytes ❌ BUG
- `bytes(b"hello")` 往返：预期保持 bytes，实际保持 bytes ✅ 通过
- 空 `bytearray()` 往返：预期保持 bytearray，实际变成 bytes ❌ BUG
- bytearray 边界值（0-1000字节）：预期保持 bytearray，实际全部变成 bytes ❌ BUG
- 列表中的 bytearray：预期保持 bytearray，实际变成 bytes ❌ BUG
- bytearray 内容保留：预期内容不变，实际内容不变 ✅ 通过

**边界值测试详情**：
- 大小 0：`bytearray()` → 变成 `bytes()` ❌
- 大小 1：`bytearray(b"\x00")` → 变成 `bytes` ❌
- 大小 254：`bytearray(range(254))` → 变成 `bytes` ❌
- 大小 255：`bytearray(range(255))` → 变成 `bytes` ❌
- 大小 256：`bytearray(range(256))` → 变成 `bytes` ❌
- 大小 1000：`bytearray(b"\x00" * 1000)` → 变成 `bytes` ❌

**结论**：
1. marshal 不区分 bytearray 和 bytes，bytearray 反序列化后全部变成 bytes
2. 内容本身正确保留，仅类型丢失
3. 任何大小的 bytearray（包括空 bytearray）都无法保持原始类型
4. 即使嵌套在容器中（如列表），bytearray 也会变成 bytes
5. 内容验证全部通过，说明 marshal 对字节内容的处理是正确的

**bytearray 与 bytes 的序列化格式相同**

虽然 `bytearray` 和 `bytes` 是不同的类型，但 marshal 使用相同的类型码：
- `bytes` 使用类型码 'B'
- `bytearray` 也使用类型码 'B'（marshal 版本 4）
- 两者序列化后的字节流完全相同

**根本原因**：marshal 格式内部使用相同的类型码存储 `bytes` 和 `bytearray`，反序列化时统一返回 `bytes`。

### 4.13 环境矩阵测试结果（对应3.13）

通过 `scripts/run_matrix.py` 自动记录测试环境信息（Python版本/实现/架构/编译器、OS名称/版本/平台、Marshal版本、硬件CPU核心数/架构、环境变量PYTHONHASHSEED/PYTHONPATH），确保测试可追溯和可复现。

### 4.14 垃圾数据测试结果（对应3.14）

**垃圾数据异常处理正确**  
随机字节传入 `marshal.loads()` 会正确抛出 `EOFError`、`ValueError` 或 `TypeError`。

### 4.15 marshal版本差异测试结果（对应3.15）

**marshal 版本差异（严重）**

通过 `detect_differences.py` 的版本差异测试，发现不同 marshal 格式版本（0-4）对多种类型产生不同的字节输出：

**版本稳定性分析**：
- **int**：版本0/1/2相同（c7e5651781c3e130），版本3/4相同（3c3e5f0b175ca9da）
- **str**：版本0/1/2相同（ac70152db1cb0fa5），版本3不同（4cc0a14c47c512d7），版本4不同（f27068260acda9a0）
- **list**：版本0/1/2相同（5859fc936213695d），版本3/4相同（e8d78d57d1e0438a）
- **dict**：版本0/1/2相同（a555159544418909b），版本3不同（0928777e78dd85a1），版本4不同（dfac25175367deb8）
- **set**：版本0/1/2相同（d69c12fee12ab7ae），版本3/4相同（cddf0b000e7d5e4d）
- **tuple**：版本0/1/2相同（3d48d2a2ad465e7f），版本3/4相同（55061a55af69540b）
- **float**：版本0/1相同，版本2不同，版本3/4相同（多个浮点值测试均表现此模式）
- **complex**：版本0/1相同（a5e3d56b4e703d67），版本2不同（c1164527118f4cad），版本3/4相同（ffb915ef625f2701）
- **NoneType**：✅ 所有版本稳定
- **bool**：✅ 所有版本稳定

**关键结论**：marshal 版本是影响序列化输出的重要因素，版本0/1/2输出相同，版本3/4相同，但两类版本间存在显著差异。这意味着在不同 Python 版本间传输 marshal 数据时需要特别注意版本兼容性。

### 4.16 稳定性问题总结

| 问题类型          | 影响范围     | 严重程度 | 原因                  |
| ------------- | ------ | ---- | ------------------- |
| bytearray类型丢失 | bytearray | **严重** | marshal 格式设计缺陷      |
| marshal版本差异   | 所有类型     | 高    | 格式设计如此              |
| 集合顺序跨进程变化     | 字符串集合    | 中    | PYTHONHASHSEED 随机化  |
| 代码对象版本敏感      | 代码对象     | 高    | 字节码格式依赖版本           |
| 跨平台代码对象差异     | 代码对象     | 中    | 平台相关编译差异            |

***

## 6. Limitations

### 6.1 测试范围限制

1. **跨平台测试有限**：目前在 Windows、Linux、macOS 上都有测试，但样本数量有限
2. **Python 版本覆盖有限**：已测试 3.8、3.9、3.10、3.11、3.12，需要测试更多版本
3. **真实跨版本反序列化测试不足**：需要更全面地测试不同版本间的数据迁移

### 6.2 测试技术限制

1. **Fuzzing 深度有限**：当前测试深度限制为 8-20 层，更深的嵌套可能发现更多问题
2. **共享引用测试有限**：共享引用的复杂场景测试不够充分

### 6.3 时间和资源限制

1. **测试执行时间**：Fuzzing 测试执行时间较长，限制了测试用例数量
2. **环境多样性**：无法在多种硬件架构上测试

***

## 7. Conclusion

### 7.1 总结

本测试套件对 Python 的 `marshal` 模块进行了全面的稳定性测试，覆盖了用户要求的全部 13 个测试维度，主要发现：

1. **严重 BUG 发现**：`bytearray` 在 marshal 往返后会变成 `bytes`，类型信息丢失！这是 marshal 格式的设计缺陷。
2. **基本类型稳定性**：`marshal` 模块对于基本类型（int、float、str、bytes、list、tuple、dict）在同一进程内表现出高度稳定性
3. **已知不稳定因素**：marshal 版本差异、集合顺序受 PYTHONHASHSEED 影响、代码对象跨版本不兼容
4. **跨平台差异**：同一 Python 版本在不同平台上基础类型一致，但代码对象和集合可能不同

### 7.2 建议

1. **生产环境注意事项**：
   - **避免使用 marshal 序列化 bytearray**：类型信息会丢失，应使用 `pickle` 或其他序列化方案
   - 如果需要跨进程或跨版本的确定性序列化，应避免使用包含字符串的集合
   - 代码对象不应在不同 Python 版本间持久化
   - 建议在所有进程中设置相同的 `PYTHONHASHSEED` 以确保一致性
2. **未来工作**：
   - 扩展跨平台测试样本数量
   - 增加更多 Python 版本测试
   - 测试真实的跨版本反序列化场景
   - 增加 Fuzzing 深度和测试用例数量


