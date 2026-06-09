# Marshal 模块稳定性测试报告（改进版）

> 仓库地址：https://github.com/Gong-xiyue/marshal-stability-tests.git
>
> 本文件是在 `final_report_draft.md` 基础上的审阅改进版。原始报告完整保留，未做删除。
> 本版本的三项主要改进：
> 1. **实际 Bug 检验**：用直接运行 `marshal` 的方式核验了报告中的每一条「关键发现」，纠正了其中的事实性错误（尤其是发现 4 的类型码描述），并新增了对**测试代码自身缺陷**的检验。
> 2. **用例数量分析**：把报告里互相矛盾的统计数字（164 vs 144 vs 实际代码展开量）逐一对账，给出可复核的真实计数与差异说明。
> 3. **更多测试用例**：针对每个测试维度补充了一批具体、可落地的新增用例建议。
>
> 核验环境：本机 macOS，Python 3.10.0a6，`marshal.version == 4`（直接调用 marshal 验证行为，未经 pytest，因本机解释器为 alpha 版与已装 pytest 不兼容）。

---

## 0. 审阅摘要（Executive Summary）

| 审阅项 | 结论 |
| --- | --- |
| 报告结构 | 完整，覆盖 11 类测试技术，章节编号有重复（出现两个「3.」、章节跳到 6/7），建议重排。 |
| 统计数字可信度 | **不可信**：正文「164/159/3/1」与唯一留存的运行记录「144→143 passed/1 skipped/0 failed」及当前代码展开量（~315 项）三者互相矛盾。详见 §1.3-改。 |
| 关键发现事实性 | 发现 1/2/3/5/6/7 基本成立；**发现 4 存在事实错误**（类型码 'B'/'y' 不正确），已更正。详见 §4.2-改。 |
| 测试代码质量 | 发现 1 处会静默丢失覆盖的**代码缺陷**（`test_code_objects.py` 类体内的游离语句）。详见 §5。 |
| 负测试充分性 | 正文宣称 5 类不支持输入，实际代码仅 2 类（`object()`、`lambda`）。数量被高估。 |

---

## 1. 引言

### 1.1 研究背景

`marshal` 是 Python 内置的序列化模块，用于读写 Python 模块的伪编译字节码。其格式被设计为架构无关，但**官方文档明确声明它在不同 Python 版本之间不保证兼容**。本测试套件的核心问题是：

> **相同的输入是否总是产生相同的（序列化）输出？**

我们把「相同」定义为 **hash-identical**（字节级完全一致）。需要进一步区分三个稳定性层级，这是原报告未明确、但对结论至关重要的：

| 稳定性层级 | 含义 | marshal 的实际表现 |
| --- | --- | --- |
| 进程内重复稳定性 | 同一进程多次 `dumps(同一对象)` | 全类型稳定 ✅ |
| 跨进程稳定性 | 不同进程、相同输入 | 含字符串的 set/dict 受 `PYTHONHASHSEED` 影响 ⚠️ |
| 跨版本/跨平台稳定性 | 不同 Python 版本或 OS | 代码对象不兼容、版本字节流不同 ❌ |

> **改进点**：原报告把这三层混在「稳定/不稳定」一栏里，导致「159 通过 / 3 失败」这种二元统计无法表达「进程内稳定但跨进程不稳定」这类**预期内的不稳定**。改进版在统计口径中区分「断言通过」与「观测到差异（不做 pass/fail 断言）」两类。

### 1.2 测试覆盖矩阵

（与原报告一致，保留 15 行覆盖矩阵；此处不重复，详见 `final_report_draft.md` §1.2。改进版仅就**数量与口径**重新核算，见下。）

### 1.3 测试统计（已对账更正）

原报告给出的统计表为「总计 164 / 通过 159 / 失败 3 / 跳过 1」。**这组数字无法被任何留存证据支持**，存在三方矛盾：

