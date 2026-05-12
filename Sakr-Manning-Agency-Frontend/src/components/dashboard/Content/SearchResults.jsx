// Content/SearchResults.jsx
// Global search results page — powered by /api/global-search/?q=
// Receives pre-fetched backend results from DashboardApp

import React, { useState, useEffect, useMemo } from "react";
import { COLORS } from "../Constants";
import {
  generateAllPageStyles,
  getMainContainerStyles,
  getPageTitleStyles,
} from "../Styles/cssClasses";
import { STYLE_TOKENS, getScaledValue } from "../Styles/globalStyles";
import SearchResultCard from "../Components/Common/SearchResultsCard";

/**
 * SearchResults Page Component
 *
 * Displays global search results grouped by category.
 * Results come from the backend /api/global-search/?q= endpoint,
 * fetched in DashboardApp and passed down as `backendResults`.
 *
 * Backend response shape (may vary — we normalise below):
 * { users: [], ships: [], companies: [], cv_submissions: [], contracts: [], ... }
 */
export function SearchResults({
  scale = 1,
  isMobile = false,
  searchQuery = "",
  backendResults = {},
  loading = false,
  onNavigate,
}) {
  // Normalise the backend payload into a consistent shape.
  // The backend key names may differ slightly from our display labels.
  const normalisedResults = useMemo(() => ({
    users: backendResults.users || [],
    companies: backendResults.companies || [],
    ships: backendResults.ships || [],
    cvs: backendResults.cvs || [],
    contracts: backendResults.contracts || [],
  }), [backendResults]);

  const totalResults = useMemo(
    () => Object.values(normalisedResults).reduce((sum, arr) => sum + arr.length, 0),
    [normalisedResults]
  );

  const hasResults = totalResults > 0;

  // Category filter tab
  const [activeCategory, setActiveCategory] = useState("all");

  // Reset to "all" whenever a new search is performed
  useEffect(() => {
    setActiveCategory("all");
  }, [searchQuery]);

  // Category display config
  const categories = [
    { key: "all", label: "All Results", count: totalResults },
    { key: "users", label: "Seafarers", count: normalisedResults.users.length },
    { key: "companies", label: "Companies", count: normalisedResults.companies.length },
    { key: "ships", label: "Ships", count: normalisedResults.ships.length },
    { key: "cvs", label: "CVs", count: normalisedResults.cvs.length },
    { key: "contracts", label: "Contracts", count: normalisedResults.contracts.length },
  ];

  // Navigate to the relevant dashboard section on result click
  const handleResultClick = (result, category) => {
    const pageMap = {
      users: "users",
      companies: "management",
      ships: "management",
      cvs: "cvs",
      contracts: "cvSubmissions",
    };
    const page = pageMap[category];
    if (page && onNavigate) onNavigate(page, result.id);
  };

  // Filtered view
  const filteredResults = useMemo(() => {
    if (activeCategory === "all") return normalisedResults;
    return { [activeCategory]: normalisedResults[activeCategory] };
  }, [activeCategory, normalisedResults]);

  const headerHeight = Math.round(101 * scale);
  const tabGap = getScaledValue(8, scale);
  const sectionGap = getScaledValue(32, scale);

  return (
    <main style={getMainContainerStyles(scale, headerHeight)}>
      <style>{generateAllPageStyles(scale)}</style>

      {/* Header */}
      <div style={{ marginBottom: `${getScaledValue(24, scale)}px` }}>
        <h1
          style={{
            ...getPageTitleStyles(scale),
            marginBottom: `${getScaledValue(8, scale)}px`,
          }}
        >
          Search Results
        </h1>
        <p
          style={{
            fontSize: `${getScaledValue(16, scale)}px`,
            color: STYLE_TOKENS.colors.lightText,
            fontFamily: STYLE_TOKENS.fonts.primary,
            margin: 0,
          }}
        >
          {loading
            ? "Searching…"
            : searchQuery
              ? `Showing results for "${searchQuery}"${hasResults ? ` • ${totalResults} result${totalResults !== 1 ? "s" : ""} found` : ""}`
              : "Enter a search term in the header to search across all sections."}
        </p>
      </div>

      {/* Loading spinner */}
      {loading && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: `${getScaledValue(80, scale)}px`,
            backgroundColor: STYLE_TOKENS.colors.white,
            borderRadius: `${getScaledValue(22, scale)}px`,
            boxShadow: STYLE_TOKENS.shadow.sm,
          }}
        >
          <div
            style={{
              width: getScaledValue(48, scale),
              height: getScaledValue(48, scale),
              border: `${getScaledValue(4, scale)}px solid rgba(0,101,175,0.15)`,
              borderTopColor: "#0065AF",
              borderRadius: "50%",
              animation: "gs-spin 0.75s linear infinite",
            }}
          />
          <style>{`@keyframes gs-spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      )}

      {!loading && (
        <>
          {/* Category Tabs */}
          <div
            style={{
              display: "flex",
              gap: `${tabGap}px`,
              marginBottom: `${getScaledValue(32, scale)}px`,
              overflowX: "auto",
              paddingBottom: `${getScaledValue(8, scale)}px`,
              scrollbarWidth: "thin",
            }}
          >
            {categories.map((cat) => (
              <button
                key={cat.key}
                onClick={() => setActiveCategory(cat.key)}
                disabled={cat.count === 0 && cat.key !== "all"}
                style={{
                  padding: `${getScaledValue(10, scale)}px ${getScaledValue(20, scale)}px`,
                  backgroundColor:
                    activeCategory === cat.key
                      ? STYLE_TOKENS.colors.primary
                      : STYLE_TOKENS.colors.white,
                  color:
                    activeCategory === cat.key
                      ? STYLE_TOKENS.colors.white
                      : cat.count === 0 && cat.key !== "all"
                        ? STYLE_TOKENS.colors.lightText
                        : STYLE_TOKENS.colors.darkText,
                  border: `1px solid ${activeCategory === cat.key
                    ? STYLE_TOKENS.colors.primary
                    : STYLE_TOKENS.colors.borderColor
                    }`,
                  borderRadius: `${getScaledValue(8, scale)}px`,
                  fontSize: `${getScaledValue(14, scale)}px`,
                  fontWeight: activeCategory === cat.key ? 600 : 400,
                  fontFamily: STYLE_TOKENS.fonts.heading,
                  cursor: cat.count === 0 && cat.key !== "all" ? "not-allowed" : "pointer",
                  transition: STYLE_TOKENS.transition.normal,
                  display: "flex",
                  alignItems: "center",
                  gap: `${getScaledValue(8, scale)}px`,
                  whiteSpace: "nowrap",
                  opacity: cat.count === 0 && cat.key !== "all" ? 0.5 : 1,
                }}
                onMouseEnter={(e) => {
                  if ((cat.count > 0 || cat.key === "all") && activeCategory !== cat.key) {
                    e.currentTarget.style.backgroundColor = STYLE_TOKENS.colors.hoverBackground;
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeCategory !== cat.key) {
                    e.currentTarget.style.backgroundColor = STYLE_TOKENS.colors.white;
                  }
                }}
              >
                {cat.label}
                {cat.count > 0 && (
                  <span
                    style={{
                      padding: `${getScaledValue(2, scale)}px ${getScaledValue(8, scale)}px`,
                      backgroundColor:
                        activeCategory === cat.key
                          ? "rgba(255, 255, 255, 0.2)"
                          : "rgba(0, 101, 175, 0.1)",
                      borderRadius: `${getScaledValue(12, scale)}px`,
                      fontSize: `${getScaledValue(12, scale)}px`,
                      fontWeight: 600,
                    }}
                  >
                    {cat.count}
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Results */}
          {hasResults ? (
            <div style={{ display: "flex", flexDirection: "column", gap: `${sectionGap}px` }}>
              {Object.entries(filteredResults).map(([category, items]) => {
                if (!items || items.length === 0) return null;
                return (
                  <div key={category}>
                    {activeCategory === "all" && (
                      <h2
                        style={{
                          fontSize: `${getScaledValue(20, scale)}px`,
                          fontWeight: 600,
                          color: STYLE_TOKENS.colors.darkText,
                          fontFamily: STYLE_TOKENS.fonts.heading,
                          marginBottom: `${getScaledValue(16, scale)}px`,
                          textTransform: "capitalize",
                        }}
                      >
                        {category.replace(/_/g, " ")} ({items.length})
                      </h2>
                    )}
                    <div
                      style={{
                        display: "grid",
                        gridTemplateColumns: isMobile
                          ? "1fr"
                          : `repeat(auto-fill, minmax(${getScaledValue(350, scale)}px, 1fr))`,
                        gap: `${getScaledValue(16, scale)}px`,
                      }}
                    >
                      {items.map((item, idx) => (
                        <SearchResultCard
                          key={item.id || idx}
                          result={item}
                          category={category}
                          query={searchQuery}
                          onClick={handleResultClick}
                          scale={scale}
                        />
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            /* Empty State */
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                padding: `${getScaledValue(80, scale)}px ${getScaledValue(20, scale)}px`,
                backgroundColor: STYLE_TOKENS.colors.white,
                borderRadius: `${getScaledValue(22, scale)}px`,
                boxShadow: STYLE_TOKENS.shadow.sm,
              }}
            >
              <div style={{ fontSize: `${getScaledValue(64, scale)}px`, marginBottom: `${getScaledValue(16, scale)}px` }}>
                🔍
              </div>
              <h3
                style={{
                  fontSize: `${getScaledValue(24, scale)}px`,
                  fontWeight: 600,
                  color: STYLE_TOKENS.colors.darkText,
                  fontFamily: STYLE_TOKENS.fonts.heading,
                  margin: 0,
                  marginBottom: `${getScaledValue(8, scale)}px`,
                }}
              >
                {searchQuery ? "No Results Found" : "Search the Platform"}
              </h3>
              <p
                style={{
                  fontSize: `${getScaledValue(16, scale)}px`,
                  color: STYLE_TOKENS.colors.lightText,
                  fontFamily: STYLE_TOKENS.fonts.primary,
                  margin: 0,
                  textAlign: "center",
                  maxWidth: `${getScaledValue(400, scale)}px`,
                }}
              >
                {searchQuery
                  ? `No results found for "${searchQuery}". Try a different search term (minimum 2 characters).`
                  : "Use the search bar in the header to find Seafarers, Companies, Ships, CV Submissions, and Contracts."}
              </p>
            </div>
          )}
        </>
      )}
    </main>
  );
}
