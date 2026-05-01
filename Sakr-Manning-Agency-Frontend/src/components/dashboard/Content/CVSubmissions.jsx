/* eslint-disable no-unused-vars */

// Content/CVSubmissions.jsx — Seafarer Applicants / CV Submission Pipeline
import React, { useState, useEffect, useMemo, useCallback } from "react";
import { RefinedDataTable } from "../Components/Data/RefinedDataTable";
import { StatisticsCard } from "../Components/Cards/StatisticsCards";
import { ASSETS } from "../../../utils/constants";
import { exportToExcel, exportToJSON } from "../../../utils/exportHelpers";
import {
    generateAllPageStyles,
    getMainContainerStyles,
    getPageTitleStyles,
    getRowBetweenStyles,
} from "../Styles/cssClasses";

import Button from "../Components/Common/Button";
import EnhancedFilterModel from "../Components/Common/EnhancedFilterModel";
import SavedFilters from "../Components/Common/SavedFilters";
import useNotification from "../hooks/useNotification";
import useCVSubmissions from "../../../hooks/dashboard/useCVSubmissions";
import CVSubmissionFormModal from "../Components/Modal/CVSubmissionFormModal";
import DocumentUploadModal from "../Components/AI/DocumentUploadModal";
import CVSubmissionViewModal from "../Components/Modal/ViewModal/CVSubmissionViewModal";
import { useCompanies } from "../../../hooks/dashboard/useCompanies";
import { useRanks } from "../../../hooks/dashboard/useRanks";

// ── Status pipeline (matches backend choice field) ──────────────────────────
const STATUS_PIPELINE = [
    "Pending",
    "Under Review",
    "Interviewed",
    "Shortlisted",
    "Approved",
    "Hired",
    "Rejected",
];

// Status is read directly from submission.status
const mapStatusToState = (status) => {
    if (status && STATUS_PIPELINE.includes(status)) return status;
    return "Pending";
};

// Thin button style — overrides the default 40 px height to a slimmer toolbar size
const thinBtn = {
    minHeight: 30,
    height: 30,
    padding: "0 14px",
    fontSize: 13,
    borderRadius: 8,
    fontWeight: 500,
    lineHeight: "30px",
};

