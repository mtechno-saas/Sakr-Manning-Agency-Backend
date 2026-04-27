// components/Common/NotificationCenter.jsx
// Container that displays all active notifications/toasts
// Usually placed at top-right of screen

import React from "react";
import Toast from "./Toast";
import useNotification from "../../hooks/useNotification";
import { getScaledValue } from "../../Styles/globalStyles";

/**
 * NotificationCenter Component
 *
 * Displays all active notifications stacked vertically
 * Auto-positions at top-right corner
 * Handles multiple notifications gracefully
 *
 * Props:
 * @param {number} scale - Scale factor (default: 1)
 * @param {string} position - Position: 'top-right', 'top-left', 'bottom-right', 'bottom-left' (default: 'top-right')
 *
 * Usage:
 * <NotificationCenter scale={scale} position="top-right" />
 *
 * Place this in your main layout, typically in App.jsx or DashboardApp.jsx
 */
const NotificationCenter = ({ scale = 1, position = "top-right" }) => {
  const { notifications, removeNotification } = useNotification();

  // Calculate position values
  const gap = getScaledValue(12, scale);
  const padding = getScaledValue(20, scale);

  // Determine fixed positioning based on position prop
  const positionStyles = {
    "top-right": {
      top: `${padding}px`,
      right: `${padding}px`,
      left: "auto",
      bottom: "auto",
    },
    "top-left": {
      top: `${padding}px`,
      left: `${padding}px`,
      right: "auto",
      bottom: "auto",
    },
    "bottom-right": {
      bottom: `${padding}px`,
      right: `${padding}px`,
      left: "auto",
      top: "auto",
    },
    "bottom-left": {
      bottom: `${padding}px`,
      left: `${padding}px`,
      right: "auto",
      top: "auto",
    },
  };

  return (
    <div
      role="region"
      aria-label="Notifications"
      aria-live="polite"
      aria-atomic="false"
      style={{
        position: "fixed",
        ...positionStyles[position],
        display: "flex",
        flexDirection: "column",
        gap: `${gap}px`,
        zIndex: 9999,
        pointerEvents: "none", // Allow clicks through empty space
      }}
    >
      {notifications.map((notification) => (
        <div
          key={notification.id}
          style={{
            pointerEvents: "auto", // Re-enable clicks on actual toasts
          }}
        >
          <Toast
            id={notification.id}
            type={notification.type}
            message={notification.message}
            onClose={removeNotification}
            scale={scale}
          />
        </div>
      ))}
    </div>
  );
};

export default NotificationCenter;
