const TOKEN_KEYS = {
  ACCESS: "maritime_access_token",
  REFRESH: "maritime_refresh_token",
  USER: "maritime_user",
};

// Use Vite's built-in env flag — true in `npm run build`, false in `npm run dev`
const isProduction = import.meta.env.PROD;

// ── Cookie helpers ────────────────────────────────────────────────────────────
const setCookie = (name, value, days = 7) => {
  const expires = new Date();
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
  // Secure flag only works on HTTPS — omit on localhost (dev)
  const secureFlag = isProduction ? ";Secure" : "";
  document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/${secureFlag};SameSite=Strict`;
};

const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
};

const deleteCookie = (name) => {
  document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:01 GMT;path=/;SameSite=Strict`;
};

// ── Token storage (cookies in production, localStorage in dev) ────────────────
export const tokenStorage = {
  // ── Access Token ────────────────────────────────────────────────────────────
  setAccessToken: (token) => {
    if (isProduction) {
      setCookie(TOKEN_KEYS.ACCESS, token, 1); // 1 day
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

  // ── Refresh Token ───────────────────────────────────────────────────────────
  setRefreshToken: (token) => {
    if (isProduction) {
      setCookie(TOKEN_KEYS.REFRESH, token, 15); // 15 days
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

  // ── User Profile (localStorage — not sensitive) ─────────────────────────────
  setUser: (user) => {
    try {
      localStorage.setItem(TOKEN_KEYS.USER, JSON.stringify(user));
    } catch {
      // Storage quota exceeded — silently fail, data still lives in memory
    }
  },

  getUser: () => {
    try {
      const user = localStorage.getItem(TOKEN_KEYS.USER);
      return user ? JSON.parse(user) : null;
    } catch {
      return null;
    }
  },

  removeUser: () => {
    localStorage.removeItem(TOKEN_KEYS.USER);
  },

  // ── Convenience: read role directly from stored user ────────────────────────
  // UI-only — backend enforces real permissions. Do NOT trust this for security.
  getStoredRole: () => {
    try {
      const user = localStorage.getItem(TOKEN_KEYS.USER);
      if (!user) return null;
      const parsed = JSON.parse(user);
      return parsed?.role?.toLowerCase() ?? null;
    } catch {
      return null;
    }
  },

  isStoredAdmin: () => {
    const role = tokenStorage.getStoredRole();
    return role === "admin" || role === "administrator";
  },

  // ── Clear everything ────────────────────────────────────────────────────────
  clearAll: () => {
    // Remove localStorage items
    Object.values(TOKEN_KEYS).forEach((key) => {
      localStorage.removeItem(key);
    });
    // Remove cookies
    deleteCookie(TOKEN_KEYS.ACCESS);
    deleteCookie(TOKEN_KEYS.REFRESH);
    // Do NOT delete USER cookie — there isn't one; user is in localStorage
  },
};
