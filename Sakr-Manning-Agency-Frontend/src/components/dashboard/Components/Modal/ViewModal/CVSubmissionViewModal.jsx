// components/dashboard/Components/Modal/ViewModal/CVSubmissionViewModal.jsx
import React from "react";
import {
    User, Phone, Mail, Calendar, Briefcase,
    FileText, Building, CreditCard, Activity,
    History, ClipboardCheck, Star,
    Hash, CheckCircle2, Clock, Download, ShieldCheck, Anchor
} from "lucide-react";
import {
    ViewDetailModal,
    Section,
    FieldItem,
    AvatarHeader,
    Tag,
} from "./ViewDetailModal";

/**
 * CVSubmissionViewModal - Dedicated view for recruitment pipeline entries (Section 4)
 * 
 * Displays:
 * - Application Status & Pipeline progress
 * - Company & Position details
 * - Expected salary & Availability
 * - Cover letter & Internal notes
 * - Linked Seafarer basic info
 * - Assigned Rank Codes (from ranks[] array)
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

    const user = submission.user_detail || {};
    const fullName = submission.user_name || [user.first_name, user.last_name].filter(Boolean).join(" ") || "Unknown Candidate";

    // Build actions array
    const actions = [];
    if (canDelete && onDelete) {
        actions.push({
            label: "Remove",
            onClick: () => onDelete(submission.id),
            variant: "danger",
        });
    }
    actions.push({
        label: "Close",
        onClick: onClose,
        variant: "primary",
    });

    // Normalize ranks: may come as submission.ranks or submission.coded_rank
    const ranks = submission.ranks || submission.coded_rank || [];

    return (
        <ViewDetailModal
            isOpen={isOpen}
            onClose={onClose}
            title="Application Details"
            subtitle={`Submission ID: ${submission.id}`}
            actions={actions}
            scale={scale}
            size="xl"
        >
            {/* Header: Candidate & Status */}
            <AvatarHeader
                image={user.profile_image}
                name={fullName}
                subtitle={`Applying for ${submission.position_name || submission.position || "Unspecified Position"}`}
                status={submission.status || "Pending"}
                scale={scale}
            />

            {/* Core Application Details */}
            <Section title="Application Details" icon={Briefcase} scale={scale} columns={2}>
                <FieldItem label="Status" value={submission.status} icon={CheckCircle2} scale={scale} />
                <FieldItem label="Submission Date" value={submission.submitted_date} format="date" icon={Calendar} scale={scale} />

                <FieldItem label="Company" value={submission.company_name || `ID: ${submission.company || 'Not Specified'}`} icon={Building} scale={scale} />
                <FieldItem label="Position" value={submission.position_name || submission.position || "—"} icon={Briefcase} scale={scale} />
                <FieldItem label="Generated ID" value={submission.generated_id || "Pending"} icon={Hash} scale={scale} />
                <FieldItem label="Experience" value={submission.experience_years ? `${submission.experience_years} Years` : "—"} icon={Activity} scale={scale} />
                <FieldItem label="Salary Expectations" value={submission.salary} icon={CreditCard} scale={scale} />
            </Section>

            {/* Assigned Rank Codes */}
            {ranks.length > 0 ? (
                <Section title="Assigned Rank Codes" icon={ShieldCheck} scale={scale} columns={1}>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: `${Math.round(8 * scale)}px`, marginTop: `${Math.round(4 * scale)}px` }}>
                        {ranks.map((r, i) => {
                            const code = r.assigned_code || r.rank_code || r.code || "";
                            const name = r.rank_name || r.name || "";
                            const rankCode = r.rank?.code || r.rank_code || "";
                            return (
                                <div
                                    key={i}
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: `${Math.round(8 * scale)}px`,
                                        padding: `${Math.round(6 * scale)}px ${Math.round(12 * scale)}px`,
                                        background: "#F8F7FF",
                                        border: "1px solid #E9E6FF",
                                        borderRadius: `${Math.round(8 * scale)}px`,
                                    }}
                                >
                                    <Anchor size={Math.round(13 * scale)} color="#6366F1" />
                                    <div>
                                        {name && (
                                            <div style={{ fontSize: `${Math.round(13 * scale)}px`, fontWeight: 600, color: "#1F2937" }}>
                                                {name}
                                            </div>
                                        )}
                                        <div style={{ display: "flex", gap: `${Math.round(6 * scale)}px`, flexWrap: "wrap" }}>
                                            {rankCode && (
                                                <span style={{
                                                    fontSize: `${Math.round(11 * scale)}px`,
                                                    fontFamily: "monospace",
                                                    color: "#6B7280",
                                                    background: "#F3F4F6",
                                                    padding: "1px 5px",
                                                    borderRadius: "4px",
                                                }}>
                                                    {rankCode}
                                                </span>
                                            )}
                                            {code && (
                                                <span style={{
                                                    fontSize: `${Math.round(11 * scale)}px`,
                                                    fontFamily: "monospace",
                                                    color: "#4F46E5",
                                                    background: "#EEF2FF",
                                                    padding: "1px 5px",
                                                    borderRadius: "4px",
                                                    fontWeight: 700,
                                                }}>
                                                    {code}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </Section>
            ) : (
                <Section title="Assigned Rank Codes" icon={ShieldCheck} scale={scale} columns={1}>
                    <p style={{ fontSize: `${Math.round(13 * scale)}px`, color: "#9CA3AF", margin: 0 }}>
                        No rank codes assigned to this submission yet.
                    </p>
                </Section>
            )}
        </ViewDetailModal>
    );
}

export default CVSubmissionViewModal;
