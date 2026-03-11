# {{paper_title}} — 论文深度解读

> 📄 **论文信息**
> - **标题：** {{paper_title}}
> - **作者：** {{authors}}
> - **发表：** {{venue}} {{year}}
> - **链接：** [论文原文]({{paper_url}}) | [代码仓库]({{repo_url}})
> - **阅读深度：** 🔬 逐层张量追踪（极致详细）
> - **生成时间：** {{generated_date}}

---

## 📑 目录

<!-- INSTRUCTION: 根据实际论文章节自动生成目录 -->
1. [论文概览](#论文概览)
2. [逐章精讲](#逐章精讲)
3. [批判性评价](#批判性评价)
4. [延伸阅读](#延伸阅读)

---

## 论文概览

### 一句话概括
{{one_sentence_summary}}

### 研究背景与动机
<!-- INSTRUCTION: 写 3-4 段，包含研究方向发展脉络、关键里程碑工作、现实需求或痛点。解释清楚"为什么现在要做这件事"。 -->
{{background_and_motivation}}

### 研究问题定义
- **任务/问题：** {{problem_statement}}
- **输入：** {{problem_inputs}}
- **输出：** {{problem_outputs}}
- **评价指标：** {{primary_metrics}}
- **关键假设与约束：** {{assumptions_and_constraints}}

### 核心贡献
<!-- INSTRUCTION: 列出论文全部贡献，每条说明"做了什么"和"为什么重要"。 -->
{{contributions}}

### 与前人工作的关系

| 代表工作 | 核心想法 | 局限/缺口 | 本文如何不同 |
|---------|----------|-----------|-------------|
| {{prior_work_1}} | {{prior_work_1_idea}} | {{prior_work_1_gap}} | {{this_work_diff_1}} |
<!-- INSTRUCTION: 按需补充更多行 -->

### 关键术语与符号表

| 术语/符号 | 含义 | 一句话解释 |
|-----------|------|------------|
| {{term_1}} | {{term_1_meaning}} | {{term_1_plain}} |
<!-- INSTRUCTION: 按需补充 -->

---

## 📖 逐章精讲

<!-- INSTRUCTION: 按论文原文章节顺序，逐章逐节解读。
     - Introduction / Related Work：2-4 段通俗说明，背景、痛点、前人工作
     - Method 章节（核心）：采用"逐层张量追踪"格式（见下方模板）
     - Experiments：解读每张结果表格，说明消融实验结论
     - Conclusion：1-2 段总结
-->

### {{section_number}} {{section_title}}

<!-- INSTRUCTION: 用通俗语言重述本章。若为 Method 章节，使用下方的"架构图流程讲解"和"逐层张量追踪"格式。 -->

{{section_content}}

<!-- INSTRUCTION: 若本章有架构图，必须采用“先图后文”顺序：
     1) 先插图
     2) 紧接一行小字注释（示例：<sub>Fig.2 ConTriNet 整体架构图</sub>）
     3) 再写 🔍 图解批注
     4) 最后写模块正文与流程讲解
     不允许先用大标题写“Fig.x 批注”再放图。 -->

<!-- ===== 架构图模板（Method 章节必须使用此格式）===== -->
<!--
![{{figure_caption}}](./images/{{figure_filename}})

<sub>Fig.{{figure_number}} {{figure_short_note}}</sub>

> 🔍 **架构流程解析**
>
> **整体类比：** {{architecture_analogy}}  （例：这个系统像一个双摄像头的智能分拣机...）
>
> **逐步流程：**
>
> ① {{module_name_1}}
>    - 输入：`{{input_shape_1}}`  （例：RGB 图像 `(B, 3, 224, 224)`）
>    - 操作：{{operation_detail_1}}  （例：3×3 卷积，64 个滤波器，stride=1，padding=1）
>    - 输出：`{{output_shape_1}}`  （例：`(B, 64, 224, 224)`）
>    - 参数量：{{param_count_1}}  （例：3×64×3×3 = 1,728）
>    - 为什么这样设计：{{design_rationale_1}}
>
> ② {{module_name_2}}
>    - 输入：`{{input_shape_2}}`
>    - 操作：{{operation_detail_2}}
>    - 输出：`{{output_shape_2}}`
>    - 为什么这样设计：{{design_rationale_2}}
>
> <!-- INSTRUCTION: 每个模块都要有一个编号步骤，覆盖所有模块 -->
>
> **关键设计决策：**
> - 为什么用 concat 而非 add？→ {{answer}}
> - 为什么在这里降采样？→ {{answer}}
> <!-- INSTRUCTION: 根据架构图中的实际设计决策填写 -->
>
> **数据流向总结：**
> ```
> 输入 → 模块A → 模块B → ... → 输出
> 形状变化：X → Y → Z → ...
> ```
>
> 💡 **一句话记住：** {{architecture_takeaway}}
-->

> 📌 **本章要点：** {{section_key_takeaway}}

#### 本节关键点
<!-- INSTRUCTION: 只列事实与结论，每条含"结论"与"证据来源（图/表/公式/实验）"。 -->
{{section_key_points}}

#### 容易误解的点
{{section_common_misunderstandings}}

<!-- INSTRUCTION: 为论文每一章（含附录）复制以上模板 -->

---

## 📊 全部图表

<!-- INSTRUCTION: 每张图表在逐章讲解中就地出现后，此处做汇总索引，每条包含图号、标题、所在章节 -->

| 图号 | 标题 | 所在章节 | 核心要点 |
|------|------|----------|----------|
| 图 1 | {{fig1_title}} | {{fig1_section}} | {{fig1_takeaway}} |
<!-- INSTRUCTION: 按需补充 -->

---

## 📐 全部公式

<!-- INSTRUCTION: 论文中每个公式在逐章讲解中就地出现后，此处做汇总。
     每个公式必须包含完整的逐符号拆解表格（参考 annotation-guide.md）-->

### {{formula_name}}

<sub>公式（{{formula_number}}）</sub>

$${{formula_latex}}$$

> 🔍 **公式批注**
>
> **这个公式在算什么？** {{formula_explanation}}
>
> **逐符号拆解：**
> | 符号 | 含义 | 通俗理解 | 取值范围/形状 |
> |------|------|----------|---------------|
> | ${{sym_1}}$ | {{sym_1_meaning}} | {{sym_1_plain}} | {{sym_1_range}} |
>
> **直觉理解：** {{formula_intuition}}
>
> 🗣️ **一句话总结：** {{formula_takeaway}}

<!-- INSTRUCTION: 为每个公式复制以上模板 -->

---

## 🎯 批判性评价

### 论文优势
{{strengths}}

### 论文局限
{{limitations}}

### 方法论评价
{{methodology_evaluation}}

### 适用与不适用场景
{{use_cases}}

### 未来方向
{{future_directions}}

---

## 📚 延伸阅读

### 前置知识
{{prerequisites}}

### 相关论文
{{related_papers}}

### 后续工作
{{follow_up_work}}

---

> 📝 由 paper-reader 生成 | 阅读深度：🔬 逐层张量追踪
