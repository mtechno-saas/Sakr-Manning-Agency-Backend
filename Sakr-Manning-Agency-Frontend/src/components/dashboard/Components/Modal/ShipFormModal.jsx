// components/dashboard/Modals/ShipFormModal.jsx - REFACTORED v2.1
import React, { useState, useEffect, useMemo } from "react";
import BaseModal from "./BaseModal";
import Button from "../Common/Button";

// Import form components
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";

// Import refactoring utilities
import { useFormModal } from "../../hooks/useFormModal";
import { SHIP_FORM_FIELDS } from "../../../../utils/dashboard/fieldConfigs";

// Import context and API
import { useDashboardData } from "../../context/DashboardDataContext";
import { coreApi } from "../../../../services/Dashboard/shipsApi";
import useNotification from "../../hooks/useNotification";

/**
 * ShipFormModal v2.1 - Uses BaseModal for responsive scrolling
 */
const ShipFormModal = ({
  ship = null,
  onClose,
  onSave,
  scale = 1,
}) => {
  const { notify } = useNotification();

  // Get data from context
  const {
    referenceOptions,
    flags,
    loadingFlags
  } = useDashboardData();

  // Local state for reference data
  const [vesselTypes, setVesselTypes] = useState([]);
  const [loadingVesselTypes, setLoadingVesselTypes] = useState(true);

  // Load vessel types on mount
  useEffect(() => {
    const loadVesselTypes = async () => {
      try {
        const types = await coreApi.getVesselTypes();
        setVesselTypes(types);
      } catch (error) {
        console.error("Failed to load vessel types:", error);
        notify.error("Failed to load vessel types");
      } finally {
        setLoadingVesselTypes(false);
      }
    };

    loadVesselTypes();
  }, [notify]);

  // Prepare field config with dynamic options
  const enrichedFieldConfig = useMemo(() => {
    return SHIP_FORM_FIELDS.map((field) => {
      if (field.name === "ship_type") {
        return {
          ...field,
          options: vesselTypes.map((type) => ({
            value: type.id,
            label: type.name,
          })),
        };
      }
      if (field.name === "flag") {
        return {
          ...field,
          options: flags.map((flag) => ({
            value: flag.id,
            label: `${flag.name}${flag.code ? ` (${flag.code})` : ""}`,
          })),
        };
      }
      if (field.name === "company") {
        return {
          ...field,
          options: referenceOptions.companies,
        };
      }
      if (field.name === "crew") {
        return {
          ...field,
          options: referenceOptions.users,
        };
      }
      return field;
    });
  }, [vesselTypes, flags, referenceOptions.companies, referenceOptions.users]);

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
    record: ship,
    onSave,
    onClose,
    successMessage: (isEdit) =>
      isEdit ? "Ship updated successfully" : "Ship created successfully",
    errorMessage: "Failed to save ship",
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
        return (
          <Select
            {...commonProps}
            options={field.options}
            disabled={
              (field.name === "ship_type" && loadingVesselTypes) ||
              (field.name === "flag" && loadingFlags)
            }
          />
        );

      default:
        return null;
    }
  };

  const isLoadingReferenceData = loadingVesselTypes || loadingFlags;

  const footer = (
    <div style={{ display: "flex", flexDirection: "column", gap: "12px", width: "100%" }}>
      <div style={{ display: "flex", gap: `${Math.round(12 * scale)}px`, justifyContent: "flex-end" }}>
        <Button variant="outline" onClick={handleClose} scale={scale} disabled={loading}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleSave} scale={scale} disabled={loading} loading={loading}>
          {loading ? "Saving..." : isEditMode ? "Update Ship" : "Create Ship"}
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
      title={isEditMode ? "Edit Ship" : "Add New Ship"}
      size="lg"
      footer={footer}
      scale={scale}
    >
      {isLoadingReferenceData ? (
        <div style={{ padding: "40px", textAlign: "center", color: "#8C8C8C" }}>
          Loading form data...
        </div>
      ) : (
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
      )}
    </BaseModal>
  );
};

export default ShipFormModal;