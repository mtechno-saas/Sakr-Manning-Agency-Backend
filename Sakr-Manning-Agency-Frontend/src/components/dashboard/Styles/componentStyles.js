// styles/componentStyles.js
// Pre-calculated style objects for common components

import STYLE_TOKENS, {
  getScaledValue,
  getButtonBaseStyles,
  getInputBaseStyles,
  getModalOverlayStyles,
  getModalPanelStyles,
} from "./globalStyles";

// ============================================
// BUTTON STYLES
// ============================================

export const getButtonStyles = (variant = "primary", scale = 1) => {
  const base = getButtonBaseStyles(scale);

  const variants = {
    primary: {
      ...base,
      backgroundColor: STYLE_TOKENS.colors.primary,
      color: STYLE_TOKENS.colors.white,
      ":hover": {
        backgroundColor: "#1565C0",
      },
    },
    outline: {
      ...base,
      backgroundColor: STYLE_TOKENS.colors.white,
      color: STYLE_TOKENS.colors.primary,
      border: `1px solid ${STYLE_TOKENS.colors.primary}`,
      ":hover": {
        backgroundColor: STYLE_TOKENS.colors.hoverBackground,
      },
    },
    icon: {
      width: `${getScaledValue(32, scale)}px`,
      height: `${getScaledValue(32, scale)}px`,
      borderRadius: `${getScaledValue(12, scale)}px`,
      backgroundColor: "#F5F7FA",
      border: "none",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      transition: STYLE_TOKENS.transition.normal,
      cursor: "pointer",
      padding: 0,
      ":hover": {
        backgroundColor: STYLE_TOKENS.colors.hoverLight,
      },
    },
    ghost: {
      ...base,
      backgroundColor: "transparent",
      color: STYLE_TOKENS.colors.primary,
      border: "none",
      padding: `${getScaledValue(8, scale)}px ${getScaledValue(12, scale)}px`,
      ":hover": {
        backgroundColor: "rgba(0, 101, 175, 0.1)",
      },
    },
    danger: {
      ...base,
      backgroundColor: "#FFE6E6",
      color: "#D32F2F",
      border: "none",
      padding: `${getScaledValue(6, scale)}px ${getScaledValue(12, scale)}px`,
      minHeight: `${getScaledValue(32, scale)}px`,
      fontSize: `${getScaledValue(13, scale)}px`,
      ":hover": {
        backgroundColor: "#FFCCCC",
      },
    },
  };

  return variants[variant] || variants.primary;
};

// ============================================
// MODAL STYLES
// ============================================

export const getModalStyles = (scale = 1) => ({
  overlay: getModalOverlayStyles(),
  panel: getModalPanelStyles(scale),

});

// ============================================
// FILTER MODAL STYLES
// ============================================

export const getFilterModalStyles = (scale = 1) => {
  return {
    overlay: {
      ...getModalOverlayStyles(),
    },
    panel: {
      ...getModalPanelStyles(scale),
    },
    title: {
      fontSize: `${getScaledValue(STYLE_TOKENS.fontSize.lg, scale)}px`,
      fontWeight: 500,
      color: STYLE_TOKENS.colors.darkText,
      margin: `0 0 ${getScaledValue(20, scale)}px 0`,
      fontFamily: STYLE_TOKENS.fonts.heading,
    },
    field: {
      marginBottom: `${getScaledValue(20, scale)}px`,
    },
    label: {
      display: "block",
      fontSize: `${getScaledValue(STYLE_TOKENS.fontSize.sm, scale)}px`,
      fontWeight: 500,
      color: STYLE_TOKENS.colors.darkText,
      marginBottom: `${getScaledValue(8, scale)}px`,
      fontFamily: STYLE_TOKENS.fonts.heading,
    },
    input: getInputBaseStyles(scale),
    buttonRow: {
      display: "flex",
      gap: `${getScaledValue(12, scale)}px`,
      justifyContent: "flex-end",
      marginTop: `${getScaledValue(24, scale)}px`,
    },
  };
};

