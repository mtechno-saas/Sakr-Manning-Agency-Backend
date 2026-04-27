import React from "react";
import Background from "./Background";

const AuthLayout = ({
  children,
  title,
  subtitle,
  showSideContent = true,
  sideContent,
}) => {
  return (
    <div className="min-h-screen relative flex flex-row-reverse px-9">
      <Background />

      {/* Left Side - Form */}
      <div className="relative z-10 flex-1 flex items-center justify-center px-4 lg:px-12">
        <div className="w-full max-w-md">{children}</div>
      </div>

      {/* Right Side - Content */}
      {showSideContent && (
        <div className="hidden lg:flex flex-1 items-start justify-center mt-20 text-white relative z-10">
          <div className="w-full px-4">
            {sideContent || (
              <DefaultSideContent title={title} subtitle={subtitle} />
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// Default side content component
const DefaultSideContent = ({ title, subtitle }) => (
  <div className="animate-fade-in text-center lg:text-left">
    <h1 className="text-3xl lg:text-[55px] font-semibold mb-6 leading-[150%] tracking-wider animate-slide-up">
      {title || "Sign up to access all features and services"}
    </h1>
    <p
      className="text-lg lg:text-xl opacity-90 mb-8 leading-relaxed animate-slide-up"
      style={{ animationDelay: "0.1s" }}
    >
      {subtitle || " "}
    </p>
  </div>
);

// Enhanced feature item component
const FeatureItem = ({ title, description, delay }) => (
  <div
    className="flex items-start space-x-4 animate-slide-up"
    style={{ animationDelay: delay }}
  >
    <div className="w-2 h-2 bg-maritime-200 rounded-full mt-3 flex-shrink-0 animate-pulse-slow"></div>
    <div>
      <h3 className="font-semibold text-lg mb-2 text-white">{title}</h3>
      <p className="text-sm opacity-80 leading-relaxed">{description}</p>
    </div>
  </div>
);

export default AuthLayout;
