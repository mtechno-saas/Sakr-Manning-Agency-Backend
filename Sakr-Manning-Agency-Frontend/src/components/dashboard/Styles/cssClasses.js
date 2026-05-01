// styles/cssClasses.js
// CSS-in-JS classes for common patterns used across pages

import STYLE_TOKENS, { getScaledValue } from "./globalStyles";
import {
  generatePageStyles,
  STATUS_COLORS,
  primaryButtonStyles,
  outlineButtonStyles,
  iconButtonStyles,
  actionButtonStyles,
  deleteButtonStyles,
} from "./componentStyles";

/**
 * Generate all CSS classes for a page with given scale
 * Usage in pages:
 *   <style>{pageStyles}</style>
 *   where pageStyles = generateAllPageStyles(scale)
 */
export const generateAllPageStyles = (scale = 1) => `
  ${generatePageStyles(scale)}
  
  /* Media queries for responsive design */
  @media (max-width: 1024px) {
    .form-field {
      flex-direction: column;
      align-items: stretch;
    }
    
    .form-label {
      min-width: auto;
      padding-top: 0;
    }
    
    .form-input {
      max-width: 100%;
    }
    
    .record-item {
      grid-template-columns: 1fr;
    }
    
    .form-buttons-row {
      position: relative;
      bottom: auto;
      right: auto;
      justify-content: flex-start;
      margin-top: ${getScaledValue(20, scale)}px;
    }
  }

  /* Hide scrollbars while maintaining scroll functionality */
  .hide-scrollbar {
    scrollbar-width: none;
    -ms-overflow-style: none;
  }
  
  .hide-scrollbar::-webkit-scrollbar {
    display: none;
  }

  /* Smooth scroll behavior */
  .smooth-scroll {
    scroll-behavior: smooth;
  }

  /* Flex utility classes */
  .flex-center {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .flex-between {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  /* Text truncation */
  .truncate {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .truncate-lines-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
`;

/**
 * Get inline styles for commonly used elements
 * More maintainable than hardcoding styles in JSX
 */

// Header/Page title
export const getPageTitleStyles = (scale = 1) => ({
  fontSize: `${getScaledValue(22, scale)}px`,
  fontWeight: 500,
  color: STYLE_TOKENS.colors.darkText,
  margin: 0,
  fontFamily: STYLE_TOKENS.fonts.heading,
  lineHeight: `${getScaledValue(24, scale)}px`,
});

// Section title
export const getSectionTitleStyles = (scale = 1) => ({
  fontSize: `${getScaledValue(20, scale)}px`,
  fontWeight: 500,
  color: STYLE_TOKENS.colors.darkText,
  margin: `0 0 ${getScaledValue(20, scale)}px 0`,
  fontFamily: STYLE_TOKENS.fonts.heading,
  lineHeight: `${getScaledValue(28, scale)}px`,
});

// Subtitle/description
export const getSubtitleStyles = (scale = 1) => ({
  fontSize: `${getScaledValue(16, scale)}px`,
  fontWeight: 400,
  color: STYLE_TOKENS.colors.lightText,
  fontFamily: STYLE_TOKENS.fonts.primary,
  lineHeight: `${getScaledValue(24, scale)}px`,
});

// Main container/section
export const getMainContainerStyles = (scale = 1, headerHeight = 101) => ({
  padding: `${getScaledValue(32, scale)}px`,
  paddingTop: `calc(${getScaledValue(headerHeight, scale)}px + ${getScaledValue(
    32,
    scale
  )}px)`,
  overflow: "auto",
  flex: 1,
  backgroundColor: STYLE_TOKENS.colors.background,
});

// Card/container with shadow
export const getCardStyles = (scale = 1) => ({
  backgroundColor: STYLE_TOKENS.colors.white,
  borderRadius: `${getScaledValue(22, scale)}px`,
  padding: `${getScaledValue(24, scale)}px`,
  boxShadow: STYLE_TOKENS.shadow.sm,
  minHeight: `${getScaledValue(200, scale)}px`,
});

// Row layout with space between
export const getRowBetweenStyles = (scale = 1) => ({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: `${getScaledValue(20, scale)}px`,
  gap: `${getScaledValue(12, scale)}px`,
});

// Horizontal group of buttons/items
export const getButtonGroupStyles = (scale = 1) => ({
  display: "flex",
  justifyContent: "flex-end",
  gap: `${getScaledValue(12, scale)}px`,
  marginTop: `${getScaledValue(20, scale)}px`,
});

// Modal title
export const getModalTitleStyles = (scale = 1) => ({
  fontSize: `${getScaledValue(20, scale)}px`,
  fontWeight: 500,
  color: STYLE_TOKENS.colors.darkText,
  margin: `0 0 ${getScaledValue(20, scale)}px 0`,
  fontFamily: STYLE_TOKENS.fonts.heading,
});

// Disabled state overlay
export const getDisabledOverlayStyles = () => ({
  opacity: 0.5,
  pointerEvents: "none",
});

/**
 * Helper to get flex layout styles
 */
export const getFlexLayoutStyles = (
  direction = "row",
  gap = 12,
  scale = 1,
  alignItems = "center"
) => ({
  display: "flex",
  flexDirection: direction,
  gap: `${getScaledValue(gap, scale)}px`,
  alignItems,
});

/**
 * Helper for grid layout (for records/tables)
 */
export const getGridLayoutStyles = (columns = 1, gap = 16, scale = 1) => ({
  display: "grid",
  gridTemplateColumns: `repeat(${columns}, 1fr)`,
  gap: `${getScaledValue(gap, scale)}px`,
});

/**
 * Export all helper functions
 */
export default {
  generateAllPageStyles,
  getPageTitleStyles,
  getSectionTitleStyles,
  getSubtitleStyles,
  getMainContainerStyles,
  getCardStyles,
  getRowBetweenStyles,
  getButtonGroupStyles,
  getModalTitleStyles,
  getDisabledOverlayStyles,
  getFlexLayoutStyles,
  getGridLayoutStyles,
  STATUS_COLORS,
};
