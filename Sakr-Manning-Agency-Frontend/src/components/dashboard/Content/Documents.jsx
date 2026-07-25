/* eslint-disable no-unused-vars */
import React, { useState, useMemo, useCallback, useEffect, useRef } from "react";
import { Bell, Eye, Upload, Download, Pencil, Trash2, LayoutGrid, List, ChevronUp, ChevronDown } from "lucide-react";
import { StackedProgressLegendCard } from "../Components/Cards/StatisticsCards";
import DocumentCard from "../Components/Cards/DocumentCard";
import {
  getExpiryMessage,
  formatDateLocal,
  COLORS,
  TOKENS,
} from "../Constants";
import { exportToExcel, exportToJSON } from "../../../utils/exportHelpers";
import { generateStatPdfReport } from "../../../utils/pdfReportGenerator";
import { generateContractPdf } from "../../../utils/contractPdfGenerator";

import {
  generateAllPageStyles,
  getMainContainerStyles,
  getPageTitleStyles,
  getRowBetweenStyles,
} from "../Styles/cssClasses";
import Button from "../Components/Common/Button";
import ConfirmDialog from "../Components/Common/ConfirmDialog";
import LoadingScreen from "../Components/Common/LoadingScreen";
import DocumentFormModal from "../Components/Modal/DocumentsFormModal";
import { ContractViewModal } from "../Components/Modal/ViewModal";
import Pagination from "../../common/Pagination";
import useNotification from "../hooks/useNotification";

import RankManagementModal from "../Components/Modal/RankManagementModal";
import { userService } from "../../../services/Form/userService";
import { useDashboardData } from "../context/DashboardDataContext";
import { usersApi } from "../../../services/Dashboard/usersApi";

import { AdvancedDataTable } from "../Components/Data/AdvancedDataTable";
import { DataTableLayout } from "../Components/Data/DataTableLayout";
import { BulkActionBar } from "../Components/Data/BulkActionBar";

import useDocuments from "../../../hooks/dashboard/useDocuments";
import usePermissions from "../../../hooks/dashboard/usePermissions";
import { useReferenceDataContext } from "../../../context/ReferenceDataContext";
import useUsers from "../../../hooks/dashboard/useUsers";

