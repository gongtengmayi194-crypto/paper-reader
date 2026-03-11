#!/usr/bin/env python3
from __future__ import annotations

import json
import importlib
import logging
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    fitz = importlib.import_module("fitz")
except Exception as exc:
    raise RuntimeError("PyMuPDF is required. Install with: pip install pymupdf") from exc


LOGGER = logging.getLogger("pdf_to_sections")

SPECIAL_H1 = {
    "abstract",
    "references",
    "acknowledgments",
    "acknowledgements",
}

HEADING_PATTERNS: Dict[int, re.Pattern[str]] = {
    1: re.compile(r"^\d+\.?\s+[A-Z].*"),
    2: re.compile(r"^\d+\.\d+\.?\s+.*"),
    3: re.compile(r"^\d+\.\d+\.\d+\.?\s+.*"),
}

FIGURE_REF_PATTERN = re.compile(r"\b(Figure|Fig\.?|Table)\s*(\d+[A-Za-z]?)\b", re.IGNORECASE)
EQUATION_REF_PATTERN = re.compile(r"(?:(?:Eq\.?|Equation)\s*)?\((\d{1,3})\)")


@dataclass
class SpanInfo:
    text: str
    font_size: float
    is_bold: bool
    page_number: int
    bbox: Tuple[float, float, float, float]


@dataclass
class LineInfo:
    text: str
    page_number: int
    bbox: Tuple[float, float, float, float]
    font_size: float
    is_bold: bool
    spans: List[SpanInfo]


@dataclass
class HeadingCandidate:
    line_index: int
    page_number: int
    text: str
    level: int
    font_size: float


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def clean_line_text(text: str) -> str:
    cleaned = text.replace("\u00a0", " ").replace("\t", " ")
    return normalize_space(cleaned)


def is_bold_from_flags(flags: int) -> bool:
    return bool(flags & 16)


def build_line_from_spans(spans: Sequence[SpanInfo], page_number: int, bbox: Sequence[float]) -> Optional[LineInfo]:
    chunks: List[str] = []
    font_sizes: List[float] = []
    bold_votes = 0
    kept_spans: List[SpanInfo] = []
    for span in spans:
        text = clean_line_text(span.text)
        if not text:
            continue
        chunks.append(text)
        font_sizes.append(span.font_size)
        if span.is_bold:
            bold_votes += 1
        kept_spans.append(span)

    if not chunks:
        return None

    full_text = normalize_space(" ".join(chunks))
    if not full_text:
        return None

    line_font_size = max(font_sizes) if font_sizes else 0.0
    is_bold = bold_votes >= max(1, len(kept_spans) // 2)
    return LineInfo(
        text=full_text,
        page_number=page_number,
        bbox=(float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])),
        font_size=line_font_size,
        is_bold=is_bold,
        spans=kept_spans,
    )


def extract_spans_and_lines(doc: Any) -> Tuple[List[SpanInfo], Dict[int, List[LineInfo]], Dict[int, float]]:
    all_spans: List[SpanInfo] = []
    page_lines: Dict[int, List[LineInfo]] = defaultdict(list)
    page_widths: Dict[int, float] = {}

    for page_idx in range(len(doc)):
        page_number = page_idx + 1
        page = doc[page_idx]
        page_widths[page_number] = float(page.rect.width)
        try:
            data = page.get_text("dict")
        except Exception as exc:
            LOGGER.warning("Failed to extract page %s: %s", page_number, exc)
            continue

        blocks = data.get("blocks", [])
        for block in blocks:
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                line_spans: List[SpanInfo] = []
                for span in line.get("spans", []):
                    raw_text = str(span.get("text", ""))
                    if not raw_text.strip():
                        continue
                    size = float(span.get("size", 0.0))
                    flags = int(span.get("flags", 0))
                    bbox_raw = span.get("bbox", (0.0, 0.0, 0.0, 0.0))
                    span_info = SpanInfo(
                        text=raw_text,
                        font_size=size,
                        is_bold=is_bold_from_flags(flags),
                        page_number=page_number,
                        bbox=(
                            float(bbox_raw[0]),
                            float(bbox_raw[1]),
                            float(bbox_raw[2]),
                            float(bbox_raw[3]),
                        ),
                    )
                    all_spans.append(span_info)
                    line_spans.append(span_info)

                line_bbox = line.get("bbox", (0.0, 0.0, 0.0, 0.0))
                line_info = build_line_from_spans(line_spans, page_number, line_bbox)
                if line_info is not None:
                    page_lines[page_number].append(line_info)

    return all_spans, page_lines, page_widths


