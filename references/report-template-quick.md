# {{paper_title}}

> 📄 **论文信息**
> - **标题：** {{paper_title}}
> - **作者：** {{authors}}
> - **发表：** {{venue}} {{year}}
> - **链接：** [论文原文]({{paper_url}}) | [代码仓库]({{repo_url}})
> - **阅读深度：** ⚡ 快速阅读

---

<!-- INSTRUCTION: 用一句话说清楚这篇论文做了什么、为什么重要。参考 annotation-guide.md 的 "一句话概括" 规则：聚焦核心创新，避免细节。 -->

## 💡 一句话概括

{{one_sentence_summary}}

<!-- INSTRUCTION: 列出 2-3 个最重要的贡献点，每个用一句话解释。参考 annotation-guide.md 的 "核心贡献" 规则：区分技术贡献与实验贡献。 -->

## 🎯 核心贡献

1. **{{contribution_1_title}}：** {{contribution_1_desc}}
2. **{{contribution_2_title}}：** {{contribution_2_desc}}
3. **{{contribution_3_title}}：** {{contribution_3_desc}}

<!-- INSTRUCTION: 选择论文中最重要的一张图（通常是方法概览图/架构图），按 annotation-guide.md 格式批注。快速模式只批注一张图。 -->

## 📊 关键图解

![{{figure_caption}}](./images/{{figure_filename}})

> 🔍 **图解批注**
> 
> **这张图在说什么？** {{figure_explanation}}
> 
> **关键要素：**
> - {{element_1}}: {{element_1_explanation}}
> - {{element_2}}: {{element_2_explanation}}
>
> 💡 **一句话记住：** {{figure_takeaway}}

<!-- INSTRUCTION: 如果论文有一个定义性的核心公式，在这里展示并批注。如果论文不以公式为核心，可以跳过此节。 -->

## 📐 核心公式

<!-- 如果论文有一个定义性的核心公式，取消注释并填写 -->
<!--
$${{core_formula_latex}}$$

> 🔍 **公式批注**
> 
> **这个公式在算什么？** {{formula_explanation}}
>
> 🗣️ **一句话总结：** {{formula_takeaway}}
-->

<!-- INSTRUCTION: 如果找到了代码仓库，展示核心信息。如果没找到，提供搜索建议。 -->

## 💻 代码速览

<!-- 如果找到了代码仓库，取消注释并填写 -->
<!--
- **仓库：** [{{repo_name}}]({{repo_url}})
- **语言：** {{primary_language}}
- **核心文件：** `{{core_file_1}}`, `{{core_file_2}}`

### 快速复现
```bash
{{reproduce_commands}}
```
-->

<!-- 如果没找到代码仓库，取消注释并填写 -->
<!--
> ⚠️ 未找到官方代码实现。可在 GitHub 搜索关键词：`{{search_keywords}}`
-->

<!-- INSTRUCTION: 列出 2-3 篇相关论文或资源，帮助读者深入。可选，如果时间有限可跳过。 -->

## 📚 延伸阅读

<!-- 可选，取消注释并填写 -->
<!--
- {{related_1}}
- {{related_2}}
-->

---

> 📝 本报告由 paper-reader 自动生成 | 阅读深度：⚡ 快速阅读
> 如需更详细的分析，请使用 `core` 或 `full` 深度重新生成。