// components/dashboard/Modals/RankFormModal.jsx
import React, { useEffect } from "react";
import Button from "../Common/Button";
import { getModalStyles } from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";

// Import form components
import { BaseInput } from "../inputs/BaseInput";

// Import refactoring utilities
import { useFormModal } from "../../hooks/useFormModal";
import { RANK_FORM_FIELDS } from "../../../../utils/dashboard/fieldConfigs";

const RankFormModal = ({
  rank = null,
  onClose,
  onSave,
  scale = 1
}) => {
  const modalStyles = getModalStyles(scale);
  const titleStyles = getModalTitleStyles(scale);

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

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") {
        handleClose();
      }
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        handleSave();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleClose, handleSave]);

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

  return (
    <div
      style={modalStyles.overlay}
      onClick={handleClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="rank-form-modal-title"
    >
      <div
        style={{
          ...modalStyles.panel,
          maxWidth: `${Math.round(600 * scale)}px`,
          maxHeight: "90vh",
          overflowY: "auto",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Title */}
        <h2 id="rank-form-modal-title" style={titleStyles}>
          {isEditMode ? "Edit Rank" : "Add New Rank"}
        </h2>

        {/* Form Fields - Dynamic Rendering */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(12, 1fr)",
            gap: `${Math.round(16 * scale)}px`,
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

        {/* Action Buttons */}
        <div
          style={{
            display: "flex",
            gap: `${Math.round(12 * scale)}px`,
            justifyContent: "flex-end",
            marginTop: `${Math.round(24 * scale)}px`,
          }}
        >
          <Button
            variant="outline"
            onClick={handleClose}
            scale={scale}
            disabled={loading}
          >
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
                ? "Update Rank"
                : "Create Rank"}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default RankFormModal;
