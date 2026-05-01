// styles/globalStyles.js
// Centralized styling tokens and utilities

export const STYLE_TOKENS = {
  // Color Palette
  colors: {
    primary: "#0065AF",
    primaryLight: "#25548E",
    secondary: "#1976D2",
    background: "#F9FAFB",
    white: "#FFFFFF",
    darkText: "#000000",
    lightText: "#8C8C8C",
    borderColor: "#E5E7EB",
    cardBg: "#DBEAF7",
    iconGray: "#464242",
    statusGray: "#706F6C",
    rejected: "#B21101",
    accepted: "#15AB10",
    interview: "#7D6335",
    pending: "#0065AF",
    hoverLight: "#E8ECEF",
    hoverBackground: "#F0F7FF",
    dividerColor: "#E5E7EB",
  },

  // Border Radius
  borderRadius: {
    sm: 8,
    md: 16,
    lg: 22,
    pill: 100,
  },

  // Shadows
  shadow: {
    xs: "0px 0px 7.4px rgba(164, 164, 164, 0.2)",
    sm: "0px 1px 2px rgba(0, 0, 0, 0.04)",
    md: "0px 2px 10px rgba(0, 0, 0, 0.15)",
    lg: "0px 8px 24px rgba(69, 69, 80, 0.1)",
  },

  // Spacing
  spacing: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 24,
    xxl: 32,
  },

  // Font Sizes
  fontSize: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20,
    xxl: 24,
  },

  // Fonts
  fonts: {
    primary: "Inter, sans-serif",
    heading: "Poppins, sans-serif",
  },

  // Transitions
  transition: {
    fast: "all 0.15s ease",
    normal: "all 0.2s ease",
    slow: "all 0.3s ease",
  },
};

// Helper to get scaled value
export const getScaledValue = (baseValue, scale = 1) => {
  return Math.round(baseValue * scale);
};

// Helper to generate button base styles
export const getButtonBaseStyles = (scale = 1) => ({
  fontFamily: STYLE_TOKENS.fonts.heading,
  fontWeight: 500,
  fontSize: `${getScaledValue(16, scale)}px`,
  border: "none",
  borderRadius: `${getScaledValue(22, scale)}px`,
  cursor: "pointer",
  transition: STYLE_TOKENS.transition.normal,
  minHeight: `${getScaledValue(40, scale)}px`,
  padding: `${getScaledValue(8, scale)}px ${getScaledValue(19, scale)}px`,
});

// Helper to generate input/select base styles
export const getInputBaseStyles = (scale = 1) => ({
  fontFamily: STYLE_TOKENS.fonts.primary,
  fontSize: `${getScaledValue(14, scale)}px`,
  padding: `${getScaledValue(10, scale)}px`,
  borderRadius: `${getScaledValue(8, scale)}px`,
  border: `1px solid ${STYLE_TOKENS.colors.borderColor}`,
  backgroundColor: STYLE_TOKENS.colors.white,
  color: STYLE_TOKENS.colors.darkText,
  cursor: "pointer",
  width: "100%",
  boxSizing: "border-box",
});

// Helper to generate modal overlay styles
export const getModalOverlayStyles = () => ({
  position: "fixed",
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: "rgba(0,0,0,0.5)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  zIndex: 1000,
});

// Helper to generate modal panel styles
export const getModalPanelStyles = (scale = 1) => ({
  backgroundColor: STYLE_TOKENS.colors.white,
  borderRadius: `${getScaledValue(22, scale)}px`,
  padding: `${getScaledValue(24, scale)}px`,
  paddingBottom: `${getScaledValue(24, scale)}px !important`,
  boxShadow: STYLE_TOKENS.shadow.lg,
  maxWidth: "400px",
  width: "90%",
  maxHeight: "90vh",
  overflowY: "none !important",
});

// Helper for hover state styling
export const getHoverStyles = (baseColor, hoverColor) => ({
  transition: STYLE_TOKENS.transition.normal,
  ":hover": {
    backgroundColor: hoverColor,
  },
});

// Export all tokens for direct use
export default STYLE_TOKENS;
