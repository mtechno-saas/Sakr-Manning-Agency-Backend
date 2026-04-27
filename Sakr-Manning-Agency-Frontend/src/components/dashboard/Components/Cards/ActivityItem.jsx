// ActivityItem.jsx
import React, { useState } from "react";
import { COLORS } from "../../Constants";

export const ActivityItem = ({ title, name, timestamp, scale, onClick }) => {
  const [isHovered, setIsHovered] = useState(false);
  const paddingBottom = Math.round(20 * scale);
  const marginBottom = Math.round(20 * scale);
  const titleFontSize = Math.round(20 * scale);
  const nameFontSize = Math.round(20 * scale);
  const timestampFontSize = Math.round(16 * scale);

  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
        gap: `${Math.round(12 * scale)}px`,
        borderBottom: `1px solid ${COLORS.borderColor}`,
        paddingBottom: `${paddingBottom}px`,
        marginBottom: `${marginBottom}px`,
        cursor: onClick ? "pointer" : "default",
        backgroundColor: isHovered && onClick ? "#F8FAFC" : "transparent",
        borderRadius: `${Math.round(8 * scale)}px`,
        padding: onClick ? `${Math.round(8 * scale)}px` : undefined,
        transition: "background-color 0.2s ease",
      }}
    >
      <h4
        style={{
          fontSize: `${titleFontSize}px`,
          fontWeight: "500",
          color: COLORS.darkText,
          margin: 0,
          fontFamily: "Poppins, sans-serif",
          lineHeight: `${Math.round(24 * scale)}px`,
        }}
      >
        {title}
      </h4>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          width: "100%",
          alignItems: "center",
          flexWrap: "wrap",
          gap: `${Math.round(12 * scale)}px`,
        }}
      >
        <p
          style={{
            fontSize: `${nameFontSize}px`,
            fontWeight: "400",
            color: COLORS.darkText,
            margin: 0,
            fontFamily: "Poppins, sans-serif",
            lineHeight: `${Math.round(21 * scale)}px`,
            flex: 1,
          }}
        >
          {name}
        </p>
        <span
          style={{
            fontSize: `${timestampFontSize}px`,
            fontWeight: "400",
            color: COLORS.primary,
            fontFamily: "Poppins, sans-serif",
            lineHeight: `${Math.round(20 * scale)}px`,
            whiteSpace: "nowrap",
          }}
        >
          {timestamp}
        </span>
      </div>
    </div>
  );
};
