#!/usr/bin/env python3
# pyright: reportMissingImports=false, reportDeprecated=false, reportUnusedCallResult=false
# basedpyright: reportAny=false, reportExplicitAny=false, reportUnnecessaryTypeIgnoreComment=false
from __future__ import annotations

import json
import logging
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import median
from typing import Any, Optional


LOG = logging.getLogger("extract_formulas")


def import_fitz() -> Any:
    try:
        import fitz  # pyright: ignore[reportMissingImports]

        return fitz
    except Exception as exc:
        raise RuntimeError(
            "PyMuPDF is required. Install with: pip install pymupdf"
        ) from exc


UNICODE_TO_LATEX: dict[str, str] = {
    "α": r"\\alpha",
    "β": r"\\beta",
    "γ": r"\\gamma",
    "δ": r"\\delta",
    "ε": r"\\epsilon",
    "ζ": r"\\zeta",
    "η": r"\\eta",
    "θ": r"\\theta",
    "ι": r"\\iota",
    "κ": r"\\kappa",
    "λ": r"\\lambda",
    "μ": r"\\mu",
    "ν": r"\\nu",
    "ξ": r"\\xi",
    "ο": "o",
    "π": r"\\pi",
    "ρ": r"\\rho",
    "σ": r"\\sigma",
    "τ": r"\\tau",
    "υ": r"\\upsilon",
    "φ": r"\\phi",
    "χ": r"\\chi",
    "ψ": r"\\psi",
    "ω": r"\\omega",
    "ϑ": r"\\vartheta",
    "ϕ": r"\\varphi",
    "ϖ": r"\\varpi",
    "ϱ": r"\\varrho",
    "ϵ": r"\\varepsilon",
    "Γ": r"\\Gamma",
    "Δ": r"\\Delta",
    "Θ": r"\\Theta",
    "Λ": r"\\Lambda",
    "Ξ": r"\\Xi",
    "Π": r"\\Pi",
    "Σ": r"\\sum",
    "Υ": r"\\Upsilon",
    "Φ": r"\\Phi",
    "Ψ": r"\\Psi",
    "Ω": r"\\Omega",
    "∑": r"\\sum",
    "∏": r"\\prod",
    "∐": r"\\coprod",
    "∫": r"\\int",
    "∬": r"\\iint",
    "∭": r"\\iiint",
    "∮": r"\\oint",
    "∞": r"\\infty",
    "∂": r"\\partial",
    "∇": r"\\nabla",
    "√": r"\\sqrt{}",
    "∝": r"\\propto",
    "∈": r"\\in",
    "∉": r"\\notin",
    "∋": r"\\ni",
    "∅": r"\\emptyset",
    "∧": r"\\wedge",
    "∨": r"\\vee",
    "¬": r"\\neg",
    "∀": r"\\forall",
    "∃": r"\\exists",
    "∄": r"\\nexists",
    "∴": r"\\therefore",
    "∵": r"\\because",
    "≈": r"\\approx",
    "≅": r"\\cong",
    "≃": r"\\simeq",
    "≡": r"\\equiv",
    "≠": r"\\neq",
    "≤": r"\\leq",
    "≥": r"\\geq",
    "≪": r"\\ll",
    "≫": r"\\gg",
    "⊂": r"\\subset",
    "⊃": r"\\supset",
    "⊆": r"\\subseteq",
    "⊇": r"\\supseteq",
    "⊄": r"\\nsubset",
    "⊅": r"\\nsupset",
    "⊊": r"\\subsetneq",
    "⊋": r"\\supsetneq",
    "⊑": r"\\sqsubseteq",
    "⊒": r"\\sqsupseteq",
    "⊓": r"\\sqcap",
    "⊔": r"\\sqcup",
    "∪": r"\\cup",
    "∩": r"\\cap",
    "⊎": r"\\uplus",
    "⊗": r"\\otimes",
    "⊕": r"\\oplus",
    "⊙": r"\\odot",
    "⊖": r"\\ominus",
    "⊘": r"\\oslash",
    "⊥": r"\\perp",
    "∥": r"\\parallel",
    "∦": r"\\nparallel",
    "∼": r"\\sim",
    "←": r"\\leftarrow",
    "→": r"\\rightarrow",
    "↔": r"\\leftrightarrow",
    "↑": r"\\uparrow",
    "↓": r"\\downarrow",
    "⇐": r"\\Leftarrow",
    "⇒": r"\\Rightarrow",
    "⇔": r"\\Leftrightarrow",
    "↦": r"\\mapsto",
    "↗": r"\\nearrow",
    "↘": r"\\searrow",
    "↙": r"\\swarrow",
    "↖": r"\\nwarrow",
    "±": r"\\pm",
    "∓": r"\\mp",
    "×": r"\\times",
    "÷": r"\\div",
    "⋅": r"\\cdot",
    "…": r"\\ldots",
    "⋯": r"\\cdots",
    "∠": r"\\angle",
    "⊢": r"\\vdash",
    "⊣": r"\\dashv",
    "⊨": r"\\models",
    "⊭": r"\\not\\models",
    "ℓ": r"\\ell",
    "ℜ": r"\\Re",
    "ℑ": r"\\Im",
    "ℕ": r"\\mathbb{N}",
    "ℤ": r"\\mathbb{Z}",
    "ℚ": r"\\mathbb{Q}",
    "ℝ": r"\\mathbb{R}",
    "ℂ": r"\\mathbb{C}",
    "ℙ": r"\\mathbb{P}",
    "ℱ": r"\\mathcal{F}",
    "𝒟": r"\\mathcal{D}",
    "°": r"^\\circ",
    "′": "'",
    "″": "''",
}


