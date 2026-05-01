// components/auth/SignUpForm.jsx
import React from "react";
import { User, Mail, Lock, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Button from "../../_archive/ui/Button";
import Input from "../../_archive/ui/Input";
import { useForm } from "../../hooks/useForm";
import {
  validateEmail,
  validatePassword,
  validateName,
} from "../../utils/validation";
import { GoogleLoginButton } from "./GoogleLoginButton";

export const SignUpForm = ({ onSubmit, isLoading, onSwitchToLogin, onGoogleLogin }) => {
  const navigate = useNavigate();

  // Form validation rules
  const validationRules = {
    name: validateName,
    email: validateEmail,
    password: validatePassword,
  };

  // Initialize form
  const { handleSubmit, isValid, getFieldProps } = useForm(
    {
      name: "",
      email: "",
      password: "",
    },
    validationRules,
    {
      validateOnChange: true,
      validateOnBlur: true,
    }
  );

  // Handle form submission
  const onFormSubmit = handleSubmit(async (formData) => {
    await onSubmit(formData);
  });

  // Handle Google login
  const handleGoogleSuccess = (googleData) => {
    if (onGoogleLogin) {
      onGoogleLogin(googleData);
    }
  };

  const handleGoogleError = (error) => {
    console.error("Google sign up error:", error);
  };

  return (
    <div className="w-[95%] md:w-[620px] h-auto md:h-[703px] min-h-fit md:min-h-[703px] pt-12 pb-6 md:py-8 bg-white/95 backdrop-blur-sm rounded-3xl p-4 md:p-8 shadow-2xl border border-maritime-200/20 border-[3px] border-maritime-600 flex flex-col justify-center items-center relative my-6 md:my-0 mx-auto">
      {/* Back to Home Button */}
      <button
        onClick={() => navigate("/")}
        className="absolute top-6 left-6 flex items-center gap-2 text-gray-600 hover:text-maritime-600 transition-colors duration-200"
        type="button"
      >
        <ArrowLeft size={20} />
        <span className="text-sm font-medium">Back to Home</span>
      </button>

      {/* Header */}
      <h2 className="text-xl md:text-3xl font-bold text-gray-900 text-center mb-8 md:mb-10 mt-1 md:mt-4">
        Welcome
      </h2>

      {/* Google Sign-In Button */}
      <div className="w-full px-0 md:px-6 mb-3 md:mb-4">
        <GoogleLoginButton
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
          disabled={isLoading}
        />
      </div>

      {/* Divider */}
      <div className="w-full px-0 md:px-6 mb-6 md:mb-6 mt-2 md:mt-0">
        <div className="relative flex items-center">
          <div className="flex-grow border-t border-gray-300"></div>
          <span className="flex-shrink mx-4 text-sm text-gray-500">or</span>
          <div className="flex-grow border-t border-gray-300"></div>
        </div>
      </div>

      {/* Form */}
      <form
        onSubmit={onFormSubmit}
        noValidate
        className="space-y-3 md:space-y-8 w-full px-0 md:px-6"
      >
        {/* Name Field */}
        <Input
          {...getFieldProps("name")}
          icon={User}
          placeholder="Enter your name"
          label=""
          required
          small
          autoComplete="name"
          className="rounded-xl border-gray-200 focus:border-maritime-400 focus:ring-maritime-400/20"
        />

        {/* Email Field */}
        <Input
          {...getFieldProps("email")}
          icon={Mail}
          type="email"
          placeholder="Enter your email"
          label=""
          required
          small
          autoComplete="email"
          className="rounded-xl border-gray-200 focus:border-maritime-400 focus:ring-maritime-400/20"
        />

        {/* Password Field */}
        <Input
          {...getFieldProps("password")}
          icon={Lock}
          type="password"
          placeholder="Enter your password"
          label=""
          required
          small
          showPasswordToggle
          autoComplete="new-password"
          className="rounded-xl border-gray-200 focus:border-maritime-400 focus:ring-maritime-400/20"
        />

        {/* Submit Button */}
        <Button
          type="submit"
          loading={isLoading}
          disabled={!isValid || isLoading}
          fullWidth
          className="mt-6 bg-[#1976D2] text-white py-2 rounded-xl font-semibold text-base"
        >
          Sign up
        </Button>
      </form>

      {/* Login Link */}
      <div className="mt-8 text-center">
        <p className="text-sm text-gray-600">
          Already have an account?{" "}
          <button
            onClick={onSwitchToLogin}
            className="text-maritime-600 hover:text-maritime-700 font-semibold transition-colors duration-200"
            type="button"
          >
            Sign in here
          </button>
        </p>
      </div>
    </div>
  );
};
