# {{paper_title}}

> 📄 **论文信息**
> - **标题：** {{paper_title}}
> - **作者：** {{authors}}
> - **发表：** {{venue}} {{year}}
> - **链接：** [论文原文]({{paper_url}}) | [代码仓库]({{repo_url}})
> - **阅读深度：** 🔬 完整阅读
> - **生成时间：** {{generated_date}}

---

## 📑 目录

<!-- INSTRUCTION: 自动根据实际生成的章节生成目录，使用 Markdown 锚链接 -->
1. [论文概览](#论文概览)
2. [逐章详解](#逐章详解)
3. [全部图解](#全部图解)
4. [全部公式](#全部公式)
5. [代码深度分析](#代码深度分析)
6. [完整复现指南](#完整复现指南)
7. [批判性评价](#批判性评价)
8. [延伸阅读](#延伸阅读)

---

## 论文概览

### 一句话概括
{{one_sentence_summary}}

### 研究背景与动机
<!-- INSTRUCTION: 写 3 到 4 段，包含该研究方向的发展脉络，关键里程碑工作，现实需求或痛点。避免空泛口号，要能解释清楚“为什么现在要做这件事”。 -->
{{background_and_motivation_3to4_paragraphs}}

### 研究问题定义
<!-- INSTRUCTION: 用读者能听懂的话明确：输入是什么，输出是什么，目标是什么，约束是什么。 -->
- **任务/问题：** {{problem_statement}}
- **输入：** {{problem_inputs}}
- **输出：** {{problem_outputs}}
- **评价指标：** {{primary_metrics}}
- **关键假设与约束：** {{assumptions_and_constraints}}

### 核心贡献
<!-- INSTRUCTION: 列出论文明确声明的全部贡献，数量不限。每条贡献写“做了什么”和“为什么重要”。 -->
{{contributions_full_bullets}}

### 与前人工作的关系
<!-- INSTRUCTION: 写一个小型文献综述，说明本文填补的缺口，以及相对现有方法的差异点与取舍。 -->

#### 相关工作快速对照
| 代表工作 | 核心想法 | 局限/缺口 | 本文如何不同 |
|---------|----------|-----------|-------------|
| {{prior_work_1_cite}} | {{prior_work_1_idea}} | {{prior_work_1_gap}} | {{this_work_diff_1}} |
| {{prior_work_2_cite}} | {{prior_work_2_idea}} | {{prior_work_2_gap}} | {{this_work_diff_2}} |
<!-- INSTRUCTION: 按需要补充更多行，覆盖论文讨论或隐含依赖的重要前置工作。 -->

#### 本文的定位与叙事
{{positioning_narrative}}

### 关键术语与符号表
<!-- INSTRUCTION: 汇总全文频繁出现的术语与符号，便于后文逐章阅读。符号含义要与“全部公式”一致。 -->
| 术语/符号 | 含义 | 一句话解释 | 首次出现位置 |
|-----------|------|------------|--------------|
| {{term_or_symbol_1}} | {{term_or_symbol_1_meaning}} | {{term_or_symbol_1_plain}} | {{term_or_symbol_1_first_seen}} |
| {{term_or_symbol_2}} | {{term_or_symbol_2_meaning}} | {{term_or_symbol_2_plain}} | {{term_or_symbol_2_first_seen}} |
| {{term_or_symbol_3}} | {{term_or_symbol_3_meaning}} | {{term_or_symbol_3_plain}} | {{term_or_symbol_3_first_seen}} |
<!-- INSTRUCTION: 按需要补充更多术语/符号。 -->

### 全文路线图
<!-- INSTRUCTION: 用 6 到 10 句话描述论文从问题到方法到实验到结论的逻辑链条。 -->
{{paper_roadmap}}

---

## 📖 逐章详解

<!-- INSTRUCTION: 按论文原文的章节顺序，逐章逐节解读。每一章都要用通俗语言重述，让零基础读者也能理解 -->
<!-- INSTRUCTION: 使用 sections.json 获取论文的章节结构 -->
<!-- INSTRUCTION: 如果这一章包含图表或公式，在对应位置插入批注（不要集中放在后面）。图解与公式批注格式严格参考 annotation-guide.md -->

### {{section_number}} {{section_title}}

<!-- INSTRUCTION: 用通俗语言重述这一章的核心内容。不是翻译，是“用自己的话讲给朋友听”。必要时用具体例子辅助理解。 -->
{{section_explanation}}

<!-- INSTRUCTION: 本节若出现关键图表或公式，请在这里就地插入对应批注块，格式见 annotation-guide.md；并写明它如何支撑本节结论。 -->

> 📌 **本章要点：** {{section_key_takeaway}}

#### 本节的关键点清单
<!-- INSTRUCTION: 只列事实与结论，不要抄原文句子。每条包含“结论”与“证据来源（图/表/公式/实验）”。 -->
{{section_key_points_with_evidence}}

#### 容易误解的点
<!-- INSTRUCTION: 列出读者最可能误解的点，并给出纠正方式。 -->
{{section_common_misunderstandings_and_fixes}}

<!-- INSTRUCTION: 重复以上模板，覆盖论文中的每一节（包括引言、相关工作、方法、实验、讨论、结论、附录）。 -->

---

## 📊 全部图解

<!-- INSTRUCTION: 论文中的每一张图、每一张表都必须在这里出现并批注。不允许遗漏任何图表 -->
<!-- INSTRUCTION: 每张图都必须严格按 annotation-guide.md 的图解批注模板格式 -->
<!-- INSTRUCTION: 对于特殊图表类型（架构图、对比表、消融实验表、训练曲线），参考 annotation-guide.md 的特殊情况处理 -->

### 图 {{figure_number}}: {{figure_caption}}

![{{figure_caption}}](./images/{{figure_filename}})

> 🔍 **图解批注**
> 
> **这张图在说什么？** {{figure_explanation}}
> 
> **关键要素：**
> - {{figure_element_1_name}}: {{figure_element_1_explanation}}
> - {{figure_element_2_name}}: {{figure_element_2_explanation}}
> - {{figure_element_3_name}}: {{figure_element_3_explanation}}
>
> **读图顺序：** {{figure_reading_order}}
>
> **为什么重要？** {{figure_importance}}
>
> **与其他图的关系：** {{figure_cross_reference}}
>
> 💡 **一句话记住：** {{figure_takeaway}}

<!-- INSTRUCTION: 重复以上模板，为论文中的每一张图和每一张表都生成批注。表格若没有图片，也要用文字复刻核心数据，并解释每一列含义与单位。 -->

---

## 📐 全部公式

<!-- INSTRUCTION: 论文中的每一个公式都必须在这里出现并批注。不允许遗漏 -->
<!-- INSTRUCTION: 每个公式都必须严格按 annotation-guide.md 的公式批注模板，包含完整的逐符号拆解表格 -->

### 公式 {{formula_number}}: {{formula_name}}

$${{formula_latex}}$$

> 🔍 **公式批注**
> 
> **这个公式在算什么？** {{formula_explanation}}
>
> **逐符号拆解：**
> | 符号 | 含义 | 通俗理解 | 取值范围/形状 |
> |------|------|----------|---------------|
> | ${{symbol_1}}$ | {{symbol_1_meaning}} | {{symbol_1_plain}} | {{symbol_1_shape}} |
> | ${{symbol_2}}$ | {{symbol_2_meaning}} | {{symbol_2_plain}} | {{symbol_2_shape}} |
> | ${{symbol_3}}$ | {{symbol_3_meaning}} | {{symbol_3_plain}} | {{symbol_3_shape}} |
>
> **推导过程：**
> <!-- INSTRUCTION: 如果公式有推导过程，用通俗语言一步步解释。每步都要说“为什么这样变换”。如果论文未给出完整推导，也要说明缺失点并给出合理补全。 -->
> {{derivation_steps}}
>
> **直觉理解：** {{formula_intuition}}
>
> **与其他公式的关系：** {{formula_cross_reference}}
>
> 🗣️ **一句话总结：** {{formula_takeaway}}

<!-- INSTRUCTION: 重复以上模板，为论文中的每一个公式都生成批注。若论文中存在未编号的关键等式或定义，也要纳入并给出编号策略。 -->

---

## 💻 代码深度分析

### 仓库概况
<!-- INSTRUCTION: 若无代码仓库，也必须说明缺失，并给出可复现的替代实现建议与风险。 -->
- **仓库链接：** {{repo_url}}
- **提交信息：** {{repo_commit_ref}}
- **主要语言：** {{repo_primary_languages}}
- **许可协议：** {{repo_license}}
- **可运行入口概览：** {{repo_entrypoints_overview}}

### 完整项目结构
<!-- INSTRUCTION: 生成完整目录树，包含关键子目录与关键文件，不要只列顶层。 -->
```
{{full_structure_tree}}
```

### 论文↔代码完整映射
<!-- INSTRUCTION: 每一个论文中提到的方法、模块、算法都要映射到代码，覆盖“方法细节”与“实验设置”。 -->
| 论文章节 | 论文内容 | 代码文件 | 代码函数/类 | 说明 |
|----------|----------|----------|-------------|------|
| {{paper_section_id_1}} | {{paper_component_1}} | `{{code_file_1}}` | `{{code_symbol_1}}` | {{mapping_desc_1}} |
<!-- INSTRUCTION: 按论文所有模块扩展此表，直到覆盖完。 -->

### 核心模块逐行解读
<!-- INSTRUCTION: 对最核心的 2 到 3 个代码文件，给出关键代码段的逐行注释。必须包含行号，并解释关键分支，张量形状变化，损失项计算，日志记录与保存逻辑。 -->

#### {{module_1_name}} (`{{module_1_file}}`)
- **功能概述：** {{module_1_purpose}}
- **与论文对应：** {{module_1_paper_link}}
```{{module_1_language}}
{{module_1_code_block_with_line_numbers}}
```
> 📝 **逐行解读：**
> - **第 {{module_1_range_1_start}} 到 {{module_1_range_1_end}} 行：** {{module_1_range_1_explanation}}
> - **第 {{module_1_range_2_start}} 到 {{module_1_range_2_end}} 行：** {{module_1_range_2_explanation}}
> - **第 {{module_1_range_3_start}} 到 {{module_1_range_3_end}} 行：** {{module_1_range_3_explanation}}
- **关键边界情况：** {{module_1_edge_cases}}
- **容易踩坑的实现细节：** {{module_1_gotchas}}

#### {{module_2_name}} (`{{module_2_file}}`)
- **功能概述：** {{module_2_purpose}}
- **与论文对应：** {{module_2_paper_link}}
```{{module_2_language}}
{{module_2_code_block_with_line_numbers}}
```
> 📝 **逐行解读：**
> - **第 {{module_2_range_1_start}} 到 {{module_2_range_1_end}} 行：** {{module_2_range_1_explanation}}
> - **第 {{module_2_range_2_start}} 到 {{module_2_range_2_end}} 行：** {{module_2_range_2_explanation}}
- **关键边界情况：** {{module_2_edge_cases}}
- **容易踩坑的实现细节：** {{module_2_gotchas}}

<!-- INSTRUCTION: 如需第 3 个核心文件，复制以上模块并命名为 module_3，并保持行号解释粒度一致。 -->

### 数据流分析
<!-- INSTRUCTION: 从输入到输出，追踪数据如何在代码中流动。用简洁的文本图或 Mermaid 展示关键节点。 -->
```text
{{data_flow_diagram}}
```
{{data_flow_explanation}}

### 依赖关系分析
<!-- INSTRUCTION: 列出所有外部依赖，说明各自的作用。若仓库同时有 Python 与 JS 依赖，分别列出。 -->
| 依赖包 | 版本 | 用途 |
|--------|------|------|
| {{dep_name_1}} | {{dep_version_1}} | {{dep_purpose_1}} |
<!-- INSTRUCTION: 按需要补充更多依赖，并注明是否影响复现（例如 CUDA 版本绑定）。 -->

---

## 🔧 完整复现指南

### 硬件要求
{{hardware_requirements}}

### 环境配置
```bash
{{environment_setup_commands}}
```

### 数据准备
{{data_preparation_steps}}

### 训练步骤
```bash
{{training_commands}}
```

### 评估步骤
```bash
{{evaluation_commands}}
```

### 预期输出
<!-- INSTRUCTION: 描述成功复现后应该看到的输出和指标，给出数值范围或表格。 -->
{{expected_outputs}}

### 复现检查清单
- [ ] {{checklist_item_1}}
- [ ] {{checklist_item_2}}
- [ ] {{checklist_item_3}}
- [ ] {{checklist_item_4}}
- [ ] {{checklist_item_5}}
<!-- INSTRUCTION: 按需要补充更多检查项，保持每项可验证。 -->

### 常见问题与排错
| 问题 | 原因 | 解决方案 |
|------|------|----------|
| {{issue_1}} | {{cause_1}} | {{solution_1}} |
| {{issue_2}} | {{cause_2}} | {{solution_2}} |
| {{issue_3}} | {{cause_3}} | {{solution_3}} |

---

## 🎯 批判性评价

### 论文优势
{{strengths_detailed}}

### 论文局限
{{limitations_detailed}}

### 方法论评价
<!-- INSTRUCTION: 评价实验设计是否合理、对比是否公平、结论是否有力支撑。 -->
{{methodology_evaluation}}

### 适用场景与不适用场景
{{use_cases_and_limitations}}

### 未来方向
<!-- INSTRUCTION: 基于论文的局限性，提出可能的改进方向。 -->
{{future_directions}}

---

## 📚 延伸阅读

### 前置知识
<!-- INSTRUCTION: 如果读者想更好地理解这篇论文，应该先读哪些材料 -->
{{prerequisite_readings}}

### 相关论文
{{related_papers}}

### 后续工作
<!-- INSTRUCTION: 引用了这篇论文的重要后续工作 -->
{{follow_up_work}}

---

> 📝 本报告由 paper-reader 自动生成 | 阅读深度：🔬 完整阅读
> 本报告覆盖了论文的所有章节、图表、公式，并提供了代码逐行分析。
