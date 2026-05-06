// src/components/dashboard/Components/PDF/SeafarerApplicationPDF.jsx
import React from "react";
import {
  Document,
  Page,
  Text,
  View,
  StyleSheet,
  Font,
} from "@react-pdf/renderer";

// ── Helpers ──────────────────────────────────────────────────────────────────
const val = (v, fb = "—") =>
  v !== undefined && v !== null && v !== "" ? String(v) : fb;

const fmtDate = (d) => {
  if (!d) return "—";
  try {
    return new Date(d).toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  } catch {
    return d;
  }
};

const boolCheck = (obj) => {
  if (!obj) return "—";
  const found = Object.keys(obj).find((k) => obj[k] === true);
  return found ? found.charAt(0).toUpperCase() + found.slice(1) : "—";
};

// ── Styles ───────────────────────────────────────────────────────────────────
const S = StyleSheet.create({
  page: {
    fontFamily: "Helvetica",
    fontSize: 7.5,
    paddingTop: 20,
    paddingBottom: 25,
    paddingHorizontal: 22,
    color: "#111",
  },
  // Header
  headerBox: {
    borderWidth: 1.5,
    borderColor: "#003580",
    marginBottom: 6,
    padding: 6,
    flexDirection: "row",
    alignItems: "center",
  },
  headerLeft: { flex: 1 },
  headerTitle: {
    fontSize: 14,
    fontFamily: "Helvetica-Bold",
    color: "#003580",
    letterSpacing: 1,
  },
  headerSub: { fontSize: 7, color: "#555", marginTop: 2 },
  headerRight: {
    width: 70,
    height: 70,
    borderWidth: 1,
    borderColor: "#ccc",
    alignItems: "center",
    justifyContent: "center",
  },
  photoText: { fontSize: 6.5, color: "#888" },

  // Section title
  sectionTitle: {
    backgroundColor: "#003580",
    color: "#fff",
    fontFamily: "Helvetica-Bold",
    fontSize: 8,
    paddingVertical: 3,
    paddingHorizontal: 6,
    marginTop: 6,
    marginBottom: 2,
    letterSpacing: 0.5,
  },

  // Table / row layouts
  row: { flexDirection: "row", borderBottomWidth: 0.5, borderColor: "#ccc" },
  cell: {
    borderRightWidth: 0.5,
    borderColor: "#ccc",
    paddingHorizontal: 4,
    paddingVertical: 3,
    flex: 1,
  },
  cellNoBorder: {
    paddingHorizontal: 4,
    paddingVertical: 3,
    flex: 1,
  },
  label: { fontSize: 6.5, color: "#555", marginBottom: 1 },
  value: { fontSize: 7.5, fontFamily: "Helvetica-Bold" },
  tableHeader: {
    backgroundColor: "#dce6f1",
    flexDirection: "row",
    borderBottomWidth: 1,
    borderColor: "#003580",
  },
  th: {
    flex: 1,
    paddingHorizontal: 3,
    paddingVertical: 3,
    fontSize: 6.5,
    fontFamily: "Helvetica-Bold",
    borderRightWidth: 0.5,
    borderColor: "#999",
    color: "#003580",
  },
  td: {
    flex: 1,
    paddingHorizontal: 3,
    paddingVertical: 3,
    fontSize: 7,
    borderRightWidth: 0.5,
    borderColor: "#ddd",
    borderBottomWidth: 0.5,
    borderBottomColor: "#ddd",
  },
  tableRow: { flexDirection: "row" },

  // checkbox
  checkRow: { flexDirection: "row", alignItems: "center", marginRight: 8 },
  checkbox: {
    width: 8,
    height: 8,
    borderWidth: 1,
    borderColor: "#333",
    marginRight: 2,
    alignItems: "center",
    justifyContent: "center",
  },
  checkMark: { fontSize: 6, fontFamily: "Helvetica-Bold" },

  // Footer
  footer: {
    marginTop: 8,
    borderTopWidth: 1,
    borderColor: "#003580",
    paddingTop: 4,
    fontSize: 6.5,
    color: "#555",
    textAlign: "center",
  },

  // Divider
  divider: { borderBottomWidth: 0.5, borderColor: "#ccc", marginVertical: 3 },

  // Declaration
  declarationText: { fontSize: 7, lineHeight: 1.5, marginTop: 3 },
  signLine: {
    flexDirection: "row",
    marginTop: 10,
    borderTopWidth: 0.5,
    borderColor: "#333",
    paddingTop: 3,
  },
});

