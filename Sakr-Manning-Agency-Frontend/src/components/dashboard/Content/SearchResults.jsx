// Content/SearchResults.jsx
// Global search results page
// Shows results from all pages grouped by category

import React, { useState, useEffect } from "react";
import { COLORS } from "../Constants";
import {
  generateAllPageStyles,
  getMainContainerStyles,
  getPageTitleStyles,
} from "../Styles/cssClasses";
import { STYLE_TOKENS, getScaledValue } from "../Styles/globalStyles";
import SearchResultCard from "../Components/Common/SearchResultsCard";
import useSearch from "../hooks/useSearch";
import useGlobalSearch from "../hooks/useGlobalSearch";

/**
 * SearchResults Page Component
 *
 * Displays global search results grouped by category
 * Features:
 * - Category tabs for filtering
 * - Result count per category
 * - Click result to navigate to page
 * - Empty state when no results
 */
export function SearchResults({
  scale = 1,
  isMobile = false,
  allData = {},
  onNavigate,
}) {
  const { searchQuery } = useSearch();
  const { results, totalResults, hasResults, categoryCounts } = useGlobalSearch(
    searchQuery,
    allData
  );

  // Active category filter
  const [activeCategory, setActiveCategory] = useState("all");

  // Update active category when results change
  useEffect(() => {
    // If current category has no results, switch to first category with results
    if (activeCategory !== "all" && categoryCounts[activeCategory] === 0) {
      const firstCategoryWithResults = Object.keys(categoryCounts).find(
        (cat) => categoryCounts[cat] > 0
      );
      if (firstCategoryWithResults) {
        setActiveCategory(firstCategoryWithResults);
      } else {
        setActiveCategory("all");
      }
    }
  }, [categoryCounts, activeCategory]);

  // Handle result click - navigate to relevant page
  const handleResultClick = (result, category) => {
    console.log("Navigate to:", category, result);

    // Map category to page name
    const pageMap = {
      cvs: "cvs",
      companies: "company",
      ships: "company",
      users: "users",
      interviews: "interviews",
      documents: "documents",
      finance: "finance",
    };

    const page = pageMap[category];
    if (page && onNavigate) {
      onNavigate(page, result.id);
    }
  };

  // Category configurations
  const categories = [
    { key: "all", label: "All Results", count: totalResults },
    { key: "cvs", label: "CVs", count: categoryCounts.cvs },
    { key: "companies", label: "Companies", count: categoryCounts.companies },
    { key: "ships", label: "Ships", count: categoryCounts.ships },
    { key: "users", label: "Users", count: categoryCounts.users },
    {
      key: "interviews",
      label: "Interviews",
      count: categoryCounts.interviews,
    },
    { key: "documents", label: "Documents", count: categoryCounts.documents },
    { key: "finance", label: "Finance", count: categoryCounts.finance },
  ];

  // Get filtered results based on active category
  const getFilteredResults = () => {
    if (activeCategory === "all") {
      return results;
    }
    return { [activeCategory]: results[activeCategory] };
  };

  const filteredResults = getFilteredResults();

  const headerHeight = Math.round(101 * scale);
  //   const contentPadding = Math.round(32 * scale);
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
          {searchQuery && `Showing results for "${searchQuery}"`}
          {totalResults > 0 &&
            ` • ${totalResults} result${totalResults !== 1 ? "s" : ""} found`}
        </p>
      </div>

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
            disabled={cat.count === 0}
            style={{
              padding: `${getScaledValue(10, scale)}px ${getScaledValue(
                20,
                scale
              )}px`,
              backgroundColor:
                activeCategory === cat.key
                  ? STYLE_TOKENS.colors.primary
                  : STYLE_TOKENS.colors.white,
              color:
                activeCategory === cat.key
                  ? STYLE_TOKENS.colors.white
                  : cat.count === 0
                  ? STYLE_TOKENS.colors.lightText
                  : STYLE_TOKENS.colors.darkText,
              border: `1px solid ${
                activeCategory === cat.key
                  ? STYLE_TOKENS.colors.primary
                  : STYLE_TOKENS.colors.borderColor
              }`,
              borderRadius: `${getScaledValue(8, scale)}px`,
              fontSize: `${getScaledValue(14, scale)}px`,
              fontWeight: activeCategory === cat.key ? 600 : 400,
              fontFamily: STYLE_TOKENS.fonts.heading,
              cursor: cat.count === 0 ? "not-allowed" : "pointer",
              transition: STYLE_TOKENS.transition.normal,
              display: "flex",
              alignItems: "center",
              gap: `${getScaledValue(8, scale)}px`,
              whiteSpace: "nowrap",
              opacity: cat.count === 0 ? 0.5 : 1,
            }}
            onMouseEnter={(e) => {
              if (cat.count > 0 && activeCategory !== cat.key) {
                e.currentTarget.style.backgroundColor =
                  STYLE_TOKENS.colors.hoverBackground;
              }
            }}
            onMouseLeave={(e) => {
              if (activeCategory !== cat.key) {
                e.currentTarget.style.backgroundColor =
                  STYLE_TOKENS.colors.white;
              }
            }}
          >
            {cat.label}
            {cat.count > 0 && (
              <span
                style={{
                  padding: `${getScaledValue(2, scale)}px ${getScaledValue(
                    8,
                    scale
                  )}px`,
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

      {/* Results Display */}
      {hasResults ? (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: `${sectionGap}px`,
          }}
        >
          {Object.entries(filteredResults).map(([category, items]) => {
            if (!items || items.length === 0) return null;

            return (
              <div key={category}>
                {/* Category Header (only show if "all" is selected) */}
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
                    {category} ({items.length})
                  </h2>
                )}

                {/* Results Grid */}
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: isMobile
                      ? "1fr"
                      : `repeat(auto-fill, minmax(${getScaledValue(
                          350,
                          scale
                        )}px, 1fr))`,
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
        // Empty State
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: `${getScaledValue(80, scale)}px ${getScaledValue(
              20,
              scale
            )}px`,
            backgroundColor: STYLE_TOKENS.colors.white,
            borderRadius: `${getScaledValue(22, scale)}px`,
            boxShadow: STYLE_TOKENS.shadow.sm,
          }}
        >
          <div
            style={{
              fontSize: `${getScaledValue(64, scale)}px`,
              marginBottom: `${getScaledValue(16, scale)}px`,
            }}
          >
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
            No Results Found
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
              ? `No results found for "${searchQuery}". Try a different search term.`
              : "Enter a search term to find CVs, companies, users, and more."}
          </p>
        </div>
      )}
    </main>
  );
}
