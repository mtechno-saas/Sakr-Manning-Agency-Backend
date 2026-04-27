import React from "react";

/**
 * InfoCard
 *
 * Props:
 * - variant: "compact" | "default" | "wide"  // controls spacing & avatar size
 * - scale: number (default 1)
 * - avatar: { src, alt } | null
 * - leftMeta: string (e.g. date/time)
 * - title: string
 * - subtitle: string
 * - rightLabel: string (optional, e.g. "Video Call")
 * - actions: [{ key, label, onClick, icon (component), style }]
 * - background, shadow, borderRadius, styleOverrides
 * - onClick: row click handler
 * - children: optional custom center content (takes precedence over title/subtitle)
 */

export function InfoCard({
  variant = "default",
  scale = 1,
  avatar = null,
  leftMeta = "",
  title = "",
  subtitle = "",
  rightLabel = "",
  actions = [],
  background = "#FFFFFF",
  shadow = "0px 2px 10px rgba(0,0,0,0.15)",
  borderRadius = 22,
  styleOverrides = {},
  onClick = null,
  children = null,
  className = "",
  style = {},
  loading = false,
}) {
  // design tokens per variant (unscaled)
  const VARIANTS = {
    compact: {
      containerPadding: 12,
      gap: 24,
      avatarSize: 30,
      titleFontSize: 16,
      subtitleFontSize: 14,
      height: 86,
      actionBtnH: 31,
      actionBtnPadding: [8, 16],
    },
    default: {
      containerPadding: 12,
      gap: 47,
      avatarSize: 71,
      titleFontSize: 20,
      subtitleFontSize: 16,
      height: 114,
      actionBtnH: 31,
      actionBtnPadding: [8, 19],
    },
    wide: {
      containerPadding: 12,
      gap: 47,
      avatarSize: 71,
      titleFontSize: 20,
      subtitleFontSize: 16,
      height: 114,
      actionBtnH: 31,
      actionBtnPadding: [8, 19],
    },
  };

  const t = VARIANTS[variant] || VARIANTS.default;

  // scaled values
  const padding = Math.round(
    (styleOverrides.containerPadding ?? t.containerPadding) * scale
  );
  const gap = Math.round((styleOverrides.gap ?? t.gap) * scale);
  const avatarSize = Math.round(
    (styleOverrides.avatarSize ?? t.avatarSize) * scale
  );
  const titleFs = Math.round(
    (styleOverrides.titleFontSize ?? t.titleFontSize) * scale
  );
  const subFs = Math.round(
    (styleOverrides.subtitleFontSize ?? t.subtitleFontSize) * scale
  );
  const height = Math.round((styleOverrides.height ?? t.height) * scale);
  const actionBtnH = Math.round(
    (styleOverrides.actionBtnH ?? t.actionBtnH) * scale
  );
  const actionBtnPadY = Math.round(t.actionBtnPadding[0] * scale);
  const actionBtnPadX = Math.round(t.actionBtnPadding[1] * scale);
  const br = Math.round((styleOverrides.borderRadius ?? borderRadius) * scale);

  const containerStyle = {
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: `${padding}px`,
    gap: `${gap}px`,
    width: "100%",
    minHeight: `${height}px`,
    background,
    boxShadow: styleOverrides.shadow ?? shadow,
    borderRadius: `${br}px`,
    boxSizing: "border-box",
    cursor: onClick && !loading ? "pointer" : "default",
    opacity: loading ? 0.7 : 1,
    transition: "all 0.2s ease",
    ...style,
  };

  const leftStyle = {
    display: "flex",
    gap: Math.round(12 * scale),
    alignItems: "center",
    minWidth: 0,
  };

  const titleStyle = {
    fontFamily: "Poppins, sans-serif",
    fontSize: `${titleFs}px`,
    fontWeight: 500,
    color: "#000000",
    lineHeight: Math.round(30 * scale) + "px",
    margin: 0,
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  };

  const subtitleStyle = {
    fontFamily: "Poppins, sans-serif",
    fontSize: `${subFs}px`,
    fontWeight: 500,
    color: "#000000",
    lineHeight: Math.round(30 * scale) + "px",
    margin: 0,
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  };

  const metaStyle = {
    fontFamily: "Poppins, sans-serif",
    fontSize: `${Math.round(14 * scale)}px`,
    fontWeight: 500,
    color: "#000000",
  };

  const rightStyle = {
    display: "flex",
    alignItems: "center",
    gap: Math.round(11 * scale),
  };

  const actionBtnStyle = (bg = "#056BB6", color = "#fff") => ({
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    padding: `${actionBtnPadY}px ${actionBtnPadX}px`,
    height: `${actionBtnH}px`,
    borderRadius: Math.round(22 * scale),
    background: bg,
    color,
    border: "none",
    fontFamily: "Poppins, sans-serif",
    fontSize: Math.round(16 * scale),
    cursor: "pointer",
    transition: "all 0.2s ease",
    opacity: loading ? 0.5 : 1,
    pointerEvents: loading ? "none" : "auto",
  });

  return (
    <div
      className={className}
      style={containerStyle}
      onClick={(e) => {
        if (onClick && !loading) onClick(e);
      }}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : -1}
      onKeyDown={(e) => {
        if (onClick && (e.key === "Enter" || e.key === " ")) onClick(e);
      }}
    >
      {/* LEFT group */}
      <div style={leftStyle}>
        {/* avatar */}
        {avatar ? (
          <img
            src={avatar.src}
            alt={avatar.alt || "avatar"}
            style={{
              width: avatarSize,
              height: avatarSize,
              borderRadius: "50%",
              objectFit: "cover",
              flexShrink: 0,
            }}
          />
        ) : (
          <div
            style={{
              width: avatarSize,
              height: avatarSize,
              borderRadius: "50%",
              background: "#F3F4F6",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
            }}
            aria-hidden
          >
            {/* default placeholder */}
            <svg
              width={Math.round(avatarSize * 0.5)}
              height={Math.round(avatarSize * 0.5)}
              viewBox="0 0 24 24"
            >
              <circle cx="12" cy="8" r="3.2" fill="#ddd" />
              <path d="M4 20c0-4 4-6 8-6s8 2 8 6" fill="#ddd" />
            </svg>
          </div>
        )}

        {/* center content (title / subtitle) or children */}
        <div style={{ display: "flex", flexDirection: "column", minWidth: 0 }}>
          {children ? (
            children
          ) : (
            <>
              <div style={titleStyle} title={title}>
                {title}
              </div>
              {subtitle && (
                <div style={subtitleStyle} title={subtitle}>
                  {subtitle}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* MIDDLE: optional leftMeta displayed when present (e.g., date/time) */}
      {leftMeta ? (
        <div
          style={{
            marginLeft: "auto",
            marginRight: Math.round(12 * scale),
            ...metaStyle,
          }}
        >
          {leftMeta}
        </div>
      ) : null}

      {/* RIGHT group: rightLabel + actions */}
      <div style={rightStyle}>
        {rightLabel ? (
          <div
            style={{
              fontFamily: "Poppins, sans-serif",
              fontSize: Math.round(20 * scale),
              fontWeight: 500,
            }}
          >
            {rightLabel}
          </div>
        ) : null}

        {actions.map((a) => (
          <button
            key={a.key}
            onClick={(e) => {
              e.stopPropagation();
              if (a.onClick && !loading) a.onClick(a);
            }}
            aria-label={a.label}
            title={a.label}
            style={{
              ...(a.style || {}),
              ...actionBtnStyle(a.bg || "#056BB6", a.color || "#FFFFFF"),
            }}
          >
            {a.icon ? a.icon : a.label}
          </button>
        ))}
      </div>
    </div>
  );
}
