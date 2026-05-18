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
  useLocation,
} from "react-router-dom";
import ProtectedRoute from "./components/layout/ProtectedRoute";
import { tokenStorage } from "./services/Auth/tokenStorage";

import AuthLayout from "./components/layout/AuthLayout";
import { LoginForm } from "./components/auth/LoginForm";
import { SignUpForm } from "./components/auth/SignUpForm";
import { VerificationCode } from "./components/auth/VerificationCode";
import QuickApply from "./components/landing/QuickApply";
import NotifyPage from "./components/landing/NotifyPage";

import LandingPage from "./components/landing/LandingPage";

import { useAuth } from "./hooks/useAuth";
import { AUTH_STEPS } from "./utils/constants";
import LoadingScreen from "./components/dashboard/Components/Common/LoadingScreen";

const DashboardApp = lazy(() => import("./components/dashboard/DashboardApp"));
const SakrForm = lazy(() => import("./components/form/SakrForm"));

/** Shared helper – keep in sync with ProtectedRoute & authService */
export const isAdminRole = (role) => {
  const r = role?.toLowerCase();
  return r === "admin" || r === "administrator";
};
// Auth Pages — redirect already-authenticated users away from /auth
const AuthPages = () => {
  const navigate = useNavigate();
  const { state } = useLocation();

  // Fast pre-check: if a valid session exists in storage, skip the auth page.
  // This prevents a logged-in admin from landing back on /auth via the back button.
  useEffect(() => {
    const storedUser = tokenStorage.getUser();
    if (storedUser) {
      if (tokenStorage.isStoredAdmin()) {
        navigate("/dashboard", { replace: true });
      } else {
        navigate("/quick-apply", { replace: true });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const [currentAuthStep, setCurrentAuthStep] = useState(AUTH_STEPS.LOGIN);
  const [pendingUserData, setPendingUserData] = useState(null);
  const [intendedPath, setIntendedPath] = useState(state?.intendedPath || null);

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

    if (result.success && result.user) {
      if (isAdminRole(result.user.role)) {
        navigate("/dashboard");
      } else {
        navigate(intendedPath || "/quick-apply");
      }
      setIntendedPath(null);
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
        // No verification needed — user is already logged in
        navigate("/quick-apply");
        setPendingUserData(null);
        setIntendedPath(null);
      }
    }
  };

  const handleVerification = async (code) => {
    if (!pendingUserData?.email) return;

    const result = await verifyCode(code, pendingUserData.email);

    if (result.success) {
      navigate("/quick-apply");
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

// Dashboard Wrapper — access already enforced by ProtectedRoute above
const Dashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <Suspense fallback={<LoadingScreen fullScreen={true} message="Loading Dashboard" subMessage="Preparing your maritime control panel" />}>
      <DashboardApp user={user} onLogout={handleLogout} />
    </Suspense>
  );
};

// Form Page Wrapper (Protected - requires authentication)
const FormPage = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  // Active — render the full form
  return (
    <Suspense
      fallback={<LoadingScreen fullScreen={true} message="Loading Form" subMessage="Preparing the Seafarer application form" />}
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

          {/* Authentication Route — AuthPages itself handles redirect if already logged in */}
          <Route path="/auth" element={<AuthPages />} />

          {/* Dashboard Route (Admin only) */}
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
              <ProtectedRoute>
                <FormPage />
              </ProtectedRoute>
            }
          />

          {/* Quick Apply Route */}
          <Route
            path="/quick-apply"
            element={<QuickApply />}
          />

          {/* Notify Route */}
          <Route
            path="/notify"
            element={<NotifyPage />}
          />

          {/* Catch all - redirect to landing */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App;
