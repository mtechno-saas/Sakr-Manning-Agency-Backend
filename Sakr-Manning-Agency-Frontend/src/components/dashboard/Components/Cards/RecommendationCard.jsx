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

          {/* Buttons Section */}
          {/* {(status === "interview" || status === "pending") && (
            <div
              style={{
                display: "flex",
                flexDirection: "row",
                gap: `${innerGap}px`,
                alignItems: "center",
              }}
            >
              <button
                style={{
                  backgroundColor: COLORS.white,
                  border: `1px solid ${COLORS.secondary}`,
                  borderRadius: `${buttonBorderRadius}px`,
                  padding: buttonPaddingOutlined,
                  fontSize: `${buttonFontSize}px`,
                  fontWeight: "400",
                  color: COLORS.secondary,
                  cursor: "pointer",
                  fontFamily: "Poppins, sans-serif",
                  lineHeight: `${Math.round(24 * scale)}px`,
                  transition: "all 0.2s ease",
                  whiteSpace: "nowrap",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = "#F0F7FF";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = COLORS.white;
                }}
              >
                Approve
              </button>
              <button
                style={{
                  backgroundColor: COLORS.secondary,
                  border: "none",
                  borderRadius: `${buttonBorderRadius}px`,
                  padding: buttonPaddingFill,
                  fontSize: `${buttonFontSize}px`,
                  fontWeight: "400",
                  color: COLORS.white,
                  cursor: "pointer",
                  fontFamily: "Poppins, sans-serif",
                  lineHeight: `${Math.round(24 * scale)}px`,
                  transition: "all 0.2s ease",
                  whiteSpace: "nowrap",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = "#1565C0";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = COLORS.secondary;
                }}
              >
                Schedule Interview
              </button>
            </div>
          )} */}
        </div>
      </div>
    </div>
  );
};

//////////

// // RecommendationCard.jsx - ENHANCED with Action Buttons
// import React from "react";
// import { COLORS } from "../../Constants";

// /**
//  * RecommendationCard Component - Enhanced with interactive action buttons
//  *
//  * @param {string} name - Candidate name
//  * @param {string} position - Job position
//  * @param {string} company - Company name
//  * @param {string} status - Status: 'pending' | 'interview' | 'accepted' | 'rejected'
//  * @param {string} submittedDate - Date CV was submitted (YYYY-MM-DD)
//  * @param {string} interviewDate - Interview date if scheduled (YYYY-MM-DD)
//  * @param {number} scale - UI scale factor
//  * @param {function} onSchedule - Callback for "Schedule Interview" button (pending status only)
//  * @param {function} onReschedule - Callback for "Reschedule" button (interview status only)
//  * @param {function} onApprove - Callback for "Approve" button
//  * @param {function} onReject - Callback for "Reject" button
//  */
// export const RecommendationCard = ({
//   name,
//   position,
//   company,
//   status,
//   submittedDate,
//   interviewDate,
//   scale = 1,
//   onSchedule,
//   onReschedule,
//   onApprove,
//   onReject,
// }) => {
//   // Status color mapping
//   const statusColors = {
//     pending: "#FFC107", // Yellow
//     interview: "#2196F3", // Blue
//     accepted: "#4CAF50", // Green
//     rejected: "#F44336", // Red
//   };

//   // Status labels
//   const statusLabels = {
//     pending: "Pending Review",
//     interview: "Interview Scheduled",
//     accepted: "Accepted",
//     rejected: "Rejected",
//   };

//   const cardPadding = Math.round(16 * scale);
//   // const borderRadius = Math.round(12 * scale);
//   const fontSize = Math.round(14 * scale);
//   const nameFontSize = Math.round(16 * scale);
//   const buttonPadding = `${Math.round(8 * scale)}px ${Math.round(
//     12 * scale
//   )}px`;
//   const buttonFontSize = Math.round(13 * scale);
//   const gap = Math.round(8 * scale);

//   // Button component
//   const ActionButton = ({
//     onClick,
//     children,
//     variant = "primary",
//     disabled = false,
//   }) => {
//     const getButtonStyles = () => {
//       const baseStyles = {
//         padding: buttonPadding,
//         borderRadius: `${Math.round(8 * scale)}px`,
//         fontSize: `${buttonFontSize}px`,
//         fontWeight: "500",
//         fontFamily: "Poppins, sans-serif",
//         cursor: disabled ? "not-allowed" : "pointer",
//         border: "none",
//         transition: "all 0.2s ease",
//         opacity: disabled ? 0.5 : 1,
//       };

//       const variants = {
//         primary: {
//           backgroundColor: COLORS.primary,
//           color: COLORS.white,
//         },
//         success: {
//           backgroundColor: "#4CAF50",
//           color: COLORS.white,
//         },
//         danger: {
//           backgroundColor: "#F44336",
//           color: COLORS.white,
//         },
//         outline: {
//           backgroundColor: "transparent",
//           color: COLORS.primary,
//           border: `1px solid ${COLORS.primary}`,
//         },
//       };

