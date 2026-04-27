// utils/constants.js

// Import assets directly so Vite bundles them
import Logo from "../assets/icons/logo.png";
import Background from "../assets/ship-bg.jpg";
import Subtract from "../assets/subtract.png";
import Verification from "../assets/Verification.png";
import QuickApplyBG from "../assets/quick_apply_bg.png";

// Home & About images
import Home1 from "../assets/home-1.jpg";
import Home2 from "../assets/home-2.jpg";
import About1 from "../assets/about-1.jpg";
import About2 from "../assets/about-2.jpg";

// Services & Contact
import ServicesImg from "../assets/services-1.jpg";
import ContactImg from "../assets/contact-1.png";

// Slider images
import Slider1 from "../assets/slider-1.jpg";
import Slider2 from "../assets/slider-2.jpg";
import Slider3 from "../assets/slider-3.jpg";

// A icons
import A_Safety from "../assets/icons/a_safety.png";
import A_Integrity from "../assets/icons/a_integrity.png";
import A_Excellence from "../assets/icons/a_excellence.png";
import A_Sustainability from "../assets/icons/a_sustainability.png";
import A_Partnership from "../assets/icons/a_partnership.png";
import A_Group from "../assets/icons/a_group.png";
import A_Delete from "../assets/icons/delete.png";
import A_Update from "../assets/icons/update.png";

// Social media icons
import FacebookIcon from "../assets/icons/facebook.png";
import LinkedInIcon from "../assets/icons/linkedin.png";
import TwitterIcon from "../assets/icons/twitter.png";

// Form Icons
import PROFILE from "../assets/form-icons/Profile.svg?react";
import EDUCATION from "../assets/form-icons/Education.svg?react";
import CONTACT from "../assets/form-icons/Contact.svg?react";
import EMERGENCY from "../assets/form-icons/Emergency.svg?react";
import DOCUMENTS from "../assets/form-icons/Documents.svg?react";
import CERTIFICATES from "../assets/form-icons/Licenses.svg?react";
import HEALTH from "../assets/form-icons/Health.svg?react";
import COURSES from "../assets/form-icons/Courses.svg?react";
import SEA from "../assets/form-icons/Services.svg?react";
import REFERENCE from "../assets/form-icons/Reference.svg?react";
import DECLARATION from "../assets/form-icons/Declaration.svg?react";
import SUBMIT from "../assets/form-icons/Submit.svg?react";

import Upload from "../assets/icons/upload.png";

// import dashboard Icons
import D_HOME from "../assets/dashboard/home.png";
import D_CVS from "../assets/dashboard/document.png";
import D_COMPANY from "../assets/dashboard/employees.png";
import D_INTERVIEWS from "../assets/dashboard/interview.png";
import D_DOCUMENTS from "../assets/dashboard/payment.png";
import D_USERS from "../assets/dashboard/employee.png";
import D_FINANCE from "../assets/dashboard/finance.png";

import D_ACCEPT from "../assets/dashboard/accept.png";
import D_REJECT from "../assets/dashboard/reject.png";
import D_PENDING from "../assets/dashboard/calender.png";
import D_INTERVIEW from "../assets/dashboard/user_interview.png";

import D_TOTAL_CVS from "../assets/dashboard/cv.png";
import D_TOTAL_COMPANIES from "../assets/dashboard/companies.png";
import D_TOTAL_SHIPS from "../assets/dashboard/ship.png";
import D_PENDING_INTERVIEWS from "../assets/dashboard/schedule.png";
import D_TOTAL_USERS from "../assets/dashboard/users.png";

import D_CHATBOT from "../assets/dashboard/Chatbot.png";
// Now export them
export const ASSETS = {
  LOGO: Logo,
  BACKGROUND: Background,
  QUICKBG: QuickApplyBG,
  VERIFICATION: Verification,
  SUBTRACT: Subtract,
  HOME_IMAGES: [Home1, Home2],
  ABOUT_IMAGES: [About1, About2],
  SERVICES: ServicesImg,
  CONTACT: ContactImg,
  SLIDER_IMAGES: [Slider1, Slider2, Slider3],
  ICONS: [
    PROFILE,
    EDUCATION,
    CONTACT,
    EMERGENCY,
    DOCUMENTS,
    CERTIFICATES,
    HEALTH,
    COURSES,
    SEA,
    REFERENCE,
    DECLARATION,
    SUBMIT,
  ],
  UPLOAD: Upload,
  A_ICONS: [
    A_Safety,
    A_Integrity,
    A_Excellence,
    A_Sustainability,
    A_Partnership,
    A_Group,
    A_Delete,
    A_Update,
  ],
  SOCIAL_MEDIA: {
    FACEBOOK: FacebookIcon,
    LINKEDIN: LinkedInIcon,
    TWITTER: TwitterIcon,
  },
  DASHBOARD_Sidebar_ICONS: [
    D_HOME,
    D_CVS,
    D_COMPANY,
    D_INTERVIEWS,
    D_DOCUMENTS,
    D_USERS,
    D_FINANCE,
  ],
  DASHBOARD_STATUS_ICONS: [D_ACCEPT, D_REJECT, D_PENDING, D_INTERVIEW],
  DASHBOARD_STATS_ICONS: [
    D_TOTAL_CVS,
    D_TOTAL_COMPANIES,
    D_TOTAL_SHIPS,
    D_PENDING_INTERVIEWS,
    D_TOTAL_USERS,
  ],
  CHATBOT: D_CHATBOT,
};

