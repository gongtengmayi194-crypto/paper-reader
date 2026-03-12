---
name: paper-reader
description: >
  Academic paper reading, analysis, and beginner-friendly report generation with code repository parsing.
  Use when users ask to read/analyze/summarize academic papers, research papers, or arXiv papers.
  Also triggers when users mention: 论文阅读, 论文解读, paper reading, paper analysis, 读论文, 解读论文,
  research paper summary, code repository analysis for papers, 论文复现.
  Supports PDF files, Semantic Scholar URLs, and DOI links as input.
  Automatically extracts figures and formulas from PDFs, discovers and analyzes associated GitHub repositories,
  and generates Markdown reports with inline annotations that explain every figure and formula in plain language.
---

## Overview
Read academic papers + analyze code repos + generate beginner-friendly MD reports.
- Extract figures from PDF as PNG images
- Preserve formulas in LaTeX with symbol-by-symbol annotations
- Auto-discover GitHub repos (from paper text → GitHub search → Papers With Code)
- Deep code analysis: structure, core modules, paper↔code mapping, reproduction guide
- Configurable report depth: quick / core / full
- Chinese report with English technical terms preserved

## Quick Reference
Two tables:
1. Input formats table (PDF / Semantic Scholar / DOI / GitHub repo)
2. Report depth table (quick/core/full with descriptions)

| Input format | What to provide |
| --- | --- |
| PDF | PDF file path |
| Semantic Scholar | Semantic Scholar paper URL |
| DOI | DOI link |
| GitHub repo | GitHub repository URL |

| Report depth | Description |
| --- | --- |
| quick | Quick reading: key contributions + 1-2 most important figures/formulas + minimal code mapping |
| core | Core reading: all key figures/formulas annotated + main method explained + repo structure + reproduction checklist |
| full | Full reading: every figure/formula annotated + deep line-by-line code mapping + full reproduction guide |

## Workflow

### Phase 1: Acquire Paper
- PDF → use directly
- Semantic Scholar / DOI URL → fetch metadata via firecrawl, download PDF
- Run: `python scripts/pdf_to_sections.py <pdf> <output_dir>/`

### Phase 2: Discover Code Repository
Four-level fallback:
1. Regex extract GitHub/GitLab URLs from paper text
2. GitHub search: `gh search repos "{title}" --limit 5` or firecrawl on github.com
3. Papers With Code: firecrawl scrape `https://paperswithcode.com/search?q={url_encoded_title}`
4. Mark "⚠️ 未找到官方代码实现", continue paper-only

### Phase 3: Parse Paper (parallel)
1. `python scripts/extract_figures.py <pdf> <output_dir>/images/`
2. `python scripts/extract_formulas.py <pdf> <output_dir>/`
3. sections.json already from Phase 1
After scripts: READ figure_map.json, formulas.json, sections.json.
For formulas with confidence "low" + fallback_image: use look_at tool to visually recognize LaTeX.

### Phase 4: Analyze Code Repository
1. `git clone <url> <output_dir>/repo/`
2. `python scripts/parse_repo.py <output_dir>/repo/ <output_dir>/code-analysis/`
3. Deep analysis: identify core modules, map paper↔code, annotate key functions line-by-line, extract reproduction steps

### Phase 5: Generate Reports
1. Ask user for depth (default: core) — only if not specified
2. Read `references/annotation-guide.md` (ALWAYS)
3. Read `code-analysis/modules-index.json` to know which functional modules were detected

**Report 1 — 论文深度解读.md:**
4. Read `references/report-template-paper-deep.md`
5. Assemble 论文深度解读.md:
   - Follow each section of the template
   - Figure explanation MUST be figure-first: image -> `<sub>Fig.x ...</sub>` -> annotation -> module text
   - Formula section heading must keep only semantic name; put formula number as small note (`<sub>公式（n）</sub>`)
   - For Method sections with architecture figures: use "逐步流程" format (numbered steps with tensor shapes)
   - EVERY figure in Method sections MUST have 逐步流程解析 block (not just 🔍 annotation)
   - EVERY formula MUST have 逐符号拆解 table
   - Chapters other than Method: 2-4 paragraphs, plain language

