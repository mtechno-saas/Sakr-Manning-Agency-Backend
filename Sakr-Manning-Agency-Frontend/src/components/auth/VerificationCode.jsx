// components/auth/VerificationCode.jsx
import React, { useState, useEffect, useRef } from "react";
import { Shield, ArrowLeft, RefreshCw } from "lucide-react";
import Button from "../../_archive/ui/Button";
import { VERIFICATION, ASSETS } from "../../utils/constants";
import { validateVerificationCode } from "../../utils/validation";

export const VerificationCode = ({
  onVerify,
  onResend,
  onBack,
  isLoading,
  email,
  codeLength = VERIFICATION.CODE_LENGTH,
}) => {
  const [codes, setCodes] = useState(Array(codeLength).fill(""));
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [resendCooldown, setResendCooldown] = useState(0);
  const [attempts, setAttempts] = useState(0);
  const inputRefs = useRef([]);

  // Initialize input refs
  useEffect(() => {
    inputRefs.current = inputRefs.current.slice(0, codeLength);
  }, [codeLength]);

  // Auto-focus first input on mount
  useEffect(() => {
    if (inputRefs.current[0]) {
      inputRefs.current[0].focus();
    }
  }, []);

  // Handle resend cooldown
  useEffect(() => {
    let timer;
    if (resendCooldown > 0) {
      timer = setTimeout(() => {
        setResendCooldown(resendCooldown - 1);
      }, 1000);
    }
    return () => clearTimeout(timer);
  }, [resendCooldown]);

  // Handle individual code input changes
  const handleCodeChange = (index, value) => {
    // Only allow digits and limit to 1 character
    if (!/^\d*$/.test(value) || value.length > 1) return;

    const newCodes = [...codes];
    newCodes[index] = value;
    setCodes(newCodes);

    // Clear errors when user starts typing
    if (error) setError("");
    if (success) setSuccess("");

    // Auto-focus next input if value entered
    if (value && index < codeLength - 1) {
      inputRefs.current[index + 1]?.focus();
    }

    // Auto-submit when all fields are filled
    if (value && newCodes.every((code) => code !== "")) {
      const fullCode = newCodes.join("");
      handleSubmit(fullCode);
    }
  };

  // Handle backspace and navigation
  const handleKeyDown = (index, e) => {
    switch (e.key) {
      case "Backspace":
        if (!codes[index] && index > 0) {
          const newCodes = [...codes];
          newCodes[index - 1] = "";
          setCodes(newCodes);
          inputRefs.current[index - 1]?.focus();
        } else if (codes[index]) {
          const newCodes = [...codes];
          newCodes[index] = "";
          setCodes(newCodes);
        }
        break;

      case "ArrowLeft":
        e.preventDefault();
        if (index > 0) {
          inputRefs.current[index - 1]?.focus();
        }
        break;

      case "ArrowRight":
        e.preventDefault();
        if (index < codeLength - 1) {
          inputRefs.current[index + 1]?.focus();
        }
        break;

      case "Enter": {
        e.preventDefault();
        const fullCode = codes.join("");
        if (fullCode.length === codeLength) {
          handleSubmit(fullCode);
        }
        break;
      }
    }
  };

  // Handle paste
  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData
      .getData("text")
      .replace(/\D/g, "")
      .slice(0, codeLength);

    if (pastedData) {
      const newCodes = Array(codeLength).fill("");
      pastedData.split("").forEach((digit, index) => {
        if (index < codeLength) {
          newCodes[index] = digit;
        }
      });

      setCodes(newCodes);

      // Focus the last filled input or the next empty one
      const lastFilledIndex = pastedData.length - 1;
      const focusIndex =
        lastFilledIndex < codeLength - 1
          ? lastFilledIndex + 1
          : lastFilledIndex;
      inputRefs.current[focusIndex]?.focus();

      // Auto-submit if complete
      if (pastedData.length === codeLength) {
        handleSubmit(pastedData);
      }
    }
  };

  // Handle form submission
  const handleSubmit = async (code) => {
    const fullCode = code || codes.join("");

    // Validate code
    const validationError = validateVerificationCode(fullCode, codeLength);
    if (validationError) {
      setError(validationError);
      return;
    }

    // Check attempt limits
    if (attempts >= VERIFICATION.MAX_ATTEMPTS) {
      setError("Too many attempts. Please request a new code.");
      return;
    }

    setError("");
    setSuccess("");

    try {
      const result = await onVerify(fullCode);

      if (result.success) {
        setSuccess("Verification successful!");
        setAttempts(0);
      } else {
        setAttempts((prev) => prev + 1);
        const remainingAttempts = VERIFICATION.MAX_ATTEMPTS - attempts - 1;

        if (remainingAttempts > 0) {
          setError(`Invalid code. ${remainingAttempts} attempts remaining.`);
        } else {
          setError("Too many attempts. Please request a new code.");
        }

        // Clear codes and focus first input
        setCodes(Array(codeLength).fill(""));
        inputRefs.current[0]?.focus();
      }
    } catch (error) {
      setError(error.message || "Verification failed. Please try again.");
      setAttempts((prev) => prev + 1);
    }
  };

  // Handle resend code
  const handleResend = async () => {
    if (resendCooldown > 0) return;

    setError("");
    setSuccess("");
    setAttempts(0);
    setCodes(Array(codeLength).fill(""));

    try {
      const result = await onResend();

      if (result.success) {
        setSuccess("New verification code sent!");
        setResendCooldown(VERIFICATION.RESEND_COOLDOWN);
        inputRefs.current[0]?.focus();
      } else {
        setError(result.message || "Failed to send code. Please try again.");
      }
    } catch (error) {
      setError("Failed to send code. Please try again.");
    }
  };

  // Format email for display
  const formatEmail = (email) => {
    if (!email) return "";
    const [localPart, domain] = email.split("@");
    if (!domain) return email;

    const visibleLocal =
      localPart.length > 2
        ? `${localPart.slice(0, 2)}${"*".repeat(localPart.length - 2)}`
        : localPart;

    return `${visibleLocal}@${domain}`;
  };

  return (
    <div className="bg-white rounded-2xl py-6 px-4 sm:px-10 shadow-xl max-w-md w-[95%] sm:w-full mx-auto sm:mx-4 my-8 border-[3px] border-maritime-600">
      {/* Header */}
      <div className="text-center mb-1 flex flex-col justify-center items-center">
        <h2 className="text-2xl font-bold text-gray-900">Verification Code</h2>

        <p className="text-gray-600">We've sent a verification code to</p>
        <p className="text-sm font-medium text-gray-900">
          {formatEmail(email)}
        </p>

        <img
          src={ASSETS.VERIFICATION}
          alt="Verification"
          width={200}
          height={200}
        />
      </div>

      {/* Code Input Fields */}
      <div className="flex justify-center space-x-1 sm:space-x-3 mb-1">
        {codes.map((code, index) => (
          <input
            key={index}
            ref={(el) => (inputRefs.current[index] = el)}
            type="text"
            inputMode="numeric"
            maxLength={1}
            value={code}
            onChange={(e) => handleCodeChange(index, e.target.value)}
            onKeyDown={(e) => handleKeyDown(index, e)}
            onPaste={index === 0 ? handlePaste : undefined}
            className={`
              w-9 h-11 sm:w-14 sm:h-14 text-center text-lg sm:text-2xl font-bold border-2 rounded-lg 
              focus:outline-none focus:ring-2 transition-all duration-200
              ${
                error
                  ? "border-red-500 focus:border-red-500 focus:ring-red-200"
                  : success
                  ? "border-green-500 focus:border-green-500 focus:ring-green-200"
                  : "border-gray-300 focus:border-blue-500 focus:ring-blue-200"
              }
              ${code ? "bg-blue-50 border-blue-500" : "bg-white"}
            `}
            aria-label={`Verification code digit ${index + 1}`}
          />
        ))}
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-2 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600 text-sm text-center">{error}</p>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="p-2 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-600 text-sm text-center">{success}</p>
        </div>
      )}

      {/* Resend Section */}
      <div className="text-center mb-1">
        <span className="text-gray-600 text-sm mx-1">
          Didn't receive the code?
        </span>

        <button
          onClick={handleResend}
          disabled={resendCooldown > 0 || isLoading}
          className="text-blue-600 hover:text-blue-800 font-medium text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {/* <RefreshCw
            className={`inline w-4 h-4 mr-1 ${isLoading ? "animate-spin" : ""}`}
          /> */}
          {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : "Resend"}
        </button>
      </div>

      {/* Action Buttons */}
      <div className="space-y-3">
        <Button
          onClick={() => handleSubmit()}
          loading={isLoading}
          disabled={codes.join("").length !== codeLength}
          fullWidth
          className="bg-[#1976D2] hover:shadow-xl text-white py-2 rounded-xl font-semibold text-base"
        >
          Continue
        </Button>

        {onBack && (
          <Button
            onClick={onBack}
            variant="secondary"
            fullWidth
            leftIcon={ArrowLeft}
            className="mt-2 text-black py-2 rounded-xl font-semibold text-base"
          >
            Back to Sign Up
          </Button>
        )}
      </div>

      {/* Expiry Notice */}
      {/* <div className="text-center">
        <p className="text-xs text-gray-500">
          This code will expire in {VERIFICATION.EXPIRY_TIME} minutes
        </p>
      </div> */}
    </div>
  );
};
