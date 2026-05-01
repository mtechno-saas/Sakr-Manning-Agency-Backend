import React, { useState, useRef } from "react";
import { Upload, X, Image as ImageIcon } from "lucide-react";
import { useFormField, cx } from "../../../hooks/useFormField";

/**
 * ImageUpload - File upload component for images.
 * Enhanced with better spacing, responsive design, and comfortable sizing.
 */

export function ImageUpload({
  name,
  label,
  accept = "image/*",
  maxSize = 5 * 1024 * 1024, // 5MB default
  rules,
  required = false,
  value,
  onChange,
  error: externalError,
  multiple = false,
  preview = true,
  className = "",
  ...props
}) {
  const { inForm, register, error, setValue } = useFormField(name);
  const err = inForm ? error : externalError;
  const fileInputRef = useRef(null);

  const [previewUrl, setPreviewUrl] = useState(value || null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];

    // Validate file size
    if (maxSize && file.size > maxSize) {
      alert(`File size exceeds ${(maxSize / 1024 / 1024).toFixed(0)}MB limit`);
      return;
    }

    // Create preview
    if (preview && file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result);
      };
      reader.readAsDataURL(file);
    }

    // Update form value
    if (inForm) {
      setValue(name, file);
    } else {
      onChange?.(file);
    }
  };

  const handleClear = () => {
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    if (inForm) {
      setValue(name, null);
    } else {
      onChange?.(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      // Simulate file input change
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(files[0]);
      if (fileInputRef.current) {
        fileInputRef.current.files = dataTransfer.files;
        handleFileChange({ target: { files: dataTransfer.files } });
      }
    }
  };

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}

      <div
        className={cx(
          "relative border-2 border-dashed rounded-xl transition-all duration-200",
          "hover:border-gray-400 hover:bg-gray-50",
          isDragging
            ? "border-blue-500 bg-blue-50"
            : previewUrl
              ? "border-gray-300 bg-white"
              : "border-gray-300 bg-white",
          err ? "border-red-400" : "",
          className
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          id={name}
          name={name}
          type="file"
          accept={accept}
          multiple={multiple}
          required={required}
          aria-invalid={!!err}
          aria-describedby={err ? `${name}-error` : undefined}
          {...(inForm
            ? register(name, {
              ...rules,
              onChange: handleFileChange,
            })
            : {
              onChange: handleFileChange,
            })}
          className="sr-only"
          {...props}
        />

        {previewUrl ? (
          // Preview mode
          <div className="relative group">
            <img
              src={previewUrl}
              alt="Preview"
              className="w-full h-64 object-cover rounded-xl"
            />
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all duration-200 rounded-xl flex items-center justify-center">
              <button
                type="button"
                onClick={handleClear}
                className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-red-500 text-white p-3 rounded-full hover:bg-red-600 shadow-lg"
                aria-label="Remove image"
              >
                <X size={20} />
              </button>
            </div>
          </div>
        ) : (
          // Upload prompt
          <label
            htmlFor={name}
            className="flex flex-col items-center justify-center py-12 px-6 cursor-pointer"
          >
            <div className={cx(
              "w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-all duration-200",
              isDragging ? "bg-blue-100" : "bg-gray-100"
            )}>
              {isDragging ? (
                <ImageIcon className="w-8 h-8 text-blue-600" />
              ) : (
                <Upload className="w-8 h-8 text-gray-400" />
              )}
            </div>

            <p className="text-base font-medium text-gray-700 mb-1">
              {isDragging ? "Drop your image here" : "Click to upload or drag and drop"}
            </p>

            <p className="text-sm text-gray-500">
              PNG, JPG, GIF up to {(maxSize / 1024 / 1024).toFixed(0)}MB
            </p>
          </label>
        )}
      </div>

      {err && (
        <p
          id={`${name}-error`}
          className="mt-2 text-sm text-red-600 flex items-center gap-1.5"
        >
          <span className="w-1.5 h-1.5 bg-red-600 rounded-full flex-shrink-0" />
          {err}
        </p>
      )}
    </div>
  );
}