// components/ui/Button.jsx
import React, { forwardRef } from "react";
import { BUTTON_VARIANTS } from "../../utils/constants";

const Button = forwardRef(
  (
    {
      children,
      onClick,
      disabled = false,
      loading = false,
      variant = BUTTON_VARIANTS.PRIMARY,
      size = "md",
      type = "button",
      className = "",
      leftIcon: LeftIcon,
      rightIcon: RightIcon,
      fullWidth = false,
      small = false,
      "aria-label": ariaLabel,
      ...props
    },
    ref
  ) => {
    // Base classes
    const baseClasses = `
    inline-flex items-center justify-center
    font-medium rounded-full
    transition-all duration-200 ease-in-out
    focus:outline-none focus:ring-2 focus:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed
    relative overflow-hidden
  `;

    // Size variants
    const sizeClasses = {
      sm: "px-3 py-2 text-sm",
      md: "px-4 py-3 text-base",
      lg: "px-6 py-4 text-lg",
      xl: "px-8 py-5 text-xl",
    };

    // Color variants
    const variantClasses = {
      [BUTTON_VARIANTS.PRIMARY]: `
     
    `,
      [BUTTON_VARIANTS.SECONDARY]: `
      bg-white text-gray-700 border border-gray-300
      hover:bg-gray-50 hover:border-gray-400
      focus:ring-gray-500
      active:bg-gray-100
      shadow-sm hover:shadow-md
    `,
      [BUTTON_VARIANTS.DANGER]: `
      bg-red-600 text-white border border-red-600
      hover:bg-red-700 hover:border-red-700
      focus:ring-red-500
      active:bg-red-800
      shadow-sm hover:shadow-md
    `,
      [BUTTON_VARIANTS.SUCCESS]: `
      bg-green-600 text-white border border-green-600
      hover:bg-green-700 hover:border-green-700
      focus:ring-green-500
      active:bg-green-800
      shadow-sm hover:shadow-md
    `,
      [BUTTON_VARIANTS.GHOST]: `
      bg-transparent text-gray-600 border border-transparent
      hover:bg-gray-100 hover:text-gray-900
      focus:ring-gray-500
      active:bg-gray-200
    `,
    };

    // Width classes
    const widthClasses = fullWidth ? "w-full" : "";

    // Loading spinner component
    const LoadingSpinner = () => (
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="animate-spin rounded-full h-5 w-5 border-2 border-current border-t-transparent" />
      </div>
    );

    // Ripple effect (optional enhancement)
    const handleClick = (e) => {
      if (disabled || loading) return;

      // Create ripple effect
      const button = e.currentTarget;
      const rect = button.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = e.clientX - rect.left - size / 2;
      const y = e.clientY - rect.top - size / 2;

      const ripple = document.createElement("span");
      ripple.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      left: ${x}px;
      top: ${y}px;
      background: rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      transform: scale(0);
      animation: ripple 0.6s linear;
      pointer-events: none;
    `;

      button.appendChild(ripple);

      // Remove ripple after animation
      setTimeout(() => {
        ripple.remove();
      }, 600);

      // Call the actual onClick handler
      onClick?.(e);
    };

    const activeSize = small ? "sm" : size;

    const combinedClasses = `
    ${baseClasses}
    ${sizeClasses[activeSize]}
    ${variantClasses[variant]}
    ${widthClasses}
    ${className}
  `
      .trim()
      .replace(/\s+/g, " ");

    return (
      <>
        {/* Add ripple animation CSS */}
        <style>{`
          @keyframes ripple {
            to {
              transform: scale(4);
              opacity: 0;
            }
          }
        `}</style>

        <button
          ref={ref}
          type={type}
          onClick={handleClick}
          disabled={disabled || loading}
          className={combinedClasses}
          aria-label={ariaLabel}
          aria-busy={loading}
          {...props}
        >
          {/* Loading State */}
          {loading && <LoadingSpinner />}

          {/* Content Container */}
          <span
            className={`flex items-center justify-center gap-2 ${
              loading ? "opacity-0" : "opacity-100"
            }`}
          >
            {/* Left Icon */}
            {LeftIcon && !loading && (
              <LeftIcon
                className={`${
                  size === "sm"
                    ? "h-4 w-4"
                    : size === "md"
                    ? "h-5 w-5"
                    : size === "lg"
                    ? "h-6 w-6"
                    : "h-7 w-7"
                }`}
              />
            )}

            {/* Button Text */}
            {children}

            {/* Right Icon */}
            {RightIcon && !loading && (
              <RightIcon
                className={`${
                  size === "sm"
                    ? "h-4 w-4"
                    : size === "md"
                    ? "h-5 w-5"
                    : size === "lg"
                    ? "h-6 w-6"
                    : "h-7 w-7"
                }`}
              />
            )}
          </span>
        </button>
      </>
    );
  }
);

Button.displayName = "Button";

export default Button;
