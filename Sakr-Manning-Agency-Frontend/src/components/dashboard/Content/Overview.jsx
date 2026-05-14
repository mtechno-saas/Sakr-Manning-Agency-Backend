/* eslint-disable no-unused-vars */

// Overview.jsx - UPDATED to match backend documentation KPIs
import React, { useEffect, useMemo, useState } from "react";
import { StatCard } from "../Components/Cards/StatCard";
import { ActivityItem } from "../Components/Cards/ActivityItem";
import { StatusBadge } from "../Components/Cards/StatusBadge";
import { RecommendationCard } from "../Components/Cards/RecommendationCard";
import LoadingScreen from "../Components/Common/LoadingScreen";
import { COLORS } from "../Constants";
import { ASSETS } from "../../../utils/constants";

// Data hooks
import useUsers from "../../../hooks/dashboard/useUsers";
import useCompanies from "../../../hooks/dashboard/useCompanies";
import useInterviews from "../../../hooks/dashboard/useInterviews";
import useDocuments from "../../../hooks/dashboard/useDocuments";
import useCVSubmissions from "../../../hooks/dashboard/useCVSubmissions";
import useCVDocuments from "../../../hooks/dashboard/useCVDocuments"; // Section 2

// ─────────────────────────────────────────────────────────────────────────────
// Helper: relative time string
// ─────────────────────────────────────────────────────────────────────────────
const formatTimestamp = (dateString) => {
  if (!dateString) return "Unknown time";
  const date = new Date(dateString);
  const diffMs = Date.now() - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? "s" : ""} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? "s" : ""} ago`;
  return date.toLocaleDateString();
};

// ─────────────────────────────────────────────────────────────────────────────
export const OverviewPage = ({ scale, isMobile, onNavigate }) => {
  // ── Navigation helpers ──────────────────────────────────────────────────
  const activityPageMap = {
    "New registration": "users",
    "Interview scheduled": "interviews",
    "Company registered": "management",
    "Contract generated": "documents",
    "CV submitted": "cvs",
  };

  const handleActivityClick = (title) => {
    if (onNavigate && activityPageMap[title]) onNavigate(activityPageMap[title]);
  };

  const handleRecommendationClick = () => onNavigate?.("cvs");

  // ── Hooks ───────────────────────────────────────────────────────────────
  const {
    users,
    loading: usersLoading,
    fetchUsers,
    getUserStatusCounts,
  } = useUsers();

  const {
    companies,
    loading: companiesLoading,
    fetchCompanies,
    fetchCompanyStats,
  } = useCompanies();

  const {
    interviews,
    loading: interviewsLoading,
    fetchInterviews,
    fetchInterviewStats,
  } = useInterviews();

  const {
    contracts,
    loading: documentsLoading,
    fetchContracts,
  } = useDocuments();

  // Switch to Section 2 for Overview CV badges
  const {
    documents: cvDocuments,
    loading: cvsLoading,
    fetchDocuments,
    pagination: cvPagination,
  } = useCVDocuments();

  const [companyStats, setCompanyStats] = useState(null);
  const [interviewStats, setInterviewStats] = useState(null);

  // ── Load all data on mount ──────────────────────────────────────────────
  useEffect(() => {
    const load = async () => {
      await Promise.all([
        fetchUsers(),
        fetchCompanies(),
        fetchInterviews(),
        fetchContracts(),
        fetchDocuments({ page_size: 1000 }), // Increase page size for local counting if no stats endpoint
        fetchInterviewStats().then(res => {
          if (res?.success) setInterviewStats(res.data);
        }),
      ]);
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load company stats once companies are available
  useEffect(() => {
    if (companies.length > 0 && fetchCompanyStats) {
      fetchCompanyStats().then((res) => {
        if (res?.success) setCompanyStats(res.data);
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [companies.length]);

  // ── Derived KPI values ──────────────────────────────────────────────────
  const kpis = useMemo(() => {
    // ── Seafarers ──
    const statusCounts = getUserStatusCounts();
    const totalSeafarers = statusCounts.total;
    const recentRegistrations = statusCounts.recentRegistrations;

    // ── CV Documents (Section 2 - Public Documents) ──
    const totalCVs = cvPagination.count || cvDocuments?.length || 0;

    // ── Companies ──
    const totalCompanies =
      companyStats?.total_companies ?? companies.length;
    const openPositions =
      companyStats?.total_open_positions ??
      companies.reduce((sum, c) => sum + (c.open_positions || 0), 0);

    return {
      totalSeafarers,
      totalCVs,
      totalCompanies,
      openPositions,
      recentRegistrations,
    };
  }, [
    companies,
    cvDocuments,
    cvPagination.count,
    companyStats,
    getUserStatusCounts,
  ]);

  // ── Stat card definitions (flat list of 5) ────────────────────────────
  const statCards = useMemo(
    () => [
      {
        title: "Total Seafarers",
        value: kpis.totalSeafarers.toString(),
        trend: "Registered in system",
        trendDirection: "up",
        icon: ASSETS.DASHBOARD_STATS_ICONS?.[4] || "👥",
        accent: COLORS.primary || "#1E40AF",
      },
      {
        title: "Total CVs",
        value: kpis.totalCVs?.toString(),
        trend: "All CV submissions",
        trendDirection: "up",
        icon: ASSETS.DASHBOARD_STATS_ICONS?.[0] || "📋",
        accent: "#7C3AED",
      },
      {
        title: "Total Companies",
        value: kpis.totalCompanies.toString(),
        trend: "Registered companies",
        trendDirection: "up",
        icon: ASSETS.DASHBOARD_STATS_ICONS?.[1] || "🏢",
        accent: "#1D4ED8",
      },
      {
        title: "Open Positions",
        value: kpis.openPositions.toString(),
        trend: "Across all companies",
        trendDirection: "up",
        icon: ASSETS.DASHBOARD_STATS_ICONS?.[2] || "💼",
        accent: "#166534",
      },
      {
        title: "New Registrations",
        value: kpis.recentRegistrations.toString(),
        trend: "Last 30 days",
        trendDirection: "up",
        icon: ASSETS.DASHBOARD_STATS_ICONS?.[3] || "🆕",
        accent: "#6D28D9",
      },
    ],
    [kpis]
  );

  // ── Recent Activity (last 30 days only) ─────────────────────────────────
  const activities = useMemo(() => {
    const all = [];
    const get = (item) => item.created_at || item.createdAt;
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const pushIfRecent = (dateStr, entry) => {
      if (!dateStr) return;
      const d = new Date(dateStr);
      if (d >= thirtyDaysAgo) all.push({ ...entry, date: d });
    };

    // Latest user registrations
    users.forEach((u) => {
      pushIfRecent(get(u), {
        title: "New registration",
        name: `${u.first_name || ""} ${u.last_name || ""}`.trim() || u.email,
        timestamp: formatTimestamp(get(u)),
      });
    });

    // Interviews
    interviews.forEach((i) => {
      pushIfRecent(get(i), {
        title: "Interview scheduled",
        name: i.candidate_name || "Unknown Candidate",
        timestamp: formatTimestamp(get(i)),
      });
    });

    // Companies
    companies.forEach((c) => {
      pushIfRecent(get(c), {
        title: "Company registered",
        name: c.company_name || c.name,
        timestamp: formatTimestamp(get(c)),
      });
    });

    // Contracts
    contracts.forEach((c) => {
      pushIfRecent(get(c), {
        title: "Contract generated",
        name: c.user_name || "Unknown User",
        timestamp: formatTimestamp(get(c)),
      });
    });

    // CV submissions
    cvDocuments?.forEach((doc) => {
      pushIfRecent(get(doc), {
        title: "CV submitted",
        name: doc.name || doc.email || "Anonymous",
        timestamp: formatTimestamp(get(doc)),
      });
    });

    return all
      .sort((a, b) => b.date - a.date)
      .slice(0, 15)
      .map(({ date, ...rest }) => rest);
  }, [users, interviews, companies, contracts, cvDocuments]);

  // ── Status badge counts ────────────────────────────────────────────────
  const statusBadges = useMemo(() => {
    // ── Pending = interviews with pending/scheduled status ──────────────────
    const pending =
      interviewStats?.pending ??
      interviewStats?.scheduled ??
      interviews?.filter((i) => ["Scheduled", "Rescheduled", "Pending"].includes(i.status)).length;

    // ── Interview = total interviews count ──────────────────────────────────
    const interviewCount =
      interviewStats?.total_interviews ??
      interviews?.length;

    // ── Accepted = CV Documents with ACTIVE status (Section 2) ──────────────
    const acceptedCount = cvDocuments?.filter(
      (d) => d.status?.toLowerCase() === "active"
    ).length;

    // ── Rejected = CV Documents with BLACKLIST status (Section 2) ───────────
    const rejectedCount = cvDocuments?.filter(
      (d) => d.status?.toLowerCase() === "blacklist"
    ).length;

    return {
      pending,
      interview: interviewCount,
      accepted: acceptedCount,
      rejected: rejectedCount
    };
  }, [interviews, cvDocuments, interviewStats]);

  // ── Needs Attention (actionable items only) ────────────────────────────
  const recommendations = useMemo(() => {
    const items = [];
    const now = new Date();
    const sevenDaysFromNow = new Date();
    sevenDaysFromNow.setDate(now.getDate() + 7);
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(now.getDate() - 30);

    // 1. New users without any interview (need first contact)
    users.forEach((user) => {
      const hasInterview = interviews?.some((i) => i.candidate === user.id);
      const createdAt = user.created_at ? new Date(user.created_at) : null;
      const isRecent = createdAt && createdAt >= thirtyDaysAgo;

      if (!hasInterview && isRecent) {
        items.push({
          name: `${user.first_name || ""} ${user.last_name || ""}`.trim() || "Unknown",
          position: user.ranks?.[0]?.rank?.name || "Not Specified",
          company: "N/A",
          status: "pending",
          submittedDate: user.created_at ? user.created_at.split("T")[0] : null,
          interviewDate: null,
        });
      }
    });

    // 2. Upcoming interviews (scheduled within next 7 days)
    interviews?.forEach((interview) => {
      if (!["Scheduled", "Rescheduled"].includes(interview.status)) return;
      const schedDate = interview.scheduled_date ? new Date(interview.scheduled_date) : null;
      if (schedDate && schedDate >= now && schedDate <= sevenDaysFromNow) {
        items.push({
          name: interview.candidate_name || "Unknown Candidate",
          position: interview.position || "Not Specified",
          company: interview.company_name || "N/A",
          status: "interview",
          submittedDate: null,
          interviewDate: interview.scheduled_date,
        });
      }
    });

    // 3. Users on vacation / medical leave
    users.forEach((user) => {
      const onLeave = ["VACATION", "Vacation", "MEDICAL VACATION", "Medical Vacation"]
        .includes(user.user_status);
      if (onLeave) {
        items.push({
          name: `${user.first_name || ""} ${user.last_name || ""}`.trim() || "Unknown",
          position: user.ranks?.[0]?.rank?.name || "Not Specified",
          company: "N/A",
          status: user.user_status?.includes("MEDICAL") || user.user_status?.includes("Medical")
            ? "rejected" : "pending",
          submittedDate: null,
          interviewDate: null,
        });
      }
    });

    return items.slice(0, 10);
  }, [users, interviews]);

  // ── Loading state ──────────────────────────────────────────────────────
  const isLoading =
    usersLoading || companiesLoading || interviewsLoading || cvsLoading || documentsLoading;

  // ── Layout constants ───────────────────────────────────────────────────
  const headerHeight = Math.round(101 * scale);
  const contentPadding = Math.round(12 * scale);
  const gapLarge = Math.round(28 * scale);
  const gapSmall = Math.round(14 * scale);
  const borderRadius = Math.round(20 * scale);
  const shadow = "0px 1px 4px rgba(0,0,0,0.10)";

  if (isLoading) {
    return (
      <main
        style={{
          padding: `${contentPadding}px`,
          marginTop: `calc(${headerHeight}px + ${contentPadding}px)`,
          overflow: "auto",
          flex: 1,
          backgroundColor: COLORS.background,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <LoadingScreen scale={scale} message="Loading Dashboard Data" subMessage="Collecting the latest maritime analytics and KPIs" />
      </main>
    );
  }

  return (
    <main
      style={{
        padding: `${contentPadding}px`,
        marginTop: `calc(${headerHeight}px + ${contentPadding}px)`,
        overflow: "auto",
        flex: 1,
        backgroundColor: COLORS.background,
      }}
    >
      {/* ── KPI Stats ──────────────────────────────────────────────── */}
      <div style={{ marginBottom: `${gapLarge}px` }}>
        <h3
          style={{
            fontSize: `${Math.round(13 * scale)}px`,
            fontWeight: "600",
            color: COLORS.lightText,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            margin: `0 0 ${Math.round(10 * scale)}px ${Math.round(4 * scale)}px`,
            fontFamily: "Poppins, sans-serif",
          }}
        >
          Overview
        </h3>

        <div
          style={{
            display: "flex",
            gap: `${gapSmall}px`,
            overflowX: "auto",
            paddingBottom: `${Math.round(6 * scale)}px`,
            scrollSnapType: "x mandatory",
            scrollbarWidth: "none",
            msOverflowStyle: "none",
          }}
        >
          <style>{`div::-webkit-scrollbar { display: none; }`}</style>
          {statCards.map((card, idx) => (
            <div
              key={idx}
              style={{ scrollSnapAlign: "start", flexShrink: 0 }}
            >
              <StatCard
                title={card.title}
                value={card.value}
                trend={card.trend}
                trendDirection={card.trendDirection}
                icon={card.icon}
                scale={scale}
                accentColor={card.accent}
              />
            </div>
          ))}
        </div>
      </div>

      {/* ── Bottom Grid: Activity + Status + Recommendations ────────── */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr",
          gap: `${gapLarge}px`,
          maxWidth: "100%",
        }}
      >
        {/* Recent Activity */}
        <section>
          <h2
            style={{
              fontSize: `${Math.round(20 * scale)}px`,
              fontWeight: "500",
              color: COLORS.darkText,
              margin: `0 0 ${Math.round(20 * scale)}px 0`,
              fontFamily: "Poppins, sans-serif",
              lineHeight: `${Math.round(28 * scale)}px`,
            }}
          >
            Recent Activity
          </h2>
          <div
            style={{
              backgroundColor: COLORS.white,
              borderRadius: `${borderRadius}px`,
              padding: `${Math.round(24 * scale)}px`,
              boxShadow: shadow,
              maxHeight: `${Math.round(690 * scale)}px`,
              overflowY: "auto",
              scrollBehavior: "smooth",
            }}
          >
            {activities.length > 0 ? (
              activities.map((activity, idx) => (
                <ActivityItem
                  key={idx}
                  title={activity.title}
                  name={activity.name}
                  timestamp={activity.timestamp}
                  scale={scale}
                  onClick={() => handleActivityClick(activity.title)}
                />
              ))
            ) : (
              <p
                style={{
                  color: COLORS.lightText,
                  textAlign: "center",
                  margin: 0,
                  fontSize: `${Math.round(14 * scale)}px`,
                }}
              >
                No recent activity
              </p>
            )}
          </div>
        </section>

        {/* Status Badges + Recommendations */}
        <section
          style={{
            display: "flex",
            flexDirection: "column",
            gap: `${Math.round(27 * scale)}px`,
          }}
        >
          {/* Status Badges */}
          <div
            style={{
              width: isMobile ? "80%" : `${Math.round(650 * scale)}px`,
              display: "flex",
              margin: isMobile
                ? "0 auto"
                : `${Math.round(80 * scale)}px 0 0 0`,
              gap: `${Math.round(27 * scale)}px`,
              justifyContent: isMobile ? "space-between" : "flex-start",
              flexWrap: "wrap",
            }}
          >
            <StatusBadge
              status="pending"
              count={statusBadges.pending?.toString()}
              icon={ASSETS.DASHBOARD_STATUS_ICONS?.[2] || "⏳"}
              scale={scale}
            />
            {/* <StatusBadge
              status="interview"
              count={statusBadges.interview?.toString()}
              icon={ASSETS.DASHBOARD_STATUS_ICONS?.[3] || "👤"}
              scale={scale}
            /> */}
            <StatusBadge
              status="accepted"
              count={statusBadges.accepted?.toString()}
              icon={ASSETS.DASHBOARD_STATUS_ICONS?.[0] || "✓"}
              scale={scale}
            />
            <StatusBadge
              status="rejected"
              count={statusBadges.rejected?.toString()}
              icon={ASSETS.DASHBOARD_STATUS_ICONS?.[1] || "✕"}
              scale={scale}
            />
          </div>

          {/* Active Recommendations */}
          <div>
            <h2
              style={{
                fontSize: `${Math.round(20 * scale)}px`,
                fontWeight: "500",
                color: COLORS.darkText,
                margin: `0 0 ${Math.round(20 * scale)}px 0`,
                fontFamily: "Poppins, sans-serif",
                lineHeight: `${Math.round(28 * scale)}px`,
              }}
            >
              Needs Attention
            </h2>
            <div
              style={{
                backgroundColor: COLORS.white,
                borderRadius: `${borderRadius}px`,
                padding: `${Math.round(12 * scale)}px ${Math.round(14 * scale)}px`,
                boxShadow: shadow,
                maxHeight: `${Math.round(560 * scale)}px`,
                overflowY: "auto",
                scrollBehavior: "smooth",
              }}
            >
              {recommendations.length > 0 ? (
                recommendations.map((rec, idx) => (
                  <RecommendationCard
                    key={idx}
                    name={rec.name}
                    position={rec.position}
                    company={rec.company}
                    status={rec.status}
                    submittedDate={rec.submittedDate}
                    interviewDate={rec.interviewDate}
                    scale={scale}
                    onClick={handleRecommendationClick}
                  />
                ))
              ) : (
                <p
                  style={{
                    color: COLORS.lightText,
                    textAlign: "center",
                    margin: 0,
                    fontSize: `${Math.round(14 * scale)}px`,
                  }}
                >
                  No items need attention
                </p>
              )}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
};
