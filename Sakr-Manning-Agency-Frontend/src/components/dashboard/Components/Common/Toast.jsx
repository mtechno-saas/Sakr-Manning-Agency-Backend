// components/Common/Toast.jsx
// Individual toast/notification component
// Displays a single notification with auto-dismiss and manual close

import React from "react";
import { STYLE_TOKENS, getScaledValue } from "../../Styles/globalStyles";

/**
 * Toast Component
 *
 * Individual notification toast with icon, message, and close button
 * Auto-animates in and out
 *
 * @param {string} id - Unique notification ID
 * @param {string} type - Notification type: 'success', 'error', 'warning', 'info'
 * @param {string} message - Toast message
 * @param {function} onClose - Callback when toast closes
 * @param {number} scale - Scale factor (default: 1)
 */
const Toast = ({ id, type = "info", message, onClose, scale = 1 }) => {
  // Color schemes for different notification types
  const typeStyles = {
    success: {
      bg: "rgba(21, 171, 16, 0.1)",
      border: "rgba(21, 171, 16, 0.3)",
      color: "#15AB10",
      bgDark: "#f0f9ee",
      icon: "✓",
    },
    error: {
      bg: "rgba(178, 17, 1, 0.1)",
      border: "rgba(178, 17, 1, 0.3)",
      color: "#B21101",
      bgDark: "#fdf5f4",
      icon: "✕",
    },
    warning: {
      bg: "rgba(255, 193, 7, 0.1)",
      border: "rgba(255, 193, 7, 0.3)",
      color: "#FFC107",
      bgDark: "#fffbf0",
      icon: "!",
    },
    info: {
      bg: "rgba(36, 119, 195, 0.2)",
      border: "rgba(36, 119, 195, 0.3)",
      color: "#0065AF",
      bgDark: "#eef4fb",
      icon: "ⓘ",
    },
  };

  const styles = typeStyles[type] || typeStyles.info;

  // Calculate responsive sizing
  const padding = getScaledValue(16, scale);
  const minWidth = getScaledValue(300, scale);
  const maxWidth = getScaledValue(400, scale);
  const borderRadius = getScaledValue(12, scale);
  const fontSize = getScaledValue(14, scale);
  const iconSize = getScaledValue(20, scale);
  const closeSize = getScaledValue(16, scale);

  return (
    <div
      role="alert"
      aria-live="polite"
      aria-label={`${type} notification: ${message}`}
      style={{
        display: "flex",
        alignItems: "center",
        gap: `${getScaledValue(12, scale)}px`,
        padding: `${padding}px`,
        backgroundColor: styles.bgDark,
        border: `1px solid ${styles.border}`,
        borderRadius: `${borderRadius}px`,
        boxShadow: "0px 4px 12px rgba(0, 0, 0, 0.1)",
        minWidth: `${minWidth}px`,
        maxWidth: `${maxWidth}px`,
        fontFamily: STYLE_TOKENS.fonts.primary,
        fontSize: `${fontSize}px`,
        color: STYLE_TOKENS.colors.darkText,
        animation: "slideIn 0.3s ease-out forwards",
        backdropFilter: "blur(10px)",
      }}
    >
      <style>{`
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(400px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        @keyframes slideOut {
          from {
            opacity: 1;
            transform: translateX(0);
          }
          to {
            opacity: 0;
            transform: translateX(400px);
          }
        }
      `}</style>

      {/* Icon */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          width: `${iconSize}px`,
          height: `${iconSize}px`,
          borderRadius: "50%",
          backgroundColor: styles.bg,
          color: styles.color,
          fontSize: `${getScaledValue(12, scale)}px`,
          fontWeight: "bold",
          flexShrink: 0,
        }}
      >
        {styles.icon}
      </div>

      {/* Message */}
      <div
        style={{
          flex: 1,
          wordBreak: "break-word",
          fontWeight: 500,
          lineHeight: `${getScaledValue(20, scale)}px`,
        }}
      >
        {message}
      </div>

      {/* Close Button */}
      <button
        onClick={() => onClose(id)}
        style={{
          background: "none",
          border: "none",
          color: STYLE_TOKENS.colors.lightText,
          cursor: "pointer",
          padding: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: `${closeSize}px`,
          lineHeight: 1,
          transition: STYLE_TOKENS.transition.normal,
          flexShrink: 0,
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.color = STYLE_TOKENS.colors.darkText;
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.color = STYLE_TOKENS.colors.lightText;
        }}
        title="Close notification"
        aria-label="Close notification"
      >
        ✕
      </button>
    </div>
  );
};

export default Toast;