export function DocumentManagement({ scale = 1, isMobile = false, initialItemData }) {
  const { notify } = useNotification();
  const { canCreate, canEdit, canDelete } = usePermissions();
  const {
    contracts: backendContracts,
    loading,
    fetchContracts,
    getContractById,
    createContract,
    updateContract,
    deleteContract,
    downloadContract,
    getLocalStats,
    pagination,
    canManageContracts,
    backendStats,
    fetchContractStats,
  } = useDocuments();

  const referenceData = useReferenceDataContext();
  const { users: allUsers, fetchUsers } = useUsers();
  const { ships: allShips, fetchShips, companies: allCompanies, fetchCompanies } = useDashboardData();

  // Fetch Initial Data
  useEffect(() => {
    fetchUsers({ page_size: 1000 });
    fetchShips();
    fetchCompanies();
  }, [fetchUsers, fetchShips, fetchCompanies]);

  useEffect(() => {
    fetchContracts();
    fetchContractStats();
  }, [fetchContracts, fetchContractStats]);

  // Handle initial item navigation
  const hasOpenedInitial = useRef(false);
  useEffect(() => {
    if (initialItemData && initialItemData.id && !loading && !hasOpenedInitial.current) {
      hasOpenedInitial.current = true;
      const contract = backendContracts.find(c => c.id === initialItemData.id);
      if (contract) {
        setViewingContract(contract);
        setShowViewModal(true);
      } else {
        const loadAndOpen = async () => {
          try {
             const result = await getContractById(initialItemData.id);
             if (result && result.success) {
               setViewingContract(result.data);
               setShowViewModal(true);
             }
          } catch (e) {
            console.log("Could not load initial item in Documents", e);
          }
        };
        loadAndOpen();
      }
    }
  }, [initialItemData, backendContracts, loading, getContractById]);

  const stats = useMemo(() => {
    return getLocalStats();
  }, [getLocalStats]);

  const [activeFilters, setActiveFilters] = useState({
    user: [],
    ship: [],
    status: [],
    expiry_status: [],
    start_date_from: "",
    start_date_to: "",
    company: [],
  });
  const [appliedFilters, setAppliedFilters] = useState({});

  // View mode state
  const [viewMode, setViewMode] = useState("table");

  // Bulk Selection State
  const [selectedIds, setSelectedIds] = useState([]);
  const [showBulkDeleteConfirm, setShowBulkDeleteConfirm] = useState(false);

  // Column Visibility state
  const [hiddenCols, setHiddenCols] = useState([]);

  const [showContractModal, setShowContractModal] = useState(false);
  const [selectedContract, setSelectedContract] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [contractToDelete, setContractToDelete] = useState(null);

  const [showViewModal, setShowViewModal] = useState(false);
  const [viewingContract, setViewingContract] = useState(null);
  const [viewLoading, setViewLoading] = useState(false);
  const [isStatsOpen, setIsStatsOpen] = useState(true);

  const contracts = useMemo(() => {
    return backendContracts.map((contract, index) => ({
      index: (pagination.currentPage - 1) * (pagination.pageSize || 50) + index + 1,
      id: contract.id,
      userId: contract.user,
      user: contract.user_name,
      ship: contract.ship_name,
      company: contract.company_name,
      position: contract.rank_name || contract.position_name,
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
      _original: contract,
    }));
  }, [backendContracts, pagination]);

  const handlePageChange = useCallback(
    (newPage) => {
      fetchContracts({ ...appliedFilters, page: newPage });
    },
    [fetchContracts, appliedFilters]
  );

  const filterFields = [
    {
      key: "user", label: "User Name", type: "multi-select", multiple: true,
      placeholder: "All Seafarers",
      options: allUsers.map(u => ({ value: u.id, label: `${u.first_name} ${u.last_name}` }))
    },
    {
      key: "ship", label: "Vessel Name", type: "multi-select", multiple: true,
      placeholder: "All Vessels",
      options: allShips.map(s => ({ value: s.id, label: s.ship_name || s.name || `Vessel #${s.id}` }))
    },
    {
      key: "status", label: "Contract Status", type: "multi-select", multiple: true,
      placeholder: "All Statuses",
      options: [
        { value: "Signed", label: "Signed" },
        { value: "Pending Signature", label: "Pending Signature" },
        { value: "Draft", label: "Draft" },
        { value: "Active", label: "Active" },
        { value: "Expired", label: "Expired" },
        { value: "Cancelled", label: "Cancelled" },
      ],
    },
    {
      key: "company", label: "Principal", type: "multi-select", multiple: true,
      placeholder: "All Principals",
      options: (allCompanies || []).map(c => ({ value: c.id, label: c.company_name || c.name || `Principal #${c.id}` }))
    },
    {
      key: "expiry_status", label: "Expiry Status", type: "multi-select", multiple: true,
      placeholder: "All Expiry Statuses",
      options: [
        { value: "active", label: "Active" },
        { value: "warning", label: "Warning (< 30 days)" },
        { value: "critical", label: "Critical (< 7 days)" },
        { value: "expired", label: "Expired" },
      ],
    },
    { key: "start_date_from", label: "Start Date From", type: "date" },
    { key: "start_date_to", label: "Start Date To", type: "date" },
  ];

  const handleRefresh = useCallback(() => {
    fetchContracts({ ...appliedFilters, page: pagination?.currentPage || 1 });
    fetchContractStats();
  }, [fetchContracts, fetchContractStats, appliedFilters, pagination]);

  const pipelineSegments = useMemo(() => {
    const total = (stats.signed + stats.pending + stats.draft) || 1;
    return [
      { key: "signed", color: "#38DA4E", pct: (stats.signed / total) * 100 },
      { key: "pending", color: "#F59E0B", pct: (stats.pending / total) * 100 },
      { key: "draft", color: "#3B82F6", pct: (stats.draft / total) * 100 },
    ];
  }, [stats]);

  const handleFilterByStat = useCallback((type, value) => {
    let newFilters = { ...activeFilters };
    if (type === 'status') {
      newFilters.status = newFilters.status === value ? "" : value;
      newFilters.expiry_status = "";
    } else if (type === 'expiry_status') {
      newFilters.expiry_status = newFilters.expiry_status === value ? "" : value;
      newFilters.status = "";
    }
    setActiveFilters(newFilters);
    setAppliedFilters(newFilters);
    fetchContracts({ ...newFilters, page: 1 });
  }, [activeFilters, fetchContracts]);

  const exportCols = useMemo(() => [
    { key: "user", header: "Seafarer", render: (r) => typeof r.user === 'object' && r.user ? `${r.user.first_name || ''} ${r.user.last_name || ''}`.trim() : (r.user || r.user_name || "N/A") },
    { key: "ship", header: "Vessel", render: (r) => typeof r.ship === 'object' && r.ship ? r.ship.name : (r.ship || r.ship_name || "N/A") },
    { key: "company", header: "Principal", render: (r) => typeof r.company === 'object' && r.company ? (r.company.company_name || r.company.name) : (r.company || r.company_name || "N/A") },
    { key: "position", header: "Position", render: (r) => typeof r.position === 'object' && r.position ? (r.position.title || r.position.name) : (r.position || r.job_position || "N/A") },
    { key: "status", header: "Status", render: (r) => r.status || "N/A" },
    { key: "expiryCategory", header: "Expiry Category", render: (r) => r.expiryCategory ? r.expiryCategory.charAt(0).toUpperCase() + r.expiryCategory.slice(1) : "N/A" },
  ], []);

  const pipelineRows = useMemo(() => {
    return [
      { 
        key: "signed", color: "#38DA4E", label: "Signed Contracts", remaining: `${stats.signed}`,
        isActive: !activeFilters.status || activeFilters.status === "Signed",
        onClick: () => {
          const filtered = backendContracts.filter(c => c.status === "Signed" || c.status === "Active");
          generateStatPdfReport("Signed Contracts Report", exportCols, filtered);
        }
      },
      { 
        key: "pending", color: "#F59E0B", label: "Pending Signature", remaining: `${stats.pending}`,
        isActive: !activeFilters.status || activeFilters.status === "Pending Signature",
        onClick: () => {
          const filtered = backendContracts.filter(c => c.status === "Pending Signature");
          generateStatPdfReport("Pending Signature Contracts", exportCols, filtered);
        }
      },
      { 
        key: "draft", color: "#3B82F6", label: "Drafts", remaining: `${stats.draft}`,
        isActive: !activeFilters.status || activeFilters.status === "Draft",
        onClick: () => {
          const filtered = backendContracts.filter(c => c.status === "Draft");
          generateStatPdfReport("Draft Contracts", exportCols, filtered);
        }
      },
    ];
  }, [stats, activeFilters.status, backendContracts, exportCols]);

  const expirySegments = useMemo(() => {
    const total = (stats.critical + stats.warning + stats.notice + stats.active) || 1;
    return [
      { key: "critical", color: "#EF4444", pct: (stats.critical / total) * 100 },
      { key: "warning", color: "#F97316", pct: (stats.warning / total) * 100 },
      { key: "notice", color: "#EAB308", pct: (stats.notice / total) * 100 },
      { key: "active", color: "#10B981", pct: (stats.active / total) * 100 },
    ];
  }, [stats]);

  const expiryRows = useMemo(() => {
    return [
      { 
        key: "critical", color: "#EF4444", label: "Critical (<14 days)", remaining: `${stats.critical}`,
        isActive: !activeFilters.expiry_status || activeFilters.expiry_status === "Critical",
        onClick: () => {
          const filtered = backendContracts.filter(c => c.expiryCategory === "critical");
          generateStatPdfReport("Critical Contracts", exportCols, filtered);
        }
      },
      { 
        key: "warning", color: "#F97316", label: "Warning (<30 days)", remaining: `${stats.warning}`,
        isActive: !activeFilters.expiry_status || activeFilters.expiry_status === "Warning",
        onClick: () => {
          const filtered = backendContracts.filter(c => c.expiryCategory === "warning");
          generateStatPdfReport("Warning Contracts", exportCols, filtered);
        }
      },
      { 
        key: "notice", color: "#EAB308", label: "Notice (<90 days)", remaining: `${stats.notice}`,
        isActive: !activeFilters.expiry_status || activeFilters.expiry_status === "Notice",
        onClick: () => {
          const filtered = backendContracts.filter(c => c.expiryCategory === "notice");
          generateStatPdfReport("Notice Contracts", exportCols, filtered);
        }
      },
      { 
        key: "active", color: "#10B981", label: "Healthy (>90 days)", remaining: `${stats.active}`,
        isActive: !activeFilters.expiry_status || activeFilters.expiry_status === "Active",
        onClick: () => {
          const filtered = backendContracts.filter(c => c.expiryCategory === "active");
          generateStatPdfReport("Active Contracts Report", exportCols, filtered);
        }
      },
    ];
  }, [stats, activeFilters.expiry_status, backendContracts, exportCols]);

  // ACTION HANDLERS
  const handleView = useCallback(
    async (contract) => {
      setViewLoading(true);
      try {
        const result = await getContractById(contract.id);
        if (result.success) {
          setViewingContract(result.data);
          setShowViewModal(true);
        } else {
          notify.error("Could not load contract details");
        }
      } catch (error) {
        console.error("Failed to load contract details:", error);
        notify.error("Failed to load contract details");
      } finally {
        setViewLoading(false);
      }
    },
    [getContractById, notify]
  );

  const handleEdit = useCallback(
    (contract) => {
      if (!canEdit) {
        notify.error("You don't have permission to edit contracts");
        return;
      }
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
      notify.success("Contract deleted successfully");
      setShowDeleteConfirm(false);
      setContractToDelete(null);
    }
  }, [contractToDelete, deleteContract, notify]);

  const handleBulkDelete = useCallback(async () => {
    if (!canDelete) {
      notify.error("You don't have permission to delete contracts");
      return;
    }
    try {
      for (const id of selectedIds) {
        await deleteContract(id);
      }
      setSelectedIds([]);
      setShowBulkDeleteConfirm(false);
      notify.success(`Successfully deleted ${selectedIds.length} contracts.`);
    } catch (err) {
      console.error("Bulk delete failed", err);
      notify.error("Failed to delete some contracts.");
    }
  }, [selectedIds, deleteContract, canDelete, notify]);

  const handleAlert = useCallback(
    (contract) => {
      notify.info("Alert functionality coming soon");
    },
    [notify]
  );

  const handleDownload = useCallback(
    async (contract) => {
      try {
        const result = await getContractById(contract.id);
        if (result.success) {
          generateContractPdf(result.data);
          notify.success("Contract PDF generated successfully!");
        } else {
          notify.error("Failed to load full contract details for download");
        }
      } catch (err) {
        console.error("Failed to fetch contract for download:", err);
        notify.error("Error generating contract PDF");
      }
    },
    [getContractById, notify]
  );

  const handleUpload = useCallback(
    (contract) => {
      notify.info("Upload functionality coming soon");
    },
    [notify]
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
      }
    },
    [selectedContract, handleUpdateContract]
  );

  // Table Columns Setup
  const tableColumns = useMemo(() => [
    { key: "index", label: "#", width: 60, sortable: false, render: (val) => val },
    { key: "user", label: "Seafarer", sortable: true },
    { key: "ship", label: "Vessel", sortable: true },
    { key: "company", label: "Principal", sortable: true },
    { key: "position", label: "Position", sortable: true },
    {
      key: "status", label: "Status", sortable: true,
      render: (val, row) => (
        <select
          value={val || "Draft"}
          onClick={(e) => e.stopPropagation()}
          onChange={(e) => updateContract(row._original?.id || row.id, { status: e.target.value })}
          disabled={!canEdit}
          className={`px-2 py-1 pr-6 rounded-full text-xs font-medium appearance-none outline-none border border-transparent hover:border-slate-300 dark:hover:border-slate-600 focus:ring-2 focus:ring-blue-500/20 ${canEdit ? 'cursor-pointer' : 'cursor-not-allowed'} ${
              val === 'Signed' || val === 'Active' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' :
              val === 'Expired' || val === 'Cancelled' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' :
              val === 'Draft' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' :
              'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
          }`}
          style={{ backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`, backgroundPosition: `right 0.2rem center`, backgroundRepeat: `no-repeat`, backgroundSize: `1.2em 1.2em` }}
        >
          <option value="Draft" className="bg-white text-slate-800 dark:bg-slate-800 dark:text-slate-100">Draft</option>
          <option value="Pending Signature" className="bg-white text-slate-800 dark:bg-slate-800 dark:text-slate-100">Pending Signature</option>
          <option value="Signed" className="bg-white text-slate-800 dark:bg-slate-800 dark:text-slate-100">Signed</option>
          <option value="Active" className="bg-white text-slate-800 dark:bg-slate-800 dark:text-slate-100">Active</option>
          <option value="Expired" className="bg-white text-slate-800 dark:bg-slate-800 dark:text-slate-100">Expired</option>
          <option value="Cancelled" className="bg-white text-slate-800 dark:bg-slate-800 dark:text-slate-100">Cancelled</option>
        </select>
      )
    },
    {
      key: "expiryCategory", label: "Expiry", sortable: true,
      render: (val) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            val === 'critical' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' :
            val === 'warning' ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400' :
            val === 'notice' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' :
            'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
        }`}>
            {val ? val.charAt(0).toUpperCase() + val.slice(1) : "N/A"}
        </span>
      )
    },
    {
      key: "actions", label: "Actions", width: 100, sortable: false,
      render: (_, row) => (
        <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
            <button
                onClick={() => handleView(row._original)}
                className="p-1.5 text-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-blue-900/30 rounded transition-colors"
                title="View"
            >
                <Eye size={16} />
            </button>
            {canEdit && (
                <button
                    onClick={() => handleEdit(row._original)}
                    className="p-1.5 text-emerald-600 hover:bg-emerald-50 dark:text-emerald-400 dark:hover:bg-emerald-900/30 rounded transition-colors"
                    title="Edit"
                >
                    <Pencil size={16} />
                </button>
            )}
            {canDelete && (
                <button
                    onClick={() => handleDeleteClick(row._original)}
                    className="p-1.5 text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/30 rounded transition-colors"
                    title="Delete"
                >
                    <Trash2 size={16} />
                </button>
            )}
        </div>
      )
    }
  ], [canEdit, canDelete, handleView, handleEdit, handleDeleteClick]);

  const visibleColumns = tableColumns.filter(col => !hiddenCols.includes(col.key));

  const handleExportExcel = useCallback(() => {
    try {
      const selectedData = selectedIds.length > 0 
        ? contracts.filter(c => selectedIds.includes(c.id))
        : contracts;
        
      const out = selectedData.map(c => ({
        "Seafarer": c.user,
        "Vessel": c.ship,
        "Principal": c.company,
        "Position": c.position,
        "Status": c.status,
        "Start Date": c.startDate ? formatDateLocal(c.startDate) : "N/A",
        "End Date": c.endDate ? formatDateLocal(c.endDate) : "N/A",
        "Sign On": c.signOnDate ? formatDateLocal(c.signOnDate) : "N/A",
        "Sign Off": c.signOffDate ? formatDateLocal(c.signOffDate) : "N/A",
        "Expiry": c.expiryCategory
      }));

      exportToExcel(out, `Contracts_${new Date().toISOString().split("T")[0]}.xlsx`, "Contracts");
      notify.success("Exported to Excel!");
    } catch { notify.error("Failed to export"); }
  }, [contracts, selectedIds, notify]);

  const handleExportPdf = useCallback(() => {
    try {
      const selectedData = selectedIds.length > 0 
        ? contracts.filter(c => selectedIds.includes(c.id))
        : contracts;
        
      const pdfCols = [
        { header: "Seafarer", key: "user" },
        { header: "Vessel", key: "ship" },
        { header: "Principal", key: "company" },
        { header: "Position", key: "position" },
        { header: "Status", key: "status" },
        { header: "Start Date", key: "startDate" }
      ];
      
      generateStatPdfReport(`Contracts Export`, pdfCols, selectedData);
      notify.success("Exported to PDF!");
    } catch { notify.error("Failed to export PDF"); }
  }, [contracts, selectedIds, notify]);

  const headerHeight = Math.round(80 * scale);
  const thinBtn = { padding: "4px 12px", height: "30px", fontSize: "0.875rem", display: "flex", alignItems: "center", whiteSpace: "nowrap" };

  return (
    <main
      style={{
        ...getMainContainerStyles(scale, headerHeight),
        fontFamily: "Poppins, sans-serif",
      }}
    >
      <style>{generateAllPageStyles(scale)}</style>

      {/* Header with Filter */}
      <div style={getRowBetweenStyles(scale)} className="mb-6">
        <div className="flex items-center gap-4">
          <div className="relative flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500/10 to-purple-500/10 dark:from-indigo-400/10 dark:to-purple-400/10 border border-indigo-500/20">
            <Bell size={24} className="text-indigo-600 dark:text-indigo-400 relative z-10" />
          </div>
            <div className="cursor-pointer group flex items-start gap-2" onClick={() => setIsStatsOpen(!isStatsOpen)}>
              <div>
                <h1 className="text-2xl font-extrabold text-slate-800 dark:text-white m-0 tracking-tight flex items-center gap-2">
                  Contract Management & Document Monitoring
                  <button className="p-1 rounded-md text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                    {isStatsOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                  </button>
                </h1>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-1 m-0">
                  Manage all active maritime agreements and document statuses
                </p>
              </div>
            </div>
        </div>

        <div style={{ display: "flex", gap: `${Math.round(8 * scale)}px`, alignItems: "center", flexWrap: "wrap" }}>
          <Button
            variant="icon"
            onClick={handleRefresh}
            ariaLabel="Press to refresh the table"
            title="Press to refresh the table"
            scale={scale}
            style={{ width: 30, height: 30, borderRadius: 8, minHeight: 30 }}
          >
            <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
              <path d="M21 3v5h-5" />
              <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
              <path d="M8 16H3v5" />
            </svg>
          </Button>

          {/* Export & View Toggles */}
          <Button variant="outline" onClick={handleExportPdf} scale={scale} style={thinBtn}>
              Export PDF
          </Button>
          <Button variant="outline" onClick={handleExportExcel} scale={scale} style={thinBtn}>
              Export Excel
          </Button>

          <div className="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-lg border border-slate-200 dark:border-slate-700">
            <button
              onClick={() => setViewMode("table")}
              className={`p-1.5 rounded-md flex items-center justify-center transition-all ${
                viewMode === "table" ? "bg-white dark:bg-slate-700 shadow-sm text-blue-600 dark:text-blue-400" : "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
              }`}
              title="Table View"
            >
              <List size={16} />
            </button>
            <button
              onClick={() => setViewMode("grid")}
              className={`p-1.5 rounded-md flex items-center justify-center transition-all ${
                viewMode === "grid" ? "bg-white dark:bg-slate-700 shadow-sm text-blue-600 dark:text-blue-400" : "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
              }`}
              title="Grid View"
            >
              <LayoutGrid size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Statistics Cards - Split for Pipeline and Expiry */}
      {isStatsOpen && (
        <div
          style={{
            marginTop: `${Math.round(24 * scale)}px`,
            marginBottom: `${Math.round(32 * scale)}px`,
            width: "100%",
            display: "grid",
            gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr",
            gap: `${Math.round(24 * scale)}px`,
          }}
          className="animate-in fade-in slide-in-from-top-2 duration-300"
        >
          <StackedProgressLegendCard
            segments={pipelineSegments}
            rows={pipelineRows}
            width="100%"
            height={320}
            scale={scale}
          />
          <StackedProgressLegendCard
            segments={expirySegments}
            rows={expiryRows}
            width="100%"
            height={320}
            scale={scale}
          />
        </div>
      )}

      {/* Bulk Actions */}
      <BulkActionBar
          selectedCount={selectedIds.length}
          onClearSelection={() => setSelectedIds([])}
          actions={[
              {
                  label: "Delete Selected",
                  icon: <Trash2 size={16} />,
                  onClick: () => setShowBulkDeleteConfirm(true),
                  variant: "danger",
                  hidden: !canDelete
              }
          ]}
      />

      {/* Content area with Advanced Filters & Table/Grid */}
      <DataTableLayout
        columns={tableColumns}
        storageKey="documents"
        fields={filterFields}
        filters={activeFilters}
        onFilterChange={(k, v) => setActiveFilters(prev => ({ ...prev, [k]: v }))}
        onApplyFilters={() => {
          setAppliedFilters(activeFilters);
        }}
        onClearFilters={() => {
          const empty = { user: [], ship: [], status: [], expiry_status: [], start_date_from: "", start_date_to: "", company: [] };
          setActiveFilters(empty);
          setAppliedFilters(empty);
        }}
      >
        {viewMode === "table" ? (
          <AdvancedDataTable
            data={contracts}
            columns={visibleColumns}
            keyField="id"
            selectedIds={selectedIds}
            onSelectionChange={setSelectedIds}
            rowClassName={(row) => {
              if (row.expiryCategory === "critical" || row.expiryCategory === "expired") return "bg-red-50 dark:bg-red-900/10 !border-l-4 !border-l-red-500";
              if (row.expiryCategory === "warning") return "bg-orange-50 dark:bg-orange-900/10 !border-l-4 !border-l-orange-500";
              if (row.expiryCategory === "notice") return "bg-yellow-50 dark:bg-yellow-900/10 !border-l-4 !border-l-yellow-500";
              return "";
            }}
            onRowClick={(row) => {
              handleView(row._original);
            }}
            isLoading={loading}
            emptyStateMessage="No contracts found."
          />
        ) : (
          <div className="p-4 bg-slate-50 dark:bg-slate-900/30">
            {loading ? (
              <LoadingScreen scale={scale} message="Loading contracts..." />
            ) : contracts.length > 0 ? (
              <div style={{ display: "flex", flexDirection: "column", gap: `${Math.round(16 * scale)}px` }}>
                {contracts.map((contract) => (
                  <DocumentCard
                    key={contract.id}
                    document={contract}
                    index={contract.index}
                    scale={scale}
                    onView={() => handleView(contract._original)}
                    onEdit={() => handleEdit(contract._original)}
                    onDelete={() => handleDeleteClick(contract._original)}
                    onAlert={() => handleAlert(contract._original)}
                    onUpload={() => handleUpload(contract._original)}
                    onDownload={() => handleDownload(contract._original)}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center p-12 text-slate-500">No contracts found.</div>
            )}
          </div>
        )}
      </DataTableLayout>

      {/* Pagination */}
      {!loading && contracts.length > 0 && (
        <div style={{ marginTop: `${Math.round(20 * scale)}px` }}>
          <Pagination
            page={pagination?.currentPage || 1}
            pageSize={pagination?.pageSize || 50}
            total={pagination?.count || 0}
            onChange={handlePageChange}
            scale={scale}
            showInfo={true}
          />
        </div>
      )}

      {/* Modals */}
      {showContractModal && selectedContract && (
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

      {/* Contract View Loading Overlay */}
      {viewLoading && (
        <div style={{
          position: "fixed", inset: 0, zIndex: 9999,
          background: "rgba(15, 23, 42, 0.55)",
          backdropFilter: "blur(4px)",
          display: "flex", alignItems: "center", justifyContent: "center",
          flexDirection: "column", gap: Math.round(16 * scale),
        }}>
          <div style={{
            width: Math.round(52 * scale), height: Math.round(52 * scale),
            border: `${Math.round(4 * scale)}px solid rgba(255,255,255,0.15)`,
            borderTopColor: "#0065AF",
            borderRadius: "50%",
            animation: "doc-spin 0.75s linear infinite",
          }} />
          <p style={{ color: "#fff", fontSize: Math.round(14 * scale), fontWeight: 500, margin: 0 }}>
            Loading contract details…
          </p>
          <style>{`@keyframes doc-spin { to { transform: rotate(360deg); } }`}</style>
        </div>
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
        message={`Are you sure you want to delete the contract for ${contractToDelete?.user?.first_name || contractToDelete?.user_name || "this user"
          }? This action cannot be undone.`}
        confirmLabel="Delete"
        variant="danger"
        scale={scale}
        loading={loading}
      />

      {/* Bulk Delete Confirmation */}
      {showBulkDeleteConfirm && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/50 backdrop-blur-sm">
              <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-md p-6">
                  <h3 className="text-xl font-bold text-slate-800 dark:text-white mb-2">Confirm Bulk Delete</h3>
                  <p className="text-slate-500 dark:text-slate-400 mb-6">
                      Are you sure you want to delete {selectedIds.length} contracts? This action cannot be undone.
                  </p>
                  <div className="flex justify-end gap-3">
                      <Button variant="outline" onClick={() => setShowBulkDeleteConfirm(false)}>Cancel</Button>
                      <Button variant="danger" onClick={handleBulkDelete}>Delete All</Button>
                  </div>
              </div>
          </div>
      )}
    </main>
  );
}
