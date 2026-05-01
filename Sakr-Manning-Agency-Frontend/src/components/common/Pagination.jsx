import React, { useMemo } from "react";

/**
 * Enhanced Pagination Component
 * Supports server-side pagination with 25 records per page
 * Features: truncated page numbers, info display, modern styling
 */
export default function Pagination({
    page = 1,
    pageSize = 25,
    total = 0,
    onChange = () => { },
    scale = 1,
    showInfo = true,
    siblingCount = 1,
}) {
    const totalPages = Math.max(1, Math.ceil(total / pageSize));

    // Calculate the range of items being displayed
    const startItem = total === 0 ? 0 : (page - 1) * pageSize + 1;
    const endItem = Math.min(page * pageSize, total);

    // Generate page numbers with ellipsis for large page counts
    const pageNumbers = useMemo(() => {
        const range = (start, end) => {
            const result = [];
            for (let i = start; i <= end; i++) result.push(i);
            return result;
        };

        // If total pages is small, show all
        if (totalPages <= 7) {
            return range(1, totalPages);
        }

        const leftSiblingIndex = Math.max(page - siblingCount, 1);
        const rightSiblingIndex = Math.min(page + siblingCount, totalPages);

        const shouldShowLeftDots = leftSiblingIndex > 2;
        const shouldShowRightDots = rightSiblingIndex < totalPages - 1;

        if (!shouldShowLeftDots && shouldShowRightDots) {
            // Show first 5 pages + ellipsis + last page
            return [...range(1, 5), "...", totalPages];
        }

        if (shouldShowLeftDots && !shouldShowRightDots) {
            // Show first page + ellipsis + last 5 pages
            return [1, "...", ...range(totalPages - 4, totalPages)];
        }

        if (shouldShowLeftDots && shouldShowRightDots) {
            // Show first + ellipsis + middle + ellipsis + last
            return [
                1,
                "...",
                ...range(leftSiblingIndex, rightSiblingIndex),
                "...",
                totalPages,
            ];
        }

        return range(1, totalPages);
    }, [page, totalPages, siblingCount]);

    // Styles
    const btnPaddingX = Math.round(12 * scale);
    const btnPaddingY = Math.round(8 * scale);
    const btnFontSize = Math.round(14 * scale);
    const gap = Math.round(6 * scale);

    const baseBtn = {
        padding: `${btnPaddingY}px ${btnPaddingX}px`,
        fontSize: `${btnFontSize}px`,
        fontFamily: "'Poppins', sans-serif",
        fontWeight: 500,
        borderRadius: Math.round(8 * scale),
        border: "1px solid #E5E7EB",
        background: "#fff",
        color: "#374151",
        cursor: "pointer",
        transition: "all 0.2s ease",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        minWidth: Math.round(40 * scale),
        height: Math.round(40 * scale),
    };

    const activeBtn = {
        ...baseBtn,
        background: "linear-gradient(135deg, #056BB6 0%, #0284C7 100%)",
        color: "#fff",
        border: "1px solid #056BB6",
        boxShadow: "0 2px 8px rgba(5, 107, 182, 0.3)",
    };

    const disabledBtn = {
        ...baseBtn,
        opacity: 0.5,
        cursor: "not-allowed",
        background: "#F9FAFB",
    };

    const navBtn = {
        ...baseBtn,
        padding: `${btnPaddingY}px ${Math.round(16 * scale)}px`,
        gap: Math.round(6 * scale),
    };

    const ellipsisStyle = {
        ...baseBtn,
        border: "none",
        background: "transparent",
        cursor: "default",
        color: "#9CA3AF",
        minWidth: Math.round(32 * scale),
    };

    const infoStyle = {
        fontSize: Math.round(14 * scale),
        fontFamily: "'Inter', sans-serif",
        color: "#6B7280",
        marginRight: Math.round(16 * scale),
    };

    // Arrow SVG components
    const ChevronLeft = () => (
        <svg
            width={Math.round(16 * scale)}
            height={Math.round(16 * scale)}
            viewBox="0 0 16 16"
            fill="none"
        >
            <path
                d="M10 12L6 8L10 4"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
            />
        </svg>
    );

    const ChevronRight = () => (
        <svg
            width={Math.round(16 * scale)}
            height={Math.round(16 * scale)}
            viewBox="0 0 16 16"
            fill="none"
        >
            <path
                d="M6 4L10 8L6 12"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
            />
        </svg>
    );

    return (
        <div
            style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: Math.round(16 * scale),
                padding: `${Math.round(12 * scale)}px 0`,
            }}
        >
            {/* Info Text */}
            {showInfo && (
                <div style={infoStyle}>
                    {total === 0 ? (
                        "No records"
                    ) : (
                        <>
                            Showing <strong>{startItem}</strong> - <strong>{endItem}</strong> of{" "}
                            <strong>{total}</strong> records
                        </>
                    )}
                </div>
            )}

            {/* Pagination Controls */}
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    gap: gap,
                }}
            >
                {/* Previous Button */}
                <button
                    style={page <= 1 ? disabledBtn : navBtn}
                    onClick={() => page > 1 && onChange(page - 1)}
                    disabled={page <= 1}
                    aria-label="Previous page"
                    onMouseEnter={(e) => {
                        if (page > 1) {
                            e.currentTarget.style.background = "#F3F4F6";
                            e.currentTarget.style.borderColor = "#D1D5DB";
                        }
                    }}
                    onMouseLeave={(e) => {
                        if (page > 1) {
                            e.currentTarget.style.background = "#fff";
                            e.currentTarget.style.borderColor = "#E5E7EB";
                        }
                    }}
                >
                    <ChevronLeft />
                    <span>Prev</span>
                </button>

                {/* Page Numbers */}
                <div style={{ display: "flex", gap: gap }}>
                    {pageNumbers.map((p, idx) =>
                        p === "..." ? (
                            <span key={`ellipsis-${idx}`} style={ellipsisStyle}>
                                •••
                            </span>
                        ) : (
                            <button
                                key={p}
                                onClick={() => onChange(p)}
                                style={p === page ? activeBtn : baseBtn}
                                aria-current={p === page ? "page" : undefined}
                                onMouseEnter={(e) => {
                                    if (p !== page) {
                                        e.currentTarget.style.background = "#F3F4F6";
                                        e.currentTarget.style.borderColor = "#D1D5DB";
                                    }
                                }}
                                onMouseLeave={(e) => {
                                    if (p !== page) {
                                        e.currentTarget.style.background = "#fff";
                                        e.currentTarget.style.borderColor = "#E5E7EB";
                                    }
                                }}
                            >
                                {p}
                            </button>
                        )
                    )}
                </div>

                {/* Next Button */}
                <button
                    style={page >= totalPages ? disabledBtn : navBtn}
                    onClick={() => page < totalPages && onChange(page + 1)}
                    disabled={page >= totalPages}
                    aria-label="Next page"
                    onMouseEnter={(e) => {
                        if (page < totalPages) {
                            e.currentTarget.style.background = "#F3F4F6";
                            e.currentTarget.style.borderColor = "#D1D5DB";
                        }
                    }}
                    onMouseLeave={(e) => {
                        if (page < totalPages) {
                            e.currentTarget.style.background = "#fff";
                            e.currentTarget.style.borderColor = "#E5E7EB";
                        }
                    }}
                >
                    <span>Next</span>
                    <ChevronRight />
                </button>
            </div>
        </div>
    );
}
