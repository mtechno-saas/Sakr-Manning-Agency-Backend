import React, { useState } from "react";
import {
  Upload,
  Calendar,
  ChevronDown,
  X,
  Plus,
  Check,
  Camera,
} from "lucide-react";

// Base Input Component
export function BaseInput({
  name,
  label,
  type = "text",
  placeholder,
  value: externalValue,
  onChange: externalOnChange,
  required = false,
  error: externalError,
  icon,
  className = "",
  ...props
}) {
  const [internalValue, setInternalValue] = useState("");
  const [touched, setTouched] = useState(false);

  const value = externalValue !== undefined ? externalValue : internalValue;
  const onChange = externalOnChange || setInternalValue;

  const showError = externalError && (touched || externalValue !== undefined);

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={name}
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <div className="relative">
        <input
          id={name}
          name={name}
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onBlur={() => setTouched(true)}
          placeholder={placeholder}
          className={`w-full px-4 py-3 rounded-lg border bg-white text-sm transition-all duration-200
            ${
              showError
                ? "border-red-400 focus:ring-2 focus:ring-red-100 focus:border-red-500"
                : "border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 hover:border-gray-400"
            } ${icon ? "pr-10" : ""} ${className}`}
          {...props}
        />
        {icon && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none">
            {icon}
          </div>
        )}
      </div>
      {showError && (
        <p className="mt-1 text-red-500 text-xs flex items-center gap-1">
          <span className="w-1 h-1 bg-red-500 rounded-full"></span>
          {externalError}
        </p>
      )}
    </div>
  );
}

// Date Input Component
export function DateInput({
  name,
  label,
  value: externalValue,
  onChange: externalOnChange,
  required = false,
  error,
  min,
  max,
  ...props
}) {
  const [internalValue, setInternalValue] = useState("");
  const value = externalValue !== undefined ? externalValue : internalValue;
  const onChange = externalOnChange || setInternalValue;

  return (
    <BaseInput
      name={name}
      label={label}
      type="date"
      value={value}
      onChange={onChange}
      required={required}
      error={error}
      icon={<Calendar className="w-4 h-4" />}
      min={min}
      max={max}
      {...props}
    />
  );
}

// Select Component
export function Select({
  name,
  label,
  options = [],
  value: externalValue,
  onChange: externalOnChange,
  placeholder = "Select...",
  searchable = false,
  required = false,
  error,
  ...props
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [internalValue, setInternalValue] = useState("");

  const value = externalValue !== undefined ? externalValue : internalValue;
  const onChange = externalOnChange || setInternalValue;

  const filteredOptions = searchable
    ? options.filter((opt) =>
        (typeof opt === "string" ? opt : opt.label)
          .toLowerCase()
          .includes(searchTerm.toLowerCase())
      )
    : options;

  const getOptionLabel = (option) => {
    if (typeof option === "string") return option;
    return option.label;
  };

  const getOptionValue = (option) => {
    if (typeof option === "string") return option;
    return option.value;
  };

  const selectedOption = options.find((opt) => getOptionValue(opt) === value);
  const displayValue = selectedOption ? getOptionLabel(selectedOption) : "";

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={name}
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <div className="relative">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className={`w-full px-4 py-3 rounded-lg border bg-white text-sm 
            text-left transition-all duration-200 flex items-center justify-between
            ${
              error
                ? "border-red-400 focus:ring-2 focus:ring-red-100 focus:border-red-500"
                : "border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 hover:border-gray-400"
            }`}
          {...props}
        >
          <span className={displayValue ? "text-gray-900" : "text-gray-500"}>
            {displayValue || placeholder}
          </span>
          <ChevronDown
            className={`w-4 h-4 text-gray-400 transition-transform ${
              isOpen ? "rotate-180" : ""
            }`}
          />
        </button>

        {isOpen && (
          <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
            {searchable && (
              <div className="p-3 border-b border-gray-200">
                <input
                  type="text"
                  placeholder="Search..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-100"
                  onClick={(e) => e.stopPropagation()}
                />
              </div>
            )}
            {filteredOptions.map((option, index) => (
              <button
                key={index}
                type="button"
                onClick={() => {
                  onChange(getOptionValue(option));
                  setIsOpen(false);
                  setSearchTerm("");
                }}
                className="w-full px-4 py-3 text-left text-sm hover:bg-blue-50 focus:bg-blue-50 transition-colors"
              >
                {getOptionLabel(option)}
              </button>
            ))}
            {filteredOptions.length === 0 && (
              <div className="px-4 py-3 text-sm text-gray-500">
                No options found
              </div>
            )}
          </div>
        )}
      </div>
      {error && (
        <p className="mt-1 text-red-500 text-xs flex items-center gap-1">
          <span className="w-1 h-1 bg-red-500 rounded-full"></span>
          {error}
        </p>
      )}
    </div>
  );
}