| 数据来源 | collected | passed | failed | skipped | 说明 |
| --- | --- | --- | --- | --- | --- |
| 原报告正文 §1.3 | 164 | 159 | 3 | 1 | 无对应运行日志 |
| 唯一留存运行记录 `results/summary_run_1780541284.json`（Windows / Py3.8.6） | **144** | **143** | **0** | **1** | 真实 pytest 输出 |
| `results/A_basic_boundary_result.txt`（macOS / Py3.9.6，仅 basic+boundary） | 240 | 240 | 0 | 0 | 仅两个文件的子集运行 |
| 当前代码静态展开（本次审阅用 AST 统计，排除 Hypothesis 示例） | **~315** | — | — | — | 代码在 6/8–6/9 被改动后用例数已增长 |

> **关键矛盾**：
> 1. 「3 failed」在任何留存日志中都不存在——唯一日志是 `0 failed`。把跨进程/跨版本「观测到差异」当作「失败」计入，是**口径错误**：这些用例本身用 `print` 记录、并不 `assert` 失败（见 `test_collections.py` 的 `*_variation_detection`、`test_cross_process.py`）。
> 2. 144 与 240 的差异是因为**运行范围不同**（全量 vs 仅 basic+boundary），不能并列汇总。
> 3. 当前代码展开约 315 项（见下表），与正文 164 也对不上——说明报告统计写于早期版本、之后代码增长未回填。

**本次审阅的真实用例计数（按文件，AST 静态展开，参数化已乘开，不含 Hypothesis 的 `max_examples`）：**

| 测试文件 | 测试函数数 | 展开后用例数（约） |
| --- | --- | --- |
| `test_basic_types.py` | 6 | 141 |
| `test_boundaries.py` | 11 | 99 |
| `test_float_specials.py` | 7 | 29 |
| `test_code_objects.py` | 10 | 10 |
| `test_collections.py` | 8 | 8 |
| `test_recursive.py` | 9 | 9 |
| `test_fuzzing.py`（不计 examples） | 11 | 11 |
| `test_cross_version_enhanced.py` | 6 | 6 |
| `test_cross_process.py` | 2 | 2 |
| **合计（静态，不含 Hypothesis 示例）** | **70** | **~315** |

> 若计入 Hypothesis：`test_fuzzing.py` 的 8 个属性测试单独配置了 `max_examples`（500/500/300/200/200/100/100/150 等），单次运行实际生成的样本量在**数千级**，但 pytest 仍只报告为 11 个 test item。**因此用「pytest item 数」与「实际执行样本数」必须分开陈述**，原报告将两者混为一谈。
>
> **改进建议**：报告统计表应改为三栏口径——(a) pytest collected items；(b) 其中含 assert 的「判定型」用例 vs 仅记录的「观测型」用例；(c) Hypothesis 实际样本量。并附上一次**全量、单环境、固定 `PYTHONHASHSEED`** 的 pytest 输出作为唯一权威数字来源。

---
## 2. 关键发现的逐条核验（实际 Bug 检验）

本节对原报告 §4.2 的七条「关键发现」逐条复核。核验方法：在本机直接调用 `marshal`，对每条结论给出可复现的最小验证。

| 发现 | 原报告结论 | 核验结果 | 判定 |
| --- | --- | --- | --- |
| 1 marshal 版本差异 | v0/1/2 相同、v3/v4 不同 | 实测 `b"abc"`：v0/1/2 头字节 `0x73`，v3/v4 头字节 `0xf3`（启用 FLAG_REF/interning）。结论方向正确 | ✅ 成立 |
| 2 跨进程集合顺序 | 字符串集合跨进程输出不同，整数集合不变 | 机制正确：字符串 hash 受 `PYTHONHASHSEED` 影响，小整数 hash 为自身 | ✅ 成立 |
| 3 跨平台同版本差异 | 基础类型一致、字符串集合/代码对象不同 | 机制正确 | ✅ 成立 |
| 4 bytearray vs bytes 类型码 | **「bytes 用 'B'，bytearray 用 'y'」** | **错误**，见下方更正 | ❌ 事实错误 |
| 5 跨版本反序列化 | 旧→新可读，新→旧可能失败，代码对象完全不兼容 | 方向正确（代码对象含 magic/字节码版本相关字段） | ✅ 成立 |
| 6 共享引用 | 同一对象只序列化一次、引用关系保持 | marshal v3+ 的 FLAG_REF 机制确实如此 | ✅ 成立 |
| 7 特殊浮点值 | NaN/Inf/-0.0 正确往返，0.0≠-0.0 字节不同 | 实测 `dumps(0.0) != dumps(-0.0)` 为真，NaN 往返为 NaN | ✅ 成立 |

