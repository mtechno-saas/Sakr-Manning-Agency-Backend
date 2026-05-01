// components/Common/Button.jsx
// Unified button component replacing all button variations across the app

import React from "react";
import { getButtonStyles } from "../../Styles/componentStyles";

/**
 * Button Component
 *
 * Replaces all button implementations across the dashboard
 * Handles scaling, variants, sizes, and states
 *
 * @param {string} variant - Button style variant: 'primary' | 'outline' | 'icon' | 'ghost' | 'danger'
 * @param {string} size - Button size: 'sm' | 'md' | 'lg' (default: 'md')
 * @param {boolean} disabled - Disabled state
 * @param {boolean} loading - Loading state
 * @param {number} scale - Scale factor (default: 1)
 * @param {function} onClick - Click handler
 * @param {ReactNode} children - Button content
 * @param {string} className - Additional CSS classes
 * @param {object} style - Additional inline styles
 * @param {string} title - Tooltip text
 * @param {string} ariaLabel - Accessibility label
 *
 * @example
 * // Primary button
 * <Button variant="primary" onClick={handleClick} scale={scale}>
 *   Add New
 * </Button>
 *
 * // Icon button with hover effect
 * <Button variant="icon" onClick={handleFilter} scale={scale} title="Filter">
 *   <FilterIcon />
 * </Button>
 *
 * // Outline button
 * <Button variant="outline" onClick={handleReset}>
 *   Reset
 * </Button>
 *
 * // Danger button for delete
 * <Button variant="danger" onClick={handleDelete} scale={scale}>
 *   Delete
 * </Button>
 */
const Button = React.forwardRef((props, ref) => {
  const {
    variant = "primary",
    size = "md",
    disabled = false,
    loading = false,
    scale = 1,
    onClick,
    children,
    className = "",
    style = {},
    title,
    ariaLabel,
    type = "button",
    ...rest
  } = props;

  // Get base styles for the variant
  const baseStyles = getButtonStyles(variant, scale);

  // Merge with additional styles
  const finalStyle = {
    ...baseStyles,
    ...style,
    opacity: disabled || loading ? 0.6 : 1,
    pointerEvents: disabled || loading ? "none" : "auto",
    cursor: disabled || loading ? "not-allowed" : "pointer",
  };

  // Handle click with loading/disabled state
  const handleClick = (e) => {
    if (!disabled && !loading && onClick) {
      onClick(e);
    }
  };

  // Build className
  const finalClassName = [
    "dashboard-button",
    `button-${variant}`,
    `button-${size}`,
    disabled && "button-disabled",
    loading && "button-loading",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button
      ref={ref}
      type={type}
      style={finalStyle}
      className={finalClassName}
      onClick={handleClick}
      disabled={disabled || loading}
      title={title}
      aria-label={ariaLabel}
      {...rest}
    >
      {loading ? <span style={{ opacity: 0.6 }}>Loading...</span> : children}
    </button>
  );
});

Button.displayName = "Button";

export default Button;
