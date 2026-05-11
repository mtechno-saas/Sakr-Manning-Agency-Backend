// components/dashboard/Components/Modal/ViewModal/ViewDetailModal.jsx
/**
 * ViewDetailModal - Universal Detail View Modal Component
 * 
 * A reusable component for displaying detailed data in a clean, organized modal.
 * Supports sections, field groups, badges, images, lists, and more.
 * 
 * Props:
 * - isOpen: boolean - Controls modal visibility
 * - onClose: function - Close handler
 * - title: string - Modal title
 * - subtitle: string - Optional subtitle
 * - data: object - The data to display
 * - sections: array - Configuration for organizing data into sections
 * - headerContent: ReactNode - Optional header content (e.g., avatar, status)
 * - actions: array - Action buttons [{label, onClick, variant}]
 * - scale: number - Scale factor
 * - size: string - Modal size ('sm', 'md', 'lg', 'xl')
 */

import React from "react";
import { X, Mail, Phone, MapPin, Calendar, User, Briefcase, Shield, Clock, ExternalLink } from "lucide-react";
import { BaseModal } from "../BaseModal";
import Button from "../../Common/Button";
import { getMediaUrl } from "../../../../../utils/fileHelpers";

// Field value formatters
const formatters = {
    date: (value) => {
        if (!value) return "—";
        return new Date(value).toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric",
        });
    },
    datetime: (value) => {
        if (!value) return "—";
        return new Date(value).toLocaleString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    },
    currency: (value, currency = "USD") => {
        if (!value && value !== 0) return "—";
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: currency,
        }).format(value);
    },
    number: (value) => {
        if (!value && value !== 0) return "—";
        return new Intl.NumberFormat("en-US").format(value);
    },
    boolean: (value) => (value ? "Yes" : "No"),
    array: (value, separator = ", ") => {
        if (!value || !Array.isArray(value) || value.length === 0) return "—";
        return value.join(separator);
    },
    link: (value) => {
        if (!value) return "—";
        const url = getMediaUrl(value);
        return (
            <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                    color: "#3B82F6",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "4px",
                    textDecoration: "none",
                }}
            >
                View / Download <ExternalLink size={14} />
            </a>
        );
    },
    custom: (value) => value,
    default: (value) => {
        if (value === null || value === undefined || value === "") return "—";
        return String(value);
    },
};

// Status badge colors
const statusColors = {
    // ── CV Submission pipeline ────────────────────────────────────────────
    pending: { bg: "#F3F4F6", text: "#555555", border: "#E5E7EB" },
    "under review": { bg: "#FEF3C7", text: "#B45309", border: "#FDE68A" },
    interviewed: { bg: "#EDE9FE", text: "#6D28D9", border: "#DDD6FE" },
    shortlisted: { bg: "#DBEAFE", text: "#1D4ED8", border: "#BFDBFE" },
    approved: { bg: "#DBEAF7", text: "#0065AF", border: "#91BBE1" },
    hired: { bg: "#DCFCE7", text: "#15AB10", border: "#86EFAC" },
    rejected: { bg: "#FEE2E2", text: "#B21101", border: "#FECACA" },

    // ── General / Document statuses ───────────────────────────────────────
    active: { bg: "#DCFCE7", text: "#166534", border: "#86EFAC" },
    inactive: { bg: "#F3F4F6", text: "#374151", border: "#D1D5DB" },
    completed: { bg: "#DBEAFE", text: "#1E40AF", border: "#93C5FD" },
    cancelled: { bg: "#FEE2E2", text: "#991B1B", border: "#FECACA" },
    signed: { bg: "#DCFCE7", text: "#166534", border: "#86EFAC" },
    expired: { bg: "#FEE2E2", text: "#991B1B", border: "#FECACA" },
    draft: { bg: "#E0E7FF", text: "#3730A3", border: "#A5B4FC" },
    "pending signature": { bg: "#FEF3C7", text: "#92400E", border: "#FCD34D" },
    vacation: { bg: "#EDE9FE", text: "#5B21B6", border: "#C4B5FD" },
    on_site: { bg: "#DCFCE7", text: "#166534", border: "#86EFAC" },
    "on site": { bg: "#DCFCE7", text: "#166534", border: "#86EFAC" },
    "medical vacation": { bg: "#FEF3C7", text: "#92400E", border: "#FCD34D" },
    scheduled: { bg: "#DBEAFE", text: "#1E40AF", border: "#93C5FD" },
    rescheduled: { bg: "#FEF3C7", text: "#92400E", border: "#FCD34D" },
    prospect: { bg: "#E0E7FF", text: "#3730A3", border: "#A5B4FC" },
    blacklist: { bg: "#FEE2E2", text: "#B21101", border: "#FECACA" },
    default: { bg: "#F3F4F6", text: "#374151", border: "#D1D5DB" },
};

