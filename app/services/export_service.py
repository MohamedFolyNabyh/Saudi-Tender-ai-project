import io
import os
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

try:
    import arabic_reshaper
    from bidi.algorithm import get_display

    HAS_ARABIC_SUPPORT = True
except ImportError:
    HAS_ARABIC_SUPPORT = False


class ExportService:

    ARABIC_PATTERN = re.compile(r"[\u0600-\u06FF]")

    @classmethod
    def is_arabic(cls, text: str) -> bool:
        return bool(cls.ARABIC_PATTERN.search(text))

    @classmethod
    def reshape_text(cls, text: str) -> str:
        if not text:
            return ""

        if cls.is_arabic(text) and HAS_ARABIC_SUPPORT:
            text = arabic_reshaper.reshape(text)
            text = get_display(text)

        return text

    @classmethod
    def generate_pdf(cls, content: str, filename: str) -> bytes:

        pdf_buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            pdf_buffer,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        # -----------------------------
        # Register Arabic Font Safely
        # -----------------------------
        arabic_font = "Helvetica"
        BASE_DIR = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        font_path = os.path.join(
            BASE_DIR, "assets", "fonts", "Amiri-Regular.ttf"
        )

        # Fallback to getcwd if BASE_DIR doesn't find it
        if not os.path.exists(font_path):
            font_path = os.path.join(
                os.getcwd(), "assets", "fonts", "Amiri-Regular.ttf"
            )

        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont("Amiri", font_path))
            arabic_font = "Amiri"

        # -----------------------------
        # Dynamic Styles Definition
        # -----------------------------
        english_title = ParagraphStyle(
            "EnglishTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1A365D"),
        )

        arabic_title = ParagraphStyle(
            "ArabicTitle",
            parent=styles["Title"],
            fontName=arabic_font,
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1A365D"),
        )

        english_h1 = ParagraphStyle(
            "EnglishH1",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#2B6CB0"),
            spaceBefore=10,
            spaceAfter=4,
        )

        arabic_h1 = ParagraphStyle(
            "ArabicH1",
            parent=styles["Heading1"],
            fontName=arabic_font,
            fontSize=14,
            leading=18,
            alignment=TA_RIGHT,
            textColor=colors.HexColor("#2B6CB0"),
            spaceBefore=10,
            spaceAfter=4,
        )

        english_h2 = ParagraphStyle(
            "EnglishH2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#2D3748"),
            spaceBefore=8,
            spaceAfter=4,
        )

        arabic_h2 = ParagraphStyle(
            "ArabicH2",
            parent=styles["Heading2"],
            fontName=arabic_font,
            fontSize=12,
            leading=16,
            alignment=TA_RIGHT,
            textColor=colors.HexColor("#2D3748"),
            spaceBefore=8,
            spaceAfter=4,
        )

        english_body = ParagraphStyle(
            "EnglishBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            alignment=TA_LEFT,
        )

        arabic_body = ParagraphStyle(
            "ArabicBody",
            parent=styles["BodyText"],
            fontName=arabic_font,
            fontSize=10,
            leading=15,
            alignment=TA_RIGHT,
        )

        story = []

        # -----------------------------
        # Document Title
        # -----------------------------
        if cls.is_arabic(filename):
            story.append(
                Paragraph(cls.reshape_text(filename), arabic_title)
            )
        else:
            story.append(Paragraph(filename, english_title))

        story.append(Spacer(1, 15))

        # -----------------------------
        # Content Parsing & Formatting
        # -----------------------------
        if content:
            for line in content.splitlines():
                line = line.strip()

                if not line:
                    continue

                # 1. Horizontal Rule (---)
                if line == "---" or line.startswith("___"):
                    story.append(
                        HRFlowable(
                            width="100%",
                            thickness=1,
                            color=colors.HexColor("#CBD5E0"),
                            spaceBefore=8,
                            spaceAfter=12,
                        )
                    )
                    continue

                # 2. Markdown Bold parsing (**text** -> <b>text</b>)
                line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)

                # 3. Heading 1 (# Title)
                if line.startswith("# "):
                    clean_text = line[2:].strip()
                    if cls.is_arabic(clean_text):
                        story.append(
                            Paragraph(
                                cls.reshape_text(clean_text), arabic_h1
                            )
                        )
                    else:
                        story.append(Paragraph(clean_text, english_h1))
                    continue

                # 4. Heading 2 (## Subtitle)
                if line.startswith("## "):
                    clean_text = line[3:].strip()
                    if cls.is_arabic(clean_text):
                        story.append(
                            Paragraph(
                                cls.reshape_text(clean_text), arabic_h2
                            )
                        )
                    else:
                        story.append(Paragraph(clean_text, english_h2))
                    continue

                # 5. Regular Body Paragraph
                if cls.is_arabic(line):
                    story.append(
                        Paragraph(cls.reshape_text(line), arabic_body)
                    )
                else:
                    story.append(Paragraph(line, english_body))

                story.append(Spacer(1, 6))

        doc.build(story)
        pdf_buffer.seek(0)

        return pdf_buffer.getvalue()