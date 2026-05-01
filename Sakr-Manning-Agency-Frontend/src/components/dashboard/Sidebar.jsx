// Sidebar.jsx and MobileSidebar.jsx

import React from "react";
import { COLORS } from "./Constants";
import { X } from "lucide-react";
import { ASSETS } from "../../utils/constants";

export const Sidebar = ({ currentPage, onPageChange, scale }) => {
  const menuItems = [
    {
      id: "dashboard",
      label: "Dashboard",
      icon: ASSETS.DASHBOARD_Sidebar_ICONS[0] || "🏠",
    },
    {
      id: "cvs",
      label: "CVs",
      icon: ASSETS.DASHBOARD_Sidebar_ICONS[1] || "📄",
    },
    {
      id: "management",
      label: "Management",
      icon: ASSETS.DASHBOARD_Sidebar_ICONS[2] || "🏢",
    },
    {
      id: "cvSubmissions",
      label: "CV Submissions",
      icon: ASSETS.DASHBOARD_Sidebar_ICONS[1] || "📥",
    },
    {
      id: "interviews",
      label: "Interviews",
      icon: ASSETS.DASHBOARD_Sidebar_ICONS[3] || "📝",
    },
    {
      id: "documents",
      label: "Documents",
      icon: ASSETS.DASHBOARD_Sidebar_ICONS[4] || "📋",
    },
    {
      id: "users",
      label: "Users",
      icon: ASSETS.DASHBOARD_Sidebar_ICONS[5] || "👥",
    },
    {
      id: "finance",
      label: "Finance",
      icon: ASSETS.DASHBOARD_Sidebar_ICONS[6] || "💰",
    },
    {
      id: "AI",
      label: "AI Assistant",
      // icon: ASSETS.CHATBOT || "🏢",
    },
  ];

  const sidebarWidth = Math.round(280 * scale);
  const padding = Math.round(20 * scale);
  const logoSize = Math.round(80 * scale);
  const fontSize = Math.round(14 * scale);
  const menuItemHeight = Math.round(44 * scale);
  const gap = Math.round(32 * scale);
  const borderRadius = Math.round(22 * scale);
  const logoRadius = Math.round(50 * scale);

  return (
    <aside
      style={{
        width: `${sidebarWidth}px`,
        backgroundColor: COLORS.primary,
        height: "100vh",
        position: "fixed",
        left: 0,
        top: 0,
        fontFamily: "Inter, sans-serif",
        display: "flex",
        flexDirection: "column",
        padding: `${padding}px`,
        gap: `${gap}px`,
        overflowY: "auto",
        zIndex: 50,
      }}
    >
      <div>
        <div
          style={{
            width: `${logoSize}px`,
            height: `${logoSize}px`,
            backgroundColor: "rgba(255, 255, 255, 0.2)",
            borderRadius: `${logoRadius}px`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: COLORS.white,
            fontSize: `${Math.round(22 * scale)}px`,
            fontWeight: "700",
            marginBottom: `${Math.round(16 * scale)}px`,
            flexShrink: 0,
          }}
        >
          <img src={ASSETS.LOGO} alt="Sidebar-Logo" />
        </div>
        <p
          style={{
            fontFamily: "Poppins, sans-serif",
            fontWeight: "600",
            fontSize: `${Math.round(14 * scale)}px`,
            lineHeight: `${Math.round(20 * scale)}px`,
            color: COLORS.white,
            margin: 0,
            wordBreak: "break-word",
          }}
        >
          SAKR MANNING AGENCY
        </p>
      </div>

      <nav
        style={{
          display: "flex",
          flexDirection: "column",
          gap: `${Math.round(12 * scale)}px`,
        }}
      >
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onPageChange(item.id)}
            style={{
              padding: `${Math.round(12 * scale)}px`,
              borderRadius: `${borderRadius}px`,
              border: "none",
              backgroundColor:
                currentPage === item.id ? COLORS.primaryLight : "transparent",
              color: COLORS.white,
              fontSize: `${fontSize}px`,
              fontWeight: "600",
              fontFamily: "Poppins, sans-serif",
              textAlign: "left",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: `${Math.round(16 * scale)}px`,
              transition: "all 0.3s ease",
              width: "100%",
              height: `${menuItemHeight}px`,
            }}
            onMouseEnter={(e) => {
              if (currentPage !== item.id) {
                e.currentTarget.style.backgroundColor =
                  "rgba(255, 255, 255, 0.1)";
              }
            }}
            onMouseLeave={(e) => {
              if (currentPage !== item.id) {
                e.currentTarget.style.backgroundColor = "transparent";
              }
            }}
          >
            <span
              style={{ fontSize: `${Math.round(20 * scale)}px`, flexShrink: 0 }}
            >
              <img src={item.icon} />
            </span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  );
};

