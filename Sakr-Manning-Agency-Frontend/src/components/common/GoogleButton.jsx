import React, { useState, useEffect, useCallback, useRef } from "react";

/** *
 * @param {function} onSuccess - Callback when authentication succeeds
 * @param {function} onError - Callback when authentication fails
 * @param {string} buttonText - Custom button text
 * @param {string} theme - Google button theme: 'outline', 'filled_blue', 'filled_black'
 * @param {string} size - Google button size: 'large', 'medium', 'small'
 * @param {string} type - Button type: 'standard', 'icon'
 * @param {string} shape - Button shape: 'rectangular', 'pill', 'circle', 'square'
 * @param {boolean} useOneTap - Enable Google One Tap
 * @param {boolean} useCustomButton - Use custom styled button instead of Google's
 * @param {string} customButtonVariant - Custom button style: 'primary', 'outline', 'minimal'
 */
const GoogleIdentityServices = ({
  onSuccess,
  onError,
  buttonText = "Continue with Google",
  theme = "outline",
  size = "large",
  type = "standard",
  shape = "rectangular",
  useOneTap = true,
  useCustomButton = false,
  customButtonVariant = "primary",
  className = "",
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoaded, setIsGoogleLoaded] = useState(false);
  const [error, setError] = useState(null);
  const googleButtonRef = useRef(null);
  const customButtonRef = useRef(null);

  // Replace with your actual Google Client ID
  const GOOGLE_CLIENT_ID =
    "1097877151768-6mn37hmh3eiatd9a570hjjrltcmd5veb.apps.googleusercontent.com";

  // Load and initialize Google Identity Services
  useEffect(() => {
    const loadGoogleGIS = () => {
      // Check if already loaded
      if (window.google?.accounts?.id) {
        initializeGoogleGIS();
        return;
      }

      // Check if script is already in DOM
      if (
        document.querySelector(
          'script[src="https://accounts.google.com/gsi/client"]'
        )
      ) {
        const checkLoaded = setInterval(() => {
          if (window.google?.accounts?.id) {
            clearInterval(checkLoaded);
            initializeGoogleGIS();
          }
        }, 100);
        return;
      }

      // Load the script
      const script = document.createElement("script");
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.defer = true;
      script.onload = initializeGoogleGIS;
      script.onerror = () => {
        setError("Failed to load Google Identity Services");
      };
      document.head.appendChild(script);
    };

    loadGoogleGIS();
  }, []);

  // Initialize Google Identity Services
  const initializeGoogleGIS = useCallback(() => {
    try {
      if (!window.google?.accounts?.id) {
        setError("Google Identity Services not available");
        return;
      }

      if (GOOGLE_CLIENT_ID === "YOUR_GOOGLE_CLIENT_ID_HERE") {
        setError(
          "Please configure REACT_APP_GOOGLE_CLIENT_ID environment variable"
        );
        return;
      }

      // Initialize with your client ID
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleCredentialResponse,
        auto_select: false,
        cancel_on_tap_outside: true,
      });

      setIsGoogleLoaded(true);

      // Render Google's native button if not using custom
      if (!useCustomButton && googleButtonRef.current) {
        window.google.accounts.id.renderButton(googleButtonRef.current, {
          theme,
          size,
          type,
          shape,
          text:
            buttonText === "Continue with Google"
              ? "continue_with"
              : "signin_with",
          width: "100%",
        });
      }

      // Show One Tap if enabled
      if (useOneTap) {
        window.google.accounts.id.prompt((notification) => {
          if (notification.isNotDisplayed()) {
            console.log(
              "One Tap not displayed:",
              notification.getNotDisplayedReason()
            );
          } else if (notification.isSkippedMoment()) {
            console.log("One Tap skipped:", notification.getSkippedReason());
          }
        });
      }
    } catch (error) {
      console.error("GIS initialization failed:", error);
      setError("Failed to initialize Google authentication");
    }
  }, [
    GOOGLE_CLIENT_ID,
    theme,
    size,
    type,
    shape,
    useOneTap,
    useCustomButton,
    buttonText,
  ]);

  // Handle the credential response from Google
  const handleCredentialResponse = useCallback(
    async (response) => {
      setIsLoading(true);
      setError(null);

      try {
        // Parse the JWT credential
        const credential = response.credential;
        const payload = parseJwtPayload(credential);

        if (!payload) {
          throw new Error("Invalid credential format");
        }

        // Extract user information
        const userData = {
          // Basic info
          id: payload.sub,
          email: payload.email,
          name: payload.name,
          firstName: payload.given_name,
          lastName: payload.family_name,
          picture: payload.picture,

          // Verification status
          emailVerified: payload.email_verified,

          // Token info
          credential: credential, // The JWT token itself
          iss: payload.iss, // Issuer
          aud: payload.aud, // Audience
          iat: payload.iat, // Issued at
          exp: payload.exp, // Expires at

          // Optional fields
          locale: payload.locale,
          hd: payload.hd, // Hosted domain (for G Suite accounts)
        };

        // Call success callback
        if (onSuccess) {
          await onSuccess(userData);
        }
      } catch (error) {
        console.error("Error processing Google credential:", error);
        const errorMessage = "Failed to process Google authentication";
        setError(errorMessage);
        if (onError) {
          onError(errorMessage, error);
        }
      } finally {
        setIsLoading(false);
      }
    },
    [onSuccess, onError]
  );

  // Parse JWT payload
  const parseJwtPayload = (jwt) => {
    try {
      const base64Url = jwt.split(".")[1];
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split("")
          .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
          .join("")
      );
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error("Failed to parse JWT:", error);
      return null;
    }
  };

  // Handle custom button click
  const handleCustomButtonClick = () => {
    if (!isGoogleLoaded) {
      setError("Google authentication not ready. Please wait...");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Trigger Google One Tap or sign-in flow
      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          setIsLoading(false);
          // Fallback: Try to render a temporary button
          const tempDiv = document.createElement("div");
          window.google.accounts.id.renderButton(tempDiv, {
            theme: "filled_blue",
            size: "large",
            type: "standard",
          });
          // Click the rendered button
          setTimeout(() => {
            const gButton = tempDiv.querySelector('div[role="button"]');
            if (gButton) {
              gButton.click();
            }
          }, 100);
        }
      });
    } catch (error) {
      console.error("Failed to trigger Google sign-in:", error);
      setError("Failed to start Google sign-in");
      setIsLoading(false);
    }
  };

  // Custom button styles
  const getCustomButtonClasses = () => {
    const baseClasses =
      "flex items-center justify-center w-full px-4 py-2 rounded-[12px] font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";

    const variants = {
      primary:
        "bg-white border border-[#1976D2] text-[#1976D2] hover:bg-[#1976D2] hover:text-white focus:ring-[#1976D2]",
      outline:
        "bg-transparent border-2 border-gray-300 text-gray-700 hover:border-[#0065AF] hover:text-[#0065AF] focus:ring-[#0065AF]",
      minimal:
        "bg-gray-50 border border-gray-200 text-gray-700 hover:bg-gray-100 focus:ring-gray-500",
    };

    return `${baseClasses} ${variants[customButtonVariant]} ${className}`;
  };

  // Google Icon Component
  const GoogleIcon = () => (
    <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
      />
    </svg>
  );

  return (
    <div className="w-full space-y-2">
      {useCustomButton ? (
        // Custom styled button
        <button
          ref={customButtonRef}
          onClick={handleCustomButtonClick}
          disabled={isLoading || !isGoogleLoaded}
          className={getCustomButtonClasses()}
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-current mr-3"></div>
              Authenticating...
            </>
          ) : (
            <>
              <GoogleIcon />
              {buttonText}
            </>
          )}
        </button>
      ) : (
        // Google's native button
        <div
          ref={googleButtonRef}
          className={`w-full ${className}`}
          style={{
            minHeight:
              size === "large" ? "56px" : size === "medium" ? "48px" : "40px",
          }}
        />
      )}

      {/* Error display */}
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          <div className="flex items-start">
            <svg
              className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            {error}
          </div>
        </div>
      )}

      {/* Loading indicator when Google is initializing */}
      {!isGoogleLoaded && !error && (
        <div className="flex items-center justify-center py-2 text-sm text-gray-500">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400 mr-2"></div>
          Loading Google authentication...
        </div>
      )}
    </div>
  );
};

