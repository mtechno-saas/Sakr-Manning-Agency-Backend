// components/dashboard/Components/Modal/ViewModal/FinanceViewModal.jsx
/**
 * FinanceViewModal - Finance Record Detail View Modal
 * 
 * Displays comprehensive finance record information including:
 * - Employee information
 * - Company information
 * - Period details
 * - Financial calculations
 */

import React from "react";
import {
    DollarSign, User, Building, Calendar, Clock,
    FileText, Calculator, TrendingUp
} from "lucide-react";
import {
    ViewDetailModal,
    Section,
    FieldItem,
    StatusBadge,
} from "./ViewDetailModal";

export function FinanceViewModal({
    isOpen,
    onClose,
    record,
    onDelete,
    scale = 1,
    canDelete = true,
}) {
    if (!record) return null;

    // Get display names
    const userName = record.user_name ||
        (record.user?.first_name ?
            `${record.user.first_name} ${record.user.middle_name || ''}`.trim() :
            `User #${record.user}`);

    const companyName = record.company_name ||
        record.company?.name ||
        (record.company ? `Company #${record.company}` : "Not Specified");

    // Build actions array
    const actions = [];
    if (canDelete && onDelete) {
        actions.push({
            label: "Delete",
            onClick: () => onDelete(record.id),
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
            title="Finance Record Details"
            subtitle={`Record ID: ${record.id}`}
            actions={actions}
            scale={scale}
            size="lg"
        >
            {/* Header with Total */}
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: `${Math.round(20 * scale)}px`,
                    backgroundColor: "#EBF5FF",
                    borderRadius: `${Math.round(12 * scale)}px`,
                    marginBottom: `${Math.round(24 * scale)}px`,
                    border: "2px solid #3B82F6",
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
                        <DollarSign size={Math.round(28 * scale)} />
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
                            {userName}
                        </h3>
                        <p
                            style={{
                                fontSize: `${Math.round(14 * scale)}px`,
                                color: "#6B7280",
                                margin: `${Math.round(4 * scale)}px 0 0 0`,
                            }}
                        >
                            {companyName}
                        </p>
                    </div>
                </div>
                <div style={{ textAlign: "right" }}>
                    <p
                        style={{
                            fontSize: `${Math.round(12 * scale)}px`,
                            color: "#6B7280",
                            margin: 0,
                            textTransform: "uppercase",
                            letterSpacing: "0.05em",
                        }}
                    >
                        Total Amount
                    </p>
                    <p
                        style={{
                            fontSize: `${Math.round(28 * scale)}px`,
                            fontWeight: 700,
                            color: "#3B82F6",
                            margin: `${Math.round(4 * scale)}px 0 0 0`,
                        }}
                    >
                        ${record.total_money || record.total_amount || "0.00"}
                    </p>
                </div>
            </div>

            {/* Period Information */}
            <Section title="Period" icon={Calendar} scale={scale} columns={3}>
                <FieldItem
                    label="Start Date"
                    value={record.start_date}
                    format="date"
                    iconType="date"
                    scale={scale}
                />
                <FieldItem
                    label="End Date"
                    value={record.end_date}
                    format="date"
                    iconType="date"
                    scale={scale}
                />
                <FieldItem
                    label="Total Days"
                    value={record.total_days}
                    icon={Clock}
                    scale={scale}
                />
            </Section>

            {/* Financial Breakdown */}
            <Section title="Financial Breakdown" icon={Calculator} scale={scale} columns={3}>
                <FieldItem
                    label="Daily Rate"
                    value={record.daily_rate}
                    format="currency"
                    scale={scale}
                />
                <FieldItem
                    label="Total Days"
                    value={record.total_days}
                    scale={scale}
                />
                <FieldItem
                    label="Total Amount"
                    value={record.total_money || record.total_amount}
                    format="currency"
                    scale={scale}
                />
            </Section>

            {/* Employee Information */}
            <Section title="Employee" icon={User} scale={scale} columns={2}>
                <FieldItem label="Name" value={userName} scale={scale} />
                <FieldItem label="Employee ID" value={record.user} scale={scale} />
            </Section>

            {/* Company Information */}
            <Section title="Company" icon={Building} scale={scale} columns={2}>
                <FieldItem label="Company Name" value={companyName} scale={scale} />
                <FieldItem label="Company ID" value={record.company} scale={scale} />
            </Section>

            {/* Status */}
            {record.status && (
                <Section title="Status" icon={TrendingUp} scale={scale} columns={2}>
                    <FieldItem label="Payment Status" value={record.status} scale={scale} />
                    <FieldItem label="Payment Date" value={record.payment_date} format="date" scale={scale} />
                </Section>
            )}

            {/* Notes */}
            {record.notes && (
                <Section title="Notes" icon={FileText} scale={scale} columns={1}>
                    <FieldItem label="Additional Notes" value={record.notes} fullWidth scale={scale} />
                </Section>
            )}

            {/* Metadata */}
            <Section title="Record Information" icon={Clock} scale={scale} columns={2}>
                <FieldItem label="Created At" value={record.created_at} format="datetime" scale={scale} />
                <FieldItem label="Updated At" value={record.updated_at} format="datetime" scale={scale} />
            </Section>
        </ViewDetailModal>
    );
}

export default FinanceViewModal;
