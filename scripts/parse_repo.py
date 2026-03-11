from __future__ import annotations

import configparser
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import tomllib
except Exception:
    tomllib = None  # type: ignore[assignment]


EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "env",
    ".eggs",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
}

EXCLUDED_FILE_PATTERNS = [
    re.compile(r".*\.pyc$", re.IGNORECASE),
    re.compile(r".*\.egg-info($|/|\\\\)", re.IGNORECASE),
]

TREE_ANNOTATIONS = {
    "models": "🔑 模型定义",
    "model": "🔑 模型定义",
    "data": "📊 数据处理",
    "dataset": "📊 数据处理",
    "datasets": "📊 数据处理",
    "configs": "⚙️ 配置文件",
    "config": "⚙️ 配置文件",
    "utils": "🔧 工具函数",
    "tools": "🔧 工具函数",
}

ENTRYPOINT_PRIORITY = ["train.py", "main.py", "run.py"]
CORE_DIR_NAMES = {"models", "model", "networks", "modules", "core", "engine"}

LANGUAGE_BY_EXT = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".sh": "Shell",
    ".md": "Markdown",
    ".ipynb": "Jupyter",
}

COMMENT_PREFIX_BY_EXT = {
    ".py": ("#",),
    ".js": ("//", "/*", "*"),
    ".jsx": ("//", "/*", "*"),
    ".ts": ("//", "/*", "*"),
    ".tsx": ("//", "/*", "*"),
    ".java": ("//", "/*", "*"),
    ".c": ("//", "/*", "*"),
    ".cpp": ("//", "/*", "*"),
    ".h": ("//", "/*", "*"),
    ".go": ("//", "/*", "*"),
    ".rs": ("//", "/*", "*"),
    ".rb": ("#",),
    ".php": ("//", "#", "/*", "*"),
    ".sh": ("#",),
}

DEP_CATEGORIES = {
    "ML framework": {"torch", "tensorflow", "jax", "jaxlib", "pytorch-lightning", "lightning", "keras"},
    "Data": {"numpy", "pandas", "scipy", "polars", "pyarrow"},
    "Visualization": {"matplotlib", "seaborn", "plotly", "bokeh", "altair"},
    "NLP": {"transformers", "tokenizers", "spacy", "nltk", "sentencepiece"},
    "CV": {"opencv-python", "opencv", "pillow", "albumentations", "timm"},
    "Training tools": {"accelerate", "deepspeed", "wandb", "mlflow", "ray", "hydra-core", "omegaconf"},
    "Web/API": {"flask", "django", "fastapi", "uvicorn", "gradio", "streamlit"},
    "Test": {"pytest", "unittest", "tox", "hypothesis"},
}


@dataclass
class EntryPointInfo:
    path: Path
    cli_args: List[str]
    config_patterns: List[str]


@dataclass
class PythonFileSummary:
    path: Path
    classes: List[str]
    functions: List[str]
    imports: List[str]


def should_exclude_dir(dirname: str) -> bool:
    return dirname in EXCLUDED_DIRS or dirname.endswith(".egg-info")


def should_exclude_file(path: Path) -> bool:
    text = str(path).replace("\\", "/")
    for pattern in EXCLUDED_FILE_PATTERNS:
        if pattern.match(text):
            return True
    return False


def is_binary_bytes(blob: bytes) -> bool:
    if not blob:
        return False
    if b"\x00" in blob:
        return True
    sample = blob[:1024]
    non_text = 0
    for b in sample:
        if b < 9 or (13 < b < 32):
            non_text += 1
    return (non_text / max(1, len(sample))) > 0.2


def read_text_limited(path: Path, max_size: int = 100 * 1024, large_file_line_limit: int = 200) -> str:
    try:
        size = path.stat().st_size
    except OSError:
        return ""

    if size > max_size:
        try:
            with path.open("rb") as f:
                data = f.read(max_size)
            if is_binary_bytes(data):
                return ""
            text = data.decode("utf-8", errors="replace")
            return "\n".join(text.splitlines()[:large_file_line_limit])
        except OSError:
            return ""

    try:
        data = path.read_bytes()
    except OSError:
        return ""

    if is_binary_bytes(data):
        return ""
    return data.decode("utf-8", errors="replace")


