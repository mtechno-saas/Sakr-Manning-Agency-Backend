/* eslint-disable no-unused-vars */

// Content/Users.jsx - COMPLETE with Full CRUD Operations
import React, { useState, useEffect, useMemo, useCallback } from "react";
import { StackedProgressLegendCard } from "../Components/Cards/StatisticsCards";
import { RefinedDataTable } from "../Components/Data/RefinedDataTable";
import { ASSETS } from "../../../utils/constants";
import { exportToCSV, exportToJSON } from "../../../utils/exportHelpers";
import { getMediaUrl } from "../../../utils/fileHelpers";

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
import RankManagementModal from "../Components/Modal/RankManagementModal";
import { userService } from "../../../services/Form/userService";

import Pagination from "../../common/Pagination";
// import useTableFilters from "../hooks/useTableFilters"; // Removed for server-side filtering
import useNotification from "../hooks/useNotification";

import usePermissions from "../../../hooks/dashboard/usePermissions";
import useUsers from "../../../hooks/dashboard/useUsers";
import { useReferenceDataContext } from "../../../context/ReferenceDataContext";

export function UserManagement({ scale = 1, isMobile }) {
  const { notify } = useNotification();
  const { canCreate, canEdit, canDelete } = usePermissions();
  const referenceData = useReferenceDataContext();

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
    fetchUserStats,
    pagination,
  } = useUsers();

  // Local state
  const [showUserModal, setShowUserModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showViewModal, setShowViewModal] = useState(false);
  const [viewingUser, setViewingUser] = useState(null);
  const [viewLoading, setViewLoading] = useState(false);
  const [statistics, setStatistics] = useState(null);

  // Rank management modal
  const [showRankModal, setShowRankModal] = useState(false);
  const [rankModalUser, setRankModalUser] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);

  // Load users and stats on mount
  useEffect(() => {
    fetchUsers();
    loadStatistics();
  }, []);

  // Load statistics
  const loadStatistics = async () => {
    const result = await fetchUserStats();
    if (result.success) {
      setStatistics(result.data);
    }
  };

  // Transform backend users to match UI format
  const userData = useMemo(() => {
    return backendUsers.map((user, index) => ({
      index: (pagination.currentPage - 1) * (pagination.pageSize || 50) + index + 1,
      id: user.id,
      // name: `${user.first_name.split(" ")[0] || ""} ${user.middle_name.split(" ")[0] || ""}`.trim(),
      name: user.first_name + " " + user.middle_name,
      email: user.email,
      role: user.role,
      status:
        user.user_status === "On Site" || user.user_status === "ON_SITE"
          ? "Active"
          : "Inactive",
      // status: user.user_status,
      avatar: getMediaUrl(user.profile_image) || ASSETS.LOGO,

      lastLogin: formatLastLogin(user.last_login),
      isOnline: isUserOnline(user.last_login),

      assignedCode: user.ranks[0]?.assigned_code,
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
      ];
    }

    // Use backend statistics
    return [
      { key: "admin", color: "#BF4DD1", pct: statistics.admins || 1 },
      { key: "hr_manager", color: "#35C2FD", pct: statistics.hr_managers || 1 },
      { key: "recruiter", color: "#54D14D", pct: statistics.recruiters || 1 },
      { key: "employee", color: "#FFC107", pct: statistics.employees || 1 },
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
          label: "Employee",
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
        label: "Employee",
        remaining: `${statistics.employees || 0} users`,
      },
    ];
  }, [statistics, userData]);

  // Calculate online users (last login within 1 hour)
  const onlineUsersCount = useMemo(() => {
    return userData.filter((user) => user.isOnline).length;
  }, [userData]);

  // ✅ Table filters — keys match BE query params directly
  const [activeFilters, setActiveFilters] = useState({});
  const [showFilterModal, setShowFilterModal] = useState(false);

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
    setShowFilterModal(false);
    fetchUsers({ ...buildBackendFilters(activeFilters), page: 1 });
  }, [activeFilters, fetchUsers, buildBackendFilters]);

  const handleResetFilters = useCallback(() => {
    setActiveFilters({});
    fetchUsers({ page: 1 });
    setShowFilterModal(false);
  }, [fetchUsers]);

  const stats = useMemo(() => {
    return {
      admin: userData.filter((d) => d.role === "Admin").length,
      hr_manager: userData.filter((d) => d.role === "HR Manager").length,
      recruiter: userData.filter((d) => d.role === "Recruiter").length,
      employee: userData.filter((d) => d.role === "Employee").length,
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

  const handleExportCSV = useCallback(() => {
    try {
      const dataToExport = userData.map(
        ({ id, avatar, _original, ...rest }) => rest
      );
      exportToCSV(
        dataToExport,
        `Users_Export_${new Date().toISOString().split("T")[0]}.csv`
      );
      notify.success("Users exported to CSV successfully!");
    } catch (error) {
      notify.error("Failed to export data");
      console.error(error);
    }
  }, [userData, notify]);

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
        width: 300,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "role",
        title: "Role",
        width: 80,
        sortable: true,
        render: (value) => {
          const roleColors = {
            Admin: "#BF4DD1",
            "HR Manager": "#35C2FD",
            Recruiter: "#54D14D",
            Employee: "#FFC107",
            Craw: "#FFC107",
          };
          return (
            <span
              style={{
                color: roleColors[value] || "#000000",
                fontWeight: 500,
              }}
            >
              {value}
            </span>
          );
        },
      },
      // {
      //   key: "lastLogin",
      //   title: "Last Login",
      //   width: 100,
      //   sortable: true,
      //   render: (value) => value,
      // },
      {
        key: "status",
        title: "status",
        width: 100,
        sortable: true,
        isStatus: true,
        headerAlign: "center",
        headerTextAlign: "center",
        render: (value) => value,
      },
      {
        key: "actions",
        title: "Actions",
        width: 160,
        isActions: true,
        onView: handleView,
        onEdit: canEdit ? handleEditUser : undefined,
        onDelete: canDelete ? handleDeleteUser : undefined,
        onRank: canEdit ? handleManageRanks : undefined,
      },
    ],
    [canEdit, canDelete, handleDeleteUser, handleEditUser, handleManageRanks]
  );

  const filterSections = [
    {
      title: "Personal Information",
      fields: [
        { key: "name", label: "First Name", type: "text", colSpan: 12 },
        { key: "age", label: "Age", type: "number", colSpan: 4 },
        {
          key: "marital_status",
          label: "Marital Status",
          type: "multi-select",
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
          colSpan: 4,
          options: [
            { value: "ON_SITE", label: "On Site" },
            { value: "VACATION", label: "Vacation" },
            { value: "MEDICAL VACATION", label: "Medical Vacation" },
          ],
        },
        { key: "nationality", label: "Nationality", type: "text", colSpan: 4 },
        { key: "nearest_port", label: "Nearest Port", type: "text", colSpan: 4 },
        { key: "language", label: "Language", type: "text", colSpan: 4 },
      ],
    },
    {
      title: "Professional Details",
      fields: [
        { key: "rank_name", label: "Rank Name", type: "text" },
        { key: "assigned_code", label: "Assigned Code", type: "text" },
        {
          key: "role",
          label: "User Role",
          type: "multi-select",
          options: [
            { value: "Employee", label: "Employee" },
            { value: "Admin", label: "Admin" },
            { value: "Recruiter", label: "Recruiter" },
            { value: "HR Manager", label: "HR Manager" },
          ],
        },
        { key: "position", label: "General Position", type: "text" },
        { key: "course_name", label: "Marine Course", type: "text" },
      ],
    },
    {
      title: "Assignment & Vessels",
      fields: [
        { key: "company_name", label: "Company Name", type: "text" },
        { key: "ship_name", label: "Ship Name", type: "text" },
        { key: "company_type", label: "Company Type", type: "text" },
        { key: "ship_type", label: "Ship Type", type: "text" },
        { key: "job_position_name", label: "Job Position", type: "text" },
      ],
    },
    {
      title: "Contract Details",
      fields: [
        {
          key: "contract_status",
          label: "Contract Status",
          type: "multi-select",
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
        { key: "passport_type", label: "Passport Type", type: "text", colSpan: 6 },
        { key: "passport_expiry_from", label: "Passport Expiry From", type: "date", colSpan: 6 },
        { key: "passport_expiry_to", label: "Passport Expiry To", type: "date", colSpan: 6 },
        { key: "seaman_book_no", label: "Seaman Book No", type: "text", colSpan: 6 },
        { key: "seaman_book_type", label: "Seaman Book Type", type: "text", colSpan: 6 },
        { key: "seaman_book_expiry_from", label: "Seaman Book Expiry From", type: "date", colSpan: 6 },
        { key: "seaman_book_expiry_to", label: "Seaman Book Expiry To", type: "date", colSpan: 6 },
        { key: "medical_no", label: "Medical No", type: "text", colSpan: 6 },
        { key: "document_type", label: "General Document Type", type: "text", colSpan: 6 },
        { key: "medical_expiry_from", label: "Medical Expiry From", type: "date", colSpan: 6 },
        { key: "medical_expiry_to", label: "Medical Expiry To", type: "date", colSpan: 6 },
      ],
    },
    {
      title: "Status",
      fields: [
        { key: "is_blacklisted", label: "Blacklisted Only", type: "checkbox" },
      ],
    },
  ];
  const headerHeight = Math.round(101 * scale);

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

          <SavedFilters
            scale={scale}
            savedPresets={[]}
            currentFilters={activeFilters}
            onApplyPreset={(filters) => {
              setActiveFilters(filters);
              fetchUsers({ ...buildBackendFilters(filters), page: 1 });
            }}
            onSavePreset={() => { }}
            onDeletePreset={() => { }}
          />

          <div style={{ display: "flex", gap: `${Math.round(8 * scale)}px`, alignItems: "center" }}>
            <Button
              variant="icon"
              scale={scale}
              onClick={() => setShowFilterModal(true)}
              ariaLabel="Filter users"
              title="Filter users"
              style={{ width: 30, height: 30, borderRadius: 8, minHeight: 30 }}
            >
              <svg
                width={16}
                height={16}
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
              <Button
                variant="outline"
                onClick={handleExportCSV}
                scale={scale}
                style={{ minHeight: 30, height: 30, padding: "0 14px", fontSize: 13, borderRadius: 8, fontWeight: 500, lineHeight: "30px" }}
              >
                Export CSV
              </Button>
            )}
          </div>
        </div>

        <RefinedDataTable
          data={userData}
          columns={userColumns}
          rowKey="id"
          scale={scale}
          pageSize={pagination.pageSize || 50}
          initialPage={1}
          actions={
            canEdit && canDelete
              ? ["View", "Edit", "Download", "Delete"]
              : canEdit
                ? ["View", "Edit", "Download"]
                : ["View", "Download"]
          }
          onRowClick={handleView}
          styleOverrides={{ columnGap: 18 }}
          loading={usersLoading}
        />
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

        <UserViewModal
          isOpen={showViewModal}
          onClose={() => setShowViewModal(false)}
          user={viewingUser}
          scale={scale}
          canDelete={canDelete}
        />
      </section>

      {showUserModal && (
        <UserFormModal
          user={selectedUser}
          onClose={() => setShowUserModal(false)}
          onSave={handleSaveUser}
          scale={scale}
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

      {/* Filter Modal */}
      <EnhancedFilterModel
        isOpen={showFilterModal}
        onClose={() => setShowFilterModal(false)}
        values={activeFilters}
        onValuesChange={setActiveFilters}
        onApply={handleApplyFilters}
        onReset={handleResetFilters}
        sections={filterSections}
        scale={scale}
        title="Filter Users"
      />

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
