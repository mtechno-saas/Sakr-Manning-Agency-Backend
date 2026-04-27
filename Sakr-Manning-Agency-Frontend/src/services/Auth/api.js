import axios from "axios";
import { tokenStorage } from "./tokenStorage.js";
import config from "./config.js";
import { isTokenExpired } from "./helpers.js"; // Adjust path if needed

const api = axios.create({
  baseURL: config.API_BASE_URL,
  timeout: config.API_TIMEOUT,
  headers: {
    "Content-Type": "application/json",
  },
});

let isRefreshing = false;
let failedQueue = [];

// api.js - Update the processQueue function
const processQueue = (error, token = null) => {
  // Create a local copy of the queue and clear it immediately
  const queue = [...failedQueue];
  failedQueue = []; // Clear the queue first to prevent re-processing

  queue.forEach((prom) => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });
};

// In the response interceptor, improve the logic:
api.interceptors.response.use(
  (response) => {
    console.log(
      `%c Response: [${response.status}] ${response.config.url}`,
      "color: #4caf50; font-weight: bold"
    );
    console.log("Response Data:", response.data);
    return response;
  },
  async (error) => {
    console.log(
      `%c Error Response: [${error.response?.status || "network"}] ${error.config?.url
      }`,
      "color: #f44336; font-weight: bold"
    );
    if (error.response?.data) {
      console.log("Error Data:", error.response.data);
    }
    const originalRequest = error.config;

    // Filter out login/register calls and non-401 errors
    if (
      !error.response ||
      error.response.status !== 401 ||
      originalRequest.url.includes("/login") ||
      originalRequest.url.includes("/register") ||
      originalRequest.url.includes("/auth")
    ) {
      return Promise.reject(error);
    }

    // Check if we've already retried this request
    if (originalRequest._retry) {
      tokenStorage.clearAll();
      window.location.href = "/auth";
      return Promise.reject(error);
    }

    // Handle concurrent refresh requests
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
      processQueue(null, access); // Process queue with new token

      originalRequest.headers.Authorization = `Bearer ${access}`;
      return api(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError, null);
      tokenStorage.clearAll();
      window.location.href = "/auth";
      return Promise.reject(refreshError);
    } finally {
      // Add a small delay before resetting isRefreshing to prevent race conditions
      setTimeout(() => {
        isRefreshing = false;
      }, 100);
    }
  }
);

api.interceptors.request.use(
  (config) => {
    const token = tokenStorage.getAccessToken();
    if (token && !isTokenExpired(token)) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log(
      `%c Request: [${config.method?.toUpperCase()}] ${config.url}`,
      "color: #00bcd4; font-weight: bold"
    );
    // console.log("Request Headers:", config.headers);
    if (config.data) {
      console.log("Request Body:", config.data);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