// Text Area Component
export function TextArea({
  name,
  label,
  placeholder,
  rows = 4,
  value: externalValue,
  onChange: externalOnChange,
  required = false,
  error,
  className = "",
  ...props
}) {
  const [internalValue, setInternalValue] = useState("");
  const value = externalValue !== undefined ? externalValue : internalValue;
  const onChange = externalOnChange || setInternalValue;

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={name}
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <textarea
        id={name}
        name={name}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={rows}
        className={`w-full px-4 py-3 rounded-lg border bg-white text-sm 
          transition-all duration-200 resize-vertical
          ${
            error
              ? "border-red-400 focus:ring-2 focus:ring-red-100 focus:border-red-500"
              : "border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 hover:border-gray-400"
          } ${className}`}
        {...props}
      />
      {error && (
        <p className="mt-1 text-red-500 text-xs flex items-center gap-1">
          <span className="w-1 h-1 bg-red-500 rounded-full"></span>
          {error}
        </p>
      )}
    </div>
  );
}

// Radio Group Component
export function RadioGroup({
  name,
  label,
  options,
  value: externalValue,
  onChange: externalOnChange,
  required = false,
  inline = true,
  error,
  ...props
}) {
  const [internalValue, setInternalValue] = useState("");
  const value = externalValue !== undefined ? externalValue : internalValue;
  const onChange = externalOnChange || setInternalValue;

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-4">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <div
        className={`${
          inline ? "flex gap-6 justify-center flex-wrap" : "space-y-3"
        }`}
      >
        {options.map((option) => {
          const optionValue =
            typeof option === "string" ? option : option.value;
          const optionLabel =
            typeof option === "string" ? option : option.label;

          return (
            <label
              key={optionValue}
              className="flex items-center gap-3 cursor-pointer group"
            >
              <div className="relative">
                <input
                  type="radio"
                  name={name}
                  value={optionValue}
                  checked={value === optionValue}
                  onChange={(e) => onChange(e.target.value)}
                  className="sr-only"
                  {...props}
                />
                <div
                  className={`w-5 h-5 rounded-full border-2 transition-all duration-200 ${
                    value === optionValue
                      ? "border-blue-600 bg-blue-600"
                      : "border-gray-300 group-hover:border-blue-400"
                  }`}
                >
                  {value === optionValue && (
                    <div className="w-2 h-2 bg-white rounded-full absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
                  )}
                </div>
              </div>
              <span className="text-sm font-medium text-gray-700 group-hover:text-blue-600 transition-colors">
                {optionLabel}
              </span>
            </label>
          );
        })}
      </div>
      {error && (
        <p className="mt-2 text-red-500 text-xs flex items-center gap-1">
          <span className="w-1 h-1 bg-red-500 rounded-full"></span>
          {error}
        </p>
      )}
    </div>
  );
}

