// components/Common/EnhancedFilterModal.jsx
// Updated FilterModal that supports multi-select fields
// Drop-in replacement for existing FilterModal

import React, { useEffect, useRef } from "react";
import Button from "./Button";
import MultiSelectFilter from "./MultiSelectFilter";
import { getModalStyles } from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";
import { getFormFieldStyles } from "../../Styles/componentStyles";
/**
 * EnhancedFilterModal Component
 *
 * Extended version of FilterModal with multi-select support
 * Backwards compatible with existing FilterModal usage
 *
 * Field types supported:
 * - 'select': Single select dropdown
 * - 'multi-select': Multi-select with checkboxes
 * - 'text': Text input
 * - 'date': Date input
 * - 'number': Number input
 *
 * @param {boolean} isOpen - Modal visibility
 * @param {function} onClose - Close callback
 * @param {string} title - Modal title
 * @param {array} fields - Field configurations
 * @param {object} values - Filter values
 * @param {function} onValuesChange - Value change callback
 * @param {function} onApply - Apply filters callback
 * @param {function} onReset - Reset filters callback
 * @param {number} scale - Scale factor
 *
 * Field Configuration:
 * {
 *   key: 'status',
 *   label: 'Status',
 *   type: 'select' OR 'multi-select',
 *   options: [{ value: 'Active', label: 'Active' }],
 *   placeholder: 'Select...'
 * }
 */
const EnhancedFilterModal = ({
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

  useEffect(() => {
    if (isOpen && firstFieldRef.current) {
      firstFieldRef.current.focus();
    }

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

  const handleFieldChange = (fieldKey, value) => {
    onValuesChange({
      ...values,
      [fieldKey]: value,
    });
  };

  const renderField = (field, isFirst = false) => {
    const fieldValue =
      values[field.key] || (field.type === "multi-select" ? [] : "");

    switch (field.type) {
      case "multi-select":
        return (
          <MultiSelectFilter
            label={field.label}
            options={field.options || []}
            selectedValues={Array.isArray(fieldValue) ? fieldValue : []}
            onChange={(selected) => handleFieldChange(field.key, selected)}
            scale={scale}
            placeholder={field.placeholder || "Select options"}
          />
        );

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
        <h2 id="filter-modal-title" style={titleStyles}>
          {title}
        </h2>

        {fields.map((field, index) => (
          <div key={field.key} style={formFieldStyles.wrapper}>
            <label style={formFieldStyles.label}>{field.label}</label>
            {renderField(field, index === 0)}
          </div>
        ))}

        <div
          style={{
            display: "flex",
            gap: `${Math.round(12 * scale)}px`,
            justifyContent: "flex-end",
            marginTop: `${Math.round(24 * scale)}px`,
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

export default EnhancedFilterModal;
