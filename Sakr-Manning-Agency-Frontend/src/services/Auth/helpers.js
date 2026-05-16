// utils/authHelpers.js
import { jwtDecode } from "jwt-decode";
import config from "./config.js";

/**
 * Decode JWT token safely
 */
export const decodeToken = (token) => {
  try {
    const decodedToken = jwtDecode(token);
    return decodedToken;
  } catch (error) {
    console.error("Error decoding token:", error);
    return null;
  }
};

/**
 * Check if token is expired
 */
export const isTokenExpired = (token) => {
  if (!token) return true;

  const decoded = decodeToken(token);
  if (!decoded || !decoded.exp) return true;

  const currentTime = Date.now() / 1000;
  return decoded.exp < currentTime;
};

/**
 * Check if token needs refresh (within threshold of expiry)
 */
export const shouldRefreshToken = (token) => {
  if (!token) return false;

  const decoded = decodeToken(token);
  if (!decoded || !decoded.exp) return false;

  const currentTime = Date.now() / 1000;
  const timeUntilExpiry = decoded.exp - currentTime;
  const thresholdSeconds = config.TOKEN_REFRESH_THRESHOLD / 1000;

  return timeUntilExpiry < thresholdSeconds && timeUntilExpiry > 0;
};

/**
 * Get user ID from token
 */
export const getUserIdFromToken = (token) => {
  const decoded = decodeToken(token);
  return decoded?.user_id || decoded?.sub || null;
};

/**
 * Extract user data from JWT token
 */
export const extractUserFromToken = (token) => {
  const decoded = decodeToken(token);
  if (!decoded) return null;

  return {
    id: decoded.user_id || decoded.sub,
    email: decoded.email,
    // Add other fields from your backend JWT
  };
};

/**
 * Validate token structure
 */
export const isValidTokenStructure = (token) => {
  if (!token || typeof token !== "string") return false;

  const parts = token.split(".");
  return parts.length === 3;
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = (accessToken, refreshToken) => {
  if (!accessToken || !refreshToken) return false;

  // Check if access token is valid
  if (!isTokenExpired(accessToken)) return true;

  // If access token expired, check if refresh token is valid
  return !isTokenExpired(refreshToken);
};

/**
 * Get token expiry time in seconds
 */
export const getTokenExpiryTime = (token) => {
  const decoded = decodeToken(token);
  return decoded?.exp || null;
};

/**
 * Format user data from API response
 */
export const formatUserData = (userData) => {
  return {
    id: userData.id,
    email: userData.email,
    firstName: userData.first_name || userData.name,
    lastName: userData.last_name || "",
    name: userData.first_name || userData.name,
    role: userData.role || "",
    cv_status: userData.cv_status || false,
    // Add other fields as needed
  };
};
