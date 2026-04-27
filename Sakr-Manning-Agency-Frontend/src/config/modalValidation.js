// config/modalValidation.js
// Centralized validation rules for all form step modals
// Each key maps to React Hook Form RegisterOptions
// Import in modals: import { MODAL_VALIDATION } from '@/config/modalValidation';

import { FORM_FIELDS } from "./formConfig";

// ============================================================================
// SHARED VALIDATION HELPERS
// ============================================================================

const PATTERNS = {
    EMAIL: {
        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
        message: "Invalid email address",
    },
    PHONE: {
        value: /^[+]?[\d\s()-]{7,20}$/,
        message: "Invalid phone number format",
    },
};

/**
 * Helper: creates a "required" rule object
 */
const req = (msg) => ({ required: msg });

/**
 * Helper: creates a numeric range rule
 */
const numRange = (min, max, label) => ({
    min: { value: min, message: `${label} minimum is ${min}` },
    max: { value: max, message: `${label} maximum is ${max}` },
    valueAsNumber: true,
});

/**
 * Helper: max-length rule
 */
const maxLen = (len, label) => ({
    maxLength: { value: len, message: `${label} cannot exceed ${len} characters` },
});

// ============================================================================
// MODAL VALIDATION RULES
// ============================================================================

export const MODAL_VALIDATION = {
    // ── Certificate Modal ──────────────────────────────────────────────
    CERTIFICATE: {
        [FORM_FIELDS.CERTIFICATES.NAME]: {
            required: "Certificate name is required",
        },
        [FORM_FIELDS.CERTIFICATES.NUMBER]: {
            required: "Certificate number is required",
            ...maxLen(50, "Certificate number"),
        },
        [FORM_FIELDS.CERTIFICATES.ISSUE_DATE]: {
            required: "Issue date is required",
        },
        [FORM_FIELDS.CERTIFICATES.EXPIRY_DATE]: {},
        [FORM_FIELDS.CERTIFICATES.ISSUED_BY]: maxLen(100, "Issued by"),
        [FORM_FIELDS.CERTIFICATES.ISSUED_AT]: maxLen(100, "Issued at"),
    },

    // ── Course Modal ───────────────────────────────────────────────────
    COURSE: {
        [FORM_FIELDS.COURSES.NAME]: {
            required: "Course name is required",
        },
        [FORM_FIELDS.COURSES.NUMBER]: maxLen(50, "Course number"),
        [FORM_FIELDS.COURSES.ISSUE_DATE]: {
            required: "Issue date is required",
        },
        [FORM_FIELDS.COURSES.EXPIRY_DATE]: {},
        [FORM_FIELDS.COURSES.ISSUED_BY]: maxLen(100, "Issued by"),
        [FORM_FIELDS.COURSES.ISSUED_AT]: maxLen(100, "Issued at"),
        [FORM_FIELDS.COURSES.COUNTRY]: maxLen(100, "Country"),
    },

    // ── Document Modal ─────────────────────────────────────────────────
    DOCUMENT: {
        [FORM_FIELDS.DOCUMENTS.TYPE]: {
            required: "Document type is required",
        },
        [FORM_FIELDS.DOCUMENTS.NUMBER]: {
            required: "Document number is required",
            ...maxLen(50, "Document number"),
        },
        [FORM_FIELDS.DOCUMENTS.ISSUE_DATE]: {
            required: "Issue date is required",
        },
        [FORM_FIELDS.DOCUMENTS.EXPIRY_DATE]: {
            required: "Expiry date is required",
        },
        [FORM_FIELDS.DOCUMENTS.PLACE_OF_ISSUE]: maxLen(100, "Place of issue"),
    },

    // ── Health / Vaccination Modal ─────────────────────────────────────
    HEALTH: {
        [FORM_FIELDS.HEALTH.NAME]: {
            required: "Vaccination name is required",
        },
        [FORM_FIELDS.HEALTH.NUMBER]: maxLen(50, "Certificate number"),
        [FORM_FIELDS.HEALTH.ISSUE_DATE]: {
            required: "Issue date is required",
        },
        [FORM_FIELDS.HEALTH.EXPIRY_DATE]: {},
        [FORM_FIELDS.HEALTH.ISSUED_BY]: maxLen(100, "Issued by"),
        [FORM_FIELDS.HEALTH.ISSUED_AT]: maxLen(100, "Issued at"),
        [FORM_FIELDS.HEALTH.DISEASE]: maxLen(100, "Disease"),
        [FORM_FIELDS.HEALTH.FIRST_DATE]: {},
        [FORM_FIELDS.HEALTH.LAST_DATE]: {},
        [FORM_FIELDS.HEALTH.REMARKS]: maxLen(500, "Remarks"),
    },

    // ── Language Modal ─────────────────────────────────────────────────
    LANGUAGE: {
        [FORM_FIELDS.LANGUAGES.LANGUAGE]: {
            required: "Language is required",
        },
        [FORM_FIELDS.LANGUAGES.GENERAL]: {
            ...numRange(0, 100, "General marks"),
        },
        [FORM_FIELDS.LANGUAGES.LEVEL]: {
            required: "Proficiency level is required",
        },
        [FORM_FIELDS.LANGUAGES.SPEAKING]: {
            ...numRange(0, 100, "Speaking"),
        },
        [FORM_FIELDS.LANGUAGES.WRITING]: {
            ...numRange(0, 100, "Writing"),
        },
        [FORM_FIELDS.LANGUAGES.READING]: {
            ...numRange(0, 100, "Reading"),
        },
        [FORM_FIELDS.LANGUAGES.DESCRIPTION]: {},
    },

    // ── License Modal ──────────────────────────────────────────────────
    LICENSE: {
        [FORM_FIELDS.LICENSES.NAME]: {
            required: "License name is required",
        },
        [FORM_FIELDS.LICENSES.NUMBER]: {
            required: "License number is required",
            ...maxLen(50, "License number"),
        },
        [FORM_FIELDS.LICENSES.COUNTRY]: {
            required: "Country is required",
            ...maxLen(100, "Country"),
        },
        [FORM_FIELDS.LICENSES.ISSUE_DATE]: {
            required: "Issue date is required",
        },
        [FORM_FIELDS.LICENSES.EXPIRY_DATE]: {},
    },

    // ── Reference Modal ────────────────────────────────────────────────
    REFERENCE: {
        number: {
            required: "Reference number is required",
            ...maxLen(20, "Reference number"),
        },
        name: {
            required: "Name is required",
            ...maxLen(100, "Full name"),
        },
        company_name: {
            required: "Company name is required",
            ...maxLen(100, "Company name"),
        },
        management: maxLen(100, "Management"),
        country: {
            required: "Country is required",
            ...maxLen(100, "Country"),
        },
        position: {
            required: "Position is required",
            ...maxLen(100, "Position"),
        },
        email: {
            required: "Email is required",
            pattern: PATTERNS.EMAIL,
        },
        tel: {
            pattern: PATTERNS.PHONE,
        },
    },

    // ── Sea Service Modal ──────────────────────────────────────────────
    SEA_SERVICE: {
        [FORM_FIELDS.SEA_SERVICE.COMPANY]: {
            required: "Company name is required",
            ...maxLen(100, "Company name"),
        },
        [FORM_FIELDS.SEA_SERVICE.RANK]: {
            required: "Rank is required",
        },
        [FORM_FIELDS.SEA_SERVICE.VESSEL]: maxLen(100, "Vessel name"),
        [FORM_FIELDS.SEA_SERVICE.SIGNED_ON]: {},
        [FORM_FIELDS.SEA_SERVICE.SIGNED_OFF]: {},
        [FORM_FIELDS.SEA_SERVICE.FLAG]: maxLen(100, "Flag"),
        [FORM_FIELDS.SEA_SERVICE.PERIOD]: maxLen(50, "Period"),
        [FORM_FIELDS.SEA_SERVICE.VESSEL_TYPE]: maxLen(100, "Vessel type"),
        [FORM_FIELDS.SEA_SERVICE.DWT]: maxLen(20, "D.W.T"),
        [FORM_FIELDS.SEA_SERVICE.GRT]: maxLen(20, "G.R.T"),
        [FORM_FIELDS.SEA_SERVICE.ENGINE_TYPE]: maxLen(100, "Engine type"),
        [FORM_FIELDS.SEA_SERVICE.BH]: maxLen(20, "B.H."),
        [FORM_FIELDS.SEA_SERVICE.KW]: maxLen(20, "K.W."),
        [FORM_FIELDS.SEA_SERVICE.REASON]: maxLen(200, "Reason"),
    },

    // ── Work Experience Modal ──────────────────────────────────────────
    WORK_EXPERIENCE: {
        [FORM_FIELDS.WORK_EXPERIENCE.EXPERIENCE]: {
            required: "Experience description is required",
            ...maxLen(2000, "Experience"),
        },
    },
};

// ============================================================================
// FILE UPLOAD CONFIG
// ============================================================================

export const FILE_UPLOAD_CONFIG = {
    /** Accepted file extensions (used by FileUpload component) */
    acceptedExtensions: [".pdf", ".jpg", ".jpeg", ".png"],
    /** Max file size in megabytes */
    maxSizeMB: 10,
    /** MIME types allowed (used for MIME-type checking) */
    acceptedMimeTypes: [
        "application/pdf",
        "image/jpeg",
        "image/png",
    ],
};
