// components/dashboard/Components/Modal/ViewModal/CVSubmissionViewModal.jsx
import React from "react";
import {
    User, Mail, Calendar, Briefcase,
    FileText, Building, CreditCard, Activity,
    ClipboardCheck, Star,
    Hash, CheckCircle2, ShieldCheck, Anchor,
    BookOpen, Award, Clock, DollarSign, Package, BarChart2,
    AlertCircle, StickyNote, FileCheck2, MapPin, Globe,
    Ship, Phone, Heart, GraduationCap, Users, Waves
} from "lucide-react";
import {
    ViewDetailModal,
    Section,
    FieldItem,
    AvatarHeader,
    Tag,
} from "./ViewDetailModal";
import api from "../../../../../services/Auth/api";

// ── Helpers ──────────────────────────────────────────────────────────────────

const fmt = (val, fallback = "—") => (val !== undefined && val !== null && val !== "" ? val : fallback);

const fmtDate = (val) => {
    if (!val) return "—";
    try { return new Date(val).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }); }
    catch { return val; }
};

const fmtDateTime = (val) => {
    if (!val) return "—";
    try {
        return new Date(val).toLocaleString("en-GB", {
            day: "2-digit", month: "short", year: "numeric",
            hour: "2-digit", minute: "2-digit",
        });
    } catch { return val; }
};

// Render a simple pill/tag badge
const Badge = ({ label, color = "#6366F1", bg = "#EEF2FF", scale = 1 }) => (
    <span style={{
        display: "inline-block",
        fontSize: `${Math.round(11 * scale)}px`,
        fontFamily: "monospace",
        fontWeight: 700,
        color,
        background: bg,
        padding: `1px ${Math.round(7 * scale)}px`,
        borderRadius: 4,
        marginRight: Math.round(4 * scale),
    }}>
        {label}
    </span>
);

// Star rating display
const StarRating = ({ value = 0, max = 5, scale = 1 }) => (
    <div style={{ display: "flex", gap: Math.round(2 * scale) }}>
        {Array.from({ length: max }, (_, i) => (
            <Star
                key={i}
                size={Math.round(14 * scale)}
                fill={i < value ? "#F59E0B" : "none"}
                color={i < value ? "#F59E0B" : "#D1D5DB"}
            />
        ))}
        <span style={{ marginLeft: Math.round(4 * scale), fontSize: `${Math.round(12 * scale)}px`, color: "#6B7280" }}>
            ({value}/{max})
        </span>
    </div>
);

// ── Main component ────────────────────────────────────────────────────────────

/**
 * CVSubmissionViewModal — rich detail view for a single CV Submission.
 *
 * Expects the full payload from GET /cv-submissions/{id}/:
 *   id, user, user_name, user_email_display, generated_id,
 *   company_name, position_name, rank_code, assigned_code,
 *   cv_file, cover_letter, experience_years, expected_salary,
 *   availability_date, status, submitted_date, notes, rating,
 *   salary_display, job_position_details, coded_rank[],
 *   certificates[], user_documents { passport, seaman_book, coc, licenses[] }
 */
