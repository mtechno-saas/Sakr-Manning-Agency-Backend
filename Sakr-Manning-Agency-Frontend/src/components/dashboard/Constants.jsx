import React from "react";

// config.js
// ============================================
// BASE CONFIG & UTILITIES
// ============================================

export const BASE_WIDTH = 1440;
export const BASE_HEIGHT = 1024;

export const GRID_CONFIG = {
  total: 16,
  sidebar: 4,
  content: 12,
};

export const COLORS = {
  primary: "#0065AF",
  primaryLight: "#25548E",
  secondary: "#1976D2",
  background: "#F9FAFB",
  white: "#FFFFFF",
  darkText: "#000000",
  lightText: "#8C8C8C",
  borderColor: "#E5E7EB",
  cardBg: "#DBEAF7",
  pending: "#0065AF",
  interview: "#7D6335",
  accepted: "#15AB10",
  rejected: "#B21101",
  statusGray: "#706F6C",
  iconGray: "#464242",

  // Extended palette for variants
  successLight: "rgba(21, 171, 16, 0.1)",
  successDark: "#15AB10",
  warningLight: "rgba(164, 164, 164, 0.18)",
  warningDark: "#555555",
  amberLight: "rgba(245, 158, 11, 0.15)",
  amberDark: "#B45309",
  purpleLight: "rgba(139, 92, 246, 0.15)",
  purpleDark: "#6D28D9",
  blueLight: "rgba(59, 130, 246, 0.15)",
  blueDark: "#1D4ED8",
  infoLight: "rgba(0, 101, 175, 0.15)",
  infoDark: "#0065AF",
  errorLight: "rgba(178, 17, 1, 0.12)",
  errorDark: "#B21101",
};

export const TOKENS = {
  borderRadius: {
    sm: 8,
    md: 16,
    lg: 22,
    pill: 100,
  },
  shadow: {
    sm: "0px 1px 2px rgba(0, 0, 0, 0.04)",
    md: "0px 2px 10px rgba(0, 0, 0, 0.15)",
    lg: "0px 8px 24px rgba(69, 69, 80, 0.1)",
    xs: "0px 0px 7.4px rgba(164, 164, 164, 0.2)",
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 24,
    xxl: 32,
  },
  fontSize: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20,
    xxl: 24,
  },
};
// Get responsive scale based on viewport width
export const getScale = (viewportWidth) => viewportWidth / BASE_WIDTH;

// Get responsive sidebar width
export const getSidebarWidth = (scale) => Math.round(280 * scale);

// Get responsive content width
export const getContentWidth = (scale) => Math.round(1160 * scale);

export const formatDate = (iso) => {
  try {
    if (!iso) return "-";
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    return d.toLocaleDateString();
  } catch (e) {
    console.error("Date formatting error:", e);
    return iso;
  }
};

export function extractLeadingNumber(val) {
  if (val == null) return null;
  const s = String(val).trim();
  // match optional sign, digits, optional decimal separator + digits
  const m = s.match(/^[-+]?[0-9]+(?:[.,][0-9]+)?/);
  if (!m) return null;
  // unify comma decimal to dot, then parse
  const num = parseFloat(m[0].replace(",", "."));
  return Number.isFinite(num) ? num : null;
}

// Helper to calculate days difference from today
const MS_PER_DAY = 1000 * 60 * 60 * 24;

export function parseDate(value) {
  if (!value) return null;
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? null : d;
}

export function getDaysDifferenceFromToday(date) {
  const d = parseDate(date);
  if (!d) return null;

  const now = new Date();
  // normalize to local midnight for calendar-day difference
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const target = new Date(d.getFullYear(), d.getMonth(), d.getDate());

  // diff in ms, then convert to days
  const diffMs = target - today;
  // Use Math.ceil so any partial day counts as 1 day left.
  // If you prefer only full days remaining use Math.floor instead.
  const days = Math.ceil(diffMs / MS_PER_DAY);
  return days;
}

/** Small helper to format the date nicely */
export function formatDateLocal(date) {
  const d = parseDate(date);
  if (!d) return "—";
  return d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function getExpiryMessage(date) {
  const days = getDaysDifferenceFromToday(date);

  if (days === null) return "Invalid date";
  if (days > 1) return `${days} days left`;
  if (days === 1) return "1 day left";
  if (days === 0) return "Expires today";

  const ago = Math.abs(days);
  return ago === 1 ? "Expired 1 day ago" : `Expired ${ago} days ago`;
}

export function isISODateString(value) {
  if (typeof value !== "string") return false;

  // format check
  const match = value.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) return false;

  const [_, y, m, d] = match;
  const date = new Date(`${y}-${m}-${d}`);

  // real date check (avoids 2025-02-30)
  return (
    date.getFullYear() === Number(y) &&
    date.getMonth() + 1 === Number(m) &&
    date.getDate() === Number(d)
  );
}
