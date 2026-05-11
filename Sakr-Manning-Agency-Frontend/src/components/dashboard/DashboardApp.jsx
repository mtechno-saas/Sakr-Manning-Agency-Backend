// DashboardApp.jsx - Main Dashboard Entry Point
//////////////////////////////

// DashboardApp.jsx - UPDATED - Removed Mock Data, Simplified Props
import React, { useState, useEffect, useMemo, useCallback } from "react";
import { BASE_WIDTH, COLORS, getScale } from "./Constants";
import { Header } from "./Header";
import { Sidebar, MobileSidebar } from "./Sidebar";

import { OverviewPage } from "./Content/Overview";
import { CVManagement } from "./Content/CV";
import { CompanyManagement } from "./Content/Company";
import { InterviewManagement } from "./Content/Interviews";
import { DocumentManagement } from "./Content/Documents";
import { UserManagement } from "./Content/Users";
import { FinanceRecords } from "./Content/Finance";
import { SearchResults } from "./Content/SearchResults";
import { CVSubmissionsManagement } from "./Content/CVSubmissions";
import AIApplication from "./Content/AIApplication";
import ChatWidget from "./Components/AI/ChatWidget";

import { ASSETS } from "../../utils/constants";
import { SearchProvider } from "./context/SearchContext";
import { NotificationProvider } from "./context/NotificationContext";
import { DashboardDataProvider, useDashboardData } from "./context/DashboardDataContext";
import NotificationCenter from "./Components/Common/NotificationCenter";
import LoadingScreen from "./Components/Common/LoadingScreen";

