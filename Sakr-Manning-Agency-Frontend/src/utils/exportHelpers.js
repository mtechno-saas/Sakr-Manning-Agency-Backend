// utils/exportHelpers.js
// Utilities for exporting data in various formats

/**
 * Export data to CSV format
 * @param {Array} data - Array of objects to export
 * @param {string} filename - Output filename
 * @param {Array} columns - Optional column configuration
 */
export const exportToCSV = (data, filename = "export.csv", columns = null) => {
  if (!data || data.length === 0) {
    console.warn("No data to export");
    return;
  }

  try {
    // Determine columns
    const cols = columns || Object.keys(data[0]);

    // Create CSV header
    const header = cols.map((col) => `"${col}"`).join(",");

    // Create CSV rows
    const rows = data.map((row) => {
      return cols
        .map((col) => {
          const value = row[col];
          // Handle null/undefined
          if (value == null) return '""';
          // Escape quotes and wrap in quotes
          return `"${String(value).replace(/"/g, '""')}"`;
        })
        .join(",");
    });

    // Combine header and rows
    const csv = [header, ...rows].join("\n");

    // Create blob and download
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    downloadBlob(blob, filename);
  } catch (error) {
    console.error("Error exporting to CSV:", error);
    throw error;
  }
};

// /**
//  * Export data to JSON format
//  * @param {Array|Object} data - Data to export
//  * @param {string} filename - Output filename
//  */
// export const exportToJSON = (data, filename = "export.json") => {
//   if (!data) {
//     console.warn("No data to export");
//     return;
//   }

//   try {
//     const json = JSON.stringify(data, null, 2);
//     const blob = new Blob([json], { type: "application/json" });
//     downloadBlob(blob, filename);
//   } catch (error) {
//     console.error("Error exporting to JSON:", error);
//     throw error;
//   }
// };

// // utils/exportHelpers.js
// /**
//  * Export data to CSV format
//  */
// export const exportToCSV = (data, filename = "export.csv") => {
//   if (!data || data.length === 0) {
//     console.warn("No data to export");
//     return;
//   }

//   // Get headers from first object
//   const headers = Object.keys(data[0]);

//   // Create CSV content
//   const csvContent = [
//     headers.join(","), // Header row
//     ...data.map((row) =>
//       headers
//         .map((header) => {
//           const value = row[header];
//           // Handle commas and quotes in values
//           if (value === null || value === undefined) return "";
//           const stringValue = String(value);
//           if (stringValue.includes(",") || stringValue.includes('"')) {
//             return `"${stringValue.replace(/"/g, '""')}"`;
//           }
//           return stringValue;
//         })
//         .join(",")
//     ),
//   ].join("\n");

//   // Create blob and download
//   const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
//   const link = document.createElement("a");
//   const url = URL.createObjectURL(blob);

//   link.setAttribute("href", url);
//   link.setAttribute("download", filename);
//   link.style.visibility = "hidden";
//   document.body.appendChild(link);
//   link.click();
//   document.body.removeChild(link);
//   URL.revokeObjectURL(url);
// };

/**
 * Export data to JSON format
 */
export const exportToJSON = (data, filename = "export.json") => {
  if (!data) {
    console.warn("No data to export");
    return;
  }

  const jsonContent = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonContent], { type: "application/json" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);

  link.setAttribute("href", url);
  link.setAttribute("download", filename);
  link.style.visibility = "hidden";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Generate PDF-style text report (for browser download)
 * @param {Object} data - Single item data
 * @param {string} filename - Output filename
 * @param {string} title - Report title
 */
export const exportToPDFText = (
  data,
  filename = "cv.txt",
  title = "CV Details"
) => {
  if (!data) {
    console.warn("No data to export");
    return;
  }

  try {
    // Create formatted text report
    const lines = [
      "=".repeat(60),
      title.toUpperCase(),
      "=".repeat(60),
      "",
      `Generated: ${new Date().toLocaleString()}`,
      "",
      "=".repeat(60),
      "",
    ];

    // Add data fields
    Object.entries(data).forEach(([key, value]) => {
      // Skip avatar and id
      if (key === "avatar" || key === "id") return;

      const label =
        key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, " $1");
      lines.push(`${label}: ${value || "N/A"}`);
    });

    lines.push("");
    lines.push("=".repeat(60));

    const text = lines.join("\n");
    const blob = new Blob([text], { type: "text/plain" });
    downloadBlob(blob, filename);
  } catch (error) {
    console.error("Error exporting to PDF text:", error);
    throw error;
  }
};

/**
 * Helper function to trigger download
 * @param {Blob} blob - Blob to download
 * @param {string} filename - Filename
 */
const downloadBlob = (blob, filename) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

/**
 * Copy data to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} Success status
 */
export const copyToClipboard = async (text) => {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      // Fallback for older browsers
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.select();
      const success = document.execCommand("copy");
      document.body.removeChild(textarea);
      return success;
    }
  } catch (error) {
    console.error("Error copying to clipboard:", error);
    return false;
  }
};

/**
 * Format data for export (remove internal fields, format dates)
 * @param {Array} data - Data to format
 * @param {Array} excludeFields - Fields to exclude
 * @returns {Array} Formatted data
 */
export const formatDataForExport = (data, excludeFields = ["id", "avatar"]) => {
  return data.map((item) => {
    const formatted = {};
    Object.entries(item).forEach(([key, value]) => {
      if (!excludeFields.includes(key)) {
        formatted[key] = value;
      }
    });
    return formatted;
  });
};

/**
 * Export data to Excel (.xlsx) format
 * @param {Array} data - Data to export
 * @param {string} filename - Output filename (e.g. "data.xlsx")
 * @param {string} sheetName - Name of the worksheet
 */
export const exportToExcel = (
  data,
  filename = "export.xlsx",
  sheetName = "Sheet1"
) => {
  if (!data || data.length === 0) {
    console.warn("No data to export");
    return;
  }

  try {
    // Dynamic import to avoid build errors if xlsx is not installed yet
    import("xlsx").then((XLSX) => {
      // Create worksheet
      const worksheet = XLSX.utils.json_to_sheet(data);

      // Create workbook
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);

      // Generate buffer and download
      XLSX.writeFile(workbook, filename);
    });
  } catch (error) {
    console.error("Error exporting to Excel:", error);
    throw error;
  }
};

export default {
  exportToCSV,
  exportToExcel,
  exportToJSON,
  exportToPDFText,
  copyToClipboard,
  formatDataForExport,
};
