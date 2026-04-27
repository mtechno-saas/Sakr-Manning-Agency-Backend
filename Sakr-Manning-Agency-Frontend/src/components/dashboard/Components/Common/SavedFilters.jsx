// components/Common/SavedFilters.jsx
// Quick access buttons for saved filter presets
// Users can save common filter combinations and reapply with one click

import React, { useState } from "react";
import { Save, Trash2 } from "lucide-react";
import { STYLE_TOKENS, getScaledValue } from "../../Styles/globalStyles";
import Button from "./Button";

/**
 * SavedFilters Component
 *
 * Displays saved filter presets and allows:
 * - Click to apply saved filter
 * - Save current filters
 * - Delete saved filters
 *
 * @param {array} savedPresets - Saved filter presets: [{ name, filters }]
 * @param {object} currentFilters - Current active filters
 * @param {function} onApplyPreset - Apply a saved preset
 * @param {function} onSavePreset - Save current filters as preset
 * @param {function} onDeletePreset - Delete a saved preset
 * @param {number} scale - Scale factor
 *
 * @example
 * <SavedFilters
 *   savedPresets={[
 *     { name: 'Active Only', filters: { status: 'Active' } }
 *   ]}
 *   currentFilters={filters}
 *   onApplyPreset={handleApplyPreset}
 *   onSavePreset={handleSavePreset}
 *   onDeletePreset={handleDeletePreset}
 *   scale={scale}
 * />
 */
const SavedFilters = ({
  savedPresets = [],
  currentFilters = {},
  onApplyPreset,
  onSavePreset,
  onDeletePreset,
  scale = 1,
}) => {
  const [presetName, setPresetName] = useState("");
  const [showSaveInput, setShowSaveInput] = useState(false);

  // Check if current filters are empty
  const hasActiveFilters = Object.values(currentFilters).some(
    (val) => val && val !== "" && (!Array.isArray(val) || val.length > 0)
  );

  // Handle save preset
  const handleSaveClick = () => {
    if (presetName.trim()) {
      onSavePreset(presetName, currentFilters);
      setPresetName("");
      setShowSaveInput(false);
    }
  };

  // Calculate sizes
  const padding = getScaledValue(8, scale);
  const gap = getScaledValue(8, scale);
  const fontSize = getScaledValue(13, scale);
  const borderRadius = getScaledValue(16, scale);

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: `${gap}px`,
        flexWrap: "wrap",
        paddingBottom: `${getScaledValue(12, scale)}px`,
        borderBottom: `1px solid ${STYLE_TOKENS.colors.borderColor}`,
      }}
    >
      {/* Label */}
      <span
        style={{
          fontSize: `${fontSize}px`,
          fontWeight: 500,
          color: STYLE_TOKENS.colors.lightText,
          fontFamily: STYLE_TOKENS.fonts.primary,
        }}
      >
        Quick Filters:
      </span>

      {/* Saved Preset Buttons */}
      {savedPresets.map((preset) => (
        <div
          key={preset.name}
          style={{
            display: "flex",
            alignItems: "center",
            gap: `${getScaledValue(4, scale)}px`,
            backgroundColor: "rgba(0, 101, 175, 0.1)",
            border: `1px solid rgba(0, 101, 175, 0.2)`,
            borderRadius: `${borderRadius}px`,
            padding: `${padding}px ${getScaledValue(12, scale)}px`,
          }}
        >
          <button
            onClick={() => onApplyPreset(preset.filters)}
            style={{
              background: "none",
              border: "none",
              color: STYLE_TOKENS.colors.primary,
              cursor: "pointer",
              fontSize: `${fontSize}px`,
              fontWeight: 500,
              padding: 0,
              transition: STYLE_TOKENS.transition.normal,
              fontFamily: STYLE_TOKENS.fonts.primary,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.textDecoration = "underline";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.textDecoration = "none";
            }}
            title={`Apply ${preset.name} filter`}
          >
            {preset.name}
          </button>

          {/* Delete button */}
          <button
            onClick={() => onDeletePreset(preset.name)}
            style={{
              background: "none",
              border: "none",
              color: STYLE_TOKENS.colors.rejected,
              cursor: "pointer",
              padding: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transition: STYLE_TOKENS.transition.normal,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.opacity = "0.7";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.opacity = "1";
            }}
            title={`Delete ${preset.name} filter`}
            aria-label={`Delete ${preset.name} filter`}
          >
            <Trash2 size={getScaledValue(14, scale)} strokeWidth={2} />
          </button>
        </div>
      ))}

      {/* Save Current Filter */}
      {showSaveInput ? (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: `${gap}px`,
          }}
        >
          <input
            type="text"
            value={presetName}
            onChange={(e) => setPresetName(e.target.value)}
            placeholder="Preset name..."
            autoFocus
            onKeyPress={(e) => {
              if (e.key === "Enter") {
                handleSaveClick();
              }
            }}
            style={{
              padding: `${padding}px ${getScaledValue(8, scale)}px`,
              borderRadius: `${borderRadius}px`,
              border: `1px solid ${STYLE_TOKENS.colors.primary}`,
              fontSize: `${fontSize}px`,
              fontFamily: STYLE_TOKENS.fonts.primary,
              minWidth: `${getScaledValue(120, scale)}px`,
            }}
          />
          <Button
            variant="primary"
            onClick={handleSaveClick}
            scale={scale}
            style={{ minWidth: `${getScaledValue(60, scale)}px` }}
          >
            Save
          </Button>
          <Button
            variant="outline"
            onClick={() => {
              setShowSaveInput(false);
              setPresetName("");
            }}
            scale={scale}
            style={{ minWidth: `${getScaledValue(60, scale)}px` }}
          >
            Cancel
          </Button>
        </div>
      ) : (
        <button
          onClick={() => setShowSaveInput(true)}
          disabled={!hasActiveFilters}
          style={{
            display: "flex",
            alignItems: "center",
            gap: `${getScaledValue(4, scale)}px`,
            padding: `${padding}px ${getScaledValue(12, scale)}px`,
            backgroundColor: hasActiveFilters
              ? STYLE_TOKENS.colors.primary
              : STYLE_TOKENS.colors.borderColor,
            color: STYLE_TOKENS.colors.white,
            border: "none",
            borderRadius: `${borderRadius}px`,
            cursor: hasActiveFilters ? "pointer" : "not-allowed",
            fontSize: `${fontSize}px`,
            fontWeight: 500,
            transition: STYLE_TOKENS.transition.normal,
            fontFamily: STYLE_TOKENS.fonts.primary,
            opacity: hasActiveFilters ? 1 : 0.5,
          }}
          onMouseEnter={(e) => {
            if (hasActiveFilters) {
              e.currentTarget.style.backgroundColor = "#1565C0";
            }
          }}
          onMouseLeave={(e) => {
            if (hasActiveFilters) {
              e.currentTarget.style.backgroundColor =
                STYLE_TOKENS.colors.primary;
            }
          }}
          title={
            hasActiveFilters
              ? "Save current filters"
              : "No active filters to save"
          }
        >
          <Save size={getScaledValue(14, scale)} strokeWidth={2} />
          <span>Save Filter</span>
        </button>
      )}
    </div>
  );
};

export default SavedFilters;
