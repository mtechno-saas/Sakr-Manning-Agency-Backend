// components/Common/EnhancedFilterModal.jsx
import React, { useEffect, useRef, useState } from "react";
import Button from "./Button";
import FormField from "./FormField";
import { getModalStyles, getFormFieldStyles, getFilterModalStyles } from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";
import { STYLE_TOKENS, getScaledValue } from "../../Styles/globalStyles";

/**
 * FilterSection Component
 * Individual expandable accordion for filter groups
 */
const FilterSection = ({ title, children, scale = 1, defaultOpen = false }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  
  return (
    <div style={{ 
      marginBottom: getScaledValue(16, scale), 
      border: "1.5px solid #F1F5F9", 
      borderRadius: getScaledValue(16, scale), 
      overflow: "hidden",
      backgroundColor: "#FFFFFF",
      boxShadow: isOpen ? "0 4px 12px rgba(0,0,0,0.03)" : "none",
      transition: "all 0.3s ease"
    }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: "100%",
          padding: `${getScaledValue(16, scale)}px ${getScaledValue(20, scale)}px`,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          background: isOpen ? "#F8FAFC" : "#FFFFFF",
          border: "none",
          cursor: "pointer",
          transition: "background 0.2s ease"
        }}
      >
        <span style={{ 
          fontSize: getScaledValue(12, scale), 
          fontWeight: 800, 
          color: "#475569", 
          textTransform: "uppercase", 
          letterSpacing: "1px",
          fontFamily: STYLE_TOKENS.fonts.heading 
        }}>
          {title}
        </span>
        <div style={{
          width: getScaledValue(24, scale),
          height: getScaledValue(24, scale),
          borderRadius: "50%",
          background: isOpen ? STYLE_TOKENS.colors.primary : "#F1F5F9",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transition: "all 0.3s ease"
        }}>
          <svg 
            width="14" height="14" viewBox="0 0 24 24" fill="none" 
            stroke={isOpen ? "#FFFFFF" : "#64748B"} 
            strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"
            style={{ transform: isOpen ? "rotate(180deg)" : "rotate(0deg)", transition: "transform 0.3s ease" }}
          >
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </div>
      </button>
      {isOpen && (
        <div style={{ 
          padding: getScaledValue(20, scale), 
          background: "#FFFFFF", 
          borderTop: "1.5px solid #F1F5F9",
          animation: "fadeIn 0.3s ease-out"
        }}>
          {children}
        </div>
      )}
    </div>
  );
};

