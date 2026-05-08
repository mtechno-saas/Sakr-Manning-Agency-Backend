// components/dashboard/Modals/InterviewFormModal.jsx - REFACTORED v2.1
import React, { useMemo } from "react";
import BaseModal from "./BaseModal";
import Button from "../Common/Button";

// Import form components
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { DateInput } from "../inputs/DateInput";
import { TextArea } from "../../../form/inputs/TextArea";

// Import refactoring utilities
import { useFormModal } from "../../hooks/useFormModal"
import { INTERVIEW_FORM_FIELDS } from "../../../../utils/dashboard/fieldConfigs";

// Import context
import { useDashboardData } from "../../context/DashboardDataContext";

/**
 * InterviewFormModal v2.1 - Uses BaseModal for responsive scrolling
 */
const InterviewFormModal = ({
  interview = null,
  onClose,
  onSave,
  preSelectedDate = null,
  scale = 1,
}) => {
  // Get data from context
  const { referenceOptions } = useDashboardData();

  // Enrich field config
  const enrichedFieldConfig = useMemo(() => {
    return INTERVIEW_FORM_FIELDS.map((field) => {
      // Set preSelectedDate if provided
      if (field.name === "scheduled_date" && preSelectedDate && !interview) {
        return { ...field, defaultValue: preSelectedDate };
      }

      // Add dynamic options for candidate
      if (field.name === "candidate") {
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

      // Add dynamic options for position
      if (field.name === "position") {
        return {
          ...field,
          options: referenceOptions.ranks || [],
        };
      }

      return field;
    });
  }, [preSelectedDate, interview, referenceOptions]);

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
    record: interview,
    onSave,
    onClose,
    successMessage: (isEdit) =>
      isEdit ? "Interview updated successfully" : "Interview scheduled successfully",
    transformBeforeSave: (data) => ({
      ...data,
      candidate: parseInt(data.candidate),
      company: parseInt(data.company),
      position: data.position ? parseInt(data.position) : undefined,
      duration_minutes: parseInt(data.duration_minutes),
    }),
  });

  // Render field
  const renderField = (field) => {
    if (field.conditionalDisplay && !field.conditionalDisplay(formData)) {
      return null;
    }

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
      case "DateInput":
        return <DateInput {...commonProps} />;
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
          {loading ? "Saving..." : isEditMode ? "Update Interview" : "Schedule Interview"}
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
      title={isEditMode ? "Edit Interview" : "Schedule New Interview"}
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
        {enrichedFieldConfig.map((field) => (
          <div
            key={field.name}
            style={{
              gridColumn: `span ${field.gridCols || 12}`,
              display: field.conditionalDisplay && !field.conditionalDisplay(formData) ? "none" : "block",
            }}
          >
            {renderField(field)}
          </div>
        ))}
      </div>
    </BaseModal>
  );
};

export default InterviewFormModal;