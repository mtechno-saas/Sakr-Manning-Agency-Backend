// utils/fileHelpers.js
// Shared file utility functions used by modals and FileUpload component
import { config } from "../services/Auth/config";

/**
 * Resolve a full URL for a media file (image, document, etc.)
 * Handles both relative paths from backend and already absolute URLs.
 * 
 * @param {string} path - The file path or URL from backend
 * @returns {string|null} The absolute URL or null
 */
export function getMediaUrl(path) {
    if (!path) return null;
    if (typeof path !== "string") return null;
    
    // If it's already an absolute URL or a data/blob URI, return it
    if (path.startsWith("http://") || path.startsWith("https://") || path.startsWith("data:") || path.startsWith("blob:")) {
        return path;
    }

    // If it looks like a local frontend asset (Vite paths), return it as is
    // This handles imports like ASSETS.LOGO which might resolve to "/assets/..." or "/src/..."
    if (path.startsWith("/assets/") || path.startsWith("/src/") || path.startsWith("/@fs/") || path.startsWith("/@vite/")) {
        return path;
    }

    // Get base URL from config (e.g. "https://api.backend.soon.it/api/")
    // We want the domain part without "/api/"
    const baseUrl = (config.API_BASE_URL || "").replace(/\/api\/?$/, "");
    
    // Ensure path starts with /
    const normalizedPath = path.startsWith("/") ? path : `/${path}`;
    
    return `${baseUrl}${normalizedPath}`;
}


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