export function CVSubmissionViewModal({
    isOpen,
    onClose,
    submission,
    onDelete,
    scale = 1,
    canDelete = true,
}) {
    if (!submission) return null;

    const fullName = fmt(submission.user_name, "Unknown Candidate");
    const jpd = submission.job_position_details || {};
    const ranks = submission.coded_rank || [];
    const certs = submission.certificates || [];
    const sa = submission.seafarer_application || {};
    const companyDetails = submission.company_details || null;
    const shipDetails = submission.ship_details || null;
    const user_documents = submission.user_documents || {};

    // seafarer_application sections
    const saPersonal = sa["1_personal_details"] || null;
    const saEducation = sa["2_education"] || null;
    const saContact = sa["3_contact_details"] || null;
    const saTravelDocs = sa["4_travel_documents"] || [];
    const saCerts = sa["5_professional_qualification_certificate_of_competency"] || [];
    const saNextOfKin = sa["6_next_of_kin_emergency_contact"] || null;
    const saHealth = sa["7_health_certificates_and_vaccinations"] || null;
    const saCourses = sa["8_marine_courses"] || [];
    const saSeaService = sa["9_complete_sea_service_details"] || null;
    const saRefs = sa["10_references"] || [];
    const saDecl = sa["11_declaration"] || null;

    // ── Actions ───────────────────────────────────────────────────────────────
    const actions = [];

    if (["Approved", "Hired", "Shortlisted"].includes(submission.status)) {
        actions.push({
            label: "Generate Contract",
            onClick: () => {
                if (onClose) onClose();
                document.dispatchEvent(new CustomEvent("generate-contract", { detail: submission }));
            },
            variant: "success",
        });
    }

    if (canDelete && onDelete) {
        actions.push({
            label: "Remove",
            onClick: () => onDelete(submission.id),
            variant: "danger",
        });
    }

    actions.push({ label: "Close", onClick: onClose, variant: "primary" });

    // ── Render ────────────────────────────────────────────────────────────────
    return (
        <ViewDetailModal
            isOpen={isOpen}
            onClose={onClose}
            title="Application Details"
            subtitle={`Submission #${submission.id}  ·  ${fmt(submission.generated_id, "No ID")}`}
            actions={actions}
            scale={scale}
            size="xl"
        >
            {/* ── Candidate header ─────────────────────────────────────────── */}
            <AvatarHeader
                image={submission.user?.profile_image || submission.profile_image}
                name={fullName}
                subtitle={`Applying for ${fmt(submission.position_name, "Unspecified Position")}`}
                status={submission.status || "Pending"}
                scale={scale}
            />

            {/* ── Core application details ─────────────────────────────────── */}
            <Section title="Application Details" icon={Briefcase} scale={scale} columns={2}>
                <FieldItem label="Status" value={submission.status} icon={CheckCircle2} scale={scale} />
                <FieldItem label="Submitted" value={fmtDateTime(submission.submitted_date)} icon={Calendar} scale={scale} />
                <FieldItem label="Created At" value={fmtDateTime(submission.created_at)} icon={Calendar} scale={scale} />
                <FieldItem label="Updated At" value={fmtDateTime(submission.updated_at)} icon={Calendar} scale={scale} />
                <FieldItem label="Company" value={fmt(submission.company_name)} icon={Building} scale={scale} />
                <FieldItem label="Position" value={fmt(submission.position_name)} icon={Briefcase} scale={scale} />
                <FieldItem label="Rank Code" value={fmt(submission.rank_code)} icon={Anchor} scale={scale} />
                <FieldItem label="Assigned Code" value={fmt(submission.assigned_code)} icon={Hash} scale={scale} />
                <FieldItem label="Generated ID" value={fmt(submission.generated_id)} icon={Hash} scale={scale} />
                <FieldItem label="Experience" value={submission.experience_years != null ? `${submission.experience_years} yr${submission.experience_years !== 1 ? "s" : ""}` : "—"} icon={Activity} scale={scale} />
                {submission.cv_file && <FieldItem label="CV Document" value={submission.cv_file} format="link" icon={FileText} scale={scale} />}
                {submission.reviewed_by && <FieldItem label="Reviewed By" value={submission.reviewed_by} icon={User} scale={scale} />}
                {submission.reviewed_date && <FieldItem label="Reviewed Date" value={fmtDateTime(submission.reviewed_date)} icon={Calendar} scale={scale} />}
            </Section>

            {/* ── Salary & Availability ────────────────────────────────────── */}
            <Section title="Salary & Availability" icon={DollarSign} scale={scale} columns={2}>
                <FieldItem label="Expected Salary" value={submission.expected_salary ? (String(submission.expected_salary).includes("USD") || String(submission.expected_salary).includes("$") ? submission.expected_salary : `$${submission.expected_salary}`) : "—"} icon={CreditCard} scale={scale} />
                <FieldItem label="Salary" value={(submission.salary_display || submission.salary) ? (String(submission.salary || submission.salary_display).includes("USD") || String(submission.salary_display).includes("$") ? submission.salary_display : `$${submission.salary_display}`) : "—"} icon={CreditCard} scale={scale} />
                <FieldItem label="Availability Date" value={fmtDate(submission.available_date || submission.availability_date)} icon={Calendar} scale={scale} />
                {submission.rating && <FieldItem label="Rating"
                    value={
                        <StarRating value={submission.rating || 0} scale={scale} />
                    }
                    icon={Star}
                    scale={scale}
                />}
                <FieldItem label="Candidate Email" value={fmt(submission.user_email_display)} icon={Mail} scale={scale} />
            </Section>

            {/* ── Job Position Details ─────────────────────────────────────── */}
            {jpd && Object.keys(jpd).length > 0 && (
                <Section title="Job Position Details" icon={Package} scale={scale} columns={2}>
                    <FieldItem label="Job Position ID" value={fmt(jpd.id)} icon={Hash} scale={scale} />
                    <FieldItem label="Job Position Name" value={fmt(jpd.job_position_name)} icon={Briefcase} scale={scale} />
                    <FieldItem label="Quantity" value={fmt(jpd.quantity)} icon={BarChart2} scale={scale} />
                    <FieldItem label="Salary Min" value={jpd.salary_min ? `${jpd.salary_min} ${jpd.currency || ""}` : "—"} icon={DollarSign} scale={scale} />
                    <FieldItem label="Salary Max" value={jpd.salary_max ? `${jpd.salary_max} ${jpd.currency || ""}` : "—"} icon={DollarSign} scale={scale} />
                    <FieldItem label="Contract Duration" value={jpd.contract_duration_months ? `${jpd.contract_duration_months} months` : "—"} icon={Clock} scale={scale} />
                    <FieldItem label="Remarks" value={fmt(jpd.remarks)} icon={StickyNote} scale={scale} />
                </Section>
            )}

            {/* ── Company Details ──────────────────────────────────────────── */}
            <Section title="Company Details" icon={Building} scale={scale} columns={2}>
                <FieldItem label="Company Name" value={fmt(companyDetails?.company_name ?? submission.company_name)} icon={Building} scale={scale} />
                <FieldItem label="Company Type" value={fmt(companyDetails?.company_type_name || companyDetails?.company_type)} icon={Briefcase} scale={scale} />
                <FieldItem label="Country" value={fmt(companyDetails?.company_flag_name || companyDetails?.company_flag)} icon={Globe} scale={scale} />
                <FieldItem label="Contact Person" value={fmt(companyDetails?.contact_person)} icon={User} scale={scale} />
                <FieldItem label="Contact Email" value={fmt(companyDetails?.contact_email)} icon={Mail} scale={scale} />
                <FieldItem label="Status" value={fmt(companyDetails?.status)} icon={CheckCircle2} scale={scale} />
            </Section>

            {/* ── Ship Details ─────────────────────────────────────────────── */}
            <Section title="Ship Details" icon={Ship} scale={scale} columns={2}>
                <FieldItem label="Ship Name" value={fmt(shipDetails?.ship_name ?? submission.ship_name)} icon={Ship} scale={scale} />
                <FieldItem label="IMO Number" value={fmt(shipDetails?.imo_number)} icon={Hash} scale={scale} />
                <FieldItem label="Ship Type" value={fmt(shipDetails?.ship_type_name || shipDetails?.ship_type)} icon={Waves} scale={scale} />
                <FieldItem label="Flag" value={fmt(shipDetails?.flag_name || shipDetails?.flag)} icon={Globe} scale={scale} />
                <FieldItem label="Status" value={fmt(shipDetails?.status)} icon={CheckCircle2} scale={scale} />
            </Section>

            {/* ── Position Details ─────────────────────────────────────────── */}
            <Section title="Position Details" icon={Anchor} scale={scale} columns={2}>
                <FieldItem label="Position Name" value={fmt(submission.position_name)} icon={Briefcase} scale={scale} />
                <FieldItem label="Rank Code" value={fmt(submission.rank_code)} icon={ShieldCheck} scale={scale} />
                <FieldItem label="Assigned Code" value={fmt(submission.assigned_code)} icon={Hash} scale={scale} />
                <FieldItem label="Experience" value={submission.experience_years != null ? `${submission.experience_years} yr${submission.experience_years !== 1 ? "s" : ""}` : "—"} icon={Activity} scale={scale} />
            </Section>

            {/* ══════════════════════════════════════════════════════════════ */}
            {/* ── Seafarer Application ──────────────────────────────────── */}
            {/* ══════════════════════════════════════════════════════════════ */}

            {/* 1. Personal Details */}
            {saPersonal && (
                <Section title="Personal Details" icon={User} scale={scale} columns={2}>
                    <FieldItem label="Full Name" value={fmt(saPersonal.full_name)} icon={User} scale={scale} />
                    <FieldItem label="Date of Birth" value={fmtDate(saPersonal.date_of_birth)} icon={Calendar} scale={scale} />
                    <FieldItem label="Nationality" value={fmt(saPersonal.nationality)} icon={Globe} scale={scale} />
                    <FieldItem label="Place of Birth" value={fmt(saPersonal.place_of_birth)} icon={MapPin} scale={scale} />
                    <FieldItem label="Marital Status" value={saPersonal.marital_status ? (saPersonal.marital_status.married ? "Married" : saPersonal.marital_status.single ? "Single" : "—") : "—"} icon={Heart} scale={scale} />
                    <FieldItem label="Nearest Port" value={fmt(saPersonal.nearest_port)} icon={Anchor} scale={scale} />
                    <FieldItem label="Height (cm)" value={fmt(saPersonal.height_cm)} icon={Activity} scale={scale} />
                    <FieldItem label="Weight (kg)" value={fmt(saPersonal.weight_kg)} icon={Activity} scale={scale} />
                    <FieldItem label="Overall Size" value={fmt(saPersonal.overall_size)} icon={Package} scale={scale} />
                    <FieldItem label="Shirt Size" value={fmt(saPersonal.shirt_size)} icon={Package} scale={scale} />
                    <FieldItem label="Trouser Size" value={fmt(saPersonal.trouser_size)} icon={Package} scale={scale} />
                    <FieldItem label="Shoes Size" value={fmt(saPersonal.shoes_size)} icon={Package} scale={scale} />
                </Section>
            )}

            {/* 3. Contact Details */}
            {saContact && (
                <Section title="Contact Details" icon={Phone} scale={scale} columns={2}>
                    <FieldItem label="Email" value={fmt(saContact.e_mail)} icon={Mail} scale={scale} />
                    <FieldItem label="Mobile" value={fmt(saContact.mobile_tel)} icon={Phone} scale={scale} />
                    <FieldItem label="Home Address" value={fmt(saContact.home_address_city)} icon={MapPin} scale={scale} />
                </Section>
            )}

            {/* 2. Education */}
            {saEducation && (
                <Section title="Education" icon={GraduationCap} scale={scale} columns={2}>
                    <FieldItem label="College / School" value={fmt(saEducation.college_school)} icon={GraduationCap} scale={scale} />
                    {saEducation.marline_test && (
                        <>
                            <FieldItem label="Marline Test Date" value={fmtDate(saEducation.marline_test.issued_date)} icon={Calendar} scale={scale} />
                            <FieldItem label="Marline Result" value={fmt(saEducation.marline_test.result_percentage) !== "—" ? `${saEducation.marline_test.result_percentage}%` : "—"} icon={BarChart2} scale={scale} />
                            <FieldItem label="Marline Issued By" value={fmt(saEducation.marline_test.issued_by_authority)} icon={Building} scale={scale} />
                            <FieldItem label="Marline Issued At" value={fmt(saEducation.marline_test.issued_at)} icon={MapPin} scale={scale} />
                        </>
                    )}
                    <FieldItem label="English" value={saEducation.english_language ? Object.entries(saEducation.english_language).find(([, v]) => v)?.[0] || "—" : "—"} icon={BookOpen} scale={scale} />
                    <FieldItem label="German" value={saEducation.german_language ? Object.entries(saEducation.german_language).find(([, v]) => v)?.[0] || "—" : "—"} icon={BookOpen} scale={scale} />
                </Section>
            )}

            {/* 4. Travel Documents */}
            {saTravelDocs.length > 0 && (
                <Section title="Travel Documents" icon={FileText} scale={scale} columns={1}>
                    {saTravelDocs.map((doc, i) => (
                        <div key={i} style={{
                            padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                            background: "#F9FAFB", border: "1px solid #E5E7EB",
                            borderRadius: Math.round(8 * scale), marginBottom: Math.round(8 * scale),
                        }}>
                            <div style={{ fontSize: Math.round(12 * scale), fontWeight: 700, color: "#374151", marginBottom: Math.round(6 * scale) }}>
                                {doc.type || `Document ${i + 1}`}
                            </div>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: Math.round(8 * scale) }}>
                                <FieldItem label="Doc No" value={fmt(doc.document_no)} icon={Hash} scale={scale} />
                                <FieldItem label="Issue Date" value={fmtDate(doc.iss_date)} icon={Calendar} scale={scale} />
                                <FieldItem label="Expiry Date" value={fmtDate(doc.exp_date)} icon={AlertCircle} scale={scale} />
                                <FieldItem label="Issued By" value={fmt(doc.iss_by_authority)} icon={Building} scale={scale} />
                                <FieldItem label="Place of Issue" value={fmt(doc.place_of_issue)} icon={MapPin} scale={scale} />
                                {(doc.type?.toLowerCase() === "passport" && (user_documents?.passport?.file_url || user_documents?.passport?.download_url)) && (
                                    <FieldItem label="Attachment" value={user_documents.passport.file_url || user_documents.passport.download_url} format="link" icon={FileText} scale={scale} />
                                )}
                                {(doc.type?.toLowerCase() === "seaman book" && (user_documents?.seaman_book?.file_url || user_documents?.seaman_book?.download_url)) && (
                                    <FieldItem label="Attachment" value={user_documents.seaman_book.file_url || user_documents.seaman_book.download_url} format="link" icon={FileText} scale={scale} />
                                )}
                                {(doc.type?.toLowerCase() === "other seaman book" && (user_documents?.other_seaman_book?.file_url || user_documents?.other_seaman_book?.download_url)) && (
                                    <FieldItem label="Attachment" value={user_documents.other_seaman_book.file_url || user_documents.other_seaman_book.download_url} format="link" icon={FileText} scale={scale} />
                                )}
                            </div>
                        </div>
                    ))}
                </Section>
            )}

            {/* 5. Professional Certificates */}
            {saCerts.length > 0 && (
                <Section title="Professional Qualifications" icon={Award} scale={scale} columns={1}>
                    {saCerts.map((c, i) => (
                        <div key={i} style={{
                            padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                            background: "#F9FAFB", border: "1px solid #E5E7EB",
                            borderRadius: Math.round(8 * scale), marginBottom: Math.round(8 * scale),
                        }}>
                            <div style={{ fontSize: Math.round(12 * scale), fontWeight: 700, color: "#374151", marginBottom: Math.round(6 * scale) }}>
                                🎓 {fmt(c.certificate_name, `Certificate ${i + 1}`)}
                            </div>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: Math.round(8 * scale) }}>
                                <FieldItem label="Number" value={fmt(c.number)} icon={Hash} scale={scale} />
                                <FieldItem label="Issue Date" value={fmtDate(c.issue_date)} icon={Calendar} scale={scale} />
                                <FieldItem label="Expiry Date" value={fmtDate(c.expiry_date)} icon={AlertCircle} scale={scale} />
                                <FieldItem label="Issued By" value={fmt(c.issued_by)} icon={Building} scale={scale} />
                                <FieldItem label="Issued At" value={fmt(c.issued_at)} icon={MapPin} scale={scale} />
                                {(c.certificate_name?.toLowerCase()?.includes("coc") && (user_documents?.coc?.file_url || user_documents?.coc?.download_url)) && (
                                    <FieldItem label="Attachment" value={user_documents.coc.file_url || user_documents.coc.download_url} format="link" icon={FileText} scale={scale} />
                                )}
                                {(c.certificate_name?.toLowerCase()?.includes("goc") && (user_documents?.goc?.file_url || user_documents?.goc?.download_url)) && (
                                    <FieldItem label="Attachment" value={user_documents.goc.file_url || user_documents.goc.download_url} format="link" icon={FileText} scale={scale} />
                                )}
                            </div>
                        </div>
                    ))}
                </Section>
            )}

            {/* 6. Next of Kin */}
            {saNextOfKin && (
                <Section title="Next of Kin / Emergency Contact" icon={Users} scale={scale} columns={2}>
                    <FieldItem label="Full Name" value={fmt(saNextOfKin.full_name)} icon={User} scale={scale} />
                    <FieldItem label="Relationship" value={fmt(saNextOfKin.relationship)} icon={Heart} scale={scale} />
                    <FieldItem label="Mobile" value={fmt(saNextOfKin.tel_no_mobile)} icon={Phone} scale={scale} />
                    <FieldItem label="Email" value={fmt(saNextOfKin.email)} icon={Mail} scale={scale} />
                    <FieldItem label="Country" value={fmt(saNextOfKin.address_country)} icon={Globe} scale={scale} />
                </Section>
            )}

            {/* 7. Health Certificates & Vaccinations */}
            {(saHealth || user_documents.health_certificate) && (
                <Section title="Health Certificates & Vaccinations" icon={ShieldCheck} scale={scale} columns={1}>
                    {saHealth && (saHealth.certificates || []).map((hc, i) => {
                        const hcDoc = (user_documents.health_certificate?.records || []).find(
                            (r) => r.vaccine_name?.toLowerCase() === hc.flag_state?.toLowerCase()
                        );
                        return (
                            <div key={i} style={{
                                padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                                background: "#F9FAFB", border: "1px solid #E5E7EB",
                                borderRadius: Math.round(8 * scale), marginBottom: Math.round(8 * scale),
                            }}>
                                <div style={{ fontSize: Math.round(12 * scale), fontWeight: 700, color: "#374151", marginBottom: Math.round(6 * scale) }}>
                                    ⚕️ {fmt(hc.flag_state, `Health Cert ${i + 1}`)}
                                </div>
                                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: Math.round(8 * scale) }}>
                                    <FieldItem label="Number" value={fmt(hc.number)} icon={Hash} scale={scale} />
                                    <FieldItem label="Issue Date" value={fmtDate(hc.issue_date)} icon={Calendar} scale={scale} />
                                    <FieldItem label="Expiry Date" value={fmtDate(hc.expiry_date)} icon={AlertCircle} scale={scale} />
                                    <FieldItem label="Issued By" value={fmt(hc.issued_by)} icon={Building} scale={scale} />
                                    <FieldItem label="Issued At" value={fmt(hc.issued_at)} icon={MapPin} scale={scale} />
                                    {hcDoc && (hcDoc.file_url || hcDoc.download_url) && (
                                        <FieldItem label="Attachment" value={hcDoc.file_url || hcDoc.download_url} format="link" icon={FileText} scale={scale} />
                                    )}
                                </div>
                            </div>
                        );
                    })}
                    {user_documents.health_certificate?.international_medical_number && (
                        <div style={{
                            padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                            background: "#F0F9FF", border: "1px solid #BAE6FD",
                            borderRadius: Math.round(8 * scale), marginBottom: Math.round(8 * scale),
                        }}>
                            <div style={{ fontSize: Math.round(12 * scale), fontWeight: 700, color: "#0369A1", marginBottom: Math.round(6 * scale) }}>
                                🌐 International Medical Certificate
                            </div>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: Math.round(8 * scale) }}>
                                <FieldItem label="Number" value={fmt(user_documents.health_certificate.international_medical_number)} icon={Hash} scale={scale} />
                                <FieldItem label="Issue Date" value={fmtDate(user_documents.health_certificate.international_medical_issue_date)} icon={Calendar} scale={scale} />
                                <FieldItem label="Expiry Date" value={fmtDate(user_documents.health_certificate.international_medical_expiry_date)} icon={AlertCircle} scale={scale} />
                                {(user_documents.health_certificate.file_url || user_documents.health_certificate.download_url) && (
                                    <FieldItem label="Attachment" value={user_documents.health_certificate.file_url || user_documents.health_certificate.download_url} format="link" icon={FileText} scale={scale} />
                                )}
                            </div>
                        </div>
                    )}
                    {saHealth?.covid_19 && (
                        <div style={{
                            padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                            background: "#F0FDF4", border: "1px solid #BBF7D0",
                            borderRadius: Math.round(8 * scale),
                        }}>
                            <div style={{ fontSize: Math.round(12 * scale), fontWeight: 700, color: "#15803D", marginBottom: Math.round(6 * scale) }}>
                                💉 COVID-19 Vaccination
                            </div>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: Math.round(8 * scale) }}>
                                <FieldItem label="Vaccine Name" value={fmt(saHealth.covid_19.vaccination_name)} icon={ShieldCheck} scale={scale} />
                                <FieldItem label="1st Dose" value={fmtDate(saHealth.covid_19.first_dose)} icon={Calendar} scale={scale} />
                                <FieldItem label="2nd Dose" value={fmtDate(saHealth.covid_19.second_dose)} icon={Calendar} scale={scale} />
                                <FieldItem label="Remarks" value={fmt(saHealth.covid_19.other_does_or_remarks)} icon={StickyNote} scale={scale} />
                            </div>
                        </div>
                    )}
                </Section>
            )}

            {/* 8. Marine Courses */}
            {saCourses.length > 0 && (
                <Section title="Marine Courses" icon={BookOpen} scale={scale} columns={1}>
                    {saCourses.map((c, i) => {
                        const courseDoc = (user_documents.marine_courses || []).find(
                            (dc) => dc.course_name?.toLowerCase() === (c.course_name ?? c.name ?? c.certificate_name)?.toLowerCase()
                        );
                        return (
                            <div key={i} style={{
                                padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                                background: "#F9FAFB", border: "1px solid #E5E7EB",
                                borderRadius: Math.round(8 * scale), marginBottom: Math.round(8 * scale),
                            }}>
                                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: Math.round(8 * scale) }}>
                                    <FieldItem label="Course" value={fmt(c.course_name ?? c.name ?? c.certificate_name)} icon={BookOpen} scale={scale} />
                                    <FieldItem label="Number" value={fmt(c.number)} icon={Hash} scale={scale} />
                                    <FieldItem label="Issue Date" value={fmtDate(c.issue_date)} icon={Calendar} scale={scale} />
                                    <FieldItem label="Expiry Date" value={fmtDate(c.expiry_date)} icon={AlertCircle} scale={scale} />
                                    <FieldItem label="Issued By" value={fmt(c.issued_by)} icon={Building} scale={scale} />
                                    <FieldItem label="Issued At" value={fmt(c.issued_at)} icon={MapPin} scale={scale} />
                                    {courseDoc && (courseDoc.file_url || courseDoc.download_url) && (
                                        <FieldItem label="Attachment" value={courseDoc.file_url || courseDoc.download_url} format="link" icon={FileText} scale={scale} />
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </Section>
            )}

            {/* 9. Sea Service Records */}
            {saSeaService && saSeaService.service_records && saSeaService.service_records.length > 0 && (
                <Section title="Sea Service Records" icon={Waves} scale={scale} columns={1}>
                    {saSeaService.service_records.map((sr, i) => {
                        const ssDoc = (user_documents.sea_service || []).find(
                            (ds) => {
                                const vesselMatch = ds.vessel_name && sr.vessel_name_imo_number?.toLowerCase()?.includes(ds.vessel_name?.toLowerCase());
                                const dateMatch = ds.signed_on === sr.signed_on;
                                return vesselMatch || dateMatch;
                            }
                        );
                        return (
                            <div key={i} style={{
                                padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                                background: "#F9FAFB", border: "1px solid #E5E7EB",
                                borderRadius: Math.round(8 * scale), marginBottom: Math.round(8 * scale),
                            }}>
                                <div style={{ fontSize: Math.round(12 * scale), fontWeight: 700, color: "#374151", marginBottom: Math.round(6 * scale) }}>
                                    🚢 {fmt(sr.company_name)} — {fmt(sr.vessel_name_imo_number)}
                                </div>
                                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: Math.round(8 * scale) }}>
                                    <FieldItem label="Rank" value={fmt(sr.rank)} icon={Anchor} scale={scale} />
                                    <FieldItem label="Signed On" value={fmtDate(sr.signed_on)} icon={Calendar} scale={scale} />
                                    <FieldItem label="Signed Off" value={fmtDate(sr.signed_off)} icon={Calendar} scale={scale} />
                                    <FieldItem label="Period" value={fmt(sr.period)} icon={Clock} scale={scale} />
                                    <FieldItem label="Flag" value={fmt(sr.flag)} icon={Globe} scale={scale} />
                                    <FieldItem label="Vessel Type" value={fmt(sr.vessel_type)} icon={Ship} scale={scale} />
                                    {ssDoc && (ssDoc.file_url || ssDoc.download_url) && (
                                        <FieldItem label="Attachment" value={ssDoc.file_url || ssDoc.download_url} format="link" icon={FileText} scale={scale} />
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </Section>
            )}

            {/* 10. References */}
            {saRefs.length > 0 && (
                <Section title="References" icon={Users} scale={scale} columns={1}>
                    {saRefs.map((ref, i) => (
                        <div key={i} style={{
                            padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                            background: "#F9FAFB", border: "1px solid #E5E7EB",
                            borderRadius: Math.round(8 * scale), marginBottom: Math.round(8 * scale),
                        }}>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: Math.round(8 * scale) }}>
                                <FieldItem label="Name" value={fmt(ref.name)} icon={User} scale={scale} />
                                <FieldItem label="Position" value={fmt(ref.position)} icon={Briefcase} scale={scale} />
                                <FieldItem label="Company" value={fmt(ref.company_management_country)} icon={Building} scale={scale} />
                                <FieldItem label="Tel" value={fmt(ref.tel)} icon={Phone} scale={scale} />
                                <FieldItem label="Email" value={fmt(ref.email)} icon={Mail} scale={scale} />
                            </div>
                        </div>
                    ))}
                </Section>
            )}

            {/* ── Coded Ranks ──────────────────────────────────────────────── */}
            <Section title="Assigned Rank Codes" icon={ShieldCheck} scale={scale} columns={1}>
                {ranks.length > 0 ? (
                    <div style={{ display: "flex", flexWrap: "wrap", gap: Math.round(8 * scale) }}>
                        {ranks.map((r, i) => (
                            <div key={i} style={{
                                display: "flex", alignItems: "center", gap: Math.round(8 * scale),
                                padding: `${Math.round(6 * scale)}px ${Math.round(12 * scale)}px`,
                                background: "#F8F7FF", border: "1px solid #E9E6FF",
                                borderRadius: Math.round(8 * scale),
                            }}>
                                <Anchor size={Math.round(13 * scale)} color="#6366F1" />
                                <div>
                                    {r.rank_name && (
                                        <div style={{ fontSize: Math.round(13 * scale), fontWeight: 600, color: "#1F2937" }}>
                                            {r.rank_name}
                                        </div>
                                    )}
                                    <div style={{ display: "flex", gap: Math.round(6 * scale), flexWrap: "wrap", marginTop: 2 }}>
                                        {r.rank_code && <Badge label={r.rank_code} color="#6B7280" bg="#F3F4F6" scale={scale} />}
                                        {r.assigned_code && <Badge label={r.assigned_code} color="#4F46E5" bg="#EEF2FF" scale={scale} />}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p style={{ fontSize: Math.round(13 * scale), color: "#9CA3AF", margin: 0 }}>
                        No rank codes assigned to this submission yet.
                    </p>
                )}
            </Section>

            {/* ── Certificates ─────────────────────────────────────────────── */}
            {certs.length > 0 && (
                <Section title="Certificates" icon={Award} scale={scale} columns={1}>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: Math.round(8 * scale) }}>
                        {certs.map((c) => (
                            <div key={c.id} style={{
                                display: "flex", alignItems: "center", gap: Math.round(6 * scale),
                                padding: `${Math.round(5 * scale)}px ${Math.round(10 * scale)}px`,
                                background: "#F0FDF4", border: "1px solid #BBF7D0",
                                borderRadius: Math.round(6 * scale),
                            }}>
                                <FileCheck2 size={Math.round(13 * scale)} color="#16A34A" />
                                <span style={{ fontSize: Math.round(12 * scale), fontWeight: 600, color: "#15803D" }}>
                                    {c.code}
                                </span>
                                <span style={{ fontSize: Math.round(12 * scale), color: "#374151" }}>
                                    {c.name}
                                </span>
                            </div>
                        ))}
                    </div>
                </Section>
            )}


            {/* ── Cover Letter ─────────────────────────────────────────────── */}
            {submission.cover_letter && (
                <Section title="Cover Letter" icon={FileText} scale={scale} columns={1}>
                    <p style={{
                        fontSize: Math.round(13 * scale), color: "#374151",
                        lineHeight: 1.6, whiteSpace: "pre-wrap", margin: 0,
                        padding: `${Math.round(10 * scale)}px ${Math.round(12 * scale)}px`,
                        background: "#FAFAFA", borderRadius: Math.round(6 * scale),
                        border: "1px solid #F0F0F0",
                    }}>
                        {submission.cover_letter}
                    </p>
                </Section>
            )}

            {/* ── Internal Notes ───────────────────────────────────────────── */}
            {submission.notes && (
                <Section title="Internal Notes" icon={ClipboardCheck} scale={scale} columns={1}>
                    <p style={{
                        fontSize: Math.round(13 * scale), color: "#374151",
                        lineHeight: 1.6, whiteSpace: "pre-wrap", margin: 0,
                        padding: `${Math.round(10 * scale)}px ${Math.round(12 * scale)}px`,
                        background: "#FFFBEB", borderRadius: Math.round(6 * scale),
                        border: "1px solid #FDE68A",
                    }}>
                        {submission.notes}
                    </p>
                </Section>
            )}
        </ViewDetailModal>
    );
}

export default CVSubmissionViewModal;
