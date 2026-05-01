// components/auth/LoginForm.jsx
import React, { useState } from "react";
import { Mail, Lock, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Button from "../../_archive/ui/Button";
import Input from "../../_archive/ui/Input";
import { useForm } from "../../hooks/useForm";
import { validateEmail } from "../../utils/validation";
import { GoogleLoginButton } from "./GoogleLoginButton";

export const LoginForm = ({
  onSubmit,
  isLoading,
  onSwitchToSignUp,
  onForgotPassword,
  onGoogleLogin,
}) => {
  const navigate = useNavigate();
  const [rememberMe, setRememberMe] = useState(false);

  // Form validation rules
  const validationRules = {
    email: validateEmail,
    password: (value) => (!value ? "Password is required" : ""),
  };

  // Initialize form
  const { handleSubmit, isValid, getFieldProps } = useForm(
    {
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
    await onSubmit({ ...formData, rememberMe });
  });

  // Handle Google login
  const handleGoogleSuccess = (googleData) => {
    if (onGoogleLogin) {
      onGoogleLogin(googleData);
    }
  };

  const handleGoogleError = (error) => {
    console.error("Google login error:", error);
  };

  return (
    <div className="w-[620px] h-[703px] bg-white/95 backdrop-blur-sm rounded-3xl p-8 shadow-2xl border border-maritime-200/20 border-3 border-maritime-600 flex flex-col justify-center items-center relative">
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
      <div className="mb-6 text-center mt-4">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Welcome Back to Sakr Manning Agency
        </h2>
      </div>

      {/* Google Sign-In Button */}
      <div className="w-full px-6 mb-4">
        <GoogleLoginButton
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
          disabled={isLoading}
        />
      </div>

      {/* Divider */}
      <div className="w-full px-6 mb-4">
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
        className="space-y-5 w-full px-6"
      >
        {/* Email Field */}
        <Input
          {...getFieldProps("email")}
          icon={Mail}
          placeholder="Enter your email address"
          label=""
          required
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
          showPasswordToggle
          autoComplete="current-password"
          className="rounded-xl border-gray-200 focus:border-maritime-400 focus:ring-maritime-400/20"
        />

        {/* Remember Me & Forgot Password */}
        <div className="flex items-center justify-between py-1">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              className="h-4 w-4 text-maritime-600 focus:ring-maritime-500 border-gray-300 rounded"
            />
            <span className="ml-2 text-sm text-gray-600">Remember me</span>
          </label>

          <button
            type="button"
            onClick={onForgotPassword}
            className="text-sm text-gray-500 hover:text-maritime-700 font-medium transition-colors duration-200"
          >
            Forgot your password?
          </button>
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          variant="primary"
          loading={isLoading}
          disabled={!isValid || isLoading}
          fullWidth
          className="mt-4 bg-[#1976D2] text-white py-1 rounded-xl font-semibold text-base"
        >
          Sign In
        </Button>
      </form>

      {/* Sign Up Link */}
      <div className="mt-6 text-center">
        <p className="text-sm text-gray-600">
          Don't have an account?{" "}
          <button
            onClick={onSwitchToSignUp}
            className="text-maritime-600 hover:text-maritime-700 font-semibold transition-colors duration-200"
            type="button"
          >
            Create one here
          </button>
        </p>
      </div>
    </div>
  );
};
