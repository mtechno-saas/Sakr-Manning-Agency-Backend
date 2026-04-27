// src/components/common/Section.jsx - RESPONSIVE VERSION
// eslint-disable-next-line no-unused-vars
import { motion } from "framer-motion";

export default function Section({
  title,
  subtitle,
  description,
  children,
  layout = "default",
  reverse = false,
  background = "default",
  backgroundImage,
  padding = "lg",
  margin = "lg",
  maxWidth = "full",
  textAlign = "left",
  headerActions,
  className = "",
  ...rest
}) {
  const paddingClasses = {
    none: "",
    sm: "py-8 px-4",
    md: "py-12 px-4 sm:px-6",
    lg: "py-16 px-4 sm:px-6 lg:px-8 2xl:px-12",
    xl: "py-24 px-4 sm:px-6 lg:px-12 2xl:px-16",
  };

  const marginClasses = {
    none: "",
    sm: "my-8",
    md: "my-12",
    lg: "my-16",
    xl: "my-24",
  };

  const maxWidthClasses = {
    sm: "max-w-2xl mx-auto",
    md: "max-w-4xl mx-auto",
    lg: "max-w-6xl 2xl:max-w-7xl mx-auto",
    xl: "max-w-7xl 2xl:max-w-[1400px] mx-auto",
    "2xl": "max-w-screen-2xl mx-auto",
    "9xl": "max-w-[1440px] 2xl:max-w-[1600px] mx-auto", // Match design base with scaling
    full: "w-full", // Full width with padding from paddingClasses
  };

  const backgroundClasses = {
    default: "",
    gray: "bg-gray-50",
    blue: "bg-[#DBE9F5]",
    gradient: "bg-gradient-to-br from-[#DBE9F5] to-[#AFD1EE]",
    image: backgroundImage ? `bg-cover bg-center bg-no-repeat` : "",
    none: "",
  };

  const textAlignClasses = {
    left: "text-left",
    center: "text-center",
    right: "text-right",
  };

  const layoutClasses = {
    default: "flex flex-col gap-6 md:gap-8",
    centered:
      "flex flex-col items-center justify-center gap-1 text-center w-full",
    split: `flex flex-col ${reverse ? "lg:flex-row-reverse" : "lg:flex-row"
      } gap-6 md:gap-8 lg:gap-12 items-center`,
    grid: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8",
    masonry:
      "columns-1 md:columns-2 lg:columns-3 gap-6 md:gap-8 space-y-6 md:space-y-8",
    custom: "relative h-full w-full",
  };

  const sectionClasses = `w-full ${paddingClasses[padding]} ${marginClasses[margin]} ${backgroundClasses[background]} ${className}`;

  const contentClasses = `${maxWidthClasses[maxWidth]} ${layoutClasses[layout]}`;

  const headerClasses = `flex flex-col gap-3 md:gap-4 ${textAlignClasses[textAlign]
    } ${layout === "split" ? "lg:text-left" : ""}`;

  return (
    <section
      className={sectionClasses}
      style={
        backgroundImage ? { backgroundImage: `url(${backgroundImage})` } : {}
      }
      {...rest}
    >
      <div className={contentClasses}>
        {(title || subtitle || description || headerActions) && (
          <div className={headerClasses}>
            <div className="flex flex-col md:flex-row items-start justify-between gap-4">
              <div className="flex-1 min-w-0 w-full">
                {subtitle && (
                  <p className="text-xs sm:text-sm font-semibold text-[#0065AF] mb-2 uppercase tracking-wide">
                    {subtitle}
                  </p>
                )}
                {title && (
                  <motion.h2
                    className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-semibold text-center text-[#000000C4] mb-3 md:mb-4"
                    initial={{ y: -50, opacity: 0 }}
                    whileInView={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    viewport={{ once: true }}
                  >
                    {title}
                  </motion.h2>
                )}
                {description && (
                  <p className="text-sm sm:text-base md:text-lg text-[#000000C4]/80 leading-relaxed max-w-3xl mx-auto">
                    {description}
                  </p>
                )}
              </div>
              {headerActions && (
                <div className="flex-shrink-0 w-full md:w-auto">
                  {headerActions}
                </div>
              )}
            </div>
          </div>
        )}

        {children}
      </div>
    </section>
  );
}
