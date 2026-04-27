// Components/Common/SearchResultCard.jsx
// Displays individual search result item
// Click to navigate to relevant page with item highlighted

import React from "react";
import { STYLE_TOKENS, getScaledValue } from "../../Styles/globalStyles";

/**
 * SearchResultCard Component
 *
 * Displays a single search result with:
 * - Category badge
 * - Primary info (name/title)
 * - Secondary info (position, company, etc.)
 * - Click to navigate
 *
 * @param {object} result - Search result item
 * @param {string} category - Result category (cvs, companies, etc.)
 * @param {string} query - Search query for highlighting
 * @param {function} onClick - Click handler
 * @param {number} scale - Scale factor
 */
const SearchResultCard = ({ result, category, query, onClick, scale = 1 }) => {
  // Category configurations
  const categoryConfig = {
    cvs: {
      label: "CV",
      color: "#52C93F",
      primaryField: "name",
      secondaryFields: ["position", "experience", "status"],
    },
    companies: {
      label: "Company",
      color: "#2477C3",
      primaryField: "name",
      secondaryFields: ["type", "email", "status"],
    },
    ships: {
      label: "Ship",
      color: "#06A7FF",
      primaryField: "name",
      secondaryFields: ["imoNumber", "company", "status"],
    },
    users: {
      label: "User",
      color: "#BF4DD1",
      primaryField: "name",
      secondaryFields: ["email", "role", "status"],
    },
    interviews: {
      label: "Interview",
      color: "#7D6335",
      primaryField: "candidateName",
      secondaryFields: ["position", "company", "date"],
    },
    documents: {
      label: "Document",
      color: "#1A65A9",
      primaryField: "name",
      secondaryFields: ["position", "status"],
    },
    finance: {
      label: "Finance",
      color: "#35C2FD",
      primaryField: "user",
      secondaryFields: ["company", "startDate"],
    },
  };

  const config = categoryConfig[category] || categoryConfig.cvs;

  // Highlight matching text
  const highlightText = (text) => {
    if (!query || !text) return text;

    const regex = new RegExp(`(${query})`, "gi");
    const parts = String(text).split(regex);

    return parts.map((part, i) =>
      regex.test(part) ? (
        <mark
          key={i}
          style={{
            backgroundColor: "rgba(255, 235, 59, 0.5)",
            padding: "0 2px",
            borderRadius: "2px",
          }}
        >
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  // Calculate sizes
  const padding = getScaledValue(16, scale);
  const borderRadius = getScaledValue(12, scale);
  const badgePadding = `${getScaledValue(4, scale)}px ${getScaledValue(
    12,
    scale
  )}px`;
  const primaryFontSize = getScaledValue(16, scale);
  const secondaryFontSize = getScaledValue(14, scale);
  const badgeFontSize = getScaledValue(12, scale);

  return (
    <div
      onClick={() => onClick && onClick(result, category)}
      style={{
        display: "flex",
        flexDirection: "column",
        gap: `${getScaledValue(8, scale)}px`,
        padding: `${padding}px`,
        backgroundColor: STYLE_TOKENS.colors.white,
        borderRadius: `${borderRadius}px`,
        border: `1px solid ${STYLE_TOKENS.colors.borderColor}`,
        cursor: "pointer",
        transition: STYLE_TOKENS.transition.normal,
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = STYLE_TOKENS.shadow.md;
        e.currentTarget.style.borderColor = STYLE_TOKENS.colors.primary;
        e.currentTarget.style.transform = "translateY(-2px)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = "none";
        e.currentTarget.style.borderColor = STYLE_TOKENS.colors.borderColor;
        e.currentTarget.style.transform = "translateY(0)";
      }}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          onClick && onClick(result, category);
        }
      }}
    >
      {/* Category Badge */}
      <div
        style={{
          display: "inline-flex",
          alignSelf: "flex-start",
          padding: badgePadding,
          backgroundColor: `${config.color}20`,
          color: config.color,
          borderRadius: `${getScaledValue(16, scale)}px`,
          fontSize: `${badgeFontSize}px`,
          fontWeight: 600,
          fontFamily: STYLE_TOKENS.fonts.heading,
          textTransform: "uppercase",
          letterSpacing: "0.5px",
        }}
      >
        {config.label}
      </div>

      {/* Primary Info */}
      <div
        style={{
          fontSize: `${primaryFontSize}px`,
          fontWeight: 600,
          color: STYLE_TOKENS.colors.darkText,
          fontFamily: STYLE_TOKENS.fonts.heading,
          lineHeight: 1.4,
        }}
      >
        {highlightText(result[config.primaryField])}
      </div>

      {/* Secondary Info */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: `${getScaledValue(12, scale)}px`,
          fontSize: `${secondaryFontSize}px`,
          color: STYLE_TOKENS.colors.lightText,
          fontFamily: STYLE_TOKENS.fonts.primary,
        }}
      >
        {config.secondaryFields.map((field, idx) => {
          const value = result[field];
          if (!value) return null;

          return (
            <span key={idx}>
              {highlightText(value)}
              {idx < config.secondaryFields.length - 1 && " • "}
            </span>
          );
        })}
      </div>
    </div>
  );
};

export default SearchResultCard;
