import api from "../Auth/api.js";

/**
 * Downloads API Service
 * Handles all user document/attachment download API calls
 */
export const downloadsApi = {
  /**
   * Helper function to trigger a file download from an Axios response
   */
  triggerDownload: (response, defaultFilename) => {
    const blob = response.data;
    let filename = defaultFilename;
    const disposition = response.headers && response.headers['content-disposition'];
    
    if (disposition && disposition.indexOf('attachment') !== -1) {
      const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
      const matches = filenameRegex.exec(disposition);
      if (matches != null && matches[1]) {
        filename = matches[1].replace(/['"]/g, '');
      }
    } else {
      // Fallback: try to append correct extension based on content-type if missing
      const contentType = response.headers && response.headers['content-type'];
      if (contentType) {
        const extMap = {
          'application/pdf': '.pdf',
          'image/jpeg': '.jpg',
          'image/png': '.png',
          'application/msword': '.doc',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx'
        };
        const ext = extMap[contentType];
        if (ext && !filename.endsWith(ext)) {
          // Remove existing extension and add the correct one
          filename = filename.replace(/\.[^/.]+$/, "") + ext;
        }
      }
    }

    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
  },

  /**
   * Generic Document Download
   * @param {number} userId 
   * @param {string} type - 'passport', 'seaman_book', 'other_seaman_book', 'marlins', 'ces', 'profile_image', 'file'
   */
  downloadDocument: async (userId, type) => {
    const response = await api.get(`/users/users/${userId}/download-document/?type=${type}`, {
      responseType: "blob",
    });
    return response;
  },

  /**
   * Travel Documents
   */
  downloadPassport: async (userId) => {
    const response = await api.get(`/users/users/${userId}/download-passport/`, {
      responseType: "blob",
    });
    return response;
  },

  downloadSeamanBook: async (userId) => {
    const response = await api.get(`/users/users/${userId}/download-seaman-book/`, {
      responseType: "blob",
    });
    return response;
  },

  downloadOtherSeamanBook: async (userId) => {
    const response = await api.get(`/users/users/${userId}/download-other-seaman-book/`, {
      responseType: "blob",
    });
    return response;
  },

  downloadPersonalDocument: async (userId, docId) => {
    const response = await api.get(`/users/users/${userId}/download-personal-document/${docId}/`, {
      responseType: "blob",
    });
    return response;
  },

  /**
   * Certificates / Licenses
   */
  downloadMarlins: async (userId) => {
    const response = await api.get(`/users/users/${userId}/download-marlins/`, {
      responseType: "blob",
    });
    return response;
  },

  downloadCes: async (userId) => {
    const response = await api.get(`/users/users/${userId}/download-ces/`, {
      responseType: "blob",
    });
    return response;
  },

  downloadLicense: async (userId, licenseId) => {
    const response = await api.get(`/users/users/${userId}/download-license/${licenseId}/`, {
      responseType: "blob",
    });
    return response;
  },

  /**
   * Medical / Health
   */
  downloadVaccination: async (userId, vaccinationId) => {
    const response = await api.get(`/users/users/${userId}/download-vaccination/${vaccinationId}/`, {
      responseType: "blob",
    });
    return response;
  },

  /**
   * Marine Courses
   */
  downloadCourse: async (userId, courseId) => {
    const response = await api.get(`/users/users/${userId}/download-course/${courseId}/`, {
      responseType: "blob",
    });
    return response;
  },

  /**
   * Sea-Service
   */
  downloadSeaService: async (userId, serviceId) => {
    const response = await api.get(`/users/users/${userId}/download-sea-service/${serviceId}/`, {
      responseType: "blob",
    });
    return response;
  },
};

export default downloadsApi;
