import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { LayoutDashboard } from "lucide-react";
import { ASSETS } from "../../../utils/constants";
import { getMediaUrl } from "../../../utils/fileHelpers";

const Header = ({ onNavigate, onOpenAuth, user, onLogout, currentPage }) => {
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [active, setActive] = useState("home");

  const isAdmin = ["admin", "administrator"].includes(user?.role?.toLowerCase());

  const navLinks = [
    { id: "home", label: "Home" },
    { id: "about", label: "About us" },
    { id: "services", label: "Services" },
    { id: "contact", label: "Contact us" },
  ];

  const handleNavClick = (id) => {
    setActive(id);
    onNavigate(id);
  };

  return (
    <header className="w-full">
      <div className="max-w-[1920px] h-28 sm:h-32 md:h-36 lg:h-28 xl:h-32 2xl:h-36 mx-auto flex items-center justify-between px-4 sm:px-6 md:px-12 lg:px-12 2xl:px-20">
        {/* Logo */}
        <div
          onClick={() => handleNavClick("home")}
          className="cursor-pointer flex items-center"
        >
          <img
            src={ASSETS.LOGO}
            alt="Sakr Shipping Logo"
            className="h-20 w-20 sm:h-24 sm:w-24 md:h-28 md:w-28 2xl:h-36 2xl:w-36 object-contain rounded-full"
          />
        </div>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center flex-1 justify-center gap-4 sm:gap-6 md:gap-8 lg:gap-12">
          {navLinks.map((link) => (
            <button
              key={link.id}
              onClick={() => handleNavClick(link.id)}
              className={`text-sm sm:text-base md:text-lg 2xl:text-xl font-medium transition ${currentPage === link.id
                ? "text-[#0065AF]"
                : "text-[#333333] hover:text-[#0065AF]"
                }`}
            >
              {link.label}
            </button>
          ))}
        </nav>

        {/* Search + Right Actions */}
        <div className="hidden md:flex items-center gap-4 sm:gap-6">
          {/* <Search
            className="w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8 text-[#333333] hover:text-[#0065AF] transition"
            strokeWidth={1.5}
          >
          */}

          {!user ? (
            <button
              onClick={onOpenAuth}
              className="w-24 h-9 sm:w-28 sm:h-10 md:w-32 md:h-11 2xl:w-40 2xl:h-14 rounded-[22px] bg-[#0065AF] text-white text-sm sm:text-base 2xl:text-lg font-medium hover:bg-[#004b82] transition"
            >
              Sign up
            </button>
          ) : (
            <div className="flex items-center gap-3">
              {/* Admin Dashboard shortcut */}
              {isAdmin && (
                <button
                  onClick={() => navigate("/dashboard")}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0065AF]/10 text-[#0065AF] hover:bg-[#0065AF]/20 transition text-sm font-medium"
                  title="Go to Dashboard"
                >
                  <LayoutDashboard size={16} />
                </button>
              )}

              <div className="w-8 h-8 sm:w-9 sm:h-9 md:w-10 md:h-10 flex items-center justify-center rounded-full bg-[#0065AF] text-white font-bold">
                {user?.profile_image ? (
                  <img
                    src={getMediaUrl(user.profile_image)}
                    alt="Profile"
                    className="w-full h-full object-cover rounded-full"
                  />
                ) : (
                  user.name?.charAt(0).toUpperCase()
                )}
              </div>
              <button
                onClick={onLogout}
                className="text-sm sm:text-base 2xl:text-lg text-gray-600 hover:text-red-500"
              >
                Logout
              </button>
            </div>
          )}
        </div>

        {/* Mobile Menu Toggle */}
        <button
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="md:hidden p-2 rounded bg-gray-100"
        >
          ☰
        </button>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden flex flex-col bg-white shadow px-4 sm:px-6 py-4 gap-3">
          {navLinks.map((link) => (
            <button
              key={link.id}
              onClick={() => {
                handleNavClick(link.id);
                setIsMenuOpen(false);
              }}
              className={`text-sm sm:text-base font-medium transition ${active === link.id
                ? "text-[#0065AF] underline underline-offset-4"
                : "text-[#333333] hover:text-[#0065AF]"
                }`}
            >
              {link.label}
            </button>
          ))}
          {!user ? (
            <button
              onClick={onOpenAuth}
              className="w-full h-9 sm:h-10 rounded-[22px] bg-[#0065AF] text-white text-sm sm:text-base font-medium hover:bg-[#004b82] transition"
            >
              Sign up
            </button>
          ) : (
            <div className="flex flex-col gap-2">
              {/* Admin Dashboard shortcut - mobile */}
              {isAdmin && (
                <button
                  onClick={() => {
                    navigate("/dashboard");
                    setIsMenuOpen(false);
                  }}
                  className="flex items-center gap-2 w-full h-9 sm:h-10 px-4 rounded-[22px] bg-[#0065AF] text-white text-sm sm:text-base font-medium hover:bg-[#004b82] transition"
                >
                  <LayoutDashboard size={16} />
                </button>
              )}
              <button
                onClick={onLogout}
                className="text-sm sm:text-base text-gray-600 hover:text-red-500"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      )}
    </header>
  );
};

export default Header;
