// Header.jsx (UPDATED)
// Added search submission functionality
// Enter key or click search icon to trigger global search

import React, { useEffect } from "react";
import { Search, Filter, Bell, Menu } from "lucide-react";
import { COLORS } from "./Constants";
import useSearch from "./hooks/useSearch";
import UserProfile from "./Components/Data/UserProfile";

export const Header = ({
  pageTitle,
  onMenuClick,
  isMobile,
  scale,
  onLogout,
  onSearchSubmit, // ✅ NEW: Callback for search submission
  user,
}) => {
  const { searchQuery, setSearchQuery } = useSearch();

  // ✅ NEW: Handle search submission
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim() && onSearchSubmit) {
      onSearchSubmit(searchQuery.trim());
    }
  };

  // ✅ NEW: Handle Enter key
  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSearchSubmit(e);
    }
  };

  useEffect(() => {
    console.log(user);
  }, [user]);

  const headerHeight = Math.round(101 * scale);
  const padding = Math.round(20 * scale);
  const titleFontSize = Math.round(24 * scale);
  const searchWidth = Math.round(220 * scale);
  const buttonSize = Math.round(40 * scale);
  // const avatarSize = Math.round(45 * scale);
  const borderRadius = Math.round(22 * scale);
  const shadow = `0px ${Math.round(2 * scale)}px ${Math.round(
    8 * scale
  )}px rgba(0, 0, 0, 0.1)`;

  const headerLeft = isMobile ? 0 : Math.round(280 * scale);
  const headerWidth = isMobile
    ? "100%"
    : `calc(100% - ${Math.round(280 * scale)}px)`;

  return (
    <header
      style={{
        position: "fixed",
        top: 0,
        left: `${headerLeft}px`,
        right: 0,
        width: headerWidth,
        height: `${headerHeight}px`,
        backgroundColor: COLORS.white,
        boxShadow: shadow,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: `${padding}px`,
        fontFamily: "Inter, sans-serif",
        zIndex: 100,
        gap: `${Math.round(20 * scale)}px`,
        borderBottomLeftRadius: `${borderRadius}px`,
        borderBottomRightRadius: `${borderRadius}px`,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: `${Math.round(20 * scale)}px`,
        }}
      >
        {isMobile && (
          <button
            onClick={onMenuClick}
            style={{
              background: "transparent",
              border: "none",
              cursor: "pointer",
              padding: `${Math.round(12 * scale)}px`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: COLORS.darkText,
            }}
          >
            <Menu size={Math.round(24 * scale)} />
          </button>
        )}
        <h1
          style={{
            fontSize: `${titleFontSize}px`,
            fontWeight: "500",
            fontFamily: "Inter, sans-serif",
            color: COLORS.darkText,
            margin: 0,
            lineHeight: `${Math.round(32 * scale)}px`,
          }}
        >
          {pageTitle}
        </h1>
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: `${Math.round(20 * scale)}px`,
          justifyContent: "flex-end",
          flex: isMobile ? 0 : 1,
        }}
      >
        {!isMobile && (
          // ✅ UPDATED: Wrapped in form for Enter key submission
          <form onSubmit={handleSearchSubmit} style={{ display: "contents" }}>
            <div
              style={{
                position: "relative",
                width: `${searchWidth}px`,
                height: `${buttonSize}px`,
              }}
            >
              <input
                type="text"
                name="search"
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                style={{
                  width: "100%",
                  height: "100%",
                  padding: `0 ${Math.round(40 * scale)}px 0 ${Math.round(
                    40 * scale
                  )}px`,
                  border: "none",
                  backgroundColor: "#F5F7FA",
                  borderRadius: `${borderRadius}px`,
                  fontSize: `${Math.round(13 * scale)}px`,
                  fontFamily: "Inter, sans-serif",
                  fontWeight: "400",
                  color: COLORS.darkText,
                  outline: "none",
                  transition: "background-color 0.2s ease",
                }}
                onFocus={(e) => {
                  e.target.style.backgroundColor = "#EEEFF2";
                }}
                onBlur={(e) => {
                  e.target.style.backgroundColor = "#F5F7FA";
                }}
              />
              {/* ✅ NEW: Clickable search icon */}
              <button
                type="submit"
                style={{
                  position: "absolute",
                  left: `${Math.round(14 * scale)}px`,
                  top: "50%",
                  transform: "translateY(-50%)",
                  background: "none",
                  border: "none",
                  padding: 0,
                  cursor: searchQuery.trim() ? "pointer" : "default",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  transition: "opacity 0.2s ease",
                }}
                onMouseEnter={(e) => {
                  if (searchQuery.trim()) {
                    e.currentTarget.style.opacity = "0.7";
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.opacity = "1";
                }}
                disabled={!searchQuery.trim()}
                title={searchQuery.trim() ? "Search" : ""}
              >
                <Search
                  size={Math.round(16 * scale)}
                  color={searchQuery.trim() ? COLORS.primary : "#A6A6A6"}
                />
              </button>

              {/* ✅ NEW: Clear button when search has text */}
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery("")}
                  style={{
                    position: "absolute",
                    right: `${Math.round(14 * scale)}px`,
                    top: "50%",
                    transform: "translateY(-50%)",
                    background: "none",
                    border: "none",
                    padding: 0,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: `${Math.round(16 * scale)}px`,
                    color: "#A6A6A6",
                    transition: "opacity 0.2s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.opacity = "0.7";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.opacity = "1";
                  }}
                  title="Clear search"
                  aria-label="Clear search"
                >
                  ✕
                </button>
              )}
            </div>
          </form>
        )}

        {/* {!isMobile && (
          <button
            style={{
              width: `${buttonSize}px`,
              height: `${buttonSize}px`,
              backgroundColor: "#F5F7FA",
              border: "none",
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "#E8ECEF";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "#F5F7FA";
            }}
          >
            <Filter
              size={Math.round(18 * scale)}
              color={COLORS.darkText}
              strokeWidth={1.5}
            />
          </button>
        )} */}

        {/* <button
          style={{
            width: `${buttonSize}px`,
            height: `${buttonSize}px`,
            backgroundColor: "#F5F7FA",
            border: "none",
            borderRadius: "50%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            transition: "all 0.2s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "#E8ECEF";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "#F5F7FA";
          }}
        >
          <Bell
            size={Math.round(18 * scale)}
            color={COLORS.darkText}
            strokeWidth={1.5}
          />
        </button> */}

        {/* {!isMobile && (
          <div
            onClick={onLogout}
            style={{
              width: `${avatarSize + 40}px`,
              height: `${avatarSize}px`,
              borderRadius: "50%",
              backgroundColor: COLORS.rejected,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              color: COLORS.white,
              fontSize: `${Math.round(18 * scale)}px`,
              fontWeight: "600",
            }}
          >
            Logout
          </div>
        )} */}

        <UserProfile user={user} onLogout={onLogout} scale={scale} />
      </div>
    </header>
  );
};
