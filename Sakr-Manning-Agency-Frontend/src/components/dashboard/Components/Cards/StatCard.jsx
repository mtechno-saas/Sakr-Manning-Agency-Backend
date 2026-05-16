// StatCard.jsx - CORRECTED: Fixed spacing so text doesn't overflow 212x147 dimensions
import React from "react";
import { COLORS } from "../../Constants";

export const StatCard = ({
  title,
  value,
  trend,
  trendDirection,
  icon,
  scale,
}) => {
  const cardWidth = Math.round(212 * scale);
  const cardHeight = Math.round(147 * scale);
  const paddingY = Math.round(12 * scale); // Reduced from 24px to fit content
  const paddingX = Math.round(9 * scale); // Reduced from 16px to fit content
  const fontSize = Math.round(20 * scale); // Reduced from 16px
  const valueFontSize = Math.round(18 * scale); // Reduced from 20px
  const trendFontSize = Math.round(16 * scale); // Reduced from 14px
  const iconSize = Math.round(28 * scale); // Icon size
  const borderRadius = Math.round(22 * scale);
  const shadow = `0px ${Math.round(2 * scale)}px ${Math.round(
    4 * scale
  )}px rgba(0, 0, 0, 0.2)`;
  const trendSymbol = trendDirection === "up" ? "↗" : "↘";

  return (
    <div
      style={{
        backgroundColor: COLORS.cardBg,
        borderRadius: `${borderRadius}px`,
        padding: `${paddingY}px ${paddingX}px`,
        width: `${cardWidth}px`,
        height: `${cardHeight}px`,
        minHeight: `${cardHeight}px`,
        minWidth: `${cardWidth}px`,
        boxShadow: shadow,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "space-around", // Changed from space-between to space-around for better distribution
        gap: `${Math.round(10 * scale)}px`, // Reduced from 12px
        fontFamily: "Poppins, sans-serif",
        flexShrink: 0,
      }}
    >
      {/* Icon Image with explicit sizing and fallback */}
      <img
        src={icon}
        alt={`${title} icon`}
        width={`${iconSize}px`}
        height={`${iconSize}px`}
        style={{
          width: `${iconSize}px`,
          height: `${iconSize}px`,
          objectFit: "contain",
          lineHeight: "1",
          flexShrink: 0,
        }}
      />

      <h3
        style={{
          fontSize: `${fontSize}px`,
          fontWeight: "500",
          color: COLORS.darkText,
          margin: 0,
          textAlign: "center",
          lineHeight: `${Math.round(16 * scale)}px`, // Reduced from 24px
          wordBreak: "break-word",
          flexShrink: 0,
        }}
      >
        {title}
      </h3>

      <p
        style={{
          fontSize: `${valueFontSize}px`,
          fontWeight: "500",
          color: COLORS.darkText,
          margin: 0,
          textAlign: "center",
          fontFamily: "Inter, sans-serif",
          lineHeight: `${Math.round(20 * scale)}px`, // Reduced from 24px
          flexShrink: 0,
        }}
      >
        {value}
      </p>

      <div
        style={{
          fontSize: `${trendFontSize}px`,
          fontWeight: "500",
          // color: COLORS.lightText,
          color: COLORS.darkText,
          textAlign: "center",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: `${Math.round(2 * scale)}px`, // Reduced from 4px
          lineHeight: `${Math.round(16 * scale)}px`, // Reduced from 20px
          flexShrink: 0,
        }}
      >
        <span
          style={{
            fontSize: `${Math.round(12 * scale)}px`, // Reduced from 16px
            color: COLORS.darkText,
          }}
        >
          {trendSymbol}
        </span>
        <span>{trend}</span>
      </div>
    </div>
  );
};