SUPERSCRIPT_MAP: dict[str, str] = {
    "⁰": "0",
    "¹": "1",
    "²": "2",
    "³": "3",
    "⁴": "4",
    "⁵": "5",
    "⁶": "6",
    "⁷": "7",
    "⁸": "8",
    "⁹": "9",
    "⁺": "+",
    "⁻": "-",
    "⁼": "=",
    "⁽": "(",
    "⁾": ")",
    "ⁿ": "n",
    "ⁱ": "i",
}


SUBSCRIPT_MAP: dict[str, str] = {
    "₀": "0",
    "₁": "1",
    "₂": "2",
    "₃": "3",
    "₄": "4",
    "₅": "5",
    "₆": "6",
    "₇": "7",
    "₈": "8",
    "₉": "9",
    "₊": "+",
    "₋": "-",
    "₌": "=",
    "₍": "(",
    "₎": ")",
    "ₐ": "a",
    "ₑ": "e",
    "ₕ": "h",
    "ᵢ": "i",
    "ⱼ": "j",
    "ₖ": "k",
    "ₗ": "l",
    "ₘ": "m",
    "ₙ": "n",
    "ₒ": "o",
    "ₚ": "p",
    "ᵣ": "r",
    "ₛ": "s",
    "ₜ": "t",
    "ᵤ": "u",
    "ᵥ": "v",
    "ₓ": "x",
}


EQUATION_NUMBER_RE = re.compile(
    r"(?:^|\s)(?:\((\d+(?:\.\d+)?)\)|\[(\d+(?:\.\d+)?)\]|Eq\.?\s*\(?\d+(?:\.\d+)?\)?|Equation\s*\(?\d+(?:\.\d+)?\)?)",
    re.IGNORECASE,
)
LATEX_CMD_RE = re.compile(r"\\[A-Za-z]+")
HEADING_RE = re.compile(
    r"^(?:\d+(?:\.\d+){0,3}\s+.+|[A-Z][A-Z\s\-]{3,}|(?:Abstract|Introduction|Related Work|Method|Methods|Experiment|Experiments|Conclusion)s?)$"
)


