// components/dashboard/Components/Modal/ViewModal/ContractViewModal.jsx
/**
 * ContractViewModal - Contract/Document Detail View Modal
 * 
 * Displays comprehensive contract information including:
 * - Contract details
 * - User information
 * - Company information
 * - Ship information
 * - Financial details
 */

import React, { useState } from "react";
import {
    FileText, User, Building, Ship, Calendar,
    DollarSign, Clock, MapPin, Anchor, ShieldCheck
} from "lucide-react";
import documentsApi from "../../../../../services/Dashboard/documentsApi";
import {
    ViewDetailModal,
    Section,
    FieldItem,
    AvatarHeader,
    StatusBadge,
} from "./ViewDetailModal";

export function ContractViewModal({
    isOpen,
    onClose,
    contract,
    onDelete,
    scale = 1,
    canDelete = true,
}) {
    if (!contract) return null;

    // Get display names
    const userName = contract.user_name ||
        (contract.user?.first_name ? `${contract.user.first_name} ${contract.user.middle_name || ''}`.trim() : `User #${contract.user}`);
    const companyName = contract.company_name || contract.company?.name || `Company #${contract.company}`;
    const shipName = contract.ship_name || contract.ship?.ship_name || (contract.ship ? `Ship #${contract.ship}` : "Not Assigned");
    const rankName = contract.rank_name || contract.rank?.name || (contract.rank ? `Rank #${contract.rank}` : "Not Specified");

    // Calculate days remaining/expired
    const getDaysLabel = () => {
        const days = contract.daysToExpiry;
        if (days === null || days === undefined) return "—";
        if (days < 0) return `Expired ${Math.abs(days)} days ago`;
        if (days === 0) return "Expires today";
        return `${days} days remaining`;
    };

    const [isDownloading, setIsDownloading] = useState(false);

    const actions = [];

    // Always show Download Contract button as it's generated via backend
    actions.push({
        label: isDownloading ? "Downloading..." : "Download Contract",
        onClick: async () => {
            try {
                setIsDownloading(true);
                await documentsApi.downloadContract(contract.id);
            } catch (err) {
                console.error("Failed to download contract:", err);
                alert("Failed to download contract. It may not be available yet.");
            } finally {
                setIsDownloading(false);
            }
        },
        variant: "primary",
    });

    if (canDelete && onDelete) {
        actions.push({
            label: "Delete",
            onClick: () => onDelete(contract.id),
            variant: "danger",
        });
    }
    actions.push({
        label: "Close",
        onClick: onClose,
        variant: "outline",
    });

    return (
        <ViewDetailModal
            isOpen={isOpen}
            onClose={onClose}
            title="Contract Details"
            subtitle={`Contract ID: ${contract.id}`}
            actions={actions}
            scale={scale}
            size="lg"
        >
            {/* Header with Status */}
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
                <div>
                    <h3
                        style={{
                            fontSize: `${Math.round(18 * scale)}px`,
                            fontWeight: 600,
                            color: "#111827",
                            margin: 0,
                        }}
                    >
                        {userName}
                    </h3>
                    <p
                        style={{
                            fontSize: `${Math.round(14 * scale)}px`,
                            color: "#6B7280",
                            margin: `${Math.round(4 * scale)}px 0 0 0`,
                        }}
                    >
                        {rankName} at {companyName}
                    </p>
                </div>
                <div style={{ textAlign: "right" }}>
                    <StatusBadge status={contract.status} scale={scale} />
                    <p
                        style={{
                            fontSize: `${Math.round(12 * scale)}px`,
                            color: contract.daysToExpiry < 0 ? "#DC2626" :
                                contract.daysToExpiry <= 30 ? "#F59E0B" : "#6B7280",
                            marginTop: `${Math.round(8 * scale)}px`,
                            fontWeight: 500,
                        }}
                    >
                        {getDaysLabel()}
                    </p>
                </div>
            </div>

            {/* Contract Information */}
            <Section title="Contract Information" icon={FileText} scale={scale} columns={2}>
                <FieldItem label="Contract ID" value={contract.id} scale={scale} />
                <FieldItem label="Status" value={contract.status} scale={scale} />
                <FieldItem label="Sign On Date" value={contract.sign_on_date} format="date" iconType="date" scale={scale} />
                <FieldItem label="Sign Off Date" value={contract.sign_off_date} format="date" iconType="date" scale={scale} />
                <FieldItem label="Duration" value={contract.duration ? `${contract.duration} months` : null} icon={Clock} scale={scale} />
                <FieldItem label="Expiry Status" value={contract.expiryCategory} scale={scale} />
                {contract.repatriation_terms && (
                    <FieldItem label="Repatriation Terms" value={contract.repatriation_terms} scale={scale} />
                )}
                {contract.leave_pay_terms && (
                    <FieldItem label="Leave Pay Terms" value={contract.leave_pay_terms} scale={scale} />
                )}
            </Section>

            {/* Employee Information */}
            <Section title="Employee Information" icon={User} scale={scale} columns={2}>
                <FieldItem label="Employee Name" value={userName} scale={scale} />
                <FieldItem label="Rank" value={rankName} icon={Anchor} scale={scale} />
                <FieldItem label="Assigned Rank Code" value={contract.assigned_code || "—"} scale={scale} />
                <FieldItem label="Email" value={contract.user_email || contract.user?.email} iconType="email" scale={scale} />
            </Section>

            {/* Assigned Ranks & Certificates */}
            {(contract.coded_rank?.length > 0 || contract.certificates?.length > 0) && (
                <Section title="Qualifications & Rank Details" icon={ShieldCheck} scale={scale} columns={1}>
                    {contract.coded_rank?.length > 0 && (
                        <div style={{ marginBottom: `${Math.round(12 * scale)}px` }}>
                            <span style={{ fontSize: `${Math.round(13 * scale)}px`, color: "#6B7280", display: "block", marginBottom: "4px" }}>Coded Ranks</span>
                            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                                {contract.coded_rank.map((cr, idx) => (
                                    <span key={idx} style={{ padding: "4px 8px", background: "#EEF2FF", color: "#4F46E5", borderRadius: "6px", fontSize: "12px", fontFamily: "monospace", fontWeight: 500 }}>
                                        {cr.assigned_code || cr.rank_code} - {cr.rank_name}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {contract.certificates?.length > 0 && (
                        <div>
                            <span style={{ fontSize: `${Math.round(13 * scale)}px`, color: "#6B7280", display: "block", marginBottom: "4px" }}>Certificates</span>
                            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                                {contract.certificates.map((cert, idx) => (
                                    <span key={idx} style={{ padding: "4px 8px", background: "#F3F4F6", color: "#374151", borderRadius: "6px", fontSize: "12px", fontWeight: 500 }}>
                                        {cert.code ? `${cert.code} : ` : ""}{cert.name}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </Section>
            )}

            {/* Company & Ship Information */}
            <Section title="Company & Ship Details" icon={Building} scale={scale} columns={2}>
                <FieldItem label="Company Name" value={companyName} scale={scale} />
                <FieldItem label="Ship Name" value={shipName} scale={scale} />
            </Section>

            {/* Financial Information */}
            <Section title="Financial Information" icon={DollarSign} scale={scale} columns={2}>
                <FieldItem label="Salary" value={contract.salary} format="currency" scale={scale} />
                <FieldItem label="Currency" value={contract.currency || "USD"} scale={scale} />
            </Section>

            {/* Job Position Requirements */}
            {contract.job_position_details && (
                <Section title="Job Position Requirements" icon={FileText} scale={scale} columns={2}>
                    <FieldItem label="Expected Duration" value={`${contract.job_position_details.contract_duration_months} months`} scale={scale} />
                    <FieldItem label="Position Remarks" value={contract.job_position_details.remarks || "—"} scale={scale} />
                </Section>
            )}

            {/* User Documents */}
            {contract.user_documents && (
                <Section title="Verified Documents" icon={FileText} scale={scale} columns={2}>
                    {contract.user_documents.passport?.passport_no && (
                        <FieldItem label="Passport No." value={contract.user_documents.passport.passport_no} scale={scale} />
                    )}
                    {contract.user_documents.seaman_book?.seaman_book_no && (
                        <FieldItem label="Seaman Book No." value={contract.user_documents.seaman_book.seaman_book_no} scale={scale} />
                    )}
                    {contract.user_documents.coc?.certificate_number && (
                        <FieldItem label="COC" value={contract.user_documents.coc.certificate_name} scale={scale} />
                    )}
                    {contract.user_documents.health_certificate?.number && (
                        <FieldItem label="Health Cert No." value={contract.user_documents.health_certificate.number} scale={scale} />
                    )}
                </Section>
            )}

            {/* Metadata */}
            <Section title="Record Information" icon={Clock} scale={scale} columns={2}>
                <FieldItem label="Generated ID" value={contract.generated_id || "—"} scale={scale} />
                <FieldItem label="Created At" value={contract.created_at} format="datetime" scale={scale} />
            </Section>
        </ViewDetailModal>
    );
}

export default ContractViewModal;