// ── Sub-components ────────────────────────────────────────────────────────────

const SectionTitle = ({ children }) => (
  <Text style={S.sectionTitle}>{children}</Text>
);

const LabelValue = ({ label, value, flex }) => (
  <View style={[S.cell, flex ? { flex } : {}]}>
    <Text style={S.label}>{label}</Text>
    <Text style={S.value}>{val(value)}</Text>
  </View>
);

const LabelValueNB = ({ label, value, flex }) => (
  <View style={[S.cellNoBorder, flex ? { flex } : {}]}>
    <Text style={S.label}>{label}</Text>
    <Text style={S.value}>{val(value)}</Text>
  </View>
);

const Checkbox = ({ checked, label }) => (
  <View style={S.checkRow}>
    <View style={S.checkbox}>
      {checked && <Text style={S.checkMark}>✓</Text>}
    </View>
    <Text style={{ fontSize: 7 }}>{label}</Text>
  </View>
);

// ── Main Document ─────────────────────────────────────────────────────────────
export const SeafarerApplicationPDF = ({ app, contract }) => {
  const p1 = app?.["1_personal_details"] || {};
  const p2 = app?.["2_education"] || {};
  const p3 = app?.["3_contact_details"] || {};
  const p4 = app?.["4_travel_documents"] || [];
  const p5 = app?.["5_professional_qualification_certificate_of_competency"] || [];
  const p6 = app?.["6_next_of_kin_emergency_contact"] || {};
  const p7 = app?.["7_health_certificates_and_vaccinations"] || {};
  const p8 = app?.["8_marine_courses"] || [];
  const p9 = app?.["9_complete_sea_service_details"] || {};
  const p10 = app?.["10_references"] || [];
  const p11 = app?.["11_declaration"] || {};
  const p12 = app?.["12_for_office_use_only"] || {};

  const marline = p2.marline_test || {};
  const english = p2.english_language || {};
  const german = p2.german_language || {};
  const covid = p7.covid_19 || {};
  const healthCerts = p7.certificates || [];
  const seaService = p9.service_records || [];
  const applicantInfo = p9.applicant_info || {};
  const declarationQ = p11.questions || {};

  return (
    <Document
      title={`Seafarer Application - ${val(p1.full_name, "Applicant")}`}
      author="Sakr Manning Agency"
      subject="Seafarer Employment Application"
    >
      {/* ══════════════════════ PAGE 1 ══════════════════════ */}
      <Page size="A4" style={S.page}>

        {/* ── HEADER ── */}
        <View style={S.headerBox}>
          <View style={S.headerLeft}>
            <Text style={S.headerTitle}>SAKR MANNING AGENCY</Text>
            <Text style={S.headerSub}>SEAFARER EMPLOYMENT APPLICATION FORM</Text>
            {contract?.id && (
              <Text style={[S.headerSub, { marginTop: 4 }]}>
                Contract Ref: {contract.id}  |  Generated: {fmtDate(new Date().toISOString())}
              </Text>
            )}
          </View>
          <View style={S.headerRight}>
            <Text style={S.photoText}>PHOTO</Text>
          </View>
        </View>

        {/* ── SECTION 1: PERSONAL DETAILS ── */}
        <SectionTitle>1. PERSONAL DETAILS</SectionTitle>

        <View style={[S.row, { borderWidth: 0.5, borderColor: "#ccc" }]}>
          <LabelValue label="Full Name" value={p1.full_name} flex={3} />
          <LabelValue label="Date of Birth" value={fmtDate(p1.date_of_birth)} />
          <LabelValue label="Nationality" value={p1.nationality} />
        </View>

        <View style={[S.row, { borderWidth: 0.5, borderTopWidth: 0, borderColor: "#ccc" }]}>
          <View style={[S.cell, { flex: 2 }]}>
            <Text style={S.label}>Marital Status</Text>
            <View style={{ flexDirection: "row", marginTop: 2 }}>
              <Checkbox checked={p1.marital_status?.single} label="Single" />
              <Checkbox checked={p1.marital_status?.married} label="Married" />
            </View>
          </View>
          <LabelValue label="Height (cm)" value={p1.height_cm} />
          <LabelValue label="Weight (kg)" value={p1.weight_kg} />
          <LabelValue label="Place of Birth" value={p1.place_of_birth} />
        </View>

        <View style={[S.row, { borderWidth: 0.5, borderTopWidth: 0, borderColor: "#ccc" }]}>
          <LabelValue label="Overall Size" value={p1.overall_size} />
          <LabelValue label="Shirt Size" value={p1.shirt_size} />
          <LabelValue label="Trouser Size" value={p1.trouser_size} />
          <LabelValue label="Shoes Size" value={p1.shoes_size} />
          <LabelValue label="Nearest Port" value={p1.nearest_port} />
        </View>

        {/* ── SECTION 2: EDUCATION ── */}
        <SectionTitle>2. EDUCATION & QUALIFICATIONS</SectionTitle>

        <View style={[S.row, { borderWidth: 0.5, borderColor: "#ccc" }]}>
          <LabelValue label="College / School" value={p2.college_school} flex={2} />
          <LabelValue label="Marlins Test Issued By" value={marline.issued_by_authority} />
          <LabelValue label="Marlins Test Date" value={fmtDate(marline.issued_date)} />
          <LabelValue label="Result %" value={marline.result_percentage} />
          <LabelValue label="Issued At" value={marline.issued_at} />
        </View>

        <View style={[S.row, { borderWidth: 0.5, borderTopWidth: 0, borderColor: "#ccc" }]}>
          <View style={[S.cell, { flex: 2 }]}>
            <Text style={S.label}>English Language</Text>
            <View style={{ flexDirection: "row", marginTop: 2 }}>
              <Checkbox checked={english.fluent} label="Fluent" />
              <Checkbox checked={english.good} label="Good" />
              <Checkbox checked={english.average} label="Average" />
              <Checkbox checked={english.poor} label="Poor" />
            </View>
          </View>
          <View style={[S.cellNoBorder, { flex: 2 }]}>
            <Text style={S.label}>German Language</Text>
            <View style={{ flexDirection: "row", marginTop: 2 }}>
              <Checkbox checked={german.fluent} label="Fluent" />
              <Checkbox checked={german.good} label="Good" />
              <Checkbox checked={german.average} label="Average" />
              <Checkbox checked={german.poor} label="Poor" />
            </View>
          </View>
        </View>

        {/* ── SECTION 3: CONTACT DETAILS ── */}
        <SectionTitle>3. CONTACT DETAILS</SectionTitle>
        <View style={[S.row, { borderWidth: 0.5, borderColor: "#ccc" }]}>
          <LabelValue label="Home Address" value={p3.home_address_city} flex={3} />
          <LabelValue label="Email" value={p3.e_mail} flex={2} />
          <LabelValue label="Mobile / Tel" value={p3.mobile_tel} />
        </View>

        {/* ── SECTION 4: TRAVEL DOCUMENTS ── */}
        <SectionTitle>4. TRAVEL DOCUMENTS</SectionTitle>
        <View style={[{ borderWidth: 0.5, borderColor: "#ccc" }]}>
          <View style={S.tableHeader}>
            {["Type", "Document No.", "Issue Date", "Expiry Date", "Issued By", "Place of Issue"].map((h) => (
              <Text key={h} style={S.th}>{h}</Text>
            ))}
          </View>
          {p4.map((doc, i) => (
            <View key={i} style={S.tableRow}>
              <Text style={S.td}>{val(doc.type)}</Text>
              <Text style={S.td}>{val(doc.document_no)}</Text>
              <Text style={S.td}>{fmtDate(doc.iss_date)}</Text>
              <Text style={S.td}>{fmtDate(doc.exp_date)}</Text>
              <Text style={S.td}>{val(doc.iss_by_authority)}</Text>
              <Text style={S.td}>{val(doc.place_of_issue)}</Text>
            </View>
          ))}
        </View>

        {/* ── SECTION 5: PROFESSIONAL QUALIFICATIONS ── */}
        <SectionTitle>5. PROFESSIONAL QUALIFICATIONS / CERTIFICATES OF COMPETENCY</SectionTitle>
        <View style={[{ borderWidth: 0.5, borderColor: "#ccc" }]}>
          <View style={S.tableHeader}>
            {["Certificate Name", "Number", "Issue Date", "Expiry Date", "Issued By", "Issued At"].map((h) => (
              <Text key={h} style={S.th}>{h}</Text>
            ))}
          </View>
          {p5.map((cert, i) => (
            <View key={i} style={S.tableRow}>
              <Text style={S.td}>{val(cert.certificate_name)}</Text>
              <Text style={S.td}>{val(cert.number)}</Text>
              <Text style={S.td}>{fmtDate(cert.issue_date)}</Text>
              <Text style={S.td}>{fmtDate(cert.expiry_date)}</Text>
              <Text style={S.td}>{val(cert.issued_by)}</Text>
              <Text style={S.td}>{val(cert.issued_at)}</Text>
            </View>
          ))}
        </View>

        {/* ── SECTION 6: NEXT OF KIN ── */}
        <SectionTitle>6. NEXT OF KIN / EMERGENCY CONTACT</SectionTitle>
        <View style={[S.row, { borderWidth: 0.5, borderColor: "#ccc" }]}>
          <LabelValue label="Full Name" value={p6.full_name} flex={2} />
          <LabelValue label="Relationship" value={p6.relationship} />
          <LabelValue label="Tel / Mobile" value={p6.tel_no_mobile} />
          <LabelValue label="Address / Country" value={p6.address_country} />
          <LabelValue label="Email" value={p6.email} />
        </View>

        {/* Page footer */}
        <Text style={S.footer}>
          Sakr Manning Agency — Confidential Seafarer Application — Page 1 of 2
        </Text>
      </Page>

      {/* ══════════════════════ PAGE 2 ══════════════════════ */}
      <Page size="A4" style={S.page}>

        {/* ── SECTION 7: HEALTH CERTIFICATES ── */}
        <SectionTitle>7. HEALTH CERTIFICATES & VACCINATIONS</SectionTitle>
        <View style={[{ borderWidth: 0.5, borderColor: "#ccc" }]}>
          <View style={S.tableHeader}>
            {["Flag State / Type", "Number", "Issue Date", "Expiry Date", "Issued By", "Issued At"].map((h) => (
              <Text key={h} style={S.th}>{h}</Text>
            ))}
          </View>
          {healthCerts.map((cert, i) => (
            <View key={i} style={S.tableRow}>
              <Text style={S.td}>{val(cert.flag_state)}</Text>
              <Text style={S.td}>{val(cert.number)}</Text>
              <Text style={S.td}>{fmtDate(cert.issue_date)}</Text>
              <Text style={S.td}>{fmtDate(cert.expiry_date)}</Text>
              <Text style={S.td}>{val(cert.issued_by)}</Text>
              <Text style={S.td}>{val(cert.issued_at)}</Text>
            </View>
          ))}
        </View>

        {/* COVID-19 */}
        <View style={[S.row, { borderWidth: 0.5, borderTopWidth: 0, borderColor: "#ccc" }]}>
          <LabelValue label="COVID-19 Vaccine" value={covid.vaccination_name} />
          <LabelValue label="1st Dose" value={fmtDate(covid.first_dose)} />
          <LabelValue label="2nd Dose" value={fmtDate(covid.second_dose)} />
          <LabelValue label="Remarks" value={covid.other_does_or_remarks} flex={2} />
        </View>

        {/* ── SECTION 8: MARINE COURSES ── */}
        <SectionTitle>8. MARINE COURSES</SectionTitle>
        {p8.length === 0 ? (
          <View style={[S.row, { borderWidth: 0.5, borderColor: "#ccc" }]}>
            <View style={S.cell}>
              <Text style={{ fontSize: 7, color: "#888", fontStyle: "italic" }}>No marine courses recorded.</Text>
            </View>
          </View>
        ) : (
          <View style={[{ borderWidth: 0.5, borderColor: "#ccc" }]}>
            <View style={S.tableHeader}>
              {["Course Name", "Certificate No.", "Issue Date", "Expiry Date", "Issued By", "Issued At"].map((h) => (
                <Text key={h} style={S.th}>{h}</Text>
              ))}
            </View>
            {p8.map((c, i) => (
              <View key={i} style={S.tableRow}>
                <Text style={S.td}>{val(c.course_name ?? c.certificate_name)}</Text>
                <Text style={S.td}>{val(c.certificate_no ?? c.number)}</Text>
                <Text style={S.td}>{fmtDate(c.issue_date)}</Text>
                <Text style={S.td}>{fmtDate(c.expiry_date)}</Text>
                <Text style={S.td}>{val(c.issued_by)}</Text>
                <Text style={S.td}>{val(c.issued_at)}</Text>
              </View>
            ))}
          </View>
        )}

        {/* ── SECTION 9: SEA SERVICE ── */}
        <SectionTitle>9. COMPLETE SEA SERVICE DETAILS</SectionTitle>
        <View style={[S.row, { borderWidth: 0.5, borderColor: "#ccc" }]}>
          <LabelValue label="Applicant Name" value={applicantInfo.name} flex={3} />
          <LabelValue label="Rank" value={applicantInfo.rank} />
          <LabelValue label="Register Code" value={applicantInfo.register_code} />
        </View>
        <View style={[{ borderWidth: 0.5, borderTopWidth: 0, borderColor: "#ccc" }]}>
          <View style={S.tableHeader}>
            {["Company Name", "Rank", "Vessel / IMO", "Flag", "Sign On", "Sign Off", "Period", "Type"].map((h) => (
              <Text key={h} style={[S.th, { flex: h === "Company Name" ? 2 : 1 }]}>{h}</Text>
            ))}
          </View>
          {seaService.map((sr, i) => (
            <View key={i} style={S.tableRow}>
              <Text style={[S.td, { flex: 2 }]}>{val(sr.company_name)}</Text>
              <Text style={S.td}>{val(sr.rank)}</Text>
              <Text style={S.td}>{val(sr.vessel_name_imo_number)}</Text>
              <Text style={S.td}>{val(sr.flag)}</Text>
              <Text style={S.td}>{fmtDate(sr.signed_on)}</Text>
              <Text style={S.td}>{fmtDate(sr.signed_off)}</Text>
              <Text style={S.td}>{val(sr.period)}</Text>
              <Text style={S.td}>{val(sr.vessel_type)}</Text>
            </View>
          ))}
        </View>

        {/* ── SECTION 10: REFERENCES ── */}
        <SectionTitle>10. REFERENCES</SectionTitle>
        <View style={[{ borderWidth: 0.5, borderColor: "#ccc" }]}>
          <View style={S.tableHeader}>
            {["No.", "Company / Country", "Position", "Name", "Tel", "Email"].map((h) => (
              <Text key={h} style={S.th}>{h}</Text>
            ))}
          </View>
          {p10.map((ref, i) => (
            <View key={i} style={S.tableRow}>
              <Text style={S.td}>{val(ref.no)}</Text>
              <Text style={S.td}>{val(ref.company_management_country)}</Text>
              <Text style={S.td}>{val(ref.position)}</Text>
              <Text style={S.td}>{val(ref.name)}</Text>
              <Text style={S.td}>{val(ref.tel)}</Text>
              <Text style={S.td}>{val(ref.email)}</Text>
            </View>
          ))}
        </View>

        {/* ── SECTION 11: DECLARATION ── */}
        <SectionTitle>11. DECLARATION</SectionTitle>
        <View style={[S.row, { borderWidth: 0.5, borderColor: "#ccc" }]}>
          <View style={[S.cell, { flex: 3 }]}>
            <Text style={S.label}>Suffer from disease / unfit for sea</Text>
          </View>
          <View style={[S.cell, { flex: 1 }]}>
            <Text style={S.value}>{val(declarationQ.suffer_disease_unfit_for_sea?.answer)}</Text>
          </View>
          <View style={[S.cell, { flex: 3 }]}>
            <Text style={S.label}>Addicted to alcohol or drugs</Text>
          </View>
          <View style={[S.cellNoBorder, { flex: 1 }]}>
            <Text style={S.value}>{val(declarationQ.addicted_to_alcohol_or_drugs?.answer)}</Text>
          </View>
        </View>
        <View style={[S.row, { borderWidth: 0.5, borderTopWidth: 0, borderColor: "#ccc" }]}>
          <View style={[S.cell, { flex: 3 }]}>
            <Text style={S.label}>Suffered accident / disabled</Text>
          </View>
          <View style={[S.cell, { flex: 1 }]}>
            <Text style={S.value}>{val(declarationQ.suffer_accident_disabled?.answer)}</Text>
          </View>
          <View style={[S.cell, { flex: 3 }]}>
            <Text style={S.label}>Underwent psychiatric treatment</Text>
          </View>
          <View style={[S.cellNoBorder, { flex: 1 }]}>
            <Text style={S.value}>{val(declarationQ.undergo_psychiatric_treatment?.answer)}</Text>
          </View>
        </View>

        {/* Consent */}
        <View style={{ borderWidth: 0.5, borderTopWidth: 0, borderColor: "#ccc", padding: 6 }}>
          <Text style={S.declarationText}>
            {val(p11.consent_statement, "I hereby declare that the above facts and information are true and accurate to the best of my knowledge and belief.")}
          </Text>
        </View>

        {/* Signature block */}
        <View style={{ flexDirection: "row", marginTop: 12, borderWidth: 0.5, borderColor: "#ccc" }}>
          <View style={[S.cell, { flex: 2 }]}>
            <Text style={S.label}>Place</Text>
            <Text style={S.value}>{val(p11.place)}</Text>
          </View>
          <View style={[S.cell, { flex: 2 }]}>
            <Text style={S.label}>Date</Text>
            <Text style={S.value}>{val(p11.date)}</Text>
          </View>
          <View style={[S.cellNoBorder, { flex: 3 }]}>
            <Text style={S.label}>Applicant Signature</Text>
            <Text style={S.value}>{val(p11.signature, "________________________")}</Text>
          </View>
        </View>

        {/* ── SECTION 12: OFFICE USE ONLY ── */}
        <SectionTitle>12. FOR OFFICE USE ONLY</SectionTitle>
        <View style={[{ borderWidth: 0.5, borderColor: "#ccc" }]}>
          <View style={S.row}>
            <View style={[S.cell, { flex: 3 }]}>
              <Text style={S.label}>Initial Assessment of Applicant</Text>
              <Text style={S.value}>{val(p12.initial_assessment_of_applicant)}</Text>
            </View>
            <View style={[S.cellNoBorder, { flex: 3 }]}>
              <Text style={S.label}>Comments</Text>
              <Text style={S.value}>{val(p12.comments)}</Text>
            </View>
          </View>
          <View style={[S.row, { borderTopWidth: 0.5, borderColor: "#ccc" }]}>
            <View style={[S.cell, { flex: 2 }]}>
              <Text style={S.label}>Responsible Person Name / Signature</Text>
              <Text style={S.value}>{val(p12.responsible_person?.name_signature, "________________________")}</Text>
            </View>
            <View style={[S.cellNoBorder, { flex: 2 }]}>
              <Text style={S.label}>Date</Text>
              <Text style={S.value}>{val(p12.responsible_person?.date)}</Text>
            </View>
          </View>
        </View>

        {/* Contract info block (if from contract context) */}
        {contract && (
          <>
            <SectionTitle>CONTRACT REFERENCE</SectionTitle>
            <View style={[S.row, { borderWidth: 0.5, borderColor: "#ccc" }]}>
              <LabelValue label="Contract ID" value={contract.id} />
              <LabelValue label="Status" value={contract.status} />
              <LabelValue label="Sign On" value={fmtDate(contract.sign_on_date)} />
              <LabelValue label="Sign Off" value={fmtDate(contract.sign_off_date)} />
              <LabelValue label="Salary" value={contract.salary ? `${contract.salary} ${contract.currency || "USD"}` : null} />
            </View>
            <View style={[S.row, { borderWidth: 0.5, borderTopWidth: 0, borderColor: "#ccc" }]}>
              <LabelValue label="Ship" value={contract.ship_details?.ship_name ?? contract.ship_name} flex={2} />
              <LabelValue label="Company" value={contract.company_details?.company_name ?? contract.company_name} flex={2} />
              <LabelValue label="Rank" value={contract.rank_name} />
              <LabelValue label="Assigned Code" value={contract.assigned_code} />
            </View>
          </>
        )}

        {/* Footer */}
        <Text style={S.footer}>
          Sakr Manning Agency — Confidential Seafarer Application — Page 2 of 2
        </Text>
      </Page>
    </Document>
  );
};

export default SeafarerApplicationPDF;
