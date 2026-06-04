import os
from io import BytesIO
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

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
        except Exception as e:
            pass
            
    # 2. Title
    name = user_data.get('first_name', '')
    elements.append(Paragraph(f"Applicant Profile: {name}", title_style))
    elements.append(Spacer(1, 12))
    
    # Basic Info Table
    email = user_data.get('email', '')
    phone = user_data.get('phone_number', '')
    nationality = user_data.get('nationality', '')
    basic_info = [
        ['Email:', email, 'Phone:', phone],
        ['Nationality:', nationality, 'DOB:', str(user_data.get('date_of_birth', ''))],
        ['Position:', user_data.get('application_for_position', ''), 'Status:', user_data.get('user_status', '')]
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
                ss.get('ship_name', ''),
                ss.get('rank', ''),
                str(ss.get('signed_on', '')),
                str(ss.get('signed_off', ''))
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
                c.get('company_name', ''),
                c.get('ship_name', ''),
                str(c.get('sign_on_date', '')),
                c.get('status', '')
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

    # Documents
    docs = user_data.get('user_documents', [])
    if docs:
        elements.append(Paragraph("Documents & Certificates", subtitle_style))
        elements.append(Spacer(1, 10))
        
        d_data = [['Type/Title', 'Number', 'Issue Date', 'Expiry Date']]
        for d in docs:
            d_data.append([
                d.get('document_type', d.get('document_name', '')),
                d.get('document_number', ''),
                str(d.get('issue_date', '')),
                str(d.get('expiration_date', d.get('expiry_date', '')))
            ])
            
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
