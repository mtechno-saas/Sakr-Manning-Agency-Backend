/* eslint-disable no-unused-vars */

// Content/Users.jsx - COMPLETE with Full CRUD Operations
import React, { useState, useEffect, useMemo, useCallback, useRef } from "react";
import { StackedProgressLegendCard } from "../Components/Cards/StatisticsCards";
import { AdvancedDataTable } from "../Components/Data/AdvancedDataTable";
import { DataTableLayout } from "../Components/Data/DataTableLayout";
import { BulkActionBar } from "../Components/Data/BulkActionBar";
import { Trash2, Eye, Edit2, Download, Award, ChevronDown } from "lucide-react";
import { ASSETS } from "../../../utils/constants";
import { exportToCSV, exportToJSON, exportToExcel } from "../../../utils/exportHelpers";
import { getMediaUrl } from "../../../utils/fileHelpers";
import { generateStatPdfReport } from "../../../utils/pdfReportGenerator";

import { COLORS, TOKENS } from "../Constants";
import {
  generateAllPageStyles,
  getMainContainerStyles,
  getPageTitleStyles,
  getRowBetweenStyles,
} from "../Styles/cssClasses";
import Button from "../Components/Common/Button";
import EnhancedFilterModel from "../Components/Common/EnhancedFilterModel";
import SavedFilters from "../Components/Common/SavedFilters";
import ConfirmDialog from "../Components/Common/ConfirmDialog";

import UserFormModal from "../Components/Modal/UserFormModal";
import UserViewModal from "../Components/Modal/ViewModal/UserViewModal";
import { CVSubmissionEditModal } from "../Components/Modal/ViewModal/CVSubmissionEditModal";
import RankManagementModal from "../Components/Modal/RankManagementModal";
import BulkUpdateModal from "../Components/Modal/BulkUpdateModal";
import { userService } from "../../../services/Form/userService";
import { useDashboardData } from "../context/DashboardDataContext";
import { usersApi } from "../../../services/Dashboard/usersApi";

import Pagination from "../../common/Pagination";
// import useTableFilters from "../hooks/useTableFilters"; // Removed for server-side filtering
import useNotification from "../hooks/useNotification";

import usePermissions from "../../../hooks/dashboard/usePermissions";
import useUsers from "../../../hooks/dashboard/useUsers";

