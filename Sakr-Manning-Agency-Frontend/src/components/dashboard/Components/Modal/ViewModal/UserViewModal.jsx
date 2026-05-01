// components/dashboard/Components/Modal/ViewModal/UserViewModal.jsx
/**
 * UserViewModal - Detailed User/CV View Modal
 * 
 * Displays comprehensive user information in organized sections:
 * - Personal Information
 * - Contact Information
 * - Professional Details
 * - Certificates
 * - Ranks
 * - Employment History
 */

import React, { useState } from "react";
import {
    User, Phone, Mail, MapPin, Calendar, Briefcase,
    Award, Shield, Anchor, FileText, Globe, Hash,
    Building, CreditCard, Heart, Droplets, Activity,
    ShieldAlert, Languages, History, ClipboardCheck,
    Stethoscope, Syringe, GraduationCap, CheckCircle2,
    Clock, ExternalLink, Download, ShieldCheck
} from "lucide-react";
import {
    ViewDetailModal,
    Section,
    FieldItem,
    ListSection,
    Tag,
    AvatarHeader,
    StatusBadge,
} from "./ViewDetailModal";
import { downloadsApi } from "../../../../../services/Dashboard/downloadsApi.js";

// Map backend user status to display status
const mapUserStatus = (status) => {
    // Priority: the status string passed should be one of our pipeline states
    // If it's a legacy uppercase status, map it to a readable string
    const statusMap = {
        PENDING: "Pending",
        UNDER_REVIEW: "Under Review",
        INTERVIEWED: "Interviewed",
        SHORTLISTED: "Shortlisted",
        APPROVED: "Approved",
        HIRED: "Hired",
        REJECTED: "Rejected",

        // Keep a few general ones just in case
        ACTIVE: "Active",
        INACTIVE: "Inactive",
        BLACKLIST: "Blacklist",
    };

    if (!status) return "Pending";
    return statusMap[status.toUpperCase()] || status;
};

// Certificate chip renderer
const renderCertificate = (cert, scale) => (
    <Tag color="#10B981" scale={scale}>
        <Award size={Math.round(12 * scale)} style={{ marginRight: 4 }} />
        {cert.name || cert.certificate_name || cert.code || cert}
    </Tag>
);

// Sea Service row renderer
const renderSeaService = (service, scale) => (
    <div style={{
        padding: `${Math.round(10 * scale)}px`,
        backgroundColor: "rgba(0,0,0,0.02)",
        borderRadius: "8px",
        marginBottom: `${Math.round(8 * scale)}px`
    }}>
        <div style={{ fontWeight: 600, fontSize: `${Math.round(14 * scale)}px` }}>{service.vessel_name} ({service.vessel_type})</div>
        <div style={{ fontSize: `${Math.round(12 * scale)}px`, color: "#666" }}>
            {service.rank_name || (typeof service.rank === 'object' ? service.rank?.name : service.rank)} • {service.signed_on} to {service.signed_off}
        </div>
        {(service.company_name || service.company) && <div style={{ fontSize: `${Math.round(12 * scale)}px`, color: "#666" }}>Company: {service.company_name || service.company}</div>}
    </div>
);

