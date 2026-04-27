// services/errorHandler.js

/**
 * Handle API errors and return user-friendly messages
 */
export const handleApiError = (error) => {
  console.error("API Error:", error);

  // Network errors (no response from server)
  if (!error.response) {
    if (error.request) {
      return "Network error. Please check your internet connection.";
    }
    return error.message || "An unexpected error occurred.";
  }

  const { status, data } = error.response;

  // Handle specific status codes
  switch (status) {
    case 400: {
      // Bad Request - usually validation errors
      if (data.email) {
        if (Array.isArray(data.email)) {
          return data.email[0];
        }
        return data.email;
      }

      if (data.password) {
        if (Array.isArray(data.password)) {
          return data.password[0];
        }
        return data.password;
      }

      if (data.detail) {
        return data.detail;
      }

      // Check for non_field_errors
      if (data.non_field_errors) {
        if (Array.isArray(data.non_field_errors)) {
          return data.non_field_errors[0];
        }
        return data.non_field_errors;
      }

      // Generic validation error
      if (typeof data === "object") {
        const firstError = Object.values(data)[0];
        if (Array.isArray(firstError)) {
          return firstError[0];
        }
        return firstError;
      }

      return "Invalid request. Please check your input.";
    }

    case 401: {
      // Unauthorized
      if (data.detail) {
        // Common Django REST Framework message
        if (data.detail === "Invalid token.") {
          return "Your session has expired. Please login again.";
        }
        if (data.detail.includes("credentials")) {
          return "Invalid email or password.";
        }
        return data.detail;
      }
      return "Authentication failed. Please login again.";
    }

    case 403: {
      // Forbidden
      if (data.detail) {
        return data.detail;
      }
      return "You don't have permission to perform this action.";
    }

    case 404: {
      // Not Found
      if (data.detail) {
        return data.detail;
      }
      return "The requested resource was not found.";
    }

    case 409: {
      // Conflict - usually duplicate entries
      if (data.email) {
        return "This email is already registered.";
      }
      if (data.detail) {
        return data.detail;
      }
      return "This record already exists.";
    }

    case 429: {
      // Too Many Requests
      if (data.detail) {
        return data.detail;
      }
      return "Too many requests. Please try again later.";
    }

    case 500: {
      // Internal Server Error
      if (data.detail) {
        return data.detail;
      }
      return "Server error. Please try again later.";
    }

    case 502: {
      // Bad Gateway
      return "Service temporarily unavailable. Please try again.";
    }

    case 503: {
      // Service Unavailable
      return "Service is under maintenance. Please try again later.";
    }

    default: {
      // Any other status code
      if (data.detail) {
        return data.detail;
      }
      if (data.message) {
        return data.message;
      }
      return `An error occurred (${status}). Please try again.`;
    }
  }
};

/**
 * Format validation errors for forms
 */
export const formatValidationErrors = (error) => {
  if (!error.response || !error.response.data) {
    return {};
  }

  const data = error.response.data;
  const formattedErrors = {};

  // Handle Django REST Framework validation errors
  Object.keys(data).forEach((field) => {
    if (Array.isArray(data[field])) {
      formattedErrors[field] = data[field][0];
    } else {
      formattedErrors[field] = data[field];
    }
  });

  return formattedErrors;
};

/**
 * Check if error is authentication related
 */
export const isAuthError = (error) => {
  return error.response?.status === 401 || error.response?.status === 403;
};

/**
 * Check if error is network related
 */
export const isNetworkError = (error) => {
  return !error.response && error.request;
};

/**
 * Check if error is server error
 */
export const isServerError = (error) => {
  return error.response?.status >= 500;
};

/**
 * Extract error message from various error formats
 */
export const extractErrorMessage = (error) => {
  if (typeof error === "string") {
    return error;
  }

  if (error.response?.data) {
    const data = error.response.data;

    if (typeof data === "string") {
      return data;
    }

    if (data.detail) {
      return data.detail;
    }

    if (data.message) {
      return data.message;
    }

    // Get first error from object
    const firstKey = Object.keys(data)[0];
    if (firstKey && data[firstKey]) {
      if (Array.isArray(data[firstKey])) {
        return data[firstKey][0];
      }
      return data[firstKey];
    }
  }

  if (error.message) {
    return error.message;
  }

  return "An unexpected error occurred";
};

export default handleApiError;
