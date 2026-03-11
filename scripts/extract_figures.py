# pyright: basic

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import fitz  # pyright: ignore[reportMissingImports]
from PIL import Image  # pyright: ignore[reportMissingImports]


FIG_RE = re.compile(r"^\s*(?:Figure|Fig\.?)\s*(\d+)\b", re.IGNORECASE)
TABLE_RE = re.compile(r"^\s*TABLE\s+([IVXLC0-9]+)\b")
NUMBER_TOKEN_RE = re.compile(r"\d+(?:\.\d+)?")
MIN_FIG_DIM = 80


@dataclass
class Caption:
    kind: str
    ident: str
    page_index: int
    text: str
    bbox: fitz.Rect


@dataclass
class ImageBlock:
    bbox: fitz.Rect
    width: int
    height: int


@dataclass
class TextLine:
    bbox: fitz.Rect
    text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract figures/tables and generate figure_map.json")
    parser.add_argument("pdf_path", type=Path)
    parser.add_argument("output_images_dir", type=Path)
    return parser.parse_args()


def normalize_id(kind: str, raw_id: str) -> str:
    if kind == "fig":
        return f"fig{int(raw_id)}"
    return f"table_{raw_id.lower()}"


def read_page_dict(page: fitz.Page) -> Dict[str, Any]:
    data = page.get_text("dict")
    if isinstance(data, dict):
        return data
    return {"blocks": []}


def detect_captions(page_dict: Dict[str, Any], page_index: int) -> List[Caption]:
    out: List[Caption] = []
    for block in page_dict.get("blocks", []):
        if not isinstance(block, dict) or block.get("type") != 0:
            continue

        parts: List[str] = []
        for line in block.get("lines", []):
            if not isinstance(line, dict):
                continue
            text = "".join(
                span.get("text", "") for span in line.get("spans", []) if isinstance(span, dict)
            ).strip()
            if text:
                parts.append(text)
        if not parts:
            continue

        full_text = " ".join(parts).strip()
        fig_match = FIG_RE.match(full_text)
        table_match = TABLE_RE.match(full_text)
        if not fig_match and not table_match:
            continue

        match = fig_match if fig_match else table_match
        if match is None:
            continue

        raw_id = match.group(1)
        if not isinstance(raw_id, str) or not raw_id:
            continue

        bbox_data = block.get("bbox")
        if bbox_data is None:
            continue

        kind = "fig" if fig_match else "table"
        out.append(
            Caption(
                kind=kind,
                ident=normalize_id(kind, raw_id),
                page_index=page_index,
                text=full_text,
                bbox=fitz.Rect(bbox_data),
            )
        )
    return out


def detect_image_blocks(page_dict: Dict[str, Any]) -> List[ImageBlock]:
    out: List[ImageBlock] = []
    for block in page_dict.get("blocks", []):
        if not isinstance(block, dict) or block.get("type") != 1:
            continue
        bbox_data = block.get("bbox")
        width = block.get("width")
        height = block.get("height")
        if bbox_data is None or not isinstance(width, int) or not isinstance(height, int):
            continue
        out.append(ImageBlock(bbox=fitz.Rect(bbox_data), width=width, height=height))
    return out


def detect_text_lines(page_dict: Dict[str, Any]) -> List[TextLine]:
    out: List[TextLine] = []
    for block in page_dict.get("blocks", []):
        if not isinstance(block, dict) or block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            if not isinstance(line, dict):
                continue
            text = "".join(
                span.get("text", "") for span in line.get("spans", []) if isinstance(span, dict)
            ).strip()
            if not text:
                continue
            bbox_data = line.get("bbox")
            if bbox_data is None:
                continue
            out.append(TextLine(bbox=fitz.Rect(bbox_data), text=text))
    return out


