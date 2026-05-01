// src/components/landing/LandingPage.jsx - RESPONSIVE OPTIMIZED
import React, { useState } from "react";
import Header from "./layout/Header";
import HomePage from "./pages/HomePage";
import AboutPage from "./pages/AboutPage";
import ServicesPage from "./pages/ServicesPage";
import ContactPage from "./pages/ContactPage";
import Footer from "./layout/Footer";

import { useNavigate } from "react-router-dom";

const LandingPage = ({ user, onLogout, onOpenAuth }) => {
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState("home");

  const handleNavigation = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // Handle Apply/Online Form button click
  const handleOpenForm = () => {
    if (!user) {
      // if not logged in → open Auth overlay
      onOpenAuth();
    } else {
      // if logged in → navigate to form page
      navigate("/form");
    }
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case "home":
        return (
          <HomePage onNavigate={handleNavigation} onOpenForm={handleOpenForm} />
        );
      case "about":
        return <AboutPage />;
      case "services":
        return <ServicesPage onNavigate={handleNavigation} />;
      case "contact":
        return <ContactPage />;
      default:
        return (
          <HomePage onNavigate={handleNavigation} onOpenForm={handleOpenForm} />
        );
    }
  };

  // Normal Landing Page (with header/footer)
  return (
    <div className="min-h-screen w-full mx-auto flex flex-col bg-[#FFFFFF]">
      {/* Header - Full width */}
      <Header
        user={user}
        onLogout={onLogout}
        currentPage={currentPage}
        onNavigate={handleNavigation}
        onOpenAuth={onOpenAuth}
      />

      {/* Main Content - Full width for true edge-to-edge on large screens */}
      <main className="flex-1 w-full">
        {renderCurrentPage()}
      </main>

      {/* Footer - Full width */}
      <Footer
        onNavigate={handleNavigation}
        currentPage={currentPage}
        onOpenForm={handleOpenForm}
      />
    </div>
  );
};

export default LandingPage;
