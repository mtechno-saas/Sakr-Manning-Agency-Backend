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

/**
 * Maps SakrForm data to Backend API Structure
 */
// export const mapFormToApiData = (formData) => {
//   // 1. Main User Profile Data (PATCH /api/users/:id/)
//   const userProfile = {
//     // Position
//     application_for_position: formData.applicationForPosition,
//     expected_salary: formData.expectedSalary,
//     last_update_date: formData.lastUpdateDate,

//     // Personal
//     first_name: formData.fullName, // Assuming full name goes to first_name based on docs, or split it if needed
//     date_of_birth: formData.dateOfBirth,
//     marital_status: formData.maritalStatus?.toUpperCase(), // API expects "SINGLE" or "MARRIED"
//     nationality: formData.nationality,
//     weight_kg: Number(formData.weight),
//     height_cm: Number(formData.height),
//     overall_size: formData.overallSize,
//     place_of_birth: formData.placeOfBirth,
//     shirt_size: formData.shirtSize,
//     trouser_size: formData.trouserSize,
//     shoes_size: formData.shoesSize,

//     // Contact
//     address: formData.homeAddress,
//     email: formData.email, // Read-only usually, but good to have
//     phone_number: formData.mobile,

//     // Education (Mapping specific fields if User model supports them directly)
//     english_language_level: formData.englishLevel,

//     // Emergency
//     next_of_kin_full_name: formData.kinFullName,
//     next_of_kin_relationship: formData.kinRelationship,
//     next_of_kin_address_country: formData.kinAddress,
//     next_of_kin_phone: formData.kinPhone,
//     next_of_kin_email: formData.kinEmail,
//   };

//   // 2. Separate Arrays for nested API calls
//   const documents =
//     formData.documents?.map((doc) => ({
//       ticket_number: doc.documentNo, // Mapping 'documentNo' to 'ticket_number'
//       type: doc.documentType,
//       expiry_date: doc.expiryDate,
//       issued_date: doc.issuedDate,
//       // Note: File objects cannot be exported to JSON, only their names
//       _fileName: doc.fileName,
//     })) || [];

//   const certificates =
//     formData.certificates?.map((cert) => ({
//       name: cert.certificateName,
//       number: cert.number,
//       issued_date: cert.issuedDate,
//       expiry_date: cert.expiryDate,
//       issued_by: cert.issuedBy,
//       issued_at: cert.issuedAt,
//     })) || [];

//   const seaService =
//     formData.seaService?.map((sea) => ({
//       company_name: sea.companyName,
//       rank: sea.rank,
//       vessel_name_imo: sea.vesselName,
//       signed_on: sea.signedOn,
//       signed_off: sea.signedOff,
//       period: sea.period,
//       vessel_type: sea.vesselType,
//       dwt_grt: sea.dwtGrt,
//       engine_type_bh_kw: sea.engineType, // Mapping
//       reason_for_sign_off: sea.reasonForSignOff,
//     })) || [];

//   return {
//     userProfile,
//     documents,
//     certificates,
//     seaService,
//     // Add other arrays (health, courses) as needed
//   };
// };

/////////////////////////////////////////////////

// utils/formDataProcessor.js

/**
 * 🔄 TRANSFORMER: Maps React Form Data (camelCase) to Backend API Data (snake_case)
 * Based on API_DOCUMENTATION.md requirements for Users, SeaService, and Certificates.
 */
// export const mapFormToApiData = (formData) => {
//   if (!formData) return null;

//   // 1. Helper to safely split names
//   const splitName = (fullName) => {
//     if (!fullName) return { first: "", last: "" };
//     const parts = fullName.trim().split(" ");
//     return {
//       first: parts[0],
//       last: parts.slice(1).join(" ") || "",
//     };
//   };

//   const nameParts = splitName(formData.fullName);

//   // 2. Main User Profile Object (Matches PATCH /api/users/<id>/)
//   const userProfile = {
//     // --- Personal Information ---
//     first_name: formData.firstName || nameParts.first,
//     last_name: formData.lastName || nameParts.last,
//     // Note: The API docs mention 'name' or 'first_name', we send both standard fields

//     date_of_birth: formData.dateOfBirth, // YYYY-MM-DD
//     place_of_birth: formData.placeOfBirth,
//     nationality: formData.nationality,
//     marital_status: formData.maritalStatus?.toUpperCase(), // API Requires UPPERCASE (SINGLE/MARRIED)

//     // --- Physical Data (snake_case from API docs) ---
//     weight_kg: formData.weight ? Number(formData.weight) : null,
//     height_cm: formData.height ? Number(formData.height) : null,
//     overall_size: formData.overallSize,
//     shirt_size: formData.shirtSize,
//     trouser_size: formData.trouserSize,
//     shoes_size: formData.shoesSize,

