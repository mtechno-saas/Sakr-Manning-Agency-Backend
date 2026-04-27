import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Clock, ArrowLeft } from "lucide-react";
import PropTypes from "prop-types";

/**
 * PendingStatusModal
 *
 * Full-screen overlay informing the user their Quick Apply
 * is under review. Shows a "Go Home" button to navigate away.
 */
export default function PendingStatusModal({ isOpen, onGoHome }) {
    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.25 }}
                        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
                        aria-hidden="true"
                    />

                    {/* Modal */}
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.92, y: 30 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.92, y: 30 }}
                            transition={{ type: "spring", duration: 0.5, bounce: 0.25 }}
                            className="relative w-full max-w-md bg-white rounded-[20px] shadow-2xl overflow-hidden"
                            role="dialog"
                            aria-modal="true"
                            aria-labelledby="pending-modal-title"
                        >
                            {/* Accent bar */}
                            <div
                                style={{
                                    height: "6px",
                                    background:
                                        "linear-gradient(90deg, #0065AF 0%, #00A3E0 100%)",
                                }}
                            />

                            <div className="px-8 py-10 text-center">
                                {/* Icon */}
                                <div
                                    className="mx-auto mb-5 flex items-center justify-center"
                                    style={{
                                        width: 72,
                                        height: 72,
                                        borderRadius: "50%",
                                        background:
                                            "linear-gradient(135deg, #EBF5FF 0%, #DBEAFE 100%)",
                                    }}
                                >
                                    <Clock size={36} color="#0065AF" strokeWidth={1.8} />
                                </div>

                                {/* Title */}
                                <h2
                                    id="pending-modal-title"
                                    style={{
                                        fontSize: "22px",
                                        fontWeight: 600,
                                        color: "#0F172A",
                                        marginBottom: "12px",
                                        fontFamily: "'Poppins', sans-serif",
                                    }}
                                >
                                    Application Under Review
                                </h2>

                                {/* Body */}
                                <p
                                    style={{
                                        fontSize: "15px",
                                        lineHeight: 1.7,
                                        color: "#64748B",
                                        marginBottom: "8px",
                                        fontFamily: "'Poppins', sans-serif",
                                    }}
                                >
                                    Your application has been received and is currently being
                                    reviewed by our recruitment team.
                                </p>
                                <p
                                    style={{
                                        fontSize: "14px",
                                        lineHeight: 1.7,
                                        color: "#94A3B8",
                                        marginBottom: "32px",
                                        fontFamily: "'Poppins', sans-serif",
                                    }}
                                >
                                    You will be notified once your application has been approved
                                    and you can proceed with the full form.
                                </p>

                                {/* Go Home button */}
                                <button
                                    onClick={onGoHome}
                                    style={{
                                        display: "inline-flex",
                                        alignItems: "center",
                                        justifyContent: "center",
                                        gap: "8px",
                                        width: "100%",
                                        maxWidth: "260px",
                                        padding: "14px 28px",
                                        borderRadius: "24px",
                                        border: "none",
                                        background:
                                            "linear-gradient(135deg, #0065AF 0%, #0088D4 100%)",
                                        color: "#ffffff",
                                        fontSize: "15px",
                                        fontWeight: 500,
                                        fontFamily: "'Poppins', sans-serif",
                                        cursor: "pointer",
                                        transition: "all 0.2s ease",
                                        boxShadow: "0 4px 14px rgba(0, 101, 175, 0.35)",
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.transform = "translateY(-1px)";
                                        e.currentTarget.style.boxShadow =
                                            "0 6px 20px rgba(0, 101, 175, 0.4)";
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.transform = "translateY(0)";
                                        e.currentTarget.style.boxShadow =
                                            "0 4px 14px rgba(0, 101, 175, 0.35)";
                                    }}
                                >
                                    <ArrowLeft size={18} />
                                    Go Home
                                </button>
                            </div>
                        </motion.div>
                    </div>
                </>
            )}
        </AnimatePresence>
    );
}

PendingStatusModal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onGoHome: PropTypes.func.isRequired,
};
