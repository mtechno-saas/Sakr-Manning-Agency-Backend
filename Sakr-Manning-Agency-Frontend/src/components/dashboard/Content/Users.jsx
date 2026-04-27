/* eslint-disable no-unused-vars */

// Content/Users.jsx - COMPLETE with Full CRUD Operations
import React, { useState, useEffect, useMemo, useCallback } from "react";
import { StackedProgressLegendCard } from "../Components/Cards/StatisticsCards";
import { RefinedDataTable } from "../Components/Data/RefinedDataTable";
import { ASSETS } from "../../../utils/constants";
import { exportToCSV, exportToJSON } from "../../../utils/exportHelpers";

import { COLORS, TOKENS } from "../Constants";
import {
  generateAllPageStyles,
  getMainContainerStyles,
  getPageTitleStyles,
  getRowBetweenStyles,
} from "../Styles/cssClasses";
import Button from "../Components/Common/Button";
import FilterModel from "../Components/Common/FilterModel";
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

export function UserManagement({ scale = 1, isMobile }) {
  const { notify } = useNotification();
  const { canCreate, canEdit, canDelete } = usePermissions();

  // Helper: Check if user is online (last login within 1 hour)
  const isUserOnline = (lastLogin) => {
    // console.log(lastLogin);
    if (!lastLogin) return false;
    const lastLoginDate = new Date(lastLogin);
    const now = new Date();
    const hoursDiff = (now - lastLoginDate) / (1000 * 60 * 60);
    return hoursDiff <= 1;
  };

  // Helper: Format last login date
  const formatLastLogin = (lastLogin) => {
    // console.log(lastLogin);
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

  // Load users and stats on mount
  useEffect(() => {
    fetchUsers();
    loadStatistics();
  }, []);

  // Load statistics
  const loadStatistics = async () => {
    const result = await fetchUserStats();
    // console.log("the user stats : ", result);
    if (result.success) {
      setStatistics(result.data);
    }
  };

  // Transform backend users to match UI format
  const userData = useMemo(() => {
    // console.log("the backend user data : ", backendUsers);
    return backendUsers.map((user) => ({
      id: user.id,
      name: `${user.first_name || ""} ${user.middle_name || ""}`.trim(),
      email: user.email,
      role: user.role,
      status:
        user.user_status === "On Site" || user.user_status === "ON_SITE"
          ? "Active"
          : "Inactive",
      // status: user.user_status,
      avatar: user.profile_image || ASSETS.LOGO,

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

  // ✅ Table filters
  // Filter state for backend filtering
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [filters, setFilters] = useState({
    search: "",
    status: "",
    role: "",
  });
  const [activeFilters, setActiveFilters] = useState({
    search: "",
    status: "",
    role: "",
  });

  // Check if any filters are active
  const hasActiveFilters = activeFilters.search || activeFilters.status || activeFilters.role;

  // Handle page change for server-side pagination
  const handlePageChange = useCallback(
    (newPage) => {
      // Build current filters for pagination context
      const backendFilters = {};

      // Align with Document.html: search -> name
      if (activeFilters.search) backendFilters.name = activeFilters.search;

      // "role" is NOT in Document.html, but keeping as it likely maps to internal staff roles
      if (activeFilters.role) backendFilters.role = activeFilters.role;

      // Align with Document.html: Status values "On Site" / "Vacation"
      if (activeFilters.status === 'Active') backendFilters.user_status = 'On Site';
      if (activeFilters.status === 'Inactive') backendFilters.user_status = 'Vacation';

      fetchUsers({ ...backendFilters, page: newPage });
    },
    [fetchUsers, activeFilters]
  );

  // Backend filter handlers
  const handleApplyFilters = useCallback(() => {
    setActiveFilters({ ...filters });
    setShowFilterModal(false);

    const backendFilters = {};

    // Align with Document.html: search -> name
    if (filters.search) backendFilters.name = filters.search;

    // "role" is NOT in Document.html, but keeping as it likely maps to internal staff roles
    if (filters.role) backendFilters.role = filters.role;

    // Align with Document.html: Status values "On Site" / "Vacation"
    if (filters.status === 'Active') backendFilters.user_status = 'On Site';
    if (filters.status === 'Inactive') backendFilters.user_status = 'Vacation';

    fetchUsers({ ...backendFilters, page: 1 });
  }, [filters, fetchUsers]);

  const handleResetFilters = useCallback(() => {
    const emptyFilters = { search: "", status: "", role: "" };
    setFilters(emptyFilters);
    setActiveFilters(emptyFilters);
    setShowFilterModal(false);
    fetchUsers({ page: 1 });
  }, [fetchUsers]);

  const stats = useMemo(() => {
    return {
      admin: userData.filter((d) => d.role === "Admin").length,
      hr_manager: userData.filter((d) => d.role === "HR Manager").length,
      recruiter: userData.filter((d) => d.role === "Recruiter").length,
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
    async (id) => {
      if (!canDelete) {
        notify.error("You do not have permission to delete users");
        return;
      }

      if (window.confirm("Are you sure you want to delete this user?")) {
        const result = await deleteUser(id);
        if (result.success) {
          await loadStatistics(); // Reload stats after deletion
        }
      }
    },
    [canDelete, deleteUser, notify]
  );

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

  // TODOs:
  // const handleConfirmDelete = useCallback(async () => {
  //   setIsLoading(true);
  //   try {
  //     await userAPI.delete(userToDelete);

  //     const newData = userData.filter((item) => item.id !== userToDelete);
  //     updateAllData("users", newData);

  //     notify.success("User deleted successfully!");
  //     setShowDeleteConfirm(false);
  //     setUserToDelete(null);
  //   } catch (error) {
  //     notify.error("Failed to delete user");
  //     console.error(error);
  //   } finally {
  //     setIsLoading(false);
  //   }
  // }, [userData, userToDelete, updateAllData, notify]);

  // const handleSubmitAdd = useCallback(
  //   async (formData) => {
  //     setIsLoading(true);
  //     try {
  //       const result = await userAPI.create(formData);

  //       const newUser = {
  //         ...formData,
  //         id: result.id,
  //         lastLogin: new Date().toISOString().split("T")[0],
  //         avatar: ASSETS.LOGO,
  //       };

  //       const newData = [newUser, ...userData];
  //       updateAllData("users", newData);

  //       notify.success("User added successfully!");
  //       setShowAddModal(false);
  //     } catch (error) {
  //       notify.error("Failed to add user");
  //       console.error(error);
  //     } finally {
  //       setIsLoading(false);
  //     }
  //   },
  //   [userData, updateAllData, notify]
  // );

  // const handleSubmitEdit = useCallback(
  //   async (formData) => {
  //     setIsLoading(true);
  //     try {
  //       await userAPI.update(selectedUser.id, formData);

  //       const newData = userData.map((user) =>
  //         user.id === selectedUser.id ? { ...user, ...formData } : user
  //       );

  //       updateAllData("users", newData);

  //       notify.success("User updated successfully!");
  //       setShowEditModal(false);
  //       setSelectedUser(null);
  //     } catch (error) {
  //       notify.error("Failed to update user");
  //       console.error(error);
  //     } finally {
  //       setIsLoading(false);
  //     }
  //   },
  //   [userData, selectedUser, updateAllData, notify]
  // );

  // ✅ Export Handlers
  const handleExportCSV = useCallback(() => {
    try {
      const dataToExport = userData.map(
        ({ id, avatar, ...rest }) => rest
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

  const handleExportJSON = useCallback(() => {
    try {
      const dataToExport = userData.map(({ avatar, ...rest }) => rest);
      exportToJSON(
        dataToExport,
        `Users_Export_${new Date().toISOString().split("T")[0]}.json`
      );
      notify.success("Users exported to JSON successfully!");
    } catch (error) {
      notify.error("Failed to export data");
      console.error(error);
    }
  }, [userData, notify]);

  // ✅ Table columns
  const userColumns = useMemo(
    () => [
      {
        key: "name",
        title: "User Name",
        width: 200,
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
      {
        key: "lastLogin",
        title: "Last Login",
        width: 100,
        sortable: true,
        render: (value) => value,
      },
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

  const filterFields = [
    {
      key: "status",
      label: "Status",
      type: "select",
      placeholder: "All Statuses",
      options: [
        { value: "Active", label: "Active" },
        { value: "Inactive", label: "Inactive" },
      ],
    },
    {
      key: "role",
      label: "Role",
      type: "select",
      placeholder: "All Roles",
      options: [
        { value: "Admin", label: "Admin" },
        { value: "HR Manager", label: "HR Manager" },
        { value: "Recruiter", label: "Recruiter" },
        { value: "Employee", label: "Employee" },
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
          {/* TODO: */}
          <div
            style={{
              backgroundColor: COLORS.white,
              borderRadius: `${Math.round(22 * scale)}px`,
              padding: `${Math.round(24 * scale)}px`,
              boxShadow: TOKENS.shadow.sm,
              flex: isMobile ? "1 1 100%" : "0 0 auto",
              minWidth: `${Math.round(300 * scale)}px`,
            }}
          >
            <h3
              style={{
                fontSize: `${Math.round(18 * scale)}px`,
                fontWeight: 600,
                color: COLORS.darkText,
                margin: `0 0 ${Math.round(16 * scale)}px 0`,
                fontFamily: "Poppins, sans-serif",
              }}
            >
              User Summary
            </h3>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: `${Math.round(12 * scale)}px`,
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  padding: "8px 0",
                }}
              >
                <div
                  style={{
                    width: "12px",
                    height: "12px",
                    borderRadius: "50%",
                    backgroundColor: "#4299e1",
                    flexShrink: 0,
                  }}
                />
                <span
                  style={{
                    fontFamily: "Poppins, sans-serif",
                    fontWeight: 500,
                    fontSize: "16px",
                    color: COLORS.darkText,
                  }}
                >
                  Total Users
                </span>
                <span
                  style={{
                    marginLeft: "auto",
                    fontFamily: "Poppins, sans-serif",
                    fontWeight: 500,
                    fontSize: "16px",
                    color: COLORS.darkText,
                  }}
                >
                  {statistics?.total_users || userData.length}
                </span>
              </div>

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  padding: "8px 0",
                }}
              >
                <div
                  style={{
                    width: "12px",
                    height: "12px",
                    borderRadius: "50%",
                    backgroundColor: "#54D14D",
                    flexShrink: 0,
                  }}
                />
                <span
                  style={{
                    fontFamily: "Poppins, sans-serif",
                    fontWeight: 500,
                    fontSize: "16px",
                    color: COLORS.darkText,
                  }}
                >
                  Active Users
                </span>
                <span
                  style={{
                    marginLeft: "auto",
                    fontFamily: "Poppins, sans-serif",
                    fontWeight: 500,
                    fontSize: "16px",
                    color: COLORS.darkText,
                  }}
                >
                  {statistics?.active_users ||
                    userData.filter((u) => u.status === "Active").length}
                </span>
              </div>

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  padding: "8px 0",
                }}
              >
                <div
                  style={{
                    width: "12px",
                    height: "12px",
                    borderRadius: "50%",
                    backgroundColor: "#35C2FD",
                    flexShrink: 0,
                  }}
                />
                <span
                  style={{
                    fontFamily: "Poppins, sans-serif",
                    fontWeight: 500,
                    fontSize: "16px",
                    color: COLORS.darkText,
                  }}
                >
                  Online Now
                </span>
                <span
                  style={{
                    marginLeft: "auto",
                    fontFamily: "Poppins, sans-serif",
                    fontWeight: 500,
                    fontSize: "16px",
                    color: COLORS.darkText,
                  }}
                >
                  {onlineUsersCount}
                </span>
              </div>
            </div>
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
          <Button
            variant="icon"
            scale={scale}
            onClick={() => setShowFilterModal(true)}
            ariaLabel="Filter users"
            title="Filter users"
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

        <RefinedDataTable
          data={userData}
          columns={userColumns}
          rowKey="id"
          scale={scale}
          pageSize={pagination.pageSize || 25}
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

        {/* User View Modal */}
        <UserViewModal
          isOpen={showViewModal}
          onClose={() => setShowViewModal(false)}
          user={viewingUser}
          scale={scale}
          canDelete={canDelete}
        />

        {/* Server-side Pagination - only when NO filters active */}
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

        {/* Action Buttons */}
        {canCreate && (
          <div
            style={{
              display: "flex",
              justifyContent: "flex-end",
              gap: `${Math.round(12 * scale)}px`,
              marginTop: `${Math.round(20 * scale)}px`,
            }}
          >
            <Button variant="primary" onClick={handleAddUser} scale={scale}>
              Add User
            </Button>
            {userData.length > 0 && (
              <>
                <Button
                  variant="outline"
                  onClick={handleExportCSV}
                  scale={scale}
                >
                  Export CSV
                </Button>
                <Button
                  variant="outline"
                  onClick={handleExportJSON}
                  scale={scale}
                >
                  Export JSON
                </Button>
              </>
            )}
          </div>
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

      {showRankModal && (
        <RankManagementModal
          isOpen={showRankModal}
          onClose={() => { setShowRankModal(false); setRankModalUser(null); }}
          user={rankModalUser}
          scale={scale}
        />
      )}

      {/* Filter Modal */}
      <FilterModel
        isOpen={showFilterModal}
        onClose={() => setShowFilterModal(false)}
        title="Filter Users"
        fields={filterFields}
        values={filters}
        onValuesChange={setFilters}
        onApply={handleApplyFilters}
        onReset={handleResetFilters}
        scale={scale}
      />

      {/* <ConfirmDialog
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
        loading={isLoading}
      /> */}
    </main>
  );
}
