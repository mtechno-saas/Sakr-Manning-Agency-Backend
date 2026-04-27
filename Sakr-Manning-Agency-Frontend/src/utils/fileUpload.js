// utils/fileUpload.js

/**
 * File validation constants
 */
export const FILE_CONSTRAINTS = {
  IMAGE: {
    maxSize: 5 * 1024 * 1024, // 5MB
    acceptedTypes: ["image/jpeg", "image/jpg", "image/png", "image/webp"],
    acceptedExtensions: [".jpg", ".jpeg", ".png", ".webp"],
  },
  DOCUMENT: {
    maxSize: 10 * 1024 * 1024, // 10MB
    acceptedTypes: [
      "application/pdf",
      "application/msword",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ],
    acceptedExtensions: [".pdf", ".doc", ".docx"],
  },
  CV: {
    maxSize: 10 * 1024 * 1024, // 10MB
    acceptedTypes: [
      "application/pdf",
      "application/msword",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ],
    acceptedExtensions: [".pdf", ".doc", ".docx"],
  },
};

/**
 * Validate file size
 */
export const validateFileSize = (file, maxSize) => {
  if (!file) return { valid: false, error: "No file selected" };

  if (file.size > maxSize) {
    const sizeMB = (maxSize / (1024 * 1024)).toFixed(0);
    return {
      valid: false,
      error: `File size must be less than ${sizeMB}MB`,
    };
  }

  return { valid: true };
};

/**
 * Validate file type
 */
export const validateFileType = (file, acceptedTypes) => {
  if (!file) return { valid: false, error: "No file selected" };

  if (!acceptedTypes.includes(file.type)) {
    return {
      valid: false,
      error: `Invalid file type. Accepted types: ${acceptedTypes.join(", ")}`,
    };
  }

  return { valid: true };
};

/**
 * Validate file extension
 */
export const validateFileExtension = (file, acceptedExtensions) => {
  if (!file) return { valid: false, error: "No file selected" };

  const extension = "." + file.name.split(".").pop().toLowerCase();

  if (!acceptedExtensions.includes(extension)) {
    return {
      valid: false,
      error: `Invalid file extension. Accepted: ${acceptedExtensions.join(
        ", "
      )}`,
    };
  }

  return { valid: true };
};

/**
 * Comprehensive file validation
 */
export const validateFile = (file, type = "DOCUMENT") => {
  if (!file) {
    return { valid: false, error: "No file selected" };
  }

  const constraints = FILE_CONSTRAINTS[type];
  if (!constraints) {
    return { valid: false, error: "Invalid validation type" };
  }

  // Check size
  const sizeValidation = validateFileSize(file, constraints.maxSize);
  if (!sizeValidation.valid) return sizeValidation;

  // Check type
  const typeValidation = validateFileType(file, constraints.acceptedTypes);
  if (!typeValidation.valid) return typeValidation;

  // Check extension
  const extValidation = validateFileExtension(
    file,
    constraints.acceptedExtensions
  );
  if (!extValidation.valid) return extValidation;

  return { valid: true };
};

/**
 * Format file size for display
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
};

/**
 * Convert file to base64
 */
export const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
    reader.readAsDataURL(file);
  });
};

/**
 * Create preview URL for file
 */
export const createFilePreview = (file) => {
  if (!file) return null;

  if (file instanceof File) {
    return URL.createObjectURL(file);
  }

  // If it's already a URL string
  if (typeof file === "string") {
    return file;
  }

  return null;
};

/**
 * Clean up preview URL
 */
export const revokeFilePreview = (url) => {
  if (url && url.startsWith("blob:")) {
    URL.revokeObjectURL(url);
  }
};

/**
 * Get file extension
 */
export const getFileExtension = (filename) => {
  if (!filename) return "";
  return filename.split(".").pop().toLowerCase();
};

/**
 * Get file name without extension
 */
export const getFileNameWithoutExtension = (filename) => {
  if (!filename) return "";
  return filename.split(".").slice(0, -1).join(".");
};

/**
 * Check if file is an image
 */
export const isImageFile = (file) => {
  if (!file) return false;

  if (file instanceof File) {
    return file.type.startsWith("image/");
  }

  if (typeof file === "string") {
    const ext = getFileExtension(file);
    return ["jpg", "jpeg", "png", "gif", "webp", "svg"].includes(ext);
  }

  return false;
};

/**
 * Check if file is a PDF
 */
export const isPdfFile = (file) => {
  if (!file) return false;

  if (file instanceof File) {
    return file.type === "application/pdf";
  }

  if (typeof file === "string") {
    return getFileExtension(file) === "pdf";
  }

  return false;
};

/**
 * Compress image file (client-side)
 */
export const compressImage = async (
  file,
  maxWidth = 1920,
  maxHeight = 1080,
  quality = 0.8
) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);

    reader.onload = (event) => {
      const img = new Image();
      img.src = event.target.result;

      img.onload = () => {
        const canvas = document.createElement("canvas");
        let { width, height } = img;

        // Calculate new dimensions
        if (width > maxWidth) {
          height = (height * maxWidth) / width;
          width = maxWidth;
        }

        if (height > maxHeight) {
          width = (width * maxHeight) / height;
          height = maxHeight;
        }

        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, width, height);

        canvas.toBlob(
          (blob) => {
            const compressedFile = new File([blob], file.name, {
              type: file.type,
              lastModified: Date.now(),
            });
            resolve(compressedFile);
          },
          file.type,
          quality
        );
      };

      img.onerror = reject;
    };

    reader.onerror = reject;
  });
};

/**
 * Handle file input change
 */
export const handleFileInputChange = async (
  event,
  validationType = "DOCUMENT",
  options = {}
) => {
  const { compress = false, compressOptions = {} } = options;

  const file = event.target.files?.[0];
  if (!file) {
    return {
      success: false,
      error: "No file selected",
    };
  }

  // Validate
  const validation = validateFile(file, validationType);
  if (!validation.valid) {
    return {
      success: false,
      error: validation.error,
    };
  }

  // Compress if needed
  let processedFile = file;
  if (compress && isImageFile(file)) {
    try {
      processedFile = await compressImage(file, compressOptions);
    } catch (error) {
      console.warn("Compression failed, using original file:", error);
    }
  }

  // Create preview
  const preview = createFilePreview(processedFile);

  return {
    success: true,
    file: processedFile,
    preview,
    originalSize: file.size,
    compressedSize: processedFile.size,
    compressionRatio:
      file.size > 0
        ? ((1 - processedFile.size / file.size) * 100).toFixed(1)
        : 0,
  };
};

/**
 * Download file from URL
 */
export const downloadFile = (url, filename) => {
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Create FormData from file with additional fields
 */
export const createFileFormData = (file, additionalFields = {}) => {
  const formData = new FormData();
  formData.append("file", file);

  Object.keys(additionalFields).forEach((key) => {
    formData.append(key, additionalFields[key]);
  });

  return formData;
};

export default {
  FILE_CONSTRAINTS,
  validateFile,
  validateFileSize,
  validateFileType,
  validateFileExtension,
  formatFileSize,
  fileToBase64,
  createFilePreview,
  revokeFilePreview,
  getFileExtension,
  getFileNameWithoutExtension,
  isImageFile,
  isPdfFile,
  compressImage,
  handleFileInputChange,
  downloadFile,
  createFileFormData,
};