def iter_repo_files(repo_root: Path) -> Iterable[Path]:
    stack = [repo_root]
    while stack:
        current = stack.pop()
        try:
            entries = sorted(current.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except OSError:
            continue
        for entry in entries:
            if entry.is_dir():
                if should_exclude_dir(entry.name):
                    continue
                stack.append(entry)
            elif entry.is_file():
                if should_exclude_file(entry):
                    continue
                yield entry


def _annotation_for_path(path: Path) -> str:
    name = path.name.lower()
    if path.is_dir() and name in TREE_ANNOTATIONS:
        return TREE_ANNOTATIONS[name]
    if path.is_file():
        if re.match(r"train.*\.py$", name):
            return "🚀 训练入口"
        if re.match(r"(eval|test).*\.py$", name):
            return "📈 评估脚本"
    return ""


def build_directory_tree(repo_root: Path) -> str:
    lines: List[str] = [repo_root.name + "/"]

    def walk(path: Path, prefix: str = "") -> None:
        try:
            entries = [e for e in path.iterdir() if not (e.is_dir() and should_exclude_dir(e.name))]
        except OSError:
            return
        filtered: List[Path] = []
        for e in sorted(entries, key=lambda p: (not p.is_dir(), p.name.lower())):
            if e.is_file() and should_exclude_file(e):
                continue
            filtered.append(e)
        for i, child in enumerate(filtered):
            last = i == len(filtered) - 1
            branch = "└── " if last else "├── "
            name = child.name + ("/" if child.is_dir() else "")
            note = _annotation_for_path(child)
            suffix = f"  [{note}]" if note else ""
            lines.append(prefix + branch + name + suffix)
            if child.is_dir():
                walk(child, prefix + ("    " if last else "│   "))

    walk(repo_root)
    return "\n".join(lines)


def find_readme(repo_root: Path) -> Optional[Path]:
    candidates = []
    try:
        items = list(repo_root.iterdir())
    except OSError:
        return None
    for p in items:
        if not p.is_file():
            continue
        lower = p.name.lower()
        if lower.startswith("readme") and lower.endswith((".md", ".rst")):
            candidates.append(p)
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.name.lower())
    return candidates[0]


