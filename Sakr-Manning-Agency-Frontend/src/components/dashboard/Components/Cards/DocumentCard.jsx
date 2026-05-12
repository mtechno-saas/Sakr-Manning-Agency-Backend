import React, { useState, useEffect } from "react";
import Button from "../Common/Button";
import {
  COLORS,
  TOKENS,
  getExpiryMessage,
  formatDateLocal,
} from "../../Constants";

import { ASSETS } from "../../../../utils/constants";
const DocumentCard = ({ document, index, scale = 1, onView, onDownload, onEdit, onDelete }) => {
  const borderRadius = Math.round(22 * scale);
  const padding = Math.round(16 * scale);
  const avatarSize = Math.round(64 * scale);

  // --- Status Configuration (Left Bar) ---
  const getStatusConfig = (status) => {
    switch (status) {
      case "Signed":
        return { bg: "#C1D5E8", label: "Signed" }; // Blueish
      case "Pending Signature":
        return { bg: "#EAEBC3", label: "Pending Signature" }; // Yellow-Green
      case "Draft":
        return { bg: "#CDEBC3", label: "Draft" }; // Greenish
      case "Expired":
        return { bg: "#F7CCBD", label: "Expired" }; // Redish
      case "Cancelled":
        return { bg: "#FDFECF", label: "Cancelled" };
      default:
        return { bg: "#E5E7EB", label: status };
    }
  };

  const statusConfig = getStatusConfig(document.status);

  // --- Timing/Urgency Configuration (Text Color) ---
  const getTimingColor = (signOffDate) => {
    if (!signOffDate) return "#1E1E1E"; // Default dark text

    const today = new Date();
    const expiry = new Date(signOffDate);
    const diffTime = expiry - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    // Handle Expired (negative days) separately if needed, or stick to Critical logic
    if (diffDays < 0) return "#D32F2F"; // Expired (Dark Red)

    // Timing States from Image
    if (diffDays <= 7) return "#A0522D"; // Critical (Salmon/Orange)
    if (diffDays <= 30) return "#928C41"; // Warning (Amber/Dark Yellow - readable on white)
    if (diffDays <= 60) return "#4B5563"; // Notice (Purple)

    return "#007AFF"; // Default if > 60 days
  };

  const [expiryDate, setExpiryDate] = useState("");
  // eslint-disable-next-line no-unused-vars
  const [expiryMessage, setExpiryMessage] = useState("");
  const [timingColor, setTimingColor] = useState("#1E1E1E");

  useEffect(() => {
    if (document?.signOffDate) {
      setExpiryDate(formatDateLocal(document.signOffDate));
      setExpiryMessage(getExpiryMessage(document.signOffDate));
      // Set the color based on timing
      setTimingColor(getTimingColor(document.signOffDate));
    } else {
      setExpiryDate("—");
      setExpiryMessage("No expiry date");
      setTimingColor("#1E1E1E");
    }
  }, [document?.signOffDate]);

  // Get user name
  const userName = document.user || "Unknown User";
  // Get ship name / Role
  const shipName = document.ship || "Unknown Ship";
  const companyName = document.company || "Unknown Company";
  const positionName = document.position || "Unknown Role";


  // Calculate duration
  const duration =
    document.signOnDate && document.signOffDate
      ? `${Math.round(
        (new Date(document.signOffDate) - new Date(document.signOnDate)) /
        (1000 * 60 * 60 * 24 * 30)
      )} months`
      : "12 months";

  // --- Styles ---
  const textPrimary = {
    fontSize: `${Math.round(18 * scale)}px`,
    fontWeight: 600,
    color: "#000000",
    fontFamily: "Poppins, sans-serif",
    lineHeight: `${Math.round(24 * scale)}px`,
    marginBottom: `${Math.round(2 * scale)}px`,
  };

  const textSecondary = {
    fontSize: `${Math.round(16 * scale)}px`,
    fontWeight: 400,
    color: "#1E1E1E",
    fontFamily: "Poppins, sans-serif",
    lineHeight: `${Math.round(24 * scale)}px`,
  };

  const textDuration = {
    ...textSecondary,
    // color: "#007AFF",
    color: timingColor,
    marginTop: `${Math.round(4 * scale)}px`,
    fontWeight: 500,
  };

  const textDateLabel = {
    fontSize: `${Math.round(16 * scale)}px`,
    fontWeight: 500,
    color: "#000",
    marginRight: `${Math.round(8 * scale)}px`,
  };

  const textDateValue = {
    fontSize: `${Math.round(16 * scale)}px`,
    fontWeight: 400,
    color: "#1E1E1E",
  };

  return (
    <div
      style={{
        background: COLORS.white,
        borderRadius: `${borderRadius}px`,
        padding: `${padding}px`,
        boxShadow: TOKENS.shadow.sm,
        border: "1px solid #E5E7EB",
        display: "flex",
        alignItems: "center",
        minWidth: "100%",
        width: "100%",
        maxWidth: "fit-content",
        boxSizing: "border-box",
        justifyContent: "space-between",
      }}
    >
      {/* 1. Status Bar (Left Pill) - Indicates Document Status */}
      <div
        style={{
          width: `${Math.round(16 * scale)}px`,
          height: `${Math.round(80 * scale)}px`,
          background: statusConfig.bg,
          borderRadius: `${Math.round(10 * scale)}px`,
          marginRight: `${Math.round(20 * scale)}px`,
          flexShrink: 0,
        }}
        title={`Status: ${statusConfig.label}`}
      />

      {/* Index */}
      {index && (
        <div
          style={{
            fontSize: `${Math.round(14 * scale)}px`,
            fontWeight: 600,
            color: "#9CA3AF",
            width: `${Math.round(24 * scale)}px`,
            flexShrink: 0,
            textAlign: "center",
            marginRight: `${Math.round(12 * scale)}px`
          }}
        >
          {index}
        </div>
      )}

      {/* 2. Avatar */}
      <div
        style={{
          width: `${avatarSize}px`,
          height: `${avatarSize}px`,
          borderRadius: "50%",
          background: `url(${ASSETS.LOGO}) center/cover no-repeat #C4C4C4`,
          marginRight: `${Math.round(20 * scale)}px`,
          flexShrink: 0,
        }}
      />

      {/* 3. User Info */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          // flex: 1,
          minWidth: `${Math.round(400 * scale)}px`,
        }}
      >
        <div style={textPrimary}>{userName}</div>
        <div style={textSecondary}>{companyName}</div>
        <div style={textSecondary}>{shipName}</div>
        <div style={textSecondary}>{positionName}</div>
        {duration && <div style={textDuration}>Duration: {duration}</div>}
      </div>

      {/* 4. Dates (Generated / Signed) */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          gap: `${Math.round(4 * scale)}px`,
          marginRight: `${Math.round(30 * scale)}px`,
          minWidth: `${Math.round(350 * scale)}px`,
        }}
      >
        <div style={{ display: "flex", alignItems: "center" }}>
          <span style={textDateLabel}>Generated:</span>
          <span style={textDateValue}>
            {document.signOnDate
              ? formatDateLocal(document.signOnDate)
              : "2024-01-18"}
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center" }}>
          {/* Label changes based on status */}
          <span style={textDateLabel}>
            {document.status === "Signed" ? "Signed:" : "Expires:"}
          </span>
          {/* Value changes color based on timing (Critical/Warning/Notice) */}
          <span style={textDateValue}>
            {document.signOffDate ? expiryDate : "2024-01-19"}
          </span>
        </div>
      </div>

      {/* 5. Action Buttons */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: `${Math.round(8 * scale)}px`,
        }}
      >
        <Button
          variant="ghost"
          scale={scale}
          onClick={() => onView(document.id)}
          style={{ padding: 0 }}
          ariaLabel="View document"
          title="View document"
        >
          <svg
            width={Math.round(24 * scale)}
            height={Math.round(24 * scale)}
            viewBox="0 0 24 24"
            fill="none"
          >
            <path
              d="M1 12C1 12 5 4 12 4C19 4 23 12 23 12C23 12 19 20 12 20C5 20 1 12 1 12Z"
              stroke="black"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <circle
              cx="12"
              cy="12"
              r="3"
              stroke="black"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </Button>

        {/* Download Button */}
        {onDownload && (
          <Button
            variant="ghost"
            scale={scale}
            onClick={() => onDownload(document.id)}
            style={{ padding: 0 }}
            ariaLabel="Download document"
            title="Download document"
          >
            <svg
              width={Math.round(24 * scale)}
              height={Math.round(24 * scale)}
              viewBox="0 0 24 24"
              fill="none"
            >
              <path
                d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15"
                stroke="black"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M7 10L12 15L17 10"
                stroke="black"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M12 15V3"
                stroke="black"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </Button>
        )}

        {/* Edit Button */}
        {onEdit && (
          <Button
            variant="ghost"
            scale={scale}
            onClick={() => onEdit(document.id)}
            style={{ padding: 0 }}
            ariaLabel="Edit document"
            title="Edit document"
          >
            <svg
              width={Math.round(24 * scale)}
              height={Math.round(24 * scale)}
              viewBox="0 0 24 24"
              fill="none"
            >
              <path
                d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13"
                stroke="black"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M18.5 2.50001C18.8978 2.10219 19.4374 1.87869 20 1.87869C20.5626 1.87869 21.1022 2.10219 21.5 2.50001C21.8978 2.89784 22.1213 3.4374 22.1213 4.00001C22.1213 4.56262 21.8978 5.10219 21.5 5.50001L12 15L8 16L9 12L18.5 2.50001Z"
                stroke="black"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </Button>
        )}

        <Button
          variant="ghost"
          scale={scale}
          onClick={() => onDelete(document.id)}
          ariaLabel="Delete document"
          title="Delete document"
        >
          <svg
            width={Math.round(24 * scale)}
            height={Math.round(24 * scale)}
            viewBox="0 0 24 24"
            fill="none"
          >
            <path
              d="M3 6H21M8 6V4C8 3.44772 8.44772 3 9 3H15C15.5523 3 16 3.44772 16 4V6M19 6V20C19 20.5523 18.5523 21 18 21H6C5.44772 21 5 20.5523 5 20V6H19Z"
              stroke="black"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </Button>
      </div>
    </div>
  );
};

export default DocumentCard;
