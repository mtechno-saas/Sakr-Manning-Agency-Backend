/* eslint-disable no-unused-vars */

// Content/Finance.jsx - COMPLETE with Backend Filtering & Pagination
import React, { useState, useEffect, useMemo, useCallback } from "react";
import { COLORS, TOKENS } from "../Constants";
import { exportToExcel, exportToJSON } from "../../../utils/exportHelpers";
import {
  generateAllPageStyles,
  getMainContainerStyles,
  getPageTitleStyles,
} from "../Styles/cssClasses";

import Button from "../Components/Common/Button";
import ConfirmDialog from "../Components/Common/ConfirmDialog";
import LoadingScreen from "../Components/Common/LoadingScreen";
import EnhancedFilterModel from "../Components/Common/EnhancedFilterModel";
import SavedFilters from "../Components/Common/SavedFilters";
import Pagination from "../../common/Pagination";

import FinanceFormModal from "../Components/Modal/FinanceFormModal";
import { FinanceViewModal } from "../Components/Modal/ViewModal";

import useNotification from "../hooks/useNotification";

import usePermissions from "../../../hooks/dashboard/usePermissions";
import useFinance from "../../../hooks/dashboard/useFinance";
import useUsers from "../../../hooks/dashboard/useUsers";
import useCompanies from "../../../hooks/dashboard/useCompanies";
import { useDashboardData } from "../context/DashboardDataContext";

