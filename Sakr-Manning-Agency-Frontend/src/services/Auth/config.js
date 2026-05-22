// services/Auth/config.js - UPDATED FOR YOUR BACKEND

export const config = {
  // API Configuration
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || "https://backend.sakrshipping.com/api/",
  API_TIMEOUT: import.meta.env.VITE_API_TIMEOUT ? Number(import.meta.env.VITE_API_TIMEOUT) : 30000,
  // Auth Configuration
  TOKEN_REFRESH_THRESHOLD: 5 * 60 * 1000, // Refresh 5 minutes before expiry
  TOKEN_REFRESH_INTERVAL: 10 * 60 * 1000, // Check every 10 minutes

  // Storage Keys
  STORAGE_KEYS: {
    ACCESS_TOKEN: "maritime_access_token_new",
    REFRESH_TOKEN: "maritime_refresh_token_new",
    USER: "maritime_user_new",
  },

  // API Endpoints - CORRECTED FOR YOUR BACKEND STRUCTURE
  ENDPOINTS: {
    // ===== AUTH =====
    REGISTER: "/register/",
    LOGIN: "/login/",
    LOGIN_REFRESH: "/login/refresh/",
    LOGOUT: "/logout/",

    // ===== USERS =====
    // IMPORTANT: Your backend uses /users/users/ not /users/
    USERS: "/users/users/",
    USER_DETAIL: (id) => `/users/users/${id}/`,
    USER_STATS: "/users/users/stats/",
    USER_ME: "/users/users/me/",

    // User-specific nested endpoints
    USER_CERTIFICATES: (userId) => `/users/users/${userId}/certificates/`,
    USER_RANKS: (userId) => `/users/users/${userId}/ranks/`,
    USER_ASSIGN_BY_POSITION: (userId) => `/users/users/${userId}/assign-by-position/`,
    POSITIONS: "/positions/",

    // ===== CORE (Flags & Vessel Types) =====
    FLAGS: "/core/flags/",
    FLAG_DETAIL: (id) => `/core/flags/${id}/`,
    VESSEL_TYPES: "/core/vessel-types/",
    VESSEL_TYPE_DETAIL: (id) => `/core/vessel-types/${id}/`,

    // ===== CERTIFICATES =====
    CERTIFICATES: "/users/certificates/",
    CERTIFICATE_DETAIL: (id) => `/users/certificates/${id}/`,

    // ===== RANKS =====
    RANKS: "/ranks/",
    RANK_DETAIL: (id) => `/ranks/${id}/`,

    // ===== COMPANIES =====
    COMPANIES: "/companies/",
    COMPANY_DETAIL: (id) => `/companies/${id}/`,
    COMPANY_STATS: "/companies/stats/",

    // ===== TICKETS & PAPERS =====
    TICKETS: "/tickets-papers/tickets/",
    TICKET_DETAIL: (id) => `/tickets-papers/tickets/${id}/`,
    TRAVELING_PAPERS: "/tickets-papers/traveling-papers/",
    TRAVELING_PAPER_DETAIL: (id) => `/tickets-papers/traveling-papers/${id}/`,

    // ===== SEA SERVICES =====
    SEA_SERVICES: "/users/sea-services/",
    SEA_SERVICE_DETAIL: (id) => `/users/sea-services/${id}/`,

    // ===== VACCINATIONS (Health) =====
    VACCINATIONS: "/vaccinations/",
    VACCINATION_DETAIL: (id) => `/vaccinations/${id}/`,

    // ===== COURSES =====
    COURSES: "/courses/",
    COURSE_DETAIL: (id) => `/courses/${id}/`,

    // ===== LICENSES =====
    LICENSES: "/my-licenses/",
    LICENSE_DETAIL: (id) => `/my-licenses/${id}/`,

    // ===== LANGUAGES =====
    LANGUAGES: "/users/user-languages/",
    LANGUAGE_DETAIL: (id) => `/users/user-languages/${id}/`,

    // ===== SHIPS =====
    SHIPS: "/ships/",
    SHIP_DETAIL: (id) => `/ships/${id}/`,
    SHIP_ASSIGN_USER: (id) => `/ships/${id}/assign-user/`,
    SHIP_UNASSIGN_USER: (id) => `/ships/${id}/unassign-user/`,

    // ===== INTERVIEWS =====
    INTERVIEWS: "/users/interviews/",
    INTERVIEW_DETAIL: (id) => `/users/interviews/${id}/`,
    INTERVIEW_STATS: "/users/interviews/stats/",
    INTERVIEW_CALENDAR: "/users/interviews/calendar/",

    // ===== FINANCE =====
    FINANCE_RECORDS: "/finance/finance-records/",
    FINANCE_RECORD_DETAIL: (id) => `/finance/finance-records/${id}/`,
    FINANCE_CALCULATE: "/finance/finance-records/calculate/",
    FINANCE_STATS: "/finance/finance-records/stats/",
    FINANCE_EXPORT: "/finance/finance-records/export/",

    // ===== CONTRACTS =====
    CONTRACTS: "/contracts/",
    CONTRACT_DETAIL: (id) => `/contracts/${id}/`,
    CONTRACT_STATS: "/contracts/stats/",

    // ===== CV SUBMISSIONS / PIPELINE (Section 4) =====
    CV_SUBMISSIONS: "/cv-submissions/",
    CV_SUBMISSION_DETAIL: (id) => `/cv-submissions/${id}/`,
    CV_SUBMISSION_STATS: "/cv-submissions/stats/",
    CV_SUBMISSION_UPDATE_STATUS: (id) => `/cv-submissions/${id}/update-status/`,

    // ===== CV DOCUMENTS (Section 2) =====
    DOCUMENTS: "/documents/",
    DOCUMENT_DETAIL: (id) => `/documents/${id}/`,
    DOCUMENT_SET_STATUS: (id) => `/documents/${id}/set_status/`,
    DOCUMENT_DOWNLOAD: (id) => `/documents/${id}/download/`,

    // ===== AI CHAT =====
    AI_CHAT: "/ai-agents/chat/",
    AI_CHAT_HISTORY: (sessionId) => `/ai-agents/chat/history/${sessionId}/`,
    AI_CHAT_SESSIONS: "/ai-agents/chat/sessions/",
    AI_CAPABILITIES: "/ai-agents/capabilities/",

    // ===== AI DOCUMENTS =====
    AI_UPLOAD: "/ai/upload/",
    AI_APPLICANTS: "/ai/applicants/",
    AI_APPLICANT_DETAIL: (id) => `/ai/applicants/${id}/`,
    AI_CONVERT: "/ai/convert/",
    AI_BATCH_CONVERT: "/ai/batch-convert/",
    AI_SYNC_STATUS: "/ai/sync-status/",
  },

  // Google OAuth Configuration
  GOOGLE: {
    // Replace with your Google Client ID when ready
    CLIENT_ID: import.meta.env.VITE_GOOGLE_CLIENT_ID || "",
    // Backend endpoint for Google auth
    ENDPOINT: "/auth/google/",
  },

  // Feature Flags
  FEATURES: {
    EMAIL_VERIFICATION: false,
    // Set to true when backend supports Google OAuth
    GOOGLE_AUTH: false,
    REMEMBER_ME: true,
  },

  // Validation
  VALIDATION: {
    PASSWORD_MIN_LENGTH: 8,
    CODE_LENGTH: 6,
    MAX_VERIFICATION_ATTEMPTS: 3,
  },
};

export default config;
