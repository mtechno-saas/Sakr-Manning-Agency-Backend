// tokenStorage.js
const TOKEN_KEYS = {
  ACCESS: "maritime_access_token_new",
  REFRESH: "maritime_refresh_token_new",
  USER: "maritime_user_new",
};

// Production detection
const isProduction = true;
// Cookie helpers
const setCookie = (name, value, days = 7) => {
  if (!isProduction) return; // Only use cookies in production
  const expires = new Date();
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
  document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;Secure;SameSite=Strict`;
};

const getCookie = (name) => {
  if (!isProduction) return null;
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
};

const deleteCookie = (name) => {
  if (!isProduction) return;
  document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:01 GMT;path=/;Secure;SameSite=Strict`;
};

export const tokenStorage = {
  // Access Token
  setAccessToken: (token) => {
    if (isProduction) {
      setCookie(TOKEN_KEYS.ACCESS, token, 1); // 1 day for access token
    } else {
      localStorage.setItem(TOKEN_KEYS.ACCESS, token);
    }
  },

  getAccessToken: () => {
    if (isProduction) {
      return getCookie(TOKEN_KEYS.ACCESS);
    }
    return localStorage.getItem(TOKEN_KEYS.ACCESS);
  },

  removeAccessToken: () => {
    if (isProduction) {
      deleteCookie(TOKEN_KEYS.ACCESS);
    } else {
      localStorage.removeItem(TOKEN_KEYS.ACCESS);
    }
  },

  // Refresh Token
  setRefreshToken: (token) => {
    if (isProduction) {
      setCookie(TOKEN_KEYS.REFRESH, token, 15); // 15 days for refresh token
    } else {
      localStorage.setItem(TOKEN_KEYS.REFRESH, token);
    }
  },

  getRefreshToken: () => {
    if (isProduction) {
      return getCookie(TOKEN_KEYS.REFRESH);
    }
    return localStorage.getItem(TOKEN_KEYS.REFRESH);
  },

  removeRefreshToken: () => {
    if (isProduction) {
      deleteCookie(TOKEN_KEYS.REFRESH);
    } else {
      localStorage.removeItem(TOKEN_KEYS.REFRESH);
    }
  },

  // User Data (keep in localStorage as it's not sensitive)
  setUser: (user) => {
    localStorage.setItem(TOKEN_KEYS.USER, JSON.stringify(user));
  },

  getUser: () => {
    const user = localStorage.getItem(TOKEN_KEYS.USER);
    return user ? JSON.parse(user) : null;
  },

  removeUser: () => {
    localStorage.removeItem(TOKEN_KEYS.USER);
  },

  // Clear all
  clearAll: () => {
    Object.values(TOKEN_KEYS).forEach((key) => {
      localStorage.removeItem(key);
      deleteCookie(key);
    });
  },
};
