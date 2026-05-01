// components/dashboard/Modals/DocumentFormModal.jsx - REFACTORED v2
import React, { useState, useEffect, useMemo } from "react";
import Button from "../Common/Button";
import { getModalStyles } from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";

// Import form components
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { DateInput } from "../inputs/DateInput";

// Import refactoring utilities
import { useFormModal } from "../../hooks/useFormModal"
import { DOCUMENT_FORM_FIELDS } from "../../../../utils/dashboard/fieldConfigs";

// Import context
import { useDashboardData } from "../../context/DashboardDataContext";
import useNotification from "../../hooks/useNotification";

/**
 * DocumentFormModal v2 - REFACTORED
 * 
 * Reduced from 504 lines → ~300 lines (40% reduction)
 * 
 * Key Improvements:
 * - Centralized field configuration
 * - useFormModal hook for logic
 * - Cascading company → ships dropdown
 * - Contract duration calculation
 * - TypeaheadInput for user & company
 */

const DocumentFormModal = ({ contract = null, onClose, onSave, scale = 1 }) => {
  const modalStyles = getModalStyles(scale);
  const titleStyles = getModalTitleStyles(scale);
  const { notify } = useNotification();

  // Get data from context
  const { fetchShipsByCompany, referenceOptions } = useDashboardData();

  // Ships state (loaded based on company)
  const [ships, setShips] = useState([]);
  const [loadingShips, setLoadingShips] = useState(false);

  // Enrich field config
  const enrichedFieldConfig = useMemo(() => {
    return DOCUMENT_FORM_FIELDS.map((field) => {
      // Add dynamic options for user
      if (field.name === "user") {
        return {
          ...field,
          options: referenceOptions.users,
        };
      }

      // Add dynamic options for company
      if (field.name === "company") {
        return {
          ...field,
          options: referenceOptions.companies,
        };
      }

      // Add options for ship
      if (field.name === "ship") {
        return {
          ...field,
          options: ships.map((s) => ({
            value: s.id,
            label: `${s.ship_name}${s.imo_number ? ` (IMO: ${s.imo_number})` : ""}`,
          })),
        };
      }

      // Add options for rank from context
      if (field.name === "rank") {
        return {
          ...field,
          options: referenceOptions.ranks || [],
        };
      }

      return field;
    });
  }, [referenceOptions, ships]);

  // Use form modal hook
  const {
    formData,
    errors,
    loading,
    isEditMode,
    handleChange,
    handleBatchChange,
    handleSave,
    handleClose,
  } = useFormModal({
    fieldConfig: enrichedFieldConfig,
    record: contract,
    onSave,
    onClose,
    successMessage: (isEdit) =>
      isEdit ? "Contract updated successfully" : "Contract created successfully",
    // Custom transform
    transformBeforeSave: (data) => {
      const transformed = {
        user: parseInt(data.user),
        company: parseInt(data.company),
        rank: parseInt(data.rank),
        sign_on_date: data.sign_on_date,
        sign_off_date: data.sign_off_date,
        salary: parseFloat(data.salary).toFixed(2),
        currency: data.currency,
        status: data.status,
      };

      // Only include ship if selected
      if (data.ship) {
        transformed.ship = parseInt(data.ship);
      }

      return transformed;
    },
  });

  // Load ships when contract is loaded (for edit mode)
  useEffect(() => {
    if (contract?.company) {
      const companyId = typeof contract.company === "object"
        ? contract.company.id
        : contract.company;
      loadShipsByCompany(companyId);
    }
  }, [contract]);

  // Load ships when company changes
  const loadShipsByCompany = async (companyId) => {
    if (!companyId) {
      setShips([]);
      return;
    }

    setLoadingShips(true);
    try {
      const shipsData = await fetchShipsByCompany(companyId);
      setShips(shipsData);
    } catch (error) {
      console.error("Failed to load ships:", error);
      notify.error("Failed to load ships for selected company");
      setShips([]);
    } finally {
      setLoadingShips(false);
    }
  };

  // Handle company change (trigger ship reload)
  const handleCompanyChange = async (val) => {
    handleBatchChange({
      company: val,
      ship: "", // Reset ship selection
    });
    await loadShipsByCompany(val);
  };

  // Calculate contract duration
  const calculateDuration = (signOnDate, signOffDate) => {
    if (!signOnDate || !signOffDate) return null;
    const start = new Date(signOnDate);
    const end = new Date(signOffDate);
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    const diffMonths = Math.round(diffDays / 30);
    return diffMonths;
  };

  const previewDuration = calculateDuration(formData.sign_on_date, formData.sign_off_date);

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

  // Render field
  const renderField = (field) => {
    // Removed temporary edit mode workaround for TypeaheadInputs

    const commonProps = {
      key: field.name,
      name: field.name,
      label: field.label,
      required: field.required,
      value: formData[field.name],
      onChange: (val) => {
        // Special handling for company (triggers ship load)
        if (field.name === "company") {
          handleCompanyChange(val);
          return;
        }

        handleChange(field.name, val);
      },
      error: errors[field.name],
      placeholder: field.placeholder,
      variant: "dashboard",
      ...field.props,
    };

    // Special handling for ship field
    if (field.name === "ship") {
      return (
        <div key={field.name}>
          <Select
            {...commonProps}
            options={field.options}
            disabled={!formData.company || loadingShips}
          />
          {!formData.company && (
            <span style={{ fontSize: "12px", color: "#8C8C8C", marginTop: "4px", display: "block" }}>
              Select a company first to see available ships
            </span>
          )}
          {formData.company && ships.length === 0 && !loadingShips && (
            <span style={{ fontSize: "12px", color: "#8C8C8C", marginTop: "4px", display: "block" }}>
              No ships found for this company
            </span>
          )}
        </div>
      );
    }

    // Special handling for sign_off_date (show duration preview)
    if (field.name === "sign_off_date") {
      return (
        <div key={field.name}>
          <DateInput
            {...commonProps}
            min={formData.sign_on_date}
          />
          {previewDuration !== null && !errors.sign_off_date && (
            <div style={{ fontSize: "12px", color: "#059669", fontWeight: 500, marginTop: "4px" }}>
              Duration: {previewDuration} {previewDuration === 1 ? "month" : "months"}
            </div>
          )}
        </div>
      );
    }

    switch (field.component) {
      case "BaseInput":
        return <BaseInput {...commonProps} type={field.type} />;

      case "Select":
        return <Select {...commonProps} options={field.options} />;

      case "DateInput":
        return <DateInput {...commonProps} />;

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
      aria-labelledby="document-form-modal-title"
    >
      <div
        style={{
          ...modalStyles.panel,
          maxWidth: `${Math.round(650 * scale)}px`,
          maxHeight: "90vh",
          overflowY: "auto",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="document-form-modal-title" style={titleStyles}>
          {isEditMode ? "Edit Contract" : "Generate New Contract"}
        </h2>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: `${Math.round(16 * scale)}px`,
          }}
        >
          {enrichedFieldConfig.map((field) => {
            // Salary and currency in grid
            if (field.name === "currency") return null;

            if (field.name === "salary") {
              return (
                <div
                  key="salary-grid"
                  style={{
                    display: "grid",
                    gridTemplateColumns: "2fr 1fr",
                    gap: `${Math.round(12 * scale)}px`,
                  }}
                >
                  {renderField(field)}
                  {renderField(enrichedFieldConfig.find((f) => f.name === "currency"))}
                </div>
              );
            }

            return renderField(field);
          })}
        </div>

        <div
          style={{
            display: "flex",
            gap: `${Math.round(12 * scale)}px`,
            justifyContent: "flex-end",
            marginTop: `${Math.round(24 * scale)}px`,
            paddingTop: `${Math.round(16 * scale)}px`,
            borderTop: "1px solid #E5E7EB",
          }}
        >
          <Button variant="outline" onClick={handleClose} scale={scale} disabled={loading}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSave} scale={scale} disabled={loading} loading={loading}>
            {loading ? "Saving..." : isEditMode ? "Update Contract" : "Generate Contract"}
          </Button>
        </div>

        <div style={{ marginTop: "12px", fontSize: "11px", color: "#8C8C8C", textAlign: "center" }}>
          Press <kbd style={{ padding: "2px 4px", backgroundColor: "#F3F4F6", borderRadius: "3px", fontFamily: "monospace" }}>Esc</kbd> to close •{" "}
          <kbd style={{ padding: "2px 4px", backgroundColor: "#F3F4F6", borderRadius: "3px", fontFamily: "monospace" }}>Ctrl+Enter</kbd> to save
        </div>
      </div>
    </div>
  );
};

export default DocumentFormModal;