// Authentication steps
export const AUTH_STEPS = {
  LOGIN: "login",
  SIGNUP: "signup",
  VERIFICATION: "verification",
  FORGOT_PASSWORD: "forgot_password",
  RESET_PASSWORD: "reset_password",
  DASHBOARD: "dashboard",
  LANDING: "LANDING",
};

// Form field types
export const FIELD_TYPES = {
  TEXT: "text",
  EMAIL: "email",
  PASSWORD: "password",
  PHONE: "tel",
  NUMBER: "number",
};

// Button variants
export const BUTTON_VARIANTS = {
  PRIMARY: "primary",
  SECONDARY: "secondary",
  DANGER: "danger",
  SUCCESS: "success",
  GHOST: "ghost",
  OUTLINE: "outline",
  NAVIGATION: "navigation",
};

// Animation durations (in milliseconds)
export const ANIMATION_DURATION = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500,
};

// API endpoints
export const API_ENDPOINTS = {
  LOGIN: "/auth/login",
  SIGNUP: "/auth/signup",
  VERIFY_CODE: "/auth/verify-code",
  RESEND_CODE: "/auth/resend-code",
  FORGOT_PASSWORD: "/auth/forgot-password",
  RESET_PASSWORD: "/auth/reset-password",
  LOGOUT: "/auth/logout",
  REFRESH_TOKEN: "/auth/refresh",
  PROFILE: "/user/profile",
};

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: "Network error. Please check your connection and try again.",
  SERVER_ERROR: "Server error. Please try again later.",
  INVALID_CREDENTIALS: "Invalid email or password.",
  EMAIL_EXISTS: "An account with this email already exists.",
  INVALID_TOKEN: "Invalid or expired token.",
  VERIFICATION_FAILED: "Verification failed. Please try again.",
  RATE_LIMIT: "Too many attempts. Please try again later.",
  GENERIC: "Something went wrong. Please try again.",
};

// Success messages
export const SUCCESS_MESSAGES = {
  SIGNUP_SUCCESS: "Account created successfully! Please verify your email.",
  LOGIN_SUCCESS: "Welcome back!",
  VERIFICATION_SUCCESS: "Email verified successfully!",
  CODE_SENT: "Verification code sent to your email.",
  PASSWORD_RESET: "Password reset email sent.",
  PASSWORD_UPDATED: "Password updated successfully.",
  PROFILE_UPDATED: "Profile updated successfully.",
};

// Verification settings
export const VERIFICATION = {
  CODE_LENGTH: 3,
  RESEND_COOLDOWN: 60, // seconds
  MAX_ATTEMPTS: 5,
  EXPIRY_TIME: 10, // minutes
};

// Password requirements
export const PASSWORD_REQUIREMENTS = {
  MIN_LENGTH: 8,
  REQUIRE_UPPERCASE: true,
  REQUIRE_LOWERCASE: true,
  REQUIRE_NUMBERS: true,
  REQUIRE_SPECIAL_CHARS: true,
};

// Local storage keys
export const STORAGE_KEYS = {
  USER: "maritime_user",
  TOKEN: "maritime_token",
  REFRESH_TOKEN: "maritime_refresh_token",
  REMEMBER_ME: "maritime_remember_me",
  THEME: "maritime_theme",
};

// Theme colors
export const COLORS = {
  PRIMARY: {
    50: "#eff6ff",
    100: "#dbeafe",
    500: "#3b82f6",
    600: "#2563eb",
    700: "#1d4ed8",
  },
  SUCCESS: "#10b981",
  WARNING: "#f59e0b",
  ERROR: "#ef4444",
  GRAY: {
    50: "#f9fafb",
    100: "#f3f4f6",
    400: "#9ca3af",
    500: "#6b7280",
    600: "#4b5563",
    900: "#111827",
  },
};

