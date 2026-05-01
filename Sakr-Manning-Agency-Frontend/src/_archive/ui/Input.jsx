// components/ui/Input.jsx
import React, { forwardRef, useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { getPasswordStrength } from "../../utils/validation";

const Input = forwardRef(
  (
    {
      icon: Icon,
      type = "text",
      placeholder,
      value,
      onChange,
      onBlur,
      error,
      success,
      disabled = false,
      showPasswordToggle = false,
      showPasswordStrength = false,
      autoComplete,
      className = "",
      label,
      required = false,
      id,
      small = false,
      "aria-describedby": ariaDescribedBy,
      ...props
    },
    ref
  ) => {
    const [showPassword, setShowPassword] = useState(false);
    const [isFocused, setIsFocused] = useState(false);

    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    const passwordStrength =
      showPasswordStrength && type === "password" && value
        ? getPasswordStrength(value)
        : null;

    const handleTogglePassword = () => {
      setShowPassword(!showPassword);
    };

    const handleFocus = (e) => {
      setIsFocused(true);
      props.onFocus?.(e);
    };

    const handleBlur = (e) => {
      setIsFocused(false);
      onBlur?.(e);
    };

    // Determine input type
    const inputType =
      showPasswordToggle && type === "password"
        ? showPassword
          ? "text"
          : "password"
        : type;

    // Base classes
    const baseClasses = `
    w-full ${small ? 'px-3 py-2 text-sm' : 'px-4 py-3 text-base'} border rounded-lg 
    transition-all duration-200 ease-in-out
    focus:outline-none focus:ring-2
    disabled:opacity-50 disabled:cursor-not-allowed
    placeholder:text-gray-400
  `;

    // Icon padding
    const paddingClasses = Icon ? (small ? "pl-9" : "pl-11") : (small ? "pl-3" : "pl-4");

    const rightPadding = showPasswordToggle ? (small ? "pr-9" : "pr-11") : (small ? "pr-3" : "pr-4");

    // State-based classes
    const stateClasses = error
      ? "border-red-500 focus:border-red-500 focus:ring-red-200"
      : success
      ? "border-green-500 focus:border-green-500 focus:ring-green-200"
      : isFocused
      ? "border-blue-500 focus:border-blue-500 focus:ring-blue-200"
      : "border-gray-400 hover:border-gray-500";

    const combinedClasses = `${baseClasses} ${paddingClasses} ${rightPadding} ${stateClasses} ${className}`;

    return (
      <div className="w-full">
        {/* Label */}
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}

        {/* Input Container */}
        <div className="relative">
          {/* Left Icon */}
          {Icon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Icon
                className={`h-5 w-5 ${
                  error
                    ? "text-red-400"
                    : success
                    ? "text-green-400"
                    : isFocused
                    ? "text-blue-400"
                    : "text-gray-400"
                }`}
              />
            </div>
          )}

          {/* Input Field */}
          <input
            ref={ref}
            id={inputId}
            type={inputType}
            placeholder={placeholder}
            value={value}
            onChange={onChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            disabled={disabled}
            autoComplete={autoComplete}
            className={combinedClasses}
            aria-describedby={ariaDescribedBy}
            aria-invalid={error ? "true" : "false"}
            {...props}
          />

          {/* Password Toggle */}
          {showPasswordToggle && (
            <button
              type="button"
              onClick={handleTogglePassword}
              className="absolute inset-y-0 right-0 pr-3 flex items-center hover:text-gray-600 focus:outline-none"
              tabIndex={-1}
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? (
                <EyeOff className="h-5 w-5 text-gray-400" />
              ) : (
                <Eye className="h-5 w-5 text-gray-400" />
              )}
            </button>
          )}
        </div>

        {/* Password Strength Indicator */}
        {passwordStrength && showPasswordStrength && value && (
          <div className="mt-2">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-600">Password strength</span>
              <span
                className={`text-xs font-medium ${
                  passwordStrength.color === "red"
                    ? "text-red-600"
                    : passwordStrength.color === "orange"
                    ? "text-orange-600"
                    : passwordStrength.color === "yellow"
                    ? "text-yellow-600"
                    : passwordStrength.color === "blue"
                    ? "text-blue-600"
                    : "text-green-600"
                }`}
              >
                {passwordStrength.strength}
              </span>
            </div>

            {/* Strength Bar */}
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-300 ${
                  passwordStrength.color === "red"
                    ? "bg-red-500"
                    : passwordStrength.color === "orange"
                    ? "bg-orange-500"
                    : passwordStrength.color === "yellow"
                    ? "bg-yellow-500"
                    : passwordStrength.color === "blue"
                    ? "bg-blue-500"
                    : "bg-green-500"
                }`}
                style={{ width: `${(passwordStrength.score / 5) * 100}%` }}
              />
            </div>

            {/* Feedback */}
            {passwordStrength.feedback.length > 0 && (
              <ul className="mt-1 text-xs text-gray-600">
                {passwordStrength.feedback
                  .slice(0, 2)
                  .map((feedback, index) => (
                    <li key={index} className="flex items-center">
                      <span className="w-1 h-1 bg-gray-400 rounded-full mr-2"></span>
                      {feedback}
                    </li>
                  ))}
              </ul>
            )}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <p className="mt-2 text-sm text-red-600" role="alert">
            {error}
          </p>
        )}

        {/* Success Message */}
        {success && <p className="mt-2 text-sm text-green-600">{success}</p>}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;
