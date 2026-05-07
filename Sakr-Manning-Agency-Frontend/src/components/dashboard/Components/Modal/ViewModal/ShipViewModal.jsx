// components/dashboard/Components/Modal/ViewModal/ShipViewModal.jsx
/**
 * ShipViewModal - Ship Detail View Modal
 * 
 * Displays comprehensive ship information including:
 * - Ship details
 * - Technical specifications
 * - Crew information
 * - Associated company
 * - Associated job orders & positions
 */

import React, { useState } from "react";
import {
    Ship, Building, Anchor, MapPin, Hash, Users,
    Activity, Calendar, FileText, ClipboardList,
    ChevronDown, ChevronRight, DollarSign, Clock, Briefcase
} from "lucide-react";
import {
    ViewDetailModal,
    Section,
    FieldItem,
    StatusBadge,
    Tag,
} from "./ViewDetailModal";

export function ShipViewModal({
    isOpen,
    onClose,
    ship,
    onDelete,
    onManageCrew,
    scale = 1,
    canDelete = true,
}) {
    const [expandedOrders, setExpandedOrders] = useState({});
    if (!ship) return null;

    const toggleOrder = (id) =>
        setExpandedOrders(prev => ({ ...prev, [id]: !prev[id] }));

    const jobOrders = Array.isArray(ship.job_orders) ? ship.job_orders : [];

    // Build actions array
    const actions = [];
    if (canDelete && onDelete) {
        actions.push({
            label: "Delete",
            onClick: () => onDelete(ship.id),
            variant: "danger",
        });
    }
    if (onManageCrew) {
        actions.push({
            label: "Manage Crew",
            onClick: (e) => {
                if (e) {
                    e.stopPropagation();
                    e.preventDefault();
                }
                onManageCrew(ship);
            },
            variant: "outline",
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
            subtitle={`Ship ID: ${ship.id}`}
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
                            backgroundColor: "#0EA5E9",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            color: "white",
                        }}
                    >
                        <Ship size={Math.round(28 * scale)} />
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
                            {ship.ship_name || "Unknown Ship"}
                        </h3>
                        <p
                            style={{
                                fontSize: `${Math.round(14 * scale)}px`,
                                color: "#6B7280",
                                margin: `${Math.round(4 * scale)}px 0 0 0`,
                            }}
                        >
                            IMO: {ship.imo_number || "N/A"}
                        </p>
                    </div>
                </div>
                <StatusBadge status={ship.status} scale={scale} />
            </div>

            {/* Basic Information */}
            <Section title="Ship Information" icon={Ship} scale={scale} columns={2}>
                <FieldItem label="Ship Name" value={ship.ship_name} scale={scale} />
                <FieldItem label="IMO Number" value={ship.imo_number} icon={Hash} scale={scale} />
                <FieldItem label="Status" value={ship.status} scale={scale} />
                <FieldItem label="Ship Type (ID)" value={ship.ship_type} icon={Anchor} scale={scale} />
            </Section>

            {/* Flag & Ownership */}
            <Section title="Flag & Ownership" icon={Building} scale={scale} columns={2}>
                <FieldItem label="Flag" value={ship.flag_name || ship.flag} icon={MapPin} scale={scale} />
                <FieldItem
                    label="Company"
                    value={ship.associatedWithCompany || ship.company_name || `Company ID: ${ship.company}`}
                    scale={scale}
                />
            </Section>

            {/* Crew Information */}
            <Section title="Crew" icon={Users} scale={scale} columns={1}>
                {ship.crew && Array.isArray(ship.crew) && ship.crew.length > 0 ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: `${Math.round(8 * scale)}px`, padding: `${Math.round(4 * scale)}px` }}>
                        {ship.crew.map(member => (
                            <Tag key={member.id} color="#0EA5E9" scale={scale}>
                                <Users size={Math.round(12 * scale)} style={{ marginRight: 4 }} />
                                {member.first_name} {member.last_name || ''} {member.rank_name ? `(${member.rank_name})` : ''}
                            </Tag>
                        ))}
                    </div>
                ) : (
                    <FieldItem label="Crew Members" value="No crew assigned" scale={scale} />
                )}
            </Section>

            {/* Technical Details */}
            <Section title="Technical Details" icon={Activity} scale={scale} columns={2}>
                <FieldItem label="Gross Tonnage" value={ship.gross_tonnage} scale={scale} />
                <FieldItem label="Deadweight" value={ship.deadweight} scale={scale} />
                <FieldItem label="Build Year" value={ship.year_built} scale={scale} />
                <FieldItem label="Port of Registry" value={ship.port_of_registry} scale={scale} />
                <FieldItem label="Official No" value={ship.official_no} scale={scale} />
                <FieldItem label="Builder" value={ship.builder} scale={scale} />
            </Section>

            {/* Engine & Comms */}
            <Section title="Engine & Communications" icon={Hash} scale={scale} columns={3}>
                <FieldItem label="Engine Type" value={ship.engine_type} scale={scale} />
                <FieldItem label="Engine Power (KW)" value={ship.engine_power_kw} scale={scale} />
                <FieldItem label="Call Sign" value={ship.call_sign} scale={scale} />
                <FieldItem label="MMSI No" value={ship.mmsi_no} scale={scale} />
            </Section>

            {/* Metadata */}
            <Section title="Record Information" icon={Calendar} scale={scale} columns={2}>
                <FieldItem label="Created At" value={ship.created_at} format="datetime" scale={scale} />
                <FieldItem label="Updated At" value={ship.updated_at} format="datetime" scale={scale} />
            </Section>

            {/* Job Orders */}
            <Section title={`Job Orders (${jobOrders.length})`} icon={ClipboardList} scale={scale} columns={1}>
                {jobOrders.length === 0 ? (
                    <p style={{ fontSize: Math.round(13 * scale), color: "#9CA3AF", margin: 0 }}>No job orders linked to this ship.</p>
                ) : jobOrders.map(order => {
                    const isOpen = expandedOrders[order.id];
                    const positions = Array.isArray(order.positions) ? order.positions : [];
                    return (
                        <div key={order.id} style={{
                            border: "1px solid #E5E7EB",
                            borderRadius: Math.round(8 * scale),
                            marginBottom: Math.round(10 * scale),
                            overflow: "hidden",
                        }}>
                            {/* Order header row */}
                            <div
                                onClick={() => toggleOrder(order.id)}
                                style={{
                                    display: "flex", alignItems: "center", justifyContent: "space-between",
                                    padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                                    background: "#F9FAFB", cursor: "pointer",
                                }}
                            >
                                <div style={{ display: "flex", alignItems: "center", gap: Math.round(10 * scale) }}>
                                    {isOpen
                                        ? <ChevronDown size={Math.round(15 * scale)} color="#6B7280" />
                                        : <ChevronRight size={Math.round(15 * scale)} color="#6B7280" />}
                                    <Briefcase size={Math.round(14 * scale)} color="#6366F1" />
                                    <span style={{ fontWeight: 600, fontSize: Math.round(13 * scale), color: "#1F2937" }}>
                                        {order.reference_number || `Order #${order.id}`}
                                    </span>
                                </div>
                                <div style={{ display: "flex", alignItems: "center", gap: Math.round(8 * scale) }}>
                                    <span style={{
                                        fontSize: Math.round(11 * scale), fontWeight: 700,
                                        padding: `2px ${Math.round(8 * scale)}px`,
                                        borderRadius: 20,
                                        background: order.status === "Open" ? "#DCFCE7" : "#F3F4F6",
                                        color: order.status === "Open" ? "#15803D" : "#374151",
                                    }}>{order.status}</span>
                                    <span style={{ fontSize: Math.round(11 * scale), color: "#6B7280" }}>
                                        {positions.length} position{positions.length !== 1 ? "s" : ""}
                                    </span>
                                </div>
                            </div>

                            {/* Expanded: order meta + positions table */}
                            {isOpen && (
                                <div style={{ padding: `${Math.round(12 * scale)}px ${Math.round(14 * scale)}px`, background: "#fff" }}>
                                    {/* Order meta */}
                                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: Math.round(8 * scale), marginBottom: Math.round(10 * scale) }}>
                                        <FieldItem label="Request Date" value={order.request_date} icon={Calendar} scale={scale} />
                                        <FieldItem label="Target Joining" value={order.target_joining_date} icon={Calendar} scale={scale} />
                                        {order.notes && <FieldItem label="Notes" value={order.notes} icon={FileText} scale={scale} />}
                                    </div>

                                    {/* Positions table */}
                                    {positions.length > 0 && (
                                        <div style={{ overflowX: "auto" }}>
                                            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: Math.round(12 * scale) }}>
                                                <thead>
                                                    <tr style={{ background: "#F3F4F6" }}>
                                                        {["Rank", "Qty", "Salary Min", "Salary Max", "Currency", "Duration", "Remarks"].map(h => (
                                                            <th key={h} style={{ padding: `${Math.round(6 * scale)}px ${Math.round(10 * scale)}px`, textAlign: "left", fontWeight: 600, color: "#374151", whiteSpace: "nowrap" }}>{h}</th>
                                                        ))}
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {positions.map((pos, i) => (
                                                        <tr key={pos.id ?? i} style={{ borderTop: "1px solid #E5E7EB", background: i % 2 === 0 ? "#fff" : "#FAFAFA" }}>
                                                            <td style={{ padding: `${Math.round(6 * scale)}px ${Math.round(10 * scale)}px`, fontWeight: 500 }}>{pos.rank_name || `Rank #${pos.rank}`}</td>
                                                            <td style={{ padding: `${Math.round(6 * scale)}px ${Math.round(10 * scale)}px` }}>{pos.quantity}</td>
                                                            <td style={{ padding: `${Math.round(6 * scale)}px ${Math.round(10 * scale)}px` }}>{pos.salary_min}</td>
                                                            <td style={{ padding: `${Math.round(6 * scale)}px ${Math.round(10 * scale)}px` }}>{pos.salary_max}</td>
                                                            <td style={{ padding: `${Math.round(6 * scale)}px ${Math.round(10 * scale)}px` }}>{pos.currency}</td>
                                                            <td style={{ padding: `${Math.round(6 * scale)}px ${Math.round(10 * scale)}px` }}>{pos.contract_duration_months ? `${pos.contract_duration_months} mo` : "—"}</td>
                                                            <td style={{ padding: `${Math.round(6 * scale)}px ${Math.round(10 * scale)}px`, color: "#6B7280" }}>{pos.remarks || "—"}</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    );
                })}
            </Section>
        </ViewDetailModal>
    );
}

export default ShipViewModal;
