// components/dashboard/Components/Modal/ViewModal/CVSubmissionViewModal.jsx
import React from "react";
import {
    User, Mail, Calendar, Briefcase,
    FileText, Building, CreditCard, Activity,
    ClipboardCheck, Star,
    Hash, CheckCircle2, Download, ShieldCheck, Anchor,
    BookOpen, Award, Clock, DollarSign, Package, BarChart2,
    AlertCircle, StickyNote, FileCheck2, MapPin, Globe
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
    const docs = submission.user_documents || {};
    const ranks = submission.coded_rank || [];
    const certs = submission.certificates || [];
    const licenses = docs.licenses || [];

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
                name={fullName}
                subtitle={`Applying for ${fmt(submission.position_name, "Unspecified Position")}`}
                status={submission.status || "Pending"}
                scale={scale}
            />

            {/* ── Core application details ─────────────────────────────────── */}
            <Section title="Application Details" icon={Briefcase} scale={scale} columns={2}>
                <FieldItem label="Status"          value={submission.status}              icon={CheckCircle2} scale={scale} />
                <FieldItem label="Submitted"       value={fmtDateTime(submission.submitted_date)} icon={Calendar} scale={scale} />
                <FieldItem label="Created At"      value={fmtDateTime(submission.created_at)} icon={Calendar} scale={scale} />
                <FieldItem label="Updated At"      value={fmtDateTime(submission.updated_at)} icon={Calendar} scale={scale} />
                <FieldItem label="Company"         value={fmt(submission.company_name)}   icon={Building}    scale={scale} />
                <FieldItem label="Position"        value={fmt(submission.position_name)}  icon={Briefcase}   scale={scale} />
                <FieldItem label="Rank Code"       value={fmt(submission.rank_code)}      icon={Anchor}      scale={scale} />
                <FieldItem label="Assigned Code"   value={fmt(submission.assigned_code)}  icon={Hash}        scale={scale} />
                <FieldItem label="Generated ID"    value={fmt(submission.generated_id)}   icon={Hash}        scale={scale} />
                <FieldItem label="Experience"      value={submission.experience_years != null ? `${submission.experience_years} yr${submission.experience_years !== 1 ? "s" : ""}` : "—"} icon={Activity} scale={scale} />
                {submission.reviewed_by && <FieldItem label="Reviewed By" value={submission.reviewed_by} icon={User} scale={scale} />}
                {submission.reviewed_date && <FieldItem label="Reviewed Date" value={fmtDateTime(submission.reviewed_date)} icon={Calendar} scale={scale} />}
            </Section>

            {/* ── Salary & Availability ────────────────────────────────────── */}
            <Section title="Salary & Availability" icon={DollarSign} scale={scale} columns={2}>
                <FieldItem label="Expected Salary" value={submission.expected_salary ? `$${submission.expected_salary}` : "—"} icon={CreditCard} scale={scale} />
                <FieldItem label="Salary Display"  value={submission.salary_display ? `$${submission.salary_display}` : "—"} icon={CreditCard} scale={scale} />
                <FieldItem label="Availability Date" value={fmtDate(submission.availability_date)} icon={Calendar} scale={scale} />
                <FieldItem label="Rating"
                    value={
                        <StarRating value={submission.rating || 0} scale={scale} />
                    }
                    icon={Star}
                    scale={scale}
                />
                <FieldItem label="Candidate Email" value={fmt(submission.user_email_display)} icon={Mail} scale={scale} />
            </Section>

            {/* ── Job Position Details ─────────────────────────────────────── */}
            {jpd && Object.keys(jpd).length > 0 && (
                <Section title="Job Position Details" icon={Package} scale={scale} columns={2}>
                    <FieldItem label="Job Position ID" value={fmt(jpd.id)}               icon={Hash}        scale={scale} />
                    <FieldItem label="Job Position Name" value={fmt(jpd.job_position_name)} icon={Briefcase} scale={scale} />
                    <FieldItem label="Quantity"         value={fmt(jpd.quantity)}         icon={BarChart2}   scale={scale} />
                    <FieldItem label="Salary Min"       value={jpd.salary_min ? `${jpd.salary_min} ${jpd.currency || ""}` : "—"} icon={DollarSign} scale={scale} />
                    <FieldItem label="Salary Max"       value={jpd.salary_max ? `${jpd.salary_max} ${jpd.currency || ""}` : "—"} icon={DollarSign} scale={scale} />
                    <FieldItem label="Contract Duration" value={jpd.contract_duration_months ? `${jpd.contract_duration_months} months` : "—"} icon={Clock} scale={scale} />
                    <FieldItem label="Remarks"          value={fmt(jpd.remarks)}          icon={StickyNote}  scale={scale} />
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

            {/* ── User Documents ───────────────────────────────────────────── */}
            <Section title="User Documents" icon={BookOpen} scale={scale} columns={1}>

                {/* Passport */}
                {docs.passport && (
                    <div style={{
                        padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                        background: "#F9FAFB", border: "1px solid #E5E7EB",
                        borderRadius: Math.round(8 * scale), marginBottom: Math.round(10 * scale),
                    }}>
                        <div style={{ fontSize: Math.round(12 * scale), fontWeight: 700, color: "#374151", marginBottom: Math.round(6 * scale) }}>
                            🛂 Passport
                        </div>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: Math.round(8 * scale) }}>
                            <FieldItem label="Passport No"  value={fmt(docs.passport.passport_no)}   icon={Hash}     scale={scale} />
                            <FieldItem label="Issue Date"   value={fmtDate(docs.passport.issue_date)}  icon={Calendar} scale={scale} />
                            <FieldItem label="Expiry Date"  value={fmtDate(docs.passport.expiry_date)} icon={AlertCircle} scale={scale} />
                            {docs.passport.issued_by && <FieldItem label="Issued By" value={docs.passport.issued_by} icon={Building} scale={scale} />}
                            {docs.passport.place_of_issue && <FieldItem label="Place of Issue" value={docs.passport.place_of_issue} icon={MapPin} scale={scale} />}
                        </div>
                    </div>
                )}

                {/* Seaman Book */}
                {docs.seaman_book && (
                    <div style={{
                        padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                        background: "#F9FAFB", border: "1px solid #E5E7EB",
                        borderRadius: Math.round(8 * scale), marginBottom: Math.round(10 * scale),
                    }}>
                        <div style={{ fontSize: Math.round(12 * scale), fontWeight: 700, color: "#374151", marginBottom: Math.round(6 * scale) }}>
                            ⚓ Seaman Book
                        </div>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: Math.round(8 * scale) }}>
                            <FieldItem label="Seaman Book No" value={fmt(docs.seaman_book.seaman_book_no)} icon={Hash} scale={scale} />
                            <FieldItem label="Issue Date"   value={fmtDate(docs.seaman_book.issue_date)}  icon={Calendar} scale={scale} />
                            <FieldItem label="Expiry Date"  value={fmtDate(docs.seaman_book.expiry_date)} icon={AlertCircle} scale={scale} />
                            {docs.seaman_book.issued_by && <FieldItem label="Issued By" value={docs.seaman_book.issued_by} icon={Building} scale={scale} />}
                            {docs.seaman_book.place_of_issue && <FieldItem label="Place of Issue" value={docs.seaman_book.place_of_issue} icon={MapPin} scale={scale} />}
                        </div>
                    </div>
                )}

                {/* Other Seaman Book */}
                {docs.other_seaman_book && (docs.other_seaman_book.seaman_book_no || docs.other_seaman_book.issue_date) && (
                    <div style={{
                        padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                        background: "#F9FAFB", border: "1px solid #E5E7EB",
                        borderRadius: Math.round(8 * scale), marginBottom: Math.round(10 * scale),
                    }}>
                        <div style={{ fontSize: Math.round(12 * scale), fontWeight: 700, color: "#374151", marginBottom: Math.round(6 * scale) }}>
                            ⚓ Other Seaman Book
                        </div>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: Math.round(8 * scale) }}>
                            <FieldItem label="Seaman Book No" value={fmt(docs.other_seaman_book.seaman_book_no)} icon={Hash} scale={scale} />
                            <FieldItem label="Issue Date"   value={fmtDate(docs.other_seaman_book.issue_date)}  icon={Calendar} scale={scale} />
                            <FieldItem label="Expiry Date"  value={fmtDate(docs.other_seaman_book.expiry_date)} icon={AlertCircle} scale={scale} />
                            {docs.other_seaman_book.issued_by && <FieldItem label="Issued By" value={docs.other_seaman_book.issued_by} icon={Building} scale={scale} />}
                            {docs.other_seaman_book.place_of_issue && <FieldItem label="Place of Issue" value={docs.other_seaman_book.place_of_issue} icon={MapPin} scale={scale} />}
                        </div>
                    </div>
                )}

                {/* COC */}
                {docs.coc && (
                    <div style={{
                        padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                        background: "#F9FAFB", border: "1px solid #E5E7EB",
                        borderRadius: Math.round(8 * scale), marginBottom: Math.round(10 * scale),
                    }}>
                        <div style={{ fontSize: Math.round(12 * scale), fontWeight: 700, color: "#374151", marginBottom: Math.round(6 * scale) }}>
                            🎓 Certificate of Competency (COC)
                        </div>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: Math.round(8 * scale) }}>
                            <FieldItem label="Certificate Name"   value={fmt(docs.coc.certificate_name)}   icon={Award} scale={scale} />
                            <FieldItem label="Certificate Number" value={fmt(docs.coc.certificate_number)} icon={Hash}  scale={scale} />
                            <FieldItem label="Issue Date"   value={fmtDate(docs.coc.issue_date)}  icon={Calendar} scale={scale} />
                            <FieldItem label="Expiry Date"  value={fmtDate(docs.coc.expiry_date)} icon={AlertCircle} scale={scale} />
                            {docs.coc.issued_by && <FieldItem label="Issued By" value={docs.coc.issued_by} icon={Building} scale={scale} />}
                            {docs.coc.issued_at && <FieldItem label="Issued At" value={docs.coc.issued_at} icon={MapPin} scale={scale} />}
                        </div>
                    </div>
                )}

                {/* GOC */}
                {docs.goc && (docs.goc.certificate_number || docs.goc.issue_date) && (
                    <div style={{
                        padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                        background: "#F9FAFB", border: "1px solid #E5E7EB",
                        borderRadius: Math.round(8 * scale), marginBottom: Math.round(10 * scale),
                    }}>
                        <div style={{ fontSize: Math.round(12 * scale), fontWeight: 700, color: "#374151", marginBottom: Math.round(6 * scale) }}>
                            📻 GMDSS (GOC)
                        </div>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: Math.round(8 * scale) }}>
                            <FieldItem label="Certificate No" value={fmt(docs.goc.certificate_number)} icon={Hash} scale={scale} />
                            <FieldItem label="Issue Date"   value={fmtDate(docs.goc.issue_date)}  icon={Calendar} scale={scale} />
                            <FieldItem label="Expiry Date"  value={fmtDate(docs.goc.expiry_date)} icon={AlertCircle} scale={scale} />
                            {docs.goc.issued_by && <FieldItem label="Issued By" value={docs.goc.issued_by} icon={Building} scale={scale} />}
                            {docs.goc.issued_at && <FieldItem label="Issued At" value={docs.goc.issued_at} icon={MapPin} scale={scale} />}
                        </div>
                    </div>
                )}

                {/* Health Certificate */}
                {docs.health_certificate && (docs.health_certificate.number || docs.health_certificate.international_medical_number) && (
                    <div style={{
                        padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                        background: "#F9FAFB", border: "1px solid #E5E7EB",
                        borderRadius: Math.round(8 * scale), marginBottom: Math.round(10 * scale),
                    }}>
                        <div style={{ fontSize: Math.round(12 * scale), fontWeight: 700, color: "#374151", marginBottom: Math.round(6 * scale) }}>
                            ⚕️ Health Certificate
                        </div>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: Math.round(8 * scale) }}>
                            {docs.health_certificate.flag_state && <FieldItem label="Flag State" value={docs.health_certificate.flag_state} icon={Globe} scale={scale} />}
                            {docs.health_certificate.number && <FieldItem label="Local Medical No" value={fmt(docs.health_certificate.number)} icon={Hash} scale={scale} />}
                            {docs.health_certificate.issue_date && <FieldItem label="Local Issue Date"   value={fmtDate(docs.health_certificate.issue_date)}  icon={Calendar} scale={scale} />}
                            {docs.health_certificate.expiry_date && <FieldItem label="Local Expiry Date"  value={fmtDate(docs.health_certificate.expiry_date)} icon={AlertCircle} scale={scale} />}
                            {docs.health_certificate.issued_by && <FieldItem label="Issued By" value={docs.health_certificate.issued_by} icon={Building} scale={scale} />}
                            {docs.health_certificate.issued_at && <FieldItem label="Issued At" value={docs.health_certificate.issued_at} icon={MapPin} scale={scale} />}
                            
                            {docs.health_certificate.international_medical_number && <FieldItem label="Int'l Medical No" value={fmt(docs.health_certificate.international_medical_number)} icon={Hash} scale={scale} />}
                            {docs.health_certificate.international_medical_issue_date && <FieldItem label="Int'l Issue Date" value={fmtDate(docs.health_certificate.international_medical_issue_date)} icon={Calendar} scale={scale} />}
                            {docs.health_certificate.international_medical_expiry_date && <FieldItem label="Int'l Expiry Date" value={fmtDate(docs.health_certificate.international_medical_expiry_date)} icon={AlertCircle} scale={scale} />}
                        </div>
                    </div>
                )}

                {/* Licenses */}
                {licenses.length > 0 && (
                    <div style={{
                        padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                        background: "#F9FAFB", border: "1px solid #E5E7EB",
                        borderRadius: Math.round(8 * scale),
                    }}>
                        <div style={{ fontSize: Math.round(12 * scale), fontWeight: 700, color: "#374151", marginBottom: Math.round(8 * scale) }}>
                            📋 Licenses
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", gap: Math.round(10 * scale) }}>
                            {licenses.map((lic) => (
                                <div key={lic.id} style={{ 
                                    display: "flex", 
                                    flexDirection: "column", 
                                    gap: Math.round(6 * scale), 
                                    padding: `${Math.round(8 * scale)}px`,
                                    border: "1px solid #F3F4F6",
                                    borderRadius: Math.round(6 * scale),
                                    background: "#FFFFFF"
                                }}>
                                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                        <span style={{ fontSize: Math.round(13 * scale), fontWeight: 600, color: "#374151" }}>
                                            {lic.document_name}
                                        </span>
                                    </div>
                                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: Math.round(8 * scale) }}>
                                        <FieldItem label="Document No" value={fmt(lic.document_number)} icon={Hash} scale={scale} />
                                        <FieldItem label="Country of Issue" value={fmt(lic.country_of_issue)} icon={Globe} scale={scale} />
                                        <FieldItem label="Issue Date" value={fmtDate(lic.issue_date)} icon={Calendar} scale={scale} />
                                        <FieldItem label="Expiration Date" value={fmtDate(lic.expiration_date)} icon={AlertCircle} scale={scale} />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {!docs.passport && !docs.seaman_book && !docs.coc && !docs.other_seaman_book && !docs.goc && !docs.health_certificate && licenses.length === 0 && (
                    <p style={{ fontSize: Math.round(13 * scale), color: "#9CA3AF", margin: 0 }}>
                        No user documents available for this submission.
                    </p>
                )}
            </Section>

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
