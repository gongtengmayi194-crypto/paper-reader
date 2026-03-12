# paper-reader Skill 使用说明

`paper-reader` 是用于学术论文深度阅读与代码联动解析的 OpenCode Skill。

## 功能

- 提取论文中的图、表、公式
- 自动尝试发现论文对应代码仓库
- 生成三类产物：
  - `论文深度解读.md`
  - `code-modules/`（按模块拆分的代码解读）
  - `理解度测试.md`

## 依赖安装

```bash
pip install "PyMuPDF>=1.23.0" "Pillow>=10.0.0"
```

## 目录结构

```text
paper-reader/
├── SKILL.md
├── README.md
├── scripts/
├── references/
└── docs/
```

## 使用方式

在 OpenCode 中触发此 skill，输入论文 PDF 路径或 DOI / Semantic Scholar 链接。

示例：

- 「请用 paper-reader 解读这篇论文：`/path/to/paper.pdf`」
- 「对这篇 DOI 论文做 core 深度报告，并分析其代码仓库」

## 输出内容

输出目录示例：

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

## 风格约定

- 图文采用 figure-first：先图，再小字注释，再正文讲解
- 公式标题保留语义名，公式编号使用下标注释
- 报告默认中文，关键技术词保留英文术语