// Hook for managing Google auth state
const useGoogleAuth = () => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleSuccess = useCallback((userData) => {
    setUser(userData);
    setIsAuthenticated(true);

    // Optional: Store user data in localStorage
    localStorage.setItem("google_user", JSON.stringify(userData));
  }, []);

  const handleError = useCallback((error, details) => {
    console.error("Google Auth Error:", error, details);
    setUser(null);
    setIsAuthenticated(false);
  }, []);

  const signOut = useCallback(() => {
    // Sign out from Google
    if (window.google?.accounts?.id) {
      window.google.accounts.id.disableAutoSelect();
    }

    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem("google_user");
  }, []);

  // Check for existing user on mount
  useEffect(() => {
    const storedUser = localStorage.getItem("google_user");
    if (storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        // Check if token is still valid (basic check)
        if (userData.exp && userData.exp * 1000 > Date.now()) {
          setUser(userData);
          setIsAuthenticated(true);
        } else {
          // Token expired, remove from storage
          localStorage.removeItem("google_user");
        }
      } catch (error) {
        console.error("Error parsing stored user data:", error);
        localStorage.removeItem("google_user");
      }
    }
  }, []);

  return {
    user,
    isAuthenticated,
    signOut,
    handleSuccess,
    handleError,
  };
};

