/* eslint-disable no-unused-vars */
// Content/Documents.jsx - REFINED VERSION MATCHING UI DESIGN
import React, { useState, useMemo, useCallback, useEffect } from "react";
import { Bell, Eye, Upload, Download, Pencil, Trash2 } from "lucide-react";
import { StackedProgressLegendCard } from "../Components/Cards/StatisticsCards";
import DocumentCard from "../Components/Cards/DocumentCard";
import {
  getExpiryMessage,
  formatDateLocal,
  COLORS,
  TOKENS,
} from "../Constants";
import { exportToExcel, exportToJSON } from "../../../utils/exportHelpers";

import {
  generateAllPageStyles,
  getMainContainerStyles,
  getPageTitleStyles,
  getRowBetweenStyles,
} from "../Styles/cssClasses";
import Button from "../Components/Common/Button";
import ConfirmDialog from "../Components/Common/ConfirmDialog";
import DocumentFormModal from "../Components/Modal/DocumentsFormModal";
import EnhancedFilterModel from "../Components/Common/EnhancedFilterModel";
import { ContractViewModal } from "../Components/Modal/ViewModal";
import SavedFilters from "../Components/Common/SavedFilters";
import Pagination from "../../common/Pagination";
// import useTableFilters from "../hooks/useTableFilters"; // ❌ Remove
import useNotification from "../hooks/useNotification";

import useDocuments from "../../../hooks/dashboard/useDocuments";
import usePermissions from "../../../hooks/dashboard/usePermissions";