// Language proficiency renderer
const renderLanguage = (lang, scale) => {
    const fs = Math.round(13 * scale);
    const fsSmall = Math.round(12 * scale);
    const rowStyle = {
        display: "flex",
        justifyContent: "space-between",
        padding: `${Math.round(3 * scale)}px 0`,
        fontSize: `${fs}px`,
        color: "#444",
    };
    const labelStyle = { fontWeight: 500, color: "#666" };
    const valueStyle = { fontWeight: 600, color: "#1E1E1E" };

    return (
        <div style={{
            width: "400px",
            padding: `${Math.round(12 * scale)}px ${Math.round(14 * scale)}px`,
            backgroundColor: "rgba(0,0,0,0.02)",
            borderRadius: "8px",
            marginBottom: `${Math.round(10 * scale)}px`,
            borderLeft: "3px solid #F59E0B",
        }}>
            {/* Language Name Header */}
            <div style={{
                display: "flex",
                alignItems: "center",
                gap: `${Math.round(6 * scale)}px`,
                marginBottom: `${Math.round(8 * scale)}px`,
                paddingBottom: `${Math.round(6 * scale)}px`,
                borderBottom: "1px solid rgba(0,0,0,0.06)",
            }}>
                <Languages size={Math.round(16 * scale)} style={{ color: "#F59E0B", flexShrink: 0 }} />
                <span style={{ fontWeight: 700, fontSize: `${Math.round(15 * scale)}px`, color: "#1E1E1E" }}>
                    {lang.language}
                </span>
            </div>

            {/* Proficiency Rows */}
            {lang.speaking_level && (
                <div style={rowStyle}>
                    <span style={labelStyle}>Speaking</span>
                    <span style={valueStyle}>{lang.speaking_level}</span>
                </div>
            )}
            {lang.writing_level && (
                <div style={rowStyle}>
                    <span style={labelStyle}>Writing</span>
                    <span style={valueStyle}>{lang.writing_level}</span>
                </div>
            )}
            {lang.reading_level && (
                <div style={rowStyle}>
                    <span style={labelStyle}>Reading</span>
                    <span style={valueStyle}>{lang.reading_level}</span>
                </div>
            )}
            {lang.cefr_level && (
                <div style={rowStyle}>
                    <span style={labelStyle}>CEFR Level</span>
                    <span style={valueStyle}>{lang.cefr_level}</span>
                </div>
            )}
            {lang.cefr_description && (
                <div style={{
                    fontSize: `${fsSmall}px`,
                    color: "#888",
                    fontStyle: "italic",
                    padding: `${Math.round(4 * scale)}px 0`,
                }}>
                    {lang.cefr_description}
                </div>
            )}
            {lang.general_remarks && (
                <div style={rowStyle}>
                    <span style={labelStyle}>Remarks</span>
                    <span style={valueStyle}>{lang.general_remarks}</span>
                </div>
            )}
            {lang.attachment && (
                <div style={rowStyle}>
                    <span style={labelStyle}>Attachment</span>
                    <a href={lang.attachment} target="_blank" rel="noopener noreferrer"
                        style={{ color: "#3B82F6", textDecoration: "underline", fontWeight: 500 }}>
                        View File
                    </a>
                </div>
            )}
        </div>
    );
};

// Vaccination renderer
const renderVaccination = (vac, scale) => {
    const dateDisplay = vac.issue_date || vac.date || vac.expiry_date || "";
    return (
        <Tag color="#EF4444" scale={scale}>
            <Syringe size={Math.round(12 * scale)} style={{ marginRight: 4 }} />
            {vac.vaccination_name || vac.name}{dateDisplay ? ` (${dateDisplay})` : ""}
        </Tag>
    );
};

// Reference renderer
const renderReference = (ref, scale) => (
    <div style={{
        padding: `${Math.round(10 * scale)}px`,
        borderLeft: "3px solid #6366F1",
        backgroundColor: "rgba(0,0,0,0.02)",
        marginBottom: `${Math.round(8 * scale)}px`
    }}>
        <div style={{ fontWeight: 600 }}>{ref.company_name}</div>
        <div style={{ fontSize: `${Math.round(12 * scale)}px` }}>{ref.name || ref.contact_person} • {ref.position}</div>
        <div style={{ fontSize: `${Math.round(12 * scale)}px`, color: "#666" }}>{ref.email} | {ref.tel || ref.phone}</div>
    </div>
);

// Rank chip renderer
const renderRank = (rank, scale) => {
    const rankName = rank.rank?.name || rank.name || rank;
    const assignedCode = rank.assigned_code || "";
    return (
        <Tag color="#6366F1" scale={scale}>
            <Anchor size={Math.round(12 * scale)} style={{ marginRight: 4 }} />
            {rankName}
            {assignedCode && ` (${assignedCode})`}
        </Tag>
    );
};

