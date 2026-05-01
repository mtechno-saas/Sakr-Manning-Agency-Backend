// src/components/common/Button.jsx
/*
 * Enhanced Button component with more customization options
 * Props:
 *  - children: button text or icon
 *  - onClick: click handler
 *  - variant: "primary" | "secondary" | "danger" | "success" | "ghost" | "outline"
 *  - size: "sm" | "md" | "lg" | "xl"
 *  - type: button type (default = "button")
 *  - fullWidth: make button stretch
 *  - disabled: disable button
 *  - loading: show loading state
 *  - icon: icon element to show
 *  - iconPosition: "left" | "right"
 *  - className: additional classes
 */

const variantClasses = {
  primary:
    "bg-[#0065AF] text-white hover:bg-[#2477C3] focus:ring-[#0065AF]/50 shadow-sm rounded-[24px]",
  secondary:
    "bg-[#DBE9F5] text-[#000000C4] hover:bg-[#AFD1EE] focus:ring-[#0065AF]/30",
  danger:
    "bg-red-500 text-white hover:bg-red-600 focus:ring-red-500/50 shadow-sm",

  success: `bg-white border border-green-700 text-green-700
   rounded-[30px] w-1/4 h-full py-2
   font-poppins font-medium text-[22px] leading-[33px]
   flex justify-center items-center gap-2
   hover:bg-green-700 hover:text-white
   `,
  ghost:
    "bg-transparent text-[#000000C4] hover:bg-[#DBE9F5] focus:ring-[#0065AF]/30",
  outlined:
    "bg-transparent border border-1 border-[#0065AF] text-[#0065AF] hover:bg-[#0065AF] hover:text-white rounded-[24px] ",
  navigation:
    "bg-[#1976D2] text-white hover:bg-[#2477C3] focus:ring-[#0065AF]/50 shadow-sm",
  back: `
   bg-white border border-[#0065AF] text-[#1976D2]
   rounded-[30px] w-1/5 h-full py-2
   font-poppins font-medium text-[22px] leading-[33px]
   flex justify-center items-center gap-2
   hover:bg-gray-50
  `,
  forward: `
   bg-[#0065AF] text-white
   rounded-[30px] w-1/5 h-full py-2
   font-poppins font-medium text-[22px] leading-[33px]
   flex justify-center items-center gap-2
  `,
};

export default function Button({
  children,
  onClick,
  variant = "primary",
  type = "button",
  fullWidth = false,
  disabled = false,
  loading = false,
  icon,
  iconPosition = "left",
  className = "",
  ...rest
}) {
  const baseClasses =
    "inline-flex items-center justify-center gap-2 font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed";

  const widthClass = fullWidth ? "w-full" : "";

  const finalClasses = `${baseClasses} ${variantClasses[variant]} ${widthClass} ${className}`;

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={finalClasses}
      {...rest}
    >
      {loading && (
        <svg
          className="animate-spin -ml-1 mr-2 h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          ></circle>
          <path
            className="opacity-75"
            fill="currentColor"
            d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
      )}
      {icon && iconPosition === "left" && !loading && (
        <span className="flex-shrink-0">{icon}</span>
      )}
      {children && <span>{children}</span>}
      {icon && iconPosition === "right" && !loading && (
        <span className="flex-shrink-0">{icon}</span>
      )}
    </button>
  );
}
