// components/dashboard/Components/Modal/DocumentFormModal.jsx
import React, { useEffect, useMemo } from "react";
import Button from "../Common/Button";
import { getModalStyles } from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";

import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { DateInput } from "../inputs/DateInput";

import { useFormModal } from "../../hooks/useFormModal";

// Simplified fields specifically for the PATCH /api/contracts/{id}/ endpoint
const EDIT_CONTRACT_FIELDS = [
  {
    name: "status",
    label: "Contract Status",
    type: "select",
    component: "Select",
    required: false,
    options: [
      { value: "Draft", label: "Draft" },
      { value: "Pending Signature", label: "Pending Signature" },
      { value: "Signed", label: "Signed" },
      { value: "Active", label: "Active" },
      { value: "Completed", label: "Completed" },
      { value: "Cancelled", label: "Cancelled" },
    ],
  },
  {
    name: "salary",
    label: "Salary",
    type: "number",
    component: "BaseInput",
    required: false,
    props: { step: "0.01", min: "0" },
  },
  {
    name: "sign_off_date",
    label: "Sign-Off Date",
    type: "date",
    component: "DateInput",
    required: false,
  },
  {
    name: "repatriation_terms",
    label: "Repatriation Terms",
    type: "text",
    component: "BaseInput",
    required: false,
  },
  {
    name: "leave_pay_terms",
    label: "Leave Pay Terms",
    type: "text",
    component: "BaseInput",
    required: false,
  }
];

const DocumentFormModal = ({ contract, onClose, onSave, scale = 1 }) => {
  const modalStyles = getModalStyles(scale);
  const titleStyles = getModalTitleStyles(scale);

  const {
    formData,
    errors,
    loading,
    handleChange,
    handleSave,
    handleClose,
  } = useFormModal({
    fieldConfig: EDIT_CONTRACT_FIELDS,
    record: contract,
    onSave,
    onClose,
    successMessage: () => "Contract updated successfully",
    transformBeforeSave: (data) => {
      // Only include fields that have been modified or are present
      const payload = {};
      if (data.status) payload.status = data.status;
      if (data.salary) payload.salary = data.salary;
      if (data.sign_off_date) payload.sign_off_date = data.sign_off_date;
      if (data.repatriation_terms) payload.repatriation_terms = data.repatriation_terms;
      if (data.leave_pay_terms) payload.leave_pay_terms = data.leave_pay_terms;
      return payload;
    },
  });

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") handleClose();
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        handleSave();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleClose, handleSave]);

  const renderField = (field) => {
    const commonProps = {
      key: field.name,
      name: field.name,
      label: field.label,
      required: field.required,
      value: formData[field.name] || "",
      onChange: (val) => handleChange(field.name, val),
      error: errors[field.name],
      placeholder: field.placeholder,
      variant: "dashboard",
    };

    if (field.component === "Select") return <Select {...commonProps} options={field.options} />;
    if (field.component === "DateInput") return <DateInput {...commonProps} />;
    return <BaseInput {...commonProps} type={field.type} />;
  };

  return (
    <div style={modalStyles.overlay} onClick={handleClose} role="dialog" aria-modal="true">
      <div
        style={{
          ...modalStyles.panel,
          maxWidth: `${Math.round(500 * scale)}px`,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={titleStyles}>Edit Contract</h2>
        <p style={{ fontSize: `${Math.round(14 * scale)}px`, color: "#6B7280", marginBottom: `${Math.round(20 * scale)}px` }}>
          Updating contract for <strong>{contract?.user_name || "Employee"}</strong>.
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: `${Math.round(16 * scale)}px` }}>
          {EDIT_CONTRACT_FIELDS.map(renderField)}
        </div>

        <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end", marginTop: "24px", paddingTop: "16px", borderTop: "1px solid #E5E7EB" }}>
          <Button variant="outline" onClick={handleClose} scale={scale} disabled={loading}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSave} scale={scale} disabled={loading} loading={loading}>
            {loading ? "Saving..." : "Update Contract"}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default DocumentFormModal;