// components/dashboard/Modals/JobOrderFormModal.jsx
import React, { useEffect, useMemo } from "react";
import BaseModal from "./BaseModal";
import Button from "../Common/Button";

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
  const { notify } = useNotification();

  // Pull reference data from dashboard context
  const { referenceOptions, shipsByCompany, fetchShipsByCompany } = useDashboardData();

  const {
    formData,
    errors,
    loading,
    isEditMode,
    handleChange,
    handleSave,
    handleClose,
  } = useFormModal({
    fieldConfig: JOB_ORDER_FORM_FIELDS,
    record: jobOrder,
    onSave,
    onClose,
    successMessage: (isEdit) =>
      isEdit ? "Job order updated successfully" : "Job order created successfully",
    errorMessage: "Failed to save job order",
  });

  // Fetch ships when company changes
  useEffect(() => {
    if (formData?.company) {
      fetchShipsByCompany(formData.company);
    }
  }, [formData?.company, fetchShipsByCompany]);

  // Build enriched field config with dynamic options
  const enrichedFieldConfig = useMemo(() => {
    const companyShips = formData?.company ? (shipsByCompany[formData.company] || []) : [];
    
    return JOB_ORDER_FORM_FIELDS.map((field) => {
      if (field.name === "company") {
        return { ...field, options: referenceOptions?.companies || [] };
      }
      if (field.name === "ship") {
        return {
          ...field,
          options: companyShips.map((s) => ({
            value: s.id,
            label: s.ship_name || s.name || `Ship ${s.id}`,
          })),
        };
      }
      return field;
    });
  }, [referenceOptions, shipsByCompany, formData?.company]);

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

  const footer = (
    <div style={{ display: "flex", flexDirection: "column", gap: "12px", width: "100%" }}>
      <div style={{ display: "flex", gap: `${Math.round(12 * scale)}px`, justifyContent: "flex-end" }}>
        <Button variant="outline" onClick={handleClose} scale={scale} disabled={loading}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleSave} scale={scale} disabled={loading} loading={loading}>
          {loading ? "Saving..." : isEditMode ? "Update Job Order" : "Create Job Order"}
        </Button>
      </div>
      <div style={{ fontSize: "11px", color: "#8C8C8C", textAlign: "center" }}>
        Press <kbd style={{ padding: "2px 4px", backgroundColor: "#F3F4F6", borderRadius: "3px", fontFamily: "monospace" }}>Esc</kbd> to close •{" "}
        <kbd style={{ padding: "2px 4px", backgroundColor: "#F3F4F6", borderRadius: "3px", fontFamily: "monospace" }}>Ctrl+Enter</kbd> to save
      </div>
    </div>
  );

  return (
    <BaseModal
      isOpen={true}
      onClose={handleClose}
      title={isEditMode ? "Edit Job Order" : "Create Job Order"}
      size="lg"
      footer={footer}
      scale={scale}
    >
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(12, 1fr)",
          gap: `${Math.round(16 * scale)}px`,
          padding: "2px",
        }}
      >
        {enrichedFieldConfig.map((field) => (
          <div
            key={field.name}
            style={{
              gridColumn: `span ${field.gridCols || 12}`,
            }}
          >
            {renderField(field)}
          </div>
        ))}
      </div>
    </BaseModal>
  );
};

export default JobOrderFormModal;
