// utils/fileHelpers.js
// Shared file utility functions used by modals and FileUpload component

/**
 * Resolve the existing file URL from an item's data.
 * Backend may store the URL under different field names depending on the model.
 * This function checks all known keys and returns the first valid URL string.
 *
 * @param {Object} data - The item data (e.g., initialData from a modal)
 * @returns {string|null} The resolved file URL or null
 */
export function resolveFileUrl(data) {
    if (!data) return null;
    const FILE_URL_KEYS = ["file_url", "document", "document_file", "file", "attachment"];
    for (const key of FILE_URL_KEYS) {
        const val = data[key];
        if (val && typeof val === "string" && val.length > 0) {
            return val;
        }
    }
    return null;
}

/**
 * Extract a human-readable file name from a URL.
 *
 * @param {string} url - The file URL
 * @returns {string} The extracted filename or a fallback
 */
export function getFileNameFromUrl(url) {
    if (!url) return "Uploaded file";
    try {
        const pathname = new URL(url, "https://placeholder.com").pathname;
        const filename = pathname.split("/").pop();
        return filename ? decodeURIComponent(filename) : "Uploaded file";
    } catch {
        const segments = url.split("/");
        return segments[segments.length - 1] || "Uploaded file";
    }
}
