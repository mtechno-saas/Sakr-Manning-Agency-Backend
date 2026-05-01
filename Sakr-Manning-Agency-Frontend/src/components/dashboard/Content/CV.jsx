/* eslint-disable no-unused-vars */

// Content/CV.jsx - CVs Management using /api/documents/ endpoint
import React, { useState, useEffect, useMemo, useCallback } from "react";
import {
  exportToExcel,
  exportToJSON,
} from "../../../utils/exportHelpers";
import {
  generateAllPageStyles,
  getMainContainerStyles,
  getPageTitleStyles,
  getRowBetweenStyles,
} from "../Styles/cssClasses";
import Button from "../Components/Common/Button";
import EnhancedFilterModel from "../Components/Common/EnhancedFilterModel";
import SavedFilters from "../Components/Common/SavedFilters";
import { StatisticsCard } from "../Components/Cards/StatisticsCards";
import { RefinedDataTable } from "../Components/Data/RefinedDataTable";
import Pagination from "../../common/Pagination";

import useNotification from "../hooks/useNotification";
import usePermissions from "../../../hooks/dashboard/usePermissions";
import useCVDocuments from "../../../hooks/dashboard/useCVDocuments";
import CVFormModal from "../Components/Modal/CVFormModal";
import CVViewModal from "../Components/Modal/ViewModal/CVViewModal";

