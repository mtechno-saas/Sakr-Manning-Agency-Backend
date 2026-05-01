// components/dashboard/Components/Modal/GenerateContractModal.jsx
import React, { useState, useEffect, useMemo } from "react";
import Button from "../Common/Button";
import { getModalStyles } from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";

// Import form components
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { DateInput } from "../inputs/DateInput";

import { useFormModal } from "../../hooks/useFormModal";
import { useDashboardData } from "../../context/DashboardDataContext";
import documentsApi from "../../../../services/Dashboard/documentsApi";

export const GENERATE_CONTRACT_FIELDS = [
  {
    name: "ship",
    label: "Ship Assignment",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Ship",
    options: [],
    validation: { required: "Ship is required" }
  },
  {
    name: "sign_on_date",
    label: "Sign-On Date",
    type: "date",
    component: "DateInput",
    required: true,
    placeholder: "Select sign-on date",
    validation: { required: "Sign-on date is required" },
    defaultValue: ""
  },
  {
    name: "sign_off_date",
    label: "Sign-Off Date (Optional)",
    type: "date",
    component: "DateInput",
    required: false,
    placeholder: "Select sign-off date",
    defaultValue: ""
  },
  {
    name: "status",
    label: "Initial Status",
    type: "select",
    component: "Select",
    required: true,
    options: [
      { value: "Draft", label: "Draft" },
      { value: "Pending Signature", label: "Pending Signature" },
      { value: "Active", label: "Active" },
    ],
    defaultValue: "Draft"
  },
  {
    name: "repatriation_terms",
    label: "Repatriation Terms",
    type: "text",
    component: "BaseInput",
    required: false,
    placeholder: "e.g., Company covers return flight...",
    defaultValue: ""
  },
  {
    name: "leave_pay_terms",
    label: "Leave Pay Terms",
    type: "text",
    component: "BaseInput",
    required: false,
    placeholder: "e.g., 30 days paid leave...",
    defaultValue: ""
  }
];

const GenerateContractModal = ({ submission, onClose, onSuccess, scale = 1 }) => {
  const modalStyles = getModalStyles(scale);
  const titleStyles = getModalTitleStyles(scale);
  
  const { fetchShipsByCompany } = useDashboardData();
  const [ships, setShips] = useState([]);
  const [loadingShips, setLoadingShips] = useState(false);

  useEffect(() => {
    if (submission?.company) {
      const loadShips = async () => {
        setLoadingShips(true);
        try {
          const companyId = typeof submission.company === 'object' ? submission.company.id : submission.company;
          if (!companyId) return;
          const shipsData = await fetchShipsByCompany(companyId);
          setShips(shipsData);
        } catch (error) {
          console.error("Failed to load ships", error);
        } finally {
          setLoadingShips(false);
        }
      };
      loadShips();
    }
  }, [submission, fetchShipsByCompany]);

  const enrichedFields = useMemo(() => {
    return GENERATE_CONTRACT_FIELDS.map(f => {
      if (f.name === "ship") {
        return {
          ...f,
          options: ships.map(s => ({
            value: s.id,
            label: `${s.ship_name} ${s.imo_number ? `(${s.imo_number})` : ''}`
          }))
        };
      }
      return f;
    });
  }, [ships]);

  const handleCreate = async (data) => {
    try {
      const payload = {
        cv_submission_id: submission.id,
        ship: parseInt(data.ship),
        sign_on_date: data.sign_on_date,
        status: data.status || "Draft",
        sign_off_date: data.sign_off_date || undefined,
        repatriation_terms: data.repatriation_terms || undefined,
        leave_pay_terms: data.leave_pay_terms || undefined
      };
      const result = await documentsApi.createContract(payload);
      if (onSuccess) onSuccess(result);
      return { success: true };
    } catch (error) {
      console.error(error);
      throw error;
    }
  };

  const {
    formData,
    errors,
    loading,
    handleChange,
    handleSave,
    handleClose
  } = useFormModal({
    fieldConfig: enrichedFields,
    record: null,
    onSave: handleCreate,
    onClose,
    successMessage: () => "Contract generated successfully!"
  });

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
    };

    if (field.name === "ship") {
      return (
        <div key={field.name}>
          <Select {...commonProps} options={field.options} disabled={loadingShips || ships.length === 0} />
          {ships.length === 0 && !loadingShips && (
             <span style={{ fontSize: "12px", color: "#8C8C8C", marginTop: "4px", display: "block" }}>
               No ships found for this company. Please ensure the company has assigned ships.
             </span>
          )}
        </div>
      );
    }

    if (field.component === "Select") return <Select {...commonProps} options={field.options} />;
    if (field.component === "DateInput") return <DateInput {...commonProps} />;
    return <BaseInput {...commonProps} type={field.type} />;
  };

  return (
    <div style={modalStyles.overlay} onClick={handleClose}>
      <div 
        style={{...modalStyles.panel, maxWidth: `${Math.round(550 * scale)}px`}}
        onClick={e => e.stopPropagation()}
      >
        <h2 style={{...titleStyles, marginBottom: `${Math.round(8 * scale)}px`}}>Generate Contract</h2>
        <p style={{fontSize: `${Math.round(14 * scale)}px`, color: "#6B7280", marginBottom: `${Math.round(20 * scale)}px`}}>
          Generating contract for <strong>{submission.user_name || "Applicant"}</strong> 
          {submission.position_name ? ` as ${submission.position_name}` : ''}.
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: `${Math.round(16 * scale)}px` }}>
          {enrichedFields.map(renderField)}
        </div>

        <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end", marginTop: "24px", paddingTop: "16px", borderTop: "1px solid #E5E7EB" }}>
          <Button variant="outline" onClick={handleClose} disabled={loading} scale={scale}>Cancel</Button>
          <Button variant="primary" onClick={handleSave} disabled={loading} loading={loading} scale={scale}>Generate</Button>
        </div>
      </div>
    </div>
  );
};

export default GenerateContractModal;