**Report 2 — code-modules/ directory:**
6. Read `references/report-template-code-module.md`
7. For each module listed in `code-analysis/modules-index.json`:
   a. Read the corresponding `code-analysis/module-{name}.json`
   b. Generate `code-modules/{index}-{module_name}.md` using template
   c. Include COMPLETE code with line numbers, line-by-line annotations, tensor shape tracking
8. Generate `code-modules/00-仓库总览与映射.md`:
   - Full directory tree from `code-analysis/structure-tree.txt`
   - Paper↔code mapping table (every paper section → code file + function)
   - Navigation links to all module files

**Report 3 — 理解度测试.md:**
9. Read `references/report-template-quiz.md`
10. Generate quiz questions:
    - quick: 5 questions (2 concept + 2 flow + 1 code)
    - core: 10 questions (4 concept + 3 flow + 2 code + 1 compare)
    - full: 15-20 questions (6 concept + 5 flow + 4 code + 2 compare)
11. Every question MUST have: reference answer, answer source (paper section + code line), scoring criteria

**Final step:**
12. Write metadata.json with paper info
13. Output everything to `{paper-name}/` directory

## Output Structure
Show the directory tree:
```
{paper-name}/
├── 论文深度解读.md          # Report 1：纯论文内容，逐层张量追踪（极致详细）
├── code-modules/            # Report 2：代码解读，按功能模块拆分
│   ├── 00-仓库总览与映射.md  # 仓库结构 + 论文↔代码映射总表
│   ├── 01-数据处理流程.md    # 按实际模块动态生成，数量不固定
│   ├── 02-模型架构详解.md
│   ├── 03-训练循环.md
│   └── ...                  # 更多模块视项目结构而定
├── 理解度测试.md            # 混合题型测验（概念/流程/代码定位/对比）
├── images/
├── code-analysis/           # 中间产物（供生成 code-modules/ 使用）
│   ├── repo-report.md
│   ├── structure-tree.txt
│   ├── key-functions.md
│   ├── modules-index.json   # 功能模块索引
│   └── module-{name}.json   # 每个功能模块的分析结果
├── metadata.json
├── figure_map.json
├── formulas.json
└── sections.json
```

## Key Rules
- CRITICAL: Every figure and formula MUST have an annotation block. No exceptions.
- CRITICAL: Annotations must be understandable by someone with ZERO technical background. Use daily-life analogies.
- CRITICAL: Never use "显然", "不难看出", "由定义可知". Use "你可以把它理解为...", "简单来说就是...", "想象一下...".
- CRITICAL: Report language = Chinese + English technical terms preserved. Format: "注意力机制（Attention Mechanism）"
- CRITICAL: All LaTeX formulas must explain every symbol. Never assume reader knows math notation.
- NEVER skip code repository search. Always attempt all fallback levels.
- NEVER generate report without running extraction scripts first.
- If a script fails, fall back to LLM-based extraction (look_at tool), note reduced accuracy.

## Dependencies
```bash
pip install "PyMuPDF>=1.23.0" "Pillow>=10.0.0"
```

## Resources
- **新报告模板（主要使用）**:
  - `references/report-template-paper-deep.md` — 论文深度解读（逐层张量追踪）
  - `references/report-template-code-module.md` — 单个代码模块解读
  - `references/report-template-quiz.md` — 理解度测试
- **深度档位说明**: `quick/core/full` 仅作为生成强度参数（控制讲解深度与出题数量），不再对应独立旧模板文件
- **标注风格指南**: `references/annotation-guide.md` (ALWAYS read this)
- **脚本**: `scripts/extract_figures.py`, `scripts/extract_formulas.py`, `scripts/pdf_to_sections.py`, `scripts/parse_repo.py`