export function DocumentManagement({ scale = 1, isMobile = false }) {
  const { notify } = useNotification();
  const { canCreate, canEdit, canDelete } = usePermissions();
  const {
    contracts: backendContracts,
    loading,
    fetchContracts,
    createContract,
    updateContract,
    deleteContract,
    getLocalStats,
    pagination,
    canManageContracts,
  } = useDocuments();

  // Fetch contracts on mount
  useEffect(() => {
    fetchContracts();
    // console.log("the contracts  : ", contracts);
  }, []);

  // Calculate statistics matching UI design
  // const stats = useMemo(() => getLocalStats(), [getLocalStats]);
  const stats = useMemo(() => {
    const data = getLocalStats();
    // {active, cancelled, critical, draft, expired, notice, pending, signed, warning, total}
    // console.log("the data : ", data);
    return data;
  }, [getLocalStats]);

  // ✅ Local state for filters
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [filters, setFilters] = useState({
    search: "",
    status: "",
    expiry_status: "", // Mapping UI "Expiry Status" to backend filters might need logic or just status
  });
  const [activeFilters, setActiveFilters] = useState({
    search: "",
    status: "",
    expiry_status: "",
  });

  // ✅ Saved Filters state
  const [savedPresets, setSavedPresets] = useState([]);

  // ✅ Backend Pagination from useDocuments
  // Modal states
  const [showContractModal, setShowContractModal] = useState(false);
  const [selectedContract, setSelectedContract] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [contractToDelete, setContractToDelete] = useState(null);

  // View modal state
  const [showViewModal, setShowViewModal] = useState(false);
  const [viewingContract, setViewingContract] = useState(null);

  const contracts = useMemo(() => {
    return backendContracts.map((contract) => ({
      id: contract.id,
      userId: contract.user,
      user: contract.user_name,
      ship: contract.ship_name,
      signOffDate: contract.sign_off_date,
      signOnDate: contract.sign_on_date,
      daysToExpiry: contract.daysToExpiry,
      duration: contract.duration,
      expiryCategory: contract.expiryCategory,
      startDate: contract.start_date,
      endDate: contract.end_date,
      status: contract.status,
      createdAt: contract.created_at,
      updatedAt: contract.updated_at,
      _original: contract, // {contracts data fields : id, ship_name, user, user_name, status, sign_off_date, sign_on_date daysToExpiry, duration, expiryCategory, }
    }));
  }, [backendContracts]);
  // Filter contracts by category
  const activeContracts = useMemo(
    () =>
      contracts.filter((c) =>
        ["Signed", "Pending Signature", "Draft"].includes(c.status)
      ),
    [contracts]
  );

  const expiredContracts = useMemo(
    () => contracts.filter((c) => ["Expired", "Cancelled"].includes(c.status)),
    [contracts]
  );

  // ✅ Filter Handlers
  const handleApplyFilters = useCallback(() => {
    // console.log("Applying filters:", filters);
    setActiveFilters(filters);
    setShowFilterModal(false);
    fetchContracts({ ...filters, page: 1 });
  }, [filters, fetchContracts]);

  const handleResetFilters = useCallback(() => {
    const emptyFilters = { search: "", status: "", expiry_status: "" };
    setFilters(emptyFilters);
    setActiveFilters(emptyFilters);
    setShowFilterModal(false);
    fetchContracts({ page: 1 });
  }, [fetchContracts]);

  const handlePageChange = useCallback(
    (newPage) => {
      fetchContracts({ ...activeFilters, page: newPage });
    },
    [fetchContracts, activeFilters]
  );

  // ✅ Saved Presets Handlers
  const handleApplyPreset = useCallback(
    (preset) => {
      setFilters(preset);
      setActiveFilters(preset);
      fetchContracts({ ...preset, page: 1 });
    },
    [fetchContracts]
  );

  const handleSavePreset = useCallback((name, filterValues) => {
    setSavedPresets((prev) => [...prev, { name, filters: filterValues }]);
  }, []);

  const handleDeletePreset = useCallback((name) => {
    setSavedPresets((prev) => prev.filter((p) => p.name !== name));
  }, []);

  // Filter Fields Configuration
  const filterFields = [
    {
      key: "status",
      label: "Contract Status",
      type: "multi-select",
      placeholder: "All Statuses",
      options: [
        { value: "Signed", label: "Signed" },
        { value: "Pending Signature", label: "PendingSignature" },
        { value: "Draft", label: "Draft" },
        { value: "Expired", label: "Expired" },
        { value: "Cancelled", label: "Cancelled" },
      ],
    },
    {
      key: "expiry_status",
      label: "Expiry Status",
      type: "select",
      placeholder: "All Expiry Statuses",
      options: [
        { value: "active", label: "Active" },
        { value: "warning", label: "Warning (< 30 days)" },
        { value: "critical", label: "Critical (< 7 days)" },
        { value: "expired", label: "Expired" },
      ],
    },
  ];

  // Export handlers
  const handleExportExcel = useCallback(() => {
    try {
      const dataToExport = contracts.map(
        ({ id, avatar, _original, ...rest }) => rest
      );
      exportToExcel(
        dataToExport,
        `Contracts_Export_${new Date().toISOString().split("T")[0]}.xlsx`,
        "Contracts"
      );
      notify.success("Contracts exported to Excel!");
    } catch (error) {
      notify.error("Failed to export");
    }
  }, [contracts, notify]);

  const handleExportJSON = useCallback(() => {
    try {
      const dataToExport = contracts.map(
        ({ _original, ...rest }) => rest
      );
      exportToJSON(
        dataToExport,
        `Contracts_Export_${new Date().toISOString().split("T")[0]}.json`
      );
      notify.success("Contracts exported to JSON!");
    } catch (error) {
      notify.error("Failed to export");
    }
  }, [contracts, notify]);

  // Statistics for progress card - MATCHING UI DESIGN EXACTLY
  const documentSegments = useMemo(() => {
    const total = stats.total || 1; // Prevent division by zero
    return [
      {
        key: "signed",
        color: "#C1D5E8",
        pct: (stats.signed / total) * 100,
      },
      {
        key: "pending",
        color: "#EAEBC3",
        pct: (stats.pending / total) * 100,
      },
      {
        key: "draft",
        color: "#CDEBC3",
        pct: (stats.draft / total) * 100,
      },
      {
        key: "critical",
        color: "#F7CCBD",
        pct: (stats.critical / total) * 100,
      },
      {
        key: "warning",
        color: "#FDFECF",
        pct: (stats.warning / total) * 100,
      },
      {
        key: "notice",
        color: "#E5E7EB",
        pct: (stats.notice / total) * 100,
      },
    ];
  }, [stats]);

  const documentRows = useMemo(() => {
    return [
      {
        key: "signed",
        color: "#C1D5E8",
        label: "Signed Contracts",
        remaining: `${stats.signed}`,
      },
      {
        key: "pending",
        color: "#EAEBC3",
        label: "Pending Signature",
        remaining: `${stats.pending}`,
      },
      {
        key: "draft",
        color: "#CDEBC3",
        label: "Drafts",
        remaining: `${stats.draft}`,
      },
      {
        key: "critical",
        color: "#F7CCBD",
        label: "Critical (≤7 days)",
        remaining: `${stats.critical}`,
      },
      {
        key: "warning",
        color: "#FDFECF",
        label: "Warning (≤30 days)",
        remaining: `${stats.warning}`,
      },
      {
        key: "notice",
        color: "#E5E7EB",
        label: "Notice (≤60 days)",
        remaining: `${stats.notice}`,
      },
    ];
  }, [stats]);

  // ============================================
  // ACTION HANDLERS
  // ============================================

  const handleView = useCallback(
    (contract) => {
      setViewingContract(contract);
      setShowViewModal(true);
    },
    []
  );

  const handleEdit = useCallback(
    (contract) => {
      if (!canEdit) {
        notify.error("You don't have permission to edit contracts");
        return;
      }
      // Pass the raw backend record so populateFormData reads the correct field names
      setSelectedContract(contract._original || contract);
      setShowContractModal(true);
    },
    [canEdit, notify]
  );

  const handleDeleteClick = useCallback(
    (contract) => {
      if (!canDelete) {
        notify.error("You don't have permission to delete contracts");
        return;
      }
      setContractToDelete(contract);
      setShowDeleteConfirm(true);
    },
    [canDelete, notify]
  );

  const handleConfirmDelete = useCallback(async () => {
    if (!contractToDelete) return;

    const result = await deleteContract(contractToDelete.id);

    if (result.success) {
      setShowDeleteConfirm(false);
      setContractToDelete(null);
    }
  }, [contractToDelete, deleteContract]);

  const handleAlert = useCallback(
    (contract) => {
      // TODO: Implement alert/notification functionality
      notify.info("Alert functionality coming soon");
    },
    [notify]
  );

  const handleUpload = useCallback(
    (contract) => {
      // TODO: Implement document upload functionality
      notify.info("Upload functionality coming soon");
    },
    [notify]
  );

  const handleDownload = useCallback(
    (contract) => {
      // TODO: Implement contract document download
      notify.info("Download functionality coming soon");
    },
    [notify]
  );

  const handleCreateContract = useCallback(
    async (contractData) => {
      const result = await createContract(contractData);

      if (result.success) {
        setShowContractModal(false);
        setSelectedContract(null);
      }
    },
    [createContract]
  );

  const handleUpdateContract = useCallback(
    async (contractData) => {
      if (!selectedContract) return;

      const result = await updateContract(selectedContract.id, contractData);

      if (result.success) {
        setShowContractModal(false);
        setSelectedContract(null);
      }
    },
    [selectedContract, updateContract]
  );

  const handleSaveContract = useCallback(
    async (contractData) => {
      if (selectedContract) {
        await handleUpdateContract(contractData);
      } else {
        await handleCreateContract(contractData);
      }
    },
    [selectedContract, handleCreateContract, handleUpdateContract]
  );





  const headerHeight = Math.round(101 * scale);

  return (
    <main
      style={{
        ...getMainContainerStyles(scale, headerHeight),
        fontFamily: "Poppins, sans-serif",
      }}
    >
      <style>{generateAllPageStyles(scale)}</style>

      {/* Header with Filter */}
      <div style={getRowBetweenStyles(scale)}>
        <h2
          style={{
            ...getPageTitleStyles(scale),
            margin: 0,
            letterSpacing: "1px",
          }}
        >
          Contract Management & Document Monitoring
        </h2>

        <div
          style={{
            display: "flex",
            gap: `${Math.round(12 * scale)}px`,
          }}
        >
          <Button
            variant="icon"
            scale={scale}
            onClick={() => setShowFilterModal(true)}
            ariaLabel="Filter documents"
            title="Filter documents"
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
        </div>
      </div>

      {/* Statistics Card - Matching UI Design */}
      <div
        style={{
          marginTop: `${Math.round(24 * scale)}px`,
          marginBottom: `${Math.round(32 * scale)}px`,
          width: "100%",
          maxWidth: `${Math.round(1098.54 * scale)}px`,
        }}
      >
        <StackedProgressLegendCard
          segments={documentSegments}
          rows={documentRows}
          width={1098.54}
          height={412.39}
          scale={scale}
        />
      </div>

      {/* Loading State */}
      {loading && (
        <div
          style={{
            backgroundColor: COLORS.white,
            borderRadius: `${Math.round(22 * scale)}px`,
            padding: `${Math.round(40 * scale)}px`,
            boxShadow: TOKENS.shadow.sm,
            textAlign: "center",
            marginBottom: `${Math.round(32 * scale)}px`,
          }}
        >
          <div
            style={{
              fontSize: `${Math.round(18 * scale)}px`,
              color: COLORS.lightText,
            }}
          >
            Loading contracts...
          </div>
        </div>
      )}

      {/* Document Cards List */}
      {!loading && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: `${Math.round(16 * scale)}px`,
            marginBottom: `${Math.round(32 * scale)}px`,
          }}
        >
          {contracts.length > 0 ? (
            contracts.map((contract) => (
              <DocumentCard // Use contracts instead of filteredDocuments
                key={contract.id}
                document={contract}
                scale={scale}
                onView={() => handleView(contract)}
                onEdit={() => handleEdit(contract)}
                onDelete={() => handleDeleteClick(contract)}
                onAlert={() => handleAlert(contract)}
                onUpload={() => handleUpload(contract)}
                onDownload={() => handleDownload(contract)}
              />
            ))
          ) : (
            <div
              style={{
                backgroundColor: COLORS.white,
                borderRadius: `${Math.round(22 * scale)}px`,
                padding: `${Math.round(60 * scale)}px`,
                boxShadow: TOKENS.shadow.sm,
                textAlign: "center",
              }}
            >
              <div
                style={{
                  fontSize: `${Math.round(48 * scale)}px`,
                  marginBottom: `${Math.round(20 * scale)}px`,
                }}
              >
                📄
              </div>
              <h3
                style={{
                  fontSize: `${Math.round(24 * scale)}px`,
                  fontWeight: 600,
                  color: COLORS.darkText,
                  margin: 0,
                  marginBottom: `${Math.round(12 * scale)}px`,
                  fontFamily: "Poppins, sans-serif",
                }}
              >
                No Contracts Found
              </h3>
              <p
                style={{
                  fontSize: `${Math.round(14 * scale)}px`,
                  color: COLORS.lightText,
                  margin: 0,
                  maxWidth: "300px",
                  marginLeft: "auto",
                  marginRight: "auto",
                }}
              >
                {filters.status
                  ? "No contracts match the selected filter"
                  : "Generate your first contract to get started"}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Action Buttons Row */}
      {!loading && (
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            gap: `${Math.round(14 * scale)}px`,
            marginTop: `${Math.round(20 * scale)}px`,
          }}
        >
          {canCreate && (
            <Button
              variant="primary"
              onClick={() => {
                setSelectedContract(null);
                setShowContractModal(true);
              }}
              scale={scale}
            >
              Generate Contract
            </Button>
          )}

          {contracts.length > 0 && (
            <Button variant="outline" onClick={handleExportExcel} scale={scale}>
              Export Excel
            </Button>
          )}

        </div>
      )}

      {/* Pagination */}
      {!loading && contracts.length > 0 && (
        <div style={{ marginTop: `${Math.round(20 * scale)}px` }}>
          <Pagination
            page={pagination?.currentPage || 1}
            pageSize={25}
            total={pagination?.count || 0}
            onChange={handlePageChange}
            scale={scale}
            showInfo={true}
          />
        </div>
      )}

      {/* Modals */}
      {showContractModal && (
        <DocumentFormModal
          contract={selectedContract}
          onClose={() => {
            setShowContractModal(false);
            setSelectedContract(null);
          }}
          onSave={handleSaveContract}
          scale={scale}
        />
      )}

      {showFilterModal && (
        <EnhancedFilterModel
          isOpen={showFilterModal}
          onClose={() => setShowFilterModal(false)}
          values={filters}
          onValuesChange={setFilters}
          onApply={handleApplyFilters}
          onReset={handleResetFilters}
          fields={filterFields}
          scale={scale}
          title="Filter Contracts"
        />
      )}

      {/* Contract View Modal */}
      <ContractViewModal
        isOpen={showViewModal}
        onClose={() => {
          setShowViewModal(false);
          setViewingContract(null);
        }}
        contract={viewingContract?._original || viewingContract}
        onDelete={(id) => {
          setShowViewModal(false);
          setViewingContract(null);
          handleDeleteClick({ id });
        }}
        scale={scale}
        canDelete={canDelete}
      />

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        onClose={() => {
          setShowDeleteConfirm(false);
          setContractToDelete(null);
        }}
        onConfirm={handleConfirmDelete}
        title="Delete Contract"
        message={`Are you sure you want to delete the contract for ${contractToDelete?.user?.first_name || "this user"
          }? This action cannot be undone.`}
        confirmLabel="Delete"
        variant="danger"
        scale={scale}
        loading={loading}
      />
    </main>
  );
}
