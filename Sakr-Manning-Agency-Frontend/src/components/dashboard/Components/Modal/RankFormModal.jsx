// components/dashboard/Modals/RankFormModal.jsx
import React from "react";
import BaseModal from "./BaseModal";
import Button from "../Common/Button";

// Import form components
import { BaseInput } from "../inputs/BaseInput";

// Import refactoring utilities
import { useFormModal } from "../../hooks/useFormModal";
import { RANK_FORM_FIELDS } from "../../../../utils/dashboard/fieldConfigs";

/**
 * RankFormModal - Uses BaseModal for responsive scrolling
 */
const RankFormModal = ({
  rank = null,
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
    fieldConfig: RANK_FORM_FIELDS,
    record: rank,
    onSave,
    onClose,
    successMessage: (isEdit) =>
      isEdit ? "Rank updated successfully" : "Rank created successfully",
    errorMessage: "Failed to save rank",
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
      default:
        return null;
    }
  };

  const footer = (
    <div style={{ display: "flex", gap: `${Math.round(12 * scale)}px`, justifyContent: "flex-end", width: "100%" }}>
      <Button variant="outline" onClick={handleClose} scale={scale} disabled={loading}>
        Cancel
      </Button>
      <Button variant="primary" onClick={handleSave} scale={scale} disabled={loading} loading={loading}>
        {loading ? "Saving..." : isEditMode ? "Update Rank" : "Create Rank"}
      </Button>
    </div>
  );

  return (
    <BaseModal
      isOpen={true}
      onClose={handleClose}
      title={isEditMode ? "Edit Rank" : "Add New Rank"}
      size="sm"
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
        {RANK_FORM_FIELDS.map((field) => (
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

export default RankFormModal;
