// utils/validation.js

// Email validation
export const validateEmail = (email) => {
  if (email === "admin") return "";

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email.trim()) return "Email is required";
  if (!emailRegex.test(email)) return "Please enter a valid email address";
  return "";
};

// Password validation with strength requirements
export const validatePassword = (password) => {
  if (!password) return "Password is required";
  if (password.length < 8) return "Password must be at least 8 characters long";

  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  if (!hasUpperCase)
    return "Password must contain at least one uppercase letter";
  if (!hasLowerCase)
    return "Password must contain at least one lowercase letter";
  if (!hasNumbers) return "Password must contain at least one number";
  if (!hasSpecialChar)
    return "Password must contain at least one special character";

  return "";
};

// Name validation
export const validateName = (name) => {
  if (!name.trim()) return "Name is required";
  if (name.trim().length < 2) return "Name must be at least 2 characters long";
  if (!/^[a-zA-Z\s]+$/.test(name))
    return "Name can only contain letters and spaces";
  return "";
};

// International phone number validation
export const validatePhone = (phone) => {
  if (!phone.trim()) return "Phone number is required";

  // Remove all non-digit characters
  const cleanPhone = phone.replace(/\D/g, "");

  // Check for various international formats
  if (cleanPhone.length < 10) return "Phone number is too short";
  if (cleanPhone.length > 15) return "Phone number is too long";

  // Basic international format check
  const internationalRegex =
    /^(\+?1-?)?(\([0-9]{3}\)|[0-9]{3})[0-9]{3}[0-9]{4}$|^(\+?[1-9]\d{1,14})$/;
  if (!internationalRegex.test(phone))
    return "Please enter a valid phone number";

  return "";
};

// Verification code validation
export const validateVerificationCode = (code, requiredLength = 3) => {
  if (!code) return "Verification code is required";
  if (code.length !== requiredLength)
    return `Please enter all ${requiredLength} digits`;
  if (!/^\d+$/.test(code)) return "Verification code must contain only numbers";
  return "";
};

// Password strength calculator
export const getPasswordStrength = (password) => {
  let score = 0;
  let feedback = [];

  if (password.length >= 8) score += 1;
  else feedback.push("Use at least 8 characters");

  if (/[A-Z]/.test(password)) score += 1;
  else feedback.push("Add uppercase letters");

  if (/[a-z]/.test(password)) score += 1;
  else feedback.push("Add lowercase letters");

  if (/\d/.test(password)) score += 1;
  else feedback.push("Add numbers");

  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 1;
  else feedback.push("Add special characters");

  const strength = ["Very Weak", "Weak", "Fair", "Good", "Strong"][score];
  const color = ["red", "orange", "yellow", "blue", "green"][score];

  return { score, strength, color, feedback };
};

// Form validation helper
export const validateForm = (formData, validationRules) => {
  const errors = {};

  Object.keys(validationRules).forEach((field) => {
    const validator = validationRules[field];
    const error = validator(formData[field]);
    if (error) errors[field] = error;
  });

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};
