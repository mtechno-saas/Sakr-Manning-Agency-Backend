// components/dashboard/Components/Modal/ViewModal/CVViewModal.jsx
/**
 * CVViewModal - CV Document Detail View Modal
 *
 * Displays comprehensive CV / applicant information including:
 * - Applicant header (name, position, status)
 * - Contact details (email, phone)
 * - Application details (generated ID, upload date)
 * - Attached file with download + open actions
 */

import React from "react";
import {
    User, Phone, Mail, Calendar, Briefcase,
    FileText, Hash, Download, ExternalLink,
} from "lucide-react";
import {
    ViewDetailModal,
    Section,
    FieldItem,
    StatusBadge,
} from "./ViewDetailModal";

export function CVViewModal({
    isOpen,
    onClose,
    cv,
    onDelete,
    onDownload,
    scale = 1,
    canDelete = true,
}) {
    if (!cv) return null;

    // Normalise — `cv` may be the _raw doc or the table row
    const doc = cv._raw || cv;

    const applicantName = doc.name || "Unknown Applicant";
    const position = doc.position || "—";
    const status = doc.status || "Pending";

    // ── Actions ────────────────────────────────────────────────────────────────
    const actions = [];
    if (canDelete && onDelete) {
        actions.push({
            label: "Delete",
            onClick: () => onDelete(doc.id),
            variant: "danger",
        });
    }
    actions.push({
        label: "Close",
        onClick: onClose,
        variant: "primary",
    });

    // File helpers
    const fileName = doc.file
        ? decodeURIComponent(doc.file.split("/").pop().split("_").pop())
        : null;

    return (
        <ViewDetailModal
            isOpen={isOpen}
            onClose={onClose}
            title="CV Details"
            subtitle={`Record ID: ${doc.id}`}
            actions={actions}
            scale={scale}
            size="lg"
        >
            {/* ── Header ──────────────────────────────────────────────────────── */}
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: `${Math.round(16 * scale)}px`,
                    backgroundColor: "#F9FAFB",
                    borderRadius: `${Math.round(12 * scale)}px`,
                    marginBottom: `${Math.round(24 * scale)}px`,
                }}
            >
                <div style={{ display: "flex", alignItems: "center", gap: `${Math.round(16 * scale)}px` }}>
                    {/* Avatar circle */}
                    <div
                        style={{
                            width: `${Math.round(56 * scale)}px`,
                            height: `${Math.round(56 * scale)}px`,
                            borderRadius: "50%",
                            background: "linear-gradient(135deg, #6366F1, #8B5CF6)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            color: "white",
                            fontSize: `${Math.round(22 * scale)}px`,
                            fontWeight: 700,
                            flexShrink: 0,
                        }}
                    >
                        {applicantName.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <h3
                            style={{
                                fontSize: `${Math.round(18 * scale)}px`,
                                fontWeight: 600,
                                color: "#111827",
                                margin: 0,
                            }}
                        >
                            {applicantName}
                        </h3>
                        <p
                            style={{
                                fontSize: `${Math.round(14 * scale)}px`,
                                color: "#6B7280",
                                margin: `${Math.round(4 * scale)}px 0 0 0`,
                            }}
                        >
                            {position}
                        </p>
                    </div>
                </div>
                <StatusBadge status={status} scale={scale} />
            </div>

            {/* ── Contact Information ─────────────────────────────────────────── */}
            <Section title="Contact Information" icon={User} scale={scale} columns={2}>
                <FieldItem label="Full Name" value={doc.name} icon={User} scale={scale} />
                <FieldItem label="Email" value={doc.email} iconType="email" scale={scale} />
                <FieldItem label="Phone" value={doc.phone_number} iconType="phone" scale={scale} />
                <FieldItem label="Position / Rank" value={doc.position} icon={Briefcase} scale={scale} />
            </Section>

            {/* ── Application Details ─────────────────────────────────────────── */}
            <Section title="Application Details" icon={FileText} scale={scale} columns={2}>
                <FieldItem label="Generated ID" value={doc.generated_id || "Pending"} icon={Hash} scale={scale} />
                <FieldItem label="Status" value={doc.status} scale={scale} />
                <FieldItem label="Submitted Date" value={doc.created_at} format="datetime" icon={Calendar} scale={scale} />
                <FieldItem label="Last Updated" value={doc.updated_at} format="datetime" icon={Calendar} scale={scale} />
            </Section>

            {/* ── Vacancy Details ─────────────────────────────────────────────── */}
            {(doc.job_position || doc.job_position_details) && (
                <Section title="Specific Vacancy Details" icon={Briefcase} scale={scale} columns={2}>
                    <FieldItem
                        label="Applied Position"
                        value={doc.job_position_name || "—"}
                        icon={Briefcase}
                        scale={scale}
                    />
                    <FieldItem
                        label="Target Company"
                        value={doc.company_name}
                        scale={scale}
                    />
                    {doc.job_position_details && (
                        <>
                            <FieldItem
                                label="Monthly Salary"
                                value={doc.job_position_details.salary_min && doc.job_position_details.salary_max ?
                                    `${Number(doc.job_position_details.salary_min).toLocaleString()} - ${Number(doc.job_position_details.salary_max).toLocaleString()} ${doc.job_position_details.currency || 'USD'}` :
                                    doc.job_position_details.salary_min || '—'}
                                scale={scale}
                            />
                            <FieldItem
                                label="Contract Duration"
                                value={doc.job_position_details.contract_duration_months ? `${doc.job_position_details.contract_duration_months} Months` : '—'}
                                scale={scale}
                            />
                            {doc.job_position_details.remarks && (
                                <FieldItem
                                    label="Vacancy Remarks"
                                    value={doc.job_position_details.remarks}
                                    scale={scale}
                                />
                            )}
                        </>
                    )}
                </Section>
            )}

            {/* ── Attached CV File ─────────────────────────────────────────────── */}
            <Section title="Attached File" icon={FileText} scale={scale} columns={1}>
                {doc.file ? (
                    <div
                        style={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                            padding: `${Math.round(14 * scale)}px ${Math.round(18 * scale)}px`,
                            background: "linear-gradient(135deg, #F0F4FF 0%, #EEF2FF 100%)",
                            borderRadius: `${Math.round(10 * scale)}px`,
                            border: "1px solid #E0E7FF",
                        }}
                    >
                        <div style={{ display: "flex", alignItems: "center", gap: `${Math.round(12 * scale)}px` }}>
                            {/* File icon */}
                            <div
                                style={{
                                    width: `${Math.round(42 * scale)}px`,
                                    height: `${Math.round(42 * scale)}px`,
                                    borderRadius: `${Math.round(10 * scale)}px`,
                                    backgroundColor: "#6366F1",
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    flexShrink: 0,
                                }}
                            >
                                <FileText size={Math.round(20 * scale)} color="#fff" />
                            </div>
                            <div>
                                <p style={{
                                    margin: 0,
                                    fontSize: `${Math.round(14 * scale)}px`,
                                    fontWeight: 600,
                                    color: "#1F2937",
                                    wordBreak: "break-all",
                                }}>
                                    {fileName}
                                </p>
                                <p style={{
                                    margin: `${Math.round(2 * scale)}px 0 0`,
                                    fontSize: `${Math.round(12 * scale)}px`,
                                    color: "#6B7280",
                                }}>
                                    CV Document
                                </p>
                            </div>
                        </div>

                        {/* Action buttons */}
                        <div style={{ display: "flex", gap: `${Math.round(8 * scale)}px` }}>
                            {/* Open in new tab */}
                            {/* <a
                                href={doc.file}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{
                                    display: "inline-flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    width: `${Math.round(36 * scale)}px`,
                                    height: `${Math.round(36 * scale)}px`,
                                    borderRadius: `${Math.round(8 * scale)}px`,
                                    backgroundColor: "#fff",
                                    border: "1px solid #D1D5DB",
                                    cursor: "pointer",
                                    color: "#4F46E5",
                                    textDecoration: "none",
                                    transition: "all 0.15s",
                                }}
                                title="Open in new tab"
                            >
                                <ExternalLink size={Math.round(16 * scale)} />
                            </a> */}

                            {/* Download */}
                            {onDownload && (
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        onDownload(cv);
                                    }}
                                    style={{
                                        display: "inline-flex",
                                        alignItems: "center",
                                        justifyContent: "center",
                                        width: `${Math.round(36 * scale)}px`,
                                        height: `${Math.round(36 * scale)}px`,
                                        borderRadius: `${Math.round(8 * scale)}px`,
                                        backgroundColor: "#4F46E5",
                                        border: "none",
                                        cursor: "pointer",
                                        color: "#fff",
                                        transition: "all 0.15s",
                                    }}
                                    title="Download file"
                                >
                                    <Download size={Math.round(16 * scale)} />
                                </button>
                            )}
                        </div>
                    </div>
                ) : (
                    <div
                        style={{
                            padding: `${Math.round(24 * scale)}px`,
                            textAlign: "center",
                            color: "#9CA3AF",
                            backgroundColor: "#F9FAFB",
                            borderRadius: `${Math.round(10 * scale)}px`,
                            border: "1px dashed #D1D5DB",
                            fontSize: `${Math.round(14 * scale)}px`,
                        }}
                    >
                        No file attached to this CV.
                    </div>
                )}
            </Section>
        </ViewDetailModal>
    );
}

export default CVViewModal;
