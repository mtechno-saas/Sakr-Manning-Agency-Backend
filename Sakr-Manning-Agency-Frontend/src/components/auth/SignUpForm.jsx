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

export const SignUpForm = ({ onSubmit, isLoading, onSwitchToLogin }) => {
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
      <h2 className="text-3xl font-bold text-gray-900 text-center mb-8 mt-4">
        Welcome to Sakr Manning Agency
      </h2>

      {/* Form */}
      <form
        onSubmit={onFormSubmit}
        noValidate
        className="space-y-6 w-full px-6"
      >
        {/* Name Field */}
        <Input
          {...getFieldProps("name")}
          icon={User}
          placeholder="Enter your name"
          label=""
          required
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
