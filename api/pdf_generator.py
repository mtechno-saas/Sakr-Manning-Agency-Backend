import os
from io import BytesIO
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)


# ─── Navy blue theme color ───
NAVY = colors.HexColor('#1c3c6b')
LIGHT_GRAY = colors.HexColor('#f2f2f2')
WHITE = colors.white


def _safe(value):
    """Convert None / non-string values to safe empty strings for reportlab."""
    if value is None:
        return ''
    return str(value)


def _make_table(headers, rows, col_widths=None):
    """Build a styled Table with a navy header row and alternating body rows."""
    data = [headers] + rows
    if not col_widths:
        page_w = 515  # usable width at 40pt margins on A4
        col_widths = [page_w // len(headers)] * len(headers)

    table = Table(data, colWidths=col_widths, repeatRows=1)
    style_commands = [
        ('BACKGROUND',   (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME',     (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 10),
        ('TOPPADDING',   (0, 0), (-1, 0), 6),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE',     (0, 1), (-1, -1), 8),
        ('GRID',         (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
    ]
    # Alternate row shading
    for i in range(1, len(data)):
        bg = LIGHT_GRAY if i % 2 == 0 else WHITE
        style_commands.append(('BACKGROUND', (0, i), (-1, i), bg))

    table.setStyle(TableStyle(style_commands))
    return table


def _resolve_name(app_label, model_name, value):
    if not value or not str(value).isdigit():
        return value
    from django.apps import apps
    try:
        model_class = apps.get_model(app_label, model_name)
        obj = model_class.objects.get(id=int(value))
        return obj.name
    except Exception:
        return value


def generate_full_profile_pdf(user_data, logo_path=None):
    """
    Build a structured PDF from the full-profile endpoint payload.
    Sections:
        1. Header (logo + applicant name)
        2. Personal Information
        3. Ranks & Certificates
        4. Travel Documents (Passport, Seaman Books)
        5. Professional Qualifications (COC, GOC)
        6. Health Certificates
        7. Marine Courses
        8. Sea Service Records
        9. Contracts (companies & ships signed on)
        10. Licenses
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40,
    )

    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Heading1'],
        fontSize=16, textColor=NAVY, spaceAfter=4,
    )
    section_style = ParagraphStyle(
        'SectionTitle', parent=styles['Heading2'],
        fontSize=12, textColor=NAVY, spaceBefore=14, spaceAfter=6,
        borderWidth=0, borderPadding=0,
    )
    normal_style = styles['Normal']
    cell_style = ParagraphStyle(
        'CellStyle', parent=styles['Normal'],
        fontSize=8, leading=10, textColor=colors.black
    )

    # ── 1. Logo + Title (branded header row) ────────────────────────
    name = _safe(user_data.get('first_name', ''))
    gen_id = _safe(user_data.get('generated_id', ''))
    title_text = f"Applicant Full Profile: {name}"
    if gen_id:
        title_text += f"<br/><font size='9' color='#555555'>ID: {gen_id}</font>"

    header_built = False
    if logo_path and os.path.exists(logo_path):
        try:
            logo_img = Image(logo_path, width=70, height=70)
            header_table = Table(
                [[logo_img, Paragraph(title_text, title_style)]],
                colWidths=[80, 435],
            )
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (0, 0), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            elements.append(header_table)
            header_built = True
        except Exception:
            pass

    if not header_built:
        elements.append(Paragraph(title_text, title_style))

    elements.append(Spacer(1, 10))

    # ── 2. Personal Information ──────────────────────────────────────
    elements.append(Paragraph("Personal Information", section_style))
    info_rows = [
        ['Email:', _safe(user_data.get('email')), 'Phone:', _safe(user_data.get('phone_number'))],
        ['Nationality:', _safe(user_data.get('nationality')), 'DOB:', _safe(user_data.get('date_of_birth'))],
        ['Marital Status:', _safe(user_data.get('marital_status')), 'Blood Type:', _safe(user_data.get('blood_type'))],
        ['Position:', _safe(user_data.get('application_for_position')), 'Status:', _safe(user_data.get('user_status'))],
        ['Place of Birth:', _safe(user_data.get('Place_Of_Birth')), 'Nearest Port:', _safe(user_data.get('Nearest_Port'))],
        ['Height (cm):', _safe(user_data.get('Height_Cm')), 'Weight (kg):', _safe(user_data.get('Weight_Kg'))],
        ['Rank Code:', _safe(user_data.get('rank_code')), 'Assigned Code:', _safe(user_data.get('assigned_code'))],
        ['Salary:', _safe(user_data.get('salary')), 'Available Date:', _safe(user_data.get('available_date'))],
    ]
    info_table = Table(info_rows, colWidths=[90, 160, 90, 160])
    info_table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, -1), WHITE),
        ('TEXTCOLOR',    (0, 0), (-1, -1), colors.black),
        ('ALIGN',        (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME',     (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME',     (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 5),
        ('GRID',         (0, 0), (-1, -1), 0.25, colors.lightgrey),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 10))

    # ── 3. Ranks & Certificates ──────────────────────────────────────
    ranks = user_data.get('ranks', [])
    if ranks:
        elements.append(Paragraph("Assigned Ranks", section_style))
        rows = []
        for r in ranks:
            rank_nested = r.get('rank', {}) or {}
            rows.append([
                _safe(rank_nested.get('name', r.get('rank_name', ''))),
                _safe(rank_nested.get('code', r.get('rank_code', ''))),
                _safe(r.get('assigned_code', '')),
            ])
        elements.append(_make_table(['Rank Name', 'Rank Code', 'Assigned Code'], rows, [180, 150, 180]))
        elements.append(Spacer(1, 10))

    certs = user_data.get('certificates', [])
    if certs:
        elements.append(Paragraph("Certificates", section_style))
        rows = [[_safe(c.get('name', '')), _safe(c.get('code', ''))] for c in certs]
        elements.append(_make_table(['Certificate Name', 'Code'], rows, [300, 210]))
        elements.append(Spacer(1, 10))

    # ── 4. Travel Documents ──────────────────────────────────────────
    docs = user_data.get('user_documents', {})
    if not isinstance(docs, dict):
        docs = {}

    travel_items = []
    # Passport
    pp = docs.get('passport')
    if pp and isinstance(pp, dict):
        travel_items.append(['Passport', _safe(pp.get('passport_no')), _safe(pp.get('issue_date')),
                             _safe(pp.get('expiry_date')), _safe(pp.get('issued_by')), _safe(pp.get('place_of_issue'))])
    # Seaman Book
    sb = docs.get('seaman_book')
    if sb and isinstance(sb, dict):
        travel_items.append(['Seaman Book', _safe(sb.get('seaman_book_no')), _safe(sb.get('issue_date')),
                             _safe(sb.get('expiry_date')), _safe(sb.get('issued_by')), _safe(sb.get('place_of_issue'))])
    # Other Seaman Book
    osb = docs.get('other_seaman_book')
    if osb and isinstance(osb, dict) and _safe(osb.get('seaman_book_no')):
        travel_items.append(['Other Seaman Book', _safe(osb.get('seaman_book_no')), _safe(osb.get('issue_date')),
                             _safe(osb.get('expiry_date')), _safe(osb.get('issued_by')), _safe(osb.get('place_of_issue'))])

    if travel_items:
        elements.append(Paragraph("Travel Documents", section_style))
        elements.append(_make_table(
            ['Document', 'Number', 'Issue Date', 'Expiry Date', 'Issued By', 'Place'],
            travel_items, [90, 80, 70, 70, 80, 80]
        ))
        elements.append(Spacer(1, 10))

    # ── 5. Professional Qualifications (COC / GOC) ───────────────────
    prof_items = []
    coc = docs.get('coc')
    if coc and isinstance(coc, dict):
        prof_items.append(['COC', _safe(coc.get('certificate_name')), _safe(coc.get('certificate_number')),
                           _safe(coc.get('issue_date')), _safe(coc.get('expiry_date')),
                           _safe(coc.get('issued_by')), _safe(coc.get('issued_at'))])
    goc = docs.get('goc')
    if goc and isinstance(goc, dict):
        prof_items.append(['GOC', '', _safe(goc.get('certificate_number')),
                           _safe(goc.get('issue_date')), _safe(goc.get('expiry_date')),
                           _safe(goc.get('issued_by')), _safe(goc.get('issued_at'))])

    if prof_items:
        elements.append(Paragraph("Professional Qualifications", section_style))
        elements.append(_make_table(
            ['Type', 'Name', 'Number', 'Issue', 'Expiry', 'Issued By', 'Issued At'],
            prof_items, [40, 80, 70, 65, 65, 70, 70]
        ))
        elements.append(Spacer(1, 10))

    # ── 6. Health Certificates ───────────────────────────────────────
    hc = docs.get('health_certificate')
    if hc and isinstance(hc, dict):
        elements.append(Paragraph("Health Certificates", section_style))
        hc_rows = [
            ['Flag State:', _safe(hc.get('flag_state')), 'Number:', _safe(hc.get('number'))],
            ['Issue Date:', _safe(hc.get('issue_date')), 'Expiry Date:', _safe(hc.get('expiry_date'))],
            ['Issued By:', _safe(hc.get('issued_by')), 'Issued At:', _safe(hc.get('issued_at'))],
            ['Intl Medical No:', _safe(hc.get('international_medical_number')),
             'Intl Med Issue:', _safe(hc.get('international_medical_issue_date'))],
            ['Intl Med Expiry:', _safe(hc.get('international_medical_expiry_date')), '', ''],
        ]
        hc_table = Table(hc_rows, colWidths=[90, 160, 90, 160])
        hc_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ]))
        elements.append(hc_table)
        
        records = hc.get('records', [])
        if records:
            vac_rows = []
            for r in records:
                vac_rows.append([
                    Paragraph(_safe(r.get('vaccine_name')), cell_style),
                    _safe(r.get('first_dose_date') or r.get('issue_date')),
                    _safe(r.get('second_dose_date') or r.get('expiry_date')),
                    Paragraph(_safe(r.get('remarks')), cell_style)
                ])
            elements.append(Spacer(1, 5))
            elements.append(Paragraph("Vaccinations", section_style))
            elements.append(_make_table(
                ['Vaccine Name', '1st Dose / Issue', '2nd Dose / Expiry', 'Remarks'],
                vac_rows, [150, 100, 100, 165]
            ))
            
        elements.append(Spacer(1, 10))

    # ── 7. Licenses ──────────────────────────────────────────────────
    licenses = docs.get('licenses', []) or []
    if licenses:
        elements.append(Paragraph("Licenses / STCW", section_style))
        lic_rows = []
        for lic in licenses:
            if isinstance(lic, dict):
                lic_rows.append([
                    Paragraph(_safe(lic.get('document_name')), cell_style),
                    _safe(lic.get('document_number')),
                    Paragraph(_safe(lic.get('country_of_issue')), cell_style),
                    _safe(lic.get('issue_date')),
                    _safe(lic.get('expiration_date')),
                ])
        if lic_rows:
            elements.append(_make_table(
                ['Document Name', 'Number', 'Country', 'Issue Date', 'Expiry Date'],
                lic_rows, [140, 90, 80, 90, 90]
            ))
            elements.append(Spacer(1, 10))

    # ── 8. Marine Courses ────────────────────────────────────────────
    courses = docs.get('marine_courses', []) or []
    if courses:
        elements.append(Paragraph("Marine Courses", section_style))
        mc_rows = []
        for mc in courses:
            if isinstance(mc, dict):
                mc_rows.append([
                    _safe(mc.get('course_name')),
                    _safe(mc.get('issue_date')),
                    _safe(mc.get('expiry_date')),
                ])
        if mc_rows:
            elements.append(_make_table(
                ['Course Name', 'Issue Date', 'Expiry Date'],
                mc_rows, [260, 120, 120]
            ))
            elements.append(Spacer(1, 10))

    # ── 9. Sea Service Records ───────────────────────────────────────
    sea_services = user_data.get('sea_services', [])
    if sea_services:
        elements.append(Paragraph("Sea Service Records", section_style))
        ss_rows = []
        for ss in sea_services:
            ss_rows.append([
                Paragraph(_safe(ss.get('vessel_name', ss.get('ship_name', ''))), cell_style),
                Paragraph(_safe(_resolve_name('api', 'Rank', ss.get('rank'))), cell_style),
                Paragraph(_safe(_resolve_name('core', 'VesselType', ss.get('vessel_type'))), cell_style),
                Paragraph(_safe(_resolve_name('core', 'Flag', ss.get('flag'))), cell_style),
                _safe(ss.get('signed_on')),
                _safe(ss.get('signed_off')),
                _safe(ss.get('period')),
            ])
        elements.append(_make_table(
            ['Vessel', 'Rank', 'Type', 'Flag', 'Sign On', 'Sign Off', 'Period'],
            ss_rows, [100, 60, 60, 50, 70, 70, 50]
        ))
        elements.append(Spacer(1, 10))

    # ── 10. Contracts ────────────────────────────────────────────────
    contracts = user_data.get('contracts', [])
    if contracts:
        elements.append(Paragraph("Contracts", section_style))
        c_rows = []
        for c in contracts:
            c_rows.append([
                Paragraph(_safe(c.get('company_name')), cell_style),
                Paragraph(_safe(c.get('ship_name')), cell_style),
                Paragraph(_safe(c.get('rank_name')), cell_style),
                _safe(c.get('sign_on_date')),
                _safe(c.get('sign_off_date')),
                Paragraph(_safe(c.get('status')), cell_style),
            ])
        elements.append(_make_table(
            ['Company', 'Ship', 'Rank', 'Sign On', 'Sign Off', 'Status'],
            c_rows, [120, 90, 70, 70, 70, 70]
        ))
        elements.append(Spacer(1, 10))

    # ── 11. Next of Kin ──────────────────────────────────────────────
    nok_name = _safe(user_data.get('next_of_kin_full_name'))
    if nok_name:
        elements.append(Paragraph("Next of Kin / Emergency Contact", section_style))
        nok_rows = [
            ['Full Name:', nok_name, 'Relationship:', _safe(user_data.get('next_of_kin_relationship'))],
            ['Phone:', _safe(user_data.get('next_of_kin_phone')), 'Phone 2:', _safe(user_data.get('next_of_kin_phone2'))],
            ['Email:', _safe(user_data.get('next_of_kin_email')), 'Country:', _safe(user_data.get('next_of_kin_address_country'))],
        ]
        nok_table = Table(nok_rows, colWidths=[90, 160, 90, 160])
        nok_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ]))
        elements.append(nok_table)

    # ── Build ────────────────────────────────────────────────────────
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
