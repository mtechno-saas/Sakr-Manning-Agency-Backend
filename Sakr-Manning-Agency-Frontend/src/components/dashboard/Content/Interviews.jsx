/* eslint-disable no-unused-vars */

// Content/Interviews.jsx - COMPLETE with Full CRUD + Calendar + Backend Filtering
import React, { useState, useEffect, useMemo, useCallback } from "react";
import { SmallProgressCard } from "../Components/Cards/StatisticsCards";
import { Video, Phone, Users, Info, Filter, Calendar as LucideCalendar } from "lucide-react";
import { ASSETS } from "../../../utils/constants";
import { exportToCSV, exportToJSON } from "../../../utils/exportHelpers";
import { getMediaUrl } from "../../../utils/fileHelpers";

import {
  generateAllPageStyles,
  getMainContainerStyles,
  getPageTitleStyles,
} from "../Styles/cssClasses";
import Button from "../Components/Common/Button";
import Calendar from "../Components/Common/Calender";
import ConfirmDialog from "../Components/Common/ConfirmDialog";
import LoadingScreen from "../Components/Common/LoadingScreen";

import InterviewFormModal from "../Components/Modal/InterviewFormModal";
import { InterviewViewModal } from "../Components/Modal/ViewModal";
import EnhancedFilterModel from "../Components/Common/EnhancedFilterModel";
import Pagination from "../../common/Pagination";
import SavedFilters from "../Components/Common/SavedFilters";

import useNotification from "../hooks/useNotification";

import usePermissions from "../../../hooks/dashboard/usePermissions";
import useInterviews from "../../../hooks/dashboard/useInterviews";
import { useDashboardData } from "../context/DashboardDataContext";
import { useCompanies } from "../../../hooks/dashboard/useCompanies";
import { useRanks } from "../../../hooks/dashboard/useRanks";

