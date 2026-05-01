// context/NotificationContext.js
// Global context for managing notifications/toasts across the application

import React, { createContext, useState, useCallback, useRef } from "react";

const NotificationContext = createContext(null);

/**
 * NotificationProvider Component
 *
 * Wraps the app to provide notification functionality globally
 * Features:
 * - Add/remove notifications
 * - Auto-dismiss after timeout
 * - Queue multiple notifications
 * - Clear all notifications
 *
 * Usage:
 * <NotificationProvider>
 *   <App />
 * </NotificationProvider>
 */
export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
  const notificationIdRef = useRef(0);

  /**
   * Add a new notification
   *
   * @param {string} type - 'success', 'error', 'warning', 'info'
   * @param {string} message - Notification message
   * @param {number} duration - Auto-dismiss duration in ms (0 = no auto-dismiss)
   * @returns {string} Notification ID (can be used to remove manually)
   */
  const addNotification = useCallback(
    (type = "info", message = "", duration = 3000) => {
      const id = `notification-${notificationIdRef.current++}`;

      const notification = {
        id,
        type,
        message,
        timestamp: Date.now(),
      };

      // Add notification
      setNotifications((prev) => [...prev, notification]);

      // Auto-dismiss if duration specified
      if (duration > 0) {
        setTimeout(() => {
          removeNotification(id);
        }, duration);
      }

      return id;
    },
    []
  );

  /**
   * Remove a notification by ID
   */
  const removeNotification = useCallback((id) => {
    setNotifications((prev) => prev.filter((notif) => notif.id !== id));
  }, []);

  /**
   * Clear all notifications
   */
  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  /**
   * Convenience methods for common types — MEMOIZED
   */
  const notify = React.useMemo(() => ({
    success: (message, duration = 3000) =>
      addNotification("success", message, duration),
    error: (message, duration = 4000) =>
      addNotification("error", message, duration),
    warning: (message, duration = 3500) =>
      addNotification("warning", message, duration),
    info: (message, duration = 3000) =>
      addNotification("info", message, duration),
  }), [addNotification]);

  const value = React.useMemo(() => ({
    notifications,
    addNotification,
    removeNotification,
    clearNotifications,
    notify,
  }), [notifications, addNotification, removeNotification, clearNotifications, notify]);

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export default NotificationContext;
