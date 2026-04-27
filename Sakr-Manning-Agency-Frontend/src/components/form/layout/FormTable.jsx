// components/common/CrudTable.jsx
import React from "react";
import { Edit, Trash2, Paperclip } from "lucide-react";
import PropTypes from "prop-types";

/**
 * CrudTable - Redesigned CRUD table component matching the UI design
 *
 * Features:
 * - Clean, modern design with light blue header (#D4E7F4)
 * - Sticky first and last columns for horizontal scrolling
 * - Attachment column with paperclip icon
 * - Responsive horizontal scroll
 * - Edit/Delete actions
 *
 * @param {Array} data - Array of data objects
 * @param {Array} columns - Column definitions [{ key, label, render? }]
 * @param {Function} onEdit - Edit handler (item) => void
 * @param {Function} onDelete - Delete handler (itemId) => void
 * @param {Function} onAttachment - Attachment handler (item) => void
 * @param {string|null} editingId - Currently editing item ID
 * @param {string} emptyMessage - Message when no data
 * @param {boolean} showAttachment - Show attachment column (default: true)
 */
export function CrudTable({
    data = [],
    columns = [],
    onEdit,
    onDelete,
    onAttachment,
    editingId = null,
    emptyMessage = "No items added yet.",
    showAttachment = true,
}) {
    const formatDate = (dateString) => {
        if (!dateString) return "";
        try {
            // Ensure we're working with a string
            const str = String(dateString).trim();
            // Strip time portion if present (e.g. "2031-10-10T00:00:00Z")
            const dateOnly = str.split("T")[0];
            // Handle YYYY-MM-DD format from backend
            const parts = dateOnly.split("-");
            if (parts.length === 3 && parts[0].length === 4) {
                return `${parts[2]}-${parts[1]}-${parts[0]}`; // DD-MM-YYYY
            }
            const date = new Date(str);
            if (isNaN(date.getTime())) return str;
            const dd = String(date.getDate()).padStart(2, '0');
            const mm = String(date.getMonth() + 1).padStart(2, '0');
            const yyyy = date.getFullYear();
            return `${dd}-${mm}-${yyyy}`;
        } catch {
            return String(dateString);
        }
    };

    const getDocumentTypeLabel = (value) => {
        const types = {
            passport: "Passport",
            seamanBook: "Seaman book",
            otherSeamanBook: "Other Seaman Book",
            visa: "Visa",
            idCard: "ID Card",
            other: "Other",
        };
        return types[value] || value;
    };

    /**
     * Check if a value looks like a date string (YYYY-MM-DD or ISO format)
     */
    const looksLikeDate = (value) => {
        if (!value || typeof value !== "string") return false;
        return /^\d{4}-\d{2}-\d{2}/.test(value.trim());
    };

    /**
     * Resolve the file URL from an item by checking common backend field names.
     * Returns the URL string if found, or null.
     */
    const getFileUrl = (item) => {
        const FILE_URL_KEYS = ["file_url", "document", "document_file", "file", "attachment"];
        for (const key of FILE_URL_KEYS) {
            const val = item[key];
            if (val && typeof val === "string" && val.trim() !== "") {
                return val;
            }
        }
        return null;
    };

    const renderCellContent = (item, column) => {
        // Custom render function
        if (column.render) {
            return column.render(item[column.key], item);
        }

        const value = item[column.key];

        // Auto-format dates (by column key name OR by value pattern)
        if (value && (column.key.toLowerCase().includes("date") || looksLikeDate(value))) {
            return formatDate(value);
        }

        // Auto-format document types
        if (column.key === "documentType" && value) {
            return getDocumentTypeLabel(value);
        }

        return value || "-";
    };

    if (data.length === 0) {
        return (
            <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                <p className="text-gray-500 text-lg">{emptyMessage}</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            {/* Scrollable container */}
            <div className="overflow-x-auto relative crud-table-wrapper">
                <table className="w-full border-collapse">
                    {/* Table Header - Light Blue Background matching design */}
                    <thead className="bg-[#CFDBEC]">
                        <tr>
                            {/* First Column (Sticky) */}
                            <th className="sticky left-0 z-20 bg-[#CFDBEC] px-4 py-3 text-left text-sm font-medium text-gray-900 border-r border-gray-300">
                                {columns[0]?.label || "Type"}
                            </th>

                            {/* Middle Columns (Scrollable) */}
                            {columns.slice(1).map((column, idx) => (
                                <th
                                    key={column.key || idx}
                                    className="px-4 py-3 text-left text-sm font-medium text-gray-900 whitespace-nowrap border-r border-gray-300"
                                >
                                    {column.label}
                                </th>
                            ))}

                            {/* Attachment Column */}
                            {showAttachment && (
                                <th className="px-4 py-3 text-left text-sm font-medium text-gray-900 whitespace-nowrap border-r border-gray-300">
                                    Attachment
                                </th>
                            )}

                            {/* Action Column (Sticky) */}
                            <th className="sticky right-0 z-20 bg-[#CFDBEC] px-4 py-3 text-left text-sm font-medium text-gray-900">
                                Action
                            </th>
                        </tr>
                    </thead>

                    {/* Table Body */}
                    <tbody className="divide-y divide-gray-200">
                        {data.map((item, rowIndex) => {
                            const fileUrl = getFileUrl(item);
                            const isEvenRow = rowIndex % 2 === 1;
                            const rowBg = editingId === item.id
                                ? "bg-blue-50"
                                : isEvenRow
                                    ? "bg-[#EBF2FA]"
                                    : "bg-white";

                            return (
                                <tr
                                    key={item.id}
                                    className={`
                    transition-colors
                      ${rowBg}
                    `}
                                >
                                    {/* First Column (Sticky) */}
                                    <td className={`sticky left-0 z-10 px-4 py-3 text-sm text-gray-900 border-r border-gray-200 ${rowBg}`}>
                                        {renderCellContent(item, columns[0])}
                                    </td>

                                    {/* Middle Columns (Scrollable) */}
                                    {columns.slice(1).map((column, idx) => (
                                        <td
                                            key={column.key || idx}
                                            className="px-4 py-3 text-sm text-gray-900 whitespace-nowrap border-r border-gray-200"
                                        >
                                            {renderCellContent(item, column)}
                                        </td>
                                    ))}

                                    {/* Attachment Column */}
                                    {showAttachment && (
                                        <td className="px-4 py-3 text-center border-r border-gray-200">
                                            {fileUrl ? (
                                                <a
                                                    href={fileUrl}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="inline-flex items-center justify-center text-blue-600 hover:text-blue-800 transition-colors"
                                                    title="View attachment"
                                                    aria-label="View attachment"
                                                >
                                                    <Paperclip className="w-5 h-5" />
                                                </a>
                                            ) : (
                                                <span
                                                    className="inline-flex items-center justify-center text-gray-300"
                                                    title="No attachment"
                                                    aria-label="No attachment"
                                                >
                                                    <Paperclip className="w-5 h-5" />
                                                </span>
                                            )}
                                        </td>
                                    )}

                                    {/* Action Buttons (Sticky) */}
                                    <td className={`sticky right-0 z-10 px-4 py-3 whitespace-nowrap ${rowBg}`}>
                                        <div className="flex items-center justify-center gap-3">
                                            <button
                                                onClick={() => onEdit?.(item)}
                                                disabled={editingId && editingId !== item.id}
                                                className="text-gray-600 hover:text-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                                title="Edit"
                                                aria-label={`Edit ${columns[0]?.label}`}
                                            >
                                                <Edit className="w-5 h-5" />
                                            </button>
                                            <button
                                                onClick={() => onDelete?.(item.id)}
                                                className="text-gray-600 hover:text-red-600 transition-colors"
                                                title="Delete"
                                                aria-label={`Delete ${columns[0]?.label}`}
                                            >
                                                <Trash2 className="w-5 h-5" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

CrudTable.propTypes = {
    data: PropTypes.array,
    columns: PropTypes.arrayOf(
        PropTypes.shape({
            key: PropTypes.string.isRequired,
            label: PropTypes.string.isRequired,
            render: PropTypes.func,
        })
    ).isRequired,
    onEdit: PropTypes.func,
    onDelete: PropTypes.func,
    onAttachment: PropTypes.func,
    editingId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    emptyMessage: PropTypes.string,
    showAttachment: PropTypes.bool,
};