// Get icon for field type
const fieldIcons = {
    email: Mail,
    phone: Phone,
    location: MapPin,
    date: Calendar,
    user: User,
    role: Briefcase,
    permission: Shield,
    time: Clock,
};

// Status Badge Component
export const StatusBadge = ({ status, scale = 1 }) => {
    const normalizedStatus = (status || "").toLowerCase();
    const colors = statusColors[normalizedStatus] || statusColors.default;

    return (
        <span
            style={{
                display: "inline-flex",
                alignItems: "center",
                padding: `${Math.round(4 * scale)}px ${status === 'Pending Signature' ? Math.round(2 * scale) : Math.round(12 * scale)}px`,
                borderRadius: `${Math.round(999 * scale)}px`,
                backgroundColor: colors.bg,
                color: colors.text,
                border: `1px solid ${colors.border}`,
                fontSize: `${Math.round(12 * scale)}px`,
                fontWeight: 600,
                textTransform: "capitalize",
            }}
        >
            {status || "Unknown"}
        </span>
    );
};

// Field Item Component
export const FieldItem = ({
    label,
    value,
    format = "default",
    icon: Icon,
    iconType,
    fullWidth = false,
    scale = 1,
}) => {
    const IconComponent = Icon || fieldIcons[iconType];
    const formattedValue = formatters[format]
        ? formatters[format](value)
        : formatters.default(value);

    return (
        <div
            style={{
                display: "flex",
                flexDirection: "column",
                gap: `${Math.round(4 * scale)}px`,
                gridColumn: fullWidth ? "1 / -1" : undefined,
            }}
        >
            <span
                style={{
                    fontSize: `${Math.round(12 * scale)}px`,
                    fontWeight: 500,
                    color: "#6B7280",
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    display: "flex",
                    alignItems: "center",
                    gap: `${Math.round(6 * scale)}px`,
                }}
            >
                {IconComponent && (
                    <IconComponent size={Math.round(14 * scale)} color="#9CA3AF" />
                )}
                {label}
            </span>
            <span
                style={{
                    fontSize: `${Math.round(14 * scale)}px`,
                    fontWeight: 400,
                    color: "#111827",
                    wordBreak: "break-word",
                }}
            >
                {formattedValue}
            </span>
        </div>
    );
};

// Section Component
export const Section = ({ title, icon: Icon, children, scale = 1, columns = 2 }) => {
    return (
        <div
            style={{
                marginBottom: `${Math.round(24 * scale)}px`,
            }}
        >
            {title && (
                <h3
                    style={{
                        fontSize: `${Math.round(14 * scale)}px`,
                        fontWeight: 600,
                        color: "#374151",
                        marginBottom: `${Math.round(16 * scale)}px`,
                        paddingBottom: `${Math.round(8 * scale)}px`,
                        borderBottom: "1px solid #E5E7EB",
                        display: "flex",
                        alignItems: "center",
                        gap: `${Math.round(8 * scale)}px`,
                    }}
                >
                    {Icon && <Icon size={Math.round(16 * scale)} color="#6B7280" />}
                    {title}
                </h3>
            )}
            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: `repeat(${columns}, 1fr)`,
                    gap: `${Math.round(16 * scale)}px`,
                }}
            >
                {children}
            </div>
        </div>
    );
};

// List Item Component (for arrays like certificates, ranks)
export const ListSection = ({ title, items, renderItem, emptyMessage = "No items", scale = 1 }) => {
    return (
        <div style={{ marginBottom: `${Math.round(24 * scale)}px` }}>
            <h3
                style={{
                    fontSize: `${Math.round(14 * scale)}px`,
                    fontWeight: 600,
                    color: "#374151",
                    marginBottom: `${Math.round(12 * scale)}px`,
                    paddingBottom: `${Math.round(8 * scale)}px`,
                    borderBottom: "1px solid #E5E7EB",
                }}
            >
                {title}
            </h3>
            {items && items.length > 0 ? (
                <div
                    style={{
                        display: "flex",
                        flexWrap: "wrap",
                        gap: `${Math.round(8 * scale)}px`,
                    }}
                >
                    {items.map((item, index) => (
                        <div key={index}>{renderItem ? renderItem(item, scale) : item}</div>
                    ))}
                </div>
            ) : (
                <p
                    style={{
                        color: "#9CA3AF",
                        fontSize: `${Math.round(14 * scale)}px`,
                        fontStyle: "italic",
                    }}
                >
                    {emptyMessage}
                </p>
            )}
        </div>
    );
};

