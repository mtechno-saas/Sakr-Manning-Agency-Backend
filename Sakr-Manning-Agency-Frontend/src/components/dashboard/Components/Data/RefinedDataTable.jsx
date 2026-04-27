// ... (imports)
import React, { useMemo, useState, useCallback, useRef, useEffect } from "react";
import { Download, User, Edit, Trash2, MoreVertical, Users } from "lucide-react";
import { COLORS, TOKENS, extractLeadingNumber, isISODateString } from "../../Constants";

// ... (Icons: EditIcon, DeleteIcon, UserIcon, DownloadIcon - keep existing)
const EditIcon = ({ size = 18 }) => (
  <Edit size={size} color="#1E1E1E" strokeWidth={1.5} />
);

const DeleteIcon = ({ size = 18 }) => (
  <Trash2 size={size} color="#1E1E1E" strokeWidth={1.5} />
);

const UserIcon = ({ size = 20 }) => (
  <User size={size} color="#1E1E1E" strokeWidth={1.5} />
);

const DownloadIcon = ({ size = 20 }) => (
  <Download size={size} color="#1E1E1E" strokeWidth={1.5} />
);

const CrewIcon = ({ size = 20 }) => (
  <Users size={size} color="#1E1E1E" strokeWidth={1.5} />
);

/* ─── Status style map — CV Submission pipeline + general statuses ─────────── */
const STATUS_MAP = {
  // ── CV Submission pipeline (Pending → … → Hired / Rejected) ──────────────
  Pending: {
    bg: COLORS.warningLight,
    color: COLORS.warningDark,
    fontWeight: 500,
  },
  "Under Review": {
    bg: COLORS.amberLight,
    color: COLORS.amberDark,
    fontWeight: 500,
  },
  Interviewed: {
    bg: COLORS.purpleLight,
    color: COLORS.purpleDark,
    fontWeight: 500,
  },
  Shortlisted: {
    bg: COLORS.blueLight,
    color: COLORS.blueDark,
    fontWeight: 500,
  },
  Approved: {
    bg: COLORS.infoLight,
    color: COLORS.infoDark,
    fontWeight: 500,
  },
  Hired: {
    bg: COLORS.successLight,
    color: COLORS.successDark,
    fontWeight: 600,
  },
  Rejected: {
    bg: COLORS.errorLight,
    color: COLORS.errorDark,
    fontWeight: 500,
  },
  // ── General / document statuses ───────────────────────────────────────────
  Active: {
    bg: COLORS.successLight,
    color: COLORS.successDark,
    fontWeight: 500,
  },
  "On Site": {
    bg: COLORS.infoLight,
    color: COLORS.infoDark,
    fontWeight: 500,
  },
  INACTIVE: {
    bg: COLORS.errorLight,
    color: COLORS.errorDark,
    fontWeight: 400,
  },
  Blacklist: {
    bg: COLORS.errorLight,
    color: COLORS.errorDark,
    fontWeight: 500,
  },
  Paid: {
    bg: COLORS.successLight,
    color: COLORS.successDark,
    fontWeight: 400,
  },
  Overdue: {
    bg: COLORS.amberLight,
    color: COLORS.amberDark,
    fontWeight: 400,
  },
  Cancelled: {
    bg: COLORS.errorLight,
    color: COLORS.errorDark,
    fontWeight: 400,
  },
};


