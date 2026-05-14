// StatusBadge.jsx - FIXED: Added explicit width/height for icon images
import React from "react";
import { COLORS } from "../../Constants";

export const StatusBadge = ({ status, count, icon, scale }) => {
  const statusColors = {
    pending: COLORS.pending,
    interview: COLORS.interview,
    accepted: COLORS.accepted,
    rejected: COLORS.rejected,
  };

  const statusLabels = {
    pending: "Interview Scheduled",
    interview: "Total Interviews",
    accepted: "Accepted CVs",
    rejected: "Rejected CVs",
  };

  const width = Math.round(190 * scale);
  const height = Math.round(93 * scale);
  const padding = Math.round(12 * scale);
  const fontSize = Math.round(16 * scale);
  const countFontSize = Math.round(20 * scale);
  const iconSize = Math.round(22 * scale); // Icon size scaled proportionally
  const borderRadius = Math.round(22 * scale);
  const shadow = `0px ${Math.round(2 * scale)}px ${Math.round(
    10 * scale
  )}px rgba(0, 0, 0, 0.15)`;

  return (
    <div
      style={{
        backgroundColor: COLORS.white,
        borderRadius: `${borderRadius}px`,
        padding: `${padding}px`,
        width: `${width}px`,
        minHeight: `${height}px`,
        boxShadow: shadow,
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        fontFamily: "Poppins, sans-serif",
        flexShrink: 0,
      }}
    >
      <h5
        style={{
          fontSize: `${fontSize}px`,
          fontWeight: "500",
          color: statusColors[status],
          margin: 0,
          lineHeight: `${Math.round(24 * scale)}px`,
        }}
      >
        {statusLabels[status]}
      </h5>

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          width: "100%",
        }}
      >
        <span
          style={{
            fontSize: `${countFontSize}px`,
            fontWeight: "500",
            color: COLORS.darkText,
            lineHeight: `${Math.round(24 * scale)}px`,
          }}
        >
          {count}
        </span>

        {/* Icon Image with explicit sizing and fallback */}
        <img
          src={icon}
          alt={`${statusLabels[status]} icon`}
          width={`${iconSize}px`}
          height={`${iconSize}px`}
          style={{
            width: `${iconSize}px`,
            height: `${iconSize}px`,
            objectFit: "contain",
          }}
          onError={(e) => {
            // Fallback if image fails to load
            e.target.style.display = "none";
            const fallback = document.createElement("div");
            fallback.textContent = "•";
            fallback.style.fontSize = `${iconSize}px`;
            fallback.style.color = statusColors[status];
            e.target.parentNode.insertBefore(fallback, e.target);
          }}
        />
      </div>
    </div>
  );
};