// ============================================
// FORM FIELD STYLES
// ============================================

export const getFormFieldStyles = (scale = 1) => ({
  wrapper: {
    display: "flex",
    flexDirection: "column",
    gap: `${getScaledValue(8, scale)}px`,
    marginBottom: `${getScaledValue(20, scale)}px`,
  },
  label: {
    display: "block",
    fontSize: `${getScaledValue(STYLE_TOKENS.fontSize.sm, scale)}px`,
    fontWeight: 500,
    color: STYLE_TOKENS.colors.darkText,
    fontFamily: STYLE_TOKENS.fonts.heading,
  },
  input: {
    ...getInputBaseStyles(scale),
  },
  error: {
    fontSize: `${getScaledValue(12, scale)}px`,
    color: STYLE_TOKENS.colors.rejected,
    fontFamily: STYLE_TOKENS.fonts.primary,
  },
});

// ============================================
// STATUS BADGE STYLES
// ============================================

export const getStatusBadgeStyles = (scale = 1) => ({
  wrapper: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: `${getScaledValue(4, scale)}px ${getScaledValue(12, scale)}px`,
    borderRadius: `${getScaledValue(STYLE_TOKENS.borderRadius.pill, scale)}px`,
    fontFamily: STYLE_TOKENS.fonts.heading,
    fontWeight: 500,
    fontSize: `${getScaledValue(STYLE_TOKENS.fontSize.xs, scale)}px`,
  },
});

export const STATUS_COLORS = {
  // ── CV Submission pipeline ────────────────────────────────────────────
  Pending: {
    bg: "rgba(164, 164, 164, 0.2)",
    color: "#555555",
  },
  "Under Review": {
    bg: "rgba(245, 158, 11, 0.15)",
    color: "#B45309",
  },
  Interviewed: {
    bg: "rgba(139, 92, 246, 0.15)",
    color: "#6D28D9",
  },
  Shortlisted: {
    bg: "rgba(59, 130, 246, 0.15)",
    color: "#1D4ED8",
  },
  Approved: {
    bg: "rgba(0, 101, 175, 0.15)",
    color: "#0065AF",
  },
  Hired: {
    bg: "rgba(21, 171, 16, 0.12)",
    color: "#15AB10",
  },
  Rejected: {
    bg: "rgba(178, 17, 1, 0.12)",
    color: "#B21101",
  },
  // ── Document / General statuses ───────────────────────────────────────
  Active: {
    bg: "rgba(21, 171, 16, 0.1)",
    color: "#15AB10",
  },
  Blacklist: {
    bg: "rgba(178, 17, 1, 0.12)",
    color: "#B21101",
  },
  INACTIVE: {
    bg: "rgba(178, 17, 1, 0.1)",
    color: "#B21101",
  },
};


// ============================================
// ICON BUTTON STYLES (CSS-in-JS for inline use)
// ============================================

export const iconButtonStyles = (scale = 1) => `
  .icon-btn {
    width: ${getScaledValue(32, scale)}px;
    height: ${getScaledValue(32, scale)}px;
    border-radius: ${getScaledValue(12, scale)}px;
    background: #F5F7FA;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.18s;
    cursor: pointer;
  }
  .icon-btn:hover {
    background: ${STYLE_TOKENS.colors.hoverLight};
  }
`;

// ============================================
// PRIMARY BUTTON STYLES (CSS-in-JS for inline use)
// ============================================

export const primaryButtonStyles = (scale = 1) => `
  .primary-btn {
    padding: ${getScaledValue(6, scale)}px ${getScaledValue(16, scale)}px;
    height: ${getScaledValue(36, scale)}px;
    background: ${STYLE_TOKENS.colors.primary};
    color: ${STYLE_TOKENS.colors.white};
    border-radius: 22px;
    border: none;
    font-weight: 500;
    cursor: pointer;
    font-family: ${STYLE_TOKENS.fonts.heading};
    font-size: ${getScaledValue(STYLE_TOKENS.fontSize.md, scale)}px;
    transition: ${STYLE_TOKENS.transition.normal};
    min-width: ${getScaledValue(80, scale)}px;
    min-height: ${getScaledValue(36, scale)}px;
  }
  .primary-btn:hover {
    background: #1565C0;
  }
`;