def detect_horizontal_line_rects(page: fitz.Page) -> List[fitz.Rect]:
    min_width = page.rect.width * 0.20
    out: List[fitz.Rect] = []
    for drawing in page.get_drawings():
        width_obj = drawing.get("width", 1.0)
        stroke = float(width_obj) if isinstance(width_obj, (int, float)) else 1.0
        thick = max(0.8, stroke)
        for item in drawing.get("items", []):
            if not item:
                continue
            op = item[0]
            if op == "l":
                p1, p2 = item[1], item[2]
                if abs(p1.y - p2.y) > 1.2:
                    continue
                x0 = min(p1.x, p2.x)
                x1 = max(p1.x, p2.x)
                if x1 - x0 < min_width:
                    continue
                y = (p1.y + p2.y) / 2.0
                out.append(fitz.Rect(x0, y - thick, x1, y + thick))
            elif op == "re":
                rect = fitz.Rect(item[1])
                if rect.width >= min_width and rect.height <= 3.0:
                    out.append(rect)
    return out


def cluster_horizontal_lines(line_rects: Sequence[fitz.Rect], page_width: float) -> List[Tuple[fitz.Rect, int]]:
    if not line_rects:
        return []

    buckets: Dict[Tuple[int, int], List[fitz.Rect]] = {}
    for rect in line_rects:
        key = (int(round(rect.x0 / 8.0)), int(round(rect.x1 / 8.0)))
        buckets.setdefault(key, []).append(rect)

    groups: List[List[fitz.Rect]] = []
    for rects in buckets.values():
        ordered = sorted(rects, key=lambda rect: rect.y0)
        current: List[fitz.Rect] = [ordered[0]]
        for rect in ordered[1:]:
            if rect.y0 - current[-1].y1 <= 120.0:
                current.append(rect)
            else:
                groups.append(current)
                current = [rect]
        groups.append(current)

    clusters: List[Tuple[fitz.Rect, int]] = []
    for group in groups:
        if len(group) < 3:
            continue
        merged = fitz.Rect(group[0])
        for rect in group[1:]:
            merged.include_rect(rect)
        if merged.width < page_width * 0.25:
            continue
        if merged.height < 18.0:
            continue
        clusters.append((merged, len(group)))
    return clusters


def clamp_rect(rect: fitz.Rect, page_rect: fitz.Rect) -> fitz.Rect:
    out = fitz.Rect(rect)
    out &= page_rect
    return out


