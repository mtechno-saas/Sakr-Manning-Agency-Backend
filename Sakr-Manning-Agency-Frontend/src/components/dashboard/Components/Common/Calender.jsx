// components/Common/Calender.jsx
// Modern calendar UI for scheduling and viewing interviews
// Month view with click-to-add functionality

import React, { useState, useMemo } from "react";
import { ChevronLeft, ChevronRight, Plus } from "lucide-react";
import { STYLE_TOKENS, getScaledValue } from "../../Styles/globalStyles";
import Button from "../Common/Button";

/**
 * InterviewCalendar Component
 *
 * Modern calendar view for interview scheduling
 * Features:
 * - Month view with navigation
 * - Shows interviews on dates
 * - Click date to add interview
 * - Click interview to view/edit details
 * - Mobile responsive grid
 *
 * @param {array} interviews - Interview data with date property
 * @param {function} onDateClick - Called when date is clicked to add
 * @param {function} onInterviewClick - Called when interview is clicked
 * @param {number} scale - Scale factor
 *
 * Interview format:
 * {
 *   id: 1,
 *   date: "2025-02-10",
 *   candidateName: "John Smith",
 *   position: "Chief Engineer",
 *   time: "10:00 AM",
 *   type: "video"
 * }
 */
const InterviewCalendar = ({
  interviews = [],
  onDateClick,
  onInterviewClick,
  scale = 1,
}) => {
  const [currentDate, setCurrentDate] = useState(new Date());

  // Calculate sizes
  const padding = getScaledValue(16, scale);
  const borderRadius = getScaledValue(12, scale);
  const headerHeight = getScaledValue(60, scale);
  const dayHeaderHeight = getScaledValue(40, scale);
  const cellMinHeight = getScaledValue(100, scale);
  const fontSize = getScaledValue(14, scale);
  const dayNameFontSize = getScaledValue(12, scale);
  const eventFontSize = getScaledValue(12, scale);

  // Get calendar days
  const getDaysInMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const daysInMonth = getDaysInMonth(currentDate);
  const firstDay = getFirstDayOfMonth(currentDate);
  const monthName = currentDate.toLocaleDateString("en-US", {
    month: "long",
    year: "numeric",
  });

  // Create calendar grid
  const calendarDays = useMemo(() => {
    const days = [];
    for (let i = 0; i < firstDay; i++) {
      days.push(null);
    }
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(i);
    }
    return days;
  }, [firstDay, daysInMonth]);

  // Get interviews for specific date
  const getInterviewsForDate = (day) => {
    const dateStr = `${currentDate.getFullYear()}-${String(
      currentDate.getMonth() + 1
    ).padStart(2, "0")}-${String(day).padStart(2, "0")}`;

    return interviews.filter((interview) => interview.date === dateStr);
  };

  // Navigation handlers
  const handlePrevMonth = () => {
    setCurrentDate(
      new Date(currentDate.getFullYear(), currentDate.getMonth() - 1)
    );
  };

  const handleNextMonth = () => {
    setCurrentDate(
      new Date(currentDate.getFullYear(), currentDate.getMonth() + 1)
    );
  };

  return (
    <div
      style={{
        backgroundColor: STYLE_TOKENS.colors.white,
        borderRadius: `${borderRadius}px`,
        boxShadow: STYLE_TOKENS.shadow.sm,
        padding: `${padding}px`,
        width: "100%",
        fontFamily: STYLE_TOKENS.fonts.primary,
      }}
    >
      {/* Header with Month Navigation */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          height: `${headerHeight}px`,
          marginBottom: `${getScaledValue(16, scale)}px`,
          paddingBottom: `${getScaledValue(12, scale)}px`,
          borderBottom: `1px solid ${STYLE_TOKENS.colors.borderColor}`,
        }}
      >
        <button
          onClick={handlePrevMonth}
          style={{
            background: "none",
            border: "none",
            cursor: "pointer",
            padding: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: STYLE_TOKENS.colors.primary,
            transition: STYLE_TOKENS.transition.normal,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.opacity = "0.7";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.opacity = "1";
          }}
          title="Previous month"
          aria-label="Previous month"
        >
          <ChevronLeft size={getScaledValue(24, scale)} />
        </button>

        <h2
          style={{
            margin: 0,
            fontSize: `${getScaledValue(18, scale)}px`,
            fontWeight: 600,
            color: STYLE_TOKENS.colors.darkText,
            flex: 1,
            textAlign: "center",
          }}
        >
          {monthName}
        </h2>

        <button
          onClick={handleNextMonth}
          style={{
            background: "none",
            border: "none",
            cursor: "pointer",
            padding: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: STYLE_TOKENS.colors.primary,
            transition: STYLE_TOKENS.transition.normal,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.opacity = "0.7";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.opacity = "1";
          }}
          title="Next month"
          aria-label="Next month"
        >
          <ChevronRight size={getScaledValue(24, scale)} />
        </button>
      </div>

      {/* Day Names Row */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(7, 1fr)",
          gap: `${getScaledValue(4, scale)}px`,
          marginBottom: `${getScaledValue(8, scale)}px`,
          height: `${dayHeaderHeight}px`,
        }}
      >
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
          <div
            key={day}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: 600,
              color: STYLE_TOKENS.colors.lightText,
              fontSize: `${dayNameFontSize}px`,
              textTransform: "uppercase",
              letterSpacing: "1px",
            }}
          >
            {day}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(7, 1fr)",
          gap: `${getScaledValue(4, scale)}px`,
          minHeight: `${cellMinHeight * 6}px`,
        }}
      >
        {calendarDays.map((day, index) => {
          const dayInterviews = day ? getInterviewsForDate(day) : [];
          const isToday =
            day &&
            day === new Date().getDate() &&
            currentDate.getMonth() === new Date().getMonth() &&
            currentDate.getFullYear() === new Date().getFullYear();

          return (
            <div
              key={index}
              style={{
                // backgroundColor: day
                //   ? STYLE_TOKENS.colors.background
                //   : "transparent",
                border: isToday
                  ? `2px solid ${STYLE_TOKENS.colors.primary}`
                  : `1px solid ${STYLE_TOKENS.colors.borderColor}`,
                borderRadius: `${getScaledValue(8, scale)}px`,
                padding: `${getScaledValue(8, scale)}px`,
                minHeight: `${cellMinHeight}px`,
                display: "flex",
                flexDirection: "column",
                cursor: day ? "pointer" : "default",
                transition: STYLE_TOKENS.transition.normal,
                backgroundColor: isToday
                  ? "rgba(0, 101, 175, 0.05)"
                  : STYLE_TOKENS.colors.background,
                position: "relative",
              }}
              onMouseEnter={(e) => {
                if (day) {
                  e.currentTarget.style.boxShadow = STYLE_TOKENS.shadow.sm;
                  e.currentTarget.style.transform = "translateY(-2px)";
                }
                e.currentTarget.children[2].style.opacity = "1";
                // console.log(e.currentTarget.children[2]);
              }}
              onMouseLeave={(e) => {
                if (day) {
                  e.currentTarget.style.boxShadow = "none";
                  e.currentTarget.style.transform = "translateY(0)";
                }
                e.currentTarget.children[2].style.opacity = "0";
              }}
            >
              {day && (
                <>
                  {/* Day Number */}
                  <div
                    style={{
                      fontSize: `${getScaledValue(14, scale)}px`,
                      fontWeight: 600,
                      color: isToday
                        ? STYLE_TOKENS.colors.primary
                        : STYLE_TOKENS.colors.darkText,
                      marginBottom: `${getScaledValue(4, scale)}px`,
                    }}
                  >
                    {day}
                  </div>

                  {/* Interviews List */}
                  <div
                    style={{
                      flex: 1,
                      display: "flex",
                      flexDirection: "column",
                      gap: `${getScaledValue(4, scale)}px`,
                      overflowY: "auto",
                      minHeight: 0,
                    }}
                  >
                    {dayInterviews.slice(0, 2).map((interview) => (
                      <div
                        key={interview.id}
                        onClick={() =>
                          onInterviewClick && onInterviewClick(interview)
                        }
                        style={{
                          backgroundColor: getTypeColor(interview.type),
                          borderRadius: `${getScaledValue(4, scale)}px`,
                          padding: `${getScaledValue(
                            4,
                            scale
                          )}px ${getScaledValue(6, scale)}px`,
                          fontSize: `${eventFontSize}px`,
                          color: STYLE_TOKENS.colors.white,
                          cursor: "pointer",
                          fontWeight: 500,
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          whiteSpace: "nowrap",
                          transition: STYLE_TOKENS.transition.normal,
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.opacity = "0.8";
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.opacity = "1";
                        }}
                        title={`${interview.candidateName} - ${interview.time}`}
                      >
                        {interview.time} {interview.candidateName}
                      </div>
                    ))}

                    {dayInterviews.length > 2 && (
                      <div
                        style={{
                          fontSize: `${getScaledValue(11, scale)}px`,
                          color: STYLE_TOKENS.colors.lightText,
                          fontWeight: 500,
                          padding: `${getScaledValue(2, scale)}px`,
                        }}
                      >
                        +{dayInterviews.length - 2} more
                      </div>
                    )}
                  </div>

                  {/* Add Button (appears on hover) */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      // onDateClick && onDateClick(day);
                      onDateClick && onDateClick(day, currentDate);
                    }}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      marginTop: "auto",
                      paddingTop: `${getScaledValue(4, scale)}px`,
                      background: "none",
                      border: "none",
                      cursor: "pointer",
                      color: STYLE_TOKENS.colors.primary,
                      opacity: 0,
                      transition: STYLE_TOKENS.transition.normal,
                      fontSize: `${getScaledValue(12, scale)}px`,
                      fontWeight: 500,
                    }}
                    title={`Add interview on ${day}`}
                    aria-label={`Add interview on ${day}`}
                  >
                    <Plus size={getScaledValue(14, scale)} strokeWidth={2} />
                    <span
                      style={{ marginLeft: `${getScaledValue(2, scale)}px` }}
                    >
                      Add
                    </span>
                  </button>
                </>
              )}
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div
        style={{
          display: "flex",
          justifyContent: "flex-start",
          gap: `${getScaledValue(16, scale)}px`,
          marginTop: `${getScaledValue(16, scale)}px`,
          paddingTop: `${getScaledValue(12, scale)}px`,
          borderTop: `1px solid ${STYLE_TOKENS.colors.borderColor}`,
          flexWrap: "wrap",
        }}
      >
        {[
          { type: "video", label: "Video Call" },
          { type: "phone", label: "Phone Call" },
          { type: "in-person", label: "In-Person" },
        ].map((item) => (
          <div
            key={item.type}
            style={{
              display: "flex",
              alignItems: "center",
              gap: `${getScaledValue(6, scale)}px`,
            }}
          >
            <div
              style={{
                width: `${getScaledValue(12, scale)}px`,
                height: `${getScaledValue(12, scale)}px`,
                borderRadius: `${getScaledValue(2, scale)}px`,
                backgroundColor: getTypeColor(item.type),
              }}
            />
            <span
              style={{
                fontSize: `${getScaledValue(12, scale)}px`,
                color: STYLE_TOKENS.colors.lightText,
                fontWeight: 500,
              }}
            >
              {item.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Helper to get color based on interview type
 */
const getTypeColor = (type) => {
  switch (type) {
    case "video":
      return "#2477C3";
    case "phone":
      return "#7D6335";
    case "in-person":
      return "#15AB10";
    default:
      return "#0065AF";
  }
};

export default InterviewCalendar;