@dataclass
class FormulaRecord:
    id: str
    latex: Optional[str]
    raw_text: str
    page: int
    section: str
    context_before: str
    context_after: str
    extraction_method: str
    confidence: str
    fallback_image: Optional[str]


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def is_section_heading(text: str) -> bool:
    candidate = normalize_whitespace(text)
    if not candidate or len(candidate) > 120:
        return False
    if HEADING_RE.match(candidate):
        return True
    words = candidate.split()
    if 1 <= len(words) <= 8 and sum(1 for w in words if w[:1].isupper()) >= max(1, len(words) - 1):
        return True
    return False


def split_sentences(text: str) -> list[str]:
    cleaned = normalize_whitespace(text)
    if not cleaned:
        return []
    return [s.strip() for s in re.split(r"(?<=[.!?。！？])\s+", cleaned) if s.strip()]


def block_text(block: dict[str, Any]) -> str:
    lines: list[str] = []
    for line in block.get("lines", []):
        line_text = "".join(span.get("text", "") for span in line.get("spans", []))
        if line_text.strip():
            lines.append(line_text)
    return "\n".join(lines).strip()


def has_equation_numbering(text: str) -> bool:
    return bool(EQUATION_NUMBER_RE.search(text))


def math_signal_score(text: str) -> int:
    score = 0
    score += len(re.findall(r"[=+\-*/^_]", text))
    score += len(re.findall(r"[∑∏∫√≈≠≤≥∈∀∃λθμσπ∥]", text))
    score += len(LATEX_CMD_RE.findall(text)) * 2
    score += len(re.findall(r"\b(?:sin|cos|tan|log|exp|min|max)\b", text, flags=re.IGNORECASE))
    return score


def is_formula_candidate(text: str) -> bool:
    t = normalize_whitespace(text)
    if not t:
        return False
    if has_equation_numbering(t):
        return True
    if math_signal_score(t) >= 3 and any(ch.isdigit() for ch in t):
        return True
    if math_signal_score(t) >= 5:
        return True
    return False


def looks_garbled_math(text: str) -> bool:
    if not text.strip() or "�" in text:
        return True
    non_printable = sum(1 for ch in text if ord(ch) < 32 and ch not in "\n\t")
    if non_printable > 0:
        return True
    weird = sum(
        1
        for ch in text
        if ord(ch) > 127 and ch not in UNICODE_TO_LATEX and ch not in SUPERSCRIPT_MAP and ch not in SUBSCRIPT_MAP
    )
    return weird / max(1, len(text)) > 0.25 and math_signal_score(text) < 4


def unicode_math_to_latex(text: str) -> str:
    pieces: list[str] = []
    for ch in text:
        if ch in SUPERSCRIPT_MAP:
            pieces.append(f"^{{{SUPERSCRIPT_MAP[ch]}}}")
        elif ch in SUBSCRIPT_MAP:
            pieces.append(f"_{{{SUBSCRIPT_MAP[ch]}}}")
        else:
            pieces.append(UNICODE_TO_LATEX.get(ch, ch))
    return normalize_whitespace("".join(pieces))


def gather_spans(block: dict[str, Any]) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            if span.get("text", "").strip():
                spans.append(span)
    spans.sort(key=lambda s: (float(s.get("bbox", [0, 0, 0, 0])[1]), float(s.get("bbox", [0, 0, 0, 0])[0])))
    return spans


