// components/dashboard/Components/Modal/ViewModal/CompanyViewModal.jsx
/**
 * CompanyViewModal - Company Detail View Modal
 * 
 * Displays comprehensive company information including:
 * - Basic details
 * - Contact information
 * - Statistics
 * - Related ships
 */

import React from "react";
import {
    Building, Phone, Mail, MapPin, Users, Ship,
    FileText, Globe, Hash, Calendar, Briefcase
} from "lucide-react";
import {
    ViewDetailModal,
    Section,
    FieldItem,
    StatusBadge,
    ListSection,
    Tag,
} from "./ViewDetailModal";

export function CompanyViewModal({
    isOpen,
    onClose,
    company,
    onDelete,
    scale = 1,
    canDelete = true,
}) {
    if (!company) return null;

    // Build actions array
    const actions = [];
    if (canDelete && onDelete) {
        actions.push({
            label: "Delete",
            onClick: () => onDelete(company.id),
            variant: "danger",
        });
    }
    actions.push({
        label: "Close",
        onClick: onClose,
        variant: "primary",
    });

    // Ship renderer
    const renderShip = (ship, scale) => (
        <Tag color="#0EA5E9" scale={scale}>
            <Ship size={Math.round(12 * scale)} style={{ marginRight: 4 }} />
            {ship.ship_name || ship.name || ship}
        </Tag>
    );

    return (
        <ViewDetailModal
            isOpen={isOpen}
            onClose={onClose}
            title="Company Details"
            subtitle={`Company ID: ${company.id}`}
            actions={actions}
            scale={scale}
            size="lg"
        >
            {/* Header */}
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
                    <div
                        style={{
                            width: `${Math.round(56 * scale)}px`,
                            height: `${Math.round(56 * scale)}px`,
                            borderRadius: `${Math.round(12 * scale)}px`,
                            backgroundColor: "#3B82F6",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            color: "white",
                        }}
                    >
                        <Building size={Math.round(28 * scale)} />
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
                            {company.company_name || company.name || "Unknown Company"}
                        </h3>
                        <p
                            style={{
                                fontSize: `${Math.round(14 * scale)}px`,
                                color: "#6B7280",
                                margin: `${Math.round(4 * scale)}px 0 0 0`,
                            }}
                        >
                            {company.company_type || "Company"}
                        </p>
                    </div>
                </div>
                <StatusBadge status={company.status} scale={scale} />
            </div>

            {/* Basic Information */}
            <Section title="Company Information" icon={Building} scale={scale} columns={2}>
                <FieldItem label="Company Name" value={company.company_name || company.name} scale={scale} />
                <FieldItem label="Company Type" value={company.company_type} icon={Briefcase} scale={scale} />
                <FieldItem label="Status" value={company.status} scale={scale} />
                <FieldItem label="Open Positions" value={company.open_positions} icon={Users} scale={scale} />
                <FieldItem label="Hourly Rate" value={company.hourly_rate} icon={Hash} scale={scale} />
            </Section>

            {/* Contact Information */}
            <Section title="Contact Information" icon={Phone} scale={scale} columns={2}>
                <FieldItem label="Email" value={company.contact_email || company.email} iconType="email" scale={scale} />
                <FieldItem label="Website" value={company.website} icon={Globe} scale={scale} />
                <FieldItem label="Country (Flag)" value={company.company_flag} scale={scale} />
            </Section>

            {/* Business Information */}
            {(company.registration_number || company.tax_id) && (
                <Section title="Business Information" icon={FileText} scale={scale} columns={2}>
                    <FieldItem label="Registration Number" value={company.registration_number} icon={Hash} scale={scale} />
                    <FieldItem label="Tax ID" value={company.tax_id} scale={scale} />
                </Section>
            )}

            {/* Related Ships */}
            {company.ships && company.ships.length > 0 && (
                <ListSection
                    title={`Ships (${company.ships.length})`}
                    items={company.ships}
                    renderItem={renderShip}
                    emptyMessage="No ships assigned"
                    scale={scale}
                />
            )}

            {/* Statistics */}
            {(company.total_contracts || company.active_employees) && (
                <Section title="Statistics" icon={Hash} scale={scale} columns={3}>
                    <FieldItem label="Total Contracts" value={company.total_contracts} format="number" scale={scale} />
                    <FieldItem label="Active Employees" value={company.active_employees} format="number" scale={scale} />
                    <FieldItem label="Total Ships" value={company.ships?.length || company.total_ships} format="number" scale={scale} />
                </Section>
            )}

            {/* Notes */}
            {company.notes && (
                <Section title="Notes" icon={FileText} scale={scale} columns={1}>
                    <FieldItem label="Additional Notes" value={company.notes} fullWidth scale={scale} />
                </Section>
            )}

            {/* Metadata */}
            <Section title="Record Information" icon={Calendar} scale={scale} columns={2}>
                <FieldItem label="Created At" value={company.created_at} format="datetime" scale={scale} />
                <FieldItem label="Updated At" value={company.updated_at} format="datetime" scale={scale} />
            </Section>
        </ViewDetailModal>
    );
}

export default CompanyViewModal;
