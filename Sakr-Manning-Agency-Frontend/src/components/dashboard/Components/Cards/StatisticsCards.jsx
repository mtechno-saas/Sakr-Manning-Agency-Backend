// StatisticsCard.jsx
import React from "react";

/**
 * StatisticsCard
 *
 * Props:
 * - segments: [{ key, label, value, color }]   // values are numeric; percent computed from sum
 * - title: string (default: "Hire vs Cancel")
 * - timeframeLabel: string (default: "Today")
 * - width: number design-unit (default 440)
 * - height: number design-unit (default 248)
 * - scale: number (default 1) -- same pattern as ActivityItem
 *
 * Example usage:
 * <StatisticsCard
 *   title="Hire vs Cancel"
 *   timeframeLabel="Today"
 *   segments={[
 *     { key: "under", label: "Under review", value: 40, color: "#52C93F" },
 *     { key: "interviewed", label: "Total Interviewed", value: 60, color: "#D6B7FF" },
 *     { key: "pending", label: "Total Pending", value: 30, color: "#A2A2A2" },
 *     { key: "approved", label: "Approved", value: 20, color: "#2477C3" },
 *   ]}
 *   scale={1}
 * />
 */

function polarToCartesian(cx, cy, r, angleDeg) {
  const angleRad = ((angleDeg - 90) * Math.PI) / 180.0;
  return {
    x: cx + r * Math.cos(angleRad),
    y: cy + r * Math.sin(angleRad),
  };
}