def span_based_super_sub_latex(spans: list[dict[str, Any]]) -> str:
    if not spans:
        return ""
    sizes = [float(s.get("size", 0.0)) for s in spans if float(s.get("size", 0.0)) > 0.0]
    if not sizes:
        return unicode_math_to_latex("".join(s.get("text", "") for s in spans))
    median_size = median(sizes)
    baseline = median(float(s.get("bbox", [0, 0, 0, 0])[3]) for s in spans)
    parts: list[str] = []
    for span in spans:
        body = unicode_math_to_latex(span.get("text", ""))
        size = float(span.get("size", median_size))
        bbox = span.get("bbox", [0, 0, 0, 0])
        center_y = (float(bbox[1]) + float(bbox[3])) / 2.0
        if size < median_size * 0.82 and center_y < baseline - median_size * 0.18:
            parts.append(f"^{{{body}}}")
        elif size < median_size * 0.82 and center_y > baseline + median_size * 0.12:
            parts.append(f"_{{{body}}}")
        else:
            parts.append(body)
    return normalize_whitespace(" ".join(parts))


def line_text_and_bbox(block: dict[str, Any]) -> list[tuple[str, tuple[float, float, float, float]]]:
    rows: list[tuple[str, tuple[float, float, float, float]]] = []
    for line in block.get("lines", []):
        spans = line.get("spans", [])
        text = "".join(span.get("text", "") for span in spans).strip()
        if not text:
            continue
        bboxes = [span.get("bbox", [0, 0, 0, 0]) for span in spans]
        x0 = min(float(b[0]) for b in bboxes)
        y0 = min(float(b[1]) for b in bboxes)
        x1 = max(float(b[2]) for b in bboxes)
        y1 = max(float(b[3]) for b in bboxes)
        rows.append((text, (x0, y0, x1, y1)))
    return rows


def detect_fraction_from_layout(block: dict[str, Any]) -> Optional[str]:
    rows = line_text_and_bbox(block)
    if len(rows) < 3:
        return None
    for i in range(1, len(rows) - 1):
        bar_text, bar_box = rows[i]
        if not re.fullmatch(r"[-‐‑‒–—―_=]+", bar_text):
            continue
        num_text, num_box = rows[i - 1]
        den_text, den_box = rows[i + 1]
        bar_x0, _, bar_x1, _ = bar_box
        overlap_num = max(0.0, min(bar_x1, num_box[2]) - max(bar_x0, num_box[0]))
        overlap_den = max(0.0, min(bar_x1, den_box[2]) - max(bar_x0, den_box[0]))
        width = max(1.0, bar_x1 - bar_x0)
        if overlap_num / width > 0.35 and overlap_den / width > 0.35:
            return rf"\\frac{{{unicode_math_to_latex(num_text)}}}{{{unicode_math_to_latex(den_text)}}}"
    return None


def reconstruct_latex(block: dict[str, Any], raw_text: str) -> Optional[str]:
    raw = normalize_whitespace(raw_text)
    if not raw:
        return None
    if LATEX_CMD_RE.search(raw):
        return raw
    fraction = detect_fraction_from_layout(block)
    span_latex = span_based_super_sub_latex(gather_spans(block))
    base = span_latex if span_latex else unicode_math_to_latex(raw)
    if fraction and base:
        return normalize_whitespace(f"{fraction} {base}")
    if fraction:
        return fraction
    if base and math_signal_score(base) >= 2:
        return base
    return None


def extract_context(block_texts: list[str], idx: int) -> tuple[str, str]:
    before = " ".join(block_texts[max(0, idx - 4) : idx])
    after = " ".join(block_texts[idx + 1 : idx + 5])
    before_sents = split_sentences(before)
    after_sents = split_sentences(after)
    return (
        " ".join(before_sents[-2:]) if before_sents else "",
        " ".join(after_sents[:2]) if after_sents else "",
    )


def save_formula_region_image(
    page: Any,
    bbox: tuple[float, float, float, float],
    formula_id: str,
    images_dir: Path,
) -> Optional[str]:
    try:
        fitz = import_fitz()
        rect = fitz.Rect(bbox)
        margin = 8.0
        clip = fitz.Rect(
            max(0.0, rect.x0 - margin),
            max(0.0, rect.y0 - margin),
            min(page.rect.width, rect.x1 + margin),
            min(page.rect.height, rect.y1 + margin),
        )
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0), clip=clip, alpha=False)
        filename = f"{formula_id}_region.png"
        (images_dir / filename).write_bytes(pix.tobytes("png"))
        return str(Path("formula_images") / filename)
    except Exception as exc:
        LOG.error("Failed to render fallback image %s: %s", formula_id, exc)
        return None


