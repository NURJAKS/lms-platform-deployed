"""Персонализированный PNG-сертификат на основе uploads/certificates/certification.png."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATE_PATH = BACKEND_ROOT / "uploads" / "certificates" / "certification.png"
SIGNATURE_PATH = BACKEND_ROOT / "uploads" / "certificates" / "image-removebg-preview.png"
ISSUED_DIR = BACKEND_ROOT / "uploads" / "certificates" / "issued"

# Макет (координаты для эталона 1024×724); позиции масштабируются под фактический размер файла.
DESIGN_W = 1024
DESIGN_H = 724

# Координаты в системе макета 1024×724; anchor "mm" — геометрический центр текста в точке (X,Y).
# Имя: Y чуть ниже, чтобы сесть на верхнюю линию, не заходя на фразу выше.
NAME_CENTER = (512, 345)
COURSE_CENTER = (512, 470)
# Дата: над линией и подписью «Дата»; меньше Y — выше на листе.
DATE_POS = (195, 575)
# Подпись (PNG с альфой): центр вставки в координатах макета; max — доля ширины сертификата.
SIGNATURE_CENTER = (838, 572)
SIGNATURE_MAX_WIDTH_FRAC = 0.22

NAME_PT_DESIGN = 45
COURSE_PT_DESIGN = 32
DATE_PT_DESIGN = 22

TEXT_COLOR = (51, 51, 51)

_FONT_BOLD: Iterable[str] = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
)

_FONT_REGULAR: Iterable[str] = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
)


def _pick_existing(paths: Iterable[str]) -> str | None:
    for p in paths:
        if Path(p).is_file():
            return p
    return None


def _truetype(path: str | None, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if path:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            logger.warning("Не удалось загрузить шрифт %s", path)
    return ImageFont.load_default()


def _text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    if hasattr(draw, "textlength"):
        return int(draw.textlength(text, font=font))
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _wrap_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [text] if text else [""]
    lines: list[str] = []
    current: list[str] = []
    for w in words:
        trial = " ".join(current + [w])
        if _text_width(draw, trial, font) <= max_width:
            current.append(w)
        else:
            if current:
                lines.append(" ".join(current))
            if _text_width(draw, w, font) > max_width:
                lines.append(w)
                current = []
            else:
                current = [w]
    if current:
        lines.append(" ".join(current))
    return lines if lines else [text]


def _scale_xy(x: float, y: float, img_w: int, img_h: int) -> tuple[float, float]:
    return (x * img_w / DESIGN_W, y * img_h / DESIGN_H)


def _paste_signature_rgba(
    base: Image.Image,
    sig_path: Path,
    center_design: tuple[float, float],
    iw: int,
    ih: int,
    max_width_frac: float,
) -> None:
    if not sig_path.is_file():
        logger.warning("Файл подписи не найден: %s", sig_path)
        return
    try:
        sig = Image.open(sig_path).convert("RGBA")
    except OSError:
        logger.warning("Не удалось открыть подпись: %s", sig_path)
        return
    max_w = max(40, int(iw * max_width_frac))
    w0, h0 = sig.size
    if w0 <= 0 or h0 <= 0:
        return
    if w0 > max_w:
        ratio = max_w / w0
        new_w = max_w
        new_h = max(1, int(round(h0 * ratio)))
        sig = sig.resize((new_w, new_h), Image.Resampling.LANCZOS)
    w, h = sig.size
    cx, cy = _scale_xy(center_design[0], center_design[1], iw, ih)
    left = int(round(cx - w / 2))
    top = int(round(cy - h / 2))
    left = max(0, min(left, iw - w))
    top = max(0, min(top, ih - h))
    base.paste(sig, (left, top), sig)


def render_certificate_png(
    cert_id: int,
    student_name: str,
    course_title: str,
    issued_at: datetime | None = None,
) -> str:
    """
    Рисует сертификат и сохраняет в uploads/certificates/issued/cert_{id}.png.
    Возвращает URL-путь вида /uploads/certificates/issued/cert_{id}.png
    """
    if not TEMPLATE_PATH.is_file():
        raise FileNotFoundError(f"Шаблон сертификата не найден: {TEMPLATE_PATH}")

    ISSUED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = ISSUED_DIR / f"cert_{cert_id}.png"

    name = (student_name or "").strip() or "Студент"
    course = (course_title or "").strip() or "Курс"
    when = issued_at or datetime.now(timezone.utc)
    date_str = when.strftime("%d.%m.%Y")

    img = Image.open(TEMPLATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(img)
    iw, ih = img.size

    sx = iw / DESIGN_W
    sy = ih / DESIGN_H

    bold_path = _pick_existing(_FONT_BOLD)
    regular_path = _pick_existing(_FONT_REGULAR)

    # Имя: полужирный, уменьшать размер если не помещается в ~85% ширины; длинные ФИО — чуть меньший стартовый кегль
    max_name_w = int(iw * 0.85)
    name_size = max(18, int(round(NAME_PT_DESIGN * sx)))
    if len(name) > 20:
        name_size = max(18, name_size - 6)
    font_name = _truetype(bold_path, name_size)
    while name_size > 18 and _text_width(draw, name, font_name) > max_name_w:
        name_size -= 2
        font_name = _truetype(bold_path, name_size)

    nx, ny = _scale_xy(*NAME_CENTER, iw, ih)
    draw.text((nx, ny), name, fill=TEXT_COLOR, font=font_name, anchor="mm")

    # Название курса: перенос строк, центр блока у COURSE_CENTER
    course_size = max(16, int(round(COURSE_PT_DESIGN * sx)))
    font_course = _truetype(regular_path, course_size)
    max_course_w = int(iw * 0.88)
    lines: list[str] = []
    while course_size > 10:
        lines = _wrap_lines(draw, course, font_course, max_course_w)
        if len(lines) <= 3:
            break
        course_size -= 2
        font_course = _truetype(regular_path, course_size)
    lines = _wrap_lines(draw, course, font_course, max_course_w)

    cx, cy = _scale_xy(*COURSE_CENTER, iw, ih)
    line_gap = max(4, int(round(8 * sy)))
    heights: list[int] = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_course)
        heights.append(bbox[3] - bbox[1])
    total_h = sum(heights) + line_gap * max(0, len(lines) - 1)
    y_top = cy - total_h / 2
    for line, h in zip(lines, heights):
        draw.text((cx, y_top + h / 2), line, fill=TEXT_COLOR, font=font_course, anchor="mm")
        y_top += h + line_gap

    # Дата: центр строки в точке DATE_POS; поджимаем к холсту, если шрифт/макет у края
    date_size = max(14, int(round(DATE_PT_DESIGN * sx)))
    font_date = _truetype(regular_path, date_size)
    dx, dy = _scale_xy(*DATE_POS, iw, ih)
    pad = max(6, date_size // 2)
    dx = float(min(max(dx, pad), iw - pad))
    dy = float(min(max(dy, pad), ih - pad))
    draw.text((dx, dy), date_str, fill=TEXT_COLOR, font=font_date, anchor="mm")

    # Подпись директора поверх шаблона (после текста)
    _paste_signature_rgba(img, SIGNATURE_PATH, SIGNATURE_CENTER, iw, ih, SIGNATURE_MAX_WIDTH_FRAC)

    img.convert("RGB").save(out_path, format="PNG", optimize=True)
    return f"/uploads/certificates/issued/cert_{cert_id}.png"
