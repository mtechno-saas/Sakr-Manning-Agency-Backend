// src/components/common/Newsletter.jsx - RESPONSIVE VERSION
import { useState } from "react";
// eslint-disable-next-line no-unused-vars
import { motion, AnimatePresence } from "framer-motion";

export default function Newsletter() {
  const [email, setEmail] = useState("");
  const [showSuccess, setShowSuccess] = useState(false);

  const handleSubscribe = () => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) return;

    setShowSuccess(true);
    setEmail("");

    setTimeout(() => setShowSuccess(false), 2000);
  };

  return (
    <div className="w-full max-w-[1093px] min-h-[199px] mx-auto bg-[#0065AF] rounded-2xl flex flex-col lg:flex-row items-center justify-between px-4 sm:px-6 lg:px-12 py-6 sm:py-8 lg:py-10 gap-4 lg:gap-6 relative">
      {/* Title */}
      <h2 className="text-xl sm:text-2xl lg:text-3xl font-normal text-white text-center lg:text-left lg:flex-1">
        Subscribe to our Newsletter
      </h2>

      {/* Input + Button Container */}
      <div className="w-full lg:flex-1 lg:max-w-xl">
        <div className="relative flex items-center w-full bg-white rounded-full px-4 sm:px-6 py-2">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            className="flex-1 w-full min-w-0 h-[51px] bg-transparent text-[#2B3D51] text-sm sm:text-base placeholder-gray-400 outline-none"
          />
          <button
            onClick={handleSubscribe}
            disabled={!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)}
            className={`absolute right-2 sm:right-3 top-1/2 -translate-y-1/2 rounded-2xl px-4 sm:px-6 py-1.5 sm:py-2 text-white text-sm sm:text-base font-normal transition whitespace-nowrap ${/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
                ? "bg-[#0058A3] hover:bg-[#004B82] cursor-pointer"
                : "bg-gray-400 cursor-not-allowed"
              }`}
          >
            Subscribe now
          </button>

          {/* Floating Success Bubble */}
          <AnimatePresence>
            {showSuccess && (
              <motion.div
                initial={{ opacity: 0, y: 0 }}
                animate={{ opacity: 1, y: -64 }}
                exit={{ opacity: 0, y: -96 }}
                transition={{ duration: 1.5, ease: "easeOut" }}
                className="absolute left-1/2 -translate-x-1/2 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg text-sm sm:text-base whitespace-nowrap"
              >
                ✅ Subscribed successfully!
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