/* ---------- Main FigmaDataTable ---------- */
export function RefinedDataTable({
  data = [],
  columns = [],
  rowKey = "id",
  className = "",
  style = {},
  initialSort = null,
  pageSize = 10,
  initialPage = 1,
  actions = ["User", "Edit", "Delete", "Download"], // which action icons to show
  onSort = null,
  onRowClick = null,
  onPageChange = null,
  emptyState = null,
  scale = 1,
  styleOverrides = {},
  loading = false,
}) {
  const [sort, setSort] = useState(initialSort);
  const [page, setPage] = useState(initialPage);
  const [activeActionRowId, setActiveActionRowId] = useState(null);
  const [isScrolledEnd, setIsScrolledEnd] = useState(false);

  const scrollContainerRef = useRef(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = () => setActiveActionRowId(null);
    window.addEventListener("click", handleClickOutside);
    return () => window.removeEventListener("click", handleClickOutside);
  }, []);

  // Scroll detection for sticky shadow
  const handleScroll = useCallback(() => {
    if (scrollContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current;
      // Check if we are close to the end (within 5px tolerance)
      const isEnd = scrollWidth - clientWidth - scrollLeft < 5;
      setIsScrolledEnd(isEnd);
    }
  }, []);

  // Check scroll state on mount/resize
  useEffect(() => {
    handleScroll();
    window.addEventListener('resize', handleScroll);
    return () => window.removeEventListener('resize', handleScroll);
  }, [handleScroll, data]);

  const tokens = {
    // Removed containerPadding to allow full-width headers
    // columnGap: styleOverrides.columnGap ?? 0,
    columnGap: 0,
    headerFontSize: styleOverrides.headerFontSize ?? 14, // Slightly smaller for dense tables
    headerColor: styleOverrides.headerColor ?? COLORS.primary,
    headerHeight: styleOverrides.headerHeight ?? 48, // Taller header bar
    rowHeight: styleOverrides.rowHeight ?? 56, // Relaxed rows
    avatarSize: styleOverrides.avatarSize ?? 40,
    actionBtnW: styleOverrides.actionBtnW ?? 38,
    actionBtnH: styleOverrides.actionBtnH ?? 36,
    statusWidth: styleOverrides.statusWidth ?? 122,
    statusHeight: styleOverrides.statusHeight ?? 30,
  };

  const columnGap = Math.round(tokens.columnGap * scale);
  const headerFontSize = Math.round(tokens.headerFontSize * scale);
  const headerHeight = Math.round(tokens.headerHeight * scale);
  const rowHeight = Math.round(tokens.rowHeight * scale);
  const avatarSize = Math.round(tokens.avatarSize * scale);
  const statusWidth = Math.round(tokens.statusWidth * scale);
  const statusHeight = Math.round(tokens.statusHeight * scale);

  const sorted = useMemo(() => {
    if (!sort?.key) return data;
    const col = columns.find((c) => c.key === sort.key);
    const dir = sort.direction === "desc" ? -1 : 1;
    return [...data].sort((a, b) => {
      const va = col && col.sortValue ? col.sortValue(a) : a[sort.key];
      const vb = col && col.sortValue ? col.sortValue(b) : b[sort.key];
      if (va == null) return 1 * dir;
      if (vb == null) return -1 * dir;
      if (isISODateString(va) && isISODateString(vb)) {
        const dateA = new Date(va);
        const dateB = new Date(vb);
        return (dateA - dateB) * dir;
      }
      const na = extractLeadingNumber(va);
      const nb = extractLeadingNumber(vb);
      if (typeof na === "number" && typeof nb === "number")
        return (na - nb) * dir;
      return String(va).localeCompare(String(vb)) * dir;
    });
  }, [data, sort, columns]);

  const total = sorted.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const currentPage = Math.min(page, totalPages);
  const pageData = sorted.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  const handleHeaderClick = useCallback(
    (key, sortable) => {
      if (!sortable || loading) return;
      if (!sort || sort.key !== key) {
        setSort({ key, direction: "asc" });
        onSort && onSort({ key, direction: "asc" });
        return;
      }
      if (sort.direction === "asc") {
        setSort({ key, direction: "desc" });
        onSort && onSort({ key, direction: "desc" });
        return;
      }
      setSort(null);
      onSort && onSort(null);
    },
    [sort, loading, onSort]
  );

  const handlePageChange = (newPage) => {
    setPage(newPage);
    onPageChange && onPageChange(newPage);
  };

  if (!data || data.length === 0) {
    return emptyState ? (
      <div className={className} style={{ ...style }}>
        {emptyState}
      </div>
    ) : (
      <div className={className} style={{ ...style }}>
        <div
          style={{
            width: "100%",
            height: Math.round(80 * scale),
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: COLORS.lightText,
          }}
        >
          No data available.
        </div>
      </div>
    );
  }

  const containerStyle = {
    display: "flex",
    flexDirection: "row",
    gap: `${columnGap}px`,
    padding: 0, // removed padding for full-width header
    backgroundColor: COLORS.white,
    boxShadow: TOKENS.shadow.xs,
    borderRadius: `${Math.round(TOKENS.borderRadius.lg * scale)}px`,
    overflowX: "auto",
    minHeight: `${Math.round(379 * scale)}px`,
    width: style.width || "100%",
    opacity: loading ? 0.6 : 1,
    transition: "all 0.2s ease",
    ...style,
  };

  // Header style - flat, no bottom margin
  const thStyleBase = {
    height: `${headerHeight}px`,
    fontSize: `${headerFontSize}px`,
    fontWeight: 600,
    color: COLORS.white,
    backgroundColor: COLORS.primary,
    fontFamily: "'Poppins', sans-serif",
    display: "flex",
    alignItems: "center",
    padding: `0 ${Math.round(16 * scale)}px`,
    marginBottom: 0, // Joined with rows
    cursor: "pointer",
    userSelect: "none",
    whiteSpace: "nowrap",
  };

  const cellTextBase = {
    fontSize: `${Math.round(14 * scale)}px`,
    fontWeight: 400,
    color: COLORS.darkText,
    fontFamily: "'Inter', sans-serif",
    width: "100%",
  };

  return (
    <>
      <div
        style={containerStyle}
        className={`refined-table-root ${className}`}
        ref={scrollContainerRef}
        onScroll={handleScroll}
      >
        {/* Desktop Table View */}
        <div
          style={{
            display: "flex",
            width: "100%",
            minWidth: "100%", // ensure it fills container
            gap: `${columnGap}px`,
            overflow: "visible",
          }}
        >
          {columns.map((col, colIndex) => {
            const isActions = col.isActions;
            // Dynamic sizing logic:
            // Actions: Fixed width, no grow/shrink
            // Others: Flex grow 1, shrink 1, with a min-width to trigger scroll if needed
            const flexBasis = isActions ? "48px" : (col.width ? `${col.width}px` : "auto");
            const flexGrow = isActions ? 0 : 1;
            const flexShrink = isActions ? 0 : 1;
            const minWidth = isActions ? "48px" : (col.width ? `${col.width}px` : "150px");

            const isFirst = colIndex === 0;
            const isLast = colIndex === columns.length - 1;

            return (
              <div
                key={col.key || colIndex}
                style={{
                  flex: `${flexGrow} ${flexShrink} ${flexBasis}`,
                  minWidth: minWidth,
                  display: "flex",
                  flexDirection: "column",
                  ...(isActions && {
                    position: "sticky",
                    right: 0,
                    zIndex: 10,
                    backgroundColor: COLORS.white,
                    boxShadow: !isScrolledEnd ? "-4px 0 12px rgba(0,0,0,0.05)" : "none",
                  }),
                }}
              >
                {/* Header */}
                <div
                  style={{
                    ...thStyleBase,
                    justifyContent: col.headerAlign || "flex-start",
                    textAlign: col.headerTextAlign || "left",
                    paddingLeft: isFirst ? `${Math.round(24 * scale)}px` : thStyleBase.paddingLeft, // More padding for first col
                    // Continuous header border radius logic
                    // borderTopLeftRadius: isFirst ? `${Math.round(8 * scale)}px` : "0",
                    // borderTopRightRadius: isLast ? `${Math.round(8 * scale)}px` : "0",
                    // padding: isActions ? 0 : thStyleBase.padding, 
                    // REVERTED padding removal for Actions to keep header bar consistent height/look, 
                    // but empty content.
                    padding: isActions ? 0 : (isFirst ? `0 16px 0 24px` : `0 16px`),
                  }}
                  onClick={() => handleHeaderClick(col.key, col.sortable)}
                >
                  {!isActions && (
                    <>
                      {col.title}
                      {col.sortable && sort?.key === col.key && (
                        <span style={{ marginLeft: "4px" }}>
                          {sort.direction === "asc" ? "↑" : "↓"}
                        </span>
                      )}
                    </>
                  )}
                </div>

                {/* Cells */}
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                  }}
                >
                  {pageData.map((row, rIdx) => {
                    const value = row[col.key];
                    const cellContent = col.render
                      ? col.render(value, row)
                      : value;

                    const cellStyle = {
                      display: "flex",
                      alignItems: "center",
                      height: `${rowHeight}px`,
                      padding: isFirst ? `0 16px 0 24px` : `0 16px`, // Match header padding logic
                      borderBottom: `1px solid ${COLORS.borderColor}`, // Separator lines
                      backgroundColor: isActions ? "inherit" : "transparent",
                    };

                    // Avatar + name layout
                    if (colIndex === 0 && col.showAvatar) {
                      return (
                        <div
                          key={row[rowKey] || rIdx}
                          style={{
                            ...cellStyle,
                            gap: `${Math.round(12 * scale)}px`,
                            cursor: onRowClick ? "pointer" : "default",
                          }}
                          onClick={() => onRowClick && onRowClick(row)}
                        >
                          {row.avatar ? (
                            <img
                              src={row.avatar}
                              alt={row.name || ""}
                              style={{
                                width: `${avatarSize}px`,
                                height: `${avatarSize}px`,
                                borderRadius: "50%",
                                objectFit: "cover",
                                flexShrink: 0,
                              }}
                            />
                          ) : (
                            <div
                              style={{
                                width: `${avatarSize}px`,
                                height: `${avatarSize}px`,
                                borderRadius: "50%",
                                background: COLORS.cardBg,
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                flexShrink: 0,
                              }}
                            >
                              <svg
                                width={Math.round(avatarSize * 0.6)}
                                height={Math.round(avatarSize * 0.6)}
                                viewBox="0 0 24 24"
                              >
                                <circle cx="12" cy="8" r="3.2" fill="#ddd" />
                                <path
                                  d="M4 20c0-4 4-6 8-6s8 2 8 6"
                                  fill="#ddd"
                                />
                              </svg>
                            </div>
                          )}
                          <div style={{ ...cellTextBase }}>{cellContent}</div>
                        </div>
                      );
                    }

                    // Status column
                    if (col.isStatus) {
                      const st = STATUS_MAP[value] || {
                        bg: "rgba(0,0,0,0.06)",
                        color: COLORS.darkText,
                      };
                      return (
                        <div
                          key={row[rowKey] || rIdx}
                          style={{
                            ...cellStyle,
                            justifyContent: "flex-start", // Align left like others? Or center? usually status is left or center.
                          }}
                        >
                          <div
                            style={{
                              background: st.bg,
                              color: st.color,
                              borderRadius: Math.round(100 * scale) + "px",
                              width: `${statusWidth}px`,
                              height: `${statusHeight}px`,
                              display: "inline-flex",
                              alignItems: "center",
                              justifyContent: "center",
                              fontFamily: "'Poppins', sans-serif",
                              fontWeight: st.fontWeight,
                              fontSize: `${Math.round(12 * scale)}px`,
                            }}
                          >
                            {value}
                          </div>
                        </div>
                      );
                    }

                    // Actions column
                    if (col.isActions) {
                      const isActive = activeActionRowId === (row[rowKey] || rIdx);

                      return (
                        <div
                          key={row[rowKey] || rIdx}
                          style={{
                            ...cellStyle,
                            justifyContent: "center",
                            padding: 0, // Center actions properly
                            position: "relative",
                          }}
                        >
                          {/* Meatballs Menu Trigger */}
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setActiveActionRowId(isActive ? null : (row[rowKey] || rIdx));
                            }}
                            style={{
                              background: "transparent",
                              border: "none",
                              cursor: "pointer",
                              padding: "4px",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              color: COLORS.iconGray,
                            }}
                          >
                            <MoreVertical size={Math.round(20 * scale)} />
                          </button>

                          {/* Dropdown Menu */}
                          {isActive && (
                            <div
                              style={{
                                position: "absolute",
                                top: "70%",
                                right: "100%", // Open to the left
                                width: "160px",
                                backgroundColor: "white",
                                borderRadius: "8px",
                                boxShadow: "0px 4px 12px rgba(0,0,0,0.15)",
                                zIndex: 100,
                                padding: "8px 0",
                                border: `1px solid ${COLORS.borderColor}`,
                                flexDirection: "column",
                                display: "flex",
                                marginRight: "8px",
                              }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              {col.render ? col.render(row) : (
                                <>
                                  {actions.includes("User") && (
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        col.onUser && col.onUser(row);
                                        setActiveActionRowId(null);
                                      }}
                                      style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: "12px",
                                        padding: "10px 16px",
                                        border: "none",
                                        background: "transparent",
                                        cursor: "pointer",
                                        width: "100%",
                                        textAlign: "left",
                                        fontSize: `${Math.round(14 * scale)}px`,
                                        color: COLORS.darkText,
                                      }}
                                      onMouseEnter={(e) => e.currentTarget.style.background = COLORS.cardBg}
                                      onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                                    >
                                      <UserIcon size={16} /> View Profile
                                    </button>
                                  )}

                                  {actions.includes("Edit") && (
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        col.onEdit && col.onEdit(row);
                                        setActiveActionRowId(null);
                                      }}
                                      style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: "12px",
                                        padding: "10px 16px",
                                        border: "none",
                                        background: "transparent",
                                        cursor: "pointer",
                                        width: "100%",
                                        textAlign: "left",
                                        fontSize: `${Math.round(14 * scale)}px`,
                                        color: COLORS.darkText,
                                      }}
                                      onMouseEnter={(e) => e.currentTarget.style.background = COLORS.cardBg}
                                      onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                                    >
                                      <EditIcon size={16} /> Edit
                                    </button>
                                  )}

                                  {actions.includes("Download") && (
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        col.onDownload && col.onDownload(row);
                                        setActiveActionRowId(null);
                                      }}
                                      style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: "12px",
                                        padding: "10px 16px",
                                        border: "none",
                                        background: "transparent",
                                        cursor: "pointer",
                                        width: "100%",
                                        textAlign: "left",
                                        fontSize: `${Math.round(14 * scale)}px`,
                                        color: COLORS.darkText,
                                      }}
                                      onMouseEnter={(e) => e.currentTarget.style.background = COLORS.cardBg}
                                      onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                                    >
                                      <DownloadIcon size={16} /> Download
                                    </button>
                                  )}

                                  {actions.includes("Delete") && (
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        col.onDelete && col.onDelete(row.id || row[rowKey]);
                                        setActiveActionRowId(null);
                                      }}
                                      style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: "12px",
                                        padding: "10px 16px",
                                        border: "none",
                                        background: "transparent",
                                        cursor: "pointer",
                                        width: "100%",
                                        textAlign: "left",
                                        fontSize: `${Math.round(14 * scale)}px`,
                                        color: COLORS.errorDark,
                                      }}
                                      onMouseEnter={(e) => e.currentTarget.style.background = "#FEE2E2"}
                                      onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                                    >
                                      <DeleteIcon size={16} /> Delete
                                    </button>
                                  )}

                                  {col.onCrew && (
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        col.onCrew(row);
                                        setActiveActionRowId(null);
                                      }}
                                      style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: "12px",
                                        padding: "10px 16px",
                                        border: "none",
                                        background: "transparent",
                                        cursor: "pointer",
                                        width: "100%",
                                        textAlign: "left",
                                        fontSize: `${Math.round(14 * scale)}px`,
                                        color: COLORS.darkText,
                                      }}
                                      onMouseEnter={(e) => e.currentTarget.style.background = COLORS.cardBg}
                                      onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                                    >
                                      <CrewIcon size={16} /> Manage Crew
                                    </button>
                                  )}

                                  {col.onRank && (
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        col.onRank(row);
                                        setActiveActionRowId(null);
                                      }}
                                      style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: "12px",
                                        padding: "10px 16px",
                                        border: "none",
                                        background: "transparent",
                                        cursor: "pointer",
                                        width: "100%",
                                        textAlign: "left",
                                        fontSize: `${Math.round(14 * scale)}px`,
                                        color: "#6366F1",
                                      }}
                                      onMouseEnter={(e) => e.currentTarget.style.background = "#EEF2FF"}
                                      onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                                    >
                                      <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="#6366F1" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
                                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/><path d="M12 8v8M8 12l4-4 4 4"/>
                                      </svg>
                                       Manage Ranks
                                    </button>
                                  )}
                                </>
                              )}
                            </div>
                          )}
                        </div>
                      );
                    }

                    // Default text cell
                    return (
                      <div
                        key={row[rowKey] || rIdx}
                        style={{
                          ...cellStyle,
                        }}
                        onClick={() => onRowClick && onRowClick(row)}
                      >
                        <div
                          style={{
                            ...cellTextBase,
                            textAlign: col.textAlign || "left",
                          }}
                        >
                          {cellContent}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Pagination */}
      <div
        style={{
          marginTop: Math.round(12 * scale),
          display: "flex",
          justifyContent: "flex-end",
          gap: Math.round(8 * scale),
        }}
      >
        <button
          onClick={() => handlePageChange(Math.max(1, currentPage - 1))}
          disabled={currentPage <= 1 || loading}
          style={{
            padding: `${Math.round(6 * scale)}px ${Math.round(10 * scale)}px`,
            fontSize: `${Math.round(13 * scale)}px`,
            borderRadius: Math.round(8 * scale),
            border: `1px solid ${COLORS.borderColor}`,
            background: COLORS.white,
            cursor: currentPage <= 1 || loading ? "not-allowed" : "pointer",
            opacity: currentPage <= 1 ? 0.5 : 1,
          }}
        >
          Prev
        </button>

        <div style={{ display: "flex", gap: Math.round(6 * scale) }}>
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
            <button
              key={p}
              onClick={() => handlePageChange(p)}
              style={{
                padding: `${Math.round(6 * scale)}px ${Math.round(
                  10 * scale
                )}px`,
                fontSize: `${Math.round(13 * scale)}px`,
                borderRadius: Math.round(8 * scale),
                border: `1px solid ${p === currentPage ? COLORS.secondary : COLORS.borderColor
                  }`,
                background: p === currentPage ? COLORS.secondary : COLORS.white,
                color: p === currentPage ? COLORS.white : COLORS.darkText,
                cursor: "pointer",
              }}
              aria-current={p === currentPage ? "page" : undefined}
            >
              {p}
            </button>
          ))}
        </div>

        <button
          onClick={() =>
            handlePageChange(Math.min(totalPages, currentPage + 1))
          }
          disabled={currentPage >= totalPages || loading}
          style={{
            padding: `${Math.round(6 * scale)}px ${Math.round(10 * scale)}px`,
            fontSize: `${Math.round(13 * scale)}px`,
            borderRadius: Math.round(8 * scale),
            border: `1px solid ${COLORS.borderColor}`,
            background: COLORS.white,
            cursor:
              currentPage >= totalPages || loading ? "not-allowed" : "pointer",
            opacity: currentPage >= totalPages ? 0.5 : 1,
          }}
        >
          Next
        </button>
      </div>
    </>
  );
}

