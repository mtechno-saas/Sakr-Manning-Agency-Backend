// components/Common/FilterChips.jsx
// Visual display of active filters as removable chips
// Shows users what's currently filtered at a glance

import React from "react";
import { STYLE_TOKENS, getScaledValue } from "../../Styles/globalStyles";

/**
 * FilterChips Component
 *
 * Displays active filters as removable chips/badges
 * Gives users clear visibility into applied filters
 * Allows quick removal of individual filters or all at once
 *
 * @param {object} activeFilters - Current active filters { status: 'Active', type: 'Shipping' }
 * @param {function} onClearFilter - Called when individual chip's X is clicked: onClearFilter(filterKey)
 * @param {function} onClearAll - Called when "Clear All" is clicked
 * @param {number} scale - Scale factor for responsive sizing
 * @param {object} filterLabels - Optional: Map filter keys to display labels { status: 'Status', type: 'Type' }
 *
 * @example
 * <FilterChips
 *   activeFilters={{ status: 'Active', type: 'Shipping' }}
 *   onClearFilter={(key) => handleClearFilter(key)}
 *   onClearAll={handleResetFilters}
 *   scale={scale}
 *   filterLabels={{ status: 'Status', type: 'Type' }}
 * />
 */
const FilterChips = ({
  activeFilters = {},
  onClearFilter,
  onClearAll,
  scale = 1,
  filterLabels = {},
}) => {
  // Filter out empty values to find which filters are active
  const activeFilterEntries = Object.entries(activeFilters).filter(
    ([key, value]) => value && value !== ""
  );

  // If no active filters, don't render anything
  if (activeFilterEntries.length === 0) {
    return null;
  }

  // Calculate responsive sizes
  const containerGap = getScaledValue(8, scale);
  const chipPadding = `${getScaledValue(6, scale)}px ${getScaledValue(
    12,
    scale
  )}px`;
  const chipBorderRadius = getScaledValue(16, scale);
  const chipFontSize = getScaledValue(14, scale);
  const closeFontSize = getScaledValue(16, scale);

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: `${getScaledValue(12, scale)}px`,
        flexWrap: "wrap",
        marginBottom: `${getScaledValue(12, scale)}px`,
        padding: `${getScaledValue(8, scale)}px 0`,
      }}
    >
      {/* Active Filter Chips */}
      {activeFilterEntries.map(([key, value]) => (
        <div
          key={key}
          style={{
            display: "flex",
            alignItems: "center",
            gap: `${getScaledValue(6, scale)}px`,
            backgroundColor: STYLE_TOKENS.colors.infoLight,
            color: STYLE_TOKENS.colors.infoDark,
            padding: chipPadding,
            borderRadius: `${chipBorderRadius}px`,
            fontFamily: STYLE_TOKENS.fonts.primary,
            fontSize: `${chipFontSize}px`,
            fontWeight: 500,
          }}
        >
          <span>
            {filterLabels[key] || key}: <strong>{value}</strong>
          </span>
          <button
            onClick={() => onClearFilter && onClearFilter(key)}
            style={{
              background: "none",
              border: "none",
              color: "inherit",
              cursor: "pointer",
              padding: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: `${closeFontSize}px`,
              lineHeight: 1,
              transition: STYLE_TOKENS.transition.normal,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.opacity = "0.7";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.opacity = "1";
            }}
            title={`Remove ${filterLabels[key] || key} filter`}
            aria-label={`Remove ${filterLabels[key] || key} filter`}
          >
            ✕
          </button>
        </div>
      ))}

      {/* Clear All Button */}
      {activeFilterEntries.length > 0 && (
        <button
          onClick={onClearAll}
          style={{
            background: "none",
            border: "none",
            color: STYLE_TOKENS.colors.primary,
            cursor: "pointer",
            padding: 0,
            fontFamily: STYLE_TOKENS.fonts.primary,
            fontSize: `${chipFontSize}px`,
            fontWeight: 500,
            textDecoration: "underline",
            transition: STYLE_TOKENS.transition.normal,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.opacity = "0.7";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.opacity = "1";
          }}
          title="Clear all filters"
          aria-label="Clear all filters"
        >
          Clear All
        </button>
      )}
    </div>
  );
};

export default FilterChips;