export function InterviewManagement({ scale = 1, isMobile = false }) {
  const { notify } = useNotification();

  const { canScheduleInterviews, canEdit, canDelete } = usePermissions();

  // UI Helper Functions
  const getInterviewTypeLabel = (type) => {
    switch (type?.toLowerCase()) {
      case "video":
        return "Video Call";
      case "phone":
        return "Phone Call";
      case "in-person":
        return "In-Person";
      default:
        return type;
    }
  };

  const getInterviewTypeIcon = (type) => {
    const size = Math.round(18 * scale);
    const color = "#6B7280"; // Neutral gray
    
    switch (type?.toLowerCase()) {
      case "video":
        return <Video size={size} color={color} />;
      case "phone":
        return <Phone size={size} color={color} />;
      case "in-person":
        return <Users size={size} color={color} />;
      default:
        return <Info size={size} color={color} />;
    }
  };

  const formatInterviewDate = (dateStr) => {
    if (!dateStr) return "TBD";
    try {
      // Parse YYYY-MM-DD safely to avoid timezone shifts
      const [year, month, day] = dateStr.split("-").map(Number);
      const date = new Date(year, month - 1, day);
      
      return date.toLocaleDateString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
      });
    } catch (e) {
      return dateStr;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "Completed":
      case "Confirmed":
        return "#14A40F";
      case "Scheduled":
        return "#1976D2";
      case "Pending":
        return "#757575";
      case "Cancelled":
        return "#F44336";
      case "Rescheduled":
        return "#FF9800";
      default:
        return "#333333";
    }
  };

  const getStatusLabel = (status) => {
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  // Use custom hook for interviews data
  const {
    interviews: backendInterviews,
    loading: interviewsLoading,
    fetchInterviews,
    createInterview,
    updateInterview,
    deleteInterview,
    fetchInterviewStats,
    pagination
  } = useInterviews();

  const { companies, fetchCompanies: fetchAllCompanies } = useCompanies();
  const { ranks, fetchRanks } = useRanks();

  // centralized data
  const { fetchCompaniesByIds, companyMap, getCompanyName, users } = useDashboardData();

  // Modal states
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [selectedInterview, setSelectedInterview] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);
  const [interviewToDelete, setInterviewToDelete] = useState(null);
  const [statistics, setStatistics] = useState(null);

  // View modal state
  const [showViewModal, setShowViewModal] = useState(false);
  const [viewingInterview, setViewingInterview] = useState(null);

  // ✅ Filter State
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [filters, setFilters] = useState({
    candidate: "",
    status: "",
    company: "",
    scheduled_date: "",
    scheduled_date_from: "",
    scheduled_date_to: "",
  });
  const [activeFilters, setActiveFilters] = useState({
    candidate: "",
    status: "",
    company: "",
    scheduled_date: "",
    scheduled_date_from: "",
    scheduled_date_to: "",
  });
  const [savedPresets, setSavedPresets] = useState([]);

  // Load interviews and stats on mount
  useEffect(() => {
    fetchInterviews({ ...activeFilters });
    loadStatistics();
    fetchAllCompanies({ page_size: 1000 });
    fetchRanks();
  }, [fetchInterviews, activeFilters, fetchAllCompanies, fetchRanks]);

  // Batch fetch companies when interviews load
  useEffect(() => {
    if (backendInterviews.length > 0) {
      const companyIds = backendInterviews
        .map((i) => i.company)
        .filter((id) => id !== null && id !== undefined);

      if (companyIds.length > 0) {
        fetchCompaniesByIds(companyIds);
      }
    }
  }, [backendInterviews, fetchCompaniesByIds]);


  // Load statistics
  const loadStatistics = useCallback(async () => {
    const result = await fetchInterviewStats();
    if (result.success) {
      setStatistics(result.data);
    }
  }, [fetchInterviewStats]);

  // Transform backend interviews to match UI format
  const interviews = useMemo(() => {
    return backendInterviews.map((interview, index) => ({
      index: (pagination.currentPage - 1) * (pagination.pageSize || 50) + index + 1,
      id: interview.id,
      candidateId: interview.candidate,
      candidateName: `${interview?.candidate_name.split(" ")[0]} ${interview?.candidate_name.split(" ")[1] || ""}` || "Unknown Candidate",
      candidateEmail: interview.candidate_email || "",
      companyId: interview.company || "Unknown Company ID",
      company: interview.company_name || getCompanyName(interview.company),
      duration: interview.duration_minutes || 0,
      positionID: interview.position || "Not Specified",
      position: interview.position_name || "Not Specified",
      date: interview.scheduled_date,
      time: interview.scheduled_time
        ? interview.scheduled_time.substring(0, 5)
        : "00:00", // Format HH:MM
      type: interview.interview_type || "Video",
      status: interview.status || "Scheduled",
      meetingLink: interview.meeting_link || "",

      notes: interview.notes || "",
      feedback: interview.feedback || "",
      meetingResult: interview.result || "",
      interviewer_name: interview.interviewer_name || "",
      interviewer_email: interview.interviewer_email || "",
      location: interview.location || "",

      avatar: getMediaUrl(interview.candidate?.profile_image) || ASSETS.LOGO,
      createdAt: interview.created_at,
      createdBy: interview.created_by,
      // Store original data for editing
      _original: interview,
    }));
  }, [backendInterviews, companyMap]);

  // Interview statistics (use backend stats if available)
  const interviewStats = useMemo(() => {
    if (!statistics || !interviews.length) {
      return { today: 0, thisWeek: 0, pending: 0 };
    }

    const today = new Date().toISOString().split("T")[0];

    const now = new Date();
    const dayOfWeek = now.getDay();
    const weekStart = new Date(now);
    weekStart.setDate(now.getDate() - dayOfWeek);
    weekStart.setHours(0, 0, 0, 0);

    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekStart.getDate() + 6);
    weekEnd.setHours(23, 59, 59, 999);

    const todayCount = interviews.filter(
      (interview) => interview.date === today
    ).length;

    const thisWeekCount = interviews.filter((interview) => {
      const interviewDate = new Date(interview.date);
      return interviewDate >= weekStart && interviewDate <= weekEnd;
    }).length;

    const pendingCount =
      (statistics.scheduled || 0) + (statistics.rescheduled || 0);

    return {
      today: todayCount,
      thisWeek: thisWeekCount,
      pending: pendingCount,
    };
  }, [interviews, statistics]);

  // ============================================
  // FILTER HANDLERS
  // ============================================
  const handleApplyFilters = useCallback(() => {
    setActiveFilters(filters);
    setShowFilterModal(false);
    fetchInterviews({ ...filters, page: 1 });
  }, [filters, fetchInterviews]);

  const handlePageChange = useCallback((newPage) => {
    fetchInterviews({ ...activeFilters, page: newPage });
  }, [fetchInterviews, activeFilters]);

  const handleApplyPreset = useCallback((preset) => {
    setFilters(preset);
    setActiveFilters(preset);
    fetchInterviews({ ...preset, page: 1 });
  }, [fetchInterviews]);

  const handleSavePreset = useCallback((name, vals) => {
    setSavedPresets(prev => [...prev, { name, filters: vals }]);
  }, []);

  const handleDeletePreset = useCallback((name) => {
    setSavedPresets(prev => prev.filter(p => p.name !== name));
  }, []);

  const filterFields = [
    {
      key: "candidate",
      label: "Candidate",
      type: "select",
      placeholder: "Select Candidate",
      options: users.map(u => ({ value: u.id, label: `${u.first_name} ${u.last_name}` })),
    },
    {
      key: "company",
      label: "Company",
      type: "select",
      placeholder: "All Companies",
      options: companies.map(c => ({ value: c.id, label: c.company_name || c.name })),
    },
    {
      key: "status",
      label: "Status",
      type: "select",
      placeholder: "All Statuses",
      options: [
        { value: "Scheduled", label: "Scheduled" },
        { value: "Completed", label: "Completed" },
        { value: "Cancelled", label: "Cancelled" },
        { value: "Pending", label: "Pending" },
        { value: "No Show", label: "No Show" },
        { value: "Rescheduled", label: "Rescheduled" },
      ],
    },
    {
      key: "scheduled_date",
      label: "Specific Date",
      type: "date",
    },
    {
      key: "scheduled_date_from",
      label: "Date From",
      type: "date",
    },
    {
      key: "scheduled_date_to",
      label: "Date To",
      type: "date",
    },
  ];

  const handleResetFilters = useCallback(() => {
    const emptyFilters = {
      candidate: "",
      status: "",
      company: "",
      scheduled_date: "",
      scheduled_date_from: "",
      scheduled_date_to: "",
    };
    setFilters(emptyFilters);
    setActiveFilters(emptyFilters);
    setShowFilterModal(false);
    fetchInterviews({ page: 1 });
  }, [fetchInterviews]);

  // ============================================
  // CRUD HANDLERS
  // ============================================
  const handleDateClick = useCallback(
    (day, currentDate) => {
      if (!canScheduleInterviews) {
        notify.error("You do not have permission to schedule interviews");
        return;
      }

      const dateStr = `${currentDate.getFullYear()}-${String(
        currentDate.getMonth() + 1
      ).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
      setSelectedDate(dateStr);
      setSelectedInterview(null);
      setShowAddModal(true);
    },
    [canScheduleInterviews, notify]
  );

  const handleInterviewClick = useCallback((interview) => {
    // Open View Modal on Calendar click instead of Edit
    setViewingInterview(interview._original || interview);
    setShowViewModal(true);
  }, []);

  const handleViewInterview = useCallback((interview) => {
    setViewingInterview(interview._original || interview);
    setShowViewModal(true);
  }, []);

  const handleAddInterview = useCallback(
    async (formData) => {
      const result = await createInterview(formData);
      if (result.success) {
        setShowAddModal(false);
        setSelectedDate(null);
        await loadStatistics();
      }
    },
    [createInterview, loadStatistics]
  );

  const handleEditInterview = useCallback(
    async (formData) => {
      if (!selectedInterview) return;

      // selectedInterview is now the raw backend object; use its id directly
      const interviewId = selectedInterview.id;
      const result = await updateInterview(interviewId, formData);
      if (result.success) {
        setShowEditModal(false);
        setSelectedInterview(null);
        await loadStatistics();
      }
    },
    [selectedInterview, updateInterview, loadStatistics]
  );

  const handleDeleteClick = useCallback(
    (interview) => {
      if (!canDelete && !canScheduleInterviews) {
        notify.error("You do not have permission to delete interviews");
        return;
      }

      setInterviewToDelete(interview.id);
      setShowDeleteConfirm(true);
    },
    [canDelete, canScheduleInterviews, notify]
  );

  const handleConfirmDelete = useCallback(async () => {
    if (!interviewToDelete) return;

    const result = await deleteInterview(interviewToDelete);
    if (result.success) {
      setShowDeleteConfirm(false);
      setInterviewToDelete(null);
      await loadStatistics();
    }
  }, [interviewToDelete, deleteInterview, loadStatistics]);

  const handleStatusChange = useCallback(
    async (id, newStatus) => {
      if (!canEdit && !canScheduleInterviews) {
        notify.error("You do not have permission to update interview status");
        return;
      }

      const interview = backendInterviews.find((i) => i.id === id);
      if (!interview) return;

      const statusMap = {
        pending: "Scheduled",
        confirmed: "Completed",
        scheduled: "Scheduled",
      };

      const backendStatus = statusMap[newStatus] || "Scheduled";

      const result = await updateInterview(id, { status: backendStatus });
      if (result.success) {
        notify.success(`Interview ${newStatus} successfully!`);
        await loadStatistics();
      }
    },
    [
      backendInterviews,
      updateInterview,
      canEdit,
      canScheduleInterviews,
      loadStatistics,
      notify,
    ]
  );


  const handleRefresh = useCallback(() => {
    fetchInterviews({ ...activeFilters, page: pagination?.currentPage || 1 });
  }, [fetchInterviews, activeFilters, pagination]);

  const headerHeight = Math.round(101 * scale);
  const cardGap = Math.round(20 * scale);

  return (
    <main style={getMainContainerStyles(scale, headerHeight)}>
      <style>{generateAllPageStyles(scale)}</style>

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
          Manage and schedule candidate interviews
        </h1>

        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          {/* <Button
            variant="icon"
            onClick={() => setShowFilterModal(true)}
            ariaLabel="Filter interviews"
            title="Filter interviews"
            scale={scale}
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

      {/* Statistics Cards Row */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: `${cardGap}px`,
          marginBottom: `${Math.round(32 * scale)}px`,
          overflowX: "auto",
          paddingBottom: `${Math.round(8 * scale)}px`,
          scrollBehavior: "smooth",
        }}
      >
        <SmallProgressCard
          title="Today's Interviews"
          percent={interviewStats.today}
          width={345}
          height={85}
          scale={scale}
          fillColor="#54D14D"
        />
        <SmallProgressCard
          title="This Week"
          percent={interviewStats.thisWeek}
          width={345}
          height={85}
          scale={scale}
          fillColor="#EF7E5D"
        />
        <SmallProgressCard
          title="Total Interviews"
          flag="total"
          percent={interviewStats.pending}
          width={345}
          height={85}
          scale={scale}
          fillColor="#35C2FD"
        />
      </div>

      {/* Interview Calendar */}
      <div style={{ marginBottom: `${Math.round(32 * scale)}px` }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: `${Math.round(16 * scale)}px`,
          }}
        >
          <h2
            style={{
              fontSize: `${Math.round(22 * scale)}px`,
              fontWeight: 500,
              color: "#000000",
              margin: 0,
            }}
          >
            Interview Calendar
          </h2>
        </div>
        <Calendar
          interviews={interviews}
          onDateClick={handleDateClick}
          onInterviewClick={handleInterviewClick}
          scale={scale}
        />
      </div>

      {/* Interviews List */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: `${Math.round(20 * scale)}px`,
        }}
      >
        <h2
          style={{
            fontSize: `${Math.round(22 * scale)}px`,
            fontWeight: 500,
            color: "#000000",
            margin: 0,
          }}
        >
          Upcoming Interviews
        </h2>

        {interviewsLoading ? (
          <div style={{ backgroundColor: "#FFFFFF", borderRadius: `${Math.round(22 * scale)}px`, padding: `${Math.round(60 * scale)}px`, textAlign: "center" }}>
            <LoadingScreen scale={scale} message="Loading interviews..." subMessage="Fetching upcoming candidate meetings and evaluations" />
          </div>
        ) : interviews.length > 0 ? (
          interviews.map((interview) => (
            <div
              key={interview.id}
              style={{
                backgroundColor: "#FFFFFF",
                borderRadius: `${Math.round(22 * scale)}px`,
                padding: `${Math.round(12 * scale)}px`,
                boxShadow: "0px 1px 2px rgba(0, 0, 0, 0.04)",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: `${Math.round(47 * scale)}px`,
              }}
            >
              {/* Left Section */}
              <div
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: `${Math.round(66 * scale)}px`,
                  flex: 1,
                  paddingTop: `${Math.round(4 * scale)}px`
                }}
              >
                {/* Date & Time */}
                <div
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: `${Math.round(8 * scale)}px`,
                    minWidth: `${Math.round(154 * scale)}px`,
                  }}
                >
                  <div
                    style={{
                      fontSize: `${Math.round(14 * scale)}px`,
                      fontWeight: 600,
                      color: "#9CA3AF",
                      width: `${Math.round(24 * scale)}px`,
                      flexShrink: 0,
                      textAlign: "center",
                      marginTop: `${Math.round(8 * scale)}px`
                    }}
                  >
                    {interview.index}
                  </div>
                  <img
                    src={interview.avatar}
                    alt={interview.candidateName}
                    style={{
                      width: `${Math.round(30 * scale)}px`,
                      height: `${Math.round(30 * scale)}px`,
                      borderRadius: "50%",
                      objectFit: "cover",
                      flexShrink: 0,
                    }}
                  />
                  <div>
                    <div
                      style={{
                        fontSize: `${Math.round(18 * scale)}px`,
                        fontWeight: 600,
                        color: "#1F2937",
                        fontFamily: "Inter, sans-serif",
                        marginBottom: `${Math.round(2 * scale)}px`
                      }}
                    >
                      {formatInterviewDate(interview.date)}
                    </div>
                    <div
                      style={{
                        fontSize: `${Math.round(16 * scale)}px`,
                        fontWeight: 500,
                        color: "#6B7280",
                        fontFamily: "Inter, sans-serif",
                      }}
                    >
                      {interview.time}
                    </div>
                  </div>
                </div>

                {/* Candidate Info */}
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: `${Math.round(8 * scale)}px`,
                  }}
                >
                  <div
                    style={{
                      fontSize: `${Math.round(20 * scale)}px`,
                      fontWeight: 500,
                      color: "#000000",
                      fontFamily: "Poppins, sans-serif",
                    }}
                  >
                    {interview.candidateName}
                  </div>
                  <div
                    style={{
                      fontSize: `${Math.round(20 * scale)}px`,
                      fontWeight: 500,
                      color: "#000000",
                      fontFamily: "Poppins, sans-serif",
                    }}
                  >
                    {interview.position}
                  </div>
                  <div
                    style={{
                      fontSize: `${Math.round(20 * scale)}px`,
                      fontWeight: 500,
                      color: "#4986D0",
                      fontFamily: "Poppins, sans-serif",
                    }}
                  >
                    {interview.company}
                  </div>
                </div>

                {/* Interview Type */}
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    alignSelf: "center",
                    gap: `${Math.round(4 * scale)}px`,
                    backgroundColor: "#F3F4F6",
                    padding: `${Math.round(6 * scale)}px ${Math.round(10 * scale)}px`,
                    borderRadius: `${Math.round(12 * scale)}px`,
                    minWidth: "fit-content",
                    whiteSpace: "nowrap"
                  }}
                >
                  {getInterviewTypeIcon(interview.type)}
                  <span
                    style={{
                      fontSize: `${Math.round(16 * scale)}px`,
                      fontWeight: 500,
                      color: "#374151",
                      fontFamily: "Inter, sans-serif",
                    }}
                  >
                    {getInterviewTypeLabel(interview.type)}
                  </span>
                </div>
              </div>

              {/* Right Section: Status & Actions */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: `${Math.round(11 * scale)}px`,
                }}
              >
                {/* Status Button */}
                <Button
                  variant="primary"
                  scale={scale}
                  onClick={() => {
                    if (interview.status === "pending") {
                      handleStatusChange(interview.id, "confirm");
                    }
                  }}
                  style={{
                    backgroundColor: getStatusColor(interview.status),
                    width: `${Math.round(150 * scale)}px`,
                    height: `${Math.round(45 * scale)}px`,
                  }}
                >
                  {getStatusLabel(interview.status)}
                </Button>

                {/* View Button */}
                <Button
                  variant="primary"
                  scale={scale}
                  onClick={() => handleViewInterview(interview)}
                  style={{
                    backgroundColor: "#3B82F6",
                    width: `${Math.round(80 * scale)}px`,
                    height: `${Math.round(45 * scale)}px`,
                  }}
                >
                  View
                </Button>

                {/* Edit Button */}
                {(canEdit || canScheduleInterviews) && (
                  <Button
                    variant="primary"
                    scale={scale}
                    onClick={() => {
                      setSelectedInterview(interview._original || interview);
                      setShowEditModal(true);
                    }}
                    style={{
                      width: `${Math.round(80 * scale)}px`,
                      height: `${Math.round(45 * scale)}px`,
                    }}
                  >
                    Edit
                  </Button>
                )}

                {/* Delete Button */}
                {(canDelete || canScheduleInterviews) && (
                  <Button
                    variant="danger"
                    scale={scale}
                    onClick={() => handleDeleteClick(interview)}
                    style={{
                      width: `${Math.round(80 * scale)}px`,
                      height: `${Math.round(45 * scale)}px`,
                    }}
                  >
                    Delete
                  </Button>
                )}
              </div>
            </div>
          ))
        ) : (
          <div
            style={{
              backgroundColor: "#FFFFFF",
              borderRadius: `${Math.round(22 * scale)}px`,
              padding: `${Math.round(60 * scale)}px`,
              textAlign: "center",
            }}
          >
            <div
              style={{
                marginBottom: "20px",
                display: "flex",
                justifyContent: "center",
                color: "#D1D5DB"
              }}
            >
              <LucideCalendar size={Math.round(64 * scale)} />
            </div>
            <h3
              style={{
                fontSize: `${Math.round(24 * scale)}px`,
                fontWeight: 600,
                color: "#000000",
                margin: 0,
                marginBottom: "12px",
              }}
            >
              No Interviews Scheduled
            </h3>
            <p
              style={{
                fontSize: `${Math.round(14 * scale)}px`,
                color: "#8C8C8C",
              }}
            >
              Click on the calendar to schedule your first interview
            </p>
          </div>
        )}

        {/* Pagination */}
        {!interviewsLoading && interviews.length > 0 && (
          <div style={{ marginTop: `${Math.round(20 * scale)}px` }}>
            <Pagination
              page={pagination?.currentPage || 1}
              pageSize={pagination?.pageSize || 50} // or 25 fixed
              total={pagination?.count || 0}
              onChange={handlePageChange}
              scale={scale}
              showInfo={true}
            />
          </div>
        )}
      </div>

      {/* <EnhancedFilterModel
        isOpen={showFilterModal}
        onClose={() => setShowFilterModal(false)}
        values={filters}
        onValuesChange={setFilters}
        onApply={handleApplyFilters}
        onReset={handleResetFilters}
        fields={filterFields}
        scale={scale}
        title="Filter Interviews"
      /> */}

      {showAddModal && (
        <InterviewFormModal
          isOpen={showAddModal}
          interview={null}
          onClose={() => {
            setShowAddModal(false);
            setSelectedDate(null);
          }}
          onSave={handleAddInterview}
          preSelectedDate={selectedDate}
          scale={scale}
        />
      )}

      {showEditModal && selectedInterview && (
        <InterviewFormModal
          isOpen={showEditModal}
          interview={selectedInterview}
          onClose={() => {
            setShowEditModal(false);
            setSelectedInterview(null);
          }}
          onSave={handleEditInterview}
          scale={scale}
        />
      )}

      {showDeleteConfirm && (
        <ConfirmDialog
          isOpen={showDeleteConfirm}
          onClose={() => {
            setShowDeleteConfirm(false);
            setInterviewToDelete(null);
          }}
          onConfirm={handleConfirmDelete}
          title="Delete Interview"
          message="Are you sure you want to delete this interview? This action cannot be undone."
          confirmLabel="Delete"
          variant="danger"
          scale={scale}
          loading={interviewsLoading}
        />
      )}

      {/* Interview View Modal */}
      <InterviewViewModal
        isOpen={showViewModal}
        onClose={() => {
          setShowViewModal(false);
          setViewingInterview(null);
        }}
        interview={viewingInterview}
        onDelete={(id) => {
          setShowViewModal(false);
          setViewingInterview(null);
          setInterviewToDelete(id);
          setShowDeleteConfirm(true);
        }}
        scale={scale}
        canDelete={canDelete || canScheduleInterviews}
      />
    </main>
  );
}
