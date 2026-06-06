# -*- coding: utf-8 -*-
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "论文的" / "AI_Music_Recommendation_System_技术论文.md"
DEFAULT_OUTPUT = ROOT / "论文的" / "AI_Music_Recommendation_System_技术论文.pdf"


def register_chinese_font() -> str:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/System/Library/Fonts/Supplemental/Hiragino Sans GB.ttc",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            try:
                pdfmetrics.registerFont(TTFont("ChineseDocFont", candidate))
                return "ChineseDocFont"
            except Exception:
                continue
    return "Helvetica"


def make_styles(font_name: str):
    styles = getSampleStyleSheet()
    base = ParagraphStyle(
        "ChineseBase",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=10.5,
        leading=17,
        textColor=colors.HexColor("#1f2937"),
        alignment=TA_LEFT,
        wordWrap="CJK",
        spaceAfter=8,
    )
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base,
            fontSize=22,
            leading=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=18,
        ),
        "h1": ParagraphStyle(
            "Heading1",
            parent=base,
            fontSize=18,
            leading=25,
            textColor=colors.HexColor("#0f766e"),
            spaceBefore=16,
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "Heading2",
            parent=base,
            fontSize=15,
            leading=22,
            textColor=colors.HexColor("#166534"),
            spaceBefore=13,
            spaceAfter=8,
        ),
        "h3": ParagraphStyle(
            "Heading3",
            parent=base,
            fontSize=12.5,
            leading=19,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": base,
        "quote": ParagraphStyle(
            "Quote",
            parent=base,
            leftIndent=14,
            textColor=colors.HexColor("#475569"),
            backColor=colors.HexColor("#f1f5f9"),
            borderPadding=6,
            spaceBefore=5,
            spaceAfter=10,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base,
            fontName=font_name,
            fontSize=8.5,
            leading=12,
            leftIndent=10,
            textColor=colors.HexColor("#334155"),
            backColor=colors.HexColor("#f8fafc"),
            wordWrap="CJK",
        ),
        "table": ParagraphStyle(
            "TableCell",
            parent=base,
            fontSize=7.6,
            leading=10.5,
            wordWrap="CJK",
            spaceAfter=0,
        ),
    }


def inline_markdown(text: str) -> str:
    text = html.escape(text.strip())
    text = re.sub(r"`([^`]+)`", r"<font color='#0f766e'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def clean_heading(line: str) -> tuple[int, str] | None:
    match = re.match(r"^(#{1,3})\s+(.*)$", line)
    if not match:
        return None
    return len(match.group(1)), match.group(2).strip()


def is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def is_separator_line(line: str) -> bool:
    stripped = line.strip().strip("|").strip()
    return bool(stripped) and all(set(part.strip()) <= {"-", ":"} for part in stripped.split("|"))


def build_table(table_lines: list[str], styles: dict, page_width: float):
    rows: list[list[Paragraph]] = []
    for line in table_lines:
        if is_separator_line(line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append([Paragraph(inline_markdown(cell), styles["table"]) for cell in cells])
    if not rows:
        return []
    col_count = max(len(row) for row in rows)
    for row in rows:
        while len(row) < col_count:
            row.append(Paragraph("", styles["table"]))
    table = Table(rows, colWidths=[page_width / col_count] * col_count, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dcfce7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return [table, Spacer(1, 0.25 * cm)]


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawRightString(A4[0] - 1.6 * cm, 1.1 * cm, f"Page {doc.page}")
    canvas.drawString(1.6 * cm, 1.1 * cm, "AI Music Recommendation System Technical Paper")
    canvas.restoreState()


def convert_markdown_to_pdf(input_path: Path, output_path: Path) -> None:
    font_name = register_chinese_font()
    styles = make_styles(font_name)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.8 * cm,
        title="AI Music Recommendation System 技术论文",
        author="AI Fair Project Team",
    )
    page_width = A4[0] - doc.leftMargin - doc.rightMargin
    story = []
    paragraph_buffer: list[str] = []
    table_buffer: list[str] = []
    in_code_block = False
    code_buffer: list[str] = []

    def flush_paragraph():
        if paragraph_buffer:
            text = " ".join(item.strip() for item in paragraph_buffer if item.strip())
            if text:
                story.append(Paragraph(inline_markdown(text), styles["body"]))
            paragraph_buffer.clear()

    def flush_table():
        if table_buffer:
            story.extend(build_table(table_buffer, styles, page_width))
            table_buffer.clear()

    def flush_code():
        if code_buffer:
            code = "<br/>".join(html.escape(line) for line in code_buffer)
            story.append(Paragraph(code, styles["code"]))
            story.append(Spacer(1, 0.15 * cm))
            code_buffer.clear()

    for raw_line in input_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if line.strip().startswith("```"):
            flush_paragraph()
            flush_table()
            if in_code_block:
                flush_code()
            in_code_block = not in_code_block
            continue
        if in_code_block:
            code_buffer.append(line)
            continue
        if is_table_line(line):
            flush_paragraph()
            table_buffer.append(line)
            continue
        flush_table()
        if not line.strip():
            flush_paragraph()
            continue
        heading = clean_heading(line)
        if heading:
            flush_paragraph()
            level, text = heading
            if level == 1:
                story.append(Paragraph(inline_markdown(text), styles["title"]))
                story.append(Spacer(1, 0.3 * cm))
            elif level == 2:
                story.append(Paragraph(inline_markdown(text), styles["h1"]))
            else:
                story.append(Paragraph(inline_markdown(text), styles["h2"]))
            continue
        if line.startswith(">"):
            flush_paragraph()
            story.append(Paragraph(inline_markdown(line.lstrip("> ")), styles["quote"]))
            continue
        if re.match(r"^\d+\.\s+", line) or line.strip().startswith("- "):
            flush_paragraph()
            story.append(Paragraph(inline_markdown(line), styles["body"]))
            continue
        if line.strip() == "---":
            flush_paragraph()
            story.append(PageBreak())
            continue
        paragraph_buffer.append(line)

    flush_paragraph()
    flush_table()
    flush_code()
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


def main() -> None:
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    convert_markdown_to_pdf(input_path, output_path)
    print(output_path)


if __name__ == "__main__":
    main()
