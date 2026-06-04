import os
from io import BytesIO
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image


def _safe(value):
    """Convert None/non-string values to empty strings so reportlab never crashes."""
    if value is None:
        return ''
    return str(value)


def generate_full_profile_pdf(user_data, logo_path=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # 1. Logo
    if logo_path and os.path.exists(logo_path):
        try:
            img = Image(logo_path, width=100, height=100)
            img.hAlign = 'LEFT'
            elements.append(img)
            elements.append(Spacer(1, 12))
        except Exception:
            pass
            
    # 2. Title
    name = _safe(user_data.get('first_name', ''))
    elements.append(Paragraph(f"Applicant Profile: {name}", title_style))
    elements.append(Spacer(1, 12))
    
    # Basic Info Table
    basic_info = [
        ['Email:', _safe(user_data.get('email')), 'Phone:', _safe(user_data.get('phone_number'))],
        ['Nationality:', _safe(user_data.get('nationality')), 'DOB:', _safe(user_data.get('date_of_birth'))],
        ['Position:', _safe(user_data.get('application_for_position')), 'Status:', _safe(user_data.get('user_status'))]
    ]
    t = Table(basic_info, colWidths=[80, 170, 80, 170])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # Sea Services
    sea_services = user_data.get('sea_services', [])
    if sea_services:
        elements.append(Paragraph("Sea Service Records", subtitle_style))
        elements.append(Spacer(1, 10))
        
        data = [['Ship Name', 'Rank', 'Sign On', 'Sign Off']]
        for ss in sea_services:
            data.append([
                _safe(ss.get('ship_name')),
                _safe(ss.get('rank')),
                _safe(ss.get('signed_on')),
                _safe(ss.get('signed_off'))
            ])
            
        ss_table = Table(data, colWidths=[150, 100, 100, 100])
        ss_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1c3c6b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f2f2f2')),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(ss_table)
        elements.append(Spacer(1, 20))
        
    # Contracts
    contracts = user_data.get('contracts', [])
    if contracts:
        elements.append(Paragraph("Contracts", subtitle_style))
        elements.append(Spacer(1, 10))
        
        c_data = [['Company', 'Ship', 'Sign On', 'Status']]
        for c in contracts:
            c_data.append([
                _safe(c.get('company_name')),
                _safe(c.get('ship_name')),
                _safe(c.get('sign_on_date')),
                _safe(c.get('status'))
            ])
            
        c_table = Table(c_data, colWidths=[150, 120, 90, 90])
        c_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1c3c6b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f2f2f2')),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(c_table)
        elements.append(Spacer(1, 20))

    # Documents — user_documents is a dict with keys like passport, seaman_book, coc, etc.
    docs_dict = user_data.get('user_documents', {})
    if not isinstance(docs_dict, dict):
        docs_dict = {}
    
    # Flatten docs_dict into a list of rows: [Title, Number, Issue, Expiry]
    flat_docs = []
    
    def add_doc(title, obj):
        if obj and isinstance(obj, dict):
            flat_docs.append([
                _safe(title),
                _safe(obj.get('document_number', obj.get('certificate_number', obj.get('number', obj.get('passport_no', obj.get('seaman_book_no', '')))))),
                _safe(obj.get('issue_date')),
                _safe(obj.get('expiration_date', obj.get('expiry_date')))
            ])

    add_doc('Passport', docs_dict.get('passport'))
    add_doc('Seaman Book', docs_dict.get('seaman_book'))
    add_doc('Other Seaman Book', docs_dict.get('other_seaman_book'))
    add_doc('COC', docs_dict.get('coc'))
    add_doc('GOC', docs_dict.get('goc'))
    add_doc('Health Cert.', docs_dict.get('health_certificate'))
    
    for lic in (docs_dict.get('licenses') or []):
        if isinstance(lic, dict):
            add_doc(_safe(lic.get('document_name', 'License')), lic)
        
    for mc in (docs_dict.get('marine_courses') or []):
        if isinstance(mc, dict):
            add_doc(_safe(mc.get('course_name', 'Course')), mc)
        
    for pd_doc in (docs_dict.get('personal_documents') or []):
        if isinstance(pd_doc, dict):
            add_doc(_safe(pd_doc.get('document_type', 'Document')), pd_doc)

    if flat_docs:
        elements.append(Paragraph("Documents &amp; Certificates", subtitle_style))
        elements.append(Spacer(1, 10))
        
        d_data = [['Type/Title', 'Number', 'Issue Date', 'Expiry Date']]
        d_data.extend(flat_docs)
            
        d_table = Table(d_data, colWidths=[150, 100, 100, 100])
        d_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1c3c6b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f2f2f2')),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(d_table)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
