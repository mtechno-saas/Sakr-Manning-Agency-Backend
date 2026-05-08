import React, { useEffect, useState, useMemo } from "react";
import Button from "../Common/Button";
import { getModalStyles } from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { useFormModal } from "../../hooks/useFormModal";
import { CV_FORM_FIELDS } from "../../../../utils/dashboard/fieldConfigs";
import { usersApi } from "../../../../services/Dashboard/usersApi";

const CVFormModal = ({ isOpen, cv = null, onClose, onSave, scale = 1 }) => {
  if (!isOpen) return null;

  const modalStyles = getModalStyles(scale);
  const titleStyles = getModalTitleStyles(scale);

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
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const enrichedFieldConfig = useMemo(() => {
    return CV_FORM_FIELDS.map((field) => {
      if (field.name === "position") {
        return {
          ...field,
          options: ranks.map((pos) => ({
            value: pos.value ?? pos.id,
            label: pos.label ?? pos.name ?? pos.value,
          })),
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
    record: cv,
    onSave: async (data) => {
      // Create FormData for submission
      const fd = new FormData();
      Object.keys(data).forEach((key) => {
        // If it's the file field, only append if it's an actual File object
        if (key === "file") {
          if (data[key] instanceof File) {
            fd.append(key, data[key]);
          }
        } else if (data[key] !== null && data[key] !== undefined) {
          fd.append(key, data[key]);
        }
      });
      await onSave(fd);
    },
    onClose,
    successMessage: (isEdit) =>
      isEdit ? "CV updated successfully" : "CV created successfully",
    // Special validation for file in create mode
    customValidation: (data) => {
      const vErrors = {};
      if (!isEditMode && !data.file) {
        vErrors.file = "CV file is required";
      }
      return vErrors;
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
      required: field.required && (!isEditMode || field.name !== "file"),
      value: field.type === "file" ? undefined : formData[field.name],
      onChange: (val) => handleChange(field.name, val),
      error: errors[field.name],
      placeholder: field.placeholder,
      variant: "dashboard",
      ...field.props,
    };

    if (field.type === "file") {
      return (
        <div key={field.name} className="w-full">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {field.label} {!isEditMode && <span className="text-red-500">*</span>}
          </label>
          <input
            type="file"
            accept={field.props?.accept}
            onChange={(e) => handleChange(field.name, e.target.files[0])}
            className={`w-full px-4 py-2 border rounded-lg text-base outline-none transition-all duration-200 ${
              errors[field.name]
                ? "border-red-400 focus:ring-red-100 focus:border-red-500"
                : "border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            }`}
          />
          {errors[field.name] && (
            <p className="mt-1 text-red-500 text-xs flex items-center gap-1">
              <span className="w-1 h-1 bg-red-500 rounded-full" /> {errors[field.name]}
            </p>
          )}
          {isEditMode && (
            <p className="mt-1 text-gray-500 text-xs">
              Leave empty to keep existing file
            </p>
          )}
        </div>
      );
    }

    switch (field.component) {
      case "BaseInput":
        return <BaseInput {...commonProps} type={field.type} />;
      case "Select":
        return <Select {...commonProps} options={field.options} />;
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
    >
      <div
        style={{
          ...modalStyles.panel,
          maxWidth: `${Math.round(700 * scale)}px`,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={titleStyles}>
          {isEditMode ? "Edit CV Details" : "Upload New CV"}
        </h2>

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
            {loading ? "Saving..." : isEditMode ? "Update CV" : "Upload CV"}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default CVFormModal;
