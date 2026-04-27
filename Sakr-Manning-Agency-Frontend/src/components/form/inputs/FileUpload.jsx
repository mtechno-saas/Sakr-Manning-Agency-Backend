// components/inputs/FileUpload.jsx
import React, { useState, useRef, useMemo } from "react";
import { X, FileText, Upload, ExternalLink, Paperclip, Download, Eye, Image } from "lucide-react";
import PropTypes from "prop-types";

/**
 * Production-Ready FileUpload Component
 *
 * Features:
 * - Drag & drop with click-to-browse
 * - File type validation (extension + MIME type)
 * - File size validation
 * - Existing file URL preview (for edit mode) with download & preview
 * - Auto-derived file name from URL when not provided
 * - Image thumbnail preview for jpg/png files
 * - File name + size display after selection
 * - Remove / replace support
 * - Handles string URL values (from backend) as existing files
 *
 * @param {File|string|null} value - Currently selected file object or URL string
 * @param {function} onChange - Callback (file|null) => void
 * @param {string[]} accept - Accepted file extensions e.g. ['.pdf', '.jpg']
 * @param {number} maxSizeMB - Max file size in MB (default 10)
 * @param {string} placeholder - Drop-zone placeholder text
 * @param {string|null} existingFileUrl - URL of a previously uploaded file (edit mode)
 * @param {string|null} existingFileName - Display name for the existing file
 * @param {string|null} label - Optional label displayed above the drop zone
 */
