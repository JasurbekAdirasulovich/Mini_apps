import io
from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class PDFExporter:
    """
    Generates professional, printable Adobe PDF files for exam variants using ReportLab.
    Ensures each variant starts on a new page and outputs an Answer Key table at the end.
    """

    @staticmethod
    def generate_pdf(variants_data: Dict[str, Any]) -> io.BytesIO:
        """
        Creates a PDF document in-memory containing exam variants.

        Args:
            variants_data (dict): The dictionary containing subject, topics, and list of variants.

        Returns:
            io.BytesIO: Binary stream of the PDF file.
        """
        buffer = io.BytesIO()
        
        # 1. Page Template and Document settings
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=54,  # 0.75 in
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        # 2. Typography Styles
        styles = getSampleStyleSheet()
        
        # Custom styles to avoid modifying defaults
        style_title = ParagraphStyle(
            name='ExamTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1f2937')
        )
        
        style_subtitle = ParagraphStyle(
            name='ExamSubtitle',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#4b5563')
        )
        
        style_meta_left = ParagraphStyle(
            name='MetaLeft',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=14,
            alignment=TA_LEFT
        )

        style_meta_right = ParagraphStyle(
            name='MetaRight',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=14,
            alignment=TA_RIGHT
        )
        
        style_question = ParagraphStyle(
            name='QuestionText',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10.5,
            leading=15,
            textColor=colors.HexColor('#111827'),
            spaceBefore=10,
            spaceAfter=6
        )
        
        style_option = ParagraphStyle(
            name='OptionText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            leftIndent=20,
            spaceAfter=4
        )

        style_key_title = ParagraphStyle(
            name='KeyTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#10b981')
        )

        style_table_text = ParagraphStyle(
            name='TableText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=12,
            alignment=TA_CENTER
        )

        style_table_hdr = ParagraphStyle(
            name='TableHeaderText',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=13,
            alignment=TA_CENTER
        )

        story = []

        subject = variants_data.get('subject', 'General Subject')
        difficulty = variants_data.get('difficulty', 'medium').upper()
        variants = variants_data.get('variants', [])

        # ----------------------------------------------------
        # 3. CONSTRUCT THE STORY FLOW
        # ----------------------------------------------------
        for idx, var in enumerate(variants):
            var_name = var.get('name', f"Variant {idx+1}")
            questions = var.get('questions', [])

            # Header
            story.append(Paragraph(subject.upper(), style_title))
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"{var_name.upper()} | Qiyinlik: {difficulty}", style_subtitle))
            story.append(Spacer(1, 15))

            # Student details table
            meta_data = [
                [
                    Paragraph("Talaba F.I.Sh: __________________________________", style_meta_left),
                    Paragraph("Guruh: _________", style_meta_right)
                ]
            ]
            meta_table = Table(meta_data, colWidths=[350, 130])
            meta_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 20))

            # Write Questions
            for q_idx, q in enumerate(questions):
                q_text = q.get('question', '')
                options = q.get('options', {})

                story.append(Paragraph(f"{q_idx + 1}. {q_text}", style_question))
                
                # Options list
                for opt_key in sorted(options.keys()):
                    opt_val = options[opt_key]
                    story.append(Paragraph(f"<b>{opt_key})</b> {opt_val}", style_option))
                
                story.append(Spacer(1, 10))

            # PageBreak to separate variants
            story.append(PageBreak())

        # ----------------------------------------------------
        # 4. ANSWER KEYS PAGE
        # ----------------------------------------------------
        story.append(Paragraph("JAVOBLAR KALITI / ANSWER KEYS", style_key_title))
        story.append(Spacer(1, 4))
        
        info_str = f"Fan: {subject}<br/>Yaratilgan sana: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        story.append(Paragraph(info_str, style_subtitle))
        story.append(Spacer(1, 25))

        # Build keys data structure for Reportlab Table
        # Row 0: Headers
        hdr_row = [Paragraph("<b>T/r</b>", style_table_hdr)]
        for v_idx, var in enumerate(variants):
            var_name = var.get('name', f"Var {v_idx+1}")
            hdr_row.append(Paragraph(f"<b>{var_name}</b>", style_table_hdr))
        
        table_data = [hdr_row]

        # Fill Answers rows
        q_count = len(variants[0].get('questions', [])) if variants else 0
        for r_idx in range(q_count):
            row = [Paragraph(str(r_idx + 1), style_table_text)]
            for var in variants:
                q_list = var.get('questions', [])
                if r_idx < len(q_list):
                    ans = q_list[r_idx].get('answer', '-')
                    row.append(Paragraph(ans, style_table_text))
            table_data.append(row)

        # Style and draw the Answer table
        col_width = 480 / (len(variants) + 1)
        col_widths = [40] + [col_width] * len(variants)
        
        keys_table = Table(table_data, colWidths=col_widths)
        keys_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f3f4f6')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9fafb')])
        ]))

        story.append(keys_table)

        # 5. Build Document
        doc.build(story)
        
        buffer.seek(0)
        return buffer