//       return { ...baseStyles, ...variants[variant] };
//     };

//     return (
//       <button
//         onClick={onClick}
//         disabled={disabled}
//         style={getButtonStyles()}
//         onMouseEnter={(e) => {
//           if (!disabled) {
//             e.currentTarget.style.transform = "translateY(-2px)";
//             e.currentTarget.style.boxShadow = "0 4px 8px rgba(0,0,0,0.15)";
//           }
//         }}
//         onMouseLeave={(e) => {
//           e.currentTarget.style.transform = "translateY(0)";
//           e.currentTarget.style.boxShadow = "none";
//         }}
//       >
//         {children}
//       </button>
//     );
//   };

//   return (
//     <div
//       style={{
//         padding: `${cardPadding}px`,
//         borderBottom: `1px solid #E5E7EB`,
//         display: "flex",
//         flexDirection: "column",
//         gap: `${gap}px`,
//         fontFamily: "Inter, sans-serif",
//       }}
//     >
//       {/* Header Row: Name + Status Badge */}
//       <div
//         style={{
//           display: "flex",
//           justifyContent: "space-between",
//           alignItems: "center",
//         }}
//       >
//         <div
//           style={{
//             fontSize: `${nameFontSize}px`,
//             fontWeight: "600",
//             color: COLORS.darkText,
//           }}
//         >
//           {name}
//         </div>
//         <div
//           style={{
//             padding: `${Math.round(4 * scale)}px ${Math.round(12 * scale)}px`,
//             borderRadius: `${Math.round(16 * scale)}px`,
//             backgroundColor: `${statusColors[status]}20`,
//             color: statusColors[status],
//             fontSize: `${Math.round(12 * scale)}px`,
//             fontWeight: "600",
//           }}
//         >
//           {statusLabels[status]}
//         </div>
//       </div>

//       {/* Details Row */}
//       <div
//         style={{
//           display: "flex",
//           flexDirection: "column",
//           gap: `${Math.round(4 * scale)}px`,
//         }}
//       >
//         <div
//           style={{
//             fontSize: `${fontSize}px`,
//             color: COLORS.lightText,
//           }}
//         >
//           <span style={{ fontWeight: "500", color: COLORS.darkText }}>
//             Position:
//           </span>{" "}
//           {position}
//         </div>
//         <div
//           style={{
//             fontSize: `${fontSize}px`,
//             color: COLORS.lightText,
//           }}
//         >
//           <span style={{ fontWeight: "500", color: COLORS.darkText }}>
//             Company:
//           </span>{" "}
//           {company}
//         </div>
//         {submittedDate && (
//           <div
//             style={{
//               fontSize: `${fontSize}px`,
//               color: COLORS.lightText,
//             }}
//           >
//             <span style={{ fontWeight: "500", color: COLORS.darkText }}>
//               Submitted:
//             </span>{" "}
//             {new Date(submittedDate).toLocaleDateString()}
//           </div>
//         )}
//         {interviewDate && (
//           <div
//             style={{
//               fontSize: `${fontSize}px`,
//               color: statusColors[status],
//               fontWeight: "500",
//             }}
//           >
//             📅 Interview: {new Date(interviewDate).toLocaleDateString()} at{" "}
//             {new Date(interviewDate).toLocaleTimeString([], {
//               hour: "2-digit",
//               minute: "2-digit",
//             })}
//           </div>
//         )}
//       </div>

//       {/* Action Buttons Row */}
//       <div
//         style={{
//           display: "flex",
//           gap: `${gap}px`,
//           marginTop: `${Math.round(8 * scale)}px`,
//           flexWrap: "wrap",
//         }}
//       >
//         {/* Schedule Interview Button - Only for pending candidates without interview */}
//         {onSchedule && (
//           <ActionButton onClick={onSchedule} variant="primary">
//             📅 Schedule Interview
//           </ActionButton>
//         )}

//         {/* Reschedule Button - Only for candidates with scheduled interviews */}
//         {onReschedule && (
//           <ActionButton onClick={onReschedule} variant="outline">
//             🔄 Reschedule
//           </ActionButton>
//         )}

//         {/* Approve Button - For pending or interview status */}
//         {onApprove && (
//           <ActionButton onClick={onApprove} variant="success">
//             ✓ Approve
//           </ActionButton>
//         )}

//         {/* Reject Button - For pending or interview status */}
//         {onReject && (
//           <ActionButton onClick={onReject} variant="danger">
//             ✕ Reject
//           </ActionButton>
//         )}

//         {/* No actions available - accepted/rejected states */}
//         {!onSchedule && !onReschedule && !onApprove && !onReject && (
//           <div
//             style={{
//               fontSize: `${Math.round(12 * scale)}px`,
//               color: COLORS.lightText,
//               fontStyle: "italic",
//               padding: `${Math.round(8 * scale)}px 0`,
//             }}
//           >
//             {status === "accepted"
//               ? "✓ No actions needed - candidate accepted"
//               : "✕ No actions available"}
//           </div>
//         )}
//       </div>
//     </div>
//   );
// };
