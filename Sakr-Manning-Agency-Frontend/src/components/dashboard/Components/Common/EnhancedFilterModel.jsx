// components/Common/EnhancedFilterModal.jsx
// Premium FilterModal with scalable grid layout and standard FormField components
import React, { useEffect, useRef, useState } from "react";
import Button from "./Button";
import FormField from "./FormField";
import { getModalStyles, getFormFieldStyles } from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";
import { STYLE_TOKENS, getScaledValue } from "../../Styles/globalStyles";

/**
 * EnhancedFilterModal Component
 * Scalable grid layout utilizing standard dashboard FormFields
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
  const [isMounted, setIsMounted] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const firstFieldRef = useRef(null);

  // Style objects
  const modalStyles = getModalStyles(scale);
  const formFieldStyles = getFormFieldStyles(scale);
  const titleStyles = getModalTitleStyles(scale);

  useEffect(() => {
    if (isOpen) {
      setIsMounted(true);
      const timer = setTimeout(() => setIsVisible(true), 10);
      return () => clearTimeout(timer);
    } else {
      setIsVisible(false);
      const timer = setTimeout(() => setIsMounted(false), 300);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") onClose();
    };
    if (isVisible) document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isVisible, onClose]);

  if (!isMounted) return null;

  const handleFieldChange = (fieldName, value) => {
    onValuesChange({ ...values, [fieldName]: value });
  };

  return (
    <div
      style={{
        ...modalStyles.overlay,
        overflowY: "auto",
        padding: `${Math.round(40 * scale)}px 0`,
        opacity: isVisible ? 1 : 0,
        transition: "opacity 0.3s ease",
        zIndex: 2000,
      }}
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="filter-modal-title"
    >
      <style>{`
        .filter-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: ${getScaledValue(8, scale)}px ${getScaledValue(24, scale)}px;
          padding: 2px;
        }
        @media (max-width: 600px) {
          .filter-grid {
            grid-template-columns: 1fr;
          }
        }
        .field-item {
          position: relative;
        }
        /* Override FormField labels for filter look */
        .filter-field label {
          font-size: ${getScaledValue(12, scale)}px !important;
          text-transform: uppercase !important;
          letter-spacing: 0.8px !important;
          color: #6B7280 !important;
          font-weight: 700 !important;
          margin-bottom: ${getScaledValue(6, scale)}px !important;
        }
        .filter-field input, .filter-field select {
            background-color: #FAFAFA !important;
            border-width: 1.5px !important;
            border-radius: ${getScaledValue(12, scale)}px !important;
        }
        .filter-field input:focus, .filter-field select:focus {
            background-color: #FFFFFF !important;
            border-color: ${STYLE_TOKENS.colors.primary} !important;
        }
        /* Tighten spacing between grid rows */
        .filter-field > div {
            margin-bottom: ${getScaledValue(12, scale)}px !important;
        }
      `}</style>

      <div
        style={{
          ...modalStyles.panel,
          position: "relative",
          maxWidth: getScaledValue(780, scale),
          width: "95%",
          padding: getScaledValue(36, scale),
          borderRadius: getScaledValue(32, scale),
          boxShadow: "0 25px 70px rgba(0, 0, 0, 0.2)",
          display: "flex",
          flexDirection: "column",
          gap: 0,
          overflow: "visible",
          margin: "auto",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            marginBottom: getScaledValue(32, scale),
          }}
        >
          <div style={{ display: "flex", flexDirection: "column", gap: getScaledValue(6, scale) }}>
            <h2 id="filter-modal-title" style={{ ...titleStyles, margin: 0, fontSize: getScaledValue(26, scale), fontWeight: 700, letterSpacing: "-0.5px" }}>
              {title}
            </h2>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <div style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: STYLE_TOKENS.colors.primary }}></div>
              <p style={{ color: STYLE_TOKENS.colors.lightText, fontSize: getScaledValue(14, scale), margin: 0, fontWeight: 500 }}>
                {fields.length} available filters
              </p>
            </div>
          </div>
          <button 
            style={{
              width: getScaledValue(36, scale),
              height: getScaledValue(36, scale),
              borderRadius: "12px",
              border: "1px solid #E5E7EB",
              background: "#FFFFFF",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              color: "#6B7280",
            }}
            onClick={onClose} 
            aria-label="Close"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        {/* Grid Body */}
        <div style={{ paddingBottom: getScaledValue(12, scale) }}>
          <div className="filter-grid">
            {fields.map((field, index) => (
              <div 
                key={field.key} 
                className="field-item filter-field"
                style={{ 
                  gridColumn: (field.fullWidth || field.type === "multi-select" || (index === fields.length - 1 && fields.length % 2 !== 0)) ? "1 / -1" : "auto" 
                }}
              >
                <FormField
                    field={{
                        ...field,
                        name: field.key,
                        placeholder: field.placeholder || (field.type === 'select' ? "All Options" : `Enter ${field.label}...`)
                    }}
                    value={values[field.key]}
                    onChange={handleFieldChange}
                    scale={scale}
                    ref={index === 0 ? firstFieldRef : null}
                />
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div
          style={{
            display: "flex",
            gap: getScaledValue(16, scale),
            justifyContent: "flex-end",
            marginTop: getScaledValue(36, scale),
            paddingTop: getScaledValue(28, scale),
            borderTop: `1.5px solid #F3F4F6`,
          }}
        >
          <Button 
            variant="outline" 
            onClick={onReset} 
            scale={scale}
            style={{ 
              borderRadius: getScaledValue(16, scale),
              minWidth: getScaledValue(110, scale),
              border: "1.5px solid #E5E7EB",
              color: "#6B7280",
              fontSize: getScaledValue(14, scale),
              fontWeight: 600,
              backgroundColor: "transparent"
            }}
          >
            Clear All
          </Button>
          <Button 
            variant="primary" 
            onClick={onApply} 
            scale={scale}
            style={{ 
              borderRadius: getScaledValue(16, scale),
              minWidth: getScaledValue(160, scale),
              boxShadow: "0 10px 25px -5px rgba(0, 101, 175, 0.25)",
              fontSize: getScaledValue(14, scale),
              fontWeight: 600
            }}
          >
            Apply Filters
          </Button>
        </div>

        {/* Keyboard Shortcuts Hint */}
        <div style={{ marginTop: "16px", fontSize: "11px", color: "#8C8C8C", textAlign: "center" }}>
          Press <kbd style={{ padding: "2px 4px", backgroundColor: "#F3F4F6", borderRadius: "3px", fontFamily: "monospace" }}>Esc</kbd> to close
        </div>
      </div>
    </div>
  );
};