// Tag/Chip Component
export const Tag = ({ children, color = "#3B82F6", scale = 1 }) => {
    return (
        <span
            style={{
                display: "inline-flex",
                alignItems: "center",
                padding: `${Math.round(4 * scale)}px ${Math.round(10 * scale)}px`,
                borderRadius: `${Math.round(6 * scale)}px`,
                backgroundColor: `${color}15`,
                color: color,
                fontSize: `${Math.round(12 * scale)}px`,
                fontWeight: 500,
            }}
        >
            {children}
        </span>
    );
};

// Avatar Header Component
export const AvatarHeader = ({
    image,
    name,
    subtitle,
    status,
    scale = 1,
}) => {
    return (
        <div
            style={{
                display: "flex",
                alignItems: "center",
                gap: `${Math.round(16 * scale)}px`,
                padding: `${Math.round(16 * scale)}px`,
                backgroundColor: "#F9FAFB",
                borderRadius: `${Math.round(12 * scale)}px`,
                marginBottom: `${Math.round(24 * scale)}px`,
            }}
        >
            {image ? (
                <img
                    src={getMediaUrl(image)}
                    alt={name}
                    style={{
                        width: `${Math.round(64 * scale)}px`,
                        height: `${Math.round(64 * scale)}px`,
                        borderRadius: "50%",
                        objectFit: "cover",
                        border: "3px solid white",
                        boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                    }}
                />
            ) : (
                <div
                    style={{
                        width: `${Math.round(64 * scale)}px`,
                        height: `${Math.round(64 * scale)}px`,
                        borderRadius: "50%",
                        backgroundColor: "#3B82F6",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "white",
                        fontSize: `${Math.round(24 * scale)}px`,
                        fontWeight: 600,
                    }}
                >
                    {name?.charAt(0)?.toUpperCase() || "?"}
                </div>
            )}
            <div style={{ flex: 1 }}>
                <h3
                    style={{
                        fontSize: `${Math.round(18 * scale)}px`,
                        fontWeight: 600,
                        color: "#111827",
                        margin: 0,
                    }}
                >
                    {name || "Unknown"}
                </h3>
                {subtitle && (
                    <p
                        style={{
                            fontSize: `${Math.round(14 * scale)}px`,
                            color: "#6B7280",
                            margin: `${Math.round(4 * scale)}px 0 0 0`,
                        }}
                    >
                        {subtitle}
                    </p>
                )}
            </div>
            {status && <StatusBadge status={status} scale={scale} />}
        </div>
    );
};

// Main ViewDetailModal Component
export function ViewDetailModal({
    isOpen,
    onClose,
    title,
    subtitle,
    children,
    actions = [],
    scale = 1,
    size = "lg",
    loading = false,
}) {
    if (!isOpen) return null;

    const footer = actions.length > 0 && (
        <div
            style={{
                display: "flex",
                gap: `${Math.round(12 * scale)}px`,
                justifyContent: "flex-end",
                padding: `${Math.round(2 * scale)}px`
            }}
        >
            {actions.map((action, index) => (
                <Button
                    key={index}
                    variant={action.variant || "outline"}
                    onClick={action.onClick}
                    scale={scale}
                    disabled={action.disabled}
                >
                    {action.icon && <action.icon size={Math.round(16 * scale)} />}
                    {action.label}
                </Button>
            ))}
        </div>
    );

    return (
        <BaseModal
            isOpen={isOpen}
            onClose={onClose}
            title={title}
            subtitle={subtitle}
            size={size}
            scale={scale}
            footer={footer}
        >
            {loading ? (
                <div
                    style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        padding: `${Math.round(40 * scale)}px`,
                    }}
                >
                    <div
                        style={{
                            width: `${Math.round(40 * scale)}px`,
                            height: `${Math.round(40 * scale)}px`,
                            border: "3px solid #E5E7EB",
                            borderTopColor: "#3B82F6",
                            borderRadius: "50%",
                            animation: "spin 1s linear infinite",
                        }}
                    />
                </div>
            ) : (
                children
            )}
        </BaseModal>
    );
}

export default ViewDetailModal;
