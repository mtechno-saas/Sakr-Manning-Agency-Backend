// components/dashboard/Components/Modal/GenerateContractModal.jsx
import React, { useState, useEffect, useMemo } from "react";
import Button from "../Common/Button";
import { getModalStyles } from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { DateInput } from "../inputs/DateInput";
import { useFormModal } from "../../hooks/useFormModal";
import { useDashboardData } from "../../context/DashboardDataContext";
import documentsApi from "../../../../services/Dashboard/documentsApi";
import { shipsApi } from "../../../../services/Dashboard/shipsApi";

/**
 * GenerateContractModal
 *
 * Flow:
 *  1. Pre-load the ship from submission.ship_details (or submission.ship).
 *  2. If the user has a ship, derive position options from that ship's job_orders[].positions.
 *  3. If the user has NO ship, show a ship selector first; on ship change, load full ship detail → positions.
 *  4. Admin must pick a position → sent as `job_position` in the contract payload.
 *  5. `ship_details` and `job_position_details` are available in CVSubmissionViewModal for read display.
 */
const GenerateContractModal = ({ submission, onClose, onSuccess, scale = 1 }) => {
  const modalStyles  = getModalStyles(scale);
  const titleStyles  = getModalTitleStyles(scale);

  const { fetchShipsByCompany } = useDashboardData();

  // ─── Ship state ────────────────────────────────────────────────────────────
  const [companyShips, setCompanyShips]   = useState([]); // ships list for selector
  const [loadingShips, setLoadingShips]   = useState(false);
  const [selectedShipId, setSelectedShipId] = useState(null);
  const [selectedShipData, setSelectedShipData] = useState(null); // full ship object
  const [loadingShipDetail, setLoadingShipDetail] = useState(false);

  // ─── Position state ────────────────────────────────────────────────────────
  const [selectedPositionId, setSelectedPositionId] = useState("");
  const [positionError, setPositionError] = useState("");

  // ─── Determine pre-assigned ship from submission ───────────────────────────
  const preAssignedShip = useMemo(() => {
    if (submission?.ship_details?.id) return submission.ship_details;
    if (typeof submission?.ship === "object" && submission.ship?.id) return submission.ship;
    return null;
  }, [submission]);

  const preAssignedShipId = useMemo(() => {
    if (preAssignedShip?.id) return preAssignedShip.id;
    if (typeof submission?.ship === "number") return submission.ship;
    return null;
  }, [preAssignedShip, submission]);

  // ─── Load company ships for selector (when no pre-assigned ship) ───────────
  useEffect(() => {
    if (preAssignedShipId) return; // no need — ship already known
    const companyId = typeof submission?.company === "object"
      ? submission.company?.id
      : submission?.company;
    if (!companyId) return;
    (async () => {
      setLoadingShips(true);
      try {
        const ships = await fetchShipsByCompany(companyId);
        setCompanyShips(ships);
      } catch (e) {
        console.error("Failed to load ships", e);
      } finally {
        setLoadingShips(false);
      }
    })();
  }, [submission, preAssignedShipId, fetchShipsByCompany]);

  // ─── Load full ship detail (to get job_orders.positions) ──────────────────
  useEffect(() => {
    const id = preAssignedShipId || selectedShipId;
    if (!id) return;
    if (preAssignedShip && preAssignedShip.job_orders) {
      // already have full data from submission
      setSelectedShipData(preAssignedShip);
      return;
    }
    (async () => {
      setLoadingShipDetail(true);
      try {
        const detail = await shipsApi.getShipById(id);
        setSelectedShipData(detail);
      } catch (e) {
        console.error("Failed to load ship detail", e);
      } finally {
        setLoadingShipDetail(false);
      }
    })();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [preAssignedShipId, selectedShipId]);

  // ─── Derive position options from job_orders ───────────────────────────────
  const positionOptions = useMemo(() => {
    if (!selectedShipData?.job_orders) return [];
    const opts = [];
    selectedShipData.job_orders.forEach(order => {
      (order.positions || []).forEach(pos => {
        const label = [
          pos.rank_name || `Rank #${pos.rank}`,
          `Qty: ${pos.quantity}`,
          pos.salary_min && pos.salary_max
            ? `${pos.salary_min}–${pos.salary_max} ${pos.currency || ""}`
            : "",
          pos.contract_duration_months ? `${pos.contract_duration_months}mo` : "",
        ].filter(Boolean).join(" · ");
        opts.push({ value: String(pos.id), label, _raw: pos });
      });
    });
    return opts;
  }, [selectedShipData]);

  // ─── Static fields config ──────────────────────────────────────────────────
  const staticFields = [
    { name: "sign_on_date",  label: "Sign-On Date",          type: "date",   component: "DateInput", required: true,  defaultValue: "", gridCols: 6 },
    { name: "sign_off_date", label: "Sign-Off Date (Optional)", type: "date", component: "DateInput", required: false, defaultValue: "", gridCols: 6 },
    { name: "status",        label: "Initial Status",         type: "select", component: "Select",    required: true,
      gridCols: 12,
      options: [
        { value: "Draft",              label: "Draft" },
        { value: "Pending Signature",  label: "Pending Signature" },
        { value: "Active",             label: "Active" },
      ],
      defaultValue: "Draft"
    },
    { name: "repatriation_terms", label: "Repatriation Terms", type: "text", component: "BaseInput", required: false, placeholder: "e.g., Company covers return flight...", defaultValue: "", gridCols: 6 },
    { name: "leave_pay_terms",    label: "Leave Pay Terms",    type: "text", component: "BaseInput", required: false, placeholder: "e.g., 30 days paid leave...",          defaultValue: "", gridCols: 6 },
  ];

  // ─── handleCreate ──────────────────────────────────────────────────────────
  const handleCreate = async (data) => {
    if (!selectedPositionId) {
      setPositionError("Please select a job position.");
      throw new Error("Position required");
    }
    const shipId = preAssignedShipId || selectedShipId;
    if (!shipId) {
      setPositionError("Please select a ship first.");
      throw new Error("Ship required");
    }
    const payload = {
      cv_submission_id:  submission.id,
      ship:              parseInt(shipId),
      job_position:      parseInt(selectedPositionId),
      sign_on_date:      data.sign_on_date,
      status:            data.status || "Draft",
      sign_off_date:     data.sign_off_date || undefined,
      repatriation_terms: data.repatriation_terms || undefined,
      leave_pay_terms:   data.leave_pay_terms || undefined,
    };
    const result = await documentsApi.createContract(payload);
    if (onSuccess) onSuccess(result);
    return { success: true };
  };

  const { formData, errors, loading, handleChange, handleSave, handleClose } = useFormModal({
    fieldConfig: staticFields,
    record: null,
    onSave: handleCreate,
    onClose,
    successMessage: () => "Contract generated successfully!",
  });

  // ─── Render helpers ────────────────────────────────────────────────────────
  const renderField = (field) => {
    const props = {
      key: field.name, name: field.name, label: field.label,
      required: field.required, value: formData[field.name],
      onChange: (val) => handleChange(field.name, val),
      error: errors[field.name], placeholder: field.placeholder,
      variant: "dashboard",
    };
    if (field.component === "Select")    return <Select    {...props} options={field.options} />;
    if (field.component === "DateInput") return <DateInput {...props} />;
    return <BaseInput {...props} type={field.type} />;
  };

  const shipId = preAssignedShipId || selectedShipId;
  const noShipYet = !shipId;

  return (
    <div style={modalStyles.overlay} onClick={handleClose}>
      <div
        style={{ ...modalStyles.panel, maxWidth: `${Math.round(800 * scale)}px` }}
        onClick={e => e.stopPropagation()}
      >
        <h2 style={{ ...titleStyles, marginBottom: `${Math.round(4 * scale)}px` }}>Generate Contract</h2>
        <p style={{ fontSize: `${Math.round(14 * scale)}px`, color: "#6B7280", marginBottom: `${Math.round(20 * scale)}px` }}>
          Generating contract for <strong>{submission.user_name || "Applicant"}</strong>
          {submission.position_name ? ` — ${submission.position_name}` : ""}.
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(12, 1fr)",
            gap: `${Math.round(16 * scale)}px`,
          }}
        >
          {/* ── Ship selector (only when no pre-assigned ship) ── */}
          {!preAssignedShipId && (
            <div style={{ gridColumn: "span 12" }}>
              <Select
                name="ship"
                label="Ship Assignment"
                required
                value={selectedShipId ? String(selectedShipId) : ""}
                onChange={(val) => {
                  setSelectedShipId(val ? parseInt(val) : null);
                  setSelectedShipData(null);
                  setSelectedPositionId("");
                  setPositionError("");
                }}
                options={companyShips.map(s => ({
                  value: String(s.id),
                  label: `${s.ship_name}${s.imo_number ? ` (${s.imo_number})` : ""}`,
                }))}
                disabled={loadingShips}
                placeholder={loadingShips ? "Loading ships…" : "Select Ship"}
                variant="dashboard"
              />
              {!loadingShips && companyShips.length === 0 && (
                <span style={{ fontSize: "12px", color: "#EF4444", marginTop: "4px", display: "block" }}>
                  No ships found for this company.
                </span>
              )}
            </div>
          )}

          {/* ── Pre-assigned ship info badge ── */}
          {preAssignedShipId && (
            <div
              style={{
                gridColumn: "span 12",
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: `${Math.round(10 * scale)}px ${Math.round(14 * scale)}px`,
                background: "#EFF6FF",
                border: "1px solid #BFDBFE",
                borderRadius: Math.round(8 * scale),
                fontSize: Math.round(13 * scale),
              }}
            >
              <span style={{ fontWeight: 600, color: "#1D4ED8" }}>Ship:</span>
              <span style={{ color: "#1E40AF" }}>
                {preAssignedShip?.ship_name || `Ship #${preAssignedShipId}`}
                {preAssignedShip?.imo_number ? ` (${preAssignedShip.imo_number})` : ""}
              </span>
            </div>
          )}

          {/* ── Position selector (shown once we have a ship) ── */}
          {!noShipYet && (
            <div style={{ gridColumn: "span 12" }}>
              <Select
                name="job_position"
                label="Job Position"
                required
                value={selectedPositionId}
                onChange={(val) => {
                  setSelectedPositionId(val || "");
                  setPositionError("");
                }}
                options={positionOptions}
                disabled={loadingShipDetail || positionOptions.length === 0}
                placeholder={
                  loadingShipDetail
                    ? "Loading positions…"
                    : positionOptions.length === 0
                      ? "No positions available on this ship's job orders"
                      : "Select a position"
                }
                variant="dashboard"
                error={positionError}
              />
              {!loadingShipDetail && positionOptions.length === 0 && (
                <span style={{ fontSize: "12px", color: "#F59E0B", marginTop: "4px", display: "block" }}>
                  This ship has no open job order positions.
                </span>
              )}
            </div>
          )}

          {/* ── Rest of contract fields ── */}
          {staticFields.map((field) => (
            <div
              key={field.name}
              style={{
                gridColumn: `span ${field.gridCols || 12}`,
              }}
            >
              {renderField(field)}
            </div>
          ))}
        </div>

        <div
          style={{
            display: "flex",
            gap: "12px",
            justifyContent: "flex-end",
            marginTop: "24px",
            paddingTop: "16px",
            borderTop: "1px solid #E5E7EB",
          }}
        >
          <Button variant="outline" onClick={handleClose} disabled={loading} scale={scale}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSave}
            disabled={loading || noShipYet}
            loading={loading}
            scale={scale}
          >
            Generate
          </Button>
        </div>
      </div>
    </div>
  );
};

export default GenerateContractModal;