### 2.1 发现 4 更正（核心事实性错误）

**原报告称**：`bytes` 使用类型码 `'B'`，`bytearray` 使用类型码 `'y'`（marshal v4+），两者序列化字节流不同。

**实测（Py3.10, marshal v4）**：

```
bytes      dumps(b"abc")          = f3 03000000 616263   首字节 0xf3
bytearray  dumps(bytearray(b"abc"))= f3 03000000 616263   首字节 0xf3   # 与 bytes 完全相同！
str        dumps("abc")           = da 03 616263          首字节 0xda
```

更正要点：

1. **类型码不是 'B'/'y'。** CPython `marshal.c` 中 `bytes` 与 `bytearray` 用的是同一个基础类型码 `TYPE_STRING = 's'`（0x73）。报告写的 'B'（0x42）、'y'（0x79）并不存在于该路径。0xf3 = 0x73 | 0x80，高位是 `FLAG_REF`（引用表标记），低 7 位仍是 `'s'`。
2. **bytes 与 bytearray 在 v4 下序列化字节流相同**，不是「不同」。实测两者 `dumps` 结果逐字节一致。
3. **类型身份在往返后丢失**：`marshal.loads(marshal.dumps(bytearray(b"abc")))` 返回的是 **`bytes`**，不是 `bytearray`。这才是 bytearray 真正值得记录的稳定性问题——**marshal 不保留 bytearray 类型**。
4. 版本相关性实测：v0/1/2 下 bytes 与 bytearray 均为 `0x73...`；v3/v4 下均升级为 `0xf3...`。两者在所有版本下彼此一致，差异只发生在「版本之间」，不发生在「bytes 与 bytearray 之间」。

> **对可追溯性矩阵的连带更正**：原 §3 矩阵中「bytearray 类型标识 → 与 bytes 序列化不同 ✅」一行**结论与证据矛盾**，应改为：「bytearray 与 bytes 序列化字节流相同，且 bytearray 往返后退化为 bytes（类型不保留）」，预期证据相应调整。

---
## 3. 测试代码缺陷检验（新增）

审阅测试代码本身，发现以下问题。第 1 项是会**静默丢失覆盖**的真实缺陷，建议优先修复。

### 3.1【缺陷】`test_code_objects.py` 类体内的游离语句

`tests/test_code_objects.py:54-55`：

```python
    def test_builtin_function_no_code_attribute(self):
        with pytest.raises(AttributeError):
            _ = sum.__code__
        ...
    data = marshal.dumps(None)        # ← 第54行：缩进在类体、不在任何方法内
    assert marshal.loads(data) is None # ← 第55行：同上
```

这两行处于 `TestBasicCodeObjects` 类体作用域、不属于任何 `test_` 方法。后果：

- 它们在**类定义时执行一次**，pytest 不会把它当作测试用例统计，也不会在失败时归因到具体用例；
- 作者本意大概率是想写一个 `test_none_round_trips` 之类的方法，**这条覆盖实际上丢失了**；
- 属于「看起来在测、其实没测」的静默盲区，比测试失败更危险。

**修复**：要么删除这两行，要么提升为一个独立方法：

```python
    def test_none_round_trips(self):
        data = marshal.dumps(None)
        assert marshal.loads(data) is None
```

### 3.2【口径】负测试用例数量被高估

`cases.py` 的 `UNSUPPORTED_CASES` 实际只有 **2 项**：`object()` 与 `lambda x: x`。但原报告 §3.6 列出 **5 类**「不支持的输入」（object、lambda、自定义类实例、文件对象、socket 对象）。后三类**在代码中并不存在**对应用例。

实测这三类的真实行为（值得补测）：