export function UserViewModal({
    isOpen,
    onClose,
    user,
    onDelete,
    scale = 1,
    canDelete = true,
}) {
    const [isDownloading, setIsDownloading] = useState(null);

    const handleDownload = async (type, filename) => {
        try {
            setIsDownloading(type);
            const response = await downloadsApi.downloadDocument(user.id, type);
            downloadsApi.triggerDownload(response, filename);
        } catch (error) {
            console.error(`Failed to download ${type}:`, error);
            alert(`Failed to download file. It might not be uploaded yet or you don't have permission.`);
        } finally {
            setIsDownloading(null);
        }
    };

    const renderDownloadLink = (type, attachmentValue, defaultFilename) => {
        if (!attachmentValue) return "No Attachments";
        return (
            <span
                onClick={() => handleDownload(type, defaultFilename)}
                style={{
                    color: "#3B82F6",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "4px",
                    cursor: isDownloading === type ? "wait" : "pointer",
                    textDecoration: "none",
                    fontWeight: 500,
                    opacity: isDownloading === type ? 0.7 : 1,
                }}
            >
                {isDownloading === type ? "Downloading..." : "View / Download"} <ExternalLink size={14} />
            </span>
        );
    };


    if (!user) return null;

    // Build full name
    const fullName = [user.first_name, user.middle_name, user.last_name]
        .filter(Boolean)
        .join(" ") || "Unknown User";

    // Get primary rank for subtitle
    const primaryRank = user.ranks?.[0]?.rank?.name ||
        user.user_ranks?.[0]?.rank?.name ||
        user.position ||
        "No Rank Assigned";

    // Build actions array
    const actions = [];
    if (canDelete && onDelete) {
        actions.push({
            label: "Delete",
            onClick: () => onDelete(user.id),
            variant: "danger",
        });
    }
    actions.push({
        label: "Close",
        onClick: onClose,
        variant: "primary",
    });

    return (
        <ViewDetailModal
            isOpen={isOpen}
            onClose={onClose}
            title="User Details"
            subtitle={`ID: ${user.id}`}
            actions={actions}
            scale={scale}
            size="xl"
        >
            {/* Avatar Header */}
            <AvatarHeader
                image={user.profile_image}
                name={fullName}
                subtitle={primaryRank}
                status={mapUserStatus(user.user_status)}
                scale={scale}
            />

            {/* Personal Information */}
            <Section title="Personal Information" icon={User} scale={scale} columns={3}>
                <FieldItem label="First Name" value={user.first_name} scale={scale} />
                <FieldItem label="Middle Name" value={user.middle_name} scale={scale} />
                <FieldItem label="Last Name" value={user.last_name} scale={scale} />
                <FieldItem label="Date of Birth" value={user.date_of_birth} format="date" iconType="date" scale={scale} />
                <FieldItem label="Age" value={user.age} scale={scale} />
                <FieldItem label="Place of Birth" value={user.Place_Of_Birth || user.place_of_birth} iconType="location" scale={scale} />
                <FieldItem label="Nationality" value={user.nationality} icon={Globe} scale={scale} />
                <FieldItem label="Marital Status" value={user.marital_status} icon={Heart} scale={scale} />
                <FieldItem label="Blood Type" value={user.blood_type} icon={Droplets} scale={scale} />
                <FieldItem label="Smoker" value={user.smoker ? "Yes" : "No"} scale={scale} />
            </Section>

            {/* Physical Details */}
            <Section title="Physical Details" icon={Activity} scale={scale} columns={3}>
                <FieldItem label="Height (cm)" value={user.Height_Cm || user.height} scale={scale} />
                <FieldItem label="Weight (kg)" value={user.Weight_Kg || user.weight} scale={scale} />
                <FieldItem label="BMI" value={(() => {
                    const h = parseFloat(user.Height_Cm || user.height);
                    const w = parseFloat(user.Weight_Kg || user.weight);
                    if (!h || !w || h <= 0) return null;
                    const bmi = (w / ((h / 100) ** 2)).toFixed(1);
                    const category = bmi < 18.5 ? "Underweight" : bmi < 25 ? "Normal" : bmi < 30 ? "Overweight" : "Obese";
                    return `${bmi} (${category})`;
                })()} scale={scale} />
                <FieldItem label="Overall Size" value={user.overall_size} scale={scale} />
                <FieldItem label="Shirt Size" value={user.shirt_size} scale={scale} />
                <FieldItem label="Trouser Size" value={user.trouser_size} scale={scale} />
                <FieldItem label="Shoe Size" value={user.shoes_size || user.shoe_size} scale={scale} />
            </Section>

            {/* Contact Information */}
            <Section title="Contact Information" icon={Phone} scale={scale} columns={2}>
                <FieldItem label="Email" value={user.email} iconType="email" scale={scale} />
                <FieldItem label="Phone Number" value={user.phone_number} iconType="phone" scale={scale} />
                <FieldItem label="Tel Number" value={user.tel_number} iconType="phone" scale={scale} />
                <FieldItem label="Address" value={user.address} iconType="location" fullWidth scale={scale} />
                <FieldItem label="City" value={user.city} scale={scale} />
                <FieldItem label="Country" value={user.country} scale={scale} />
            </Section>

            {/* Document Information & Visas */}
            <Section title="Documents & Visas" icon={FileText} scale={scale} columns={3}>
                <FieldItem label="Passport Number" value={user.passport_no} icon={CreditCard} scale={scale} />
                <FieldItem label="Passport Issue Date" value={user.passport_issue_date} format="date" scale={scale} />
                <FieldItem label="Passport Expiry" value={user.passport_expiry_date} format="date" scale={scale} />
                <FieldItem label="Passport Issue Place" value={user.passport_place_of_issue || user.passport_issue_place} scale={scale} />
                <FieldItem label="Passport File" value={renderDownloadLink('passport', user.passport_attachment, `passport_${user.id}`)} format="custom" scale={scale} />
                <div />

                <FieldItem label="Seaman Book Number" value={user.seaman_book_no} scale={scale} />
                <FieldItem label="SB Issue Date" value={user.seaman_book_issue_date} format="date" scale={scale} />
                <FieldItem label="SB Expiry" value={user.seaman_book_expiry_date} format="date" scale={scale} />
                <FieldItem label="SB Issue Place" value={user.seaman_book_place_of_issue} scale={scale} />
                <FieldItem label="SB File" value={renderDownloadLink('seaman_book', user.seaman_book_attachment, `seaman_book_${user.id}`)} format="custom" scale={scale} />
                <FieldItem label="Other SB File" value={renderDownloadLink('other_seaman_book', user.other_seaman_book_attachment, `other_seaman_book_${user.id}`)} format="custom" scale={scale} />

                <FieldItem label="US Visa Status" value={user.us_visa_status} icon={ShieldCheck} scale={scale} />
                <FieldItem label="Schengen Visa Status" value={user.schengen_visa_status} icon={ShieldCheck} scale={scale} />
            </Section>

            {/* Next of Kin */}
            <Section title="Next of Kin" icon={Heart} scale={scale} columns={2}>
                <FieldItem label="Full Name" value={user.next_of_kin_full_name || user.emergency_contact_name} scale={scale} />
                <FieldItem label="Relationship" value={user.next_of_kin_relationship || user.emergency_contact_relationship} scale={scale} />
                <FieldItem label="Phone" value={user.next_of_kin_phone || user.emergency_contact_phone} iconType="phone" scale={scale} />
                <FieldItem label="Email" value={user.next_of_kin_email} iconType="email" scale={scale} />
                <FieldItem label="Address / Country" value={user.next_of_kin_address_country || user.emergency_contact_address} fullWidth scale={scale} />
            </Section>

            {/* Professional & Admin */}
            <Section title="Professional & Admin" icon={Briefcase} scale={scale} columns={3}>
                <FieldItem label="Application Position" value={user.application_for_position} scale={scale} />
                <FieldItem label="User Status" value={user.user_status} scale={scale} />
                <FieldItem label="Role" value={user.role} scale={scale} />
                <FieldItem label="Register Code" value={user.register_code} scale={scale} />
                <FieldItem label="Available From" value={user.available_date} format="date" scale={scale} />
                <FieldItem label="Salary Expected" value={user.salary} scale={scale} />
                <FieldItem label="Register Date" value={user.register_date} format="date" scale={scale} />
                <FieldItem label="Nearest Port" value={user.Nearest_Port || user.nearest_port} scale={scale} />
                {user.is_blacklisted && <FieldItem label="Blacklist Status" value="BLACKLISTED" color="red" scale={scale} />}
                {user.is_blacklisted && <FieldItem label="Reason" value={user.blacklist_reason} fullWidth scale={scale} />}
            </Section>

            {/* Test Results (Marlins / CES) */}
            <Section title="Professional Tests" icon={ClipboardCheck} scale={scale} columns={2}>
                <FieldItem label="Marlins Result" value={user.marlins_test_result} scale={scale} />
                <FieldItem label="Marlins Date" value={user.marlins_test_issued_date} format="date" scale={scale} />
                <FieldItem label="Marlins Issued By" value={user.marlins_test_issued_by} scale={scale} />
                <FieldItem label="Marlins File" value={renderDownloadLink('marlins', user.marlins_test_attachment, `marlins_${user.id}`)} format="custom" scale={scale} />

                <FieldItem label="CES Result" value={user.ces_test_result} scale={scale} />
                <FieldItem label="CES Date" value={user.ces_test_issued_date} format="date" scale={scale} />
                <FieldItem label="CES Issued By" value={user.ces_test_issued_by} scale={scale} />
                <FieldItem label="CES File" value={renderDownloadLink('ces', user.ces_test_attachment, `ces_${user.id}`)} format="custom" scale={scale} />
            </Section>

            {/* COC / GOC Details */}
            <Section title="COC / GOC Certificates" icon={GraduationCap} scale={scale} columns={2}>
                <FieldItem label="COC Name" value={user.coc_certificate_name} scale={scale} />
                <FieldItem label="COC Number" value={user.coc_certificate_number} scale={scale} />
                <FieldItem label="COC Issue Date" value={user.coc_issue_date} format="date" scale={scale} />
                <FieldItem label="COC Expiry" value={user.coc_expiry_date} format="date" scale={scale} />

                <FieldItem label="GOC Number" value={user.goc_certificate_number} scale={scale} />
                <FieldItem label="GOC Issue Date" value={user.goc_issue_date} format="date" scale={scale} />
                <FieldItem label="GOC Expiry" value={user.goc_expiry_date} format="date" scale={scale} />
            </Section>

            {/* Health & Medical */}
            <Section title="Health & Medical" icon={Stethoscope} scale={scale} columns={3}>
                <FieldItem label="Health Flag State" value={user.health_flag_state} scale={scale} />
                <FieldItem label="Health Number" value={user.health_number} scale={scale} />
                <FieldItem label="Health Expiry" value={user.health_expiry_date} format="date" scale={scale} />

                <FieldItem label="Intl Medical No" value={user.international_medical_number} scale={scale} />
                <FieldItem label="Intl Med Expiry" value={user.international_medical_expiry_date} format="date" scale={scale} />

                <FieldItem label="Yellow Fever No" value={user.yellow_fever_number} scale={scale} />
                <FieldItem label="Yellow Fever Exp" value={user.yellow_fever_expiry_date} format="date" scale={scale} />

                <FieldItem label="Cholera Number" value={user.cholera_number} scale={scale} />
                <FieldItem label="Cholera Expiry" value={user.cholera_expiry_date} format="date" scale={scale} />

                <FieldItem label="Covid Vaccine" value={user.covid_vaccine_name} scale={scale} />
                <FieldItem label="Covid 1st Dose" value={user.covid_first_dose} format="date" scale={scale} />
                <FieldItem label="Covid 2nd Dose" value={user.covid_second_dose} format="date" scale={scale} />
            </Section>

            {/* Bank Information */}
            {(user.bank_name || user.bank_account_number) && (
                <Section title="Bank Information" icon={Building} scale={scale} columns={2}>
                    <FieldItem label="Bank Name" value={user.bank_name} scale={scale} />
                    <FieldItem label="Account Number" value={user.bank_account_number} scale={scale} />
                    <FieldItem label="IBAN" value={user.iban} scale={scale} />
                    <FieldItem label="SWIFT Code" value={user.swift_code} scale={scale} />
                </Section>
            )}

            {/* Declarations */}
            {user.declaration && (
                <Section title="Declarations" icon={ShieldAlert} scale={scale} columns={2}>
                    <FieldItem label="Consent Given" value={user.declaration.consent_given ? "Yes" : "No"} scale={scale} />
                    <FieldItem label="Declaration Date" value={user.declaration.declaration_date} format="date" scale={scale} />
                    <FieldItem label="Disease History" value={user.declaration.disease_history} fullWidth scale={scale} />
                </Section>
            )}

            {/* Sea Service History */}
            <ListSection
                title={`Sea Service History (${user.sea_services?.length || 0})`}
                items={user.sea_services || []}
                renderItem={renderSeaService}
                emptyMessage="No sea service history recorded"
                scale={scale}
            />

            {/* Language Proficiency */}
            <ListSection
                title={`Languages (${user.languages?.length || 0})`}
                items={user.languages || []}
                renderItem={renderLanguage}
                emptyMessage="No additional languages recorded"
                scale={scale}
            />

            {/* Vaccinations */}
            <ListSection
                title={`Other Vaccinations (${user.vaccinations?.length || 0})`}
                items={user.vaccinations || []}
                renderItem={renderVaccination}
                emptyMessage="No additional vaccinations recorded"
                scale={scale}
            />

            {/* References */}
            <ListSection
                title={`Professional References (${user.references?.length || 0})`}
                items={user.references || []}
                renderItem={renderReference}
                emptyMessage="No references provided"
                scale={scale}
            />

            {/* Certificates */}
            <ListSection
                title={`STCW Certificates (${user.certificates?.length || user.user_certificates?.length || 0})`}
                items={user.certificates || user.user_certificates || []}
                renderItem={renderCertificate}
                emptyMessage="No STCW certificates assigned"
                scale={scale}
            />

            {/* Ranks */}
            <ListSection
                title={`Rank Codes Held (${user.ranks?.length || user.user_ranks?.length || 0})`}
                items={user.ranks || user.user_ranks || []}
                renderItem={renderRank}
                emptyMessage="No rank codes assigned"
                scale={scale}
            />

            {/* Notes */}
            {user.notes && (
                <Section title="Notes" icon={FileText} scale={scale} columns={1}>
                    <FieldItem
                        label="Additional Notes"
                        value={user.notes}
                        fullWidth
                        scale={scale}
                    />
                </Section>
            )}
        </ViewDetailModal>
    );
}

export default UserViewModal;
