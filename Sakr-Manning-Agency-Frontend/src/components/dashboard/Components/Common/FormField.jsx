// Components/Common/FormField.jsx
// Reusable form field component supporting multiple input types

import React from "react";
import { STYLE_TOKENS, getScaledValue } from "../../Styles/globalStyles";
import MultiSelectFilter from "./MultiSelectFilter";

/**
 * FormField Component
 *
 * Generic form field that adapts to different input types
 * Supports: text, email, number, date, select, multi-select, textarea, checkbox
 */
const FormField = React.forwardRef(
  (
    {
      field,
      value,
      onChange,
      error = null,
      disabled = false,
      scale = 1,
      onBlur,
    },
    ref
  ) => {
    const {
      name,
      label,
      type = "text",
      placeholder = "",
      required = false,
      options = [],
      rows = 4,
      helpText = "",
    } = field;

    // Calculate sizes
    const labelFontSize = getScaledValue(14, scale);
    const inputPadding = getScaledValue(10, scale);
    const borderRadius = getScaledValue(8, scale);
    const fontSize = getScaledValue(14, scale);

    // Base styles
    const labelStyle = {
      display: "block",
      fontSize: `${labelFontSize}px`,
      fontWeight: 500,
      color: STYLE_TOKENS.colors.darkText,
      marginBottom: `${getScaledValue(8, scale)}px`,
      fontFamily: STYLE_TOKENS.fonts.heading,
    };

    const inputBaseStyle = {
      width: "100%",
      padding: `${inputPadding}px`,
      fontSize: `${fontSize}px`,
      fontFamily: STYLE_TOKENS.fonts.primary,
      border: `1px solid ${
        error ? STYLE_TOKENS.colors.rejected : STYLE_TOKENS.colors.borderColor
      }`,
      borderRadius: `${borderRadius}px`,
      backgroundColor: disabled
        ? STYLE_TOKENS.colors.background
        : STYLE_TOKENS.colors.white,
      color: STYLE_TOKENS.colors.darkText,
      boxSizing: "border-box",
      transition: STYLE_TOKENS.transition.normal,
      outline: "none",
    };

    const errorStyle = {
      fontSize: `${getScaledValue(12, scale)}px`,
      color: STYLE_TOKENS.colors.rejected,
      marginTop: `${getScaledValue(4, scale)}px`,
      fontFamily: STYLE_TOKENS.fonts.primary,
    };

    const helpTextStyle = {
      fontSize: `${getScaledValue(12, scale)}px`,
      color: STYLE_TOKENS.colors.lightText,
      marginTop: `${getScaledValue(4, scale)}px`,
      fontFamily: STYLE_TOKENS.fonts.primary,
    };

    // Handle change events
    const handleChange = (e) => {
      if (type === "checkbox") {
        onChange(name, e.target.checked);
      } else if (type === "number") {
        onChange(name, e.target.value ? Number(e.target.value) : "");
      } else {
        onChange(name, e.target.value);
      }
    };

    // Handle multi-select change
    const handleMultiSelectChange = (selectedValues) => {
      onChange(name, selectedValues);
    };

    // Handle blur
    const handleBlur = () => {
      if (onBlur) {
        onBlur(name);
      }
    };

    // Render input based on type
    const renderInput = () => {
      switch (type) {
        case "textarea":
          return (
            <textarea
              id={name}
              name={name}
              value={value || ""}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder={placeholder}
              disabled={disabled}
              rows={rows}
              style={{
                ...inputBaseStyle,
                resize: "vertical",
                minHeight: `${getScaledValue(100, scale)}px`,
              }}
            />
          );

        case "select":
          return (
            <select
              id={name}
              name={name}
              value={value || ""}
              onChange={handleChange}
              onBlur={handleBlur}
              disabled={disabled}
              style={{
                ...inputBaseStyle,
                cursor: disabled ? "not-allowed" : "pointer",
              }}
            >
              <option value="">{placeholder || "Select an option..."}</option>
              {options.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          );

        case "multi-select":
          return (
            <MultiSelectFilter
              label=""
              options={options}
              selectedValues={Array.isArray(value) ? value : []}
              onChange={handleMultiSelectChange}
              scale={scale}
              placeholder={placeholder || "Select options..."}
            />
          );

        case "checkbox":
          return (
            <label
              style={{
                display: "flex",
                alignItems: "center",
                gap: `${getScaledValue(8, scale)}px`,
                cursor: disabled ? "not-allowed" : "pointer",
              }}
            >
              <input
                type="checkbox"
                id={name}
                name={name}
                checked={value || false}
                onChange={handleChange}
                onBlur={handleBlur}
                disabled={disabled}
                style={{
                  width: `${getScaledValue(18, scale)}px`,
                  height: `${getScaledValue(18, scale)}px`,
                  cursor: disabled ? "not-allowed" : "pointer",
                  accentColor: STYLE_TOKENS.colors.primary,
                }}
              />
              <span
                style={{
                  fontSize: `${fontSize}px`,
                  color: STYLE_TOKENS.colors.darkText,
                  fontFamily: STYLE_TOKENS.fonts.primary,
                }}
              >
                {label}
              </span>
            </label>
          );

        case "date":
        case "email":
        case "number":
        case "text":
        default:
          return (
            <input
              ref={ref}
              type={type}
              id={name}
              name={name}
              value={value || ""}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder={placeholder}
              disabled={disabled}
              style={inputBaseStyle}
              onFocus={(e) => {
                if (!error) {
                  e.target.style.borderColor = STYLE_TOKENS.colors.primary;
                  e.target.style.boxShadow =
                    "0px 0px 0px 3px rgba(5, 107, 182, 0.1)";
                }
              }}
            />
          );
      }
    };

    return (
      <div
        style={{
          marginBottom: `${getScaledValue(20, scale)}px`,
        }}
      >
        {/* Label (skip for checkbox as it's inline) */}
        {type !== "checkbox" && (
          <label htmlFor={name} style={labelStyle}>
            {label}
            {required && (
              <span style={{ color: STYLE_TOKENS.colors.rejected }}> *</span>
            )}
          </label>
        )}

        {/* Input */}
        {renderInput()}

        {/* Help Text */}
        {helpText && !error && <div style={helpTextStyle}>{helpText}</div>}

        {/* Error Message */}
        {error && <div style={errorStyle}>{error}</div>}
      </div>
    );
  }
);

FormField.displayName = "FormField";

export default FormField;