// RecommendationCard.jsx
import React, { useState } from "react";
import { COLORS } from "../../Constants";

export const RecommendationCard = ({
  name,
  position,
  company,
  status,
  submittedDate,
  interviewDate,
  scale,
  onClick,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const statusColors = {
    pending: COLORS.pending,
    interview: COLORS.interview,
    accepted: COLORS.accepted,
    rejected: COLORS.rejected,
  };

  const paddingVertical = Math.round(12 * scale);
  const paddingHorizontal = Math.round(14 * scale);
  const mainGap = Math.round(6 * scale);
  const innerGap = Math.round(10 * scale);
  const verticalGap = Math.round(25 * scale);
  const dateButtonGap = Math.round(11 * scale);
  const nameCompanyGap = Math.round(10 * scale);

  const titleFontSize = Math.round(20 * scale);
  const posFontSize = Math.round(18 * scale);
  const compFontSize = Math.round(16 * scale);
  const dateFontSize = Math.round(16 * scale);
  const statusFontSize = Math.round(20 * scale);
  // const buttonFontSize = Math.round(16 * scale);
  // const buttonBorderRadius = Math.round(30 * scale);
  // const buttonPaddingOutlined = `${Math.round(3 * scale)}px ${Math.round(
  //   10 * scale
  // )}px`;
  // const buttonPaddingFill = `${Math.round(6 * scale)}px ${Math.round(
  //   8 * scale
  // )}px`;

  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        display: "flex",
        flexDirection: "column",
        padding: `${paddingVertical}px ${paddingHorizontal}px`,
        gap: `${verticalGap}px`,
        width: "100%",
        cursor: onClick ? "pointer" : "default",
        backgroundColor: isHovered && onClick ? "#F8FAFC" : "transparent",
        borderRadius: `${Math.round(8 * scale)}px`,
        transition: "background-color 0.2s ease",
      }}
    >
      {/* Main Row: Two Columns */}
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: `${mainGap}px`,
          width: "100%",
        }}
      >
        {/* Left Column */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: `${innerGap}px`,
            flex: "0 0 auto",
          }}
        >
          {/* Name Row with Status */}
          <div
            style={{
              display: "flex",
              flexDirection: "row",
              justifyContent: "space-between",
              alignItems: "flex-end",
              gap: `${innerGap}px`,
              width: "250px",
            }}
          >
            <h4
              style={{
                fontSize: `${titleFontSize}px`,
                fontWeight: "500",
                color: COLORS.darkText,
                margin: 0,
                fontFamily: "Poppins, sans-serif",
                lineHeight: `${Math.round(30 * scale)}px`,
                display: "flex",
                alignItems: "flex-end",
              }}
            >
              {name}
            </h4>
            <span
              style={{
                fontSize: `${statusFontSize}px`,
                fontWeight: "500",
                color: statusColors[status],
                fontFamily: "Poppins, sans-serif",
                lineHeight: `${Math.round(30 * scale)}px`,
                display: "flex",
                alignItems: "flex-end",
                whiteSpace: "nowrap",
              }}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </span>
          </div>

          {/* Position and Company Row */}
          <div
            style={{
              display: "flex",
              flexDirection: "row",
              gap: `${nameCompanyGap}px`,
              alignItems: "center",
              flexWrap: "nowrap",
            }}
          >
            <span
              style={{
                fontSize: `${posFontSize}px`,
                fontWeight: "400",
                color: COLORS.darkText,
                fontFamily: "Poppins, sans-serif",
                lineHeight: `${Math.round(27 * scale)}px`,
                display: "flex",
                alignItems: "flex-end",
              }}
            >
              {position}
            </span>
            <span
              style={{
                fontSize: `${compFontSize}px`,
                fontWeight: "400",
                color: COLORS.iconGray,
                fontFamily: "Poppins, sans-serif",
                lineHeight: `${Math.round(24 * scale)}px`,
                display: "flex",
                alignItems: "flex-end",
              }}
            >
              {company}
            </span>
          </div>
        </div>

        {/* Right Column */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "flex-end",
            gap: `${dateButtonGap}px`,
            flex: "0 0 auto",
          }}
        >
          {/* Dates Section */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-end",
              gap: `${innerGap}px`,
            }}
          >
            {submittedDate && (
              <p
                style={{
                  fontSize: `${dateFontSize}px`,
                  fontWeight: "400",
                  color: COLORS.statusGray,
                  margin: 0,
                  fontFamily: "Poppins, sans-serif",
                  lineHeight: `${Math.round(24 * scale)}px`,
                  display: "flex",
                  alignItems: "flex-end",
                }}
              >
                Submitted: {submittedDate}
              </p>
            )}

            {interviewDate && (
              <p
                style={{
                  fontSize: `${dateFontSize}px`,
                  fontWeight: "400",
                  color: statusColors[status],
                  margin: 0,
                  fontFamily: "Poppins, sans-serif",
                  lineHeight: `${Math.round(24 * scale)}px`,
                  display: "flex",
                  alignItems: "flex-end",
                }}
              >
                Interview: {interviewDate}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