export function FinanceRecords({ scale = 1, isMobile = false }) {
  const { notify } = useNotification();
  const { canCreate, canEdit, canDelete, canManageFinance } = usePermissions();

  // Use custom hook for finance data
  const {
    records: backendRecords,
    loading: recordsLoading,
    fetchRecords,
    createRecord,
    updateRecord,
    deleteRecord,
    fetchStats,
    exportRecords,
    pagination,
  } = useFinance();

  const { referenceOptions } = useDashboardData();

  // For mapping IDs to names
  const { getUserById } = useUsers();
  const { getCompanyById } = useCompanies();

  // Local state
  const [showFinanceModal, setShowFinanceModal] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const [recordToDelete, setRecordToDelete] = useState(null);

  // View modal state
  const [showViewModal, setShowViewModal] = useState(false);
  const [viewingRecord, setViewingRecord] = useState(null);

  // ✅ Filter State
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [filters, setFilters] = useState({
    status: "",
    user: "",
    company: "",
    record_type: "",
    start_date_from: "",
    start_date_to: "",
  });
  const [activeFilters, setActiveFilters] = useState({
    status: "",
    user: "",
    company: "",
    record_type: "",
    start_date_from: "",
    start_date_to: "",
  });
  const [savedPresets, setSavedPresets] = useState([]);

  // Load records and stats on mount
  useEffect(() => {
    fetchRecords({ ...activeFilters });
    loadStatistics();
  }, [fetchRecords, activeFilters]);

  // Load statistics
  const loadStatistics = async () => {
    const result = await fetchStats();
    if (result.success) {
      setStatistics(result.data);
    }
  };

  // State for storing user and company data
  const [userMap, setUserMap] = useState({});
  const [companyMap, setCompanyMap] = useState({});
  const [detailsLoading, setDetailsLoading] = useState(false);

  // Fetch all unique users and companies when backendRecords change
  useEffect(() => {
    const fetchDetails = async () => {
      if (backendRecords.length === 0) return;

      setDetailsLoading(true);
      try {
        const userIds = [...new Set(backendRecords.map((r) => r.user))];
        const companyIds = [...new Set(backendRecords.map((r) => r.company))];

        // Fetch only if we have IDs
        const usersPromise = userIds.length > 0
          ? Promise.all(userIds.map((id) => getUserById(id)))
          : Promise.resolve([]);
        const companiesPromise = companyIds.length > 0
          ? Promise.all(companyIds.map((id) => getCompanyById(id)))
          : Promise.resolve([]);

        const [users, companies] = await Promise.all([usersPromise, companiesPromise]);

        const userLookup = {};
        users.forEach((result, idx) => {
          if (result && result.success) {
            const f = result.data?.first_name || "";
            const l = result.data?.last_name || "";
            let name = (f + l).trim();
            userLookup[userIds[idx]] = name || "Unknown User";
          }
        });

        const companyLookup = {};
        companies.forEach((result, idx) => {
          if (result && result.success) {
            companyLookup[companyIds[idx]] =
              result.data.company_name || "Unknown Company";
          }
        });

        setUserMap((prev) => ({ ...prev, ...userLookup }));
        setCompanyMap((prev) => ({ ...prev, ...companyLookup }));
      } catch (error) {
        console.error("Failed to load user/company details", error);
        // Don't notify error here to avoid spamming if one fails
      } finally {
        setDetailsLoading(false);
      }
    };

    fetchDetails();
  }, [backendRecords, getUserById, getCompanyById]);

  // Transform backend records to match UI format
  const records = useMemo(() => {
    return backendRecords.map((record, index) => ({
      index: (pagination.currentPage - 1) * (pagination.pageSize || 50) + index + 1,
      id: record.id,
      userId: record.user,
      user: userMap[record.user] || `User #${record.user}`, // fallback
      companyId: record.company,
      company: companyMap[record.company] || `Company #${record.company}`, // fallback
      startDate: record.start_date,
      endDate: record.end_date,
      status: record.status || "Pending",
      totalDays: record.total_days,
      dailyRate: record.daily_rate,
      totalMoney: record.total_money,
      createdAt: record.created_at,
      updatedAt: record.updated_at,
      _original: record
    }));
  }, [backendRecords, userMap, companyMap, pagination.currentPage, pagination.pageSize]);

  const columns = useMemo(() => [
    {
      key: "index",
      title: "#",
      width: 60,
      render: (v) => v,
    },
    {
      key: "user",
      title: "User",
      width: 200,
      render: (v) => v,
    },
    {
      key: "company",
      title: "Company",
      width: 200,
      render: (v) => v,
    },
    {
      key: "startDate",
      title: "Start Date",
      width: 120,
      render: (v) => v,
    },
    {
      key: "endDate",
      title: "End Date",
      width: 120,
      render: (v) => v || "-",
    },
    {
      key: "totalMoney",
      title: "Total",
      width: 120,
      render: (v) => `$${v}`,
    },
    {
      key: "actions",
      title: "Actions",
      width: 150,
      isActions: true,
      onView: handleViewRecord,
      onEdit: (canEdit || canManageFinance) ? handleEdit : undefined,
      onDelete: (canDelete || canManageFinance) ? handleDeleteClick : undefined,
    }
  ], [canEdit, canDelete, canManageFinance, handleViewRecord, handleEdit, handleDeleteClick]);

  // ============================================
  // FILTER HANDLERS
  // ============================================
  const handleApplyFilters = useCallback(() => {
    setActiveFilters(filters);
    setShowFilterModal(false);
    fetchRecords({ ...filters, page: 1 });
  }, [filters, fetchRecords]);

  const handleResetFilters = useCallback(() => {
    const empty = { status: "", user: "", company: "", record_type: "", start_date_from: "", start_date_to: "" };
    setFilters(empty);
    setActiveFilters(empty);
    setShowFilterModal(false);
    fetchRecords({ page: 1 });
  }, [fetchRecords]);

  const handlePageChange = useCallback((newPage) => {
    fetchRecords({ ...activeFilters, page: newPage });
  }, [fetchRecords, activeFilters]);

  const handleApplyPreset = useCallback((preset) => {
    setFilters(preset);
    setActiveFilters(preset);
    fetchRecords({ ...preset, page: 1 });
  }, [fetchRecords]);

  const handleSavePreset = useCallback((name, vals) => {
    setSavedPresets(prev => [...prev, { name, filters: vals }]);
  }, []);

  const handleDeletePreset = useCallback((name) => {
    setSavedPresets(prev => prev.filter(p => p.name !== name));
  }, []);

  const filterFields = [
    {
      key: "record_type",
      label: "Record Type",
      type: "select",
      placeholder: "All Types",
      options: [
        { value: "INCOME", label: "Income" },
        { value: "EXPENSE", label: "Expense" },
      ]
    },
    {
      key: "status",
      label: "Status",
      type: "select",
      placeholder: "All Statuses",
      options: [
        { value: "Paid", label: "Paid" },
        { value: "Pending", label: "Pending" },
        { value: "Overdue", label: "Overdue" },
        { value: "Cancelled", label: "Cancelled" },
      ]
    },
    {
      key: "user",
      label: "User / Seafarer",
      type: "select",
      placeholder: "All Users",
      options: referenceOptions.users
    },
    {
      key: "company",
      label: "Company",
      type: "select",
      placeholder: "All Companies",
      options: referenceOptions.companies
    },
    {
      key: "start_date_from",
      label: "Start Date From",
      type: "date",
    },
    {
      key: "start_date_to",
      label: "Start Date To",
      type: "date",
    },
  ];

  // ============================================
  // CRUD HANDLERS
  // ============================================
  const handleEdit = useCallback(
    (record) => {
      if (!canEdit && !canManageFinance) {
        notify.error("You do not have permission to edit finance records");
        return;
      }
      setSelectedRecord(record._original);
      setShowFinanceModal(true);
    },
    [canEdit, canManageFinance, notify]
  );

  const handleViewRecord = useCallback((record) => {
    // Pass raw data plus resolved names if possible. 
    // Records map already includes filtered display names, but ViewModal might expect backend structure.
    // The `_original` prop in record has backend data.
    // Let's mix them for best display.
    const displayRecord = {
      ...record._original,
      user_name: record.user, // resolved name from list
      company_name: record.company // resolved name from list
    };
    setViewingRecord(displayRecord);
    setShowViewModal(true);
  }, []);

  const handleDeleteClick = useCallback(
    (id) => {
      if (!canDelete && !canManageFinance) {
        notify.error("You do not have permission to delete finance records");
        return;
      }
      setRecordToDelete(id);
      setShowDeleteConfirm(true);
    },
    [canDelete, canManageFinance, notify]
  );

  const handleConfirmDelete = useCallback(async () => {
    if (!recordToDelete) return;
    const result = await deleteRecord(recordToDelete);
    if (result.success) {
      notify.success("Finance record deleted successfully");
      setShowDeleteConfirm(false);
      setRecordToDelete(null);
      await loadStatistics();
    }
  }, [recordToDelete, deleteRecord]);

  const handleAdd = useCallback(() => {
    if (!canCreate && !canManageFinance) {
      notify.error("You do not have permission to add finance records");
      return;
    }
    setSelectedRecord(null);
    setShowFinanceModal(true);
  }, [canCreate, canManageFinance, notify]);

  const handleSaveRecord = async (recordData) => {
    if (selectedRecord) {
      // Edit existing record
      const result = await updateRecord(selectedRecord.id, recordData);
      if (result.success) {
        setShowFinanceModal(false);
        await loadStatistics();
      }
    } else {
      // Create new record
      const result = await createRecord(recordData);
      if (result.success) {
        setShowFinanceModal(false);
        await loadStatistics();
      }
    }
  };

  const handleExportExcel = useCallback(async () => {
    // Use backend export or client export? FinanceApi has exportFinanceRecords.
    // Let's use backend export if available, but here we can try client helper for visible?
    // Actually financeApi.exportFinanceRecords is better for full dataset.
    // But wait, existing code used exportToCSV helper on `records`.
    // Since we only have one page, we should ideally use backend export. 
    // For now, let's use the helper on the CURRENT PAGE data (records) to match other modules' behavior 
    // OR update to use backend export for full data. 
    // The Documents module uses backend-filtered data but client-side export helper on the *current page* data.
    // I'll stick to that pattern for consistency, or if I want full export, use backend.
    // Let's stick to client helper on current data for now.

    if (records.length === 0) {
      notify.warning("No records to export");
      return;
    }

    const dataToExport = records.map(({ id, userId, companyId, _original, ...rest }) => rest);
    exportToExcel(dataToExport, `Finance_Records_${new Date().toISOString().split("T")[0]}.xlsx`, "Finance");
    notify.success("Finance records exported to Excel!");
  }, [records, notify]);

  const handleRefresh = useCallback(() => {
    fetchRecords({ ...activeFilters, page: pagination?.currentPage || 1 });
  }, [fetchRecords, activeFilters, pagination]);

  const headerHeight = Math.round(101 * scale);

  return (
    <main style={getMainContainerStyles(scale, headerHeight)}>
      <style>{`
        ${generateAllPageStyles(scale)}

        .records-container {
          background: ${COLORS.white};
          border-radius: ${Math.round(22 * scale)}px;
          box-shadow: ${TOKENS.shadow.sm};
          overflow: hidden;
          margin-top: ${Math.round(32 * scale)}px;
        }

        .records-header {
          padding: ${Math.round(24 * scale)}px;
          background: #F9F9F9;
          border-bottom: 1px solid ${COLORS.borderColor};
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .records-title {
          font-size: ${Math.round(18 * scale)}px;
          font-weight: 600;
          color: ${COLORS.darkText};
          font-family: Poppins, sans-serif;
          margin: 0;
        }

        .records-list {
          display: flex;
          flex-direction: column;
        }

        .record-item {
          padding: ${Math.round(16 * scale)}px ${Math.round(24 * scale)}px;
          border-bottom: 1px solid ${COLORS.borderColor};
          display: grid;
          grid-template-columns: 2fr 2fr 1.5fr 1.5fr auto auto;
          gap: ${Math.round(16 * scale)}px;
          align-items: center;
        }

        .record-item:hover {
          background: #FAFAFA;
        }

        .record-cell {
          font-size: ${Math.round(15 * scale)}px;
          color: ${COLORS.darkText};
          font-family: Inter, sans-serif;
        }

        .empty-state {
          padding: ${Math.round(60 * scale)}px ${Math.round(24 * scale)}px;
          text-align: center;
          color: ${COLORS.lightText};
        }
      `}</style>

      {/* Header */}
      <div
        style={{
          marginBottom: `${Math.round(20 * scale)}px`,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center"
        }}
      >
        <h1
          style={{
            ...getPageTitleStyles(scale),
            marginBottom: `${Math.round(8 * scale)}px`,
            margin: 0
          }}
        >
          Finance Records
        </h1>

        <div style={{ display: "flex", gap: `${Math.round(8 * scale)}px`, alignItems: "center" }}>
          {/* <Button
            variant="icon"
            onClick={() => setShowFilterModal(true)}
            scale={scale}
            ariaLabel="Filter records"
            title="Filter records"
            style={{ width: 30, height: 30, borderRadius: 8, minHeight: 30 }}
          >
            <svg width={16} height={16} viewBox="0 0 24 24" fill="none">
              <path d="M3 6h18M6 12h12M9 18h6" stroke="#1E1E1E" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </Button> */}
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

          {records.length > 0 && (
            <Button variant="outline" onClick={handleExportExcel} scale={scale} style={{ minHeight: 30, height: 30, padding: "0 14px", fontSize: 13, borderRadius: 8, fontWeight: 500, lineHeight: "30px" }}>
              Export Excel
            </Button>
          )}

          {(canCreate || canManageFinance) && (
            <Button variant="primary" onClick={handleAdd} scale={scale} style={{ minHeight: 30, height: 30, padding: "0 14px", fontSize: 13, borderRadius: 8, fontWeight: 500, lineHeight: "30px" }}>
              Add Record
            </Button>
          )}
        </div>
      </div>

      {/* <SavedFilters
        scale={scale}
        savedPresets={savedPresets}
        currentFilters={activeFilters}
        onApplyPreset={handleApplyPreset}
        onSavePreset={handleSavePreset}
        onDeletePreset={handleDeletePreset}
      /> */}

      {/* Statistics Summary */}
      {statistics && (
        <div
          style={{
            background: COLORS.white,
            borderRadius: `${Math.round(22 * scale)}px`,
            padding: `${Math.round(24 * scale)}px`,
            boxShadow: TOKENS.shadow.sm,
            marginBottom: `${Math.round(24 * scale)}px`,
            display: "grid",
            gridTemplateColumns: isMobile ? "1fr" : "repeat(4, 1fr)",
            gap: `${Math.round(16 * scale)}px`,
          }}
        >
          <div>
            <div style={{ fontSize: `${Math.round(14 * scale)}px`, color: COLORS.lightText, marginBottom: `${Math.round(8 * scale)}px` }}>
              Total Records
            </div>
            <div style={{ fontSize: `${Math.round(24 * scale)}px`, fontWeight: 600, color: COLORS.darkText }}>
              {statistics.total_records}
            </div>
          </div>

          <div>
            <div style={{ fontSize: `${Math.round(14 * scale)}px`, color: COLORS.lightText, marginBottom: `${Math.round(8 * scale)}px` }}>
              Total Money
            </div>
            <div style={{ fontSize: `${Math.round(24 * scale)}px`, fontWeight: 600, color: COLORS.primary }}>
              ${statistics.total_money}
            </div>
          </div>

          <div>
            <div style={{ fontSize: `${Math.round(14 * scale)}px`, color: COLORS.lightText, marginBottom: `${Math.round(8 * scale)}px` }}>
              Average Daily Rate
            </div>
            <div style={{ fontSize: `${Math.round(24 * scale)}px`, fontWeight: 600, color: COLORS.darkText }}>
              ${statistics.average_daily_rate}
            </div>
          </div>

          <div>
            <div style={{ fontSize: `${Math.round(14 * scale)}px`, color: COLORS.lightText, marginBottom: `${Math.round(8 * scale)}px` }}>
              This Month
            </div>
            <div style={{ fontSize: `${Math.round(24 * scale)}px`, fontWeight: 600, color: COLORS.accepted }}>
              ${statistics.this_month_total}
            </div>
          </div>
        </div>
      )}

      {/* Records Section */}
      <div className="records-container">
        <div className="records-header">
          <h3 className="records-title">All Finance Records</h3>
          <span
            style={{
              color: COLORS.lightText,
              fontSize: `${Math.round(14 * scale)}px`,
            }}
          >
            Total: {pagination?.count || records.length}
          </span>
        </div>

        <div style={{ padding: "0 24px" }}>
          <RefinedDataTable
            data={records}
            columns={columns}
            rowKey="id"
            scale={scale}
            pageSize={pagination.pageSize || 50}
            loading={recordsLoading || detailsLoading}
            initialPage={1}
            actions={["View", (canEdit || canManageFinance) && "Edit", (canDelete || canManageFinance) && "Delete"].filter(Boolean)}
            onRowClick={handleViewRecord}
            styleOverrides={{ columnGap: 9 }}
          />
        </div>

        {/* Pagination */}
        {!recordsLoading && records.length > 0 && (
          <div style={{ padding: `${Math.round(20 * scale)}px` }}>
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
      </div>

      {/* Finance Form Modal */}
      {showFinanceModal && (
        <FinanceFormModal
          record={selectedRecord}
          onClose={() => setShowFinanceModal(false)}
          onSave={handleSaveRecord}
          scale={scale}
        />
      )}

      {/* Finance View Modal */}
      <FinanceViewModal
        isOpen={showViewModal}
        onClose={() => {
          setShowViewModal(false);
          setViewingRecord(null);
        }}
        record={viewingRecord}
        onDelete={(id) => {
          setShowViewModal(false);
          setViewingRecord(null);
          handleDeleteClick(id);
        }}
        scale={scale}
        canDelete={canDelete || canManageFinance}
      />

      {/* Filter Modal */}
      {/* <EnhancedFilterModel
        isOpen={showFilterModal}
        onClose={() => setShowFilterModal(false)}
        values={filters}
        onValuesChange={setFilters}
        onApply={handleApplyFilters}
        onReset={handleResetFilters}
        fields={filterFields}
        scale={scale}
        title="Filter Finance Records"
      /> */}

      {/* Delete Confirmation */}
      {showDeleteConfirm && (
        <ConfirmDialog
          isOpen={showDeleteConfirm}
          onClose={() => {
            setShowDeleteConfirm(false);
            setRecordToDelete(null);
          }}
          onConfirm={handleConfirmDelete}
          title="Delete Record"
          message="Are you sure you want to delete this finance record? This action cannot be undone."
          confirmLabel="Delete"
          variant="danger"
          scale={scale}
          loading={recordsLoading}
        />
      )}
    </main>
  );
}
