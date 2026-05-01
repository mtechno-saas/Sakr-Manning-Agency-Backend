// App.jsx - With React Router
import React, { useState, useEffect, lazy, Suspense } from "react";
import { useApplicationStatus } from "./hooks/useApplicationStatus";
import PendingStatusModal from "./components/common/PendingStatusModal";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useNavigate,
} from "react-router-dom";
import ProtectedRoute from "./components/layout/ProtectedRoute";

import AuthLayout from "./components/layout/AuthLayout";
import { LoginForm } from "./components/auth/LoginForm";
import { SignUpForm } from "./components/auth/SignUpForm";
import { VerificationCode } from "./components/auth/VerificationCode";
import QuickApply from "./components/landing/QuickApply";

import LandingPage from "./components/landing/LandingPage";

import { useAuth } from "./hooks/useAuth";
import { AUTH_STEPS } from "./utils/constants";

const DashboardApp = lazy(() => import("./components/dashboard/DashboardApp"));
const SakrForm = lazy(() => import("./components/form/SakrForm"));
const testing = false;
// Auth Pages Component (handles all authentication screens)
const AuthPages = () => {
  const navigate = useNavigate();
  const [currentAuthStep, setCurrentAuthStep] = useState(AUTH_STEPS.LOGIN);
  const [pendingUserData, setPendingUserData] = useState(null);
  const [intendedPath, setIntendedPath] = useState(null);

  const {
    // user,
    // getProfile,
    isLoading,
    error,
    login,
    signup,
    sendVerificationCode,
    verifyCode,
    resendCode,
    clearError,
  } = useAuth();

  // Auto-dismiss errors after 4s
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => clearError(), 4000);
      return () => clearTimeout(timer);
    }
  }, [error, clearError]);

  const handleLogin = async (credentials) => {
    const result = await login(credentials);
    const userRole = result.user.role;
    const isAdmin = userRole === "admin" || userRole === "administrator" || userRole === "Admin";
    if (result.success && result.user) {
      // console.log("Login successful, user:", result.user.role);
      if (testing || isAdmin) {
        navigate("/dashboard");
        setIntendedPath(null);
      } else {
        // Navigate to intended path or quick apply page
        navigate(intendedPath || "/quick-apply");
        setIntendedPath(null);
      }
    }
    // Error will be displayed via the error toast
  };

  const handleSignUp = async (userData) => {
    const result = await signup(userData);

    if (result.success) {
      if (result.requiresVerification) {
        setPendingUserData(userData);
        await sendVerificationCode(userData.email);
        setCurrentAuthStep(AUTH_STEPS.VERIFICATION);
      } else {
        // No verification needed - user is already logged in
        navigate(intendedPath || "/quick-apply");
        setPendingUserData(null);
        setIntendedPath(null);
      }
    }
  };

  const handleVerification = async (code) => {
    if (!pendingUserData?.email) return;

    const result = await verifyCode(code, pendingUserData.email);

    if (result.success) {
      navigate(intendedPath || "/quick-apply");
      setPendingUserData(null);
      setIntendedPath(null);
    }

    return result;
  };

  const handleResendCode = async () => {
    if (!pendingUserData?.email) return { success: false };
    return await resendCode(pendingUserData.email);
  };

  // Render based on current auth step
  const renderAuthContent = () => {
    switch (currentAuthStep) {
      case AUTH_STEPS.LOGIN:
        return (
          <AuthLayout title="Sign in to access all features and services">
            <LoginForm
              onSubmit={handleLogin}
              isLoading={isLoading}
              onSwitchToSignUp={() => setCurrentAuthStep(AUTH_STEPS.SIGNUP)}
              onForgotPassword={() =>
                setCurrentAuthStep(AUTH_STEPS.FORGOT_PASSWORD)
              }
            />
          </AuthLayout>
        );

      case AUTH_STEPS.SIGNUP:
        return (
          <AuthLayout title="Sign up to access all features and services">
            <SignUpForm
              onSubmit={handleSignUp}
              isLoading={isLoading}
              onSwitchToLogin={() => setCurrentAuthStep(AUTH_STEPS.LOGIN)}
            />
          </AuthLayout>
        );

      case AUTH_STEPS.VERIFICATION:
        return (
          <AuthLayout showSideContent={true} title=" ">
            <VerificationCode
              onVerify={handleVerification}
              onResend={handleResendCode}
              onBack={() => setCurrentAuthStep(AUTH_STEPS.SIGNUP)}
              isLoading={isLoading}
              email={pendingUserData?.email}
            />
          </AuthLayout>
        );

      case AUTH_STEPS.FORGOT_PASSWORD:
        return (
          <AuthLayout showSideContent={true} title=" ">
            <VerificationCode
              onVerify={handleVerification}
              onResend={handleResendCode}
              onBack={() => setCurrentAuthStep(AUTH_STEPS.LOGIN)}
              isLoading={isLoading}
              email={pendingUserData?.email}
            />
          </AuthLayout>
        );

      default:
        return (
          <AuthLayout title="Sign in to access all features and services">
            <LoginForm
              onSubmit={handleLogin}
              isLoading={isLoading}
              onSwitchToSignUp={() => setCurrentAuthStep(AUTH_STEPS.SIGNUP)}
              onForgotPassword={() =>
                setCurrentAuthStep(AUTH_STEPS.FORGOT_PASSWORD)
              }
            />
          </AuthLayout>
        );
    }
  };

  return (
    <>
      {renderAuthContent()}

      {/* Error Toast */}
      {error && (
        <div className="fixed bottom-4 right-4 max-w-[90vw] md:max-w-md bg-red-500 text-white px-4 sm:px-6 py-2 sm:py-3 rounded-lg shadow-lg z-50 animate-fade-in">
          <div className="flex items-center justify-between gap-4">
            <span className="text-sm sm:text-base">{error}</span>
            <button
              onClick={clearError}
              className="ml-2 text-white hover:text-gray-200 p-1"
              aria-label="Close error message"
            >
              ×
            </button>
          </div>
        </div>
      )}
    </>
  );
};

