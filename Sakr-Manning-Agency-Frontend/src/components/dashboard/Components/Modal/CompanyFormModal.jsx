// components/dashboard/Modals/CompanyFormModal.jsx - REFACTORED v2.1
import React from "react";
import BaseModal from "./BaseModal";
import Button from "../Common/Button";

// Import form components
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { TextArea } from "../../../form/inputs/TextArea";

// Import refactoring utilities
import { useFormModal } from "../../hooks/useFormModal";
import { COMPANY_FORM_FIELDS } from "../../../../utils/dashboard/fieldConfigs";

/**
 * CompanyFormModal v2.1 - Uses BaseModal for responsive scrolling
 */
const CompanyFormModal = ({
  company = null,
  onClose,
  onSave,
  scale = 1
}) => {
  // Use form modal hook
  const {
    formData,
    errors,
    loading,
    isEditMode,
    handleChange,
    handleSave,
    handleClose,
  } = useFormModal({
    fieldConfig: COMPANY_FORM_FIELDS,
    record: company,
    onSave,
    onClose,
    successMessage: (isEdit) =>
      isEdit ? "Company updated successfully" : "Company created successfully",
    errorMessage: "Failed to save company",
  });

  // Render field based on configuration
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
          {loading ? "Saving..." : isEditMode ? "Update Company" : "Create Company"}
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
      title={isEditMode ? "Edit Company" : "Add New Company"}
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
        {COMPANY_FORM_FIELDS.map((field) => (
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

export default CompanyFormModal;