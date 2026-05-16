export const cleanDraftFields = (data) => {
    if (!data || typeof data !== "object") return data;

    const { Draft, ...cleanData } = data;
    return cleanData;
};

/**
 * Draft field paths for each CRUD form section
 */
export const DRAFT_PATHS = {
    CERTIFICATE: {
        certificateName: "Draft.Certificate.certificateName",
        number: "Draft.Certificate.number",
        issuedDate: "Draft.Certificate.issuedDate",
        expiryDate: "Draft.Certificate.expiryDate",
        issuedBy: "Draft.Certificate.issuedBy",
        issuedAt: "Draft.Certificate.issuedAt",
    },
    DOCUMENT: {
        documentType: "Draft.Document.documentType",
        documentNumber: "Draft.Document.documentNumber",
        issuedDate: "Draft.Document.issuedDate",
        expiryDate: "Draft.Document.expiryDate",
        issuedBy: "Draft.Document.issuedBy",
        issuedAt: "Draft.Document.issuedAt",
        file: "Draft.Document.file",
    },
    HEALTH: {
        type: "Draft.Health.type",
        number: "Draft.Health.number",
        issuedDate: "Draft.Health.issuedDate",
        expiryDate: "Draft.Health.expiryDate",
        issuedBy: "Draft.Health.issuedBy",
        issuedAt: "Draft.Health.issuedAt",
        notes: "Draft.Health.notes",
    },
    COURSE: {
        courseName: "Draft.Course.courseName",
        institution: "Draft.Course.institution",
        startDate: "Draft.Course.startDate",
        endDate: "Draft.Course.endDate",
        certificateNumber: "Draft.Course.certificateNumber",
        grade: "Draft.Course.grade",
    },
    SEA_SERVICE: {
        vesselName: "Draft.SeaService.vesselName",
        vesselType: "Draft.SeaService.vesselType",
        flag: "Draft.SeaService.flag",
        rank: "Draft.SeaService.rank",
        signOnDate: "Draft.SeaService.signOnDate",
        signOffDate: "Draft.SeaService.signOffDate",
        company: "Draft.SeaService.company",
        grt: "Draft.SeaService.grt",
        mainEngine: "Draft.SeaService.mainEngine",
        remarks: "Draft.SeaService.remarks",
    },
};

/**
 * Clear all draft fields for a specific section
 * @param {Object} methods - React Hook Form methods
 * @param {string} section - Section name (CERTIFICATE, DOCUMENT, etc.)
 */
export const clearDraftSection = (methods, section) => {
    const paths = DRAFT_PATHS[section];
    if (!paths) {
        console.warn(`Unknown draft section: ${section}`);
        return;
    }

    Object.values(paths).forEach((path) => {
        methods.setValue(path, "");
    });
};

/**
 * Clear all draft fields across all sections
 * @param {Object} methods - React Hook Form methods
 */
export const clearAllDrafts = (methods) => {
    Object.keys(DRAFT_PATHS).forEach((section) => {
        clearDraftSection(methods, section);
    });
};

/**
 * Check if any draft fields have values
 * @param {Object} methods - React Hook Form methods
 * @returns {boolean} True if any draft has data
 */
export const hasDraftData = (methods) => {
    const draftData = methods.getValues("Draft");
    if (!draftData) return false;

    return Object.values(draftData).some((section) => {
        if (typeof section !== "object") return false;
        return Object.values(section).some((value) => {
            if (typeof value === "string") return value.trim() !== "";
            return value != null;
        });
    });
};

/**
 * Get draft data for a specific section
 * @param {Object} methods - React Hook Form methods
 * @param {string} section - Section name
 * @returns {Object} Draft data or empty object
 */
export const getDraftData = (methods, section) => {
    const paths = DRAFT_PATHS[section];
    if (!paths) return {};

    const draft = {};
    Object.entries(paths).forEach(([key, path]) => {
        const value = methods.getValues(path);
        if (value) draft[key] = value;
    });

    return draft;
};

/**
 * Validate that form data doesn't contain Draft fields
 * Use before saving or submitting
 */
export const validateNoDrafts = (data) => {
    if (data && typeof data === "object" && "Draft" in data) {
        console.error("⚠️ Draft fields detected in form data:", data.Draft);
        return false;
    }
    return true;
};