export function UserManagement({ scale = 1, isMobile, initialItemData }) {
  const { notify } = useNotification();
  const { canCreate, canEdit, canDelete } = usePermissions();
  const referenceData = useDashboardData();

  // Helper: Check if user is online (last login within 1 hour)
  const isUserOnline = (lastLogin) => {
    if (!lastLogin) return false;
    const lastLoginDate = new Date(lastLogin);
    const now = new Date();
    const hoursDiff = (now - lastLoginDate) / (1000 * 60 * 60);
    return hoursDiff <= 1;
  };

  // Helper: Format last login date
  const formatLastLogin = (lastLogin) => {
    if (!lastLogin) return "Never";
    const date = new Date(lastLogin);
    return date.toISOString().split("T")[0]; // YYYY-MM-DD
  };
  const {
    users: backendUsers,
    loading: usersLoading,
    fetchUsers,
    createUser,
    updateUser,
    deleteUser,
    bulkDeleteUsers,
    bulkUpdateUsers,
    fetchUserStats,
    pagination,
  } = useUsers();

  // Add tab state
  const [activeTab, setActiveTab] = useState("All");

  // Local state
  const [selectedIds, setSelectedIds] = useState([]);
  const [showBulkUpdateModal, setShowBulkUpdateModal] = useState(false);
  const [showUserModal, setShowUserModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showViewModal, setShowViewModal] = useState(false);
  const [viewingUser, setViewingUser] = useState(null);
  const [viewLoading, setViewLoading] = useState(false);
  const [statistics, setStatistics] = useState(null);
  const [positions, setPositions] = useState([]);

  // Rank management modal
  const [showRankModal, setShowRankModal] = useState(false);
  const [rankModalUser, setRankModalUser] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);

  // Load statistics
  const loadStatistics = useCallback(async () => {
    const result = await fetchUserStats();
    if (result.success) {
      setStatistics(result.data);
    }
  }, [fetchUserStats]);

  const handleBulkDelete = async () => {
    if (window.confirm(`Are you sure you want to delete ${selectedIds.length} users?`)) {
      const result = await bulkDeleteUsers(selectedIds);
      if (result.success) {
        setSelectedIds([]);
        loadStatistics();
      }
    }
  };

  const handleBulkUpdate = async (updates) => {
    const result = await bulkUpdateUsers(selectedIds, updates);
    if (result.success) {
      notify.success("Bulk update applied successfully");
      setShowBulkUpdateModal(false);
      setSelectedIds([]);
      loadStatistics();
    }
  };

  // Load users and stats on mount
  useEffect(() => {
    fetchUsers();
    loadStatistics();
    usersApi.getPositions().then(data => setPositions(data || [])).catch(console.error);
  }, [fetchUsers, loadStatistics]);

  // Handle initial item navigation
  const hasOpenedInitial = useRef(false);
  useEffect(() => {
    if (initialItemData && initialItemData.id && !usersLoading && !hasOpenedInitial.current) {
      hasOpenedInitial.current = true;
      const loadAndOpen = async () => {
        try {
          const result = await userService.loadFullUserProfile(initialItemData.id, { raw: true });
          if (result.success) {
            setViewingUser(result.data);
            setShowViewModal(true);
          }
        } catch (e) {
          console.log("Could not load initial item in Users", e);
        }
      };
      loadAndOpen();
    }
  }, [initialItemData, usersLoading]);

  // Transform backend users to match UI format
  const userData = useMemo(() => {
    return backendUsers.map((user, index) => ({
      index: (pagination.currentPage - 1) * (pagination.pageSize || 50) + index + 1,
      id: user.id,
      // name: `${user.first_name.split(" ")[0] || ""} ${user.middle_name.split(" ")[0] || ""}`.trim(),
      name: user.first_name + " " + user.middle_name,
      email: user.email,
      role: user.role,
      status: user.status || "Active",
      availability: user.user_status || "ON_SITE",
      avatar: getMediaUrl(user.profile_image) || ASSETS.LOGO,

      lastLogin: formatLastLogin(user.last_login),
      isOnline: isUserOnline(user.last_login),

      assignedCode: user.ranks?.[0]?.assigned_code,
      rank: user.ranks?.[0]?.rank_name || "N/A",
      phone: user.phone_number || user.mobile_number || "N/A",
      _original: user, // {additionally includes: marital_status, ... }
    }));
  }, [backendUsers]);

  // Calculate user statistics from backend stats
  const userSegments = useMemo(() => {
    if (!statistics) {
      // Fallback: calculate from current data
      const roleCounts = userData.reduce(
        (acc, user) => {
          acc[user.role] = (acc[user.role] || 0) + 1;
          return acc;
        },
        { Admin: 0, "HR Manager": 0, Recruiter: 0, Employee: 0 }
      );

      return [
        { key: "admin", color: "#BF4DD1", pct: roleCounts.Admin || 1 },
        {
          key: "hr_manager",
          color: "#35C2FD",
          pct: roleCounts["HR Manager"] || 1,
        },
        { key: "recruiter", color: "#54D14D", pct: roleCounts.Recruiter || 1 },
        { key: "employee", color: "#FFC107", pct: roleCounts.Employee || 1 },
        { key: "crew", color: "#06B6D4", pct: roleCounts.Crew || 1 },
      ];
    }

    // Use backend statistics
    return [
      { key: "admin", color: "#BF4DD1", pct: statistics.admins || 1 },
      { key: "hr_manager", color: "#35C2FD", pct: statistics.hr_managers || 1 },
      { key: "recruiter", color: "#54D14D", pct: statistics.recruiters || 1 },
      { key: "employee", color: "#FFC107", pct: statistics.employees || 1 },
      { key: "crew", color: "#06B6D4", pct: statistics.crew || 1 },
    ];
  }, [statistics, userData]);

  // User segments legend rows
  const userRows = useMemo(() => {
    if (!statistics) {
      const roleCounts = userData.reduce(
        (acc, user) => {
          acc[user.role] = (acc[user.role] || 0) + 1;
          return acc;
        },
        { Admin: 0, "HR Manager": 0, Recruiter: 0, Employee: 0 }
      );

      return [
        {
          key: "admin",
          color: "#BF4DD1",
          label: "Admin",
          remaining: `${roleCounts.Admin} users`,
        },
        {
          key: "hr_manager",
          color: "#35C2FD",
          label: "HR Manager",
          remaining: `${roleCounts["HR Manager"]} users`,
        },
        {
          key: "recruiter",
          color: "#54D14D",
          label: "Recruiter",
          remaining: `${roleCounts.Recruiter} users`,
        },
        {
          key: "employee",
          color: "#FFC107",
          label: "Applicant",
          remaining: `${roleCounts.Employee} users`,
        },
      ];
    }

    return [
      {
        key: "admin",
        color: "#BF4DD1",
        label: "Admin",
        remaining: `${statistics.admins || 0} users`,
      },
      {
        key: "hr_manager",
        color: "#35C2FD",
        label: "HR Manager",
        remaining: `${statistics.hr_managers || 0} users`,
      },
      {
        key: "recruiter",
        color: "#54D14D",
        label: "Recruiter",
        remaining: `${statistics.recruiters || 0} users`,
      },
      {
        key: "employee",
        color: "#FFC107",
        label: "Applicant",
        remaining: `${statistics.employees || 0} users`,
      },
      {
        key: "crew",
        color: "#06B6D4",
        label: "Crew",
        remaining: `${statistics.crew || 0} users`,
      },
    ];
  }, [statistics, userData]);

  // Calculate online users (last login within 1 hour)
  const onlineUsersCount = useMemo(() => {
    return userData.filter((user) => user.isOnline).length;
  }, [userData]);

  // ✅ Table filters — keys match BE query params directly
  const [activeFilters, setActiveFilters] = useState({});
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const buildBackendFilters = useCallback((uiFilters) => {
    const backend = {};
    if (!uiFilters) return backend;
    Object.entries(uiFilters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "" && value !== false) {
        backend[key] = value;
      }
    });
    return backend;
  }, []);

  // Check if any filters are active
  const hasActiveFilters = Object.entries(activeFilters).some(([, v]) => v !== "" && v !== false);

  // Handle page change for server-side pagination
  const handlePageChange = useCallback(
    (newPage) => {
      fetchUsers({ ...buildBackendFilters(activeFilters), page: newPage });
    },
    [fetchUsers, activeFilters, buildBackendFilters]
  );

  // Backend filter handlers
  const handleApplyFilters = useCallback(() => {
    setIsSidebarOpen(false);
    fetchUsers({ ...buildBackendFilters(activeFilters), page: 1 });
  }, [activeFilters, fetchUsers, buildBackendFilters]);

  const handleResetFilters = useCallback(() => {
    setActiveFilters({});
    fetchUsers({ page: 1 });
    setIsSidebarOpen(false);
  }, [fetchUsers]);

  const stats = useMemo(() => {
    return {
      admin: userData.filter((d) => d.role === "Admin").length,
      hr_manager: userData.filter((d) => d.role === "HR Manager").length,
      recruiter: userData.filter((d) => d.role === "Recruiter").length,
      employee: userData.filter((d) => d.role === "Employee").length,
      crew: userData.filter((d) => d.role === "Crew").length,
    };
  }, [userData]);

  // ============================================
  // CRUD HANDLERS
  // ============================================
  const handleView = useCallback(
    async (row) => {
      setViewLoading(true);
      try {
        const result = await userService.loadFullUserProfile(row.id, { raw: true });
        if (result.success) {
          setViewingUser(result.data);
          setShowViewModal(true);
        }
      } catch (err) {
        notify.error("Failed to load full user profile");
        console.error(err);
      } finally {
        setViewLoading(false);
      }
    },
    [notify]
  );

  const handleEditUser = useCallback(
    (row) => {
      if (!canEdit) {
        notify.error("You do not have permission to edit users");
        return;
      }
      const user = backendUsers.find((u) => u.id === row.id);
      if (user) {
        setSelectedUser(user);
        setShowUserModal(true);
      }
    },
    [backendUsers, canEdit, notify]
  );

  const handleDeleteUser = useCallback(
    (id) => {
      if (!canDelete) {
        notify.error("You do not have permission to delete users");
        return;
      }
      setUserToDelete(id);
      setShowDeleteConfirm(true);
    },
    [canDelete, notify]
  );

  const handleConfirmDelete = useCallback(async () => {
    if (!userToDelete) return;
    const result = await deleteUser(userToDelete);
    if (result.success) {
      notify.success("User deleted successfully");
      setShowDeleteConfirm(false);
      setUserToDelete(null);
      await loadStatistics();
    }
  }, [userToDelete, deleteUser, loadStatistics]);

  const handleAddUser = useCallback(() => {
    if (!canCreate) {
      notify.error("You do not have permission to add users");
      return;
    }
    setSelectedUser(null);
    setShowUserModal(true);
  }, [canCreate, notify]);

  const handleManageRanks = useCallback((row) => {
    const user = backendUsers.find((u) => u.id === row.id);
    if (user) {
      setRankModalUser(user);
      setShowRankModal(true);
    } else {
      notify.error("User not found");
    }
  }, [backendUsers, notify]);

  const handleSaveUser = async (userData) => {
    if (selectedUser) {
      // Edit existing user
      const result = await updateUser(selectedUser.id, userData);
      if (result.success) {
        setShowUserModal(false);
        await loadStatistics();
      }
    } else {
      // Create new user
      const result = await createUser(userData);
      if (result.success) {
        setShowUserModal(false);
        await loadStatistics();
      }
    }
  };

  const handleExportExcel = useCallback(() => {
    try {
      const dataToExport = userData.map(
        ({ id, avatar, _original, ...rest }) => rest
      );
      exportToExcel(
        dataToExport,
        `Users_Export_${new Date().toISOString().split("T")[0]}.xlsx`,
        "Users"
      );
      notify.success("Users exported to Excel successfully!");
    } catch (error) {
      notify.error("Failed to export data");
      console.error(error);
    }
  }, [userData, notify]);

  const handleExportPdf = useCallback(() => {
    try {
      const pdfCols = [
        { key: "name", header: "User Name" },
        { key: "email", header: "Email" },
        { key: "role", header: "Role" },
        { key: "status", header: "Status" }
      ];
      generateStatPdfReport(`Users_Export`, pdfCols, userData);
      notify.success("Users exported to PDF successfully!");
    } catch (error) {
      notify.error("Failed to export PDF");
      console.error(error);
    }
  }, [userData, notify]);

  const handleDownloadPdfRow = useCallback((row) => {
    const pdfCols = [
      { key: "name", header: "User Name" },
      { key: "email", header: "Email" },
      { key: "role", header: "Role" },
      { key: "status", header: "Status" }
    ];
    generateStatPdfReport(`${row.name || "User"} - Profile`, pdfCols, [row]);
    notify.success("PDF generated successfully!");
  }, [notify]);

  const handleAvailabilityChange = useCallback(async (row, newAvailability) => {
    try {
      await updateUser(row.id, { user_status: newAvailability });
      notify.success(`Availability updated to ${newAvailability}`);
      fetchUsers({ ...activeFilters, page: pagination?.currentPage || 1 });
    } catch (err) {
      notify.error("Failed to update availability");
      console.error(err);
    }
  }, [updateUser, fetchUsers, activeFilters, pagination, notify]);

  const handleRoleChange = useCallback(async (row, newRole) => {
    try {
      await updateUser(row.id, { role: newRole });
      notify.success(`Role updated to ${newRole}`);
      fetchUsers({ ...activeFilters, page: pagination?.currentPage || 1 });
    } catch (err) {
      notify.error("Failed to update role");
      console.error(err);
    }
  }, [updateUser, fetchUsers, activeFilters, pagination, notify]);

  const handleRankChange = useCallback(async (row, newRank) => {
    if (!newRank) return;
    try {
      await usersApi.assignByPosition(row.id, newRank);
      notify.success(`Rank updated to ${newRank}`);
      fetchUsers({ ...activeFilters, page: pagination?.currentPage || 1 });
    } catch (err) {
      notify.error("Failed to update rank");
      console.error(err);
    }
  }, [fetchUsers, activeFilters, pagination, notify]);

  const handleStatusChange = useCallback(async (row, newStatus) => {
    try {
      const updateData = { status: newStatus };
      
      // If an applicant is set to Active, automatically approve them as Crew
      if (row.role === "Employee" && newStatus === "Active") {
        updateData.role = "Crew";
      }

      await updateUser(row.id, updateData);
      
      if (updateData.role === "Crew" && row.role === "Employee") {
        notify.success(`Applicant approved and moved to Crew successfully!`);
      } else {
        notify.success(`Status updated to ${newStatus}`);
      }
      
      fetchUsers({ ...activeFilters, page: pagination?.currentPage || 1 });
    } catch (err) {
      notify.error("Failed to update status");
      console.error(err);
    }
  }, [updateUser, fetchUsers, activeFilters, pagination, notify]);

  const handleRefresh = useCallback(() => {
    fetchUsers({ ...activeFilters, page: pagination?.currentPage || 1 });
  }, [fetchUsers, activeFilters, pagination]);

  // ✅ Table columns
  const userColumns = useMemo(
    () => [
      {
        key: "index",
        title: "#",
        width: 60,
        sortable: false,
        render: (val) => val,
      },
      {
        key: "name",
        title: "User Name",
        width: 360,
        showAvatar: true,
        sortable: true,
        render: (value, row) => (
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span>{row.name}</span>
            {row.isOnline && (
              <span
                style={{
                  width: "8px",
                  height: "8px",
                  borderRadius: "50%",
                  backgroundColor: "#54D14D",
                  display: "inline-block",
                }}
                title="Online now"
              />
            )}
          </div>
        ),
      },
      {
        key: "email",
        title: "Email",
        width: 250,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "phone",
        title: "Contact",
        width: 150,
        sortable: true,
        render: (value) => value,
      },
      // Conditionally show rank based on activeTab? We can just show it for now, 
      // or check if activeTab is "Applicants" or "All"
      activeTab !== "Internal" ? {
        key: "rank",
        title: "Rank",
        width: 140,
        sortable: true,
        render: (value, row) => (
          <div style={{ display: 'flex', justifyContent: 'center' }} onClick={(e) => e.stopPropagation()}>
            <div className="relative inline-block w-[130px]">
              <select
                value={value === "N/A" ? "" : value}
                onChange={(e) => handleRankChange(row, e.target.value)}
                disabled={!canEdit}
                className="appearance-none w-full border text-xs font-semibold rounded-full py-1.5 pl-4 pr-8 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500/40 transition-colors bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700"
              >
                <option value="">N/A</option>
                  {positions.map((pos, idx) => {
                    const val = pos.label || pos.value || pos;
                    return <option key={idx} value={val}>{val}</option>;
                  })}
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 opacity-60">
                <ChevronDown size={14} />
              </div>
            </div>
          </div>
        ),
      } : null,
      {
        key: "role",
        title: "Role",
        width: 140,
        sortable: true,
        render: (value, row) => {
          const roleColors = {
            Admin: "#BF4DD1",
            "HR Manager": "#35C2FD",
            Recruiter: "#54D14D",
            Employee: "#FFC107",
            Crew: "#06B6D4",
          };
          return (
            <div style={{ display: 'flex', justifyContent: 'center' }} onClick={(e) => e.stopPropagation()}>
              <div className="relative inline-block w-[130px]">
                <select
                  value={value === "Applicant" ? "Employee" : value === "Approved Crew" ? "Crew" : value}
                  onChange={(e) => handleRoleChange(row, e.target.value)}
                  disabled={!canEdit}
                  className="appearance-none w-full border text-xs font-semibold rounded-full py-1.5 pl-4 pr-8 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500/40 transition-colors bg-slate-100 border-slate-200 dark:bg-slate-800 dark:border-slate-700"
                  style={{ color: roleColors[value] || roleColors[value === "Applicant" ? "Employee" : "Crew"] || "#475569" }}
                >
                  <option value="Admin">Admin</option>
                  <option value="HR Manager">HR Manager</option>
                  <option value="Recruiter">Recruiter</option>
                  <option value="Employee">Applicant</option>
                  <option value="Crew">Crew</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 opacity-60">
                  <ChevronDown size={14} />
                </div>
              </div>
            </div>
          );
        },
      },
      {
        key: "status",
        title: "Status",
        width: 140,
        sortable: true,
        headerAlign: "center",
        render: (value, row) => {
          const isActive = value === "Active";
          const statusClass = isActive 
              ? "bg-emerald-100 text-emerald-700 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-400 dark:border-emerald-800/50" 
              : "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700";
          
          return (
            <div style={{ display: 'flex', justifyContent: 'center' }} onClick={(e) => e.stopPropagation()}>
              <div className="relative inline-block w-[110px]">
                <select
                  value={value}
                  onChange={(e) => handleStatusChange(row, e.target.value)}
                  disabled={!canEdit}
                  className={`appearance-none w-full border text-xs font-semibold rounded-full py-1.5 pl-4 pr-8 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500/40 transition-colors ${statusClass}`}
                >
                  <option value="Active" className="bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100">Active</option>
                  <option value="Inactive" className="bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100">Inactive</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 opacity-60">
                  <ChevronDown size={14} />
                </div>
              </div>
            </div>
          );
        },
      },
      {
        key: "availability",
        title: "Availability",
        width: 160,
        sortable: true,
        headerAlign: "center",
        render: (value, row) => {
          const isVacation = value === "VACATION" || value === "MEDICAL VACATION";
          const statusClass = isVacation 
              ? "bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400 dark:border-amber-800/50" 
              : "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800/50";
          
          return (
            <div style={{ display: 'flex', justifyContent: 'center' }} onClick={(e) => e.stopPropagation()}>
              <div className="relative inline-block w-[150px]">
                <select
                  value={value}
                  onChange={(e) => handleAvailabilityChange(row, e.target.value)}
                  disabled={!canEdit}
                  className={`appearance-none w-full border text-xs font-semibold rounded-full py-1.5 pl-4 pr-8 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500/40 transition-colors ${statusClass}`}
                >
                  <option value="ON_SITE" className="bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100">On Site</option>
                  <option value="VACATION" className="bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100">Vacation</option>
                  <option value="MEDICAL VACATION" className="bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100">Medical Vacation</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 opacity-60">
                  <ChevronDown size={14} />
                </div>
              </div>
            </div>
          );
        },
      },
      {
        key: "actions",
        title: "Actions",
        width: 160,
        render: (_, row) => (
          <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => handleView(row)}
              className="p-1.5 text-blue-500 hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
              title="View Details"
            >
              <Eye size={18} />
            </button>
            {canEdit && (
              <>
                <button
                  onClick={() => handleEditUser(row)}
                  className="p-1.5 text-emerald-500 hover:bg-emerald-50 dark:text-emerald-400 dark:hover:bg-emerald-900/20 rounded-lg transition-colors"
                  title="Edit User"
                >
                  <Edit2 size={18} />
                </button>
                <button
                  onClick={() => handleManageRanks(row)}
                  className="p-1.5 text-amber-500 hover:bg-amber-50 dark:text-amber-400 dark:hover:bg-amber-900/20 rounded-lg transition-colors"
                  title="Manage Ranks"
                >
                  <Award size={18} />
                </button>
              </>
            )}
            <button
              onClick={() => handleDownloadPdfRow(row)}
              className="p-1.5 text-indigo-500 hover:bg-indigo-50 dark:text-indigo-400 dark:hover:bg-indigo-900/20 rounded-lg transition-colors"
              title="Download Profile"
            >
              <Download size={18} />
            </button>
            {canDelete && (
              <button
                onClick={() => handleDeleteUser(row.id)}
                className="p-1.5 text-rose-500 hover:bg-rose-50 dark:text-rose-400 dark:hover:bg-rose-900/20 rounded-lg transition-colors"
                title="Delete User"
              >
                <Trash2 size={18} />
              </button>
            )}
          </div>
        ),
      },
    ].filter(Boolean),
    [canEdit, canDelete, handleDeleteUser, handleEditUser, handleManageRanks, handleDownloadPdfRow, activeTab, positions, handleRankChange, handleRoleChange, handleAvailabilityChange]
  );

  // Helper function to extract unique values from deep objects safely (preventing circular reference crashes)
  const getUniqueValuesForKey = useCallback((items, searchKey) => {
    const values = new Set();
    const visited = new Set();
    const extract = (obj, depth = 0) => {
      if (!obj || depth > 8) return;
      if (typeof obj === 'object') {
        if (visited.has(obj)) return;
        visited.add(obj);
        
        if (Array.isArray(obj)) {
          obj.forEach(item => extract(item, depth + 1));
        } else {
          if (obj[searchKey] !== undefined && obj[searchKey] !== null && obj[searchKey] !== "") {
            values.add(String(obj[searchKey]));
          }
          for (const key in obj) {
            if (Object.prototype.hasOwnProperty.call(obj, key)) {
              const val = obj[key];
              if (val && typeof val === 'object') {
                extract(val, depth + 1);
              }
            }
          }
        }
      }
    };
    items.forEach(item => extract(item, 0));
    return Array.from(values).sort().map(v => ({ value: v, label: v }));
  }, []);

  const dynamicShipNames = useMemo(() => getUniqueValuesForKey(backendUsers, "ship_name"), [backendUsers, getUniqueValuesForKey]);
  const dynamicNearestPorts = useMemo(() => getUniqueValuesForKey(backendUsers, "nearest_port"), [backendUsers, getUniqueValuesForKey]);
  const dynamicLanguages = useMemo(() => getUniqueValuesForKey(backendUsers, "language"), [backendUsers, getUniqueValuesForKey]);
  const dynamicCourses = useMemo(() => getUniqueValuesForKey(backendUsers, "course_name"), [backendUsers, getUniqueValuesForKey]);
  const dynamicJobPositions = useMemo(() => getUniqueValuesForKey(backendUsers, "job_position_name"), [backendUsers, getUniqueValuesForKey]);
  const dynamicPassportTypes = useMemo(() => getUniqueValuesForKey(backendUsers, "passport_type"), [backendUsers, getUniqueValuesForKey]);
  const dynamicSeamanBookTypes = useMemo(() => getUniqueValuesForKey(backendUsers, "seaman_book_type"), [backendUsers, getUniqueValuesForKey]);
  const dynamicDocumentTypes = useMemo(() => getUniqueValuesForKey(backendUsers, "document_type"), [backendUsers, getUniqueValuesForKey]);

  const filterSections = useMemo(() => [
    {
      title: "Personal Information",
      fields: [
        { key: "name", label: "First Name", type: "text", colSpan: 12 },
        { key: "age", label: "Age", type: "number", colSpan: 4 },
        {
          key: "marital_status",
          label: "Marital Status",
          type: "multi-select",
          multiple: true,
          colSpan: 4,
          options: [
            { value: "SINGLE", label: "Single" },
            { value: "MARRIED", label: "Married" },
            { value: "DIVORCED", label: "Divorced" },
            { value: "WIDOWED", label: "Widowed" },
          ],
        },
        {
          key: "user_status",
          label: "User Status",
          type: "multi-select",
          multiple: true,
          colSpan: 4,
          options: [
            { value: "ON_SITE", label: "On Site" },
            { value: "VACATION", label: "Vacation" },
            { value: "MEDICAL VACATION", label: "Medical Vacation" },
          ],
        },
        {
          key: "nationality",
          label: "Nationality",
          type: "multi-select",
          multiple: true,
          colSpan: 4,
          options: referenceData?.flags?.map(f => ({ value: f.name || f.label, label: f.name || f.label })) || []
        },
        { 
          key: "nearest_port", 
          label: "Nearest Port", 
          type: "text", 
          colSpan: 4,
          placeholder: "Type a port name..."
        },
        { 
          key: "language", 
          label: "Language", 
          type: "text", 
          colSpan: 4,
          placeholder: "Type a language..."
        },
      ],
    },
    {
      title: "Professional Details",
      fields: [
        {
          key: "rank_name",
          label: "Rank Name",
          type: "multi-select",
          multiple: true,
          options: referenceData?.ranks?.map(r => ({ value: r.name || r.label || r.rank_name, label: r.name || r.label || r.rank_name })) || []
        },
        { key: "assigned_code", label: "Assigned Code", type: "text" },
        {
          key: "role",
          label: "User Role",
          type: "multi-select",
          multiple: true,
          options: [
            { value: "Employee", label: "Applicant" },
            { value: "HR Manager", label: "HR Manager" },
            { value: "Recruiter", label: "Recruiter" },
            { value: "Crew", label: "Approved Crew" },
          ],
        },
        {
          key: "position",
          label: "General Position",
          type: "multi-select",
          multiple: true,
          options: referenceData?.positions?.map(p => ({ value: p.label, label: p.label })) || []
        },
        { 
          key: "course_name", 
          label: "Marine Course", 
          type: "text",
          placeholder: "Type a course name..."
        },
      ],
    },
    {
      title: "Assignment & Vessels",
      fields: [
        {
          key: "company_name",
          label: "Principal Name",
          type: "multi-select",
          multiple: true,
          options: referenceData?.companies?.map(c => ({ value: c.name || c.label || c.company_name, label: c.name || c.label || c.company_name })) || []
        },
        {
          key: "ship_name",
          label: "Vessel Name",
          type: "multi-select",
          multiple: true,
          options: referenceData?.ships?.map(s => ({ value: s.name || s.label || s.ship_name, label: s.name || s.label || s.ship_name })) || []
        },
        {
          key: "company_type",
          label: "Principal Type",
          type: "multi-select",
          multiple: true,
          options: [
            { value: "Shipping Manning Principals", label: "Shipping Manning Principals" },
            { value: "Cargo Manning Principals", label: "Cargo Manning Principals" },
            { value: "Cruise & Hospitality Manning Principals", label: "Cruise & Hospitality Manning Principals" },
            { value: "Offshore & Oil/Gas Manning Principals", label: "Offshore & Oil/Gas Manning Principals" },
            { value: "Fishing Fleet Manning Principals", label: "Fishing Fleet Manning Principals" },
            { value: "General Crew Manning Principals", label: "General Crew Manning Principals" },
            { value: "Specialized Marine Manning Principals", label: "Specialized Marine Manning Principals" },
            { value: "Temporary / Contract Manning Agencies", label: "Temporary / Contract Manning Agencies" },
            { value: "Full Crew Management Principals", label: "Full Crew Management Principals" },
          ]
        },
        {
          key: "ship_type",
          label: "Vessel Type",
          type: "multi-select",
          multiple: true,
          options: [
            { value: "Container Vessels", label: "Container Vessels" },
            { value: "Bulk Carriers", label: "Bulk Carriers" },
            { value: "Tankers", label: "Tankers" },
            { value: "Ro-Ro Vessels", label: "Ro-Ro Vessels" },
            { value: "Passenger Vessels", label: "Passenger Vessels" },
            { value: "Fishing Vessels", label: "Fishing Vessels" },
            { value: "Recreational", label: "Recreational" },
            { value: "Offshore Support Vessels", label: "Offshore Support Vessels" },
            { value: "Icebreakers", label: "Icebreakers" },
            { value: "Tugboats", label: "Tugboats" },
          ]
        },
        { 
          key: "job_position_name", 
          label: "Job Position", 
          type: "text",
          placeholder: "Type a job position..."
        },
      ],
    },
    {
      title: "Contract Details",
      fields: [
        {
          key: "contract_status",
          label: "Contract Status",
          type: "multi-select",
          multiple: true,
          colSpan: 12,
          options: [
            { value: "Draft", label: "Draft" },
            { value: "Signed", label: "Signed" },
            { value: "Active", label: "Active" },
            { value: "Completed", label: "Completed" },
            { value: "Terminated", label: "Terminated" },
          ],
        },
        { key: "signed_on_from", label: "Signed On From", type: "date", colSpan: 6 },
        { key: "signed_on_to", label: "Signed On To", type: "date", colSpan: 6 },
        { key: "signed_off_from", label: "Signed Off From", type: "date", colSpan: 6 },
        { key: "signed_off_to", label: "Signed Off To", type: "date", colSpan: 6 },
      ],
    },
    {
      title: "Documentation",
      fields: [
        { key: "passport_no", label: "Passport No", type: "text", colSpan: 6 },
        { 
          key: "passport_type", 
          label: "Passport Type", 
          type: "text", 
          colSpan: 6,
          placeholder: "Type passport type..."
        },
        { key: "passport_expiry_from", label: "Passport Expiry From", type: "date", colSpan: 6 },
        { key: "passport_expiry_to", label: "Passport Expiry To", type: "date", colSpan: 6 },
        { key: "seaman_book_no", label: "Seaman Book No", type: "text", colSpan: 6 },
        { 
          key: "seaman_book_type", 
          label: "Seaman Book Type", 
          type: "text", 
          colSpan: 6,
          placeholder: "Type seaman book type..."
        },
        { key: "seaman_book_expiry_from", label: "Seaman Book Expiry From", type: "date", colSpan: 6 },
        { key: "seaman_book_expiry_to", label: "Seaman Book Expiry To", type: "date", colSpan: 6 },
        { key: "medical_no", label: "Medical No", type: "text", colSpan: 6 },
        {
          key: "document_type",
          label: "General Document Type",
          type: "multi-select",
          multiple: true,
          colSpan: 6,
          options: dynamicDocumentTypes
        },
        { key: "medical_expiry_from", label: "Medical Expiry From", type: "date", colSpan: 6 },
        { key: "medical_expiry_to", label: "Medical Expiry To", type: "date", colSpan: 6 },
      ],
    },
    {
      title: "Status",
      fields: [
        { 
          key: "is_blacklisted", 
          label: "Blacklisted Only", 
          type: "checkbox",
          options: [
            { value: "true", label: "Show Blacklisted Users Only" }
          ]
        },
      ],
    },
  ], [
    referenceData, 
    dynamicShipNames, 
    dynamicNearestPorts, 
    dynamicLanguages, 
    dynamicCourses, 
    dynamicJobPositions, 
    dynamicPassportTypes, 
    dynamicSeamanBookTypes, 
    dynamicDocumentTypes
  ]);

  const filterFields = useMemo(() => filterSections.flatMap(s => s.fields), [filterSections]);

  const handleTabChange = useCallback((tab) => {
    setActiveTab(tab);
    if (tab === "All") {
      setActiveFilters(prev => ({ ...prev, role: "" }));
      fetchUsers({ ...buildBackendFilters({ ...activeFilters, role: "" }), page: 1 });
    } else if (tab === "Internal") {
      setActiveFilters(prev => ({ ...prev, role: "Admin,HR Manager,Recruiter" }));
      fetchUsers({ ...buildBackendFilters({ ...activeFilters, role: "Admin,HR Manager,Recruiter" }), page: 1 });
    } else if (tab === "Applicants") {
      setActiveFilters(prev => ({ ...prev, role: "Employee" }));
      fetchUsers({ ...buildBackendFilters({ ...activeFilters, role: "Employee" }), page: 1 });
    } else if (tab === "Crew") {
      setActiveFilters(prev => ({ ...prev, role: "Crew" }));
      fetchUsers({ ...buildBackendFilters({ ...activeFilters, role: "Crew" }), page: 1 });
    }
  }, [activeFilters, buildBackendFilters, fetchUsers]);

  const headerHeight = Math.round(80 * scale);

  return (
    <main style={getMainContainerStyles(scale, headerHeight)}>
      <style>{generateAllPageStyles(scale)}</style>

      {/* User Statistics Section */}
      <div
        style={{
          marginBottom: `${Math.round(32 * scale)}px`,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "flex-start",
            gap: `${Math.round(24 * scale)}px`,
            marginBottom: `${Math.round(24 * scale)}px`,
            flexWrap: isMobile ? "wrap" : "nowrap",
          }}
        >
          <div style={{ flex: isMobile ? "1 1 100%" : "1" }}>
            <StackedProgressLegendCard
              segments={userSegments}
              rows={userRows}
              width={747.53}
              height={214}
              scale={scale}
              loading={usersLoading}
            />
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 dark:border-slate-700 mb-6 gap-6 px-2">
        {["All", "Internal", "Applicants", "Crew"].map(tab => (
          <button
            key={tab}
            className={`pb-3 px-2 font-medium text-sm transition-colors border-b-2 ${
              activeTab === tab 
                ? "border-blue-600 text-blue-600 dark:border-blue-500 dark:text-blue-500" 
                : "border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
            }`}
            onClick={() => handleTabChange(tab)}
          >
            {tab === "Internal" ? "Internal Staff" : tab === "Applicants" ? "Applicants" : tab === "Crew" ? "Crew" : "All Users"}
          </button>
        ))}
      </div>

      {/* Users Table Section */}
      <section>
        <div style={getRowBetweenStyles(scale)}>
          <h2
            style={{
              ...getPageTitleStyles(scale),
              marginBottom: `${Math.round(8 * scale)}px`,
            }}
          >
            User Management
          </h2>

          <div style={{ display: "flex", gap: `${Math.round(8 * scale)}px`, alignItems: "center" }}>
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
            {canCreate && (
              <Button
                variant="primary"
                onClick={handleAddUser}
                scale={scale}
                style={{ minHeight: 30, height: 30, padding: "0 14px", fontSize: 13, borderRadius: 8, fontWeight: 500, lineHeight: "30px" }}
              >
                Add User
              </Button>
            )}
            {userData.length > 0 && (
              <>
                <Button
                  variant="outline"
                  onClick={handleExportPdf}
                  scale={scale}
                  style={{ minHeight: 30, height: 30, padding: "0 14px", fontSize: 13, borderRadius: 8, fontWeight: 500, lineHeight: "30px" }}
                >
                  Export PDF
                </Button>
                <Button
                  variant="outline"
                  onClick={handleExportExcel}
                  scale={scale}
                  style={{ minHeight: 30, height: 30, padding: "0 14px", fontSize: 13, borderRadius: 8, fontWeight: 500, lineHeight: "30px" }}
                >
                  Export Excel
                </Button>
              </>
            )}
          </div>
        </div>

        <DataTableLayout
          columns={userColumns}
          storageKey="users-table"
          fields={filterFields}
          filters={activeFilters}
          onFilterChange={(k, v) => setActiveFilters(prev => ({ ...prev, [k]: v }))}
          onApplyFilters={() => fetchUsers({ ...buildBackendFilters(activeFilters), page: 1 })}
          onClearFilters={() => {
            setActiveFilters({});
            fetchUsers({ ...buildBackendFilters({}), page: 1 });
          }}
          isSidebarOpen={isSidebarOpen}
          onSidebarToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        >
          {selectedIds.length > 0 && (canDelete || canEdit) && (
            <div className="mb-4">
              <BulkActionBar
                selectedCount={selectedIds.length}
                onClearSelection={() => setSelectedIds([])}
                actions={[
                  ...(canEdit ? [
                    {
                      icon: <Edit2 size={16} />,
                      label: "Bulk Edit",
                      onClick: () => setShowBulkUpdateModal(true),
                      variant: "primary"
                    }
                  ] : []),
                  ...(canDelete ? [
                    {
                      icon: <Trash2 size={16} />,
                      label: "Delete Selected",
                      onClick: handleBulkDelete,
                      variant: "danger"
                    }
                  ] : [])
                ]}
              />
            </div>
          )}
          <AdvancedDataTable
            data={userData}
            columns={userColumns}
            keyField="id"
            selectedIds={selectedIds}
            onSelectionChange={setSelectedIds}
            onRowClick={handleView}
            isLoading={usersLoading}
          />
        </DataTableLayout>
        <div style={{ marginTop: "20px" }}>
          <Pagination
            page={pagination.currentPage}
            pageSize={pagination.pageSize || 50}
            total={pagination.count}
            onChange={handlePageChange}
            scale={scale}
            showInfo={true}
          />
        </div>

        {viewingUser?.role === "Employee" || viewingUser?.role === "Crew" ? (
          <CVSubmissionEditModal
            isOpen={showViewModal}
            onClose={() => setShowViewModal(false)}
            submission={{
              id: viewingUser.id,
              generated_id: viewingUser.assigned_code,
              user: viewingUser,
              user_name: viewingUser.name || viewingUser.first_name + " " + viewingUser.last_name,
              profile_image: viewingUser.profile_image
            }}
          />
        ) : (
          <UserViewModal
            isOpen={showViewModal}
            onClose={() => setShowViewModal(false)}
            user={viewingUser}
            scale={scale}
            canDelete={canDelete}
          />
        )}
      </section>

      {showUserModal && (
        <UserFormModal
          user={selectedUser}
          onClose={() => setShowUserModal(false)}
          onSave={handleSaveUser}
          scale={scale}
        />
      )}

      {showBulkUpdateModal && (
        <BulkUpdateModal
          isOpen={showBulkUpdateModal}
          selectedCount={selectedIds.length}
          onClose={() => setShowBulkUpdateModal(false)}
          onApply={handleBulkUpdate}
        />
      )}

      {showRankModal && (
        <RankManagementModal
          isOpen={showRankModal}
          onClose={() => {
            setShowRankModal(false);
            setRankModalUser(null);
          }}
          user={rankModalUser}
          scale={scale}
        />
      )}

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        onClose={() => {
          setShowDeleteConfirm(false);
          setUserToDelete(null);
        }}
        onConfirm={handleConfirmDelete}
        title="Delete User"
        message="Are you sure you want to delete this user? This action cannot be undone."
        confirmLabel="Delete"
        variant="danger"
        scale={scale}
        loading={usersLoading}
      />

      {/* View Loading Overlay */}
      {viewLoading && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 9999,
            background: "rgba(15, 23, 42, 0.55)",
            backdropFilter: "blur(4px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            gap: Math.round(16 * scale),
          }}
        >
          <div
            style={{
              width: Math.round(52 * scale),
              height: Math.round(52 * scale),
              border: `${Math.round(4 * scale)}px solid rgba(255,255,255,0.15)`,
              borderTopColor: "#6366F1",
              borderRadius: "50%",
              animation: "user-spin 0.75s linear infinite",
            }}
          />
          <p
            style={{
              color: "#fff",
              fontSize: Math.round(14 * scale),
              fontWeight: 500,
              margin: 0,
            }}
          >
            Loading user profile...
          </p>
          <style>{`@keyframes user-spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      )}
    </main>
  );
}

