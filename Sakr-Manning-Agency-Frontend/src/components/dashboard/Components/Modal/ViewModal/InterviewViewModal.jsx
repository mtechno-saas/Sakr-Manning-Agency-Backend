// components/dashboard/Components/Modal/ViewModal/InterviewViewModal.jsx
/**
 * InterviewViewModal - Interview Detail View Modal
 * 
 * Displays comprehensive interview information including:
 * - Candidate information
 * - Interview schedule
 * - Company/Position details
 * - Interview type and status
 */

import React from "react";
import {
    Calendar, User, Building, Clock, Video, MapPin,
    FileText, Phone, Mail, MessageSquare, Briefcase
} from "lucide-react";
import {
    ViewDetailModal,
    Section,
    FieldItem,
    AvatarHeader,
    StatusBadge,
} from "./ViewDetailModal";

// Interview type icons
const typeIcons = {
    video: Video,
    "in-person": MapPin,
    phone: Phone,
    online: Video,
};

export function InterviewViewModal({
    isOpen,
    onClose,
    interview,
    onDelete,
    scale = 1,
    canDelete = true,
}) {
    if (!interview) return null;

    // Get display names
    const candidateName = interview.candidate_name ||
        (interview.candidate?.first_name ?
            `${interview.candidate.first_name} ${interview.candidate.middle_name || ''}`.trim() :
            `Candidate #${interview.candidate}`);

    const companyName = interview.company_name ||
        interview.company?.name ||
        (interview.company ? `Company #${interview.company}` : "Not Specified");

    const positionName = interview.position_name ||
        interview.position?.name ||
        interview.position ||
        "Not Specified";

    // Format time display
    const formatTime = (time) => {
        if (!time) return "—";
        // Handle HH:MM:SS or HH:MM format
        const parts = time.split(":");
        const hours = parseInt(parts[0], 10);
        const minutes = parts[1] || "00";
        const ampm = hours >= 12 ? "PM" : "AM";
        const displayHours = hours % 12 || 12;
        return `${displayHours}:${minutes} ${ampm}`;
    };

    // Build actions array
    const actions = [];
    if (canDelete && onDelete) {
        actions.push({
            label: "Delete",
            onClick: () => onDelete(interview.id),
            variant: "danger",
        });
    }
    actions.push({
        label: "Close",
        onClick: onClose,
        variant: "primary",
    });

    const TypeIcon = typeIcons[interview.interview_type?.toLowerCase()] || Calendar;

    return (
        <ViewDetailModal
            isOpen={isOpen}
            onClose={onClose}
            title="Interview Details"
            subtitle={`Interview ID: ${interview.id}`}
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
                            backgroundColor: "#8B5CF6",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            color: "white",
                        }}
                    >
                        <TypeIcon size={Math.round(28 * scale)} />
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
                            {candidateName}
                        </h3>
                        <p
                            style={{
                                fontSize: `${Math.round(14 * scale)}px`,
                                color: "#6B7280",
                                margin: `${Math.round(4 * scale)}px 0 0 0`,
                            }}
                        >
                            {positionName} at {companyName}
                        </p>
                    </div>
                </div>
                <StatusBadge status={interview.status} scale={scale} />
            </div>

            {/* Schedule Information */}
            <Section title="Schedule" icon={Calendar} scale={scale} columns={3}>
                <FieldItem
                    label="Date"
                    value={interview.scheduled_date}
                    format="date"
                    iconType="date"
                    scale={scale}
                />
                <FieldItem
                    label="Time"
                    value={formatTime(interview.scheduled_time)}
                    icon={Clock}
                    scale={scale}
                />
                <FieldItem
                    label="Duration"
                    value={interview.duration_minutes ? `${interview.duration_minutes} minutes` : null}
                    icon={Clock}
                    scale={scale}
                />
            </Section>

            {/* Interviewer Details */}
            {(interview.interviewer_name || interview.interviewer_email) && (
                <Section title="Interviewer Information" icon={User} scale={scale} columns={2}>
                    <FieldItem label="Interviewer Name" value={interview.interviewer_name} scale={scale} />
                    <FieldItem label="Interviewer Email" value={interview.interviewer_email} icon={Mail} scale={scale} />
                </Section>
            )}

            {/* Interview Details */}
            <Section title="Interview Details" icon={MessageSquare} scale={scale} columns={2}>
                <FieldItem label="Type" value={interview.interview_type} scale={scale} />
                <FieldItem label="Status" value={interview.status} scale={scale} />
                {interview.meeting_link && (
                    <FieldItem
                        label="Meeting Link"
                        value={interview.meeting_link}
                        icon={Video}
                        fullWidth
                        scale={scale}
                    />
                )}
                {interview.location && (
                    <FieldItem
                        label="Location"
                        value={interview.location}
                        iconType="location"
                        fullWidth
                        scale={scale}
                    />
                )}
            </Section>

            {/* Candidate Information */}
            <Section title="Candidate Information" icon={User} scale={scale} columns={2}>
                <FieldItem label="Name" value={candidateName} scale={scale} />
                <FieldItem label="Candidate ID" value={interview.candidate} scale={scale} />
                <FieldItem
                    label="Email"
                    value={interview.candidate_email || interview.candidate?.email}
                    iconType="email"
                    scale={scale}
                />
                <FieldItem
                    label="Phone"
                    value={interview.candidate_phone || interview.candidate?.phone_number}
                    iconType="phone"
                    scale={scale}
                />
            </Section>

            {/* Company Information */}
            <Section title="Company & Position" icon={Building} scale={scale} columns={2}>
                <FieldItem label="Company" value={companyName} scale={scale} />
                <FieldItem label="Position" value={positionName} icon={Briefcase} scale={scale} />
            </Section>

            {/* Notes */}
            {interview.notes && (
                <Section title="Notes" icon={FileText} scale={scale} columns={1}>
                    <FieldItem label="Interview Notes" value={interview.notes} fullWidth scale={scale} />
                </Section>
            )}

            {/* Metadata */}
            <Section title="Record Information" icon={Clock} scale={scale} columns={2}>
                <FieldItem label="Created At" value={interview.created_at} format="datetime" scale={scale} />
                <FieldItem label="Updated At" value={interview.updated_at} format="datetime" scale={scale} />
            </Section>
        </ViewDetailModal>
    );
}

export default InterviewViewModal;