def bbox_from_block(block: dict[str, Any]) -> tuple[float, float, float, float]:
    b = block.get("bbox", [0, 0, 0, 0])
    return float(b[0]), float(b[1]), float(b[2]), float(b[3])


def numbering_word_regions(page: Any) -> list[tuple[float, float, float, float]]:
    regions: list[tuple[float, float, float, float]] = []
    for word in page.get_text("words"):
        x0, y0, x1, y1, token = float(word[0]), float(word[1]), float(word[2]), float(word[3]), str(word[4])
        if EQUATION_NUMBER_RE.search(f" {token} "):
            pad_x = max(60.0, (x1 - x0) * 8)
            pad_y = max(18.0, (y1 - y0) * 2)
            regions.append((max(0.0, x0 - pad_x), max(0.0, y0 - pad_y), min(page.rect.width, x1 + pad_x), min(page.rect.height, y1 + pad_y)))
    return regions


def dedupe_regions(regions: list[tuple[float, float, float, float]]) -> list[tuple[float, float, float, float]]:
    output: list[tuple[float, float, float, float]] = []
    for region in regions:
        rx0, ry0, rx1, ry1 = region
        keep = True
        for ox0, oy0, ox1, oy1 in output:
            inter_w = max(0.0, min(rx1, ox1) - max(rx0, ox0))
            inter_h = max(0.0, min(ry1, oy1) - max(ry0, oy0))
            inter = inter_w * inter_h
            area = max(1.0, (rx1 - rx0) * (ry1 - ry0))
            if inter / area > 0.65:
                keep = False
                break
        if keep:
            output.append(region)
    return output