/* ---------- Pagination helper component ---------- */
function Pagination({
  page = 1,
  pageSize = 10,
  total = 0,
  onChange = () => { },
  scale = 1,
}) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const pages = [];
  for (let i = 1; i <= totalPages; i++) pages.push(i);

  const btnPaddingX = Math.round(10 * scale);
  const btnPaddingY = Math.round(6 * scale);
  const btnFontSize = Math.round(13 * scale);
  const baseBtn = {
    padding: `${btnPaddingY}px ${btnPaddingX}px`,
    fontSize: `${btnFontSize}px`,
    borderRadius: Math.round(8 * scale),
    border: "1px solid rgba(229,231,235,1)",
    background: "#fff",
    cursor: "pointer",
  };
  const activeBtn = {
    ...baseBtn,
    background: "#056BB6",
    color: "#fff",
    border: "1px solid rgba(5,107,182,1)",
  };

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: Math.round(8 * scale),
      }}
    >
      <button
        style={baseBtn}
        onClick={() => onChange(Math.max(1, page - 1))}
        disabled={page <= 1}
      >
        Prev
      </button>
      <div style={{ display: "flex", gap: Math.round(6 * scale) }}>
        {pages.map((p) => (
          <button
            key={p}
            onClick={() => onChange(p)}
            style={p === page ? activeBtn : baseBtn}
            aria-current={p === page ? "page" : undefined}
          >
            {p}
          </button>
        ))}
      </div>
      <button
        style={baseBtn}
        onClick={() => onChange(Math.min(totalPages, page + 1))}
        disabled={page >= totalPages}
      >
        Next
      </button>
    </div>
  );
}