// Checkbox Component
export function Checkbox({
  name,
  label,
  checked: externalChecked,
  onChange: externalOnChange,
  required = false,
  error,
  ...props
}) {
  const [internalChecked, setInternalChecked] = useState(false);
  const checked =
    externalChecked !== undefined ? externalChecked : internalChecked;
  const onChange = externalOnChange || setInternalChecked;

  return (
    <div className="w-full">
      <label className="flex items-center gap-3 cursor-pointer group">
        <div className="relative">
          <input
            type="checkbox"
            name={name}
            checked={checked}
            onChange={(e) => onChange(e.target.checked)}
            className="sr-only"
            {...props}
          />
          <div
            className={`w-5 h-5 rounded border-2 transition-all duration-200 ${
              checked
                ? "border-blue-600 bg-blue-600"
                : "border-gray-300 group-hover:border-blue-400"
            }`}
          >
            {checked && (
              <Check className="w-3 h-3 text-white absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
            )}
          </div>
        </div>
        <span className="text-sm font-medium text-gray-700 group-hover:text-blue-600 transition-colors">
          {label} {required && <span className="text-red-500">*</span>}
        </span>
      </label>
      {error && (
        <p className="mt-1 text-red-500 text-xs flex items-center gap-1">
          <span className="w-1 h-1 bg-red-500 rounded-full"></span>
          {error}
        </p>
      )}
    </div>
  );
}

// File Upload Component
export function FileUpload({
  name,
  label,
  acceptedTypes = "image/*",
  multiple = false,
  files: externalFiles,
  onChange: externalOnChange,
  error,
  dropzoneText = "Click to upload or drag & drop",
  fileTypeText,
  ...props
}) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [internalFiles, setInternalFiles] = useState([]);

  const files = externalFiles !== undefined ? externalFiles : internalFiles;
  const onChange = externalOnChange || setInternalFiles;

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragIn = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragOut = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    if (multiple) {
      onChange([...files, ...droppedFiles]);
    } else {
      onChange(droppedFiles.slice(0, 1));
    }
  };

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    if (multiple) {
      onChange([...files, ...selectedFiles]);
    } else {
      onChange(selectedFiles);
    }
  };

  const removeFile = (index) => {
    onChange(files.filter((_, i) => i !== index));
  };

  const defaultFileTypeText = acceptedTypes.includes("image")
    ? "Images (JPG, PNG)"
    : "Documents";

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-4">
          {label}
        </label>
      )}

      <label
        htmlFor={name}
        onDrag={handleDrag}
        onDragStart={handleDrag}
        onDragEnd={handleDrag}
        onDragOver={handleDrag}
        onDragEnter={handleDragIn}
        onDragLeave={handleDragOut}
        onDrop={handleDrop}
        className={`flex flex-col items-center justify-center w-full h-40 border-2 border-dashed 
          rounded-lg cursor-pointer transition-all duration-200 ${
            isDragOver
              ? "border-blue-400 bg-blue-50"
              : "border-gray-300 bg-gray-50 hover:bg-gray-100"
          }`}
      >
        <Upload
          className={`w-8 h-8 mb-2 ${
            isDragOver ? "text-blue-600" : "text-blue-600"
          }`}
        />
        <p className="text-xs text-gray-500 text-center px-4">
          <span className="text-blue-500 underline">{dropzoneText}</span>
          <br />
          {fileTypeText || defaultFileTypeText}
        </p>
        <input
          type="file"
          id={name}
          name={name}
          accept={acceptedTypes}
          multiple={multiple}
          onChange={handleFileSelect}
          className="hidden"
          {...props}
        />
      </label>

      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          {files.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Upload className="w-4 h-4 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {file.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => removeFile(index)}
                className="w-6 h-6 bg-red-100 hover:bg-red-200 text-red-600 rounded-full flex items-center justify-center transition-colors"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      )}

      {error && (
        <p className="mt-2 text-red-500 text-xs flex items-center gap-1">
          <span className="w-1 h-1 bg-red-500 rounded-full"></span>
          {error}
        </p>
      )}
    </div>
  );
}

