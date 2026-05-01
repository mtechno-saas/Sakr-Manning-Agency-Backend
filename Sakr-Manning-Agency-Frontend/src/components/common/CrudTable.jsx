import React from "react";
import { Edit, Trash2 } from "lucide-react";
import { cx } from "../../hooks/useFormField";
import { ASSETS } from "../../utils/constants";

/**
 * CrudTable - Reusable CRUD table component
 *
 * Props:
 *  - data: array of objects to display
 *  - columns: array of column definitions { key, label, render? }
 *  - onEdit: callback when editing item (item) => void
 *  - onDelete: callback when deleting item (itemId) => void
 *  - editingId: ID of currently editing item (for highlighting)
 *  - emptyMessage: message to show when no data
 *  - className: custom classes
 */

export function CrudTable({
  data = [],
  columns = [],
  onEdit,
  onDelete,
  editingId = null,
  emptyMessage = "No items added yet.",
  className = "",
}) {
  const formatDate = (dateString) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-GB");
  };

  const getDocumentTypeLabel = (value) => {
    const types = {
      passport: "Passport",
      seamanBook: "Seaman Book",
      visa: "Visa",
      idCard: "ID Card",
    };
    return types[value] || value;
  };

  const renderCellContent = (item, column) => {
    if (column.render) {
      return column.render(item[column.key], item);
    }

    const value = item[column.key];

    // Handle special formatting
    if (column.key.includes("Date") && value) {
      return formatDate(value);
    }

    if (column.key === "documentType" && value) {
      return getDocumentTypeLabel(value);
    }

    return value || "";
  };

  return (
    <div
      className={cx(
        "bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden",
        className
      )}
    >
      <div className="overflow-x-auto">
        <table className="w-full justify-center">
          {/* Table Header */}
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              {columns.map((column, index) => (
                <th
                  key={column.key || index}
                  className="px-4 py-3 text-left text-lg font-medium text-[#4986D0] uppercase tracking-wider"
                >
                  {column.label}
                </th>
              ))}
              <th className="px-4 py-3 text-left text-lg font-medium text-[#4986D0] uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>

          {/* Table Body */}
          <tbody className="bg-white divide-y divide-gray-100">
            {data.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length + 1}
                  className="px-4 py-8 text-center text-gray-500"
                >
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              data.map((item) => (
                <tr
                  key={item.id}
                  className={cx(
                    "hover:bg-gray-50",
                    editingId === item.id ? "bg-blue-50" : ""
                  )}
                >
                  {columns.map((column, index) => (
                    <td
                      key={column.key || index}
                      className="px-4 py-3 whitespace-nowrap"
                    >
                      {index === 0 ? (
                        // First column gets the blue dot indicator
                        <div className="flex items-center">
                          <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                          <span className="text-lg text-gray-900">
                            {renderCellContent(item, column)}
                          </span>
                        </div>
                      ) : (
                        <span className="text-lg text-gray-900">
                          {renderCellContent(item, column)}
                        </span>
                      )}
                    </td>
                  ))}

                  {/* Actions Column */}
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => onEdit?.(item)}
                        disabled={editingId && editingId !== item.id}
                        className={cx(
                          "text-blue-600 hover:text-blue-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
                          editingId === item.id ? "text-blue-800" : ""
                        )}
                        title="Edit"
                      >
                        <Edit className="w-7 h-7" />
                      </button>
                      <button
                        onClick={() => onDelete?.(item.id)}
                        className="text-red-600 hover:text-red-800 transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-7 h-7" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Footer info */}
      {data.length > 0 && (
        <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 text-md text-gray-500">
          Total items: {data.length}
        </div>
      )}
    </div>
  );
}