```
marshal.dumps(自定义类实例)  -> ValueError   # 可加入 UNSUPPORTED_CASES
marshal.dumps(object())      -> ValueError   # 已覆盖
marshal.dumps(lambda x:x)    -> ValueError   # 已覆盖（注意：函数对象本身不支持）
```

建议把文档宣称的 5 类**真正写进** `UNSUPPORTED_CASES`，让正文与代码一致（见 §4.5 补充用例）。

### 3.3【健壮性】`test_recursive.py::test_deeply_nested_list` 假设过强

该用例断言 2000 层嵌套必抛 `RecursionError`。但 marshal 的栈深度上限依**平台/构建**而异（本机实测 2000 层抛的是 `ValueError`，不是 `RecursionError`）。该断言可能在某些环境误失败。建议放宽为 `pytest.raises((RecursionError, ValueError))`，或显式探测当前解释器的实际阈值。

### 3.4【可重现性】跨进程/Fuzzing 未固定种子

`test_cross_process.py`、`test_collections.py` 的 variation 检测以及 fuzzing 均未固定 `PYTHONHASHSEED`，导致每次运行的「观测结果」不可重现，也无法纳入稳定的 pass/fail 统计。建议：判定型断言固定 seed；观测型用例显式标注 `@pytest.mark.observational` 并与判定型分开统计。

---
## 4. 新增测试用例建议（更多测试用例）

下面按测试维度给出**具体、可直接落地**的新增用例。每条标注目的与建议的断言形态（判定型 assert / 观测型 record）。

### 4.1 基础类型与编码边界

1. **整数符号位与零的多种表示**：`-0`（int，应等于 0）、`int.from_bytes(b"\x00"*8,"big")`、超长大整数 `2**1000`、`-(2**1000)`，验证 marshal 长整数编码（TYPE_LONG，按 15-bit digit 分块）在位宽进位处稳定。
2. **`str` 的 interning 边界**：同一字符串多次出现于一个容器，验证 v3+ 的 FLAG_REF 复用（`dumps([s, s])` 应短于 `dumps([s, s2])`，其中 s2 内容相同但为不同对象——实测 marshal 是否对相等短字符串去重）。
3. **非 ASCII / 代理对 / 组合字符**：`"\ud800"`（孤立代理，注意 surrogatepass）、`"é"` 的 NFC vs NFD 两种表示、零宽字符，验证 str 编码是否按码位稳定。
4. **`bytes` vs `bytearray` 的往返类型**（承 §2.1）：新增判定型用例
   ```python
   def test_bytearray_round_trips_to_bytes():
       r = marshal.loads(marshal.dumps(bytearray(b"abc")))
       assert type(r) is bytes          # 记录：类型不保留
       assert marshal.dumps(b"abc") == marshal.dumps(bytearray(b"abc"))  # v4 字节流相同
   ```
5. **`bool` vs `int` 的类型保持**：`marshal.loads(marshal.dumps(True))` 应仍为 `bool` 且 `is True`，区别于 `1`。
6. **`memoryview` / `array.array`**：验证是否落入 UNSUPPORTED（预期 ValueError），补足负测试。

### 4.2 浮点与复数

7. **subnormal（非规格化）浮点全扫**：`5e-324`（最小正 subnormal）、`float.fromhex('0x0.0000000000001p-1022')`，验证最小步长处往返精度。
8. **NaN 的位模式保持**：`struct` 构造不同 payload 的 NaN（quiet/signaling、不同尾数），验证 marshal 是否逐位保留 NaN 载荷，还是规范化为单一 NaN。这是「相同语义、不同字节」的经典案例。
9. **复数的 -0.0 分量**：`complex(-0.0, -0.0)` vs `complex(0.0, 0.0)`，验证分量级别的零符号是否进入字节流。

### 4.3 容器与共享引用

10. **DAG（菱形共享）**：`shared=[1]; obj=[shared, shared]`，验证反序列化后 `r[0] is r[1]`（共享被保留），并对比 `obj2=[[1],[1]]`（不共享）字节流更长。
11. **dict 插入顺序敏感性**：`{"a":1,"b":2}` vs `{"b":2,"a":1}`，验证 marshal 按插入顺序序列化（字节流应不同），这是「值相等但字节不同」的确定性案例，适合判定型断言。
12. **frozenset 作为 dict key / set 成员**：验证嵌套可哈希容器的稳定性。
13. **超大容器长度字段边界**：list 长度 `2**16-1, 2**16, 2**32-1`（注意内存，用 `[0]*n` 谨慎取样），验证长度字段编码进位。

