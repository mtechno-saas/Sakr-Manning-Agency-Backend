// src/components/common/Card.jsx - RESPONSIVE VERSION

export default function Card({
  title,
  subtitle,
  text,
  icon,
  iconPosition = "top",
  image,
  imageAlt,
  actions,
  variant = "default",
  size = "md",
  clickable = false,
  onClick,
  className = "",
  children,
  ...rest
}) {
  const baseClasses = "transition-all duration-200";

  const sizeClasses = {
    sm: "p-3 md:p-4 gap-2 md:gap-3",
    md: "p-4 md:p-6 gap-3 md:gap-4",
    lg: "p-6 md:p-8 gap-4 md:gap-6",
  };

  const variantClasses = {
    default: "bg-[#DBE9F5] rounded-2xl shadow-sm hover:shadow-md",
    outlined:
      "bg-white border-2 border-[#B6B6B642] rounded-2xl hover:border-[#0065AF]/30",
    elevated: "bg-white rounded-2xl shadow-lg hover:shadow-xl",
    flat: "bg-transparent",
    values:
      "bg-transparent rounded-[22px] border border-[#0065AF] hover:shadow-md",
    contact: "bg-[rgba(36,119,195,0.1)] rounded-[22px] relative",
    team: "bg-white shadow-[0px_4px_4px_rgba(0,0,0,0.25)] rounded-[22px]",
    service:
      "border border-white rounded-[22px] cursor-pointer hover:bg-white/10 transition-colors",
    feature:
      "bg-white rounded-xl shadow-md border border-gray-100 hover:shadow-lg transition-shadow duration-300",
  };

  const clickableClasses = clickable
    ? "cursor-pointer hover:scale-[1.02] active:scale-[0.98]"
    : "";

  // For values variant, override the size classes
  const finalSizeClasses = variant === "values" ? "" : sizeClasses[size];

  const cardClasses = `${baseClasses} ${finalSizeClasses} ${variantClasses[variant]} ${clickableClasses} ${className}`;

  const handleClick = (e) => {
    if (clickable && onClick) {
      onClick(e);
    }
  };

  const renderContent = () => {
    if (children) return children;

    // Special layout for values variant - RESPONSIVE
    if (variant === "values") {
      return (
        <div className="flex flex-col sm:flex-row items-center gap-4 sm:gap-6 h-full p-4 sm:p-6">
          {/* Icon */}
          {icon && (
            <div className="flex-shrink-0">
              {typeof icon === "string" ? (
                <img
                  src={icon}
                  alt={`${title} icon`}
                  className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 object-contain"
                />
              ) : (
                <div className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 flex items-center justify-center">
                  {icon}
                </div>
              )}
            </div>
          )}

          {/* Content */}
          <div className="flex-1 min-w-0 space-y-2 text-center sm:text-left">
            {title && (
              <h3 className="text-base sm:text-lg md:text-xl lg:text-2xl font-bold text-[#000000C4]">
                {title}
              </h3>
            )}
            {text && (
              <p className="text-sm sm:text-base md:text-lg text-[#000000C4]/80 leading-relaxed">
                {text}
              </p>
            )}
          </div>
        </div>
      );
    }

    // Default content layout for other variants
    const iconElement = icon && (
      <div
        className={`flex-shrink-0 ${
          iconPosition === "top"
            ? "w-8 h-8 sm:w-10 sm:h-10 md:w-12 md:h-12"
            : "w-6 h-6 sm:w-8 sm:h-8 md:w-10 md:h-10"
        }`}
      >
        {typeof icon === "string" ? (
          <img
            src={icon}
            alt={`${title} icon`}
            className="w-full h-full object-contain"
          />
        ) : (
          icon
        )}
      </div>
    );

    const textContent = (
      <div className="flex-1 min-w-0">
        {title && (
          <h3
            className={`font-bold text-[#000000C4] ${
              size === "lg"
                ? "text-lg sm:text-xl md:text-2xl"
                : size === "sm"
                ? "text-sm sm:text-base"
                : "text-base sm:text-lg"
            }`}
          >
            {title}
          </h3>
        )}
        {subtitle && (
          <p
            className={`text-[#000000C4]/70 font-medium ${
              size === "lg" ? "text-sm sm:text-base" : "text-xs sm:text-sm"
            }`}
          >
            {subtitle}
          </p>
        )}
        {text && (
          <p
            className={`text-[#000000C4]/80 leading-relaxed ${
              size === "lg" ? "text-sm sm:text-base" : "text-xs sm:text-sm"
            }`}
          >
            {text}
          </p>
        )}
      </div>
    );

    if (iconPosition === "left" || iconPosition === "right") {
      return (
        <div
          className={`flex items-start gap-3 sm:gap-4 ${
            iconPosition === "right" ? "flex-row-reverse" : ""
          }`}
        >
          {iconElement}
          {textContent}
        </div>
      );
    }

    return (
      <>
        {iconElement}
        {textContent}
      </>
    );
  };

  return (
    <div
      className={`${
        variant === "values" ? "flex" : "flex flex-col"
      } ${cardClasses}`}
      onClick={handleClick}
      {...rest}
    >
      {image && (
        <div className="w-full h-32 sm:h-40 md:h-48 mb-4 -m-2 rounded-xl overflow-hidden">
          <img
            src={image}
            alt={imageAlt || "Card image"}
            className="w-full h-full object-cover"
          />
        </div>
      )}

      {renderContent()}

      {actions && variant !== "values" && (
        <div className="flex flex-wrap items-center gap-2 mt-auto pt-2">
          {actions}
        </div>
      )}
    </div>
  );
}
