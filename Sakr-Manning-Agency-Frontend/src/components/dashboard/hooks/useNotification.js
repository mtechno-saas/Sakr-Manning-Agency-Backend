// hooks/useNotification.js
// Custom hook to access notification context
// Simplifies adding notifications from anywhere in the app

import { useContext } from "react";
import NotificationContext from "../context/NotificationContext";

/**
 * Custom Hook: useNotification
 *
 * Access notification system from any component
 * Provides convenient methods for showing different notification types
 *
 * @returns {object} Notification utilities
 *
 * @example
 * const { notify } = useNotification();
 *
 * // Show success notification
 * notify.success("CV uploaded successfully!");
 *
 * // Show error notification
 * notify.error("Failed to delete CV");
 *
 * // Show warning
 * notify.warning("Are you sure?");
 *
 * // Show info
 * notify.info("CV is under review");
 *
 * // Custom duration
 * const { addNotification } = useNotification();
 * addNotification("success", "Custom message", 5000); // 5 seconds
 */
const useNotification = () => {
  const context = useContext(NotificationContext);

  if (!context) {
    throw new Error(
      "useNotification must be used within NotificationProvider. " +
        "Make sure your app is wrapped with NotificationProvider."
    );
  }

  return context;
};

export default useNotification;
