import React from "react";
import { Loader2, Ship } from "lucide-react";
import { COLORS } from "../../Constants";

/**
 * LoadingScreen - A modern, premium loading screen for the dashboard.
 * 
 * Features:
 * - Centered layout with subtle backdrop
 * - Animated ship icon + spinner
 * - Descriptive message
 * - Support for scale factor
 * - Full screen or container-relative modes
 */
const LoadingScreen = ({ 
    message = "Loading your dashboard...", 
    subMessage = "Setting up your maritime operations",
    scale = 1,
    fullScreen = false
}) => {
    const containerStyle = {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        width: "100%",
        height: fullScreen ? "100vh" : "100%",
        minHeight: fullScreen ? "auto" : "400px",
        backgroundColor: fullScreen ? COLORS.background : "transparent",
        flex: 1,
    };

    const logoContainerStyle = {
        position: "relative",
        marginBottom: `${Math.round(24 * scale)}px`,
    };

    const pulseStyle = `
        @keyframes pulse-ring {
            0% { transform: scale(.33); opacity: 0; }
            50% { opacity: 0.5; }
            100% { transform: scale(1.2); opacity: 0; }
        }
        @keyframes float-ship {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
    `;

    return (
        <div style={containerStyle}>
            <style>{pulseStyle}</style>
            
            <div style={logoContainerStyle}>
                {/* Pulse rings */}
                <div style={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%, -50%)",
                    width: `${Math.round(120 * scale)}px`,
                    height: `${Math.round(120 * scale)}px`,
                    borderRadius: "50%",
                    backgroundColor: "rgba(99, 102, 241, 0.1)",
                    animation: "pulse-ring 2s cubic-bezier(0.215, 0.61, 0.355, 1) infinite"
                }} />
                
                {/* Ship Icon with floating animation */}
                <div style={{
                    position: "relative",
                    width: `${Math.round(80 * scale)}px`,
                    height: `${Math.round(80 * scale)}px`,
                    borderRadius: "50%",
                    backgroundColor: "white",
                    boxShadow: "0 10px 25px rgba(0,0,0,0.05)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    animation: "float-ship 3s ease-in-out infinite",
                    zIndex: 2
                }}>
                    <Ship size={Math.round(40 * scale)} color="#4F46E5" strokeWidth={1.5} />
                </div>

                {/* Spinning border around the ship */}
                <div style={{
                    position: "absolute",
                    top: `-${Math.round(4 * scale)}px`,
                    left: `-${Math.round(4 * scale)}px`,
                    right: `-${Math.round(4 * scale)}px`,
                    bottom: `-${Math.round(4 * scale)}px`,
                    border: `${Math.round(2 * scale)}px solid transparent`,
                    borderTopColor: "#4F46E5",
                    borderRadius: "50%",
                    animation: "spin 1.5s linear infinite"
                }} />
            </div>

            <h3 style={{
                fontSize: `${Math.round(20 * scale)}px`,
                fontWeight: 600,
                color: "#111827",
                margin: 0,
                fontFamily: "Inter, sans-serif"
            }}>
                {message}
            </h3>
            
            <p style={{
                fontSize: `${Math.round(14 * scale)}px`,
                color: "#6B7280",
                margin: `${Math.round(8 * scale)}px 0 0`,
                fontFamily: "Inter, sans-serif"
            }}>
                {subMessage}
            </p>

            <div style={{
                marginTop: `${Math.round(32 * scale)}px`,
                display: "flex",
                alignItems: "center",
                gap: `${Math.round(8 * scale)}px`,
                color: "#9CA3AF"
            }}>
                <Loader2 size={Math.round(16 * scale)} className="animate-spin" />
                <span style={{ fontSize: `${Math.round(12 * scale)}px`, fontWeight: 500, letterSpacing: "0.05em", textTransform: "uppercase" }}>
                    Synchronizing Data
                </span>
            </div>
        </div>
    );
};

export default LoadingScreen;