//     // --- Position & Salary ---
//     // These might need specific backend fields or be stored in a separate application model
//     // Mapping them to generic fields for now based on typical Django user models
//     application_for_position: formData.applicationForPosition,
//     expected_salary: formData.expectedSalary,

//     // --- Contact Information ---
//     address: formData.homeAddress, // Maps to 'address' in User model
//     phone_number: formData.mobile, // Maps to 'phone_number'
//     email: formData.email, // Should match login email

//     // --- Emergency Contact (Next of Kin) ---
//     next_of_kin_full_name: formData.kinFullName,
//     next_of_kin_relationship: formData.kinRelationship,
//     next_of_kin_phone: formData.kinPhone,
//     next_of_kin_email: formData.kinEmail,
//     next_of_kin_address_country: formData.kinAddress,

//     // --- Education ---
//     english_language_level: formData.englishLevel,
//   };

//   // Remove null/undefined/empty string keys from userProfile to avoid overwriting existing data
//   Object.keys(userProfile).forEach((key) => {
//     if (
//       userProfile[key] === null ||
//       userProfile[key] === undefined ||
//       userProfile[key] === ""
//     ) {
//       delete userProfile[key];
//     }
//   });

//   // 3. Map Arrays for Child Models (SeaService, Certificates, Documents)

//   // Sea Service -> POST /api/references-sea-services/sea-service/
//   const seaService = (formData.seaService || []).map((item) => ({
//     company_name: item.companyName,
//     rank: item.rank,
//     vessel_name_imo: item.vesselName,
//     signed_on: item.signedOn,
//     signed_off: item.signedOff,
//     period: item.period,
//     vessel_type: item.vesselType,
//     dwt_grt: item.dwtGrt,
//     engine_type_bh_kw: item.engineType || item.bhKw, // Handling variation
//     reason_for_sign_off: item.reasonForSignOff,
//     flag: item.flag,
//   }));

//   // Certificates -> POST /api/certificates-ranks/certificates/
//   const certificates = (formData.certificates || []).map((item) => ({
//     name: item.certificateName,
//     number: item.number,
//     issued_date: item.issuedDate,
//     expiry_date: item.expiryDate,
//     issued_by: item.issuedBy,
//     issued_at: item.issuedAt,
//     // Note: 'file' object is stripped here as it can't be JSON stringified
//     _hasFile: !!item.file,
//   }));

//   // Documents -> POST /api/tickets-papers/tickets/
//   const documents = (formData.documents || []).map((item) => ({
//     ticket_number: item.documentNo, // Mapping documentNo to ticket_number based on API docs
//     type: item.documentType,
//     issued_date: item.issuedDate,
//     expiry_date: item.expiryDate,
//     issuing_authority: item.issuingAuthority,
//     place_of_issue: item.placeOfIssue,
//     _hasFile: !!item.file,
//   }));

//   return {
//     user_profile: userProfile,
//     sea_service: seaService,
//     certificates: certificates,
//     documents: documents,
//   };
// };

// ------------------------------------------------------------------
// Existing JSON Export (Updated to use the Mapper)
// ------------------------------------------------------------------

// export const exportFormDataAsJSON = async (formData) => {
//   try {
//     // 1. Map the data first to ensure it matches backend structure
//     const apiReadyData = mapFormToApiData(formData);

//     const applicationData = {
//       metadata: {
//         applicationType: "Maritime Employment Application",
//         company: "Sakr Manning Agency",
//         submissionDate: new Date().toISOString(),
//         version: "2.0 (API Compatible)",
//       },
//       // Save the mapped data
//       data: apiReadyData,
//       // Keep original for debugging/reloading form
//       originalFormData: formData,
//     };

//     // Generate filename
//     const timestamp = new Date()
//       .toISOString()
//       .slice(0, 16)
//       .replace(/[:-]/g, "");
//     const applicantName = formData.fullName
//       ? formData.fullName.replace(/\s+/g, "_").toLowerCase()
//       : "applicant";
//     const filename = `sakr_application_${applicantName}_${timestamp}.json`;

//     // Create and download file
//     const blob = new Blob([JSON.stringify(applicationData, null, 2)], {
//       type: "application/json",
//     });

//     const url = URL.createObjectURL(blob);
//     const link = document.createElement("a");
//     link.href = url;
//     link.download = filename;

//     document.body.appendChild(link);
//     link.click();
//     document.body.removeChild(link);
//     URL.revokeObjectURL(url);

//     return {
//       success: true,
//       message: "Application data exported successfully",
//       filename,
//     };
//   } catch (error) {
//     console.error("Export failed:", error);
//     return {
//       success: false,
//       message: "Failed to export application data: " + error.message,
//     };
//   }
// };

// export default {
//   mapFormToApiData,
//   exportFormDataAsJSON,
// };
