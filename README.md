# paper-reader

`paper-reader` 是一个用于学术论文深度阅读的 OpenCode Skill，支持从论文 PDF/DOI/Semantic Scholar 链接出发，自动提取图表与公式、发现关联代码仓库，并生成面向初学者的结构化解读报告。

## 能力概览

- 自动提取论文 `figures`、`tables`、`formulas`
- 自动发现论文对应 GitHub 仓库并做模块级代码分析
- 生成三类产物：
  - `论文深度解读.md`
  - `code-modules/`（按模块拆分的代码讲解）
  - `理解度测试.md`
- 支持 `quick` / `core` / `full` 三种解读深度

## 前置要求

- OpenCode 环境（支持 Skills）
- Python 3.10+
- 可用的 `git` 命令
- 建议安装 GitHub CLI（可选，用于更稳健地检索仓库）

安装依赖：

```bash
pip install "PyMuPDF>=1.23.0" "pdfplumber>=0.10.0"
```

## 安装 Skill

将本仓库内容放到 OpenCode skills 目录，例如：

```text
~/.config/opencode/skills/paper-reader/
```

目录结构应包含：

```text
paper-reader/
├── SKILL.md
├── scripts/
├── references/
└── docs/
```

## 使用方式

在 OpenCode 中直接提出任务，例如：

- 「请用 `paper-reader` 深度解读这篇论文：`xxx.pdf`」
- 「对这篇 DOI 论文做 `core` 深度报告，并分析其官方实现仓库」

Skill 会按以下阶段执行：

1. 获取论文内容（PDF/URL）
2. 提取章节、图像、公式
3. 自动发现并分析关联代码仓库
4. 生成解读报告与测试题

## 输出结果

默认输出目录（示例）：

```text
{paper-name}/
├── 论文深度解读.md
├── code-modules/
├── 理解度测试.md
├── images/
├── code-analysis/
├── metadata.json
├── figure_map.json
├── formulas.json
└── sections.json
```

## 报告风格说明

- 图文结构采用 `figure-first`：先图，再小字注释，再正文讲解
- 公式标题保留语义名，公式编号以下注形式呈现
- 内容语言默认中文，保留关键英文术语（如 Attention Mechanism）

## 常见问题

- 图表提取不完整：确认输入 PDF 清晰且未损坏；重试可提升成功率
- 未找到官方代码仓库：Skill 会继续生成纯论文分析，不会中断
- 公式识别置信度低：会自动回退到图像识别路径并标注精度风险

## 许可证

如无额外声明，按仓库维护者设置执行。