// Demo component showing different implementations
const GoogleGISDemo = () => {
  const { user, isAuthenticated, signOut, handleSuccess, handleError } =
    useGoogleAuth();

  if (isAuthenticated && user) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-2xl mx-auto px-4">
          {/* User Profile */}
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <div className="flex items-center space-x-6 mb-6">
              <img
                src={user.picture}
                alt={user.name}
                className="w-20 h-20 rounded-full border-4 border-[#0065AF]"
              />
              <div>
                <h2 className="text-2xl font-bold text-gray-800">
                  {user.name}
                </h2>
                <p className="text-gray-600">{user.email}</p>
                <span
                  className={`inline-block px-2 py-1 text-xs rounded-full mt-2 ${user.emailVerified
                      ? "bg-green-100 text-green-800"
                      : "bg-yellow-100 text-yellow-800"
                    }`}
                >
                  {user.emailVerified ? "✓ Verified" : "⚠ Unverified"}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm bg-gray-50 rounded-lg p-4 mb-6">
              <div>
                <strong>User ID:</strong> {user.id}
              </div>
              <div>
                <strong>First Name:</strong> {user.firstName}
              </div>
              <div>
                <strong>Last Name:</strong> {user.lastName}
              </div>
              <div>
                <strong>Locale:</strong> {user.locale || "N/A"}
              </div>
              {user.hd && (
                <div>
                  <strong>Domain:</strong> {user.hd}
                </div>
              )}
            </div>

            <div className="text-center">
              <button
                onClick={signOut}
                className="bg-red-500 text-white px-6 py-2 rounded-lg hover:bg-red-600 transition-colors"
              >
                Sign Out
              </button>
            </div>
          </div>

          {/* JWT Token Display */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-3">
              JWT Credential (for Backend)
            </h3>
            <div className="bg-gray-100 p-3 rounded text-xs break-all overflow-auto max-h-40 mb-3">
              {user.credential}
            </div>
            <p className="text-sm text-gray-600">
              Send this JWT token to your backend for verification and user
              creation.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-6">
        {/* Title */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Google Identity Services
          </h1>
          <p className="text-gray-600">Modern Google authentication with GIS</p>
        </div>

        {/* Google's Native Button */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h3 className="text-lg font-semibold mb-4 text-center">
            Google's Native Button
          </h3>
          <GoogleIdentityServices
            onSuccess={handleSuccess}
            onError={handleError}
            theme="outline"
            size="large"
            useOneTap={true}
            useCustomButton={false}
          />
        </div>

        {/* Custom Styled Button */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h3 className="text-lg font-semibold mb-4 text-center">
            Custom Styled Button
          </h3>
          <GoogleIdentityServices
            onSuccess={handleSuccess}
            onError={handleError}
            buttonText="Continue with Google"
            useOneTap={false}
            useCustomButton={true}
            customButtonVariant="primary"
          />
        </div>

        {/* Instructions */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm">
          <h4 className="font-semibold text-yellow-800 mb-2">
            Setup Instructions:
          </h4>
          <ol className="text-yellow-700 space-y-1">
            <li>1. Get Google Client ID from Google Cloud Console</li>
            <li>2. Set REACT_APP_GOOGLE_CLIENT_ID environment variable</li>
            <li>3. Add your domain to authorized origins</li>
            <li>4. Test the authentication flow</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default GoogleIdentityServices;
// export { GoogleGISDemo, useGoogleAuth };