export const MobileSidebar = ({
  isOpen,
  onClose,
  currentPage,
  onPageChange,
  scale,
}) => {
  const menuItems = [
    {
      id: "dashboard",
      label: "Dashboard",
      icon: ASSETS.DASHBOARD_Sidebar_ICONS[0] || "🏠",
    },
    {
      id: "cvs",
      label: "CVs",
      icon: ASSETS.DASHBOARD_Sidebar_ICONS[1] || "📄",
    },
    {
      id: "management",
      label: "Management",
      icon: ASSETS.DASHBOARD_Sidebar_ICONS[2] || "🏢",
    },
    {
      id: "cvSubmissions",
      label: "CV Submissions",
      icon: "📥",
    },
    {
      id: "interviews",
      label: "Interviews",
      icon: ASSETS.DASHBOARD_Sidebar_ICONS[3] || "📝",
    },
    {
      id: "documents",
      label: "Documents",
      icon: ASSETS.DASHBOARD_Sidebar_ICONS[4] || "📋",
    },
    {
      id: "users",
      label: "Users",
      icon: ASSETS.DASHBOARD_Sidebar_ICONS[5] || "👥",
    },
    {
      id: "finance",
      label: "Finance",
      icon: ASSETS.DASHBOARD_Sidebar_ICONS[6] || "💰",
    },
    {
      id: "AI",
      label: "AI Assistant",
      // icon: ASSETS.CHATBOT || "🏢",
    },
  ];

  const sidebarWidth = Math.round(280 * scale);
  const padding = Math.round(20 * scale);
  const logoSize = Math.round(80 * scale);
  const fontSize = Math.round(14 * scale);
  const menuItemHeight = Math.round(44 * scale);
  const gap = Math.round(32 * scale);
  const borderRadius = Math.round(12 * scale);

  return (
    <>
      {isOpen && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.5)",
            zIndex: 999,
          }}
          onClick={onClose}
        />
      )}

      <aside
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: `${sidebarWidth}px`,
          height: "100vh",
          backgroundColor: COLORS.primary,
          zIndex: 1000,
          transform: isOpen
            ? "translateX(0)"
            : `translateX(-${sidebarWidth}px)`,
          transition: "transform 0.3s ease-in-out",
          display: "flex",
          flexDirection: "column",
          padding: `${padding}px`,
          gap: `${gap}px`,
          overflowY: "auto",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
          }}
        >
          <div>
            <div
              style={{
                width: `${logoSize}px`,
                height: `${logoSize}px`,
                backgroundColor: "rgba(255, 255, 255, 0.2)",
                borderRadius: `${Math.round(50 * scale)}px`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: COLORS.white,
                fontSize: `${Math.round(22 * scale)}px`,
                fontWeight: "700",
                marginBottom: `${Math.round(16 * scale)}px`,
              }}
            >
              SM
            </div>
            <p
              style={{
                fontFamily: "Poppins, sans-serif",
                fontWeight: "600",
                fontSize: `${Math.round(14 * scale)}px`,
                lineHeight: `${Math.round(20 * scale)}px`,
                color: COLORS.white,
                margin: 0,
              }}
            >
              SAKR MANNING AGENCY
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              color: COLORS.white,
              cursor: "pointer",
              padding: `${Math.round(12 * scale)}px`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <X size={Math.round(24 * scale)} />
          </button>
        </div>

        <nav
          style={{
            display: "flex",
            flexDirection: "column",
            gap: `${Math.round(12 * scale)}px`,
          }}
        >
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => {
                onPageChange(item.id);
                onClose();
              }}
              style={{
                padding: `${Math.round(12 * scale)}px`,
                borderRadius: `${borderRadius}px`,
                border: "none",
                backgroundColor:
                  currentPage === item.id ? COLORS.primaryLight : "transparent",
                color: COLORS.white,
                fontSize: `${fontSize}px`,
                fontWeight: "600",
                fontFamily: "Poppins, sans-serif",
                textAlign: "left",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: `${Math.round(16 * scale)}px`,
                transition: "all 0.3s ease",
                width: "100%",
                height: `${menuItemHeight}px`,
              }}
            >
              <span
                style={{
                  fontSize: `${Math.round(20 * scale)}px`,
                  flexShrink: 0,
                }}
              >
                {item.icon}
              </span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
      </aside>
    </>
  );
};
