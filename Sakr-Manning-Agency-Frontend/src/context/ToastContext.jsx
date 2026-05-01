import { createContext, useState, useCallback, useContext, useRef, useMemo } from "react";
import "../components/form/layout/ToastContainer.css";

const ToastContext = createContext(null);

// ─── Toast Item Component ───────────────────────────────────────────────────
function ToastItem({ toast, onClose }) {
  const typeConfig = {
    success: { icon: "✓", bg: "#f0f9ee", border: "#c6e7c0", color: "#2e7d32" },
    error: { icon: "✕", bg: "#fef2f2", border: "#f5c6c6", color: "#c62828" },
    warning: { icon: "⚠", bg: "#fffbeb", border: "#fde68a", color: "#b45309" },
    info: { icon: "ℹ", bg: "#eff6ff", border: "#bfdbfe", color: "#1e40af" },
  };

  const config = typeConfig[toast.type] || typeConfig.info;

  return (
    <div
      className="toast-item toast-slide-in"
      role="alert"
      aria-live="polite"
      style={{
        display: "flex",
        alignItems: "flex-start",
        gap: "12px",
        padding: "14px 16px",
        backgroundColor: config.bg,
        border: `1px solid ${config.border}`,
        borderRadius: "10px",
        boxShadow: "0 4px 16px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.06)",
        minWidth: "320px",
        maxWidth: "420px",
        fontFamily: "'Inter', 'Segoe UI', sans-serif",
        fontSize: "14px",
        lineHeight: "1.5",
        color: "#374151",
      }}
    >
      {/* Icon */}
      <span
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          width: "24px",
          height: "24px",
          borderRadius: "50%",
          backgroundColor: `${config.color}18`,
          color: config.color,
          fontSize: "13px",
          fontWeight: "700",
          flexShrink: 0,
        }}
      >
        {config.icon}
      </span>

      {/* Message */}
      <div style={{ flex: 1, fontWeight: 500, wordBreak: "break-word" }}>
        {toast.message}
      </div>

      {/* Close button */}
      <button
        onClick={() => onClose(toast.id)}
        style={{
          background: "none",
          border: "none",
          color: "#9ca3af",
          cursor: "pointer",
          padding: "2px",
          fontSize: "14px",
          lineHeight: 1,
          flexShrink: 0,
          transition: "color 0.15s",
        }}
        onMouseEnter={(e) => (e.currentTarget.style.color = "#374151")}
        onMouseLeave={(e) => (e.currentTarget.style.color = "#9ca3af")}
        aria-label="Close notification"
      >
        ✕
      </button>
    </div>
  );
}

// ─── Toast Container ────────────────────────────────────────────────────────
function ToastContainer({ toasts, onClose }) {
  return (
    <div
      className="toast-container"
      role="region"
      aria-label="Notifications"
      aria-live="polite"
      style={{
        position: "fixed",
        bottom: "20px",
        right: "20px",
        display: "flex",
        flexDirection: "column",
        gap: "10px",
        zIndex: 9999,
        pointerEvents: "none",
      }}
    >
      {toasts.map((toast) => (
        <div key={toast.id} style={{ pointerEvents: "auto" }}>
          <ToastItem toast={toast} onClose={onClose} />
        </div>
      ))}
    </div>
  );
}

// ─── Duration defaults (ms) ─────────────────────────────────────────────────
const DURATIONS = {
  success: 1000,
  error: 3000,
  warning: 2000,
  info: 2000,
};

// ─── Provider ───────────────────────────────────────────────────────────────
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const idRef = useRef(0);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = useCallback(
    (type, message, duration) => {
      const id = `toast-${idRef.current++}`;
      const ms = duration ?? DURATIONS[type] ?? 3000;

      setToasts((prev) => [...prev, { id, type, message }]);

      if (ms > 0) {
        setTimeout(() => removeToast(id), ms);
      }
      return id;
    },
    [removeToast]
  );

  const notify = useMemo(() => ({
    success: (msg, ms) => addToast("success", msg, ms),
    error: (msg, ms) => addToast("error", msg, ms),
    warning: (msg, ms) => addToast("warning", msg, ms),
    info: (msg, ms) => addToast("info", msg, ms),
  }), [addToast]);

  return (
    <ToastContext.Provider value={{ notify, addToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} onClose={removeToast} />
    </ToastContext.Provider>
  );
}

// ─── Hook ───────────────────────────────────────────────────────────────────
export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error("useToast must be used within <ToastProvider>");
  }
  return ctx;
}

export default ToastContext;