function describeArc(cx, cy, r, startAngle, endAngle) {
  // returns an SVG path string for arc from startAngle to endAngle (degrees)
  const start = polarToCartesian(cx, cy, r, endAngle);
  const end = polarToCartesian(cx, cy, r, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
  return `M ${cx} ${cy} L ${start.x} ${start.y} A ${r} ${r} 0 ${largeArcFlag} 0 ${end.x} ${end.y} Z`;
}

export function StatisticsCard({
  segments = [],
  title = "Hire vs Cancel",
  timeframeLabel = "Today",
  width = 440,
  height = 248,
  scale = 1,
  style = {},
  className = "",
  loading = false,
}) {
  // Figma tokens (unscaled)
  const tokens = {
    padding: 24,
    gap: 30,
    borderRadius: 22,
    shadow: "0px 8px 24px rgba(69,69,80,0.1)",
    headerFontSize: 18,
    headerColor: "#656575",
    timeframeFontSize: 12,
    pieSize: 146,
    legendWidth: 222,
    legendGap: 8,
    legendDot: 16,
    labelFontSize: 16,
    percentFontSize: 16,
    labelColor: "#1A1919",
  };

  // scaled values
  const pad = Math.round(tokens.padding * scale);
  const gap = Math.round(tokens.gap * scale);
  const containerW = Math.round(width * scale);
  const containerH = Math.round(height * scale);
  const borderRadius = Math.round(tokens.borderRadius * scale);
  const headerFontSize = Math.round(tokens.headerFontSize * scale);
  const timeframeFontSize = Math.round(tokens.timeframeFontSize * scale);
  const pieSize = Math.round(tokens.pieSize * scale);
  const legendW = Math.round(tokens.legendWidth * scale);
  const legendDot = Math.round(tokens.legendDot * scale);
  const labelFontSize = Math.round(tokens.labelFontSize * scale);
  const percentFontSize = Math.round(tokens.percentFontSize * scale);

  // compute percentages
  const totalValue =
    segments.reduce((s, seg) => s + (Number(seg.value) || 0), 0) || 1;
  const segs = segments.map((seg) => ({
    ...seg,
    pct: (Number(seg.value || 0) / totalValue) * 100,
  }));

  // Build arcs: accumulate start/end angles
  let accAngle = 0; // degrees
  const center = pieSize / 2;
  const radius = Math.round((pieSize / 2) * 0.9); // leave small padding
  const arcs = segs.map((s) => {
    const angle = (s.pct / 100) * 360;
    const startAngle = accAngle;
    const endAngle = accAngle + angle;
    accAngle += angle;
    return {
      ...s,
      startAngle,
      endAngle,
      path: describeArc(center, center, radius, startAngle, endAngle),
    };
  });

  // Component styles
  const containerStyle = {
    width: containerW,
    height: containerH,
    padding: pad,
    display: "flex",
    flexDirection: "column",
    gap: gap,
    background: "#FDFDFD",
    boxShadow: tokens.shadow,
    borderRadius,
    boxSizing: "border-box",
    opacity: loading ? 0.6 : 1,
    transition: "all 0.2s ease",
    ...style,
  };

  const headerStyle = {
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    width: Math.round((containerW - pad * 2) * 0.55),
  };

  const titleStyle = {
    margin: 0,
    fontFamily: "Inter, sans-serif",
    fontSize: headerFontSize,
    fontWeight: 500,
    lineHeight: Math.round(24 * scale) + "px",
    color: tokens.headerColor,
  };

  const timeframeStyle = {
    background: "#F8F7F1",
    padding: `${Math.round(4 * scale)}px ${Math.round(8 * scale)}px`,
    borderRadius: Math.round(2 * scale),
    display: "flex",
    alignItems: "center",
    gap: Math.round(8 * scale),
    fontFamily: "Inter, sans-serif",
    fontSize: timeframeFontSize,
    color: tokens.headerColor,
  };

  const statsRowStyle = {
    display: "flex",
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "flex-start",
    gap: Math.round(24 * scale),
    width: "100%",
    boxSizing: "border-box",
  };

  const pieWrapperStyle = {
    width: pieSize,
    height: pieSize,
    position: "relative",
    flex: "0 0 auto",
  };

  const legendStyle = {
    display: "flex",
    flexDirection: "column",
    gap: Math.round(tokens.legendGap * scale),
    width: legendW,
    boxSizing: "border-box",
  };

  const legendItemStyle = {
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    width: "100%",
  };

  const legendLeftStyle = {
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
    gap: Math.round(12 * scale),
  };

  const dotStyle = (color) => ({
    width: legendDot,
    height: legendDot,
    borderRadius: "50%",
    background: color,
    flexShrink: 0,
  });

  const labelStyle = {
    fontFamily: "Inter, sans-serif",
    fontSize: labelFontSize,
    color: tokens.labelColor,
    lineHeight: Math.round(24 * scale) + "px",
  };

  const pctStyle = {
    fontFamily: "Inter, sans-serif",
    fontSize: percentFontSize,
    color: tokens.labelColor,
    lineHeight: Math.round(24 * scale) + "px",
    minWidth: Math.round(34 * scale),
    textAlign: "right",
  };

  return (
    <div
      className={className}
      style={containerStyle}
      role="region"
      aria-label={`${title} statistics`}
    >
      {/* Header */}
      <div style={headerStyle}>
        <h4 style={titleStyle}>{loading ? "..." : title}</h4>
        <div style={timeframeStyle}>
          <div style={{ fontSize: timeframeFontSize, fontWeight: 400 }}>
            {timeframeLabel}
          </div>
        </div>
      </div>

      {/* Stats body */}
      <div style={statsRowStyle}>
        {/* Pie */}
        <div
          style={pieWrapperStyle}
          aria-hidden="false"
          role="img"
          aria-label="Pie chart"
        >
          <svg
            width={pieSize}
            height={pieSize}
            viewBox={`0 0 ${pieSize} ${pieSize}`}
          >
            {/* background circle fallback */}
            <circle cx={center} cy={center} r={radius} fill="#fff" />
            {/* render arcs */}
            {arcs.map((a, idx) => (
              <path
                key={a.key || idx}
                d={a.path}
                fill={a.color}
                stroke="none"
              />
            ))}
            {/* center cutout to create donut-like slight hole if desired (optional) */}
            <circle
              cx={center}
              cy={center}
              r={Math.round(radius * 0.45)}
              fill="#FDFDFD"
            />
          </svg>
        </div>

        {/* Legend / keys */}
        <div style={legendStyle}>
          {segs.map((s, i) => {
            // Support labels like "Pending (4)" — split count from label
            const countMatch = s.label.match(/\((\d+)\)$/);
            const count = countMatch ? countMatch[1] : null;
            const cleanLabel = count !== null ? s.label.replace(/\s*\(\d+\)$/, "") : s.label;
            return (
              <div key={s.key || i} style={legendItemStyle}>
                <div style={legendLeftStyle}>
                  <div style={dotStyle(s.color)} />
                  <div style={labelStyle}>{cleanLabel}</div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: Math.round(8 * scale) }}>
                  {count !== null && (
                    <div
                      style={{
                        fontFamily: "Inter, sans-serif",
                        fontSize: labelFontSize,
                        fontWeight: 700,
                        color: s.color,
                        minWidth: Math.round(22 * scale),
                        textAlign: "right",
                      }}
                    >
                      {count}
                    </div>
                  )}
                  <div style={pctStyle}>{Math.round(s.pct)}%</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

/////////////////////////////////////////////////////////////////////////
/**
 * SmallProgressCard
 * - title: string ("Protein")
 * - percent: number (0-100)
 * - width, height: design units (defaults match Figma)
 * - scale: number (default 1)
 * - trackColor / fillColor: hex
 */
export function SmallProgressCard({
  title = "Today's Interview",
  flag = "partial",
  percent = 82,
  width = 348.33,
  height = 86.27,
  scale = 1,
  trackColor = "#F9F9F9",
  fillColor = "#54D14D",
  background = "#FFFFFF",
  style = {},
  className = "",
  loading = false,
}) {
  // scaled tokens
  const W = Math.round(width * scale);
  const H = Math.round(height * scale);
  const borderRadius = Math.round(22 * scale);
  // const shadow = "0px 2px 48px rgba(0,0,0,0.06)";
  const paddingH = Math.round(12 * scale);
  const paddingV = Math.round(12 * scale);
  const titleFontSize = Math.round(14 * scale);
  const percentFontSize = Math.round(14 * scale);
  const lineHeight = Math.round(8.35 * scale); // track height
  const trackRadius = Math.round(22 * scale);
  const trackWidth = Math.round(W - paddingH * 2); // full track inside padding
  const fillWidth = Math.round(
    (Math.max(0, Math.min(100, percent)) / 100) * trackWidth
  );

  return (
    <div
      className={className}
      style={{
        width: W,
        height: H,
        position: "relative",
        background,
        borderRadius,
        // boxShadow: shadow,
        padding: `${paddingV}px ${paddingH}px`,
        boxSizing: "border-box",
        opacity: loading ? 0.6 : 1,
        transition: "all 0.2s ease",
        ...style,
      }}
      role="group"
      aria-label={`${title} progress ${percent}`}
    >
      {/* Title and percent row */}
      <div
        style={{ position: "relative", height: `${Math.round(24 * scale)}px` }}
      >
        <div
          style={{
            position: "absolute",
            left: `${Math.round((1.13 / 100) * W)}px`,
            top: "50%",
            transform: `translateY(-50%)`,
            fontFamily: "Poppins, sans-serif",
            fontSize: titleFontSize,
            fontWeight: 500,
            letterSpacing: "1px",
            color: "#1E2022",
            lineHeight: `${Math.round(21 * scale)}px`,
          }}
        >
          {title}
        </div>

        <div
          style={{
            position: "absolute",
            right: `${Math.round((0 / 100) * W)}px`,
            top: "50%",
            transform: `translateY(-50%)`,
            fontFamily: "Poppins, sans-serif",
            fontSize: percentFontSize,
            fontWeight: 400,
            letterSpacing: "1px",
            color: "#77838F",
            lineHeight: `${Math.round(21 * scale)}px`,
            paddingRight: Math.round(8 * scale),
          }}
        >
          {loading ? "--" : `${percent}`}
        </div>
      </div>

      {/* Track (line) placed below */}
      <div
        style={{
          position: "absolute",
          left: `${Math.round(12.63 * scale)}px`,
          right: `${Math.round(12.63 * scale)}px`,
          bottom: `${Math.round(12 * scale)}px`,
          height: `${lineHeight}px`,
          borderRadius: `${trackRadius}px`,
          background: trackColor,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${flag === "total" ? fillWidth : fillWidth * 10}px`,
            height: "100%",
            background: fillColor,
            borderRadius: `${trackRadius}px`,
            transition: "width 400ms ease",
          }}
        />
      </div>
    </div>
  );
}

/////////////////////////////////////////////////////////////////////////
/**
 * StackedProgressLegendCard
 * - segments: [{ key, color, width (design px for stacked bar) OR pct }]
 *    You can supply absolute widths for stacked visual or {pct} to compute relative widths
 * - rows: [{ color, label, remainingText }]  // each legend row shown below stacked bar
 * - width/height: design units defaults approximate your figma
 * - scale: number (default 1)
 */
export function StackedProgressLegendCard({
  segments = [
    { key: "s1", color: "#35C2FD", pct: 60 },
    { key: "s2", color: "#38DA4E", pct: 40 },
    { key: "s3", color: "#BF4DD1", pct: 30 },
  ],
  rows = [
    { key: "carbs", color: "#BF4DD1", label: "Carbs", remaining: "Remaining" },
    {
      key: "protein",
      color: "#38DA4E",
      label: "Protein",
      remaining: "Remaining",
    },
    { key: "fat", color: "#35C2FD", label: "Fat", remaining: "Remaining" },
  ],
  width = 747.53,
  height = 214,
  scale = 1,
  background = "#FFFFFF",
  style = {},
  className = "",
  loading = false,
}) {
  const W = Math.round(width * scale);
  const H = Math.round(height * scale);
  const containerRadius = Math.round(5 * scale);
  const shadow = "0px 2px 48px rgba(0,0,0,0.06)";
  const paddingLeft = Math.round(16 * scale);
  const paddingTop = Math.round(14 * scale);
  const stackedBarH = Math.round(12 * scale);
  const stackedBarAvailableW = Math.round(693.31 * scale); // as per Figma token

  // Compute segment widths based on pct if provided
  const totalPct = segments.reduce((s, x) => s + (x.pct || 0), 0) || 100;
  const segs = segments.map((s) => {
    const pct = s.pct !== undefined ? s.pct : 0;
    const px = Math.round((pct / totalPct) * stackedBarAvailableW);
    return { ...s, pct, px };
  });

  const rowH = Math.round(40 * scale);
  const leftMarkerW = Math.round(15.49 * scale);
  const labelFont = Math.round(16 * scale);
  const remainingFont = Math.round(14 * scale);

  return (
    <div
      className={className}
      style={{
        width: W,
        minHeight: H,
        background,
        borderRadius: containerRadius,
        boxShadow: shadow,
        padding: `${paddingTop}px ${paddingLeft}px`,
        boxSizing: "border-box",
        opacity: loading ? 0.6 : 1,
        transition: "all 0.2s ease",
        ...style,
      }}
    >
      {/* Stacked Bar (center aligned) */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          marginBottom: Math.round(18 * scale),
        }}
      >
        <div
          style={{
            width: stackedBarAvailableW,
            height: stackedBarH,
            background: "#F9F9F9",
            borderRadius: Math.round(7.5 * scale),
            overflow: "hidden",
            display: "flex",
            alignItems: "center",
          }}
        >
          {/* Render each segment left-to-right */}
          {segs.map((s, idx) => (
            <div
              key={s.key || idx}
              style={{
                width: s.px,
                height: "100%",
                background: s.color,
              }}
            />
          ))}
        </div>
      </div>

      {/* Rows list (legend with left color marker) */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: Math.round(16 * scale),
        }}
      >
        {rows.map((r, i) => (
          <div
            key={r.key || i}
            style={{
              display: "flex",
              alignItems: "center",
              height: rowH,
            }}
          >
            <div
              style={{
                width: leftMarkerW,
                height: rowH,
                borderRadius: Math.round(7.5 * scale),
                background: r.color,
                flexShrink: 0,
              }}
            />

            <div
              style={{
                marginLeft: Math.round(12 * scale),
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                width: "100%",
              }}
            >
              <div
                style={{
                  fontFamily: "Poppins, sans-serif",
                  fontWeight: 500,
                  fontSize: labelFont,
                  color: "#1E2022",
                }}
              >
                {r.label}
              </div>
              <div
                style={{
                  fontFamily: "Poppins, sans-serif",
                  fontWeight: 500,
                  fontSize: remainingFont,
                  color: "#1E2022",
                }}
              >
                {r.remaining}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
