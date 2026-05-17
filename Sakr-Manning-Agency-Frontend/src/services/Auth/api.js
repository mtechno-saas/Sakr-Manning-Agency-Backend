// api.js — Axios instance with request/response interceptors
import axios from "axios";
import { tokenStorage } from "./tokenStorage.js";
import config from "./config.js";
import { isTokenExpired } from "./helpers.js";

const isDev = import.meta.env.DEV;

const api = axios.create({
  baseURL: config.API_BASE_URL,
  timeout: config.API_TIMEOUT,
  headers: {
    "Content-Type": "application/json",
  },
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  const queue = [...failedQueue];
  failedQueue = [];
  queue.forEach((prom) => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });
};

// ── Request interceptor — attach access token ─────────────────────────────────
api.interceptors.request.use(
  (cfg) => {
    const token = tokenStorage.getAccessToken();
    if (token && !isTokenExpired(token)) {
      cfg.headers.Authorization = `Bearer ${token}`;
    }
    return cfg;
  },
  (error) => Promise.reject(error)
);

// ── Response interceptor — handle 401 + auto token refresh ───────────────────
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Only handle 401 errors — skip auth endpoints to avoid infinite loops
    if (
      !error.response ||
      error.response.status !== 401 ||
      originalRequest._retry ||
      originalRequest.url.includes("/login") ||
      originalRequest.url.includes("/register") ||
      originalRequest.url.includes("/auth")
    ) {
      if (originalRequest._retry) {
        // Second failure after refresh — session is dead
        tokenStorage.clearAll();

        // Only redirect if not on a public page
        const publicPaths = ["/", "/auth"];
        if (!publicPaths.includes(window.location.pathname)) {
          window.location.href = "/auth";
        }
      }
      return Promise.reject(error);
    }

    // Queue concurrent requests while refreshing
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      })
        .then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        })
        .catch((err) => Promise.reject(err));
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const refreshToken = tokenStorage.getRefreshToken();
      if (!refreshToken) throw new Error("No refresh token");

      const response = await axios.post(
        `${config.API_BASE_URL}${config.ENDPOINTS.LOGIN_REFRESH}`,
        { refresh: refreshToken }
      );

      const { access } = response.data;
      tokenStorage.setAccessToken(access);
      api.defaults.headers.common.Authorization = `Bearer ${access}`;
      processQueue(null, access);

      originalRequest.headers.Authorization = `Bearer ${access}`;
      return api(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError, null);
      tokenStorage.clearAll();

      // Only redirect to auth if we are not on a public page
      const publicPaths = ["/", "/auth"];
      if (!publicPaths.includes(window.location.pathname)) {
        window.location.href = "/auth";
      }

      return Promise.reject(refreshError);
    } finally {
      setTimeout(() => {
        isRefreshing = false;
      }, 100);
    }
  }
);

export default api;
