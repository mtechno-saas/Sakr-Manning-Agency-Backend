// services/Form/userService.js - REFACTORED: Collections route to dedicated endpoints
import api from "../Auth/api";
import { handleApiError } from "../Auth/handlers";
import { mapFormToBackend, mapBackendToFrontend } from "../../utils/formMapper";
import { seaServiceService } from "./seaServiceService";
import { languageService } from "./languageService";
import { courseService } from "./courseService";
import { licenseService } from "./licenseService";
import { vaccinationService } from "./vaccinationService";
import { referenceService } from "./referenceService";
import { declarationService } from "./declarationService";
import { documentService } from "./documentService";
import { nextOfKinService } from "./nextOfKinService";

// Keys that must NEVER be sent in the user PATCH payload
const COLLECTION_KEYS = [
  'sea_services', 'languages', 'courses', 'licenses',
  'vaccinations', 'references', 'declaration', 'documents',
  'certificates', 'work_experience', 'next_of_kin',
];

/** Strip all collection keys from a payload so only flat user fields remain */
const stripCollections = (payload) => {
  const clean = { ...payload };
  COLLECTION_KEYS.forEach(k => delete clean[k]);
  return clean;
};

// Helper to sync a collection using its service
// Returns an array of error messages (empty = all succeeded)
const syncCollectionWithService = async (service, serviceMethods, currentItems, savedItems, idPrefix, serviceName, userId) => {
  const errors = [];

  if (!currentItems || currentItems.length === 0) {
    // Delete all existing items if current is empty but saved has items
    if (savedItems && savedItems.length > 0) {
      for (const item of savedItems) {
        if (item.id && typeof item.id === 'number') {
          try {
            await serviceMethods.delete(item.id, userId);
          } catch (err) {
            console.error(`Failed to delete ${serviceName}:`, err);
            errors.push(`Failed to delete ${serviceName}`);
          }
        }
      }
    }
    return errors;
  }

  // Find items to create (no ID or temp ID)
  const toCreate = currentItems.filter(item => !item.id || String(item.id).startsWith(idPrefix));

  // Find items to update (has numeric ID)
  const toUpdate = currentItems.filter(item => item.id && typeof item.id === 'number');

  // Find items to delete (in saved but not in current)
  const currentIds = currentItems.map(i => i.id).filter(id => id && typeof id === 'number');
  const toDelete = (savedItems || []).filter(item => item.id && !currentIds.includes(item.id));

  // Execute create operations
  for (const item of toCreate) {
    try {
      const result = await serviceMethods.create(userId, item);
      if (!result.success) {
        console.error(`Failed to create ${serviceName}:`, result.error);
        errors.push(`Failed to save new ${serviceName}`);
      }
    } catch (err) {
      console.error(`Failed to create ${serviceName}:`, err);
      errors.push(`Failed to save new ${serviceName}`);
    }
  }

  // Execute update operations
  for (const item of toUpdate) {
    try {
      const result = await serviceMethods.update(item.id, item, userId);
      if (!result.success) {
        console.error(`Failed to update ${serviceName}:`, result.error);
        errors.push(`Failed to update ${serviceName}`);
      }
    } catch (err) {
      console.error(`Failed to update ${serviceName}:`, err);
      errors.push(`Failed to update ${serviceName}`);
    }
  }

  // Execute delete operations
  for (const item of toDelete) {
    try {
      const result = await serviceMethods.delete(item.id, userId);
      if (!result.success) {
        console.error(`Failed to delete ${serviceName}:`, result.error);
        errors.push(`Failed to delete ${serviceName}`);
      }
    } catch (err) {
      console.error(`Failed to delete ${serviceName}:`, err);
      errors.push(`Failed to delete ${serviceName}`);
    }
  }

  return errors;
};

