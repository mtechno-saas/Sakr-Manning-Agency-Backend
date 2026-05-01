import { ASSETS } from "../../../utils/constants";
import Newsletter from "../../common/Newsletter";

export default function Footer({ onNavigate, currentPage, onOpenForm }) {
  const contactInfo = [
    { label: "Mobile", value: "00201009250111" },
    {
      label: "Email",
      value: "info@sakrshipping.com",
      link: "mailto:info@sakrshipping.com",
    },
    {
      value: "sakrshipping@sakrshipping.com",
      link: "mailto:sakrshipping@sakrshipping.com",
    },
    { value: "crew@sakrshipping.com", link: "mailto:crew@sakrshipping.com" },
    { label: "Tel", value: "0020663616209" },
    { label: "Fax", value: "0020663616209" },
  ];

  return (
    <footer className="w-full bg-[#031F33] text-white flex flex-col items-center px-4 sm:px-6 md:px-12 lg:px-24 2xl:px-32 py-10">
      {/* Newsletter */}
      <Newsletter />

      {/* Links + Contacts + Social */}
      <div className="w-full max-w-screen-lg xl:max-w-screen-xl 2xl:max-w-[1600px] flex flex-col gap-4 sm:gap-6 mb-6 mt-2">
        <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4 md:gap-0">
          {/* Navigation Links */}
          {[
            { id: "about", label: "About us" },
            {
              id: "onlineForm",
              label: "Online form",
              action: () => onOpenForm(),
            },
            {
              id: "jobs",
              label: "Free jobs",
              action: () => onNavigate("home"),
            },
            { id: "contact", label: "Contact us" },
          ].map((link) => (
            <button
              key={link.id}
              onClick={() => {
                if (link.action) {
                  link.action();
                } else {
                  onNavigate(link.id);
                }
              }}
              className={`text-sm sm:text-base 2xl:text-lg transition ${currentPage === link.id
                ? "text-[#0065AF]"
                : "text-white hover:text-[#00A3FF]"
                }`}
            >
              {link.label}
            </button>
          ))}

          {/* Social Icons */}
          <div className="flex flex-row gap-4 sm:gap-6 mt-2 md:mt-0">
            {["FACEBOOK", "TWITTER", "LINKEDIN"].map((icon) => (
              <a key={icon} href="#">
                <img
                  src={ASSETS.SOCIAL_MEDIA[icon]}
                  alt={icon}
                  className="w-6 h-6 sm:w-6 sm:h-6"
                />
              </a>
            ))}
          </div>
        </div>

        {/* Contact Info */}
        <ul className="flex flex-col gap-1 sm:gap-2 text-sm sm:text-base 2xl:text-lg leading-6 list-disc list-inside">
          {contactInfo.map((item, index) => (
            <li key={index}>
              {item.label && <span>{item.label}: </span>}
              {item.link ? (
                <a href={item.link} className="underline">
                  {item.value}
                </a>
              ) : (
                <span>{item.value}</span>
              )}
            </li>
          ))}
        </ul>
      </div>

      {/* Bottom Section */}
      <div className="w-full max-w-screen-lg xl:max-w-screen-xl 2xl:max-w-[1600px] flex flex-col md:flex-row items-center justify-between gap-4 md:gap-0">
        <p className="text-sm sm:text-base 2xl:text-lg text-[#FEFEFE] opacity-75">
          © {new Date().getFullYear()}. All rights reserved.
        </p>

        <div className="flex items-center justify-center">
          <img
            src={ASSETS.LOGO}
            alt="Logo"
            className="w-20 h-20 sm:w-24 sm:h-24 md:w-28 md:h-28 2xl:w-36 2xl:h-36 rounded-full object-cover"
          />
        </div>

        <div className="flex flex-row gap-4 sm:gap-6 md:gap-8">
          <a className="text-sm sm:text-base 2xl:text-lg">Terms of Service</a>
          <a className="text-sm sm:text-base 2xl:text-lg">Privacy Policy</a>
        </div>
      </div>
    </footer>
  );
}
