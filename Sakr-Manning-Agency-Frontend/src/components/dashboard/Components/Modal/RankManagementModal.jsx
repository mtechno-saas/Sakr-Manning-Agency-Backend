// components/dashboard/Modals/RankManagementModal.jsx
// Updated to use the position-based rank assignment API:
//   GET  /api/positions/                              → position dropdown
//   POST /api/users/{userId}/assign-by-position/      → { position } → auto-generates assigned_code
//   GET  /api/users/{userId}/ranks/                   → list current user ranks
//   DEL  /api/users/{userId}/ranks/{id}/remove/       → remove a rank
import React, { useState, useEffect, useCallback } from "react";
import { X, Anchor, ChevronDown, Trash2, Loader2, CheckCircle2 } from "lucide-react";
import Button from "../Common/Button";
import { getModalStyles } from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";
import { usersApi } from "../../../../services/Dashboard/usersApi";
import useNotification from "../../hooks/useNotification";

const RankManagementModal = ({ isOpen, onClose, user, scale = 1 }) => {
    const [userRanks, setUserRanks]         = useState([]);
    const [positions, setPositions]         = useState([]);
    const [selectedPosition, setSelectedPosition] = useState("");
    const [loadingRanks, setLoadingRanks]   = useState(true);
    const [loadingPositions, setLoadingPositions] = useState(true);
    const [assigning, setAssigning]         = useState(false);
    const [lastAssigned, setLastAssigned]   = useState(null); // { assigned_code, rank_name }
    const { notify } = useNotification();

    const modalStyles = getModalStyles(scale);
    const titleStyles = getModalTitleStyles(scale);

    // ── Fetch current user ranks ───────────────────────────────────────────────
    const fetchUserRanks = useCallback(async () => {
        if (!user?.id) return;
        setLoadingRanks(true);
        try {
            const data = await usersApi.getUserRanks(user.id);
            const list = Array.isArray(data)
                ? data
                : data.results || data.user_ranks || [];
            setUserRanks(list);
        } catch (err) {
            notify.error("Failed to load user ranks");
        } finally {
            setLoadingRanks(false);
        }
    }, [user?.id, notify]);

    // ── Fetch positions dropdown ───────────────────────────────────────────────
    const fetchPositions = useCallback(async () => {
        setLoadingPositions(true);
        try {
            const data = await usersApi.getPositions();
            setPositions(data);
        } catch (err) {
            notify.error("Failed to load positions");
        } finally {
            setLoadingPositions(false);
        }
    }, [notify]);

    useEffect(() => {
        if (isOpen) {
            fetchUserRanks();
            fetchPositions();
            setSelectedPosition("");
            setLastAssigned(null);
        }
    }, [isOpen, fetchUserRanks, fetchPositions]);

    // ── Assign by position ─────────────────────────────────────────────────────
    const handleAssign = async () => {
        if (!selectedPosition) {
            notify.error("Please select a position first");
            return;
        }
        setAssigning(true);
        setLastAssigned(null);
        try {
            const result = await usersApi.assignByPosition(user.id, selectedPosition);
            const code = result.user_rank?.assigned_code || "";
            const name = result.user_rank?.rank_name || selectedPosition;
            notify.success(result.message || `Rank "${name}" assigned — code: ${code}`);
            setLastAssigned({ assigned_code: code, rank_name: name });
            setSelectedPosition("");
            await fetchUserRanks();
        } catch (err) {
            // Parse the backend error message
            const msg = err.message || "Failed to assign rank";
            notify.error(msg);
        } finally {
            setAssigning(false);
        }
    };

    // ── Remove rank ────────────────────────────────────────────────────────────
    const handleRemove = async (userRank) => {
        const name = userRank.rank?.name || userRank.rank_name || "rank";
        if (!window.confirm(`Remove "${name}" from this user?`)) return;
        try {
            await usersApi.removeRankFromUser(user.id, userRank.id);
            notify.success(`Rank "${name}" removed`);
            await fetchUserRanks();
        } catch (err) {
            notify.error(err.message || "Failed to remove rank");
        }
    };

    if (!isOpen) return null;

    const userName = [user?.first_name, user?.last_name].filter(Boolean).join(" ") || user?.email || "User";

    // Already-assigned position values (to visually mark them in the dropdown)
    const assignedPositionNames = new Set(userRanks.map(ur => ur.rank?.name || ur.rank_name || ""));

    return (
        <div style={modalStyles.overlay} onClick={onClose}>
            <div
                style={{
                    ...modalStyles.panel,
                    maxWidth: `${Math.round(660 * scale)}px`,
                    width: "100%",
                    maxHeight: "90vh",
                    overflowY: "auto",
                }}
                onClick={(e) => e.stopPropagation()}
            >
                {/* ── Header ─────────────────────────────────────────────────────── */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: `${Math.round(20 * scale)}px` }}>
                    <div>
                        <h2 style={titleStyles}>Assign Coded Rank</h2>
                        <p style={{ margin: 0, fontSize: `${Math.round(13 * scale)}px`, color: "#6B7280" }}>{userName}</p>
                    </div>
                    <button onClick={onClose} style={{ border: "none", background: "none", cursor: "pointer", color: "#6B7280", padding: `${Math.round(4 * scale)}px` }}>
                        <X size={Math.round(22 * scale)} />
                    </button>
                </div>

                {/* ── Position selector ──────────────────────────────────────────── */}
                <div style={{
                    background: "#F8F7FF",
                    border: "1px solid #E9E6FF",
                    borderRadius: `${Math.round(12 * scale)}px`,
                    padding: `${Math.round(20 * scale)}px`,
                    marginBottom: `${Math.round(24 * scale)}px`,
                }}>
                    <label style={{
                        display: "block",
                        fontSize: `${Math.round(13 * scale)}px`,
                        fontWeight: 600,
                        color: "#374151",
                        marginBottom: `${Math.round(10 * scale)}px`,
                    }}>
                        Select Position
                    </label>

                    <div style={{ position: "relative" }}>
                        <select
                            value={selectedPosition}
                            onChange={(e) => setSelectedPosition(e.target.value)}
                            disabled={loadingPositions || assigning}
                            style={{
                                width: "100%",
                                appearance: "none",
                                padding: `${Math.round(11 * scale)}px ${Math.round(40 * scale)}px ${Math.round(11 * scale)}px ${Math.round(14 * scale)}px`,
                                borderRadius: `${Math.round(8 * scale)}px`,
                                border: "1.5px solid #D1D5DB",
                                fontSize: `${Math.round(14 * scale)}px`,
                                color: selectedPosition ? "#111827" : "#9CA3AF",
                                background: "#fff",
                                outline: "none",
                                cursor: loadingPositions ? "wait" : "pointer",
                                boxSizing: "border-box",
                            }}
                        >
                            <option value="">
                                {loadingPositions ? "Loading positions…" : "— Choose a position —"}
                            </option>
                            {positions.map((p) => {
                                const alreadyAssigned = assignedPositionNames.has(p.value);
                                return (
                                    <option key={p.value} value={p.value} disabled={alreadyAssigned}>
                                        {alreadyAssigned ? `✓ ${p.label} (already assigned)` : p.label}
                                    </option>
                                );
                            })}
                        </select>
                        <div style={{
                            position: "absolute",
                            right: `${Math.round(12 * scale)}px`,
                            top: "50%",
                            transform: "translateY(-50%)",
                            pointerEvents: "none",
                            color: "#9CA3AF",
                        }}>
                            {loadingPositions
                                ? <Loader2 size={Math.round(16 * scale)} style={{ animation: "spin 1s linear infinite" }} />
                                : <ChevronDown size={Math.round(16 * scale)} />
                            }
                        </div>
                    </div>

                    <div style={{ marginTop: `${Math.round(14 * scale)}px`, display: "flex", justifyContent: "flex-end" }}>
                        <Button
                            variant="primary"
                            scale={scale}
                            onClick={handleAssign}
                            disabled={!selectedPosition || assigning}
                            style={{
                                opacity: (!selectedPosition || assigning) ? 0.6 : 1,
                                cursor: (!selectedPosition || assigning) ? "not-allowed" : "pointer",
                            }}
                        >
                            {assigning
                                ? <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                                    <Loader2 size={Math.round(14 * scale)} style={{ animation: "spin 1s linear infinite" }} />
                                    Assigning…
                                  </span>
                                : "Assign Rank"
                            }
                        </Button>
                    </div>

                    {/* Success banner for last assignment */}
                    {lastAssigned && (
                        <div style={{
                            marginTop: `${Math.round(12 * scale)}px`,
                            display: "flex",
                            alignItems: "center",
                            gap: `${Math.round(8 * scale)}px`,
                            padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                            background: "#ECFDF5",
                            border: "1px solid #A7F3D0",
                            borderRadius: `${Math.round(8 * scale)}px`,
                            fontSize: `${Math.round(13 * scale)}px`,
                            color: "#065F46",
                        }}>
                            <CheckCircle2 size={Math.round(16 * scale)} color="#059669" />
                            <span>
                                <strong>{lastAssigned.rank_name}</strong> assigned —&nbsp;
                                code: <span style={{ fontFamily: "monospace", fontWeight: 700 }}>{lastAssigned.assigned_code}</span>
                            </span>
                        </div>
                    )}
                </div>

                {/* ── Assigned Ranks List ────────────────────────────────────────── */}
                <div>
                    <h3 style={{ fontSize: `${Math.round(15 * scale)}px`, fontWeight: 700, color: "#111827", marginBottom: `${Math.round(12 * scale)}px` }}>
                        Assigned Ranks ({userRanks.length})
                    </h3>

                    {loadingRanks ? (
                        <div style={{ textAlign: "center", padding: `${Math.round(40 * scale)}px`, color: "#6B7280" }}>
                            <Loader2 style={{ display: "inline-block", animation: "spin 1s linear infinite", color: "#6366F1" }} size={Math.round(24 * scale)} />
                            <p style={{ marginTop: `${Math.round(8 * scale)}px` }}>Loading ranks…</p>
                        </div>
                    ) : userRanks.length === 0 ? (
                        <div style={{
                            textAlign: "center",
                            padding: `${Math.round(32 * scale)}px`,
                            background: "#F9FAFB",
                            borderRadius: `${Math.round(10 * scale)}px`,
                            color: "#9CA3AF",
                            fontSize: `${Math.round(14 * scale)}px`,
                        }}>
                            No ranks assigned to this user yet.
                        </div>
                    ) : (
                        <div style={{ display: "flex", flexDirection: "column", gap: `${Math.round(8 * scale)}px`, maxHeight: `${Math.round(320 * scale)}px`, overflowY: "auto" }}>
                            {userRanks.map((ur) => {
                                const rankName     = ur.rank?.name || ur.rank_name || "Unknown Rank";
                                const rankCode     = ur.rank?.code || ur.rank_code || "";
                                const assignedCode = ur.assigned_code || "";

                                return (
                                    <div
                                        key={ur.id}
                                        style={{
                                            display: "flex",
                                            justifyContent: "space-between",
                                            alignItems: "center",
                                            padding: `${Math.round(12 * scale)}px ${Math.round(16 * scale)}px`,
                                            backgroundColor: "#F8F7FF",
                                            borderRadius: `${Math.round(10 * scale)}px`,
                                            border: "1px solid #E9E6FF",
                                        }}
                                    >
                                        <div style={{ display: "flex", alignItems: "center", gap: `${Math.round(12 * scale)}px` }}>
                                            <div style={{
                                                width: `${Math.round(38 * scale)}px`,
                                                height: `${Math.round(38 * scale)}px`,
                                                borderRadius: "50%",
                                                background: "linear-gradient(135deg, #6366F1, #8B5CF6)",
                                                display: "flex",
                                                alignItems: "center",
                                                justifyContent: "center",
                                                flexShrink: 0,
                                            }}>
                                                <Anchor size={Math.round(16 * scale)} color="#fff" />
                                            </div>

                                            <div>
                                                <div style={{ fontSize: `${Math.round(14 * scale)}px`, fontWeight: 600, color: "#1F2937" }}>{rankName}</div>
                                                <div style={{ display: "flex", gap: `${Math.round(8 * scale)}px`, marginTop: "2px", flexWrap: "wrap" }}>
                                                    {rankCode && (
                                                        <span style={{
                                                            fontSize: `${Math.round(11 * scale)}px`,
                                                            fontFamily: "monospace",
                                                            color: "#6B7280",
                                                            backgroundColor: "#F3F4F6",
                                                            padding: "1px 6px",
                                                            borderRadius: "4px",
                                                        }}>
                                                            {rankCode}
                                                        </span>
                                                    )}
                                                    {assignedCode && (
                                                        <span style={{
                                                            fontSize: `${Math.round(11 * scale)}px`,
                                                            fontFamily: "monospace",
                                                            color: "#4F46E5",
                                                            backgroundColor: "#EEF2FF",
                                                            padding: "1px 6px",
                                                            borderRadius: "4px",
                                                            fontWeight: 600,
                                                        }}>
                                                            {assignedCode}
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>

                                        <button
                                            onClick={() => handleRemove(ur)}
                                            style={{
                                                background: "none",
                                                border: "none",
                                                padding: `${Math.round(8 * scale)}px`,
                                                cursor: "pointer",
                                                color: "#EF4444",
                                                borderRadius: "6px",
                                                transition: "background 0.15s",
                                            }}
                                            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#FEE2E2")}
                                            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
                                            title="Remove rank"
                                        >
                                            <Trash2 size={Math.round(16 * scale)} />
                                        </button>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* ── Footer ──────────────────────────────────────────────────────── */}
                <div style={{ marginTop: `${Math.round(24 * scale)}px`, display: "flex", justifyContent: "flex-end" }}>
                    <Button variant="primary" onClick={onClose} scale={scale}>Done</Button>
                </div>
            </div>

            <style>{`
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to   { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    );
};

export default RankManagementModal;
