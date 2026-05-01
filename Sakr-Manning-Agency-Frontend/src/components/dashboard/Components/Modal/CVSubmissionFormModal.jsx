// components/dashboard/Modal/CVSubmissionFormModal.jsx
import React, { useState, useEffect, useMemo } from "react";
import Button from "../Common/Button";
import { getModalStyles } from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";

// Import form components
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { DateInput } from "../inputs/DateInput";
import { TextArea } from "../../../form/inputs/TextArea";

// Import refactoring utilities
import { useFormModal } from "../../hooks/useFormModal";
import { CV_SUBMISSION_FORM_FIELDS } from "../../../../utils/dashboard/fieldConfigs";

// Import APIs
import { usersApi } from "../../../../services/Dashboard/usersApi";
import { companiesApi } from "../../../../services/Dashboard/companiesApi";
import useNotification from "../../hooks/useNotification";

/**
 * CVSubmissionFormModal - Dedicated form for recruitment pipeline entries (Section 4)
 * 
 * Allows Admin/HR to:
 * - Link a Seafarer to a Company/Position
 * - Track experience, salary, and availability
 * - Capture cover letters and internal notes/ratings
 */
const CVSubmissionFormModal = ({ submission = null, onClose, onSave, scale = 1 }) => {
  const modalStyles = getModalStyles(scale);
  const titleStyles = getModalTitleStyles(scale);
  const { notify } = useNotification();

  // Reference data
  const [seafarers, setSeafarers] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [ranks, setRanks] = useState([]);
  const [loadingReference, setLoadingReference] = useState(true);

  // Load reference data
  useEffect(() => {
    const loadData = async () => {
      try {
        const [usersRes, companiesRes, positionsRes] = await Promise.all([
          usersApi.getUsers({ role: "employee", page_size: 1000 }),
          companiesApi.getCompanies({ page_size: 1000 }),
          usersApi.getPositions(),  // GET /api/positions/ → [{ value, label }]
        ]);

        const userList = usersRes.users || usersRes.results || (Array.isArray(usersRes) ? usersRes : []);
        const companyList = companiesRes.companies || companiesRes.results || (Array.isArray(companiesRes) ? companiesRes : []);

        setSeafarers(userList);
        setCompanies(companyList);
        setRanks(positionsRes); // positions array: [{ value, label }]
      } catch (error) {
        console.error("Failed to load reference data for CV Submission:", error);
        notify.error("Failed to load users, companies or ranks");
      } finally {
        setLoadingReference(false);
      }
    };
    loadData();
  }, [notify]);

  // Enrich field config with dynamic data
  const enrichedFieldConfig = useMemo(() => {
    return CV_SUBMISSION_FORM_FIELDS.map((field) => {
       if (field.name === "user") {
        const options = seafarers.map((u) => ({
          value: u.id,
          label: `${u.first_name} ${u.middle_name || ""} ${u.last_name || ""} (${u.email})`,
        }));

        // ✅ IMPORTANT: Always include currently selected user if missing from reference data
        if (submission?.user && !options.some((o) => o.value === submission.user)) {
          options.unshift({
            value: submission.user,
            label: submission.user_name || `Seafarer ID: ${submission.user}`,
          });
        }
        return { ...field, options };
      }

      if (field.name === "company") {
        const options = companies.map((c) => ({
          value: c.id,
          label: c.company_name,
        }));

        // ✅ IMPORTANT: Always include currently selected company if missing from reference data
        if (submission?.company && !options.some((o) => o.value === submission.company)) {
          options.unshift({
            value: submission.company,
            label: submission.company_name || `Company ID: ${submission.company}`,
          });
        }
        return { ...field, options };
      }

      if (field.name === "position") {
        // positions endpoint returns [{ value: "Master", label: "Master" }]
        // The backend assign-by-position expects the value string directly
        const options = ranks.map((p) => ({
          value: p.value ?? p.id,
          label: p.label ?? p.name ?? p.value,
        }));

        // Keep currently selected position if not in the list
        if (submission?.position && !options.some((o) => o.value === submission.position)) {
          options.unshift({
            value: submission.position,
            label: submission.position_name || submission.position,
          });
        }
        return { ...field, options };
      }
      return field;
    });
  }, [seafarers, companies, ranks, submission]);

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
    record: submission,
    onSave,
    onClose,
    successMessage: (isEdit) =>
      isEdit ? "Submission updated successfully" : "Submission created successfully",
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

  // Render field
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
      case "DateInput":
        return <DateInput {...commonProps} />;
      case "TextArea":
        return <TextArea {...commonProps} />;
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
          maxWidth: `${Math.round(800 * scale)}px`, // Wider for submission details
          maxHeight: "90vh",
          overflowY: "auto",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={titleStyles}>
          {isEditMode ? "Edit Submission Pipeline" : "New Pipeline Submission"}
        </h2>

        {loadingReference ? (
          <div style={{ padding: "40px", textAlign: "center", color: "#8C8C8C" }}>
            Loading recruitment data...
          </div>
        ) : (
          <>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: `${Math.round(20 * scale)}px`,
              }}
            >
              {/* Links & Logistics */}
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                {renderField(enrichedFieldConfig.find(f => f.name === "user"))}
                {renderField(enrichedFieldConfig.find(f => f.name === "company"))}
                {renderField(enrichedFieldConfig.find(f => f.name === "position"))}
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                {renderField(enrichedFieldConfig.find(f => f.name === "status"))}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                  {renderField(enrichedFieldConfig.find(f => f.name === "experience_years"))}
                  {renderField(enrichedFieldConfig.find(f => f.name === "salary"))}
                </div>
              </div>
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
                {loading ? "Saving..." : isEditMode ? "Update Submission" : "Create Submission"}
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default CVSubmissionFormModal;