const DashboardAppContent = ({ onLogout, user }) => {
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [windowWidth, setWindowWidth] = useState(
    typeof window !== "undefined" ? window.innerWidth : BASE_WIDTH
  );
  const [scale, setScale] = useState(1);

  // Get loading states from context
  const {
    loadingCompanies,
    loadingUsers,
    loadingRanks,
    loadingFlags,
    loadingVesselTypes,
    loadingCertificates,
    companies,
    users,
    ranks
  } = useDashboardData();

  // Determine if we are in the initial loading phase
  // We consider it initial loading if critical data hasn't arrived yet
  const isInitialLoading = (loadingCompanies && (companies?.length ?? 0) === 0) ||
    (loadingUsers && (users?.length ?? 0) === 0) ||
    (loadingRanks && (ranks?.length ?? 0) === 0);

  const userData = user;

  useEffect(() => {
    const handleResize = () => {
      const newWidth = window.innerWidth;
      setWindowWidth(newWidth);
      setScale(getScale(newWidth));
    };

    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const isMobile = windowWidth < 768;
  const isDesktop = windowWidth >= 1024;

  const pageData = {
    dashboard: "Dashboard Overview",
    cvs: "CVs Management",
    management: "Companies and Ships Management",
    interviews: "Interviews Scheduling",
    documents: "Documents Management",
    users: "Users Management",
    finance: "Finance Record",
    search: "Search Results",
    cvSubmissions: "CV Submissions",
  };

  const handleSearchSubmit = useCallback((query) => {
    setCurrentPage("search");
  }, []);

  const handleNavigateFromSearch = useCallback((page, itemId) => {
    setCurrentPage(page);
  }, []);

  // Simplified common props - only scale and isMobile needed
  // Each page manages its own data through hooks
  const commonProps = useMemo(
    () => ({
      scale,
      isMobile,
    }),
    [scale, isMobile]
  );

  const renderCurrentPage = () => {
    if (isInitialLoading) {
      return <LoadingScreen scale={scale} message="Initializing Dashboard" subMessage="Loading core data and reference systems" />;
    }

    switch (currentPage) {
      case "dashboard":
        return <OverviewPage {...commonProps} onNavigate={setCurrentPage} />;
      case "cvs":
        return <CVManagement {...commonProps} />;
      case "management":
        return <CompanyManagement {...commonProps} />;
      case "interviews":
        return <InterviewManagement {...commonProps} />;
      case "documents":
        return <DocumentManagement {...commonProps} />;
      case "users":
        return <UserManagement {...commonProps} />;
      case "finance":
        return <FinanceRecords {...commonProps} />;
      case "AI":
        return <AIApplication {...commonProps} />;
      case "search":
        return (
          <SearchResults
            {...commonProps}
            onNavigate={handleNavigateFromSearch}
          />
        );
      case "cvSubmissions":
        return <CVSubmissionsManagement {...commonProps} />;
      default:
        return (
          <PlaceholderPage pageTitle={pageData[currentPage]} scale={scale} />
        );
    }
  };

  return (
    <SearchProvider currentPage={currentPage}>
      <div
        style={{
          display: "flex",
          minHeight: "100vh",
          backgroundColor: COLORS.background,
          fontFamily: "Inter, sans-serif",
        }}
      >
        {isDesktop && (
          <Sidebar
            currentPage={currentPage}
            onPageChange={setCurrentPage}
            scale={scale}
          />
        )}

        {isMobile && (
          <MobileSidebar
            isOpen={mobileMenuOpen}
            onClose={() => setMobileMenuOpen(false)}
            currentPage={currentPage}
            onPageChange={setCurrentPage}
            scale={scale}
          />
        )}

        <div
          style={{
            marginLeft: isDesktop ? `${Math.round(280 * scale)}px` : 0,
            width: isDesktop
              ? `calc(100% - ${Math.round(280 * scale)}px)`
              : "100%",
            display: "flex",
            flexDirection: "column",
            minHeight: "100vh",
          }}
        >
          <Header
            pageTitle={pageData[currentPage]}
            onMenuClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            isMobile={isMobile}
            scale={scale}
            onLogout={onLogout}
            onSearchSubmit={handleSearchSubmit}
            user={userData}
          />

          {renderCurrentPage()}
          {/* <ChatWidget scale={1} isFloating={true} /> */}
          {/* <img
              src={ASSETS.CHATBOT}
              alt="ChatBot"
              className={`fixed cursor-pointer z-[1000]
                transition-transform duration-500 ease-in-out
                hover:animate-[float_1.5s_ease-in-out_infinite]
                [@keyframes_float]:[0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)_scale(1.5)_rotate(45deg)}]
                ${
                  isMobile
                    ? "w-[20px] h-[20px] bottom-[30px] right-[30px]"
                    : "w-[50px] h-[50px] bottom-[30px] right-[30px]"
                }`}
            /> */}
        </div>
        <NotificationCenter scale={scale} position="bottom-left" />
      </div>
    </SearchProvider>
  );
};

const DashboardApp = (props) => {
  return (
    <NotificationProvider>
      <DashboardDataProvider>
        <DashboardAppContent {...props} />
      </DashboardDataProvider>
    </NotificationProvider>
  );
};

// Placeholder component for unimplemented pages
export const PlaceholderPage = ({ pageTitle, scale }) => {
  const headerHeight = Math.round(101 * scale);
  const padding = Math.round(32 * scale);
  const borderRadius = Math.round(16 * scale);
  const shadow = `0px 1px 3px rgba(0, 0, 0, 0.12)`;
  const fontSize = Math.round(48 * scale);
  const titleFontSize = Math.round(24 * scale);
  const descFontSize = Math.round(14 * scale);
  const minHeight = Math.round(500 * scale);

  return (
    <main
      style={{
        padding: `${padding}px`,
        paddingTop: `calc(${headerHeight}px + ${padding}px)`,
        overflow: "auto",
        flex: 1,
        backgroundColor: COLORS.background,
      }}
    >
      <div
        style={{
          backgroundColor: COLORS.white,
          borderRadius: `${borderRadius}px`,
          padding: `${padding}px`,
          boxShadow: shadow,
          minHeight: `${minHeight}px`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column",
          fontFamily: "Poppins, sans-serif",
          textAlign: "center",
          gap: `${Math.round(20 * scale)}px`,
        }}
      >
        <div style={{ fontSize: `${fontSize}px` }}>🚀</div>
        <h2
          style={{
            margin: 0,
            color: COLORS.darkText,
            fontSize: `${titleFontSize}px`,
            fontWeight: "600",
          }}
        >
          Coming Soon
        </h2>
        <p
          style={{
            color: COLORS.lightText,
            margin: 0,
            fontSize: `${descFontSize}px`,
            maxWidth: "300px",
          }}
        >
          {pageTitle} page is under development. Check back soon!
        </p>
      </div>
    </main>
  );
};

export default DashboardApp;