const EnhancedFilterModal = ({
  isOpen,
  onClose,
  title,
  fields, 
  sections, 
  values,
  onValuesChange,
  onApply,
  onReset,
  scale = 1,
}) => {
  const [isMounted, setIsMounted] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const firstFieldRef = useRef(null);

  const filterStyles = getFilterModalStyles(scale);

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

  const renderField = (field, index) => {
    const span = field.colSpan || (field.fullWidth || field.type === "multi-select" || field.type === "checkbox" ? 12 : 6);
    
    return (
      <div 
        key={field.key} 
        className="field-item filter-field"
        style={{ 
          gridColumn: span >= 12 ? "1 / -1" : `span ${span}`,
          marginBottom: getScaledValue(4, scale)
        }}
      >
      <FormField
          field={{
              ...field,
              name: field.key,
              placeholder: field.placeholder || (field.type === 'select' || field.type === 'multi-select' ? "All Options" : `Enter ${field.label}...`)
          }}
          value={values[field.key]}
          onChange={handleFieldChange}
          scale={scale}
          ref={index === 0 ? firstFieldRef : null}
      />
    </div>
    );
  };

  return (
    <div
      style={{
        ...filterStyles.overlay,
        overflowY: "auto",
        padding: `${Math.round(40 * scale)}px 0`,
        opacity: isVisible ? 1 : 0,
        transition: "opacity 0.3s ease",
        zIndex: 2000,
      }}
      onClick={onClose}
      role="dialog"
      aria-modal="true"
    >
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .filter-grid {
          display: grid;
          grid-template-columns: repeat(12, 1fr);
          gap: 0 ${getScaledValue(20, scale)}px;
        }
        @media (max-width: 600px) {
          .filter-grid {
            display: flex;
            flex-direction: column;
          }
        }
        .filter-field label {
          font-size: ${getScaledValue(11, scale)}px !important;
          text-transform: uppercase !important;
          letter-spacing: 0.5px !important;
          color: #64748B !important;
          font-weight: 700 !important;
          margin-bottom: ${getScaledValue(6, scale)}px !important;
          font-family: ${STYLE_TOKENS.fonts.heading} !important;
        }
        .filter-field input, .filter-field select, .filter-field button {
            background-color: #F8FAFC !important;
            border-radius: ${getScaledValue(12, scale)}px !important;
            height: ${getScaledValue(42, scale)}px !important;
            font-size: ${getScaledValue(13, scale)}px !important;
            border: 1px solid #E2E8F0 !important;
            transition: all 0.2s ease !important;
        }
        .filter-field input:focus, .filter-field button:focus {
            border-color: ${STYLE_TOKENS.colors.primary} !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
            background-color: #FFFFFF !important;
        }
      `}</style>

      <div
        style={{
          ...filterStyles.panel,
          position: "relative",
          maxWidth: getScaledValue(760, scale),
          width: "95%",
          maxHeight: "92vh",
          padding: getScaledValue(32, scale),
          borderRadius: getScaledValue(32, scale),
          boxShadow: "0 25px 70px rgba(0, 0, 0, 0.15)",
          display: "flex",
          flexDirection: "column",
          gap: 0,
          overflow: "hidden",
          margin: "auto",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: getScaledValue(28, scale), flexShrink: 0 }}>
          <div>
            <h2 style={{ ...filterStyles.title, margin: 0, fontSize: getScaledValue(24, scale), fontWeight: 800, color: "#1E293B" }}>
              {title}
            </h2>
            <p style={{ color: STYLE_TOKENS.colors.lightText, fontSize: getScaledValue(13, scale), marginTop: getScaledValue(4, scale), fontWeight: 500 }}>
              {sections 
                ? sections.reduce((acc, s) => acc + s.fields.length, 0) 
                : (fields?.length || 0)} parameters available to refine results
            </p>
          </div>
          <button 
            style={{ 
              width: getScaledValue(36, scale), 
              height: getScaledValue(36, scale), 
              borderRadius: "12px", 
              border: "1px solid #E2E8F0", 
              background: "#FFFFFF", 
              display: "flex", 
              alignItems: "center", 
              justifyContent: "center", 
              cursor: "pointer", 
              color: "#94A3B8",
              transition: "all 0.2s ease"
            }}
            onMouseOver={(e) => { e.currentTarget.style.background = "#F8FAFC"; e.currentTarget.style.color = "#475569"; }}
            onMouseOut={(e) => { e.currentTarget.style.background = "#FFFFFF"; e.currentTarget.style.color = "#94A3B8"; }}
            onClick={onClose} 
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>

        <div style={{ flex: 1, overflowY: "auto", paddingRight: getScaledValue(8, scale), scrollbarWidth: 'thin' }}>
          {sections ? (
            sections.map((section, sIdx) => {
              let currentRowSpan = 0;
              return (
                <FilterSection key={sIdx} title={section.title} scale={scale} defaultOpen={sIdx === 0}>
                  <div className="filter-grid">
                    {section.fields.map((field, fIdx) => {
                      const isLast = fIdx === section.fields.length - 1;
                      let span = field.colSpan || (field.fullWidth || field.type === "multi-select" || field.type === "checkbox" ? 12 : 6);
                      if (isLast && currentRowSpan % 12 === 0) span = 12;
                      currentRowSpan += span;
                      return renderField({ ...field, colSpan: span }, fIdx);
                    })}
                  </div>
                </FilterSection>
              );
            })
          ) : (
            <div className="filter-grid">
              {fields && fields.map((field, fIdx) => renderField(field, fIdx))}
            </div>
          )}
        </div>

        <div style={{ 
          display: "flex", 
          gap: getScaledValue(16, scale), 
          justifyContent: "flex-end", 
          marginTop: getScaledValue(24, scale), 
          paddingTop: getScaledValue(24, scale), 
          borderTop: `1.5px solid #F1F5F9`, 
          flexShrink: 0 
        }}>
          <Button 
            variant="outline" 
            onClick={onReset} 
            scale={scale} 
            style={{ borderRadius: getScaledValue(14, scale), minWidth: getScaledValue(110, scale), height: getScaledValue(44, scale) }}
          >
            Reset All
          </Button>
          <Button 
            variant="primary" 
            onClick={onApply} 
            scale={scale} 
            style={{ borderRadius: getScaledValue(14, scale), minWidth: getScaledValue(160, scale), height: getScaledValue(44, scale), boxShadow: "0 4px 12px rgba(37, 99, 235, 0.2)" }}
          >
            Apply Filters
          </Button>
        </div>
      </div>
    </div>
  );
};

export default EnhancedFilterModal;
