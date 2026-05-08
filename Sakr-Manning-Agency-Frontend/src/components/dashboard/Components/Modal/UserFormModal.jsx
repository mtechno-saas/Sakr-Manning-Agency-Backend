// components/dashboard/Modals/UserFormModal.jsx - REFACTORED v2.1
import React, { useState, useEffect, useMemo } from "react";
import BaseModal from "./BaseModal";
import Button from "../Common/Button";

// Import form components
import { BaseInput, SuggestionInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { DateInput } from "../inputs/DateInput";
import { Checkbox } from "../../../form/inputs/Checkbox";

// Import refactoring utilities
import { useFormModal } from "../../hooks/useFormModal"
import { USER_FORM_FIELDS } from "../../../../utils/dashboard/fieldConfigs";
import { POPULAR_NATIONALITIES } from "../../../../config/formConfig";

// Import APIs
import { usersApi } from "../../../../services/Dashboard/usersApi";
import useNotification from "../../hooks/useNotification";

/**
 * UserFormModal v2.1 - Uses BaseModal for responsive scrolling
 */
const UserFormModal = ({ user = null, onClose, onSave, scale = 1 }) => {
  const { notify } = useNotification();

  // Reference data
  const [ranks, setRanks] = useState([]);
  const [loadingReference, setLoadingReference] = useState(true);

  // Load reference data
  useEffect(() => {
    const loadData = async () => {
      try {
        const ranksRes = await usersApi.getPositions();
        setRanks(ranksRes);
      } catch (error) {
        console.error("Failed to load reference data:", error);
      } finally {
        setLoadingReference(false);
      }
    };
    loadData();
  }, [notify]);

  // Enrich field config with dynamic data
  const enrichedFieldConfig = useMemo(() => {
    return USER_FORM_FIELDS.map((field) => {
      if (field.name === "rank_ids") {
        return {
          ...field,
          options: ranks.map((pos) => ({
            value: pos.label ?? pos.name ?? pos.value ?? pos,
            label: pos.label ?? pos.name ?? pos.value ?? pos,
          })),
        };
      }
      if (field.name === "nationality") {
        return {
          ...field,
          suggestions: POPULAR_NATIONALITIES,
        };
      }
      return field;
    });
  }, [ranks]);

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

      case "SuggestionInput":
        return <SuggestionInput {...commonProps} suggestions={field.suggestions || []} />;

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

  const footer = (
    <div style={{ display: "flex", flexDirection: "column", gap: "12px", width: "100%" }}>
      <div style={{ display: "flex", gap: `${Math.round(12 * scale)}px`, justifyContent: "flex-end" }}>
        <Button variant="outline" onClick={handleClose} scale={scale} disabled={loading}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleSave} scale={scale} disabled={loading} loading={loading}>
          {loading ? "Saving..." : isEditMode ? "Update User" : "Create User"}
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
      title={isEditMode ? "Edit User" : "Add New User"}
      size="lg"
      footer={footer}
      scale={scale}
    >
      {loadingReference ? (
        <div style={{ padding: "40px", textAlign: "center", color: "#8C8C8C" }}>
          Loading form data...
        </div>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(12, 1fr)",
            gap: `${Math.round(16 * scale)}px`,
            padding: "2px", // Avoid clipping field focus rings
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
      )}
    </BaseModal>
  );
};

export default UserFormModal;