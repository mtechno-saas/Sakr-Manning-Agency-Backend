// src/components/common/ImageBlock.jsx
/*
 * Enhanced Image component with more features
 * Props:
 *  - src: image URL (renamed from image)
 *  - alt: alt text
 *  - aspectRatio: "square" | "video" | "portrait" | "landscape" | "auto"
 *  - objectFit: "cover" | "contain" | "fill" | "none" | "scale-down"
 *  - rounded: "none" | "sm" | "md" | "lg" | "xl" | "2xl" | "full"
 *  - shadow: "none" | "sm" | "md" | "lg" | "xl"
 *  - loading: "lazy" | "eager"
 *  - placeholder: placeholder content while loading
 *  - overlay: overlay content (text, buttons, etc.)
 *  - overlayPosition: "center" | "top" | "bottom" | "top-left" | "top-right" | "bottom-left" | "bottom-right"
 *  - className: additional classes
 *  - onClick: click handler
 */

import { useState } from "react";

export default function ImageBlock({
  src,
  alt = "",
  aspectRatio = "auto",
  objectFit = "cover",
  rounded = "none",
  shadow = "none",
  loading = "lazy",
  placeholder,
  overlay,
  overlayPosition = "center",
  className = "",
  onClick,
  ...rest
}) {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  const aspectRatioClasses = {
    square: "aspect-square",
    video: "aspect-video",
    portrait: "aspect-[3/4]",
    landscape: "aspect-[4/3]",
    auto: "",
  };

  const objectFitClasses = {
    cover: "object-cover",
    contain: "object-contain",
    fill: "object-fill",
    none: "object-none",
    "scale-down": "object-scale-down",
  };

  const roundedClasses = {
    none: "",
    sm: "rounded-sm",
    md: "rounded-md",
    lg: "rounded-lg",
    xl: "rounded-xl",
    "2xl": "rounded-2xl",
    full: "rounded-full",
  };

  const shadowClasses = {
    none: "",
    sm: "shadow-sm",
    md: "shadow-md",
    lg: "shadow-lg",
    xl: "shadow-xl",
  };

  const overlayPositionClasses = {
    center: "items-center justify-center",
    top: "items-start justify-center",
    bottom: "items-end justify-center",
    "top-left": "items-start justify-start",
    "top-right": "items-start justify-end",
    "bottom-left": "items-end justify-start",
    "bottom-right": "items-end justify-end",
  };

  const containerClasses = `relative overflow-hidden ${
    aspectRatioClasses[aspectRatio]
  } ${roundedClasses[rounded]} ${shadowClasses[shadow]} ${
    onClick ? "cursor-pointer" : ""
  } ${className}`;

  const imageClasses = `w-full h-full flex items-center justify-center transition-opacity duration-300 ${
    objectFitClasses[objectFit]
  } ${isLoading ? "opacity-0" : "opacity-100"}`;

  const handleLoad = () => setIsLoading(false);
  const handleError = () => {
    setHasError(true);
    setIsLoading(false);
  };

  return (
    <div className={containerClasses} onClick={onClick} {...rest}>
      {/* Loading/Error Placeholder */}
      {(isLoading || hasError) && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
          {hasError ? (
            <div className="text-center text-gray-400">
              <svg
                className="w-12 h-12 mx-auto mb-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <p className="text-xs">Failed to load</p>
            </div>
          ) : placeholder ? (
            placeholder
          ) : (
            <div className="animate-pulse bg-gray-200 w-full h-full" />
          )}
        </div>
      )}

      {/* Main Image */}
      {src && !hasError && (
        <img
          src={src}
          alt={alt}
          loading={loading}
          className={imageClasses}
          onLoad={handleLoad}
          onError={handleError}
        />
      )}

      {/* Overlay */}
      {overlay && (
        <div
          className={`absolute inset-0 flex p-4 m-0 ${overlayPositionClasses[overlayPosition]}`}
        >
          {overlay}
        </div>
      )}
    </div>
  );
}
