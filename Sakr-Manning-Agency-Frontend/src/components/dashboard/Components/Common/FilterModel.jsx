// components/Common/FilterModal.jsx
// Reusable filter modal component used across CV, Company, Users pages

import React, { useEffect, useRef } from "react";
import Button from "./Button";
import {
  getModalStyles,
  getFormFieldStyles,
} from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";

/**
 * FilterModal Component
 *
 * Generic, reusable modal for filtering data across all pages
 * Handles dynamic form field generation based on configuration
 *
 * @param {boolean} isOpen - Control modal visibility
 * @param {function} onClose - Callback when modal closes
 * @param {string} title - Modal title (e.g., "Filter CVs")
 * @param {array} fields - Array of field configurations
 * @param {object} values - Current filter values
 * @param {function} onValuesChange - Callback when values change
 * @param {function} onApply - Callback when Apply button clicked
 * @param {function} onReset - Callback when Reset button clicked
 * @param {number} scale - Scale factor for responsive sizing
 *
 * Field Configuration Format:
 * [
 *   {
 *     key: 'status',                    // Unique field identifier
 *     label: 'Status',                  // Display label
 *     type: 'select',                   // 'select', 'text', 'date', 'number'
 *     options: [                        // For select type only
 *       { value: 'Under Review', label: 'Under Review' },
 *       { value: 'Approved', label: 'Approved' }
 *     ],
 *     placeholder: 'Select status'      // Optional
 *   },
 *   {
 *     key: 'dateFrom',
 *     label: 'Date From',
 *     type: 'date'
 *   },
 *   {
 *     key: 'dateTo',
 *     label: 'Date To',
 *     type: 'date'
 *   }
 * ]
 *
 * @example
 * const filterFields = [
 *   {
 *     key: 'status',
 *     label: 'Status',
 *     type: 'select',
 *     options: [
 *       { value: 'Active', label: 'Active' },
 *       { value: 'INACTIVE', label: 'Inactive' }
 *     ]
 *   },
 *   {
 *     key: 'type',
 *     label: 'Type',
 *     type: 'select',
 *     options: [
 *       { value: 'Shipping', label: 'Shipping' },
 *       { value: 'Cruise', label: 'Cruise' }
 *     ]
 *   }
 * ];
 *
 * <FilterModal
 *   isOpen={showFilterModal}
 *   onClose={() => setShowFilterModal(false)}
 *   title="Filter Companies"
 *   fields={filterFields}
 *   values={filters}
 *   onValuesChange={setFilters}
 *   onApply={handleApplyFilters}
 *   onReset={handleResetFilters}
 *   scale={scale}
 * />
 */
const FilterModal = ({
  isOpen,
  onClose,
  title,
  fields,
  values,
  onValuesChange,
  onApply,
  onReset,
  scale = 1,
}) => {
  const firstFieldRef = useRef(null);
  const modalStyles = getModalStyles(scale);
  const formFieldStyles = getFormFieldStyles(scale);
  const titleStyles = getModalTitleStyles(scale);

  // Focus management: focus first field when modal opens
  useEffect(() => {
    if (isOpen && firstFieldRef.current) {
      firstFieldRef.current.focus();
    }

    // Keyboard shortcut: Escape key closes modal
    if (isOpen) {
      const handleKeyDown = (e) => {
        if (e.key === "Escape") {
          onClose();
        }
      };

      document.addEventListener("keydown", handleKeyDown);
      return () => document.removeEventListener("keydown", handleKeyDown);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  // Handle field value changes
  const handleFieldChange = (fieldKey, value) => {
    onValuesChange({
      ...values,
      [fieldKey]: value,
    });
  };

  // Render input based on field type
  const renderField = (field, isFirst = false) => {
    const fieldValue = values[field.key] || "";

    switch (field.type) {
      case "select":
        return (
          <select
            ref={isFirst ? firstFieldRef : null}
            value={fieldValue}
            onChange={(e) => handleFieldChange(field.key, e.target.value || "")}
            style={formFieldStyles.input}
          >
            <option value="">{field.placeholder || "All Options"}</option>
            {field.options?.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        );

      case "date":
        return (
          <input
            ref={isFirst ? firstFieldRef : null}
            type="date"
            value={fieldValue}
            onChange={(e) => handleFieldChange(field.key, e.target.value)}
            style={formFieldStyles.input}
          />
        );

      case "text":
        return (
          <input
            ref={isFirst ? firstFieldRef : null}
            type="text"
            placeholder={field.placeholder || "Enter text"}
            value={fieldValue}
            onChange={(e) => handleFieldChange(field.key, e.target.value)}
            style={formFieldStyles.input}
          />
        );

      case "number":
        return (
          <input
            ref={isFirst ? firstFieldRef : null}
            type="number"
            placeholder={field.placeholder || "Enter number"}
            value={fieldValue}
            onChange={(e) => handleFieldChange(field.key, e.target.value)}
            style={formFieldStyles.input}
          />
        );

      default:
        return null;
    }
  };

  return (
    <div
      style={modalStyles.overlay}
      role="dialog"
      aria-modal="true"
      aria-labelledby="filter-modal-title"
      onClick={onClose}
    >
      <div style={modalStyles.panel} onClick={(e) => e.stopPropagation()}>
        {/* Modal Title */}
        <h2 id="filter-modal-title" style={{ ...titleStyles, flexShrink: 0 }}>
          {title}
        </h2>

        {/* Filter Fields */}
        <div style={{ flex: 1, overflowY: 'auto', paddingRight: '4px' }}>
          {fields.map((field, index) => (
            <div key={field.key} style={formFieldStyles.wrapper}>
              <label style={formFieldStyles.label}>{field.label}</label>
              {renderField(field, index === 0)}
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
            flexShrink: 0,
          }}
        >
          <Button variant="outline" onClick={onReset} scale={scale}>
            Reset
          </Button>
          <Button variant="primary" onClick={onApply} scale={scale}>
            Apply Filters
          </Button>
        </div>
      </div>
    </div>
  );
};

export default FilterModal;