export function FileUpload({
  value,
  onChange,
  accept = [".pdf", ".jpg", ".jpeg", ".png"],
  maxSizeMB = 10,
  placeholder = "Click to upload or drag & drop relevant document",
  existingFileUrl = null,
  existingFileName = null,
  label = null,
}) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  // Map extensions → expected MIME types for extra validation
  const MIME_MAP = {
    ".pdf": ["application/pdf"],
    ".jpg": ["image/jpeg"],
    ".jpeg": ["image/jpeg"],
    ".png": ["image/png"],
    ".doc": ["application/msword"],
    ".docx": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
  };

  // IMAGE extensions for preview
  const IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"];

  /**
   * Extract file name from a URL string
   */
  const getFileNameFromUrl = (url) => {
    if (!url) return "Uploaded file";
    try {
      const pathname = new URL(url, "https://placeholder.com").pathname;
      const filename = pathname.split("/").pop();
      return filename ? decodeURIComponent(filename) : "Uploaded file";
    } catch {
      // Fallback: try to get last segment after /
      const segments = url.split("/");
      return segments[segments.length - 1] || "Uploaded file";
    }
  };

  /**
   * Check if URL points to an image file
   */
  const isImageUrl = (url) => {
    if (!url) return false;
    const lower = url.toLowerCase().split("?")[0]; // strip query params
    return IMAGE_EXTENSIONS.some((ext) => lower.endsWith(ext));
  };

  // Determine what to render: new file, existing file URL, or empty drop zone
  // value can be a File object, a string URL (from backend), or null
  const isValueStringUrl = typeof value === "string" && value.length > 0;
  const hasNewFile = !!value && !isValueStringUrl;

  // Resolve the effective existing file URL:
  // 1. If value is a string URL, use it
  // 2. Otherwise fall back to the existingFileUrl prop
  const effectiveExistingUrl = isValueStringUrl ? value : existingFileUrl;
  const hasExistingFile = !hasNewFile && !!effectiveExistingUrl;

  // Derive filename: use provided name, or extract from URL
  const displayFileName = useMemo(() => {
    if (existingFileName) return existingFileName;
    return getFileNameFromUrl(effectiveExistingUrl);
  }, [existingFileName, effectiveExistingUrl]);

  const validateFile = (file) => {
    // 1. Size check
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      return `File size must be less than ${maxSizeMB}MB. Current: ${formatFileSize(file.size)}`;
    }

    // 2. Extension check
    const fileExtension = `.${file.name.split(".").pop().toLowerCase()}`;
    if (!accept.includes(fileExtension)) {
      return `File type "${fileExtension}" is not allowed. Accepted: ${accept.join(", ")}`;
    }

    // 3. MIME-type check (prevents renamed malicious files)
    const allowedMimes = accept.flatMap((ext) => MIME_MAP[ext] || []);
    if (allowedMimes.length > 0 && file.type && !allowedMimes.includes(file.type)) {
      return `File MIME type "${file.type}" does not match the expected format`;
    }

    return null;
  };

  const handleFile = (file) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setError("");
    onChange(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      // Only accept the first file (single-file upload)
      handleFile(files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleInputChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleRemove = (e) => {
    e.stopPropagation();
    onChange(null);
    setError("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleDownload = (e) => {
    e.stopPropagation();
    if (effectiveExistingUrl) {
      const link = document.createElement("a");
      link.href = effectiveExistingUrl;
      link.download = displayFileName;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handlePreview = (e) => {
    e.stopPropagation();
    if (effectiveExistingUrl) {
      window.open(effectiveExistingUrl, "_blank", "noopener,noreferrer");
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  return (
    <div className="w-full">
      {/* Optional Label */}
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          {label}
        </label>
      )}

      {/* Drop Zone */}
      <div
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`
                    relative border-2 border-dashed rounded-lg p-6
                    transition-all duration-200 cursor-pointer
                    ${isDragging
            ? "border-blue-500 bg-blue-50"
            : hasNewFile
              ? "border-green-300 bg-green-50"
              : hasExistingFile
                ? "border-blue-200 bg-blue-50/50"
                : "border-gray-300 hover:border-gray-400 bg-white"
          }
                `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept.join(",")}
          onChange={handleInputChange}
          className="hidden"
          aria-label="File upload"
        />

        {hasNewFile ? (
          /* ── New File Selected ── */
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <FileText className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900 truncate max-w-[280px]">
                  {value.name}
                </p>
                <p className="text-xs text-gray-500">
                  {formatFileSize(value.size)}
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={handleRemove}
              className="p-2 hover:bg-red-50 rounded-lg transition-colors group"
              aria-label="Remove file"
            >
              <X className="w-5 h-5 text-gray-400 group-hover:text-red-500" />
            </button>
          </div>
        ) : hasExistingFile ? (
          /* ── Existing File (edit mode) ── */
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {/* Thumbnail preview for images */}
              {isImageUrl(effectiveExistingUrl) ? (
                <div className="w-12 h-12 rounded-lg overflow-hidden border border-blue-200 flex-shrink-0">
                  <img
                    src={effectiveExistingUrl}
                    alt={displayFileName}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      // Fallback to icon if image fails to load
                      e.target.style.display = "none";
                      e.target.parentElement.innerHTML = '<div class="w-full h-full flex items-center justify-center bg-blue-100"><svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg></div>';
                    }}
                  />
                </div>
              ) : (
                <div className="p-2 bg-blue-100 rounded-lg">
                  <FileText className="w-6 h-6 text-blue-600" />
                </div>
              )}
              <div>
                <p className="text-sm font-medium text-gray-700 truncate max-w-[180px]">
                  {displayFileName}
                </p>
                {/* Action buttons row */}
                <div className="flex items-center gap-3 mt-1">
                  <button
                    type="button"
                    onClick={handlePreview}
                    className="text-xs text-blue-600 hover:text-blue-800 underline inline-flex items-center gap-1 transition-colors"
                    title="Preview file in new tab"
                  >
                    <Eye className="w-3 h-3" />
                    Preview
                  </button>
                  <button
                    type="button"
                    onClick={handleDownload}
                    className="text-xs text-green-600 hover:text-green-800 underline inline-flex items-center gap-1 transition-colors"
                    title="Download file"
                  >
                    <Download className="w-3 h-3" />
                    Download
                  </button>
                </div>
              </div>
            </div>
            <span className="text-xs text-gray-400 italic">Click to replace</span>
          </div>
        ) : (
          /* ── Empty Drop Zone ── */
          <div className="flex flex-col items-center justify-center text-center py-2">
            <Paperclip className="w-5 h-5 text-gray-500 mb-2 transform -rotate-45" />
            <p className="text-[13px] text-gray-500">
              <span className="text-blue-500 font-medium underline cursor-pointer hover:text-blue-600 transition-colors">Click</span> to upload or drag & drop relevant document
            </p>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <p className="mt-2 text-sm text-red-600 flex items-center gap-1">
          <span className="text-red-500">⚠</span>
          {error}
        </p>
      )}
    </div>
  );
}

FileUpload.propTypes = {
  value: PropTypes.oneOfType([PropTypes.object, PropTypes.string]),
  onChange: PropTypes.func.isRequired,
  accept: PropTypes.arrayOf(PropTypes.string),
  maxSizeMB: PropTypes.number,
  placeholder: PropTypes.string,
  existingFileUrl: PropTypes.string,
  existingFileName: PropTypes.string,
  label: PropTypes.string,
};