// Responsive breakpoints
export const BREAKPOINTS = {
  SM: "640px",
  MD: "768px",
  LG: "1024px",
  XL: "1280px",
  "2XL": "1536px",
};

// Assets paths
// export const ASSETS = {
//   LOGO: "src/assets/icons/logo.png",
//   BACKGROUND: "src/assets/ship-bg.jpg",
//   SUBTRACT: "src/assets/subtract.png",
//   HOME_IMAGES: ["src/assets/home-1.jpg", "src/assets/home-2.jpg"],
//   ABOUT_IMAGES: ["src/assets/about-1.jpg", "src/assets/about-2.jpg"],
//   SERVICES: "src/assets/services-1.jpg",
//   CONTACT: "src/assets/contact-1.png",
//   SLIDER_IMAGES: [
//     "src/assets/slider-1.jpg",
//     "src/assets/slider-2.jpg",
//     "src/assets/slider-3.jpg",
//   ],
//   A_ICONS: [
//     "src/assets/icons/a_safety.png",
//     "src/assets/icons/a_integrity.png",
//     "src/assets/icons/a_excellence.png",
//     "src/assets/icons/a_sustainability.png",
//     "src/assets/icons/a_partnership.png",
//     "src/assets/icons/a_group.png",
//   ],
//   SOCIAL_MEDIA: {
//     FACEBOOK: "src/assets/icons/facebook.png",
//     LINKEDIN: "src/assets/icons/linkedin.png",
//     TWITTER: "src/assets/icons/twitter.png",
//   },
// };

export const BUTTON_SIZES = {
  SM: "sm",
  MD: "md",
  LG: "lg",
  XL: "xl",
};

export const CARD_VARIANTS = {
  DEFAULT: "default",
  OUTLINED: "outlined",
  ELEVATED: "elevated",
  FLAT: "flat",
};

export const INPUT_VARIANTS = {
  DEFAULT: "default",
  OUTLINED: "outlined",
  FILLED: "filled",
};

export const SECTION_LAYOUTS = {
  DEFAULT: "default",
  CENTERED: "centered",
  SPLIT: "split",
  GRID: "grid",
  MASONRY: "masonry",
};

export const SPACING_SIZES = {
  NONE: "none",
  SM: "sm",
  MD: "md",
  LG: "lg",
  XL: "xl",
};

export const COMPONENT_SIZES = {
  SM: "sm",
  MD: "md",
  LG: "lg",
};

// inputConstants.js
export const INPUT_SIZES = {
  SM: "sm",
  MD: "md",
  LG: "lg",
};

export const sizeClasses = {
  [INPUT_SIZES.SM]: "px-3 py-2 text-sm rounded-lg",
  [INPUT_SIZES.MD]: "px-4 py-2 text-base rounded-xl",
  [INPUT_SIZES.LG]: "px-5 py-3 text-lg rounded-2xl",
};

export const FORM_SECTION_VARIANTS = {
  PRIMARY: "primary",
  LIGHT: "light",
  DEFAULT: "default",
};

export const formSectionVariants = {
  [FORM_SECTION_VARIANTS.PRIMARY]: "bg-white shadow-lg rounded-2xl p-8 md:p-12",
  [FORM_SECTION_VARIANTS.LIGHT]:
    "bg-gray-50 border border-gray-200 rounded-2xl p-8 md:p-12",
  [FORM_SECTION_VARIANTS.DEFAULT]: "bg-transparent p-4 md:p-6",
};

export const variantClasses = {
  [INPUT_VARIANTS.DEFAULT]:
    "border border-gray-300 bg-white focus:ring-2 focus:ring-blue-500",
  [INPUT_VARIANTS.OUTLINED]:
    "border-2 border-gray-300 bg-transparent focus:ring-2 focus:ring-blue-500",
  [INPUT_VARIANTS.FILLED]:
    "border-0 bg-gray-100 focus:ring-2 focus:ring-blue-500 focus:bg-white",
};

export const stateClasses = ({ error, success, disabled, variant }) => {
  if (disabled) return "opacity-50 cursor-not-allowed bg-gray-50";
  if (error) return "border-red-500 focus:ring-red-500";
  if (success) return "border-green-500 focus:ring-green-500";
  return variantClasses[variant] || variantClasses[INPUT_VARIANTS.DEFAULT];
};

// utility
export const cx = (...parts) => parts.filter(Boolean).join(" ");