// Landing Page Wrapper
const Landing = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  // console.log("user from auth : ", user);
  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  const handleOpenAuth = () => {
    navigate("/auth");
  };

  const handleOpenForm = () => {
    if (user) {
      navigate("/form");
    } else {
      navigate("/auth");
    }
  };

  return (
    <LandingPage
      user={user}
      onLogout={handleLogout}
      onOpenAuth={handleOpenAuth}
      onOpenForm={handleOpenForm}
    />
  );
};

// Dashboard Wrapper
const Dashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  useEffect(() => {
    const checkAdminAccess = () => {
      if (!user) {
        navigate("/auth");
        return;
      }

      const userRole = user.role?.toLowerCase();
      const isAdmin = userRole === "admin" || userRole === "administrator" || userRole === "Admin";
      if (!isAdmin) {
        if (testing) {
          navigate("/dashboard", { replace: true });
        } else {
          console.warn(
            "Non-admin user attempted to access dashboard. Redirecting..."
          );
          navigate("/", { replace: true });
        }
      } else {
        navigate("/dashboard", { replace: true });
      }
    };
    checkAdminAccess();
  }, [user, navigate]);

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  const userRole = user?.role?.toLowerCase();
  const isAdmin = userRole === "admin" || userRole === "administrator" || userRole === "Admin";
  if (!testing && !isAdmin) {
    return <Navigate to="/" replace />;
  }

  return (
    <Suspense fallback={<div>Loading Dashboard...</div>}>
      <DashboardApp user={user} onLogout={handleLogout} />
    </Suspense>
  );
};

// Form Page Wrapper (Protected - requires authentication)
const FormPage = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { status, isLoading } = useApplicationStatus();

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  // Redirect new users (no Quick Apply submission) to /quick-apply
  useEffect(() => {
    if (!isLoading && status === "none") {
      navigate("/quick-apply", { replace: true });
    }
  }, [status, isLoading, navigate]);

  // Loading state while checking application status
  if (isLoading || status === "none") {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Checking application status...</p>
        </div>
      </div>
    );
  }

  // Pending review — show informational modal
  if (status === "Pending") {
    return (
      <PendingStatusModal
        isOpen={true}
        onGoHome={() => navigate("/")}
      />
    );
  }

  // Blacklisted — access denied
  if (status === "Blacklist") {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md px-6">
          <div className="text-5xl mb-4">🚫</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Access Denied
          </h2>
          <p className="text-gray-500 mb-6">
            Your application has been denied. Please contact support for further
            assistance.
          </p>
          <button
            onClick={() => navigate("/")}
            className="px-6 py-3 rounded-full bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  // Active — render the full form
  // for Active status
  return (
    <Suspense
      fallback={
        <div className="min-h-screen w-full flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading form...</p>
          </div>
        </div>
      }
    >
      <SakrForm userId={user?.id} onLogout={handleLogout} />
    </Suspense>
  );
};

// Main App Component
const App = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen">
        <Routes>
          {/* Landing Page - Base Route */}
          <Route path="/" element={<Landing />} />

          {/* Authentication Route */}
          <Route path="/auth" element={<AuthPages />} />
          {/* Dashboard Route (Admin only) */}
          {/* <Route path="/dashboard" element={<Dashboard />} /> */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute requiredRole="admin">
                <Dashboard />
              </ProtectedRoute>
            }
          />

          {/* Form Route (Protected - any authenticated user) */}
          <Route
            path="/form"
            element={
              // <ProtectedRoute>
              <FormPage />
              // </ProtectedRoute>
            }
          />

          {/* Quick Apply Route */}
          <Route path="/quick-apply" element={<QuickApply />} />

          {/* Catch all - redirect to landing */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App;
