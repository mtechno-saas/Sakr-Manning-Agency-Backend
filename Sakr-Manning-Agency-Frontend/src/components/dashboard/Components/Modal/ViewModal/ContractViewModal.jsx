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

import React from "react";
import {
    FileText, User, Building, Ship, Calendar,
    DollarSign, Clock, MapPin, Anchor
} from "lucide-react";
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

    // Build actions array
    const actions = [];
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
        variant: "primary",
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
            </Section>

            {/* Employee Information */}
            <Section title="Employee Information" icon={User} scale={scale} columns={2}>
                <FieldItem label="Employee Name" value={userName} scale={scale} />
                <FieldItem label="Employee ID" value={contract.user} scale={scale} />
                <FieldItem label="Rank" value={rankName} icon={Anchor} scale={scale} />
                <FieldItem label="Email" value={contract.user_email || contract.user?.email} iconType="email" scale={scale} />
            </Section>

            {/* Company Information */}
            <Section title="Company Information" icon={Building} scale={scale} columns={2}>
                <FieldItem label="Company Name" value={companyName} scale={scale} />
                <FieldItem label="Company ID" value={contract.company} scale={scale} />
            </Section>

            {/* Ship Information */}
            <Section title="Ship Information" icon={Ship} scale={scale} columns={2}>
                <FieldItem label="Ship Name" value={shipName} scale={scale} />
                <FieldItem label="Ship ID" value={contract.ship} scale={scale} />
            </Section>

            {/* Financial Information */}
            <Section title="Financial Information" icon={DollarSign} scale={scale} columns={2}>
                <FieldItem label="Salary" value={contract.salary} format="currency" scale={scale} />
                <FieldItem label="Currency" value={contract.currency || "USD"} scale={scale} />
            </Section>

            {/* Metadata */}
            <Section title="Record Information" icon={Clock} scale={scale} columns={2}>
                <FieldItem label="Created At" value={contract.created_at} format="datetime" scale={scale} />
                <FieldItem label="Updated At" value={contract.updated_at} format="datetime" scale={scale} />
            </Section>
        </ViewDetailModal>
    );
}

export default ContractViewModal;
