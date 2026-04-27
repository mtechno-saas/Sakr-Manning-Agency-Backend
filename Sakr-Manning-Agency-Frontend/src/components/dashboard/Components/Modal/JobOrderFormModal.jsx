// components/dashboard/Modals/JobOrderFormModal.jsx
import React, { useEffect, useMemo } from "react";
import Button from "../Common/Button";
import { getModalStyles } from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";

import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { DateInput } from "../inputs/DateInput";
import { TextArea } from "../../../form/inputs/TextArea";

import { useFormModal } from "../../hooks/useFormModal";
import { JOB_ORDER_FORM_FIELDS } from "../../../../utils/dashboard/fieldConfigs";
import { useDashboardData } from "../../context/DashboardDataContext";
import useNotification from "../../hooks/useNotification";

/**
 * JobOrderFormModal
 * Handles create / edit for Job Orders at /api/companies/job-orders/
 */
const JobOrderFormModal = ({
  jobOrder = null,
  onClose,
  onSave,
  scale = 1,
}) => {
  const modalStyles = getModalStyles(scale);
  const titleStyles = getModalTitleStyles(scale);
  const { notify } = useNotification();

  // Pull reference data from dashboard context
  const { referenceOptions, ships = [] } = useDashboardData();

  // Build enriched field config with dynamic options
  const enrichedFieldConfig = useMemo(() => {
    return JOB_ORDER_FORM_FIELDS.map((field) => {
      if (field.name === "company") {
        return { ...field, options: referenceOptions?.companies || [] };
      }
      if (field.name === "ship") {
        return {
          ...field,
          options: (ships || []).map((s) => ({
            value: s.id,
            label: s.ship_name || s.name || `Ship ${s.id}`,
          })),
        };
      }
      return field;
    });
  }, [referenceOptions, ships]);

  const {
    formData,
    errors,
    loading,
    isEditMode,
    handleChange,
    handleSave,
    handleClose,
  } = useFormModal({
    fieldConfig: enrichedFieldConfig,
    record: jobOrder,
    onSave,
    onClose,
    successMessage: (isEdit) =>
      isEdit ? "Job order updated successfully" : "Job order created successfully",
    errorMessage: "Failed to save job order",
  });

  // Keyboard shortcuts
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "Escape") handleClose();
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        handleSave();
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [handleClose, handleSave]);

  // Dynamic field renderer
  const renderField = (field) => {
    const commonProps = {
      key: field.name,
      name: field.name,
      label: field.label,
      required: field.required,
      value: formData[field.name],
      onChange: (val) => handleChange(field.name, val),
      error: errors[field.name],
      placeholder: field.placeholder,
      variant: "dashboard",
      ...field.props,
    };

    switch (field.component) {
      case "BaseInput":
        return <BaseInput {...commonProps} type={field.type} />;
      case "Select":
        return <Select {...commonProps} options={field.options} />;
      case "DateInput":
        return <DateInput {...commonProps} />;
      case "TextArea":
        return <TextArea {...commonProps} scale={scale} />;
      default:
        return null;
    }
  };

  return (
    <div
      style={modalStyles.overlay}
      onClick={handleClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="job-order-modal-title"
    >
      <div
        style={{
          ...modalStyles.panel,
          maxWidth: `${Math.round(620 * scale)}px`,
          maxHeight: "90vh",
          overflowY: "auto",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="job-order-modal-title" style={titleStyles}>
          {isEditMode ? "Edit Job Order" : "Create Job Order"}
        </h2>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: `${Math.round(16 * scale)}px`,
          }}
        >
          {enrichedFieldConfig.map((field) => renderField(field))}
        </div>

        <div
          style={{
            display: "flex",
            gap: `${Math.round(12 * scale)}px`,
            justifyContent: "flex-end",
            marginTop: `${Math.round(24 * scale)}px`,
          }}
        >
          <Button variant="outline" onClick={handleClose} scale={scale} disabled={loading}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSave}
            scale={scale}
            disabled={loading}
            loading={loading}
          >
            {loading
              ? "Saving..."
              : isEditMode
              ? "Update Job Order"
              : "Create Job Order"}
          </Button>
        </div>

        <div
          style={{
            marginTop: `${Math.round(12 * scale)}px`,
            fontSize: `${Math.round(11 * scale)}px`,
            color: "#8C8C8C",
            textAlign: "center",
          }}
        >
          Press{" "}
          <kbd
            style={{
              padding: `${Math.round(2 * scale)}px ${Math.round(4 * scale)}px`,
              backgroundColor: "#F3F4F6",
              borderRadius: `${Math.round(3 * scale)}px`,
              fontFamily: "monospace",
            }}
          >
            Esc
          </kbd>{" "}
          to close •{" "}
          <kbd
            style={{
              padding: `${Math.round(2 * scale)}px ${Math.round(4 * scale)}px`,
              backgroundColor: "#F3F4F6",
              borderRadius: `${Math.round(3 * scale)}px`,
              fontFamily: "monospace",
            }}
          >
            Ctrl+Enter
          </kbd>{" "}
          to save
        </div>
      </div>
    </div>
  );
};

export default JobOrderFormModal;