export function CVSubmissionsManagement({ scale = 1, isMobile = false }) {
    const { notify } = useNotification();
    const {
        submissions: backendSubmissions,
        loading,
        fetchSubmissions,
        updateStatus,
        createSubmission,
        updateSubmission,
        deleteSubmission,
        pagination,
    } = useCVSubmissions();
    const { companies, fetchCompanies } = useCompanies();
    const { ranks, fetchRanks } = useRanks();

    // Permissions (Fallback for now, or check from context if available)
    const canCreate = true;
    const canEdit = true;
    const canDelete = true;

    // ── Modal states ──────────────────────────────────────────────────────────
    const [showSubmissionModal, setShowSubmissionModal] = useState(false);
    const [showAIModal, setShowAIModal] = useState(false);
    const [showViewModal, setShowViewModal] = useState(false);
    const [selectedSubmission, setSelectedSubmission] = useState(null);

    // ── Filter states ─────────────────────────────────────────────────────────
    const [showFilterModal, setShowFilterModal] = useState(false);
    const [filters, setFilters] = useState({ search: "", status: "" });
    const [activeFilters, setActiveFilters] = useState({ search: "", status: "" });
    const [savedPresets, setSavedPresets] = useState([]);

    // ── Data fetch ────────────────────────────────────────────────────────────
    useEffect(() => {
        fetchSubmissions();
        fetchCompanies({ page_size: 1000 });
        fetchRanks();
    }, [fetchSubmissions, fetchCompanies, fetchRanks]);

    const handleRefresh = useCallback(() => {
        fetchSubmissions({ ...activeFilters });
    }, [fetchSubmissions, activeFilters]);

    // ── CRUD handlers ─────────────────────────────────────────────────────────
    const handleAddManual = useCallback(() => {
        if (!canCreate) { notify.error("You do not have permission to add applicants"); return; }
        setSelectedSubmission(null);
        setShowSubmissionModal(true);
    }, [canCreate, notify]);

    const handleAddAI = useCallback(() => {
        if (!canCreate) { notify.error("You do not have permission to upload CVs"); return; }
        setShowAIModal(true);
    }, [canCreate, notify]);

    const handleEdit = useCallback((row) => {
        if (!canEdit) { notify.error("You do not have permission to edit applicants"); return; }
        const submission = backendSubmissions.find((s) => s.id === row.id);
        if (submission) {
            setSelectedSubmission(submission);
            setShowSubmissionModal(true);
        }
        else notify.error("Submission data not found");
    }, [backendSubmissions, canEdit, notify]);

    const handleView = useCallback((row) => {
        const submission = backendSubmissions.find((s) => s.id === row.id);
        if (submission) {
            setSelectedSubmission(submission);
            setShowViewModal(true);
        }
        else notify.error("Submission data not found");
    }, [backendSubmissions, notify]);

    const handleDelete = useCallback(async (id) => {
        if (!canDelete) { notify.error("You do not have permission to delete applicants"); return; }
        if (window.confirm("Are you sure you want to delete this submission?")) {
            const result = await deleteSubmission(id);
            if (result.success) handleRefresh();
        }
    }, [canDelete, deleteSubmission, handleRefresh, notify]);

    const handleStatusChange = useCallback(async (id, newStatus) => {
        const result = await updateStatus(id, newStatus);
        if (result.success) {
            handleRefresh();
        }
    }, [updateStatus, handleRefresh]);

    const handleSaveSubmission = async (data) => {
        if (selectedSubmission) {
            await updateSubmission(selectedSubmission.id, data);
        } else {
            await createSubmission(data);
        }
        setShowSubmissionModal(false);
        handleRefresh();
    };

    const handleAISuccess = () => {
        notify.success("CV processed and saved successfully");
        handleRefresh();
    };

    // ── Data transform (per field reference) ──────────────────────────────────
    const userData = useMemo(() => {
        return backendSubmissions.map((submission) => {
            const state = mapStatusToState(submission.status);

            // Lookup names from reference lists
            const companyObj = companies.find(c => c.id === submission.company);
            const rankObj = ranks.find(r => r.id === submission.position);

            return {
                id: submission.id,
                name: `${submission.user_name.split(" ")[0]} ${submission.user_name.split(" ")[1]}` || "—",
                generatedId: submission.generated_id || "—",
                company: submission.company_name || companyObj?.company_name || (submission.company ? `ID: ${submission.company}` : "—"),
                position: submission.position_name || rankObj?.rank_name || rankObj?.name || (submission.position ? `ID: ${submission.position}` : "—"),
                codedRank: submission.coded_rank?.length
                    ? submission.coded_rank.map((r) => r.assigned_code || r.rank_code || "").filter(Boolean).join(", ")
                    : "—",
                experience:
                    submission.experience_years !== undefined && submission.experience_years !== null
                        ? `${submission.experience_years} yr${submission.experience_years !== 1 ? "s" : ""}`
                        : "—",
                salary: submission.salary || "—",
                state,
                date: submission.submitted_date
                    ? new Date(submission.submitted_date).toLocaleDateString("en-GB")
                    : "—",
                avatar: ASSETS.LOGO,
                _original: submission,
            };
        });
    }, [backendSubmissions, companies, ranks]);

    // ── Statistics (full pipeline) ────────────────────────────────────────────
    const statisticsData = useMemo(() => {
        const counts = userData.reduce((acc, item) => {
            acc[item.state] = (acc[item.state] || 0) + 1;
            return acc;
        }, {});

        return STATUS_PIPELINE.map((status, i) => {
            const count = counts[status] || 0;
            const COLORS = ["#A2A2A2", "#F59E0B", "#8B5CF6", "#3B82F6", "#0065AF", "#52C93F", "#E74C3C"];
            return {
                key: status.toLowerCase().replace(/\s+/g, "_"),
                label: `${status} (${count})`,
                value: count,
                color: COLORS[i],
            };
        });
    }, [userData]);

    // ── Table columns (matching "In List" fields) ─────────────────────────────
    const columns = useMemo(() => [
        {
            key: "name",
            title: "Name",
            width: 300,
            showAvatar: true,
            sortable: true,
            render: (val) => val,
        },
        {
            key: "generatedId",
            title: "ID",
            width: 200,
            sortable: false,
            render: (val) => val,
        },
        {
            key: "company",
            title: "Company",
            width: 300,
            sortable: true,
            render: (val) => val,
        },
        {
            key: "position",
            title: "Position",
            width: 300,
            sortable: true,
            render: (val) => val.split("/").length > 3 ? `${val.split("/")[0]} / ${val.split("/")[1]} / ${val.split("/")[2]} / ...` : val,
        },
        {
            key: "codedRank",
            title: "Rank Code",
            width: 200,
            sortable: false,
            render: (val) => val,
        },
        {
            key: "experience",
            title: "Experience",
            width: 95,
            sortable: true,
            render: (val) => val,
        },
        {
            key: "salary",
            title: "Salary",
            width: 120,
            sortable: true,
            render: (val) => val,
        },
        {
            key: "state",
            title: "Status",
            width: 130,
            isStatus: true,
            headerAlign: "center",
            headerTextAlign: "center",
            sortable: true,
            render: (val, row) => (
                <select
                    value={val}
                    onChange={(e) => handleStatusChange(row.id, e.target.value)}
                    onClick={(e) => e.stopPropagation()}
                    style={{
                        background: "transparent",
                        border: "none",
                        color: "inherit",
                        fontSize: "inherit",
                        fontFamily: "inherit",
                        fontWeight: "inherit",
                        cursor: "pointer",
                        width: "100%",
                        textAlign: "center",
                        appearance: "none",
                    }}
                >
                    {STATUS_PIPELINE.map((s) => (
                        <option key={s} value={s}>{s}</option>
                    ))}
                </select>
            ),
        },
        {
            key: "actions",
            title: "Actions",
            width: 130,
            isActions: true,
            onUser: handleView,
            onEdit: canEdit ? handleEdit : undefined,
            onDelete: canDelete ? handleDelete : undefined,
        },
    ], [canEdit, canDelete, handleView, handleEdit, handleDelete, handleStatusChange]);

    // ── Filter handlers ───────────────────────────────────────────────────────
    const handleApplyFilters = useCallback(() => {
        setActiveFilters({ ...filters });
        setShowFilterModal(false);
        fetchSubmissions({ ...filters, page: 1 });
    }, [filters, fetchSubmissions]);

    const handleResetFilters = useCallback(() => {
        const empty = { search: "", status: "" };
        setFilters(empty);
        setActiveFilters(empty);
        setShowFilterModal(false);
        fetchSubmissions({ page: 1 });
    }, [fetchSubmissions]);

    // ── Saved preset handlers ─────────────────────────────────────────────────
    const handleApplyPreset = useCallback((preset) => {
        setFilters(preset);
        setActiveFilters(preset);
        fetchSubmissions({ ...preset, page: 1 });
    }, [fetchSubmissions]);

    const handleSavePreset = useCallback((name, vals) => setSavedPresets((p) => [...p, { name, filters: vals }]), []);
    const handleDeletePreset = useCallback((name) => setSavedPresets((p) => p.filter((x) => x.name !== name)), []);

    // ── Export handlers ───────────────────────────────────────────────────────
    const handleExportExcel = useCallback(() => {
        try {
            const out = userData.map(({ avatar, _original, ...rest }) => rest);
            exportToExcel(out, `CVSubmissions_${new Date().toISOString().split("T")[0]}.xlsx`, "CV Submissions");
            notify.success("Exported to Excel!");
        } catch { notify.error("Failed to export"); }
    }, [userData, notify]);

    const handleExportJSON = useCallback(() => {
        try {
            const out = userData.map(({ avatar, _original, ...rest }) => rest);
            exportToJSON(out, `CVSubmissions_${new Date().toISOString().split("T")[0]}.json`);
            notify.success("Exported to JSON!");
        } catch { notify.error("Failed to export"); }
    }, [userData, notify]);

    // ── Filter field config (full status pipeline) ────────────────────────────
    const filterFields = [
        {
            key: "search",
            label: "Search",
            type: "text",
            placeholder: "Search by name or email…",
        },
        {
            key: "status",
            label: "Application Status",
            type: "select",
            placeholder: "All Statuses",
            options: STATUS_PIPELINE.map(s => ({ value: s, label: `⬤ ${s}` })),
        },
    ];


    const headerHeight = Math.round(101 * scale);

    return (
        <main style={getMainContainerStyles(scale, headerHeight)}>
            <style>{generateAllPageStyles(scale)}</style>

            {/* ── Statistics Card ──────────────────────────────────────────── */}
            <div style={{ marginBottom: `${Math.round(32 * scale)}px` }}>
                <StatisticsCard
                    title="CV Submissions"
                    timeframeLabel="All time"
                    segments={statisticsData}
                    width={680}
                    height={280}
                    scale={scale}
                    loading={loading}
                    style={{
                        height: "auto",
                        minHeight: Math.round(280 * scale),
                    }}
                />
            </div>

            {/* ── Title + Toolbar ──────────────────────────────────────────── */}
            <div style={getRowBetweenStyles(scale)}>
                <h1
                    style={{
                        ...getPageTitleStyles(scale),
                        marginBottom: `${Math.round(8 * scale)}px`,
                    }}
                >
                    Manage seafarer applicants
                </h1>

                {/* Saved Filter Presets */}
                <SavedFilters
                    scale={scale}
                    savedPresets={savedPresets}
                    currentFilters={activeFilters}
                    onApplyPreset={handleApplyPreset}
                    onSavePreset={handleSavePreset}
                    onDeletePreset={handleDeletePreset}
                />

                {/* Action toolbar */}
                <div
                    style={{
                        display: "flex",
                        alignItems: "center",
                        gap: `${Math.round(8 * scale)}px`,
                        marginTop: `${Math.round(20 * scale)}px`,
                        flexWrap: "wrap",
                    }}
                >
                    {/* Filter icon */}
                    <Button
                        variant="icon"
                        onClick={() => setShowFilterModal(true)}
                        ariaLabel="Filter applicants"
                        title="Filter applicants"
                        scale={scale}
                        style={{ width: 30, height: 30, borderRadius: 8, minHeight: 30 }}
                    >
                        <svg width={16} height={16} viewBox="0 0 24 24" fill="none">
                            <path d="M3 6h18M6 12h12M9 18h6" stroke="#1E1E1E" strokeWidth="1.5" strokeLinecap="round" />
                        </svg>
                    </Button>

                    {/* Refresh */}
                    <Button variant="outline" scale={scale} onClick={handleRefresh} style={thinBtn}>
                        Refresh
                    </Button>

                    {/* Add Applicant (Admin only) */}
                    {canCreate && (
                        <Button variant="primary" scale={scale} onClick={handleAddManual} style={thinBtn}>
                            + Add Applicant
                        </Button>
                    )}

                    {/* Export — shown only when data exists */}
                    {userData.length > 0 && (
                        <>
                            <Button variant="outline" onClick={handleExportExcel} scale={scale} style={thinBtn}>
                                Export Excel
                            </Button>
                            <Button variant="outline" onClick={handleExportJSON} scale={scale} style={thinBtn}>
                                Export JSON
                            </Button>
                        </>
                    )}
                </div>
            </div>

            {/* ── Data Table ───────────────────────────────────────────────── */}
            <div
                style={{
                    marginTop: `${Math.round(20 * scale)}px`,
                    marginBottom: `${Math.round(20 * scale)}px`,
                }}
            >
                <RefinedDataTable
                    data={userData}
                    columns={columns}
                    rowKey="id"
                    scale={scale}
                    pageSize={pagination.pageSize || 25}
                    loading={loading}
                    initialPage={pagination.currentPage}
                    onPageChange={(p) => fetchSubmissions({ page: p, ...activeFilters })}
                    totalRecords={pagination.count}
                    actions={["User", canEdit && "Edit", canDelete && "Delete"].filter(Boolean)}
                    onRowClick={handleView}
                    styleOverrides={{ columnGap: 9 }}
                />
            </div>

            {/* ── Footer CTA — AI upload + manual (Admin only) ─────────────── */}
            {/* {canCreate && (
                <div
                    style={{
                        display: "flex",
                        justifyContent: "center",
                        gap: `${Math.round(16 * scale)}px`,
                        marginTop: `${Math.round(32 * scale)}px`,
                        padding: `${Math.round(16 * scale)}px`,
                        borderTop: "1px solid #E5E7EB",
                    }}
                >
                    <Button
                        variant="primary"
                        scale={scale}
                        onClick={handleAddAI}
                        style={{
                            ...thinBtn,
                            minHeight: 36,
                            height: 36,
                            padding: "0 28px",
                            fontSize: 14,
                            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                            border: "none",
                            boxShadow: "0 3px 10px rgba(102, 126, 234, 0.35)",
                        }}
                    >
                        🤖 AI Upload CV
                    </Button>

                    <Button
                        variant="outline"
                        scale={scale}
                        onClick={handleAddManual}
                        style={{
                            ...thinBtn,
                            minHeight: 36,
                            height: 36,
                            padding: "0 28px",
                            fontSize: 14,
                            borderColor: "#667eea",
                            color: "#667eea",
                        }}
                    >
                        Add Manual CV
                    </Button>
                </div>
            )} */}

            {/* ── Modals ───────────────────────────────────────────────────── */}
            {showSubmissionModal && (
                <CVSubmissionFormModal
                    submission={selectedSubmission}
                    onClose={() => setShowSubmissionModal(false)}
                    onSave={handleSaveSubmission}
                    scale={scale}
                />
            )}

            {showAIModal && (
                <DocumentUploadModal
                    isOpen={showAIModal}
                    onClose={() => setShowAIModal(false)}
                    onSuccess={handleAISuccess}
                    scale={scale}
                />
            )}

            {showViewModal && (
                <CVSubmissionViewModal
                    isOpen={showViewModal}
                    onClose={() => setShowViewModal(false)}
                    submission={selectedSubmission}
                    onDelete={handleDelete}
                    scale={scale}
                />
            )}

            {/* Enhanced Filter Modal */}
            <EnhancedFilterModel
                isOpen={showFilterModal}
                onClose={() => setShowFilterModal(false)}
                title="Filter CV Submissions"
                fields={filterFields}
                values={filters}
                onValuesChange={setFilters}
                onApply={handleApplyFilters}
                onReset={handleResetFilters}
                scale={scale}
            />
        </main>
    );
}