### 4.4 代码对象（白盒）

14. **同源重复编译的字节级一致性**：用 `compile(同一源码)` 两次得到两个 code object，验证 `marshal.dumps` 是否字节相同（探测 code object 是否含 id/地址相关的非确定字段）。
15. **`co_filename` / `co_firstlineno` 敏感性**：相同函数体、不同文件名或行号，验证这些字段如何进入字节流（解释为什么「同一份逻辑」跨文件不可复现）。
16. **嵌套 code object（含闭包/内层函数）**：验证 `co_consts` 中嵌套 code 的递归序列化稳定性。
17. **`PYTHONDONTWRITEBYTECODE` / `-O` 优化级别**：在 `-O`、`-OO` 下编译（去除断言/文档串），验证 code object 字节流随优化级别变化——一个常被忽视的「相同源码不同输出」来源。
18. **跨次解释器启动的 code 稳定性**：子进程中 `compile` 同一源码并比较 hash，区分「进程内稳定」与「跨进程稳定」（代码对象本身不应受 hashseed 影响，可作为对照组）。

### 4.5 负测试补全（与文档对齐）

19. 把原报告 §3.6 宣称的 5 类全部写入 `UNSUPPORTED_CASES` 并各加判定型断言（均预期 `ValueError`）：
   ```python
   import io, socket
   class _Custom: pass
   UNSUPPORTED_CASES += [
       _Custom(),                    # 自定义类实例
       io.StringIO("x"),             # 文件类对象
       socket.socket(),              # socket
       (i for i in range(3)),        # 生成器
       iter([1,2,3]),                # 迭代器
   ]
   ```
20. **「部分不支持」容器**：`[1, object()]`——验证当容器中混入不支持元素时，是否在写入途中抛错（以及已写入部分是否产生副作用）。

### 4.6 跨进程 / 跨版本 / 跨平台

21. **固定 seed 的可重现对照**：同一字符串集合，在 `PYTHONHASHSEED=0` 下跨进程多次运行，验证「固定 seed ⇒ 输出一致」（把发现 2 从「观测」升级为「可判定」）。
22. **整数集合作为 hashseed 不敏感对照**：跨多个 seed 验证 `{1,2,3}` 字节流恒定，与字符串集合形成对照实验。
23. **真实跨版本反序列化矩阵**：用子进程在 3.8/3.9/3.10/3.11/3.12 分别 `dumps` 同一基础对象，交叉 `loads`，构建 NxN 兼容性矩阵（区分「基础类型」全通过 vs「代码对象」跨版本失败）。
24. **marshal 版本显式矩阵**：对每个支持类型，遍历 `version=0..4` 各自 `dumps`，断言「同版本稳定、跨版本可不同」，把发现 1 落成结构化数据而非散述。

### 4.7 Fuzzing 增强

25. **差分 Fuzzing（往返不变式）**：对 Hypothesis 生成值断言 `loads(dumps(x))` 等价于 `x`（已有），**额外**断言 `dumps(loads(dumps(x))) == dumps(x)`（幂等性/规范形），能捕捉「往返语义相等但字节漂移」的隐性 bug。
26. **更深嵌套 + 收缩报告**：把 `max_depth` 提升并依赖 Hypothesis 的 shrinking 给出最小反例；当前 deadline=None 已合理。
27. **针对 set/dict 的 stateful 测试**：用 `hypothesis.stateful` 随机增删元素后比较序列化，探测顺序相关的非确定性。

---
## 5. 更新后的关键发现（修订版结论）

