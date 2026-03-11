# {{paper_title}} — 理解度测试

> 🎯 **测试说明**
> - **论文：** {{paper_title}}
> - **题目数量：** {{question_count}}（quick: 5题 / core: 10题 / full: 15-20题）
> - **题型分布：** 概念理解 40% | 流程追踪 30% | 代码定位 20% | 对比分析 10%
> - **使用方法：** 先独立作答，再对照参考答案；重点检查"答案出处"是否真正理解

---

## 第一类：概念理解题（40%）

<!-- INSTRUCTION: 出题要求——必须需要真正理解论文设计动机才能回答，不能从论文直接摘抄，要求读者用自己的话解释 -->

### 题目 1

**问题：** {{concept_q1}}

示例格式：
> 论文使用 concat（通道拼接）而非 add（逐元素相加）来融合 RGB 和红外特征，请解释这个设计选择背后的理由，以及在什么场景下 add 会是更好的选择？

**参考答案：** {{concept_q1_answer}}

**答案出处：**
- 论文章节：{{concept_q1_paper_ref}}
- 关键图表：{{concept_q1_figure_ref}}

**评分标准：**
- [ ] {{concept_q1_criterion_1}}
- [ ] {{concept_q1_criterion_2}}
- [ ] {{concept_q1_criterion_3}}

<!-- INSTRUCTION: 出 4 道概念理解题（full 模式），每题覆盖论文不同核心设计点 -->

---

## 第二类：流程追踪题（30%）

<!-- INSTRUCTION: 出题要求——要求读者完整描述数据从输入到输出的流程，必须包含张量形状变化 -->

### 题目 {{concept_count + 1}}

**问题：** {{flow_q1}}

示例格式：
> 请详细描述一张 RGB 图像（224×224×3）从网络输入，经过双分支编码器，到达第一个特征融合层的完整流程。要求说明每个操作的名称、参数和输出形状。

**参考答案：** {{flow_q1_answer}}

**答案出处：**
- 论文章节：{{flow_q1_paper_ref}}
- 代码文件：{{flow_q1_code_ref}}

**评分标准：**
- [ ] {{flow_q1_criterion_1}}
- [ ] {{flow_q1_criterion_2}}

<!-- INSTRUCTION: 出 3 道流程追踪题（full 模式） -->

---

## 第三类：代码定位题（20%）

<!-- INSTRUCTION: 出题要求——要求读者找到论文某个概念对应的代码位置，测试论文↔代码映射理解 -->

### 题目 {{concept_count + flow_count + 1}}

**问题：** {{code_q1}}

示例格式：
> 论文 3.3 节提到"跨模态注意力权重"的计算，请找出代码中实现这个计算的具体函数名、文件路径和关键行号范围。

**参考答案：**
- 文件：`{{code_q1_file}}`
- 函数/类：`{{code_q1_symbol}}`
- 行号范围：{{code_q1_lines}}
- 说明：{{code_q1_explanation}}

**答案出处：**
- code-modules/: {{code_q1_module_file}}

**评分标准：**
- [ ] {{code_q1_criterion_1}}
- [ ] {{code_q1_criterion_2}}

<!-- INSTRUCTION: 出 2 道代码定位题（full 模式） -->

---

## 第四类：对比分析题（10%）

<!-- INSTRUCTION: 出题要求——要求读者对比本文方法与论文中提到的 baseline 或相关工作 -->

### 题目 {{concept_count + flow_count + code_count + 1}}

**问题：** {{compare_q1}}

示例格式：
> 论文在 Related Work 中提到了方法 X（cite），请从网络结构、融合策略、计算复杂度三个角度，对比本文方法与方法 X 的核心差异，并解释为什么本文的改进是有意义的。

**参考答案：** {{compare_q1_answer}}

**答案出处：**
- 论文章节：{{compare_q1_paper_ref}}
- 相关图表：{{compare_q1_figure_ref}}

**评分标准：**
- [ ] {{compare_q1_criterion_1}}
- [ ] {{compare_q1_criterion_2}}

<!-- INSTRUCTION: 出 1 道对比分析题（full 模式） -->

---

## 答题完成检查

完成所有题目后，对照以下清单评估自己的理解程度：

- [ ] 我能用自己的话解释本文的核心创新点
- [ ] 我能完整描述数据从输入到输出的流程（含形状）
- [ ] 我能在代码中找到论文中每个关键模块的对应位置
- [ ] 我能解释本文相对前人工作的改进和局限

**若以上有打叉的条目，建议回到对应章节重读。**

---

> 📝 由 paper-reader 生成 | 理解度测试