def _first_paragraph(text: str) -> str:
    lines = text.splitlines()
    cleaned: List[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if cleaned:
                break
            continue
        if stripped.startswith("#"):
            continue
        cleaned.append(stripped)
    return " ".join(cleaned).strip()


def _extract_section(text: str, keywords: Sequence[str]) -> str:
    lines = text.splitlines()
    heading_re = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$")
    rst_re = re.compile(r"^\s*[=\-~`^]{3,}\s*$")
    target = None
    for i, line in enumerate(lines):
        m = heading_re.match(line)
        if m:
            title = m.group(2).strip().lower()
            if any(k in title for k in keywords):
                target = i
                break
        elif i + 1 < len(lines) and rst_re.match(lines[i + 1]):
            title = line.strip().lower()
            if any(k in title for k in keywords):
                target = i
                break
    if target is None:
        return ""

    section: List[str] = []
    for j in range(target + 1, len(lines)):
        line = lines[j]
        if heading_re.match(line):
            break
        if j + 1 < len(lines) and rst_re.match(lines[j + 1]) and lines[j].strip():
            break
        section.append(line)
    return "\n".join(section).strip()


def parse_readme(repo_root: Path) -> Dict[str, str]:
    readme_path = find_readme(repo_root)
    if not readme_path:
        return {
            "path": "",
            "description": "No README found",
            "installation": "No README found",
            "usage": "No README found",
        }
    text = read_text_limited(readme_path)
    return {
        "path": str(readme_path.relative_to(repo_root)),
        "description": _first_paragraph(text) or "No description found",
        "installation": _extract_section(text, ["install", "setup", "requirements"]) or "No installation section found",
        "usage": _extract_section(text, ["usage", "quickstart", "getting started", "run", "inference"]) or "No usage section found",
    }


def parse_dependency_line(raw: str) -> Optional[Tuple[str, str]]:
    line = raw.strip()
    if not line or line.startswith("#"):
        return None
    line = line.split("#", 1)[0].strip()
    if line.startswith(("-r ", "--requirement ", "-e ", "--editable ")):
        return None
    line = re.split(r";", line, maxsplit=1)[0].strip()
    m = re.match(r"([A-Za-z0-9_.\-\[\]]+)\s*([<>=!~].+)?$", line)
    if not m:
        return None
    name = m.group(1).split("[", 1)[0].strip().lower()
    version = (m.group(2) or "").strip()
    return (name, version)


def extract_dependencies(repo_root: Path) -> Dict[str, Dict[str, str]]:
    python_deps: Dict[str, str] = {}
    node_deps: Dict[str, str] = {}
    python_version_req = ""

    req_file = repo_root / "requirements.txt"
    if req_file.is_file():
        for line in read_text_limited(req_file).splitlines():
            parsed = parse_dependency_line(line)
            if parsed:
                python_deps.setdefault(parsed[0], parsed[1])

    setup_py = repo_root / "setup.py"
    if setup_py.is_file():
        text = read_text_limited(setup_py)
        for block in re.findall(r"install_requires\s*=\s*\[(.*?)\]", text, flags=re.DOTALL):
            for token in re.findall(r"['\"]([^'\"]+)['\"]", block):
                parsed = parse_dependency_line(token)
                if parsed:
                    python_deps.setdefault(parsed[0], parsed[1])
        py_ver = re.search(r"python_requires\s*=\s*['\"]([^'\"]+)['\"]", text)
        if py_ver:
            python_version_req = py_ver.group(1).strip()

    setup_cfg = repo_root / "setup.cfg"
    if setup_cfg.is_file():
        cp = configparser.ConfigParser()
        try:
            cp.read(setup_cfg, encoding="utf-8")
            if cp.has_option("options", "install_requires"):
                raw = cp.get("options", "install_requires")
                for line in raw.splitlines():
                    parsed = parse_dependency_line(line)
                    if parsed:
                        python_deps.setdefault(parsed[0], parsed[1])
            if cp.has_option("options", "python_requires") and not python_version_req:
                python_version_req = cp.get("options", "python_requires").strip()
        except (OSError, configparser.Error):
            pass

    pyproject = repo_root / "pyproject.toml"
    if pyproject.is_file():
        text = read_text_limited(pyproject)
        if tomllib is not None:
            try:
                data = tomllib.loads(text)
                project = data.get("project", {})
                for dep in project.get("dependencies", []) or []:
                    parsed = parse_dependency_line(dep)
                    if parsed:
                        python_deps.setdefault(parsed[0], parsed[1])
                req = project.get("requires-python")
                if isinstance(req, str) and req.strip() and not python_version_req:
                    python_version_req = req.strip()
                poetry = data.get("tool", {}).get("poetry", {})
                for name, val in (poetry.get("dependencies") or {}).items():
                    if str(name).lower() == "python":
                        if not python_version_req:
                            python_version_req = str(val)
                        continue
                    python_deps.setdefault(str(name).lower(), str(val))
            except Exception:
                pass
        else:
            for m in re.findall(r"^\s*([A-Za-z0-9_.\-]+)\s*=\s*['\"]([^'\"]+)['\"]", text, flags=re.MULTILINE):
                python_deps.setdefault(m[0].lower(), m[1])

    package_json = repo_root / "package.json"
    if package_json.is_file():
        text = read_text_limited(package_json)
        try:
            data = json.loads(text)
            for section in ("dependencies", "devDependencies"):
                deps = data.get(section, {})
                if isinstance(deps, dict):
                    for k, v in deps.items():
                        node_deps[str(k)] = str(v)
        except json.JSONDecodeError:
            pass

    return {
        "python": python_deps,
        "node": node_deps,
        "python_requires": {"value": python_version_req},
    }


def categorize_dependencies(py_deps: Dict[str, str], node_deps: Dict[str, str]) -> Dict[str, List[str]]:
    all_deps = {k.lower(): v for k, v in {**py_deps, **node_deps}.items()}
    result: Dict[str, List[str]] = {}
    for category, names in DEP_CATEGORIES.items():
        matched = []
        for dep_name in sorted(all_deps):
            if dep_name in names:
                version = all_deps.get(dep_name, "")
                matched.append(f"{dep_name}{(' ' + version) if version else ''}")
        if matched:
            result[category] = matched
    return result


def find_entry_points(repo_root: Path, files: Iterable[Path]) -> List[EntryPointInfo]:
    patterns = [
        re.compile(r"train.*\.py$", re.IGNORECASE),
        re.compile(r"main\.py$", re.IGNORECASE),
        re.compile(r"run.*\.py$", re.IGNORECASE),
        re.compile(r"app\.py$", re.IGNORECASE),
        re.compile(r"demo.*\.py$", re.IGNORECASE),
        re.compile(r"inference.*\.py$", re.IGNORECASE),
        re.compile(r"eval.*\.py$", re.IGNORECASE),
        re.compile(r"test.*\.py$", re.IGNORECASE),
    ]
    results: List[EntryPointInfo] = []
    for file_path in files:
        name = file_path.name
        if not any(p.match(name) for p in patterns):
            continue
        if file_path.suffix.lower() != ".py":
            continue
        content = read_text_limited(file_path)
        lines = content.splitlines()[:50]
        block = "\n".join(lines)
        arg_matches = re.findall(r"add_argument\(([^\)]*)\)", block)
        args_clean = []
        for m in arg_matches:
            quoted = re.findall(r"['\"]([^'\"]+)['\"]", m)
            if quoted:
                args_clean.append(", ".join(quoted))
        config_patterns = []
        for token in ["yaml", "toml", "json", "config", "omegaconf", "hydra"]:
            if re.search(token, block, flags=re.IGNORECASE):
                config_patterns.append(token)
        results.append(
            EntryPointInfo(
                path=file_path.relative_to(repo_root),
                cli_args=sorted(set(args_clean)),
                config_patterns=sorted(set(config_patterns)),
            )
        )
    results.sort(key=lambda x: str(x.path).lower())
    return results


def pick_primary_entry(entry_points: Sequence[EntryPointInfo]) -> Optional[EntryPointInfo]:
    if not entry_points:
        return None
    by_name = {ep.path.name.lower(): ep for ep in entry_points}
    for candidate in ENTRYPOINT_PRIORITY:
        for name, ep in by_name.items():
            if name == candidate or name.startswith(candidate.replace(".py", "")):
                return ep
    return entry_points[0]


def extract_py_summary(path: Path) -> PythonFileSummary:
    text = read_text_limited(path)
    classes = re.findall(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(|:)", text, flags=re.MULTILINE)
    functions = re.findall(r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text, flags=re.MULTILINE)
    imports: List[str] = []
    for m in re.findall(r"^\s*import\s+([^\n]+)", text, flags=re.MULTILINE):
        parts = [p.strip().split(" as ")[0].strip() for p in m.split(",")]
        imports.extend([p for p in parts if p])
    for m in re.findall(r"^\s*from\s+([A-Za-z0-9_\.]+)\s+import\s+([^\n]+)", text, flags=re.MULTILINE):
        mod = m[0].strip()
        imports.append(mod)
    return PythonFileSummary(path=path, classes=classes, functions=functions, imports=imports)


def find_core_modules(repo_root: Path, files: Sequence[Path]) -> Dict[str, Dict[str, object]]:
    core_dirs: Dict[Path, List[Path]] = defaultdict(list)
    py_files = [p for p in files if p.suffix.lower() == ".py"]

    for p in py_files:
        rel = p.relative_to(repo_root)
        for idx, part in enumerate(rel.parts[:-1]):
            if part.lower() in CORE_DIR_NAMES:
                core_dir = repo_root / Path(*rel.parts[: idx + 1])
                core_dirs[core_dir].append(p)
                break

    summaries: Dict[Path, PythonFileSummary] = {p: extract_py_summary(p) for p in py_files}

    import_name_to_files: Dict[str, List[Path]] = defaultdict(list)
    for p in py_files:
        rel_no_ext = p.relative_to(repo_root).with_suffix("")
        dotted = ".".join(rel_no_ext.parts)
        import_name_to_files[dotted].append(p)
        import_name_to_files[p.stem].append(p)

    imported_count: Counter[Path] = Counter()
    for src, summary in summaries.items():
        for dep in summary.imports:
            dep_tail = dep.split(".")[-1]
            candidates = import_name_to_files.get(dep, []) + import_name_to_files.get(dep_tail, [])
            for c in candidates:
                if c != src:
                    imported_count[c] += 1

    result: Dict[str, Dict[str, object]] = {}
    for core_dir, dir_files in sorted(core_dirs.items(), key=lambda x: str(x[0]).lower()):
        file_infos: List[Dict[str, object]] = []
        best_file: Optional[Path] = None
        best_score = (-1, -1, -1)
        for p in sorted(set(dir_files), key=lambda x: str(x).lower()):
            s = summaries[p]
            imp_count = int(imported_count.get(p, 0))
            score = (len(s.classes), imp_count, len(s.functions))
            if score > best_score:
                best_score = score
                best_file = p
            file_infos.append(
                {
                    "path": str(p.relative_to(repo_root)),
                    "classes": s.classes,
                    "functions": s.functions,
                    "imports": s.imports,
                    "imported_by": imp_count,
                }
            )
        result[str(core_dir.relative_to(repo_root))] = {
            "files": file_infos,
            "important_file": str(best_file.relative_to(repo_root)) if best_file else "",
        }
    return result


def compute_statistics(files: Sequence[Path]) -> Dict[str, object]:
    ext_counter: Counter[str] = Counter()
    loc_by_lang: Counter[str] = Counter()
    total_loc = 0

    for p in files:
        ext = p.suffix.lower() or "<no_ext>"
        ext_counter[ext] += 1
        language = LANGUAGE_BY_EXT.get(ext, "Other")
        text = read_text_limited(p)
        if not text:
            continue
        comment_prefixes = COMMENT_PREFIX_BY_EXT.get(ext, tuple())
        file_loc = 0
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if comment_prefixes and any(stripped.startswith(prefix) for prefix in comment_prefixes):
                continue
            file_loc += 1
        loc_by_lang[language] += file_loc
        total_loc += file_loc

    primary_language = "Unknown"
    primary_percent = 0.0
    if total_loc > 0 and loc_by_lang:
        primary_language, primary_count = max(loc_by_lang.items(), key=lambda x: x[1])
        primary_percent = 100.0 * primary_count / total_loc

    return {
        "files_by_extension": dict(sorted(ext_counter.items(), key=lambda x: (-x[1], x[0]))),
        "total_files": len(files),
        "total_lines": total_loc,
        "loc_by_language": dict(sorted(loc_by_lang.items(), key=lambda x: (-x[1], x[0]))),
        "primary_language": primary_language,
        "primary_percent": primary_percent,
    }


def extract_docstring_or_comment(lines: List[str], start_idx: int) -> str:
    i = start_idx
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith('"""') or stripped.startswith("'''"):
            quote = stripped[:3]
            if stripped.count(quote) >= 2 and len(stripped) > 6:
                return stripped.strip(quote).strip() or "(无文档说明)"
            chunks = [stripped[3:].strip()]
            i += 1
            while i < len(lines):
                part = lines[i].strip()
                if quote in part:
                    chunks.append(part.split(quote, 1)[0].strip())
                    break
                chunks.append(part)
                i += 1
            text = " ".join([c for c in chunks if c])
            return text or "(无文档说明)"
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or "(无文档说明)"
        break
    return "(无文档说明)"


def extract_key_signatures(path: Path, limit: int = 5) -> List[Dict[str, object]]:
    text = read_text_limited(path)
    lines = text.splitlines()
    class_matches = list(re.finditer(r"^(\s*)class\s+([A-Za-z_][A-Za-z0-9_]*)\s*(\([^\)]*\))?\s*:", text, flags=re.MULTILINE))
    func_matches = list(re.finditer(r"^(\s*)def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^\)]*)\)\s*:", text, flags=re.MULTILINE))
    items: List[Dict[str, object]] = []

    for cm in class_matches:
        class_name = cm.group(2)
        start_line = text[: cm.start()].count("\n")
        doc = extract_docstring_or_comment(lines, start_line + 1)
        indent = len(cm.group(1))
        methods: List[str] = []
        for fm in func_matches:
            f_indent = len(fm.group(1))
            if f_indent <= indent:
                continue
            f_line = text[: fm.start()].count("\n")
            if f_line <= start_line:
                continue
            methods.append(fm.group(2))
        items.append(
            {
                "type": "class",
                "name": class_name,
                "signature": f"class {class_name}",
                "doc": doc,
                "methods": sorted(set(methods))[:8],
            }
        )

    for fm in func_matches:
        name = fm.group(2)
        params = re.sub(r"\s+", " ", fm.group(3).strip())
        start_line = text[: fm.start()].count("\n")
        doc = extract_docstring_or_comment(lines, start_line + 1)
        items.append(
            {
                "type": "function",
                "name": name,
                "signature": f"def {name}({params})",
                "doc": doc,
                "methods": [],
            }
        )

    items.sort(key=lambda x: (0 if x["type"] == "class" else 1, str(x["name"]).lower()))
    return items[:limit]


def render_dependency_section(deps: Dict[str, Dict[str, str]], categorized: Dict[str, List[str]]) -> str:
    lines: List[str] = []
    py = deps.get("python", {})
    node = deps.get("node", {})
    if py:
        lines.append("- Python 依赖：")
        for name in sorted(py):
            ver = py[name]
            lines.append(f"  - `{name}` {ver}".rstrip())
    else:
        lines.append("- Python 依赖：未检测到")
    if node:
        lines.append("- Node 依赖：")
        for name in sorted(node):
            lines.append(f"  - `{name}` {node[name]}")
    else:
        lines.append("- Node 依赖：未检测到")

    if categorized:
        lines.append("- 关键依赖分类：")
        for cat, values in categorized.items():
            lines.append(f"  - **{cat}**: {', '.join(values)}")
    else:
        lines.append("- 关键依赖分类：未匹配到常见类别")
    return "\n".join(lines)


def render_core_modules(core_modules: Dict[str, Dict[str, object]]) -> str:
    if not core_modules:
        return "未识别到核心模块目录。"
    lines: List[str] = []
    for dirname, payload in core_modules.items():
        lines.append(f"### `{dirname}`")
        important = payload.get("important_file", "")
        if important:
            lines.append(f"- 关键文件：`{important}`")
        files = payload.get("files", [])
        if not isinstance(files, list):
            continue
        for file_info in files:
            if not isinstance(file_info, dict):
                continue
            lines.append(f"- `{file_info.get('path', '')}`")
            cls = file_info.get("classes", []) or []
            fn = file_info.get("functions", []) or []
            lines.append(f"  - class: {', '.join(cls[:6]) if cls else '无'}")
            lines.append(f"  - def: {', '.join(fn[:8]) if fn else '无'}")
    return "\n".join(lines)


def render_entry_points(entry_points: Sequence[EntryPointInfo], primary: Optional[EntryPointInfo]) -> str:
    if not entry_points:
        return "未发现入口文件。"
    lines: List[str] = []
    if primary:
        lines.append(f"- PRIMARY: `{primary.path}`")
    for ep in entry_points:
        lines.append(f"- `{ep.path}`")
        lines.append(f"  - CLI 参数: {', '.join(ep.cli_args) if ep.cli_args else '未检测到 argparse 参数'}")
        lines.append(f"  - 配置模式: {', '.join(ep.config_patterns) if ep.config_patterns else '未检测到'}")
    return "\n".join(lines)


def generate_report(
    repo_root: Path,
    output_dir: Path,
    tree_text: str,
    readme_info: Dict[str, str],
    deps: Dict[str, Dict[str, str]],
    categorized_deps: Dict[str, List[str]],
    entry_points: Sequence[EntryPointInfo],
    primary_entry: Optional[EntryPointInfo],
    core_modules: Dict[str, Dict[str, object]],
    stats: Dict[str, object],
) -> None:
    framework = "Unknown"
    py_dep_names = set((deps.get("python", {}) or {}).keys())
    if "torch" in py_dep_names:
        framework = "PyTorch"
    elif "tensorflow" in py_dep_names:
        framework = "TensorFlow"
    elif "jax" in py_dep_names or "jaxlib" in py_dep_names:
        framework = "JAX"

    percent_raw = stats.get("primary_percent", 0.0)
    primary_percent = float(percent_raw) if isinstance(percent_raw, (int, float)) else 0.0

    report = f"""# 💻 代码仓库解析：{repo_root.name}

## 基本信息
| 项目 | 内容 |
|------|------|
| 语言 | {(stats.get('primary_language') or 'Unknown')} ({primary_percent:.1f}%) |
| 代码规模 | {stats.get('total_files', 0)} 文件, {stats.get('total_lines', 0)} 行 |
| 主要框架 | {framework} |
| Python版本要求 | {deps.get('python_requires', {}).get('value') or '未检测到'} |

## 项目结构
```text
{tree_text}
```

## 核心模块
{render_core_modules(core_modules)}

## 入口文件
{render_entry_points(entry_points, primary_entry)}

## 依赖分析
{render_dependency_section(deps, categorized_deps)}

## 复现指南（基于README）
- README 路径：`{readme_info.get('path') or 'No README found'}`
- 项目描述：{readme_info.get('description', 'No README found')}

### Installation
{readme_info.get('installation', 'No README found')}

### Usage
{readme_info.get('usage', 'No README found')}
"""
    (output_dir / "repo-report.md").write_text(report, encoding="utf-8")


def generate_key_functions_md(
    repo_root: Path,
    output_dir: Path,
    core_modules: Dict[str, Dict[str, object]],
) -> int:
    blocks: List[str] = ["# 🔬 核心函数索引", ""]
    module_count = 0
    for _, payload in core_modules.items():
        important = payload.get("important_file", "")
        if not important:
            continue
        important_str = str(important)
        path = repo_root / important_str
        if not path.exists() or not path.is_file():
            continue
        module_count += 1
        blocks.append(f"## `{path.name}`")
        blocks.append(f"📍 位置：`{Path(important_str)}`")
        blocks.append("")
        signatures = extract_key_signatures(path, limit=5)
        if not signatures:
            blocks.append("未提取到 class/def 定义。")
            blocks.append("")
            continue
        for item in signatures:
            if item["type"] == "class":
                blocks.append(f"### class {item['name']}")
                blocks.append(str(item["doc"]))
                methods_raw = item.get("methods", [])
                methods = [str(m) for m in methods_raw] if isinstance(methods_raw, list) else []
                method_text = ", ".join(methods) if methods else "无"
                blocks.append(f"Methods: {method_text}")
                blocks.append("")
            else:
                blocks.append(f"### {item['signature']}")
                blocks.append(str(item["doc"]))
                blocks.append("")
    if module_count == 0:
        blocks.append("未识别到可提取的核心文件。")
    (output_dir / "key-functions.md").write_text("\n".join(blocks).rstrip() + "\n", encoding="utf-8")
    return module_count


FUNCTIONAL_MODULE_PATTERNS: List[Tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"(data|dataset|dataloader|loader|preprocess|augment)", re.IGNORECASE), "data", "数据处理与加载"),
    (re.compile(r"(model|network|net|arch|backbone|encoder|decoder|head)", re.IGNORECASE), "model", "模型架构"),
    (re.compile(r"(train|trainer|runner|engine|solver)", re.IGNORECASE), "train", "训练循环"),
    (re.compile(r"(loss|criterion|objective)", re.IGNORECASE), "loss", "损失函数与优化器"),
    (re.compile(r"(eval|test|metric|valid|infer|predict)", re.IGNORECASE), "eval", "推理与评估"),
    (re.compile(r"(util|helper|tool|misc|common)", re.IGNORECASE), "utils", "工具函数"),
    (re.compile(r"(config|cfg|setting|param|hyperp)", re.IGNORECASE), "config", "配置与超参数"),
]