export const userService = {
  /**
   * ✅ LOAD: Fetch complete user profile + all related data
   */
  loadFullUserProfile: async (userId, { raw = false } = {}) => {
    try {
      // Fetch all data in parallel using dedicated service methods
      const [
        userRes,
        seaServicesRes,
        languagesRes,
        coursesRes,
        licensesRes,
        vaccinationsRes,
        referencesRes,
        documentsRes,
        declarationRes,
        nextOfKinRes,
      ] = await Promise.all([
        api.get(`/users/users/${userId}`),
        seaServiceService.getSeaServices(userId),
        languageService.getLanguages(userId),
        courseService.getCourses(userId),
        licenseService.getLicenses(userId),
        vaccinationService.getVaccinations(userId),
        referenceService.getReferences(userId),
        documentService.getDocuments(userId),
        declarationService.getDeclaration(userId),
        nextOfKinService.getNextOfKin(userId),
      ]);

      // Merge all data into user data before mapping
      const userData = {
        ...userRes.data,
        sea_services: seaServicesRes.data || [],
        languages: languagesRes.data || [],
        courses: coursesRes.data || [],
        licenses: licensesRes.data || [],
        vaccinations: vaccinationsRes.data || [],
        references: referencesRes.data || [],
        documents: documentsRes.data || [],
        declaration: declarationRes.data || null,
        next_of_kin: nextOfKinRes.data || [],
      };

      // When raw=true, return backend data as-is (for view modals).
      // When raw=false (default), map to frontend form field names.
      if (raw) {
        return {
          success: true,
          data: userData,
          message: "Profile loaded successfully",
        };
      }

      const mappedData = mapBackendToFrontend(userData);

      return {
        success: true,
        data: mappedData,
        message: "Profile loaded successfully",
      };
    } catch (error) {
      console.error("Load profile error:", error);
      return {
        success: false,
        error: handleApiError(error),
        message: "Failed to load profile",
      };
    }
  },

  /**
   * ✅ SAVE STEP: Save only data relevant to the current step
   */
  saveStepData: async (userId, stepIndex, currentData, lastSavedData) => {
    try {
      const payload = mapFormToBackend(currentData);

      // Destructure ALL collections out — they go to their own endpoints
      const {
        sea_services, languages, courses, licenses,
        vaccinations, references, declaration, documents,
        certificates, work_experience, next_of_kin,
        ...rawUserPayload
      } = payload;

      // Safety: strip any remaining collection keys
      const userPayload = stripCollections(rawUserPayload);

      let savedProfileData = lastSavedData ? mapFormToBackend(lastSavedData) : null;

      if (!savedProfileData) {
        // Fetch latest data for comparison
        const loadedProfile = await userService.loadFullUserProfile(userId);
        if (loadedProfile.success) {
          savedProfileData = mapFormToBackend(loadedProfile.data);
        } else {
          savedProfileData = {}; // Fallback
        }
      }

      // Save flat user fields (profile data) for applicable steps
      // Steps 7 (Courses), 8 (Sea Service), 9 (References), and 10 (Declaration) are purely dedicated endpoints
      if (stepIndex <= 11 && stepIndex !== 7 && stepIndex !== 8 && stepIndex !== 9 && stepIndex !== 10) {

        // Detect if any file fields are File objects (newly selected by user)
        const fileFields = ['profile_image', 'marlins_test_attachment', 'ces_test_attachment'];
        const hasNewFiles = fileFields.some(f => userPayload[f] instanceof File);

        if (hasNewFiles) {
          // Build FormData for multipart upload
          const formData = new FormData();
          Object.entries(userPayload).forEach(([key, value]) => {
            if (value === undefined || value === null) return;
            if (value instanceof File) {
              formData.append(key, value);
            } else if (typeof value === 'object') {
              // Skip non-File objects (e.g. arrays already stripped, but safety check)
            } else {
              formData.append(key, value);
            }
          });
          await api.patch(`/users/users/${userId}/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });
        } else {
          // Remove file fields with string values (already-uploaded URLs) to avoid sending strings to file fields
          fileFields.forEach(f => {
            if (typeof userPayload[f] === 'string') delete userPayload[f];
          });
          await api.patch(`/users/users/${userId}/`, userPayload);
        }
      }

      // Sync Collections based on Step — collect errors
      let syncErrors = [];

      // Step 1: Education -> Languages
      if (stepIndex === 1) {
        const errs = await syncCollectionWithService(
          languageService,
          {
            create: languageService.createLanguage,
            update: languageService.updateLanguage,
            delete: languageService.deleteLanguage,
          },
          languages,
          savedProfileData.languages || [],
          'lang-',
          'language',
          userId
        );
        syncErrors.push(...errs);
      }

      // Step 3: Emergency -> Next of Kin
      if (stepIndex === 3) {
        const errs = await syncCollectionWithService(
          nextOfKinService,
          {
            create: nextOfKinService.createNextOfKin,
            update: nextOfKinService.updateNextOfKin,
            delete: nextOfKinService.deleteNextOfKin,
          },
          next_of_kin,
          savedProfileData.next_of_kin || [],
          'nok-',
          'next_of_kin',
          userId
        );
        syncErrors.push(...errs);
      }

      // Step 4: Documents
      if (stepIndex === 4) {
        const errs = await syncCollectionWithService(
          documentService,
          {
            create: documentService.createDocument,
            update: documentService.updateDocument,
            delete: documentService.deleteDocument,
          },
          documents,
          savedProfileData.documents || [],
          'doc-',
          'document',
          userId
        );
        syncErrors.push(...errs);
      }

      // Step 5: Certificates -> Use licenseService
      if (stepIndex === 5) {
        const errs = await syncCollectionWithService(
          licenseService,
          {
            create: licenseService.createLicense,
            update: licenseService.updateLicense,
            delete: licenseService.deleteLicense,
          },
          licenses,
          savedProfileData.licenses || [],
          'lic-',
          'license',
          userId
        );
        syncErrors.push(...errs);
      }

      // Step 6: Health -> Vaccinations
      if (stepIndex === 6) {
        const errs = await syncCollectionWithService(
          vaccinationService,
          {
            create: vaccinationService.createVaccination,
            update: vaccinationService.updateVaccination,
            delete: vaccinationService.deleteVaccination,
          },
          vaccinations,
          savedProfileData.vaccinations || [],
          'health-',
          'vaccination',
          userId
        );
        syncErrors.push(...errs);
      }

      // Step 7: Courses
      if (stepIndex === 7) {
        const errs = await syncCollectionWithService(
          courseService,
          {
            create: courseService.createCourse,
            update: courseService.updateCourse,
            delete: courseService.deleteCourse,
          },
          courses,
          savedProfileData.courses || [],
          'course-',
          'course',
          userId
        );
        syncErrors.push(...errs);
      }

      // Step 8: Sea Service
      if (stepIndex === 8) {
        const errs = await syncCollectionWithService(
          seaServiceService,
          {
            create: seaServiceService.createSeaService,
            update: seaServiceService.updateSeaService,
            delete: seaServiceService.deleteSeaService,
          },
          sea_services,
          savedProfileData.sea_services || [],
          'sea-',
          'sea_service',
          userId
        );
        syncErrors.push(...errs);
      }

      // Step 9: References
      if (stepIndex === 9) {
        const errs = await syncCollectionWithService(
          referenceService,
          {
            create: referenceService.createReference,
            update: referenceService.updateReference,
            delete: referenceService.deleteReference,
          },
          references,
          savedProfileData.references || [],
          'ref-',
          'reference',
          userId
        );
        syncErrors.push(...errs);
      }

      // Step 10: Declaration (Single Object, not collection)
      if (stepIndex === 10) {
        if (declaration) {
          try {
            const existingId = savedProfileData.declaration?.id || null;
            await declarationService.saveDeclaration(userId, declaration, existingId);
          } catch (err) {
            console.error('Failed to save declaration:', err);
            syncErrors.push('Failed to save declaration');
          }
        }
      }

      // Reload full profile to get updated data
      const fullProfile = await userService.loadFullUserProfile(userId);

      return {
        success: true,
        data: fullProfile.data,
        message: "Step saved successfully",
        syncErrors,
      };

    } catch (error) {
      console.error("Save step error:", error);
      return {
        success: false,
        error: handleApiError(error),
        message: "Failed to save step",
      };
    }
  },

  /**
   * ✅ SAVE COMPLETE: Legacy/Final save
   */
  saveCompleteForm: async (userId, formData) => {
    try {
      // Map form data to backend structure
      const payload = mapFormToBackend(formData);

      // Destructure ALL collections out
      const {
        sea_services, languages, courses, licenses,
        vaccinations, references, declaration, documents,
        certificates, work_experience, next_of_kin,
        ...rawUserPayload
      } = payload;

      // Safety: strip any remaining collection keys
      const userPayload = stripCollections(rawUserPayload);

      // 1. Save main user profile (flat fields only)

      // Detect if any file fields are File objects (newly selected by user)
      const fileFields = ['profile_image', 'marlins_test_attachment', 'ces_test_attachment'];
      const hasNewFiles = fileFields.some(f => userPayload[f] instanceof File);

      if (hasNewFiles) {
        const formDataPayload = new FormData();
        Object.entries(userPayload).forEach(([key, value]) => {
          if (value === undefined || value === null) return;
          if (value instanceof File) {
            formDataPayload.append(key, value);
          } else if (typeof value === 'object') {
            // Skip non-File objects
          } else {
            formDataPayload.append(key, value);
          }
        });
        await api.patch(`/users/users/${userId}/`, formDataPayload, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      } else {
        fileFields.forEach(f => {
          if (typeof userPayload[f] === 'string') delete userPayload[f];
        });
        await api.patch(`/users/users/${userId}/`, userPayload);
      }

      // 2. Sync all collections in parallel
      const loadedProfile = await userService.loadFullUserProfile(userId);
      const savedProfileData = loadedProfile.success ? mapFormToBackend(loadedProfile.data) : {};

      const syncResults = await Promise.all([
        syncCollectionWithService(
          languageService,
          {
            create: languageService.createLanguage,
            update: languageService.updateLanguage,
            delete: languageService.deleteLanguage,
          },
          languages,
          savedProfileData.languages || [],
          'lang-',
          'language',
          userId
        ),
        syncCollectionWithService(
          licenseService,
          {
            create: licenseService.createLicense,
            update: licenseService.updateLicense,
            delete: licenseService.deleteLicense,
          },
          licenses,
          savedProfileData.licenses || [],
          'lic-',
          'license',
          userId
        ),
        syncCollectionWithService(
          vaccinationService,
          {
            create: vaccinationService.createVaccination,
            update: vaccinationService.updateVaccination,
            delete: vaccinationService.deleteVaccination,
          },
          vaccinations,
          savedProfileData.vaccinations || [],
          'vac-',
          'vaccination',
          userId
        ),
        syncCollectionWithService(
          courseService,
          {
            create: courseService.createCourse,
            update: courseService.updateCourse,
            delete: courseService.deleteCourse,
          },
          courses,
          savedProfileData.courses || [],
          'course-',
          'course',
          userId
        ),
        syncCollectionWithService(
          seaServiceService,
          {
            create: seaServiceService.createSeaService,
            update: seaServiceService.updateSeaService,
            delete: seaServiceService.deleteSeaService,
          },
          sea_services,
          savedProfileData.sea_services || [],
          'sea-',
          'sea_service',
          userId
        ),
        syncCollectionWithService(
          referenceService,
          {
            create: referenceService.createReference,
            update: referenceService.updateReference,
            delete: referenceService.deleteReference,
          },
          references,
          savedProfileData.references || [],
          'ref-',
          'reference',
          userId
        ),
        syncCollectionWithService(
          documentService,
          {
            create: documentService.createDocument,
            update: documentService.updateDocument,
            delete: documentService.deleteDocument,
          },
          documents,
          savedProfileData.documents || [],
          'doc-',
          'document',
          userId
        ),
        syncCollectionWithService(
          nextOfKinService,
          {
            create: nextOfKinService.createNextOfKin,
            update: nextOfKinService.updateNextOfKin,
            delete: nextOfKinService.deleteNextOfKin,
          },
          next_of_kin,
          savedProfileData.next_of_kin || [],
          'nok-',
          'next_of_kin',
          userId
        ),
      ]);

      // Aggregate sync errors from all collections
      const syncErrors = syncResults.flat();

      // Declaration (single object)
      if (declaration) {
        try {
          const existingId = savedProfileData.declaration?.id || null;
          await declarationService.saveDeclaration(userId, declaration, existingId);
        } catch (err) {
          console.error('Failed to save declaration:', err);
          syncErrors.push('Failed to save declaration');
        }
      }

      // Reload full profile to get all updated data
      const fullProfile = await userService.loadFullUserProfile(userId);

      return {
        success: true,
        data: fullProfile.data,
        message: "Form saved successfully",
        syncErrors,
      };
    } catch (error) {
      console.error("Save form error:", error);
      console.error("Error details:", error.response?.data);
      return {
        success: false,
        error: handleApiError(error),
        message: "Failed to save form",
      };
    }
  },

  /**
   * ✅ PARTIAL SAVE: For auto-save (only changed flat fields)
   * Collections are NOT auto-saved — they sync on manual step save only.
   */
  savePartialForm: async (userId, currentData, lastSavedData) => {
    try {
      const currentPayload = mapFormToBackend(currentData);
      const lastPayload = mapFormToBackend(lastSavedData);

      // Calculate diff (only send changed fields)
      const diff = {};
      Object.keys(currentPayload).forEach((key) => {
        if (
          JSON.stringify(currentPayload[key]) !==
          JSON.stringify(lastPayload[key])
        ) {
          diff[key] = currentPayload[key];
        }
      });

      // Strip collection keys — they must NOT go to the user endpoint
      const cleanDiff = stripCollections(diff);

      if (Object.keys(cleanDiff).length === 0) {
        return {
          success: true,
          message: "No changes detected",
          data: currentData,
        };
      }

      const res = await api.patch(`/users/users/${userId}/`, cleanDiff);

      return {
        success: true,
        data: mapBackendToFrontend(res.data),
        message: "Changes saved",
      };
    } catch (error) {
      console.error("Partial save error:", error);
      return {
        success: false,
        error: handleApiError(error),
        message: "Failed to save changes",
      };
    }
  },

  /**
   * Helper to fetch all pages of a paginated endpoint
   */
  fetchAllPages: async (endpoint) => {
    let allData = [];
    let nextUrl = endpoint;

    try {
      while (nextUrl) {
        // If nextUrl is an absolute URL (from DRF pagination), we need to extract the path
        // because our api instance is pre-configured with the baseURL
        if (nextUrl.startsWith("http")) {
          const urlObj = new URL(nextUrl);
          // Only keep path and query string (e.g., "/api/core/flags/?page=2")
          // Assuming the api instance baseURL handles the "/api" prefix, we might need to strip it
          // A safer way is to just pass the original endpoint but with the page parameter
          const pageMatch = nextUrl.match(/page=(\d+)/);
          if (pageMatch) {
            const separator = endpoint.includes('?') ? '&' : '?';
            nextUrl = `${endpoint}${separator}page=${pageMatch[1]}`;
          } else {
            nextUrl = null; // Failsafe
          }
        }

        const res = await api.get(nextUrl);

        if (res.data && res.data.results) {
          // It's a paginated response
          allData = [...allData, ...res.data.results];
          nextUrl = res.data.next;
        } else {
          // Not paginated or simple array
          allData = Array.isArray(res.data) ? res.data : [res.data];
          nextUrl = null;
        }
      }
      return allData;
    } catch (error) {
      console.error(`Failed fetching all pages for ${endpoint}:`, error);
      throw error;
    }
  },

  /**
   * ✅ LOAD REFERENCE DATA: For dropdowns
   */
  loadAllReferenceData: async () => {
    try {
      const endpoints = {
        flags: "/core/flags/",
        vesselTypes: "/core/vessel-types/",
        certificates: "/users/certificates/",
        companies: "/companies/",
        positions: "/users/positions/",
      };

      const results = await Promise.allSettled(
        Object.entries(endpoints).map(async ([key, endpoint]) => {
          const data = await userService.fetchAllPages(endpoint);
          return { key, data };
        })
      );
      const data = {};
      results.forEach((result) => {
        if (result.status === "fulfilled") {
          data[result.value.key] = result.value.data;
        } else {
          const types = [
            "flags",
            "vesselTypes",
            "certificates",
            "ranks",
            "companies",
            "positions",
          ];
          const failedKey = types[results.indexOf(result)];
          console.warn(`Failed to load ${failedKey}:`, result.reason);
          data[failedKey] = [];
        }
      });

      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error("Failed to load reference data:", error);
      return {
        success: false,
        data: {
          flags: [],
          vesselTypes: [],
          certificates: [],
          ranks: [],
          companies: [],
          positions: [],
        },
        message: "Failed to load reference data",
      };
    }
  },

  /**
   * ✅ LOAD SPECIFIC REFERENCE TYPE
   */
  getReferenceData: async (type) => {
    try {
      const endpoints = {
        flags: "/core/flags/",
        vesselTypes: "/core/vessel-types/",
        certificates: "/users/certificates/",
        ranks: "/ranks/",
        companies: "/companies/",
        positions: "/users/positions/",
      };

      if (!endpoints[type]) {
        throw new Error(`Invalid reference type: ${type}`);
      }

      const data = await userService.fetchAllPages(endpoints[type]);

      return {
        success: true,
        data: data,
      };
    } catch (error) {
      console.error(`Failed to load ${type}:`, error);
      return {
        success: false,
        data: [],
        message: `Failed to load ${type}`,
      };
    }
  },

  /**
   * ✅ UPLOAD FILE
   */
  uploadFile: async (endpoint, file, additionalData = {}) => {
    try {
      const formData = new FormData();
      formData.append("file", file);

      Object.keys(additionalData).forEach((key) => {
        formData.append(key, additionalData[key]);
      });

      const res = await api.post(endpoint, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      return {
        success: true,
        data: res.data,
        message: "File uploaded successfully",
      };
    } catch (error) {
      return {
        success: false,
        error: handleApiError(error),
        message: "File upload failed",
      };
    }
  },

  /**
   * ✅ UPDATE PROFILE IMAGE
   */
  updateProfileImage: async (userId, imageFile) => {
    try {
      const formData = new FormData();
      formData.append("profile_image", imageFile);

      const res = await api.patch(`/users/users/${userId}/`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      return {
        success: true,
        data: res.data,
        message: "Profile image updated successfully",
      };
    } catch (error) {
      return {
        success: false,
        error: handleApiError(error),
        message: "Failed to update profile image",
      };
    }
  },

  /**
   * ✅ SUBMIT CV
   */
  submitCV: async (cvData) => {
    try {
      const formData = new FormData();

      formData.append("company", cvData.company);
      formData.append("position", cvData.position);
      formData.append("cv_file", cvData.cv_file);

      if (cvData.cover_letter) {
        formData.append("cover_letter", cvData.cover_letter);
      }

      const res = await api.post("/cv-submissions/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      return {
        success: true,
        data: res.data,
        message: "CV submitted successfully",
      };
    } catch (error) {
      return {
        success: false,
        error: handleApiError(error),
        message: "CV submission failed",
      };
    }
  },

  /**
   * ✅ GET USER STATISTICS
   */
  getUserStats: async (userId) => {
    try {
      const res = await api.get(`/users/users/${userId}/stats/`);
      return {
        success: true,
        data: res.data,
      };
    } catch (error) {
      console.warn("Failed to load user stats:", error);
      return {
        success: false,
        data: {},
        message: "Stats not available",
      };
    }
  },
};

export default userService;