1. **进程内确定性成立**：所有 marshal 支持类型在同一进程内重复 `dumps` 字节一致（实测 + 现有用例支持）。
2. **跨进程不确定性来自 `PYTHONHASHSEED`**：仅影响含字符串元素的 set/frozenset/由 set 构造的 dict；整数集合不受影响。这是「预期内的不稳定」，应记录而非判失败。
3. **代码对象不可跨版本/跨平台/跨优化级别复用**：依赖字节码版本、`co_filename`、`co_firstlineno`、优化级别等。
4. **bytes 与 bytearray（更正）**：在 marshal v4 下两者序列化字节流**相同**，且 **bytearray 往返后退化为 bytes（类型不保留）**。原报告关于类型码 'B'/'y' 的描述不成立。
5. **共享引用与特殊浮点值处理正确**：FLAG_REF 保留共享；NaN/Inf/-0.0 正确往返，0.0 与 -0.0 字节不同。
6. **marshal 版本差异成立**：v0/1/2 与 v3/v4 的字符串/字节编码不同（FLAG_REF/interning 引入）。

### 5.1 稳定性问题汇总（修订）

| 问题 | 影响范围 | 严重度 | 根因 | 与原报告差异 |
| --- | --- | --- | --- | --- |
| marshal 版本差异 | 全类型 | 高 | 格式设计 | 不变 |
| 跨进程集合顺序 | 含 str 的 set/dict | 中 | PYTHONHASHSEED | 改为「观测型」，不计 failed |
| 代码对象版本/平台/优化敏感 | code object | 高 | 字节码与编译环境 | 补充「优化级别」维度 |
| **bytearray 类型不保留** | bytearray | 中 | marshal 不存类型，退化为 bytes | **新增/更正**（替换原错误的类型码描述）|

---

## 6. Limitations（在原报告基础上补充）

1. 本次审阅的行为核验在 **Python 3.10.0a6（alpha）** 上以直接调用 marshal 完成，未经 pytest 全量运行（本机 pytest 与该 alpha 解释器不兼容）。结论中涉及具体字节的部分已逐条实测，但**完整 pytest 通过率需在稳定版解释器上重跑**。
2. 统计数字的权威来源仍缺失：建议补一次「全量 + 单环境 + 固定 PYTHONHASHSEED」的 pytest 运行，作为报告唯一引用的数字。
3. 跨版本/跨平台目前依赖手工收集的结果文件（仅 win32/3.8.6 与 darwin/3.10.0a6 两份），样本不足以支撑「矩阵」级结论。

## 7. Conclusion

`marshal` 在**进程内**对所有支持类型是确定性的；不确定性集中在三处可解释的来源：marshal 格式版本、`PYTHONHASHSEED`（仅影响字符串集合顺序）、以及代码对象对编译环境的依赖。原报告的整体方向正确，但存在**一处事实性错误（发现 4 的类型码）**、**一处测试代码缺陷（游离语句丢失覆盖）**、以及**统计数字三方不一致**。本改进版已逐条更正，并给出 27 条可落地的新增用例与可重现性改进建议。

### 生产环境建议

- 需要跨进程/跨版本确定性时，避免序列化含字符串的 set/dict；如必须，固定 `PYTHONHASHSEED`。
- 不要把 code object 跨 Python 版本或跨优化级别持久化。
- 不要依赖 marshal 保留 `bytearray` 类型——它会退化为 `bytes`。

---

## 附录 A. 本次审阅的可复现核验脚本

```python
import marshal
# 发现4更正
assert marshal.dumps(b"abc") == marshal.dumps(bytearray(b"abc"))   # v4 字节流相同
assert type(marshal.loads(marshal.dumps(bytearray(b"abc")))) is bytes  # 类型退化
assert marshal.dumps(b"abc")[0] == 0xf3                            # 's'|FLAG_REF，非 'B'/'y'
# 发现7
assert marshal.dumps(0.0) != marshal.dumps(-0.0)
# 负测试真实行为
for x in (object(), lambda x:x):
    try: marshal.dumps(x); raise SystemExit("should fail")
    except ValueError: pass
```

## 附录 B. 与原报告的对应关系

本改进版**新增/修改**：§0 审阅摘要、§1.3 统计对账、§2 发现逐条核验、§3 测试代码缺陷、§4 新增 27 条用例、§5 修订结论。原报告 `final_report_draft.md` 全文保留未删改，作为对照基线。
