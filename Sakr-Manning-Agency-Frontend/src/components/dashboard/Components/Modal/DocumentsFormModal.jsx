// components/dashboard/Components/Modal/DocumentsFormModal.jsx
import React from "react";
import BaseModal from "./BaseModal";
import Button from "../Common/Button";

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

  const footer = (
    <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end", width: "100%" }}>
      <Button variant="outline" onClick={handleClose} scale={scale} disabled={loading}>
        Cancel
      </Button>
      <Button variant="primary" onClick={handleSave} scale={scale} disabled={loading} loading={loading}>
        {loading ? "Saving..." : "Update Contract"}
      </Button>
    </div>
  );

  return (
    <BaseModal
      isOpen={true}
      onClose={handleClose}
      title="Edit Contract"
      subtitle={`Updating contract for ${contract?.user_name || "Employee"}`}
      size="sm"
      footer={footer}
      scale={scale}
    >
      <div style={{ display: "flex", flexDirection: "column", gap: `${Math.round(16 * scale)}px` }}>
        {EDIT_CONTRACT_FIELDS.map(renderField)}
      </div>
    </BaseModal>
  );
};

export default DocumentFormModal;