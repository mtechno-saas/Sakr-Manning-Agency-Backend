// components/Common/MultiSelectFilter.jsx
// Multi-select filter component for advanced filtering
// Allows selecting multiple values instead of just one

import React, { useState, useRef, useEffect } from "react";
import { ChevronDown } from "lucide-react";
import { STYLE_TOKENS, getScaledValue } from "../../Styles/globalStyles";

/**
 * MultiSelectFilter Component
 *
 * Dropdown with checkboxes for selecting multiple filter values
 * Compact display showing selected count
 * Expands on click, collapses on blur
 *
 * @param {string} label - Filter label
 * @param {array} options - Available options: [{ value, label }]
 * @param {array} selectedValues - Currently selected values
 * @param {function} onChange - Callback when selection changes
 * @param {number} scale - Scale factor
 * @param {string} placeholder - Placeholder text
 *
 * @example
 * <MultiSelectFilter
 *   label="Status"
 *   options={[
 *     { value: 'Active', label: 'Active' },
 *     { value: 'Inactive', label: 'Inactive' }
 *   ]}
 *   selectedValues={['Active']}
 *   onChange={(values) => setFilters({ status: values })}
 *   scale={scale}
 * />
 */
const MultiSelectFilter = ({
  label,
  options = [],
  selectedValues = [],
  onChange,
  scale = 1,
  placeholder = "Select options",
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Handle checkbox toggle
  const handleToggle = (value) => {
    const newValues = selectedValues.includes(value)
      ? selectedValues.filter((v) => v !== value)
      : [...selectedValues, value];
    onChange(newValues);
  };

  // Calculate sizes
  const padding = getScaledValue(10, scale);
  const borderRadius = getScaledValue(8, scale);
  const fontSize = getScaledValue(14, scale);
  const dropdownMaxHeight = getScaledValue(300, scale);
  const checkboxSize = getScaledValue(18, scale);

  return (
    <div
      ref={containerRef}
      style={{
        position: "relative",
        width: "100%",
      }}
    >
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: "100%",
          padding: `${padding}px`,
          backgroundColor: STYLE_TOKENS.colors.white,
          border: `1px solid ${STYLE_TOKENS.colors.borderColor}`,
          borderRadius: `${borderRadius}px`,
          fontSize: `${fontSize}px`,
          fontFamily: STYLE_TOKENS.fonts.primary,
          cursor: "pointer",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          transition: STYLE_TOKENS.transition.normal,
          color:
            selectedValues.length > 0
              ? STYLE_TOKENS.colors.darkText
              : STYLE_TOKENS.colors.lightText,
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = STYLE_TOKENS.colors.primary;
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = STYLE_TOKENS.colors.borderColor;
        }}
      >
        <span>
          {selectedValues.length === 0
            ? placeholder
            : `${selectedValues.length} selected`}
        </span>
        <ChevronDown
          size={getScaledValue(18, scale)}
          style={{
            transition: STYLE_TOKENS.transition.normal,
            transform: isOpen ? "rotate(180deg)" : "rotate(0deg)",
          }}
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          style={{
            position: "absolute",
            top: "100%",
            left: 0,
            right: 0,
            marginTop: `${getScaledValue(4, scale)}px`,
            backgroundColor: STYLE_TOKENS.colors.white,
            border: `1px solid ${STYLE_TOKENS.colors.borderColor}`,
            borderRadius: `${borderRadius}px`,
            boxShadow: STYLE_TOKENS.shadow.md,
            maxHeight: `${dropdownMaxHeight}px`,
            overflowY: "auto",
            zIndex: 1000,
            padding: `${getScaledValue(4, scale)}px 0`,
          }}
        >
          {options.map((option) => (
            <label
              key={option.value}
              style={{
                display: "flex",
                alignItems: "center",
                padding: `${getScaledValue(8, scale)}px ${padding}px`,
                cursor: "pointer",
                userSelect: "none",
                transition: STYLE_TOKENS.transition.normal,
                backgroundColor: selectedValues.includes(option.value)
                  ? "rgba(0, 101, 175, 0.05)"
                  : "transparent",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = "rgba(0, 0, 0, 0.03)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = selectedValues.includes(
                  option.value
                )
                  ? "rgba(0, 101, 175, 0.05)"
                  : "transparent";
              }}
            >
              <input
                type="checkbox"
                checked={selectedValues.includes(option.value)}
                onChange={() => handleToggle(option.value)}
                style={{
                  width: `${checkboxSize}px`,
                  height: `${checkboxSize}px`,
                  marginRight: `${getScaledValue(8, scale)}px`,
                  cursor: "pointer",
                  accentColor: STYLE_TOKENS.colors.primary,
                }}
              />
              <span style={{ fontSize: `${fontSize}px`, flex: 1 }}>
                {option.label}
              </span>
            </label>
          ))}
        </div>
      )}
    </div>
  );
};

export default MultiSelectFilter;