def classify_file_to_module(path: Path) -> Optional[Tuple[str, str]]:
    """Return (module_key, module_name) for a file path, or None if unclassified."""
    check_parts = list(path.parts) + [path.stem]
    for part in check_parts:
        for pattern, key, name in FUNCTIONAL_MODULE_PATTERNS:
            if pattern.search(part):
                return (key, name)
    return None


def generate_module_jsons(
    repo_root: Path,
    output_dir: Path,
    core_modules: Dict[str, Dict[str, object]],
    entry_points: Sequence[EntryPointInfo],
    deps: Dict[str, Dict[str, str]],
) -> None:
    """Generate per-functional-module JSON files for code-modules/ report generation."""
    # Group all repo Python files by functional module
    module_files: Dict[str, Dict[str, object]] = {}

    for core_dir_str, payload in core_modules.items():
        files = payload.get("files", [])
        if not isinstance(files, list):
            continue
        for file_info in files:
            if not isinstance(file_info, dict):
                continue
            file_path_str = str(file_info.get("path", ""))
            if not file_path_str:
                continue
            file_path = repo_root / file_path_str
            classification = classify_file_to_module(file_path)
            if classification is None:
                # Fallback: use core_dir name
                dir_name = Path(core_dir_str).name.lower()
                classification = (dir_name, core_dir_str)

            module_key, module_name = classification
            if module_key not in module_files:
                module_files[module_key] = {
                    "module_key": module_key,
                    "module_name": module_name,
                    "files": [],
                }
            module_entry = module_files[module_key]
            files_list = module_entry.get("files")
            if not isinstance(files_list, list):
                continue

            # Extract full signatures for this file
            signatures = extract_key_signatures(file_path, limit=20)
            full_text = read_text_limited(file_path, max_size=200 * 1024)
            lines = full_text.splitlines()

            files_list.append({
                "path": file_path_str,
                "classes": file_info.get("classes", []),
                "functions": file_info.get("functions", []),
                "imports": file_info.get("imports", []),
                "imported_by_count": int(file_info.get("imported_by", 0)),
                "signatures": signatures,
                "line_count": len(lines),
                "code_preview": "\n".join(lines[:100]),
            })

    # Also add entry points to their respective modules if not already covered
    for ep in entry_points:
        ep_path = repo_root / ep.path
        classification = classify_file_to_module(ep_path)
        module_key = classification[0] if classification else "train"
        module_name = classification[1] if classification else "训练循环"

        if module_key not in module_files:
            module_files[module_key] = {
                "module_key": module_key,
                "module_name": module_name,
                "files": [],
            }

        ep_files = module_files[module_key].get("files")
        if not isinstance(ep_files, list):
            continue

        # Check not already added
        existing_paths = {str(f.get("path", "")) for f in ep_files if isinstance(f, dict)}
        ep_path_str = str(ep.path)
        if ep_path_str not in existing_paths:
            full_text = read_text_limited(ep_path, max_size=200 * 1024)
            lines = full_text.splitlines()
            ep_files.append({
                "path": ep_path_str,
                "is_entrypoint": True,
                "cli_args": ep.cli_args,
                "config_patterns": ep.config_patterns,
                "line_count": len(lines),
                "code_preview": "\n".join(lines[:100]),
            })

    # Write one JSON per module
    for module_key, module_data in module_files.items():
        out_path = output_dir / f"module-{module_key}.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(module_data, f, ensure_ascii=False, indent=2)

    # Write index JSON
    index = {
        "modules": [
            {
                "key": k,
                "name": v.get("module_name", k),
                "file_count": len(files_obj) if isinstance(files_obj := v.get("files"), list) else 0,
                "json_file": f"module-{k}.json",
            }
            for k, v in module_files.items()
        ]
    }
    index_path = output_dir / "modules-index.json"
    with index_path.open("w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def analyze_repository(repo_root: Path, output_dir: Path) -> None:
    if not repo_root.exists() or not repo_root.is_dir():
        raise FileNotFoundError(f"Repository path does not exist or is not a directory: {repo_root}")

    output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(iter_repo_files(repo_root), key=lambda p: str(p).lower())
    tree_text = build_directory_tree(repo_root)
    (output_dir / "structure-tree.txt").write_text(tree_text + "\n", encoding="utf-8")

    readme_info = parse_readme(repo_root)
    deps = extract_dependencies(repo_root)
    categorized = categorize_dependencies(deps.get("python", {}), deps.get("node", {}))
    entry_points = find_entry_points(repo_root, files)
    primary_entry = pick_primary_entry(entry_points)
    core_modules = find_core_modules(repo_root, files)
    stats = compute_statistics(files)

    generate_report(
        repo_root=repo_root,
        output_dir=output_dir,
        tree_text=tree_text,
        readme_info=readme_info,
        deps=deps,
        categorized_deps=categorized,
        entry_points=entry_points,
        primary_entry=primary_entry,
        core_modules=core_modules,
        stats=stats,
    )
    core_module_count = generate_key_functions_md(repo_root, output_dir, core_modules)
    generate_module_jsons(repo_root, output_dir, core_modules, entry_points, deps)

    print(
        f"Analyzed {repo_root.name}: {stats.get('total_files', 0)} files, "
        f"{stats.get('total_lines', 0)} lines, {core_module_count} core modules identified"
    )


def main(argv: Sequence[str]) -> int:
    if len(argv) != 3:
        print("Usage: python parse_repo.py <repo_path> <output_dir>", file=sys.stderr)
        return 1
    repo_path = Path(argv[1]).expanduser().resolve()
    output_dir = Path(argv[2]).expanduser().resolve()
    try:
        analyze_repository(repo_path, output_dir)
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