export function CVManagement({ scale = 1, isMobile = false }) {
  const { notify } = useNotification();
  const { canCreate, canEdit, canDelete } = usePermissions();

  const {
    documents,
    loading,
    pagination,
    fetchDocuments,
    setDocumentStatus,
    downloadDocument,
    createDocument,
    updateDocument,
    deleteDocument,
  } = useCVDocuments();

  // Modal state
  const [showCVModal, setShowCVModal] = useState(false);
  const [selectedCV, setSelectedCV] = useState(null);
  const [showViewModal, setShowViewModal] = useState(false);
  const [viewingCV, setViewingCV] = useState(null);

  // Local state
  const [savedPresets, setSavedPresets] = useState([]);

  // Filter state
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [filters, setFilters] = useState({
    search: "",
    status: "",
  });
  const [activeFilters, setActiveFilters] = useState({
    search: "",
    status: "",
  });

  const hasActiveFilters = activeFilters.search || activeFilters.status;

  // Load documents on mount
  useEffect(() => {
    fetchDocuments({ page: 1 });
  }, []);

  // Handle page change (server-side pagination)
  const handlePageChange = useCallback(
    (newPage) => {
      if (!hasActiveFilters) {
        fetchDocuments({ page: newPage });
      }
    },
    [fetchDocuments, hasActiveFilters]
  );

  // ── Transform API response into table rows ──
  const cvData = useMemo(() => {
    return documents.map((doc) => ({
      id: doc.id,
      name: doc.name || "—",
      generated_id: doc.generated_id || "—",
      email: doc.email || "—",
      phone: doc.phone_number || "—",
      position: doc.position || "—",
      file: doc.file || null,
      fileLabel: doc.file ? doc.file.split("/").pop().split("_").pop() : "No file",
      date: doc.created_at
        ? new Date(doc.created_at).toLocaleDateString("en-GB")   // DD/MM/YYYY
        : "—",
      status: doc.status || "Pending",
      // keep raw for downloads / actions
      _raw: doc,
    }));
  }, [documents]);

  // ── Statistics ──
  const statisticsData = useMemo(() => {
    const counts = cvData.reduce(
      (acc, item) => {
        const s = item.status;
        acc[s] = (acc[s] || 0) + 1;
        acc.total += 1;
        return acc;
      },
      { total: 0 }
    );

    return [
      {
        key: "pending",
        label: "Pending",
        value: counts["Pending"] || 0,
        color: "#A2A2A2",
      },
      {
        key: "active",
        label: "Active",
        value: counts["Active"] || 0,
        color: "#52C93F",
      },
      {
        key: "blacklist",
        label: "Blacklist",
        value: counts["Blacklist"] || 0,
        color: "#E74C3C",
      },
    ];
  }, [cvData]);

  // ── CRUD Handlers ──
  const handleStatusChange = useCallback(async (id, newStatus) => {
    const result = await setDocumentStatus(id, newStatus);
    if (result.success) {
      // Reload is handled by hook's state update or manual refresh if needed
      fetchDocuments({ page: pagination.currentPage, ...activeFilters });
    }
  }, [setDocumentStatus, fetchDocuments, pagination.currentPage, activeFilters]);

  const handleView = useCallback(
    (row) => {
      const doc = row._raw || documents.find((d) => d.id === row.id);
      if (doc) {
        setViewingCV(doc);
        setShowViewModal(true);
      } else {
        notify.error("CV data not found");
      }
    },
    [documents, notify]
  );

  const handleDownload = useCallback(
    async (row) => {
      const doc = row._raw || documents.find((d) => d.id === row.id);
      if (doc?.file) {
        await downloadDocument(doc.id, doc.file.split("/").pop());
      } else {
        notify.error("No file available for download");
      }
    },
    [documents, downloadDocument, notify]
  );

  const handleAddCV = useCallback(() => {
    if (!canCreate) {
      notify.error("You do not have permission to add CVs");
      return;
    }
    setSelectedCV(null);
    setShowCVModal(true);
  }, [canCreate, notify]);

  const handleEditCV = useCallback(
    (row) => {
      if (!canEdit) {
        notify.error("You do not have permission to edit CVs");
        return;
      }
      // Find original document in the list
      const doc = documents.find((d) => d.id === row.id);
      if (doc) {
        setSelectedCV(doc);
        setShowCVModal(true);
      } else {
        notify.error("CV data not found");
      }
    },
    [canEdit, documents, notify]
  );

  const handleSaveCV = async (cvData) => {
    if (selectedCV) {
      // Update
      const result = await updateDocument(selectedCV.id, cvData);
      if (result.success) setShowCVModal(false);
    } else {
      // Create
      const result = await createDocument(cvData);
      if (result.success) setShowCVModal(false);
    }
  };

  const handleDelete = useCallback(
    async (id) => {
      if (!canDelete) {
        notify.error("You do not have permission to delete CVs");
        return;
      }
      if (window.confirm("Are you sure you want to delete this CV?")) {
        await deleteDocument(id);
      }
    },
    [canDelete, deleteDocument, notify]
  );

  // ── Table columns ──
  const columns = useMemo(
    () => [
      {
        key: "name",
        title: "Name",
        width: 360,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "generated_id",
        title: "ID",
        width: 200,
        sortable: false,
        render: (val) => val,
      },
      {
        key: "email",
        title: "Email",
        width: 400,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "phone",
        title: "Phone",
        width: 140,
        sortable: false,
        render: (value) => value,
      },
      {
        key: "position",
        title: "Position",
        width: 150,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "fileLabel",
        title: "Uploaded CV",
        width: 180,
        sortable: false,
        render: (value, row) => {
          if (!row.file) return "—";
          return (
            <span
              onClick={(e) => {
                e.stopPropagation();
                handleDownload(row);
              }}
              style={{
                color: "#3B82F6",
                textDecoration: "underline",
                cursor: "pointer",
                fontSize: "inherit",
              }}
            >
              {value}
            </span>
          );
        },
      },
      {
        key: "date",
        title: "Date",
        width: 110,
        sortable: true,
        sortValue: (row) => {
          const doc = row._raw;
          return doc?.created_at || "";
        },
        render: (value) => value,
      },
      {
        key: "status",
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
            {["Pending", "Active", "Blacklist"].map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        ),
      },
      {
        key: "actions",
        title: "Actions",
        width: 140,
        isActions: true,
        onUser: handleView,
        onEdit: canEdit ? handleEditCV : undefined,
        onDownload: handleDownload,
        onDelete: canDelete ? handleDelete : undefined,
      },
    ],
    [canDelete, canEdit, handleDelete, handleDownload, handleEditCV, handleView, handleStatusChange]
  );

  // ── Filter handlers ──
  const handleApplyFilters = useCallback(() => {
    setActiveFilters({ ...filters });
    setShowFilterModal(false);

    const backendFilters = {};
    if (filters.search) backendFilters.search = filters.search;
    if (filters.status) backendFilters.status = filters.status;

    fetchDocuments({ ...backendFilters, page: 1 });
  }, [filters, fetchDocuments]);

  const handleResetFilters = useCallback(() => {
    const emptyFilters = { search: "", status: "" };
    setFilters(emptyFilters);
    setActiveFilters(emptyFilters);
    setShowFilterModal(false);
    fetchDocuments({ page: 1 });
  }, [fetchDocuments]);

  const filterFields = [
    {
      key: "search",
      label: "Search",
      type: "text",
      placeholder: "Search by name, email…",
    },
    {
      key: "status",
      label: "Status",
      type: "select",
      placeholder: "All Statuses",
      options: [
        { value: "Pending", label: "Pending" },
        { value: "Active", label: "Active" },
        { value: "Blacklist", label: "Blacklist" },
      ],
    },
  ];

  // ── Export handlers ──
  const handleExportExcel = useCallback(() => {
    try {
      const dataToExport = cvData.map(
        ({ id, _raw, file, ...rest }) => rest
      );
      exportToExcel(
        dataToExport,
        `CVs_Export_${new Date().toISOString().split("T")[0]}.xlsx`,
        "CVs"
      );
      notify.success("Data exported to Excel successfully!");
    } catch (error) {
      notify.error("Failed to export data");
      console.error("Export failed:", error);
    }
  }, [cvData, notify]);

  const handleExportJSON = useCallback(() => {
    try {
      const dataToExport = cvData.map(({ _raw, ...rest }) => rest);
      exportToJSON(
        dataToExport,
        `CVs_Export_${new Date().toISOString().split("T")[0]}.json`
      );
      notify.success("Data exported to JSON successfully!");
    } catch (error) {
      notify.error("Failed to export data");
      console.error(error);
    }
  }, [cvData, notify]);

  // ── Saved filters ──
  const handleApplyPreset = useCallback(
    (preset) => {
      setFilters(preset);
      setActiveFilters(preset);
      const backendFilters = {};
      if (preset.search) backendFilters.search = preset.search;
      if (preset.status) backendFilters.status = preset.status;
      fetchDocuments(backendFilters);
    },
    [fetchDocuments]
  );

  const handleSavePreset = useCallback((name, filterValues) => {
    setSavedPresets((prev) => [...prev, { name, filters: filterValues }]);
  }, []);

  const handleDeletePreset = useCallback((name) => {
    setSavedPresets((prev) => prev.filter((val) => val.name !== name));
  }, []);

  const headerHeight = Math.round(101 * scale);

  return (
    <main style={getMainContainerStyles(scale, headerHeight)}>
      <style>{generateAllPageStyles(scale)}</style>

      {/* Statistics Card */}
      <div style={{ marginBottom: `${Math.round(32 * scale)}px` }}>
        <StatisticsCard
          title="CVs"
          timeframeLabel="Total"
          segments={statisticsData}
          width={440}
          height={248}
          scale={scale}
          loading={loading}
        />
      </div>

      {/* Title and Actions Row */}
      <div style={getRowBetweenStyles(scale)}>
        <h1
          style={{
            ...getPageTitleStyles(scale),
            marginBottom: `${Math.round(8 * scale)}px`,
          }}
        >
          Manage and review submitted CVs
        </h1>

        <SavedFilters
          scale={scale}
          savedPresets={savedPresets}
          currentFilters={activeFilters}
          onApplyPreset={handleApplyPreset}
          onSavePreset={handleSavePreset}
          onDeletePreset={handleDeletePreset}
        />

        <Button
          variant="icon"
          onClick={() => setShowFilterModal(true)}
          ariaLabel="Filter CVs"
          title="Filter CVs"
          scale={scale}
        >
          <svg
            width={Math.round(21 * scale)}
            height={Math.round(21 * scale)}
            viewBox="0 0 24 24"
            fill="none"
          >
            <path
              d="M3 6h18M6 12h12M9 18h6"
              stroke="#1E1E1E"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
          </svg>
        </Button>

        {canCreate && (
          <Button
            variant="primary"
            onClick={handleAddCV}
            scale={scale}
            icon={
              <svg
                width={Math.round(18 * scale)}
                height={Math.round(18 * scale)}
                viewBox="0 0 24 24"
                fill="none"
              >
                <path
                  d="M12 5v14M5 12h14"
                  stroke="white"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
            }
          >
            Add CV
          </Button>
        )}
      </div>

      {/* Data Table */}
      <div style={{ marginBottom: `${Math.round(20 * scale)}px` }}>
        <RefinedDataTable
          data={cvData}
          columns={columns}
          rowKey="id"
          scale={scale}
          pageSize={pagination.pageSize}
          initialPage={1}
          actions={
            [
              "User",
              "Download",
              canEdit && "Edit",
              canDelete && "Delete"
            ].filter(Boolean)
          }
          onRowClick={(row) => handleView(row)}
          loading={loading}
        />

        {/* Server-side Pagination */}
        {/* {!hasActiveFilters && (
          <Pagination
            page={pagination.currentPage}
            pageSize={pagination.pageSize}
            total={pagination.count}
            onChange={handlePageChange}
            scale={scale}
            showInfo={true}
          />
        )} */}
      </div>

      {/* Action Buttons */}
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          gap: `${Math.round(12 * scale)}px`,
          justifyContent: "flex-end",
        }}
      >
        {cvData.length > 0 && (
          <div
            style={{
              display: "flex",
              gap: `${Math.round(12 * scale)}px`,
              justifyContent: "flex-end",
            }}
          >
            <Button variant="outline" onClick={handleExportExcel} scale={scale}>
              Export Excel
            </Button>
            <Button variant="outline" onClick={handleExportJSON} scale={scale}>
              Export JSON
            </Button>
          </div>
        )}
      </div>

      <CVFormModal
        isOpen={showCVModal}
        onClose={() => setShowCVModal(false)}
        cv={selectedCV}
        onSave={handleSaveCV}
        scale={scale}
      />

      {showViewModal && (
        <CVViewModal
          isOpen={showViewModal}
          onClose={() => { setShowViewModal(false); setViewingCV(null); }}
          cv={viewingCV}
          onDelete={(id) => {
            setShowViewModal(false);
            handleDelete(id);
          }}
          onDownload={handleDownload}
          scale={scale}
          canDelete={canDelete}
        />
      )}

      {/* Filter Modal */}
      <EnhancedFilterModel
        isOpen={showFilterModal}
        onClose={() => setShowFilterModal(false)}
        title="Filter CVs"
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
