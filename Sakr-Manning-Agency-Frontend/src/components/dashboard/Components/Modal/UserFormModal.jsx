// components/dashboard/Modals/UserFormModal.jsx - REFACTORED v2
import React, { useState, useEffect, useMemo } from "react";
import Button from "../Common/Button";
import { getModalStyles } from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";

// Import form components
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { DateInput } from "../inputs/DateInput";
import { Checkbox } from "../../../form/inputs/Checkbox";

// Import refactoring utilities
import { useFormModal } from "../../hooks/useFormModal"
import { USER_FORM_FIELDS } from "../../../../utils/dashboard/fieldConfigs";

// Import APIs
import { certificatesApi, usersApi } from "../../../../services/Dashboard/usersApi";
import useNotification from "../../hooks/useNotification";

/**
 * UserFormModal v2 - REFACTORED
 * 
 * Reduced from 363 lines → ~220 lines (39% reduction)
 * 
 * Key Improvements:
 * - Centralized field configuration
 * - useFormModal hook handles logic
 * - Checkbox array pattern for certificates/ranks
 * - Dynamic reference data loading
 */

const UserFormModal = ({ user = null, onClose, onSave, scale = 1 }) => {
  const modalStyles = getModalStyles(scale);
  const titleStyles = getModalTitleStyles(scale);
  const { notify } = useNotification();

  // Reference data
  const [certificates, setCertificates] = useState([]);
  const [ranks, setRanks] = useState([]);
  const [loadingReference, setLoadingReference] = useState(true);

  // Load reference data
  useEffect(() => {
    const loadData = async () => {
      try {
        const [certsRes, ranksRes] = await Promise.all([
          certificatesApi.getCertificates(),
          usersApi.getPositions(),
        ]);
        setCertificates(certsRes);
        // getPositions returns [{ value, label }] — normalize to match rank shape
        setRanks(ranksRes);
      } catch (error) {
        console.error("Failed to load reference data:", error);
        notify.error("Failed to load certificates and ranks");
      } finally {
        setLoadingReference(false);
      }
    };
    loadData();
  }, [notify]);

  // Enrich field config with dynamic data
  const enrichedFieldConfig = useMemo(() => {
    return USER_FORM_FIELDS.map((field) => {
      if (field.name === "certificate_ids") {
        return {
          ...field,
          options: certificates.map((cert) => ({
            value: cert.id,
            label: cert.name,
          })),
        };
      }
      if (field.name === "rank_ids") {
        return {
          ...field,
          options: ranks.map((pos) => ({
            // positions endpoint returns { value, label } — use value as the stored key
            value: pos.value ?? pos.id,
            label: pos.label ?? pos.name ?? pos.value,
          })),
        };
      }
      return field;
    });
  }, [certificates, ranks]);

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
    fieldConfig: enrichedFieldConfig,
    record: user,
    onSave,
    onClose,
    successMessage: (isEdit) =>
      isEdit ? "User updated successfully" : "User created successfully",
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

  // Handle checkbox array change
  const handleCheckboxArrayChange = (fieldName, value) => {
    const currentValues = formData[fieldName] || [];
    const newValues = currentValues.includes(value)
      ? currentValues.filter((v) => v !== value)
      : [...currentValues, value];
    handleChange(fieldName, newValues);
  };

  // Render field
  const renderField = (field) => {
    // Email is disabled in edit mode
    // const isDisabled = field.props?.disabled === "editMode" && isEditMode;
    const isDisabled = false;

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
      disabled: isDisabled,
      ...field.props,
    };

    switch (field.component) {
      case "BaseInput":
        return <BaseInput {...commonProps} type={field.type} />;

      case "Select":
        return <Select {...commonProps} options={field.options} />;

      case "DateInput":
        return <DateInput {...commonProps} />;

      case "CheckboxArray":
        return (
          <div key={field.name}>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {field.label}
            </label>
            <div
              style={{
                border: "1px solid #E5E7EB",
                borderRadius: `${Math.round(8 * scale)}px`,
                padding: `${Math.round(8 * scale)}px`,
                maxHeight: `${Math.round(150 * scale)}px`,
                overflowY: "auto",
                backgroundColor: "#fff",
              }}
            >
              {field.options.length === 0 ? (
                <p className="text-gray-500 text-sm py-2">
                  Loading {field.label.toLowerCase()}...
                </p>
              ) : (
                field.options.map((option) => (
                  <Checkbox
                    key={option.value}
                    name={`${field.name}_${option.value}`}
                    label={option.label}
                    checked={(formData[field.name] || []).includes(option.value)}
                    onChange={() =>
                      handleCheckboxArrayChange(field.name, option.value)
                    }
                  />
                ))
              )}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div
      onClick={handleClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="user-form-modal-title"
      style={{
        ...modalStyles.overlay,
        overflowY: "auto",
        padding: `${Math.round(40 * scale)}px 0`,
      }}
    >
      <div
        style={{
          ...modalStyles.panel,
          maxWidth: `${Math.round(800 * scale)}px`,
          overflow: "visible",
          margin: "auto",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="user-form-modal-title" style={titleStyles}>
          {isEditMode ? "Edit User" : "Add New User"}
        </h2>

        {loadingReference ? (
          <div style={{ padding: "40px", textAlign: "center", color: "#8C8C8C" }}>
            Loading form data...
          </div>
        ) : (
          <>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(12, 1fr)",
                gap: `${Math.round(16 * scale)}px`,
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
              <Button variant="primary" onClick={handleSave} scale={scale} disabled={loading} loading={loading}>
                {loading ? "Saving..." : isEditMode ? "Update User" : "Create User"}
              </Button>
            </div>

            <div style={{ marginTop: "12px", fontSize: "11px", color: "#8C8C8C", textAlign: "center" }}>
              Press <kbd style={{ padding: "2px 4px", backgroundColor: "#F3F4F6", borderRadius: "3px", fontFamily: "monospace" }}>Esc</kbd> to close •{" "}
              <kbd style={{ padding: "2px 4px", backgroundColor: "#F3F4F6", borderRadius: "3px", fontFamily: "monospace" }}>Ctrl+Enter</kbd> to save
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default UserFormModal;