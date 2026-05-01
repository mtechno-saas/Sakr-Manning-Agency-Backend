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
    FileText, User, Building, Ship, Calendar, Briefcase, Award,
    DollarSign, Clock, MapPin, Anchor, ShieldCheck, Download, ExternalLink
} from "lucide-react";
import Button from "../../Common/Button";
import documentsApi from "../../../../../services/Dashboard/documentsApi";
import { downloadsApi } from "../../../../../services/Dashboard/downloadsApi.js";
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
    const [isDownloadingDoc, setIsDownloadingDoc] = useState(null);

    const handleDocDownload = async (type, filename) => {
        try {
            setIsDownloadingDoc(type);
            const response = await downloadsApi.downloadDocument(contract.user, type);
            downloadsApi.triggerDownload(response, filename);
        } catch (error) {
            console.error(`Failed to download ${type}:`, error);
            alert(`Failed to download file. It might not be uploaded yet or you don't have permission.`);
        } finally {
            setIsDownloadingDoc(null);
        }
    };

    const handleLicenseDownload = async (licenseId, filename) => {
        try {
            setIsDownloadingDoc(`lic_${licenseId}`);
            const response = await downloadsApi.downloadLicense(contract.user, licenseId);
            downloadsApi.triggerDownload(response, filename);
        } catch (error) {
            console.error(`Failed to download license ${licenseId}:`, error);
            alert(`Failed to download license file.`);
        } finally {
            setIsDownloadingDoc(null);
        }
    };

    const renderDownloadLink = (type, hasFile, defaultFilename) => {
        if (!hasFile) return "No Attachments";
        const isCurrent = isDownloadingDoc === type;
        return (
            <span
                onClick={() => handleDocDownload(type, defaultFilename)}
                style={{
                    color: "#3B82F6",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "4px",
                    cursor: isCurrent ? "wait" : "pointer",
                    textDecoration: "none",
                    fontWeight: 500,
                    opacity: isCurrent ? 0.7 : 1,
                }}
            >
                {isCurrent ? "Downloading..." : "View / Download"} <ExternalLink size={14} />
            </span>
        );
    };

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
            <AvatarHeader 
                name={userName}
                subtitle={`${rankName} at ${companyName}`}
                status={contract.status}
                scale={scale}
            />

            {/* Contract Information */}
            <Section title="Contract Information" icon={FileText} scale={scale} columns={2}>
                <FieldItem label="Contract ID" value={contract.id} scale={scale} />
                <FieldItem label="Status" value={contract.status} scale={scale} />
                <FieldItem 
                    label="Expiry Progress" 
                    value={getDaysLabel()} 
                    scale={scale} 
                />
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
                    <FieldItem label="Vacancy ID" value={`#${contract.job_position_details.id}`} scale={scale} />
                    <FieldItem label="Expected Duration" value={`${contract.job_position_details.contract_duration_months} months`} scale={scale} />
                    <FieldItem 
                        label="Salary Budget" 
                        value={`${Number(contract.job_position_details.salary_min).toLocaleString()} - ${Number(contract.job_position_details.salary_max).toLocaleString()} ${contract.job_position_details.currency}`} 
                        scale={scale} 
                    />
                    <FieldItem label="Position Remarks" value={contract.job_position_details.remarks || "—"} scale={scale} />
                </Section>
            )}

            {/* User Documents Breakdown */}
            {contract.user_documents && (
                <>
                    {/* Passport Section */}
                    <Section title="Passport Details" icon={User} scale={scale} columns={2}>
                        <FieldItem label="Passport No." value={contract.user_documents.passport?.passport_no} scale={scale} />
                        <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "flex-end" }}>
                            {contract.user_documents.passport?.file_url && (
                                <Button 
                                    variant="outline" 
                                    size="sm" 
                                    onClick={() => handleDocDownload('passport', `passport_${contract.user_name}`)}
                                    disabled={isDownloadingDoc === 'passport'}
                                    scale={scale}
                                    title="Download Passport"
                                >
                                    <Download size={14} />
                                </Button>
                            )}
                        </div>
                        <FieldItem label="Issue Date" value={contract.user_documents.passport?.issue_date} format="date" scale={scale} />
                        <FieldItem label="Expiry Date" value={contract.user_documents.passport?.expiry_date} format="date" scale={scale} />
                        <FieldItem label="Issued By" value={contract.user_documents.passport?.issued_by} scale={scale} />
                        <FieldItem label="Place of Issue" value={contract.user_documents.passport?.place_of_issue} scale={scale} />
                    </Section>

                    {/* Seaman Book Section */}
                    <Section title="Seaman Book Details" icon={Anchor} scale={scale} columns={2}>
                        <FieldItem label="Primary SB No." value={contract.user_documents.seaman_book?.seaman_book_no} scale={scale} />
                        <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "flex-end" }}>
                            {contract.user_documents.seaman_book?.file_url && (
                                <Button 
                                    variant="outline" 
                                    size="sm" 
                                    onClick={() => handleDocDownload('seaman_book', `seaman_book_${contract.user_name}`)}
                                    disabled={isDownloadingDoc === 'seaman_book'}
                                    scale={scale}
                                    title="Download Seaman Book"
                                >
                                    <Download size={14} />
                                </Button>
                            )}
                        </div>
                        <FieldItem label="Issue Date" value={contract.user_documents.seaman_book?.issue_date} format="date" scale={scale} />
                        <FieldItem label="Expiry Date" value={contract.user_documents.seaman_book?.expiry_date} format="date" scale={scale} />
                        <FieldItem label="Issued By" value={contract.user_documents.seaman_book?.issued_by} scale={scale} />
                        <FieldItem label="Place of Issue" value={contract.user_documents.seaman_book?.place_of_issue} scale={scale} />
                        
                        <div style={{ gridColumn: "span 2", height: "1px", background: "#E5E7EB", margin: "8px 0" }} />
                        
                        <FieldItem label="Other SB No." value={contract.user_documents.other_seaman_book?.seaman_book_no} scale={scale} />
                        <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "flex-end" }}>
                            {contract.user_documents.other_seaman_book?.file_url && (
                                <Button 
                                    variant="outline" 
                                    size="sm" 
                                    onClick={() => handleDocDownload('other_seaman_book', `other_sb_${contract.user_name}`)}
                                    disabled={isDownloadingDoc === 'other_seaman_book'}
                                    scale={scale}
                                    title="Download Other SB"
                                >
                                    <Download size={14} />
                                </Button>
                            )}
                        </div>
                        <FieldItem label="Issue Date" value={contract.user_documents.other_seaman_book?.issue_date} format="date" scale={scale} />
                        <FieldItem label="Expiry Date" value={contract.user_documents.other_seaman_book?.expiry_date} format="date" scale={scale} />
                    </Section>

                    {/* COC Section */}
                    <Section title="Certificate of Competency (COC)" icon={Award} scale={scale} columns={2}>
                        <FieldItem label="Certificate Name" value={contract.user_documents.coc?.certificate_name} scale={scale} />
                        <FieldItem label="Certificate Number" value={contract.user_documents.coc?.certificate_number} scale={scale} />
                        <div style={{ gridColumn: "span 2", display: "flex", justifyContent: "flex-end" }}>
                            {contract.user_documents.coc?.file_url && (
                                <Button 
                                    variant="outline" 
                                    size="sm" 
                                    onClick={() => handleDocDownload('coc', `coc_${contract.user_name}`)}
                                    disabled={isDownloadingDoc === 'coc'}
                                    scale={scale}
                                    title="Download COC"
                                >
                                    <Download size={14} />
                                </Button>
                            )}
                        </div>
                        <FieldItem label="Issue Date" value={contract.user_documents.coc?.issue_date} format="date" scale={scale} />
                        <FieldItem label="Expiry Date" value={contract.user_documents.coc?.expiry_date} format="date" scale={scale} />
                        <FieldItem label="Issued By" value={contract.user_documents.coc?.issued_by} scale={scale} />
                        <FieldItem label="Issued At" value={contract.user_documents.coc?.issued_at} scale={scale} />
                    </Section>

                    {/* GOC Section */}
                    <Section title="General Operator Certificate (GOC)" icon={ShieldCheck} scale={scale} columns={2}>
                        <FieldItem label="Certificate Number" value={contract.user_documents.goc?.certificate_number} scale={scale} />
                        <div style={{ gridColumn: "span 2", display: "flex", justifyContent: "flex-end" }}>
                            {contract.user_documents.goc?.file_url && (
                                <Button 
                                    variant="outline" 
                                    size="sm" 
                                    onClick={() => handleDocDownload('goc', `goc_${contract.user_name}`)}
                                    disabled={isDownloadingDoc === 'goc'}
                                    scale={scale}
                                    title="Download GOC"
                                >
                                    <Download size={14} />
                                </Button>
                            )}
                        </div>
                        <FieldItem label="Issue Date" value={contract.user_documents.goc?.issue_date} format="date" scale={scale} />
                        <FieldItem label="Expiry Date" value={contract.user_documents.goc?.expiry_date} format="date" scale={scale} />
                        <FieldItem label="Issued By" value={contract.user_documents.goc?.issued_by} scale={scale} />
                        <FieldItem label="Issued At" value={contract.user_documents.goc?.issued_at} scale={scale} />
                    </Section>

                    {/* Medical Section */}
                    <Section title="Medical & Health Certificates" icon={ShieldCheck} scale={scale} columns={2}>
                        <FieldItem label="Health Cert No." value={contract.user_documents.health_certificate?.number} scale={scale} />
                        <div style={{ gridColumn: "span 2", display: "flex", justifyContent: "flex-end" }}>
                            {contract.user_documents.health_certificate?.file_url && (
                                <Button 
                                    variant="outline" 
                                    size="sm" 
                                    onClick={() => handleDocDownload('health_certificate', `medical_${contract.user_name}`)}
                                    disabled={isDownloadingDoc === 'health_certificate'}
                                    scale={scale}
                                    title="Download Medical"
                                >
                                    <Download size={14} />
                                </Button>
                            )}
                        </div>
                        <FieldItem label="Issue Date" value={contract.user_documents.health_certificate?.issue_date} format="date" scale={scale} />
                        <FieldItem label="Expiry Date" value={contract.user_documents.health_certificate?.expiry_date} format="date" scale={scale} />
                        <FieldItem label="Flag State" value={contract.user_documents.health_certificate?.flag_state} scale={scale} />
                        <FieldItem label="Issued By" value={contract.user_documents.health_certificate?.issued_by} scale={scale} />
                        <div style={{ gridColumn: "span 2", height: "1px", background: "#E5E7EB", margin: "8px 0" }} />
                        <FieldItem label="Intl Medical No." value={contract.user_documents.health_certificate?.international_medical_number} scale={scale} />
                        <FieldItem label="Intl Issue Date" value={contract.user_documents.health_certificate?.international_medical_issue_date} format="date" scale={scale} />
                        <FieldItem label="Intl Expiry Date" value={contract.user_documents.health_certificate?.international_medical_expiry_date} format="date" scale={scale} />
                    </Section>

                    {/* Licenses Section */}
                    {contract.user_documents.licenses?.length > 0 && (
                        <Section title="Professional Licenses" icon={Briefcase} scale={scale} columns={1}>
                            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                                {contract.user_documents.licenses.map((lic, idx) => {
                                    const isCurrentLic = isDownloadingDoc === `lic_${lic.id}`;
                                    return (
                                        <div key={idx} style={{ padding: "16px", background: "#F9FAFB", borderRadius: "10px", border: "1px solid #E5E7EB" }}>
                                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                                                <div>
                                                    <div style={{ fontWeight: 700, fontSize: "15px", color: "#111827" }}>{lic.document_name}</div>
                                                    <div style={{ fontSize: "13px", color: "#6B7280" }}>No: {lic.document_number} • {lic.country_of_issue}</div>
                                                </div>
                                                {lic.file_url && (
                                                    <Button 
                                                        variant="outline" 
                                                        size="sm" 
                                                        onClick={() => handleLicenseDownload(lic.id, `${lic.document_name}_${contract.user_name}`)}
                                                        disabled={isCurrentLic}
                                                        scale={scale}
                                                        title="Download License"
                                                    >
                                                        <Download size={14} />
                                                    </Button>
                                                )}
                                            </div>
                                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                                                <FieldItem label="Issue Date" value={lic.issue_date} format="date" scale={scale} />
                                                <FieldItem label="Expiration Date" value={lic.expiration_date} format="date" scale={scale} />
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </Section>
                    )}
                </>
            )}

            {/* Signed File (If available) */}
            {contract.signed_file && (
                <Section title="Signed Documents" icon={FileText} scale={scale} columns={1}>
                    <div style={{ padding: "12px", background: "#F0FDF4", border: "1px solid #BBF7D0", borderRadius: "8px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                            <FileText size={20} color="#15803D" />
                            <div>
                                <div style={{ fontWeight: 600, color: "#166534", fontSize: "14px" }}>Signed Contract Available</div>
                                <div style={{ fontSize: "12px", color: "#15803D" }}>Signed on: {new Date(contract.signed_at).toLocaleDateString()}</div>
                            </div>
                        </div>
                        <a 
                            href={contract.signed_file} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            style={{ background: "#166534", color: "white", padding: "6px 14px", borderRadius: "6px", fontSize: "13px", fontWeight: 600, textDecoration: "none", display: "flex", alignItems: "center", gap: "6px" }}
                        >
                            View Signed Contract <ExternalLink size={14} />
                        </a>
                    </div>
                </Section>
            )}

            {/* Metadata */}
            <Section title="Record Information" icon={Clock} scale={scale} columns={2}>
                <FieldItem label="Generated ID" value={contract.generated_id || "—"} scale={scale} />
                <FieldItem label="Contract Created" value={contract.created_at} format="datetime" scale={scale} />
                <FieldItem label="Last Updated" value={contract.updated_at} format="datetime" scale={scale} />
            </Section>
        </ViewDetailModal>
    );
}

export default ContractViewModal;