def detect_two_column(page_lines: List[LineInfo], page_width: float) -> bool:
    if len(page_lines) < 12:
        return False

    mid_x = page_width / 2.0
    left = 0
    right = 0
    crossing = 0
    for ln in page_lines:
        x0, _, x1, _ = ln.bbox
        center = (x0 + x1) / 2.0
        if x0 < mid_x < x1:
            crossing += 1
        elif center <= mid_x:
            left += 1
        else:
            right += 1

    if left < 4 or right < 4:
        return False

    crossing_ratio = crossing / max(1, len(page_lines))
    balance = min(left, right) / max(left, right)
    return crossing_ratio < 0.25 and balance > 0.30


def sorted_page_lines(page_lines: Dict[int, List[LineInfo]], page_widths: Dict[int, float]) -> Dict[int, List[LineInfo]]:
    ordered: Dict[int, List[LineInfo]] = {}
    for page_no, lines in page_lines.items():
        width = page_widths.get(page_no, 0.0)
        two_column = detect_two_column(lines, width)
        if not two_column:
            ordered[page_no] = sorted(lines, key=lambda ln: (round(ln.bbox[1], 1), ln.bbox[0]))
            continue

        mid_x = width / 2.0
        left = [ln for ln in lines if (ln.bbox[0] + ln.bbox[2]) / 2.0 <= mid_x]
        right = [ln for ln in lines if (ln.bbox[0] + ln.bbox[2]) / 2.0 > mid_x]
        left_sorted = sorted(left, key=lambda ln: (round(ln.bbox[1], 1), ln.bbox[0]))
        right_sorted = sorted(right, key=lambda ln: (round(ln.bbox[1], 1), ln.bbox[0]))
        ordered[page_no] = left_sorted + right_sorted
    return ordered


