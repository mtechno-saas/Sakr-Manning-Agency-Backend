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
    <div className="min-h-screen relative flex flex-col-reverse lg:flex-row-reverse px-4 lg:px-9 py-8 lg:py-0">
      <Background />

      {/* Left Side - Form (DOM Order 1, appears below on mobile/tablet, right on desktop) */}
      <div className="relative z-10 flex-1 flex items-center justify-center px-0 sm:px-4 lg:px-12 mt-2 lg:mt-0">
        <div className="w-full max-w-[620px] flex justify-center">{children}</div>
      </div>

      {/* Right Side - Content (DOM Order 2, appears above on mobile/tablet, left on desktop) */}
      {showSideContent && (
        <div className="flex flex-1 items-center lg:items-start justify-center lg:mt-20 text-white relative z-10 mb-2 lg:mb-0">
          <div className="w-full px-0 text-center lg:text-left">
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
  <div className="animate-fade-in">
    <h1 className="text-2xl md:text-[50px] lg:text-[55px] font-semibold mb-2 lg:mb-6 leading-[130%] lg:leading-[150%] tracking-wider animate-slide-up" style={{ textShadow: "1px 1px 4px rgba(0,0,0,0.6)" }}>
      {title || "Sign up to access all features and services"}
    </h1>
    <p
      className="text-sm md:text-2xl lg:text-xl opacity-90 mb-0 lg:mb-8 leading-relaxed animate-slide-up"
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
