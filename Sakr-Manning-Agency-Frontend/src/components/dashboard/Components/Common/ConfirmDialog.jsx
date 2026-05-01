// Components/Common/ConfirmDialog.jsx
// Reusable confirmation dialog for delete/destructive actions

import React, { useEffect } from "react";
import Button from "./Button";
import { getModalStyles } from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";
import { getScaledValue } from "../../Styles/globalStyles";

/**
 * ConfirmDialog Component
 *
 * Generic confirmation modal for destructive actions
 * Supports customizable title, message, and button labels
 *
 * @param {boolean} isOpen - Modal visibility
 * @param {Function} onClose - Close callback
 * @param {Function} onConfirm - Confirm callback
 * @param {string} title - Dialog title
 * @param {string} message - Dialog message
 * @param {string} confirmLabel - Confirm button label
 * @param {string} cancelLabel - Cancel button label
 * @param {string} variant - Confirm button variant ('danger', 'primary')
 * @param {number} scale - Scale factor
 * @param {boolean} loading - Loading state during confirmation
 *
 * @example
 * <ConfirmDialog
 *   isOpen={showConfirm}
 *   onClose={() => setShowConfirm(false)}
 *   onConfirm={handleDelete}
 *   title="Delete CV"
 *   message="Are you sure you want to delete this CV? This action cannot be undone."
 *   confirmLabel="Delete"
 *   variant="danger"
 *   scale={scale}
 * />
 */
const ConfirmDialog = ({
  isOpen,
  onClose,
  onConfirm,
  title = "Confirm Action",
  message = "Are you sure you want to proceed?",
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  variant = "danger",
  scale = 1,
  loading = false,
}) => {
  const modalStyles = getModalStyles(scale);
  const titleStyles = getModalTitleStyles(scale);

  // Handle Escape key
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e) => {
      if (e.key === "Escape" && !loading) {
        onClose();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose, loading]);

  if (!isOpen) return null;

  const handleConfirm = () => {
    if (!loading) {
      onConfirm();
    }
  };

  const handleCancel = () => {
    if (!loading) {
      onClose();
    }
  };

  return (
    <div
      style={modalStyles.overlay}
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
      onClick={handleCancel}
    >
      <div
        style={{
          ...modalStyles.panel,
          maxWidth: `${getScaledValue(450, scale)}px`,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Title */}
        <h2 id="confirm-dialog-title" style={titleStyles}>
          {title}
        </h2>

        {/* Message */}
        <p
          style={{
            fontSize: `${getScaledValue(16, scale)}px`,
            lineHeight: `${getScaledValue(24, scale)}px`,
            color: "#4B5563",
            margin: `${getScaledValue(16, scale)}px 0 ${getScaledValue(
              24,
              scale
            )}px 0`,
            fontFamily: "Inter, sans-serif",
          }}
        >
          {message}
        </p>

        {/* Action Buttons */}
        <div
          style={{
            display: "flex",
            gap: `${getScaledValue(12, scale)}px`,
            justifyContent: "flex-end",
          }}
        >
          <Button
            variant="outline"
            onClick={handleCancel}
            scale={scale}
            disabled={loading}
          >
            {cancelLabel}
          </Button>
          <Button
            variant={variant}
            onClick={handleConfirm}
            scale={scale}
            loading={loading}
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDialog;
