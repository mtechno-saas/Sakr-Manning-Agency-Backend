// components/dashboard/Modals/CrewManagementModal.jsx
import React, { useState, useEffect, useCallback } from "react";
import { X, Search, UserPlus, UserMinus, Loader2 } from "lucide-react";
import Button from "../Common/Button";
import { getModalStyles } from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";
import { shipsApi } from "../../../../services/Dashboard/shipsApi";
import { usersApi } from "../../../../services/Dashboard/usersApi";
import useNotification from "../../hooks/useNotification";

const CrewManagementModal = ({
    isOpen,
    onClose,
    ship,
    scale = 1
}) => {
    const [crew, setCrew] = useState([]);
    const [loadingCrew, setLoadingCrew] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [searchResults, setSearchResults] = useState([]);
    const [searching, setSearching] = useState(false);
    const { notify } = useNotification();

    const modalStyles = getModalStyles(scale);
    const titleStyles = getModalTitleStyles(scale);

    const fetchCrew = useCallback(async () => {
        if (!ship?.id) return;
        setLoadingCrew(true);
        try {
            const data = await shipsApi.getShipCrew(ship.id);
            setCrew(data);
        } catch (error) {
            notify.error("Failed to load crew members");
        } finally {
            setLoadingCrew(false);
        }
    }, [ship?.id, notify]);

    useEffect(() => {
        if (isOpen) {
            fetchCrew();
        }
    }, [isOpen, fetchCrew]);

    const handleSearch = async (e) => {
        const val = e.target.value;
        setSearchTerm(val);
        
        if (val.length < 2) {
            setSearchResults([]);
            return;
        }

        setSearching(true);
        try {
            const results = await usersApi.searchUsers({ search: val, limit: 5 });
            // Filter out existing crew
            const crewIds = new Set(crew.map(member => member.id));
            setSearchResults(results.filter(user => !crewIds.has(user.id)));
        } catch (error) {
            console.error("Search failed:", error);
        } finally {
            setSearching(false);
        }
    };

    const handleAssign = async (user) => {
        try {
            await shipsApi.assignUserToShip(ship.id, user.id);
            notify.success(`Assigned ${user.label} to ${ship.ship_name}`);
            setSearchTerm("");
            setSearchResults([]);
            fetchCrew();
        } catch (error) {
            notify.error(error.message || "Failed to assign user");
        }
    };

    const handleUnassign = async (user) => {
        if (!window.confirm(`Are you sure you want to remove ${user.first_name || user.email} from the crew?`)) return;
        
        try {
            await shipsApi.unassignUserFromShip(ship.id, user.id);
            notify.success("User removed from crew");
            fetchCrew();
        } catch (error) {
            notify.error(error.message || "Failed to remove user");
        }
    };

    if (!isOpen) return null;

    return (
        <div 
            style={{ ...modalStyles.overlay, zIndex: 1100 }} 
            onClick={onClose}
            onMouseDown={e => e.stopPropagation()}
        >
            <div 
                style={{
                    ...modalStyles.panel,
                    maxWidth: `${Math.round(600 * scale)}px`,
                    width: "100%",
                }} 
                onClick={e => e.stopPropagation()}
                onMouseDown={e => e.stopPropagation()}
            >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: `${Math.round(20 * scale)}px` }}>
                    <h2 style={titleStyles}>Manage Crew: {ship.ship_name}</h2>
                    <button onClick={onClose} style={{ border: "none", background: "none", cursor: "pointer", color: "#6B7280" }}>
                        <X size={Math.round(24 * scale)} />
                    </button>
                </div>

                {/* Assignment Search */}
                <div style={{ marginBottom: `${Math.round(24 * scale)}px` }}>
                    <label style={{ display: "block", fontSize: `${Math.round(14 * scale)}px`, fontWeight: 500, color: "#374151", marginBottom: `${Math.round(8 * scale)}px` }}>
                        Assign New Seafarer
                    </label>
                    <div style={{ position: "relative" }}>
                        <div style={{ position: "absolute", left: `${Math.round(12 * scale)}px`, top: "50%", transform: "translateY(-50%)", color: "#9CA3AF" }}>
                            {searching ? <Loader2 size={Math.round(18 * scale)} className="animate-spin" /> : <Search size={Math.round(18 * scale)} />}
                        </div>
                        <input 
                            type="text"
                            placeholder="Search by name or email..."
                            value={searchTerm}
                            onChange={handleSearch}
                            style={{
                                width: "100%",
                                padding: `${Math.round(10 * scale)}px ${Math.round(40 * scale)}px`,
                                borderRadius: `${Math.round(8 * scale)}px`,
                                border: "1px solid #D1D5DB",
                                fontSize: `${Math.round(14 * scale)}px`,
                                outline: "none",
                            }}
                        />
                        
                        {searchResults.length > 0 && (
                            <div style={{
                                position: "absolute",
                                top: "100%",
                                left: 0,
                                right: 0,
                                backgroundColor: "white",
                                border: "1px solid #D1D5DB",
                                borderRadius: `${Math.round(8 * scale)}px`,
                                marginTop: `${Math.round(4 * scale)}px`,
                                boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                                zIndex: 10,
                                overflow: "hidden"
                            }}>
                                {searchResults.map(result => (
                                    <div 
                                        key={result.id}
                                        onClick={() => handleAssign(result)}
                                        style={{
                                            padding: `${Math.round(12 * scale)}px`,
                                            display: "flex",
                                            justifyContent: "space-between",
                                            alignItems: "center",
                                            cursor: "pointer",
                                            borderBottom: "1px solid #F3F4F6"
                                        }}
                                        onMouseEnter={e => e.currentTarget.style.backgroundColor = "#F9FAFB"}
                                        onMouseLeave={e => e.currentTarget.style.backgroundColor = "white"}
                                    >
                                        <div style={{ display: "flex", alignItems: "center", gap: `${Math.round(8 * scale)}px` }}>
                                            <div style={{ width: `${Math.round(32 * scale)}px`, height: `${Math.round(32 * scale)}px`, borderRadius: "50%", backgroundColor: "#E5E7EB", display: "flex", alignItems: "center", justifyContent: "center" }}>
                                                <Users size={Math.round(16 * scale)} color="#6B7280" />
                                            </div>
                                            <div>
                                                <div style={{ fontSize: `${Math.round(14 * scale)}px`, fontWeight: 500 }}>{result.label}</div>
                                                <div style={{ fontSize: `${Math.round(12 * scale)}px`, color: "#6B7280" }}>{result.email}</div>
                                            </div>
                                        </div>
                                        <UserPlus size={Math.round(18 * scale)} color="#0EA5E9" />
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Current Crew List */}
                <div>
                    <h3 style={{ fontSize: `${Math.round(16 * scale)}px`, fontWeight: 600, color: "#111827", marginBottom: `${Math.round(12 * scale)}px` }}>
                        Current Crew ({crew.length})
                    </h3>
                    
                    {loadingCrew ? (
                        <div style={{ textAlign: "center", padding: `${Math.round(40 * scale)}px` }}>
                            <Loader2 className="animate-spin" style={{ margin: "0 auto", color: "#0EA5E9" }} />
                            <p style={{ marginTop: `${Math.round(8 * scale)}px`, color: "#6B7280" }}>Loading crew members...</p>
                        </div>
                    ) : crew.length === 0 ? (
                        <div style={{ textAlign: "center", padding: `${Math.round(40 * scale)}px`, backgroundColor: "#F9FAFB", borderRadius: `${Math.round(8 * scale)}px`, color: "#6B7280" }}>
                            No crew members assigned to this ship.
                        </div>
                    ) : (
                        <div style={{ display: "flex", flexDirection: "column", gap: `${Math.round(8 * scale)}px`, maxHeight: `${Math.round(300 * scale)}px`, overflowY: "auto" }}>
                            {crew.map(member => (
                                <div 
                                    key={member.id}
                                    style={{
                                        display: "flex",
                                        justifyContent: "space-between",
                                        alignItems: "center",
                                        padding: `${Math.round(12 * scale)}px`,
                                        backgroundColor: "#F9FAFB",
                                        borderRadius: `${Math.round(8 * scale)}px`,
                                        border: "1px solid #F3F4F6"
                                    }}
                                >
                                    <div style={{ display: "flex", alignItems: "center", gap: `${Math.round(12 * scale)}px` }}>
                                        <div style={{ width: `${Math.round(40 * scale)}px`, height: `${Math.round(40 * scale)}px`, borderRadius: "50%", backgroundColor: "#0EA5E9", display: "flex", alignItems: "center", justifyContent: "center", color: "white", fontSize: `${Math.round(16 * scale)}px`, fontWeight: 600 }}>
                                            {(member.first_name || 'U')[0]}
                                        </div>
                                        <div>
                                            <div style={{ fontSize: `${Math.round(14 * scale)}px`, fontWeight: 600, color: "#111827" }}>
                                                {member.first_name} {member.last_name}
                                            </div>
                                            <div style={{ fontSize: `${Math.round(12 * scale)}px`, color: "#6B7280" }}>
                                                {member.rank_name || "Seafarer"} • {member.email}
                                            </div>
                                        </div>
                                    </div>
                                    <button 
                                        onClick={() => handleUnassign(member)}
                                        style={{ 
                                            background: "none", 
                                            border: "none", 
                                            padding: `${Math.round(8 * scale)}px`, 
                                            cursor: "pointer", 
                                            color: "#EF4444",
                                            borderRadius: "50%"
                                        }}
                                        onMouseEnter={e => e.currentTarget.style.backgroundColor = "#FEE2E2"}
                                        onMouseLeave={e => e.currentTarget.style.backgroundColor = "transparent"}
                                        title="Remove from crew"
                                    >
                                        <UserMinus size={Math.round(18 * scale)} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div style={{ marginTop: `${Math.round(24 * scale)}px`, display: "flex", justifyContent: "flex-end" }}>
                    <Button variant="primary" onClick={onClose} scale={scale}>Done</Button>
                </div>
            </div>
        </div>
    );
};

// Internal icon component for search results
function Users({ size, color }) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke={color}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
    );
}

export default CrewManagementModal;
