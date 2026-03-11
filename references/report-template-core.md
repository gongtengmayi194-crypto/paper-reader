# {{paper_title}}

> 📄 **论文信息**
> - **标题：** {{paper_title}}
> - **作者：** {{authors}}
> - **发表：** {{venue}} {{year}}
> - **链接：** [论文原文]({{paper_url}}) | [代码仓库]({{repo_url}})
> - **阅读深度：** 📖 核心阅读

---

## 💡 论文概览

### 一句话概括
{{one_sentence_summary}}

### 研究背景与动机
<!-- INSTRUCTION: 用 2-3 段话解释：这篇论文要解决什么问题？为什么之前的方法不够好？作者的核心洞察是什么？ -->
<!-- INSTRUCTION: 使用类比让非专业读者理解问题的重要性 -->
{{background_and_motivation}}

### 核心贡献
1. **{{contribution_1_title}}：** {{contribution_1_desc}}
2. **{{contribution_2_title}}：** {{contribution_2_desc}}
3. **{{contribution_3_title}}：** {{contribution_3_desc}}

---

## 🔬 方法详解

<!-- INSTRUCTION: 这是报告的核心部分。按论文的方法章节结构，用通俗语言解释每个关键步骤 -->
<!-- INSTRUCTION: 每个子步骤都要有类比，让读者理解"为什么这样做" -->

### {{method_step_1_title}}
{{method_step_1_explanation}}

### {{method_step_2_title}}
{{method_step_2_explanation}}

<!-- INSTRUCTION: 根据论文实际内容添加更多子步骤 -->

---

## 📊 关键图解

<!-- INSTRUCTION: 标注论文中所有关键图表。至少包括：方法概览图、核心架构图、实验结果图 -->
<!-- INSTRUCTION: 每张图都必须按 annotation-guide.md 的图解批注模板格式批注 -->

### 图 {{figure_number}}: {{figure_caption}}

![{{figure_caption}}](./images/{{figure_filename}})

> 🔍 **图解批注**
> 
> **这张图在说什么？** {{figure_explanation}}
> 
> **关键要素：**
> - {{element_1}}: {{element_1_explanation}}
> - {{element_2}}: {{element_2_explanation}}
> - {{element_3}}: {{element_3_explanation}}
>
> **为什么重要？** {{figure_importance}}
>
> 💡 **一句话记住：** {{figure_takeaway}}

<!-- INSTRUCTION: 重复以上模板，为每张关键图都生成批注 -->

---

## 📐 核心公式

<!-- INSTRUCTION: 标注论文中所有核心公式。每个公式都必须按 annotation-guide.md 的公式批注模板格式批注 -->
<!-- INSTRUCTION: 每个公式必须有逐符号拆解表格 -->

### 公式 {{formula_number}}: {{formula_name}}

$${{formula_latex}}$$

> 🔍 **公式批注**
> 
> **这个公式在算什么？** {{formula_explanation}}
>
> **逐符号拆解：**
> | 符号 | 含义 | 通俗理解 |
> |------|------|----------|
> | ${{symbol_1}}$ | {{symbol_1_meaning}} | {{symbol_1_plain}} |
> | ${{symbol_2}}$ | {{symbol_2_meaning}} | {{symbol_2_plain}} |
>
> 🗣️ **一句话总结：** {{formula_takeaway}}

<!-- INSTRUCTION: 重复以上模板，为每个核心公式都生成批注 -->

---

## 📈 实验结果

<!-- INSTRUCTION: 总结论文的主要实验结果。解释每个指标是什么意思（用通俗语言），结果说明了什么 -->

### 主要结果
{{main_results_summary}}

### 关键发现
<!-- INSTRUCTION: 列出 3-5 个最重要的实验发现，每个用通俗语言解释含义 -->
1. {{finding_1}}
2. {{finding_2}}
3. {{finding_3}}

---

## 💻 代码仓库分析

<!-- INSTRUCTION: 如果找到了代码仓库，提供详细分析 -->

### 仓库概况
- **仓库：** [{{repo_name}}]({{repo_url}})
- **语言：** {{primary_language}} ({{language_percentage}})
- **框架：** {{framework}}
- **星标：** {{stars}} ⭐

### 项目结构
```
{{structure_tree}}
```

### 论文↔代码映射
<!-- INSTRUCTION: 将论文中的方法/模块映射到具体的代码文件和函数 -->
| 论文内容 | 代码位置 | 说明 |
|----------|----------|------|
| {{paper_component_1}} | `{{code_file_1}}` | {{mapping_desc_1}} |
| {{paper_component_2}} | `{{code_file_2}}` | {{mapping_desc_2}} |

### 核心代码片段
<!-- INSTRUCTION: 展示 2-3 个最关键的代码片段，并用通俗语言解释每段代码在做什么 -->

**{{code_snippet_1_title}}** (`{{code_snippet_1_file}}`)
```{{language}}
{{code_snippet_1}}
```
> 📝 **代码解读：** {{code_snippet_1_explanation}}

---

## 🔧 复现指南

### 环境要求
{{environment_requirements}}

### 复现步骤
```bash
{{reproduce_commands}}
```

### 复现检查清单
- [ ] {{checklist_item_1}}
- [ ] {{checklist_item_2}}
- [ ] {{checklist_item_3}}
- [ ] {{checklist_item_4}}

### 常见问题
<!-- INSTRUCTION: 如果在代码分析中发现了潜在的坑，列在这里 -->
- **{{issue_1}}：** {{solution_1}}

---

## 🎯 总结与评价

### 论文优势
{{strengths}}

### 论文局限
{{limitations}}

### 适用场景
<!-- INSTRUCTION: 什么时候该用这篇论文的方法，什么时候不该用 -->
{{use_cases}}

---

> 📝 本报告由 paper-reader 自动生成 | 阅读深度：📖 核心阅读
> 如需逐章逐节的完整分析，请使用 `full` 深度重新生成。