def render_crop(page: fitz.Page, rect: fitz.Rect, dpi: int = 220) -> Image.Image:
    pix = page.get_pixmap(dpi=dpi, clip=rect, alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def block_is_face_like(block: ImageBlock) -> bool:
    return block.width <= 420 and block.height <= 460


def block_is_usable_figure(block: ImageBlock) -> bool:
    if block_is_face_like(block):
        return False
    return block.width >= 900 and block.height >= 500


def figure_caption_score(caption: Caption, image_block: ImageBlock) -> float:
    if caption.bbox.y0 >= image_block.bbox.y1:
        direction_penalty = 0.0
    elif caption.bbox.y1 <= image_block.bbox.y0:
        direction_penalty = 18.0
    else:
        direction_penalty = 40.0

    cx = (caption.bbox.x0 + caption.bbox.x1) / 2.0
    ix = (image_block.bbox.x0 + image_block.bbox.x1) / 2.0
    dx = abs(cx - ix)
    dy = min(
        abs(caption.bbox.y0 - image_block.bbox.y1),
        abs(image_block.bbox.y0 - caption.bbox.y1),
    )
    return dy + dx * 0.35 + direction_penalty


def numeric_token_count(text: str) -> int:
    return len(NUMBER_TOKEN_RE.findall(text))


def is_table_like_line(text: str) -> bool:
    s = text.strip()
    if len(s) < 6:
        return False
    nums = numeric_token_count(s)
    if nums >= 3:
        return True
    upper = s.upper()
    has_metric = any(token in upper for token in ("SM", "EM", "MAE", "METHOD", "BACKBONE", "VT"))
    return has_metric and nums >= 1 and len(s.split()) >= 4


def union_rect(lines: Sequence[TextLine]) -> fitz.Rect:
    rect = fitz.Rect(lines[0].bbox)
    for line in lines[1:]:
        rect.include_rect(line.bbox)
    return rect


def group_lines(lines: Sequence[TextLine], gap: float = 11.0) -> List[List[TextLine]]:
    if not lines:
        return []
    ordered = sorted(lines, key=lambda line: (line.bbox.y0, line.bbox.x0))
    groups: List[List[TextLine]] = [[ordered[0]]]
    for line in ordered[1:]:
        prev = groups[-1][-1]
        if line.bbox.y0 - prev.bbox.y1 <= gap:
            groups[-1].append(line)
        else:
            groups.append([line])
    return groups


def table_crop_from_clusters(
    caption: Caption,
    clusters: Sequence[Tuple[fitz.Rect, int]],
    page_rect: fitz.Rect,
    used_cluster_indices: set[int],
) -> Tuple[int, fitz.Rect] | None:
    best_rect: fitz.Rect | None = None
    best_score = float("-inf")
    best_index = -1
    for idx, pair in enumerate(clusters):
        if idx in used_cluster_indices:
            continue
        rect, count = pair
        if rect.y0 >= caption.bbox.y1:
            dist = rect.y0 - caption.bbox.y1
            direction_bonus = 5.0
        elif rect.y1 <= caption.bbox.y0:
            dist = caption.bbox.y0 - rect.y1
            direction_bonus = 3.0
        else:
            dist = 0.0
            direction_bonus = 1.0

        if dist > page_rect.height * 0.48:
            continue

        width_ratio = rect.width / max(1.0, page_rect.width)
        score = width_ratio * 22.0 + count * 2.5 + direction_bonus - dist * 0.05
        if score > best_score:
            best_score = score
            best_rect = fitz.Rect(rect)
            best_index = idx

    if best_rect is None:
        return None

    pad_x = max(6.0, best_rect.width * 0.015)
    pad_y = max(6.0, best_rect.height * 0.04)
    expanded = clamp_rect(
        fitz.Rect(best_rect.x0 - pad_x, best_rect.y0 - pad_y, best_rect.x1 + pad_x, best_rect.y1 + pad_y),
        page_rect,
    )
    return best_index, expanded


def search_windows(captions: Sequence[Caption], idx: int, page_rect: fitz.Rect) -> List[fitz.Rect]:
    cap = captions[idx]
    prev_cap = captions[idx - 1] if idx > 0 else None
    next_cap = captions[idx + 1] if idx + 1 < len(captions) else None

    margin_x = page_rect.width * 0.03
    x0 = page_rect.x0 + margin_x
    x1 = page_rect.x1 - margin_x

    below_y0 = cap.bbox.y1 + 2.0
    below_limit = next_cap.bbox.y0 - 2.0 if next_cap else page_rect.y1 - 6.0
    below_y1 = min(below_limit, cap.bbox.y1 + page_rect.height * 0.70)

    above_y1 = cap.bbox.y0 - 2.0
    above_limit = prev_cap.bbox.y1 + 2.0 if prev_cap else page_rect.y0 + 6.0
    above_y0 = max(above_limit, cap.bbox.y0 - page_rect.height * 0.70)

    wins: List[fitz.Rect] = []
    if below_y1 - below_y0 > 28:
        wins.append(fitz.Rect(x0, below_y0, x1, below_y1))
    if above_y1 - above_y0 > 28:
        wins.append(fitz.Rect(x0, above_y0, x1, above_y1))
    return wins


def table_crop_from_text(page: fitz.Page, page_dict: Dict[str, Any], captions: Sequence[Caption], idx: int) -> fitz.Rect:
    page_rect = page.rect
    cap = captions[idx]
    lines = detect_text_lines(page_dict)
    best_rect: fitz.Rect | None = None
    best_score = float("-inf")

    for win in search_windows(captions, idx, page_rect):
        candidates: List[TextLine] = []
        for line in lines:
            if not line.bbox.intersects(win):
                continue
            if line.bbox.width < page_rect.width * 0.17:
                continue
            if not is_table_like_line(line.text):
                continue
            candidates.append(line)

        for group in group_lines(candidates):
            rect = union_rect(group)
            if rect.height < 18:
                continue
            width_ratio = rect.width / max(1.0, page_rect.width)
            digits = sum(numeric_token_count(line.text) for line in group)
            anchor_dist = min(abs(rect.y0 - cap.bbox.y1), abs(cap.bbox.y0 - rect.y1))
            score = digits * 0.55 + len(group) * 3.2 + width_ratio * 18.0 - anchor_dist * 0.025
            if score > best_score:
                best_score = score
                best_rect = rect

    if best_rect is None:
        margin = page_rect.width * 0.03
        y0 = max(page_rect.y0 + 6.0, cap.bbox.y1 + 2.0)
        y1 = min(page_rect.y1 - 6.0, y0 + page_rect.height * 0.50)
        best_rect = fitz.Rect(page_rect.x0 + margin, y0, page_rect.x1 - margin, y1)

    if best_rect.width < page_rect.width * 0.78:
        target = page_rect.width * 0.78
        cx = (best_rect.x0 + best_rect.x1) / 2.0
        best_rect = fitz.Rect(cx - target / 2.0, best_rect.y0, cx + target / 2.0, best_rect.y1)

    pad_x = max(5.0, best_rect.width * 0.02)
    pad_y = max(2.5, best_rect.height * 0.02)
    return clamp_rect(
        fitz.Rect(best_rect.x0 - pad_x, best_rect.y0 - pad_y, best_rect.x1 + pad_x, best_rect.y1 + pad_y),
        page_rect,
    )


def edge_ratio(image: Image.Image, side: str, threshold: int = 245, band: int = 4) -> float:
    gray = image.convert("L")
    w, h = gray.size
    if side == "left":
        crop = gray.crop((0, 0, min(band, w), h))
    elif side == "right":
        crop = gray.crop((max(0, w - band), 0, w, h))
    elif side == "top":
        crop = gray.crop((0, 0, w, min(band, h)))
    else:
        crop = gray.crop((0, max(0, h - band), w, h))
    values = list(crop.getdata())
    if not values:
        return 0.0
    return sum(1 for value in values if value < threshold) / float(len(values))


def refine_table_crop(page: fitz.Page, rect: fitz.Rect) -> fitz.Rect:
    page_rect = page.rect
    current = fitz.Rect(rect)
    for _ in range(3):
        image = render_crop(page, current)
        left = edge_ratio(image, "left")
        right = edge_ratio(image, "right")
        changed = False
        expand = max(10.0, page_rect.width * 0.02)
        if left > 0.03 and current.x0 > page_rect.x0 + 0.5:
            current.x0 -= expand
            changed = True
        if right > 0.03 and current.x1 < page_rect.x1 - 0.5:
            current.x1 += expand
            changed = True
        current = clamp_rect(current, page_rect)
        if not changed:
            break
    return current


def dedupe(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    best: Dict[str, Dict[str, Any]] = {}
    for entry in entries:
        key = str(entry["id"])
        area = int(entry["width"]) * int(entry["height"])
        old = best.get(key)
        if old is None:
            best[key] = entry
            continue
        old_area = int(old["width"]) * int(old["height"])
        if area > old_area:
            best[key] = entry
    return list(best.values())


def ensure_unique_stem(base_stem: str, used_stems: set[str]) -> str:
    if base_stem not in used_stems:
        used_stems.add(base_stem)
        return base_stem
    i = 2
    while True:
        name = f"{base_stem}_{i}"
        if name not in used_stems:
            used_stems.add(name)
            return name
        i += 1


def write_figure_map(output_images_dir: Path, figures: List[Dict[str, Any]]) -> None:
    out_path = output_images_dir.parent / "figure_map.json"
    payload = {"figures": sorted(figures, key=lambda item: str(item["id"]))}
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_figures(pdf_path: Path, output_images_dir: Path) -> Dict[str, int]:
    doc = fitz.open(pdf_path)
    entries: List[Dict[str, Any]] = []
    used_stems: set[str] = set()
    fig_count = 0
    table_count = 0

    with doc:
        for page_index in range(len(doc)):
            page = doc[page_index]
            page_dict = read_page_dict(page)
            captions = detect_captions(page_dict, page_index)
            fig_captions = sorted([c for c in captions if c.kind == "fig"], key=lambda c: c.bbox.y0)
            table_captions = sorted([c for c in captions if c.kind == "table"], key=lambda c: c.bbox.y0)

            image_blocks = [b for b in detect_image_blocks(page_dict) if block_is_usable_figure(b)]
            used_image_indices: set[int] = set()

            for caption in fig_captions:
                best_idx = -1
                best_score = float("inf")
                for i, block in enumerate(image_blocks):
                    if i in used_image_indices:
                        continue
                    score = figure_caption_score(caption, block)
                    if score < best_score:
                        best_score = score
                        best_idx = i

                if best_idx < 0:
                    continue

                used_image_indices.add(best_idx)
                block = image_blocks[best_idx]
                pad_x = page.rect.width * 0.006
                pad_y = page.rect.height * 0.006
                rect = clamp_rect(
                    fitz.Rect(
                        block.bbox.x0 - pad_x,
                        block.bbox.y0 - pad_y,
                        block.bbox.x1 + pad_x,
                        block.bbox.y1 + pad_y,
                    ),
                    page.rect,
                )
                image = render_crop(page, rect)
                if image.width < MIN_FIG_DIM or image.height < MIN_FIG_DIM:
                    continue

                stem = ensure_unique_stem(caption.ident, used_stems)
                file_name = f"{stem}.png"
                image.save(output_images_dir / file_name)
                entries.append(
                    {
                        "id": stem,
                        "kind": "fig",
                        "file": f"{output_images_dir.name}/{file_name}",
                        "page": page_index + 1,
                        "caption": caption.text,
                        "width": image.width,
                        "height": image.height,
                    }
                )
                fig_count += 1

            line_clusters = cluster_horizontal_lines(detect_horizontal_line_rects(page), page.rect.width)
            used_cluster_indices: set[int] = set()

            for idx, caption in enumerate(table_captions):
                selected = table_crop_from_clusters(
                    caption,
                    line_clusters,
                    page.rect,
                    used_cluster_indices,
                )
                if selected is not None:
                    used_cluster_indices.add(selected[0])
                    rect = selected[1]
                else:
                    rect = table_crop_from_text(page, page_dict, table_captions, idx)
                rect = refine_table_crop(page, rect)

                image = render_crop(page, rect)
                if image.width < 700 or image.height < 90:
                    continue

                stem = ensure_unique_stem(caption.ident, used_stems)
                file_name = f"{stem}.png"
                image.save(output_images_dir / file_name)
                entries.append(
                    {
                        "id": stem,
                        "kind": "table",
                        "file": f"{output_images_dir.name}/{file_name}",
                        "page": page_index + 1,
                        "caption": caption.text,
                        "width": image.width,
                        "height": image.height,
                    }
                )
                table_count += 1

    entries = dedupe(entries)
    write_figure_map(output_images_dir, entries)
    return {"figures": fig_count, "tables": table_count}


def main() -> int:
    args = parse_args()
    pdf_path = args.pdf_path.expanduser().resolve()
    output_images_dir = args.output_images_dir.expanduser().resolve()

    if not pdf_path.exists() or not pdf_path.is_file():
        print(f"ERROR: invalid PDF path: {pdf_path}", file=sys.stderr)
        return 1

    output_images_dir.mkdir(parents=True, exist_ok=True)

    try:
        counts = extract_figures(pdf_path, output_images_dir)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        f"Extracted {counts['figures']} figures, {counts['tables']} tables from PDF. Output: {output_images_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
