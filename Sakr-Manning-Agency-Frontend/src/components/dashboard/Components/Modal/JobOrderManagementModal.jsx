// components/dashboard/Components/Modal/JobOrderManagementModal.jsx
import React, { useState, useEffect, useCallback, useMemo } from "react";
import { X, Briefcase, Plus, Loader2, Trash2, Search, ChevronRight, UserPlus, FileText } from "lucide-react";
import Button from "../Common/Button";
import { getModalStyles } from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";
import { useJobOrders } from "../../../../hooks/dashboard/useJobOrders";
import { JOB_ORDER_FORM_FIELDS, JOB_POSITION_FORM_FIELDS, getDefaultValues, validateFormData, transformForSave } from "../../../../utils/dashboard/fieldConfigs";
import useNotification from "../../hooks/useNotification";
import { useDashboardData } from "../../context/DashboardDataContext";

// Import standard form components
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { DateInput } from "../inputs/DateInput";
import { TextArea } from "../../../form/inputs/TextArea";

const JobOrderManagementModal = ({
    isOpen,
    onClose,
    company,
    scale = 1
}) => {
    const { 
        jobOrders, 
        loading, 
        fetchJobOrders, 
        createJobOrder, 
        updateJobOrder,
        deleteJobOrder,
        addPositionToOrder,
        removePosition,
        canCreate,
        canDelete 
    } = useJobOrders();
    
    const { notify } = useNotification();
    const { referenceOptions, shipsByCompany, fetchShipsByCompany } = useDashboardData();
    const companyShips = useMemo(() => {
        if (!company?.id) return [];
        return shipsByCompany[company.id] || [];
    }, [shipsByCompany, company?.id]);
    
    // UI State
    const [selectedOrder, setSelectedOrder] = useState(null);
    const [searchTerm, setSearchTerm] = useState("");
    
    // Form States
    const [orderFormData, setOrderFormData] = useState(getDefaultValues(JOB_ORDER_FORM_FIELDS));
    const [posFormData, setPosFormData] = useState(getDefaultValues(JOB_POSITION_FORM_FIELDS));
    const [errors, setErrors] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    const modalStyles = getModalStyles(scale);
    const titleStyles = getModalTitleStyles(scale);

    // Initial Load
    useEffect(() => {
        if (isOpen && company?.id) {
            fetchJobOrders({ company: company.id });
            fetchShipsByCompany(company.id);
            // Pre-fill company in form state so validation passes
            setOrderFormData(prev => ({ ...prev, company: company.id }));
        }
    }, [isOpen, company?.id, fetchJobOrders, fetchShipsByCompany]);

    // Filtered list
    const filteredOrders = useMemo(() => {
        if (!Array.isArray(jobOrders)) return [];
        if (!searchTerm) return jobOrders;
        const lower = searchTerm.toLowerCase();
        return jobOrders.filter(o => 
            o.reference_number.toLowerCase().includes(lower) ||
            (o.ship_name || "").toLowerCase().includes(lower)
        );
    }, [jobOrders, searchTerm]);

    // Handlers
    const handleOrderChange = (name, val) => {
        setOrderFormData(prev => ({ ...prev, [name]: val }));
        if (errors[name]) setErrors(prev => ({ ...prev, [name]: null }));
    };

    const handlePosChange = (name, val) => {
        setPosFormData(prev => ({ ...prev, [name]: val }));
        if (errors[name]) setErrors(prev => ({ ...prev, [name]: null }));
    };

    const handleCreateOrder = async (e) => {
        e.preventDefault();
        const validation = validateFormData(orderFormData, JOB_ORDER_FORM_FIELDS);
        if (Object.keys(validation).length > 0) {
            setErrors(validation);
            notify.error("Please fill in all required fields");
            return;
        }

        setIsSubmitting(true);
        const data = transformForSave(orderFormData, JOB_ORDER_FORM_FIELDS);
        data.company = company.id;

        const result = await createJobOrder(data);
        if (result.success) {
            const defaults = getDefaultValues(JOB_ORDER_FORM_FIELDS);
            setOrderFormData({ ...defaults, company: company.id });
            // Automatically select the new order to add positions
            setSelectedOrder(result.data);
        }
        setIsSubmitting(false);
    };

    const handleAddPosition = async (e) => {
        e.preventDefault();
        if (!selectedOrder) return;

        const validation = validateFormData(posFormData, JOB_POSITION_FORM_FIELDS);
        if (Object.keys(validation).length > 0) {
            setErrors(validation);
            return;
        }

        setIsSubmitting(true);
        const data = transformForSave(posFormData, JOB_POSITION_FORM_FIELDS);
        data.job_order = selectedOrder.id;

        const result = await addPositionToOrder(data);
        if (result.success) {
            setPosFormData(getDefaultValues(JOB_POSITION_FORM_FIELDS));
            // Refresh detail to get updated positions list
            fetchJobOrders({ company: company.id });
        }
        setIsSubmitting(false);
    };

    const handleDeleteOrder = async (id) => {
        if (!window.confirm("Delete this Job Order and all its positions?")) return;
        const result = await deleteJobOrder(id);
        if (result.success && selectedOrder?.id === id) {
            setSelectedOrder(null);
        }
    };

    const handleUpdateStatus = async (newStatus) => {
        if (!selectedOrder) return;
        
        // Optimistically update local state for faster UI
        const previousOrder = { ...selectedOrder };
        setSelectedOrder(prev => ({ ...prev, status: newStatus }));
        
        const result = await updateJobOrder(selectedOrder.id, { status: newStatus });
        if (!result.success) {
            // Revert if failed
            setSelectedOrder(previousOrder);
        } else {
            // Refresh main list
            fetchJobOrders({ company: company.id });
        }
    };

    const renderField = (field, currentData, onChange) => {
        const commonProps = {
            name: field.name,
            label: field.label,
            required: field.required,
            value: currentData[field.name],
            onChange: (val) => onChange(field.name, val),
            error: errors[field.name],
            placeholder: field.placeholder,
            variant: "dashboard",
            scale: scale
        };

        if (field.name === "rank") {
            return <Select {...commonProps} key={field.name} options={referenceOptions.ranks} />;
        }
        if (field.name === "ship") {
            const shipOptions = companyShips.map(s => ({ 
                value: s.id, 
                label: s.ship_name || s.name 
            }));
            return <Select {...commonProps} key={field.name} options={shipOptions} />;
        }
        if (field.component === "DateInput") {
            return <DateInput {...commonProps} key={field.name} />;
        }
        if (field.component === "Select" && field.options) {
            return <Select {...commonProps} key={field.name} options={field.options} />;
        }
        if (field.component === "TextArea") {
            return <TextArea {...commonProps} key={field.name} rows={3} />;
        }

        return <BaseInput {...commonProps} key={field.name} type={field.type} />;
    };

    if (!isOpen) return null;

    return (
        <div style={{ ...modalStyles.overlay, zIndex: 1100 }} onClick={onClose}>
            <div 
                style={{
                    ...modalStyles.panel,
                    maxWidth: `${Math.round(1000 * scale)}px`,
                    width: "100%",
                    display: "flex",
                    flexDirection: "column",
                    maxHeight: "90vh",
                    padding: 0,
                    overflow: "hidden"
                }} 
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div style={{ padding: `${Math.round(20 * scale)}px ${Math.round(24 * scale)}px`, borderBottom: "1px solid #E5E7EB", display: "flex", justifyContent: "space-between", alignItems: "center", backgroundColor: "#fff" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                        <div style={{ width: "48px", height: "48px", borderRadius: "12px", backgroundColor: "#0369A1", display: "flex", alignItems: "center", justifyContent: "center", color: "#fff" }}>
                            <FileText size={24} />
                        </div>
                        <div>
                            <h2 style={{ ...titleStyles, marginBottom: 0, fontSize: "20px" }}>Job Order Management</h2>
                            <p style={{ fontSize: "14px", color: "#6B7280", margin: "2px 0 0 0" }}>{company?.company_name}</p>
                        </div>
                    </div>
                    <button onClick={onClose} style={{ border: "none", background: "#F3F4F6", cursor: "pointer", color: "#6B7280", width: "36px", height: "36px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center" }}>
                        <X size={20} />
                    </button>
                </div>

                <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
                    {/* Left: Job Orders List */}
                    <div style={{ flex: 1, backgroundColor: "#F9FAFB", borderRight: "1px solid #E5E7EB", display: "flex", flexDirection: "column" }}>
                        <div style={{ padding: "16px", borderBottom: "1px solid #E5E7EB" }}>
                            <div style={{ position: "relative" }}>
                                <Search size={16} style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "#9CA3AF" }} />
                                <input 
                                    type="text" 
                                    placeholder="Search orders..." 
                                    value={searchTerm}
                                    onChange={e => setSearchTerm(e.target.value)}
                                    style={{ width: "100%", padding: "8px 8px 8px 36px", borderRadius: "8px", border: "1px solid #E5E7EB", fontSize: "13px" }}
                                />
                            </div>
                        </div>
                        
                        <div style={{ flex: 1, overflowY: "auto", padding: "12px" }}>
                            {jobOrders.length === 0 ? (
                                <div style={{ textAlign: "center", padding: "40px", color: "#6B7280" }}>
                                    <FileText size={32} style={{ margin: "0 auto 12px", opacity: 0.3 }} />
                                    <p style={{ fontSize: "13px" }}>No job orders found.</p>
                                </div>
                            ) : (
                                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                                    {filteredOrders.map(order => (
                                        <div 
                                            key={order.id}
                                            onClick={() => setSelectedOrder(order)}
                                            style={{
                                                padding: "14px",
                                                backgroundColor: selectedOrder?.id === order.id ? "#E0F2FE" : "white",
                                                borderRadius: "10px",
                                                border: `1px solid ${selectedOrder?.id === order.id ? "#0369A1" : "#E5E7EB"}`,
                                                cursor: "pointer",
                                                transition: "all 0.2s"
                                            }}
                                        >
                                            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                                                <span style={{ fontWeight: 700, fontSize: "14px", color: "#111827" }}>{order.reference_number}</span>
                                                <span style={{ fontSize: "11px", color: "#0369A1", backgroundColor: "#F0F9FF", padding: "2px 6px", borderRadius: "4px" }}>{order.status}</span>
                                            </div>
                                            <div style={{ fontSize: "12px", color: "#6B7280" }}>{order.ship_name || "No ship assigned"}</div>
                                            <div style={{ fontSize: "11px", color: "#9CA3AF", marginTop: "6px", display: "flex", justifyContent: "space-between" }}>
                                                <span>{order.positions?.length || 0} Positions</span>
                                                <div style={{ display: "flex", gap: "8px" }}>
                                                    <button onClick={(e) => { e.stopPropagation(); handleDeleteOrder(order.id); }} style={{ border: "none", background: "none", color: "#EF4444", cursor: "pointer", padding: "2px" }}><Trash2 size={14} /></button>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right: Dynamic Panel */}
                    <div style={{ flex: 1.5, backgroundColor: "#fff", display: "flex", flexDirection: "column", overflow: "hidden" }}>
                        {!selectedOrder ? (
                            /* Create New Order Form */
                            <div style={{ padding: "24px", overflowY: "auto" }}>
                                <div style={{ marginBottom: "20px" }}>
                                    <h3 style={{ fontSize: "16px", fontWeight: 700, margin: 0 }}>Create New Job Order</h3>
                                    <p style={{ fontSize: "13px", color: "#6B7280", marginTop: "4px" }}>Start a new recruitment request for this company.</p>
                                </div>
                                <form onSubmit={handleCreateOrder} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                                        {JOB_ORDER_FORM_FIELDS.slice(0, -1).map(field => {
                                            if (field.name === "company") return null; // Already context-aware
                                            return renderField(field, orderFormData, handleOrderChange);
                                        })}
                                    </div>
                                    {renderField(JOB_ORDER_FORM_FIELDS[JOB_ORDER_FORM_FIELDS.length - 1], orderFormData, handleOrderChange)}
                                    <div style={{ marginTop: "12px" }}>
                                        <Button type="submit" variant="primary" style={{ width: "100%" }} disabled={isSubmitting}>
                                            {isSubmitting ? <Loader2 className="animate-spin" /> : "Create Job Order"}
                                        </Button>
                                    </div>
                                </form>
                            </div>
                        ) : (
                            /* Manage Positions View */
                            <div style={{ display: "flex", flexDirection: "column", flex: 1, overflow: "hidden" }}>
                                <div style={{ padding: "20px", backgroundColor: "#F8FAFC", borderBottom: "1px solid #E5E7EB" }}>
                                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                                        <div>
                                            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                                                <h3 style={{ fontSize: "16px", fontWeight: 700, margin: 0 }}>Positions for {selectedOrder.reference_number}</h3>
                                                <select 
                                                    value={selectedOrder.status || "Pending"}
                                                    onChange={(e) => handleUpdateStatus(e.target.value)}
                                                    style={{ fontSize: "12px", padding: "2px 8px", borderRadius: "6px", border: "1px solid #E5E7EB", backgroundColor: "#fff", cursor: "pointer", color: "#0369A1", fontWeight: 600, outline: "none" }}
                                                >
                                                    <option value="Pending">Pending</option>
                                                    <option value="Open">Open</option>
                                                    <option value="Active">Active</option>
                                                    <option value="In Progress">In Progress</option>
                                                    <option value="Fulfilled">Fulfilled</option>
                                                    <option value="Cancelled">Cancelled</option>
                                                </select>
                                            </div>
                                            <p style={{ fontSize: "13px", color: "#6B7280", marginTop: "4px" }}>Add or remove ranks for this job order.</p>
                                        </div>
                                        <Button variant="outline" size="sm" onClick={() => setSelectedOrder(null)}>Back to New Order</Button>
                                    </div>
                                </div>

                                <div style={{ flex: 1, overflowY: "auto", padding: "20px" }}>
                                    {/* Add Position Form */}
                                    <div style={{ padding: "16px", backgroundColor: "#F9FAFB", borderRadius: "12px", border: "1px solid #E5E7EB", marginBottom: "24px" }}>
                                        <h4 style={{ fontSize: "14px", fontWeight: 600, marginBottom: "12px" }}>Add Position</h4>
                                        <form onSubmit={handleAddPosition}>
                                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                                                {/* Main fields in 2 columns */}
                                                {JOB_POSITION_FORM_FIELDS.filter(f => f.component !== "TextArea").map(field => renderField(field, posFormData, handlePosChange))}
                                            </div>
                                            {/* Remarks in full width */}
                                            <div style={{ marginTop: "12px" }}>
                                                {JOB_POSITION_FORM_FIELDS.filter(f => f.component === "TextArea").map(field => renderField(field, posFormData, handlePosChange))}
                                            </div>
                                            <div style={{ marginTop: "12px", display: "flex", justifyContent: "flex-end" }}>
                                                <Button type="submit" variant="primary" size="sm" disabled={isSubmitting}>
                                                    {isSubmitting ? <Loader2 size={16} className="animate-spin" /> : "Add Position"}
                                                </Button>
                                            </div>
                                        </form>
                                    </div>

                                    {/* Positions List */}
                                    <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                                        {selectedOrder.positions?.length === 0 ? (
                                            <p style={{ textAlign: "center", color: "#9CA3AF", fontSize: "13px", padding: "20px" }}>No positions added yet.</p>
                                        ) : (
                                            selectedOrder.positions.map(pos => (
                                                <div key={pos.id} style={{ padding: "14px", border: "1px solid #F1F5F9", borderRadius: "10px", display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                                                    <div style={{ flex: 1 }}>
                                                        <div style={{ fontWeight: 600, fontSize: "14px", display: "flex", alignItems: "center", gap: "8px" }}>
                                                            {pos.rank_name} 
                                                            <span style={{ fontWeight: 400, color: "#0369A1", backgroundColor: "#E0F2FE", padding: "1px 6px", borderRadius: "4px", fontSize: "11px" }}>x{pos.quantity}</span>
                                                        </div>
                                                        <div style={{ fontSize: "12px", color: "#6B7280", marginTop: "4px", display: "flex", gap: "12px" }}>
                                                            <span>💰 {pos.salary_min || '?'}-{pos.salary_max || '?'} {pos.currency}</span>
                                                            <span>📅 {pos.contract_duration_months} Months</span>
                                                        </div>
                                                        {pos.remarks && (
                                                            <div style={{ fontSize: "11px", color: "#9CA3AF", marginTop: "6px", fontStyle: "italic", borderTop: "1px dashed #F1F5F9", paddingTop: "4px" }}>
                                                                "{pos.remarks}"
                                                            </div>
                                                        )}
                                                    </div>
                                                    <button onClick={() => removePosition(pos.id, selectedOrder.id)} style={{ border: "none", background: "#FEF2F2", color: "#EF4444", cursor: "pointer", padding: "6px", borderRadius: "6px", display: "flex", alignItems: "center", justifyContent: "center" }} title="Remove Position"><Trash2 size={14} /></button>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <div style={{ padding: "16px 24px", borderTop: "1px solid #E5E7EB", display: "flex", justifyContent: "flex-end", backgroundColor: "#fff" }}>
                    <Button variant="outline" onClick={onClose}>Close Management</Button>
                </div>
            </div>
        </div>
    );
};

export default JobOrderManagementModal;
