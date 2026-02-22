"""
PDF report generator using reportlab.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional
from loguru import logger


def generate_pdf(
    filepath: str,
    company_name: str,
    narratives: dict[str, str] = None,
    dcf_summary: dict = None,
) -> str:
    """Generate a PDF valuation report."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.units import inch
    except ImportError:
        logger.warning("reportlab not available — PDF export skipped")
        return ""

    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(str(path), pagesize=letter,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=18, spaceAfter=20)
    heading_style = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14, spaceAfter=10)
    body_style = styles["BodyText"]

    story = []
    story.append(Paragraph(f"Valuation Report — {company_name}", title_style))
    story.append(Spacer(1, 0.2*inch))

    if dcf_summary:
        story.append(Paragraph("DCF Summary", heading_style))
        for k, v in dcf_summary.items():
            story.append(Paragraph(f"<b>{k}:</b> {v}", body_style))
        story.append(Spacer(1, 0.2*inch))

    if narratives:
        for section, text in narratives.items():
            title = section.replace("_", " ").title()
            story.append(Paragraph(title, heading_style))
            for para in text.split("\n\n"):
                if para.strip():
                    story.append(Paragraph(para.strip(), body_style))
            story.append(Spacer(1, 0.15*inch))

    doc.build(story)
    logger.info(f"PDF report exported to {filepath}")
    return str(path)