def extract_formulas(pdf_path: Path, output_dir: Path) -> dict[str, Any]:
    formulas: list[FormulaRecord] = []
    formula_counter = 1
    current_section = "Unknown"
    images_dir = output_dir / "formula_images"
    images_dir.mkdir(parents=True, exist_ok=True)

    fitz = import_fitz()
    with fitz.open(pdf_path) as doc:
        for page_idx in range(doc.page_count):
            page = doc.load_page(page_idx)
            page_num = page_idx + 1
            try:
                page_dict = page.get_text("dict")
            except Exception as exc:
                LOG.error("Page %d dict extraction failed: %s", page_num, exc)
                eq_id = f"eq{formula_counter}"
                fallback = save_formula_region_image(
                    page,
                    (0.0, 0.0, min(page.rect.width, 600.0), min(page.rect.height, 240.0)),
                    eq_id,
                    images_dir,
                )
                formulas.append(
                    FormulaRecord(
                        id=eq_id,
                        latex=None,
                        raw_text=f"[page_text_extraction_error] {exc}",
                        page=page_num,
                        section=current_section,
                        context_before="",
                        context_after="",
                        extraction_method="visual_fallback",
                        confidence="low",
                        fallback_image=fallback,
                    )
                )
                formula_counter += 1
                continue

            blocks = [b for b in page_dict.get("blocks", []) if b.get("type") == 0]
            blocks.sort(key=lambda b: (float(b.get("bbox", [0, 0, 0, 0])[1]), float(b.get("bbox", [0, 0, 0, 0])[0])))
            block_texts = [block_text(b) for b in blocks]
            page_text = normalize_whitespace(" ".join(block_texts))
            page_has_numbering = has_equation_numbering(page_text)
            page_detected = 0

            for idx, block in enumerate(blocks):
                text = block_texts[idx]
                if is_section_heading(text):
                    current_section = normalize_whitespace(text)
                if not is_formula_candidate(text):
                    continue

                page_detected += 1
                eq_id = f"eq{formula_counter}"
                raw_text = normalize_whitespace(text) or "[garbled]"
                context_before, context_after = extract_context(block_texts, idx)
                bbox = bbox_from_block(block)

                try:
                    latex = reconstruct_latex(block, raw_text)
                    if looks_garbled_math(raw_text) and page_has_numbering:
                        fallback = save_formula_region_image(page, bbox, eq_id, images_dir)
                        formulas.append(
                            FormulaRecord(
                                id=eq_id,
                                latex=None,
                                raw_text=raw_text,
                                page=page_num,
                                section=current_section,
                                context_before=context_before,
                                context_after=context_after,
                                extraction_method="visual_fallback",
                                confidence="low",
                                fallback_image=fallback,
                            )
                        )
                    else:
                        formulas.append(
                            FormulaRecord(
                                id=eq_id,
                                latex=latex,
                                raw_text=raw_text,
                                page=page_num,
                                section=current_section,
                                context_before=context_before,
                                context_after=context_after,
                                extraction_method="text",
                                confidence="high" if latex else "low",
                                fallback_image=None,
                            )
                        )
                except Exception as exc:
                    LOG.error("Formula extraction failed for %s (page %d): %s", eq_id, page_num, exc)
                    fallback = save_formula_region_image(page, bbox, eq_id, images_dir)
                    formulas.append(
                        FormulaRecord(
                            id=eq_id,
                            latex=None,
                            raw_text=f"[extraction_error] {raw_text}",
                            page=page_num,
                            section=current_section,
                            context_before=context_before,
                            context_after=context_after,
                            extraction_method="visual_fallback",
                            confidence="low",
                            fallback_image=fallback,
                        )
                    )
                formula_counter += 1

            if page_has_numbering and page_detected == 0:
                for region in dedupe_regions(numbering_word_regions(page)):
                    eq_id = f"eq{formula_counter}"
                    fallback = save_formula_region_image(page, region, eq_id, images_dir)
                    formulas.append(
                        FormulaRecord(
                            id=eq_id,
                            latex=None,
                            raw_text="[garbled]",
                            page=page_num,
                            section=current_section,
                            context_before="",
                            context_after="",
                            extraction_method="visual_fallback",
                            confidence="low",
                            fallback_image=fallback,
                        )
                    )
                    formula_counter += 1

    text_count = sum(1 for f in formulas if f.extraction_method == "text")
    visual_count = sum(1 for f in formulas if f.extraction_method == "visual_fallback")
    return {
        "formulas": [asdict(f) for f in formulas],
        "stats": {
            "total_detected": len(formulas),
            "text_extracted": text_count,
            "visual_fallback": visual_count,
        },
    }


def validate_inputs(pdf_path: Path, output_dir: Path) -> None:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if not pdf_path.is_file():
        raise ValueError(f"PDF path is not a file: {pdf_path}")
    output_dir.mkdir(parents=True, exist_ok=True)


def main(argv: list[str]) -> int:
    configure_logging()
    if len(argv) != 3:
        print("Usage: python extract_formulas.py <pdf_path> <output_dir>")
        return 1

    pdf_path = Path(argv[1]).expanduser().resolve()
    output_dir = Path(argv[2]).expanduser().resolve()

    try:
        validate_inputs(pdf_path, output_dir)
    except Exception as exc:
        LOG.error("Input validation failed: %s", exc)
        return 2

    try:
        result = extract_formulas(pdf_path, output_dir)
        (output_dir / "formulas.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as exc:
        LOG.exception("Formula extraction failed: %s", exc)
        return 3

    total = int(result["stats"]["total_detected"])
    text_count = int(result["stats"]["text_extracted"])
    visual_count = int(result["stats"]["visual_fallback"])
    print(f"Detected {total} formulas: {text_count} extracted as LaTeX, {visual_count} need visual recognition")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
