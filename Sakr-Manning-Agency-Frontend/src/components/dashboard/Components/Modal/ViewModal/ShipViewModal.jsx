// components/dashboard/Components/Modal/ViewModal/ShipViewModal.jsx
/**
 * ShipViewModal - Ship Detail View Modal
 * 
 * Displays comprehensive ship information including:
 * - Ship details
 * - Technical specifications
 * - Crew information
 * - Associated company
 */

import React from "react";
import {
    Ship, Building, Anchor, MapPin, Hash, Users,
    Activity, Calendar, FileText
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
    if (!ship) return null;

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
                <FieldItem label="Flag (ID)" value={ship.flag} icon={MapPin} scale={scale} />
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
        </ViewDetailModal>
    );
}

export default ShipViewModal;