def detect_repeated_headers_footers(page_lines: Dict[int, List[LineInfo]], total_pages: int) -> set[Tuple[int, int]]:
    line_counts: Counter[str] = Counter()
    line_positions: Dict[str, List[Tuple[int, int, float]]] = defaultdict(list)
    for page_no, lines in page_lines.items():
        for idx, line in enumerate(lines):
            normalized = normalize_space(line.text.lower())
            if len(normalized) < 2:
                continue
            line_counts[normalized] += 1
            line_positions[normalized].append((page_no, idx, line.bbox[1]))

    threshold = max(2, total_pages // 3)
    removable: set[Tuple[int, int]] = set()
    for text, count in line_counts.items():
        if count < threshold:
            continue
        entries = line_positions[text]
        ys = [y for _, _, y in entries]
        if not ys:
            continue
        y_med = median(ys)
        if y_med < 80 or y_med > 700:
            for page_no, idx, _ in entries:
                removable.add((page_no, idx))
    return removable


def remove_headers_footers(page_lines: Dict[int, List[LineInfo]], total_pages: int) -> Dict[int, List[LineInfo]]:
    removable = detect_repeated_headers_footers(page_lines, total_pages)
    cleaned: Dict[int, List[LineInfo]] = {}
    for page_no, lines in page_lines.items():
        retained = [ln for idx, ln in enumerate(lines) if (page_no, idx) not in removable]
        cleaned[page_no] = retained
    return cleaned


def body_font_size(spans: Sequence[SpanInfo]) -> float:
    if not spans:
        return 10.0
    counts: Counter[float] = Counter(round(sp.font_size, 1) for sp in spans if sp.text.strip())
    if not counts:
        return 10.0
    return counts.most_common(1)[0][0]


def largest_font_size(spans: Sequence[SpanInfo]) -> float:
    if not spans:
        return 0.0
    return max(sp.font_size for sp in spans)


def classify_heading_level(text: str, font_size: float, body_size: float, max_size: float, is_bold: bool) -> int:
    raw = text.strip()
    low = raw.lower()

    if low in SPECIAL_H1:
        return 1
    if HEADING_PATTERNS[3].match(raw):
        return 3
    if HEADING_PATTERNS[2].match(raw):
        return 2
    if HEADING_PATTERNS[1].match(raw):
        return 1

    if font_size >= max_size - 0.2:
        return 0
    if font_size >= body_size + 2.0:
        return 1
    if font_size >= body_size + 1.2 and is_bold:
        return 2
    return -1


def collect_ordered_lines(page_lines: Dict[int, List[LineInfo]]) -> List[LineInfo]:
    all_lines: List[LineInfo] = []
    for page_no in sorted(page_lines):
        all_lines.extend(page_lines[page_no])
    return all_lines


def detect_headings(lines: Sequence[LineInfo], body_size: float, max_size: float) -> List[HeadingCandidate]:
    candidates: List[HeadingCandidate] = []
    for idx, line in enumerate(lines):
        text = normalize_space(line.text)
        if not text:
            continue
        level = classify_heading_level(text, line.font_size, body_size, max_size, line.is_bold)
        if level < 0:
            continue
        if level == 0 and line.page_number != 1:
            continue
        if level == 0:
            continue
        candidates.append(
            HeadingCandidate(
                line_index=idx,
                page_number=line.page_number,
                text=text,
                level=level,
                font_size=line.font_size,
            )
        )

    filtered: List[HeadingCandidate] = []
    last_index = -10
    for cand in candidates:
        if cand.line_index - last_index <= 0:
            continue
        if len(cand.text) > 180:
            continue
        filtered.append(cand)
        last_index = cand.line_index
    return filtered


def merge_paragraph_lines(lines: Sequence[str]) -> str:
    if not lines:
        return ""

    merged_parts: List[str] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            if merged_parts and not merged_parts[-1].endswith("\n\n"):
                merged_parts.append("\n\n")
            continue

        if not merged_parts:
            merged_parts.append(line)
            continue

        prev = merged_parts[-1]
        if prev.endswith("-") and line and line[0].islower():
            merged_parts[-1] = prev[:-1] + line
            continue

        if prev.endswith("\n\n"):
            merged_parts.append(line)
            continue

        sentence_end = bool(re.search(r"[\.!\?:;]$", prev))
        starts_new_list = bool(re.match(r"^(?:[-*]|\d+\.|\(\d+\))\s+", line))
        if sentence_end or starts_new_list:
            merged_parts.append("\n" + line)
        else:
            merged_parts[-1] = prev + " " + line

    text = "".join(merged_parts)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_references_count(content: str) -> int:
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    if not lines:
        return 0

    pattern_count = 0
    for ln in lines:
        if re.match(r"^(?:\[\d+\]|\d+\.|\d+\s)", ln):
            pattern_count += 1

    if pattern_count > 0:
        return pattern_count
    return len(lines)


def extract_figures_and_formulas(content: str) -> Tuple[List[str], List[str]]:
    figures: List[str] = []
    formulas: List[str] = []

    for match in FIGURE_REF_PATTERN.finditer(content):
        kind = match.group(1).lower()
        num = match.group(2).lower()
        if kind.startswith("tab"):
            ref = f"table{num}"
        else:
            ref = f"fig{num}"
        if ref not in figures:
            figures.append(ref)

    for match in EQUATION_REF_PATTERN.finditer(content):
        num = match.group(1)
        ref = f"eq{num}"
        if ref not in formulas:
            formulas.append(ref)

    return figures, formulas


def section_id_from_heading(heading: str, idx: int) -> str:
    num_match = re.match(r"^(\d+(?:\.\d+)*)", heading)
    if num_match:
        return f"sec_{num_match.group(1).replace('.', '_')}"
    slug = re.sub(r"[^a-z0-9]+", "_", heading.lower()).strip("_")
    if slug:
        return f"sec_{slug}"
    return f"sec_{idx}"


def split_into_sections(lines: Sequence[LineInfo], headings: Sequence[HeadingCandidate]) -> List[Dict[str, Any]]:
    if not headings:
        content = merge_paragraph_lines([ln.text for ln in lines])
        figures, formulas = extract_figures_and_formulas(content)
        return [
            {
                "id": "sec_1",
                "heading": "Document",
                "level": 1,
                "page_start": lines[0].page_number if lines else 1,
                "page_end": lines[-1].page_number if lines else 1,
                "content": content,
                "figures_referenced": figures,
                "formulas_referenced": formulas,
            }
        ]

    sections: List[Dict[str, Any]] = []
    heading_sorted = sorted(headings, key=lambda h: h.line_index)

    for i, hd in enumerate(heading_sorted):
        start = hd.line_index + 1
        end = heading_sorted[i + 1].line_index if i + 1 < len(heading_sorted) else len(lines)
        body_lines = [ln.text for ln in lines[start:end]]
        content = merge_paragraph_lines(body_lines)

        if hd.text.lower() == "references":
            count = extract_references_count(content)
            content = f"References: {count} entries"

        figures, formulas = extract_figures_and_formulas(content)
        page_start = lines[hd.line_index].page_number
        page_end = lines[end - 1].page_number if end - 1 >= 0 and end - 1 < len(lines) else page_start

        sections.append(
            {
                "id": section_id_from_heading(hd.text, i + 1),
                "heading": hd.text,
                "level": hd.level,
                "page_start": page_start,
                "page_end": page_end,
                "content": content,
                "figures_referenced": figures,
                "formulas_referenced": formulas,
            }
        )

    return sections


def extract_title_and_authors(lines: Sequence[LineInfo], body_size: float) -> Tuple[str, List[str]]:
    page1 = [ln for ln in lines if ln.page_number == 1]
    if not page1:
        return "", []

    title_line = max(page1, key=lambda ln: ln.font_size)
    title = title_line.text.strip()
    title_idx = page1.index(title_line)

    abstract_idx = next(
        (i for i, ln in enumerate(page1) if normalize_space(ln.text.lower()) == "abstract"),
        len(page1),
    )

    author_candidates: List[str] = []
    for ln in page1[title_idx + 1 : abstract_idx]:
        text = normalize_space(ln.text)
        if not text:
            continue
        if ln.font_size >= title_line.font_size - 0.1:
            continue
        if re.search(r"@|university|institute|department|laboratory", text, re.IGNORECASE):
            continue
        if len(text) > 200:
            continue
        if ln.font_size < body_size - 1.0:
            continue
        author_candidates.append(text)

    author_blob = " ".join(author_candidates)
    author_blob = re.sub(r"\b(and|&)\b", ",", author_blob)
    author_blob = re.sub(r"\s+", " ", author_blob)
    parts = [re.sub(r"\d+$", "", part).strip() for part in author_blob.split(",")]
    authors = [p for p in parts if p and 2 <= len(p) <= 80]

    unique_authors: List[str] = []
    seen = set()
    for author in authors:
        key = author.lower()
        if key in seen:
            continue
        seen.add(key)
        unique_authors.append(author)

    return title, unique_authors


def extract_abstract_from_sections(sections: Sequence[Dict[str, Any]]) -> str:
    for sec in sections:
        if normalize_space(sec.get("heading", "").lower()) == "abstract":
            return str(sec.get("content", "")).strip()
    return ""


def parse_pdf_to_sections(pdf_path: Path, output_dir: Path) -> Dict[str, Any]:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if not pdf_path.is_file():
        raise ValueError(f"PDF path is not a file: {pdf_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        raise RuntimeError(f"Unable to open PDF: {pdf_path}") from exc

    with doc:
        spans, page_lines, page_widths = extract_spans_and_lines(doc)
        total_pages = len(doc)

    ordered_pages = sorted_page_lines(page_lines, page_widths)
    cleaned_pages = remove_headers_footers(ordered_pages, total_pages)
    ordered_lines = collect_ordered_lines(cleaned_pages)

    if not ordered_lines:
        LOGGER.warning("No text extracted from %s", pdf_path)
        data = {
            "title": "",
            "authors": [],
            "abstract": "",
            "sections": [],
            "stats": {
                "total_pages": total_pages,
                "total_sections": 0,
                "total_figure_refs": 0,
                "total_formula_refs": 0,
            },
        }
        out_file = output_dir / "sections.json"
        out_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data

    body_size = body_font_size(spans)
    max_size = largest_font_size(spans)

    headings = detect_headings(ordered_lines, body_size, max_size)
    if not headings:
        LOGGER.warning("No clear headings detected in %s; using fallback single section", pdf_path)

    sections = split_into_sections(ordered_lines, headings)
    title, authors = extract_title_and_authors(ordered_lines, body_size)
    abstract = extract_abstract_from_sections(sections)

    total_figure_refs = sum(len(sec["figures_referenced"]) for sec in sections)
    total_formula_refs = sum(len(sec["formulas_referenced"]) for sec in sections)

    data: Dict[str, Any] = {
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "sections": sections,
        "stats": {
            "total_pages": total_pages,
            "total_sections": len(sections),
            "total_figure_refs": total_figure_refs,
            "total_formula_refs": total_formula_refs,
        },
    }

    out_file = output_dir / "sections.json"
    out_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def main(argv: Sequence[str]) -> int:
    configure_logging()

    if len(argv) != 3:
        print("Usage: python pdf_to_sections.py <pdf_path> <output_dir>")
        return 2

    pdf_path = Path(argv[1]).expanduser().resolve()
    output_dir = Path(argv[2]).expanduser().resolve()

    try:
        result = parse_pdf_to_sections(pdf_path, output_dir)
    except Exception as exc:
        LOGGER.error("Failed to parse PDF: %s", exc)
        return 1

    print(
        "Parsed {sections} sections across {pages} pages. Title: {title}".format(
            sections=result["stats"]["total_sections"],
            pages=result["stats"]["total_pages"],
            title=result.get("title") or "<unknown>",
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
