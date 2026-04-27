// Components/Common/UserProfile.jsx
// Professional user profile dropdown with admin info and logout

import React, { useState, useRef, useEffect } from "react";
import { User, LogOut, Settings, ChevronDown } from "lucide-react";
import { STYLE_TOKENS, getScaledValue } from "../../Styles/globalStyles";

/**
 * UserProfile Component
 *
 * Professional dropdown menu for user profile
 * Features:
 * - User avatar/icon
 * - Admin name and role
 * - Settings option
 * - Logout button
 * - Click outside to close
 * - Keyboard accessible
 *
 * @param {object} user - User data { name, email, role, avatar }
 * @param {function} onLogout - Logout callback
 * @param {number} scale - Scale factor
 */
const UserProfile = ({ user, onLogout, scale = 1 }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Default user data if not provided
  const userData = user || {
    name: "Admin User",
    email: "admin@sakrmanning.com",
    role: "Administrator",
    avatar: null,
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    // Close on Escape key
    const handleEscape = (event) => {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("keydown", handleEscape);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [isOpen]);

  // Handle logout
  const handleLogout = () => {
    setIsOpen(false);
    if (onLogout) {
      onLogout();
    }
  };

  // Handle settings (placeholder)
  const handleSettings = () => {
    console.log("Settings clicked");
    setIsOpen(false);
    // TODO: Navigate to settings page
  };

  // Calculate sizes
  const buttonSize = getScaledValue(45, scale);
  const dropdownWidth = getScaledValue(280, scale);
  const avatarSize = getScaledValue(50, scale);
  const padding = getScaledValue(16, scale);
  const borderRadius = getScaledValue(12, scale);
  const itemHeight = getScaledValue(44, scale);
  const fontSize = getScaledValue(14, scale);
  const nameFontSize = getScaledValue(16, scale);
  const iconSize = getScaledValue(20, scale);
  const chevronSize = getScaledValue(16, scale);

  // Get user initials for avatar fallback
  const getInitials = (name) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div
      ref={dropdownRef}
      style={{
        position: "relative",
        display: "inline-block",
      }}
    >
      {/* Profile Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: "flex",
          alignItems: "center",
          gap: `${getScaledValue(8, scale)}px`,
          padding: `${getScaledValue(6, scale)}px ${getScaledValue(
            12,
            scale
          )}px`,
          backgroundColor: isOpen ? "rgba(0, 101, 175, 0.1)" : "transparent",
          border: `1px solid ${
            isOpen ? STYLE_TOKENS.colors.primary : "transparent"
          }`,
          borderRadius: `${getScaledValue(24, scale)}px`,
          cursor: "pointer",
          transition: STYLE_TOKENS.transition.normal,
          height: `${buttonSize}px`,
        }}
        onMouseEnter={(e) => {
          if (!isOpen) {
            e.currentTarget.style.backgroundColor = "rgba(0, 0, 0, 0.05)";
          }
        }}
        onMouseLeave={(e) => {
          if (!isOpen) {
            e.currentTarget.style.backgroundColor = "transparent";
          }
        }}
        aria-expanded={isOpen}
        aria-haspopup="true"
        title="User menu"
      >
        {/* Avatar */}
        {userData.avatar ? (
          <img
            src={userData.avatar}
            alt={userData.name}
            style={{
              width: `${getScaledValue(32, scale)}px`,
              height: `${getScaledValue(32, scale)}px`,
              borderRadius: "50%",
              objectFit: "cover",
            }}
          />
        ) : (
          <div
            style={{
              width: `${getScaledValue(32, scale)}px`,
              height: `${getScaledValue(32, scale)}px`,
              borderRadius: "50%",
              backgroundColor: STYLE_TOKENS.colors.primary,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: STYLE_TOKENS.colors.white,
              fontSize: `${getScaledValue(12, scale)}px`,
              fontWeight: 600,
              fontFamily: STYLE_TOKENS.fonts.heading,
            }}
          >
            {getInitials(userData.name)}
          </div>
        )}

        {/* Chevron Icon */}
        <ChevronDown
          size={chevronSize}
          style={{
            transition: STYLE_TOKENS.transition.normal,
            transform: isOpen ? "rotate(180deg)" : "rotate(0deg)",
            color: STYLE_TOKENS.colors.darkText,
          }}
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          style={{
            position: "absolute",
            top: `calc(100% + ${getScaledValue(8, scale)}px)`,
            right: 0,
            width: `${dropdownWidth}px`,
            backgroundColor: STYLE_TOKENS.colors.white,
            borderRadius: `${borderRadius}px`,
            boxShadow: STYLE_TOKENS.shadow.lg,
            border: `1px solid ${STYLE_TOKENS.colors.borderColor}`,
            overflow: "hidden",
            zIndex: 1000,
            animation: "fadeIn 0.2s ease-out",
          }}
        >
          <style>{`
            @keyframes fadeIn {
              from {
                opacity: 0;
                transform: translateY(-10px);
              }
              to {
                opacity: 1;
                transform: translateY(0);
              }
            }
          `}</style>

          {/* User Info Section */}
          <div
            style={{
              padding: `${padding}px`,
              borderBottom: `1px solid ${STYLE_TOKENS.colors.borderColor}`,
              display: "flex",
              alignItems: "center",
              gap: `${getScaledValue(12, scale)}px`,
            }}
          >
            {/* Large Avatar */}
            {userData.avatar ? (
              <img
                src={userData.avatar}
                alt={userData.name}
                style={{
                  width: `${avatarSize}px`,
                  height: `${avatarSize}px`,
                  borderRadius: "50%",
                  objectFit: "cover",
                  flexShrink: 0,
                }}
              />
            ) : (
              <div
                style={{
                  width: `${avatarSize}px`,
                  height: `${avatarSize}px`,
                  borderRadius: "50%",
                  backgroundColor: STYLE_TOKENS.colors.primary,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: STYLE_TOKENS.colors.white,
                  fontSize: `${getScaledValue(20, scale)}px`,
                  fontWeight: 600,
                  fontFamily: STYLE_TOKENS.fonts.heading,
                  flexShrink: 0,
                }}
              >
                {getInitials(userData.name)}
              </div>
            )}

            {/* User Details */}
            <div
              style={{
                flex: 1,
                minWidth: 0,
              }}
            >
              <div
                style={{
                  fontSize: `${nameFontSize}px`,
                  fontWeight: 600,
                  color: STYLE_TOKENS.colors.darkText,
                  fontFamily: STYLE_TOKENS.fonts.heading,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                  marginBottom: `${getScaledValue(2, scale)}px`,
                }}
                title={userData.name}
              >
                {userData.name}
              </div>
              <div
                style={{
                  fontSize: `${getScaledValue(12, scale)}px`,
                  color: STYLE_TOKENS.colors.lightText,
                  fontFamily: STYLE_TOKENS.fonts.primary,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
                title={userData.email}
              >
                {userData.email}
              </div>
              <div
                style={{
                  fontSize: `${getScaledValue(11, scale)}px`,
                  color: STYLE_TOKENS.colors.primary,
                  fontFamily: STYLE_TOKENS.fonts.primary,
                  fontWeight: 500,
                  marginTop: `${getScaledValue(4, scale)}px`,
                  textTransform: "uppercase",
                  letterSpacing: "0.5px",
                }}
              >
                {userData.role}
              </div>
            </div>
          </div>

          {/* Menu Items */}
          <div style={{ padding: `${getScaledValue(8, scale)}px 0` }}>
            {/* Settings Option */}
            <button
              onClick={handleSettings}
              style={{
                width: "100%",
                height: `${itemHeight}px`,
                padding: `0 ${padding}px`,
                display: "flex",
                alignItems: "center",
                gap: `${getScaledValue(12, scale)}px`,
                backgroundColor: "transparent",
                border: "none",
                cursor: "pointer",
                fontSize: `${fontSize}px`,
                fontFamily: STYLE_TOKENS.fonts.primary,
                color: STYLE_TOKENS.colors.darkText,
                transition: STYLE_TOKENS.transition.normal,
                textAlign: "left",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor =
                  STYLE_TOKENS.colors.hoverBackground;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = "transparent";
              }}
            >
              <Settings size={iconSize} strokeWidth={2} />
              <span>Account Settings</span>
            </button>

            {/* Divider */}
            <div
              style={{
                height: "1px",
                backgroundColor: STYLE_TOKENS.colors.borderColor,
                margin: `${getScaledValue(8, scale)}px 0`,
              }}
            />

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              style={{
                width: "100%",
                height: `${itemHeight}px`,
                padding: `0 ${padding}px`,
                display: "flex",
                alignItems: "center",
                gap: `${getScaledValue(12, scale)}px`,
                backgroundColor: "transparent",
                border: "none",
                cursor: "pointer",
                fontSize: `${fontSize}px`,
                fontFamily: STYLE_TOKENS.fonts.primary,
                color: STYLE_TOKENS.colors.rejected,
                transition: STYLE_TOKENS.transition.normal,
                textAlign: "left",
                fontWeight: 500,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = "rgba(178, 17, 1, 0.1)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = "transparent";
              }}
            >
              <LogOut size={iconSize} strokeWidth={2} />
              <span>Logout</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserProfile;