// ============================================
// OUTLINE BUTTON STYLES (CSS-in-JS for inline use)
// ============================================

export const outlineButtonStyles = (scale = 1) => `
  .outline-btn {
    padding: ${getScaledValue(6, scale)}px ${getScaledValue(16, scale)}px;
    height: ${getScaledValue(36, scale)}px;
    background: ${STYLE_TOKENS.colors.white};
    color: ${STYLE_TOKENS.colors.primary};
    border-radius: 22px;
    border: 1px solid ${STYLE_TOKENS.colors.primary};
    font-weight: 400;
    font-family: ${STYLE_TOKENS.fonts.heading};
    cursor: pointer;
    font-size: ${getScaledValue(STYLE_TOKENS.fontSize.md, scale)}px;
    transition: ${STYLE_TOKENS.transition.normal};
    min-width: ${getScaledValue(140, scale)}px;
    min-height: ${getScaledValue(36, scale)}px;
  }
  .outline-btn:hover {
    background: ${STYLE_TOKENS.colors.hoverBackground};
  }
`;

// ============================================
// ACTION BUTTON STYLES (CSS-in-JS for inline use)
// ============================================

export const actionButtonStyles = (scale = 1) => `
  .action-btn {
    width: ${getScaledValue(60, scale)}px;
    height: ${getScaledValue(36, scale)}px;
    padding: ${getScaledValue(6, scale)}px ${getScaledValue(16, scale)}px;
    border-radius: 22px;
    border: none;
    cursor: pointer;
    font-family: ${STYLE_TOKENS.fonts.heading};
    font-weight: 400;
    font-size: ${getScaledValue(STYLE_TOKENS.fontSize.md, scale)}px;
    background: ${STYLE_TOKENS.colors.primary};
    color: ${STYLE_TOKENS.colors.white};
    transition: ${STYLE_TOKENS.transition.normal};
    min-width: ${getScaledValue(67, scale)}px;
  }
  .action-btn:hover {
    background: #1565C0;
  }
`;

// ============================================
// DELETE BUTTON STYLES (CSS-in-JS for inline use)
// ============================================

export const deleteButtonStyles = (scale = 1) => `
  .btn-delete {
    padding: ${getScaledValue(6, scale)}px ${getScaledValue(12, scale)}px;
    height: ${getScaledValue(32, scale)}px;
    background: #FFE6E6;
    color: #D32F2F;
    border: none;
    border-radius: ${getScaledValue(8, scale)}px;
    cursor: pointer;
    font-family: ${STYLE_TOKENS.fonts.heading};
    font-size: ${getScaledValue(13, scale)}px;
    font-weight: 500;
    transition: ${STYLE_TOKENS.transition.normal};
  }
  .btn-delete:hover {
    background: #FFCCCC;
  }
`;

// ============================================
// MAIN STYLE GENERATOR - All CSS in one place
// ============================================

export const generatePageStyles = (scale = 1) => `
  ${iconButtonStyles(scale)}
  ${primaryButtonStyles(scale)}
  ${outlineButtonStyles(scale)}
  ${actionButtonStyles(scale)}
  ${deleteButtonStyles(scale)}
  
  .filter-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  .filter-panel {
    background: ${STYLE_TOKENS.colors.white};
    border-radius: ${getScaledValue(22, scale)}px;
    padding: ${getScaledValue(24, scale)}px;
    box-shadow: ${STYLE_TOKENS.shadow.lg};
    max-width: 400px;
    width: 90%;
  }
`;

export default {
  getButtonStyles,
  getModalStyles,
  getFilterModalStyles,
  getFormFieldStyles,
  getStatusBadgeStyles,
  STATUS_COLORS,
  generatePageStyles,
};
