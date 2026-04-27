// components/layout/Background.jsx
import React from "react";
import { ASSETS } from "../../utils/constants";

const Background = () => {
  return (
    <div className="absolute inset-0 overflow-hidden transform scale-x-[-1]">
      {/* Background Image - Maritime Ship Scene */}
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat animate-slow-zoom"
        style={{
          backgroundImage: `url(${ASSETS.BACKGROUND})`,
          filter: "brightness(0.8) contrast(1.1) saturate(1.1)",
        }}
      />

      {/* Subtle Dark Overlay for Better Text Contrast */}
      <div className="absolute inset-0 bg-gradient-to-r from-black/30 via-transparent to-black/20"></div>

      {/* Light Maritime Tinted Overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-maritime-600/15 via-transparent to-maritime-500/20 animate-gradient-shift"></div>

      {/* Floating Light Elements for Enhancement */}
      <div className="absolute inset-0 opacity-60">
        <div className="absolute top-1/4 left-1/4 w-1 h-1 bg-white/40 rounded-full animate-float-1"></div>
        <div className="absolute top-1/3 right-1/3 w-0.5 h-0.5 bg-maritime-200/60 rounded-full animate-float-2"></div>
        <div className="absolute bottom-1/3 left-1/6 w-1.5 h-1.5 bg-white/30 rounded-full animate-float-3"></div>
        <div className="absolute top-2/3 right-1/4 w-0.5 h-0.5 bg-maritime-200/50 rounded-full animate-float-4"></div>
        <div className="absolute top-1/2 left-1/2 w-1 h-1 bg-maritime-100/40 rounded-full animate-float-5"></div>
      </div>

      {/* Subtle Grid Pattern Overlay */}
      <div
        className="absolute inset-0 opacity-5"
        style={{
          backgroundImage: `
            linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)
          `,
          backgroundSize: "60px 60px",
        }}
      />

      {/* CSS Animations */}
      <style>{`
        @keyframes slow-zoom {
          0%,
          100% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.05);
          }
        }

        @keyframes gradient-shift {
          0%,
          100% {
            opacity: 1;
          }
          50% {
            opacity: 0.7;
          }
        }

        @keyframes float-1 {
          0%,
          100% {
            transform: translate(0, 0);
            opacity: 0.4;
          }
          50% {
            transform: translate(8px, -12px);
            opacity: 0.8;
          }
        }

        @keyframes float-2 {
          0%,
          100% {
            transform: translate(0, 0);
            opacity: 0.6;
          }
          50% {
            transform: translate(-10px, 8px);
            opacity: 0.3;
          }
        }

        @keyframes float-3 {
          0%,
          100% {
            transform: translate(0, 0);
            opacity: 0.3;
          }
          50% {
            transform: translate(15px, -18px);
            opacity: 0.7;
          }
        }

        @keyframes float-4 {
          0%,
          100% {
            transform: translate(0, 0);
            opacity: 0.5;
          }
          50% {
            transform: translate(-12px, 10px);
            opacity: 0.2;
          }
        }

        @keyframes float-5 {
          0%,
          100% {
            transform: translate(0, 0) scale(1);
            opacity: 0.4;
          }
          50% {
            transform: translate(-8px, -15px) scale(1.2);
            opacity: 0.8;
          }
        }

        .animate-slow-zoom {
          animation: slow-zoom 30s ease-in-out infinite;
        }

        .animate-gradient-shift {
          animation: gradient-shift 15s ease-in-out infinite;
        }

        .animate-float-1 {
          animation: float-1 20s ease-in-out infinite;
        }

        .animate-float-2 {
          animation: float-2 18s ease-in-out infinite 3s;
        }

        .animate-float-3 {
          animation: float-3 25s ease-in-out infinite 1s;
        }

        .animate-float-4 {
          animation: float-4 22s ease-in-out infinite 4s;
        }

        .animate-float-5 {
          animation: float-5 16s ease-in-out infinite 2s;
        }
      `}</style>
    </div>
  );
};

export default Background;