// Image Upload Component (Profile Photo style)
export function ImageUpload({
  name,
  label,
  value: externalValue,
  onChange: externalOnChange,
  error,
  placeholder = "Click to upload or drag & drop your profile photo (JPG/PNG)",
  ...props
}) {
  const [preview, setPreview] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFile = (file) => {
    if (file && file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);

      if (externalOnChange) {
        externalOnChange(file);
      }
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragIn = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragOut = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-4">
          {label}
        </label>
      )}

      <label
        htmlFor={name}
        onDrag={handleDrag}
        onDragStart={handleDrag}
        onDragEnd={handleDrag}
        onDragOver={handleDrag}
        onDragEnter={handleDragIn}
        onDragLeave={handleDragOut}
        onDrop={handleDrop}
        className={`flex flex-col items-center justify-center w-full h-40 border-2 rounded-lg cursor-pointer transition-all duration-200
          ${
            isDragOver
              ? "border-blue-400 bg-blue-50"
              : "border-gray-300 bg-gray-50 hover:bg-gray-100"
          }`}
      >
        {preview ? (
          <div className="relative w-32 h-32">
            <img
              src={preview}
              alt="Preview"
              className="w-full h-full object-cover rounded-lg"
            />
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                setPreview(null);
                if (externalOnChange) externalOnChange(null);
              }}
              className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        ) : (
          <>
            <Camera
              className={`w-8 h-8 mb-2 ${
                isDragOver ? "text-blue-600" : "text-green-600"
              }`}
            />
            <p className="text-xs text-gray-500 text-center px-4">
              {placeholder}
            </p>
          </>
        )}
        <input
          type="file"
          id={name}
          name={name}
          accept="image/*"
          onChange={(e) => handleFile(e.target.files[0])}
          className="hidden"
          {...props}
        />
      </label>

      {error && (
        <p className="mt-2 text-red-500 text-xs flex items-center gap-1">
          <span className="w-1 h-1 bg-red-500 rounded-full"></span>
          {error}
        </p>
      )}
    </div>
  );
}

// Dynamic Field Array Component
export function DynamicFieldArray({
  name,
  fields,
  onFieldsChange,
  renderField,
  addButtonText = "Add Another",
  removeButtonText = "Remove",
  maxItems = 10,
  minItems = 1,
  className = "",
}) {
  const handleAdd = () => {
    if (fields.length < maxItems) {
      onFieldsChange([...fields, { id: Date.now() }]);
    }
  };

  const handleRemove = (index) => {
    if (fields.length > minItems) {
      onFieldsChange(fields.filter((_, i) => i !== index));
    }
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {fields.map((field, index) => (
        <div key={field.id} className="relative group">
          {renderField(field, index)}
          {fields.length > minItems && (
            <button
              type="button"
              onClick={() => handleRemove(index)}
              className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center text-sm transition-colors duration-200 shadow-sm opacity-0 group-hover:opacity-100"
            >
              <X className="w-3 h-3" />
            </button>
          )}
        </div>
      ))}

      <div className="text-center pt-4">
        <button
          type="button"
          onClick={handleAdd}
          disabled={fields.length >= maxItems}
          className={`px-6 py-3 rounded-full font-medium transition-all duration-200 inline-flex items-center gap-2 ${
            fields.length >= maxItems
              ? "bg-gray-300 text-gray-500 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700 text-white shadow-md hover:shadow-lg"
          }`}
        >
          <Plus className="w-4 h-4" />
          {addButtonText}
        </button>
        {fields.length >= maxItems && (
          <p className="text-xs text-gray-500 mt-2">
            Maximum {maxItems} items allowed
          </p>
        )}
      </div>
    </div>
  );
}

// Section Container Component

export function FormSection({
  title,
  children,
  className = "",
  variant = "default", // default, primary, light
}) {
  const variants = {
    default: "bg-white border border-gray-200",
    primary:
      "bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200",
    light: "bg-blue-50/50",
  };

  return (
    <div className={`rounded-2xl p-6 md:p-8 ${variants[variant]} ${className}`}>
      {title && (
        <h3
          className="text-lg font-semibold text-center mb-6 
          ${variant === 'primary' ? 'text-blue-800 uppercase tracking-wide' : 'text-gray-800'}"
        >
          {title}
        </h3>
      )}
      {children}
    </div>
  );
}
