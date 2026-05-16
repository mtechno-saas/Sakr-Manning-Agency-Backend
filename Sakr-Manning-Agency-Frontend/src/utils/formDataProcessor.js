// utils/formDataProcessor.js
import * as XLSX from "xlsx";

// Export form data as JSON file
export const exportFormDataAsJSON = async (formData) => {
  try {
    const applicationData = {
      metadata: {
        applicationType: "Maritime Employment Application",
        company: "Sakr Manning Agency",
        submissionDate: new Date().toISOString(),
        version: "1.0",
      },
      applicantData: formData,
    };

    const timestamp = new Date()
      .toISOString()
      .slice(0, 16)
      .replace(/[:-]/g, "");
    const applicantName = formData.fullName
      ? formData.fullName.replace(/\s+/g, "_").toLowerCase()
      : "applicant";

    const filename = `sakr_application_${applicantName}_${timestamp}.json`;
    const blob = new Blob([JSON.stringify(applicationData, null, 2)], {
      type: "application/json",
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    return {
      success: true,
      message: "Application data exported successfully",
      filename,
    };
  } catch (error) {
    console.error("Export failed:", error);
    return {
      success: false,
      message: "Failed to export application data: " + error.message,
    };
  }
};

// ——— Helpers for Excel Export ———

/** Convert a flat object into a 2-column array [[Label, Value], …] */
const flatToRows = (obj, excludeKeys = []) => {
  const rows = [];
  for (const [key, value] of Object.entries(obj)) {
    if (excludeKeys.includes(key)) continue;
    if (value === null || value === undefined) continue;
    if (typeof value === "object") continue; // skip nested objects/arrays
    const label = key
      .replace(/_/g, " ")
      .replace(/([A-Z])/g, " $1")
      .replace(/^\w/, (c) => c.toUpperCase())
      .trim();
    rows.push([label, String(value)]);
  }
  return rows;
};

/** Convert an array of objects into a sheet (header row + data rows) */
const arrayToSheet = (arr) => {
  if (!arr || arr.length === 0) return null;
  // Build header from keys of first item, excluding file/object fields
  const allKeys = [];
  arr.forEach((item) => {
    Object.keys(item).forEach((k) => {
      if (!allKeys.includes(k) && typeof item[k] !== "object") allKeys.push(k);
    });
  });
  const headers = allKeys.map((k) =>
    k
      .replace(/_/g, " ")
      .replace(/([A-Z])/g, " $1")
      .replace(/^\w/, (c) => c.toUpperCase())
      .trim()
  );
  const dataRows = arr.map((item) =>
    allKeys.map((k) => (item[k] != null ? String(item[k]) : ""))
  );
  return [headers, ...dataRows];
};

// ——— Main Excel Export Function ———

/**
 * Export the full form data as a multi-sheet Excel workbook.
 * - "Profile" sheet: flat user fields (2-column key/value)
 * - Separate sheets for each array section (Documents, Certificates, etc.)
 */
export const exportFormDataAsExcel = async (formData) => {
  try {
    const wb = XLSX.utils.book_new();

    // Array field keys — these get their own sheets
    const arrayFields = [
      { key: "documents", title: "Documents" },
      { key: "certificates", title: "Certificates" },
      { key: "health", title: "Health" },
      { key: "courses", title: "Courses" },
      { key: "seaServices", title: "Sea Service" },
      { key: "workExperiences", title: "Work Experience" },
      { key: "references", title: "References" },
    ];
    const arrayKeys = arrayFields.map((f) => f.key);

    // Also exclude declaration (nested object) — we'll flatten it separately
    const excludeFromProfile = [...arrayKeys, "declaration"];

    // 1. Profile sheet (flat fields as 2-col table)
    const profileRows = [["Field", "Value"], ...flatToRows(formData, excludeFromProfile)];

    // If declaration exists, append its fields
    if (formData.declaration && typeof formData.declaration === "object") {
      profileRows.push([]); // empty row separator
      profileRows.push(["— Declaration —", ""]);
      flatToRows(formData.declaration).forEach((r) => profileRows.push(r));
    }

    const profileSheet = XLSX.utils.aoa_to_sheet(profileRows);
    // Set column widths
    profileSheet["!cols"] = [{ wch: 30 }, { wch: 50 }];
    XLSX.utils.book_append_sheet(wb, profileSheet, "Profile");

    // 2. Array sheets
    arrayFields.forEach(({ key, title }) => {
      const arr = formData[key];
      if (!arr || !Array.isArray(arr) || arr.length === 0) return;
      const sheetData = arrayToSheet(arr);
      if (!sheetData) return;
      const ws = XLSX.utils.aoa_to_sheet(sheetData);
      // Auto-width columns
      ws["!cols"] = sheetData[0].map(() => ({ wch: 20 }));
      XLSX.utils.book_append_sheet(wb, ws, title);
    });

    // 3. Generate & download
    const wbOut = XLSX.write(wb, { bookType: "xlsx", type: "array" });
    const blob = new Blob([wbOut], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });

    const timestamp = new Date()
      .toISOString()
      .slice(0, 16)
      .replace(/[:-]/g, "");
    const applicantName = formData.fullName
      ? formData.fullName.replace(/\s+/g, "_").toLowerCase()
      : "applicant";
    const filename = `sakr_profile_${applicantName}_${timestamp}.xlsx`;

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    return { success: true, message: "Profile exported successfully", filename };
  } catch (error) {
    console.error("Excel export failed:", error);
    return { success: false, message: "Failed to export: " + error.message };
  }
};