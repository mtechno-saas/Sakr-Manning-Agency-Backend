// components/Features/InterviewModal.jsx
// Modal for adding and editing interview appointments
// Used with InterviewCalendar component

import React, { useState, useEffect, useRef } from "react";
import Button from "../Common/Button";
import {
  getModalStyles,
  getFormFieldStyles,
} from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";
import { getScaledValue } from "../../Styles/globalStyles";
/**
 * InterviewModal Component
 *
 * Modal for creating or editing interview appointments
 * Handles date, time, candidate info, interview type, and status
 *
 * @param {boolean} isOpen - Modal visibility
 * @param {string} mode - 'add' or 'edit'
 * @param {object} interview - Interview data (for edit mode)
 * @param {function} onClose - Close callback
 * @param {function} onSave - Save callback with updated interview data
 * @param {number} scale - Scale factor
 * @param {string} preSelectedDate - Pre-selected date (YYYY-MM-DD format)
 *
 * @example
 * // Add mode
 * <InterviewModal
 *   isOpen={showAddModal}
 *   mode="add"
 *   onClose={() => setShowAddModal(false)}
 *   onSave={handleAddInterview}
 *   scale={scale}
 *   preSelectedDate="2025-02-10"
 * />
 *
 * // Edit mode
 * <InterviewModal
 *   isOpen={showEditModal}
 *   mode="edit"
 *   interview={selectedInterview}
 *   onClose={() => setShowEditModal(false)}
 *   onSave={handleEditInterview}
 *   scale={scale}
 * />
 */
const InterviewModal = ({
  isOpen,
  mode = "add",
  interview = null,
  onClose,
  onSave,
  scale = 1,
  preSelectedDate = null,
}) => {
  // Form state
  const [formData, setFormData] = useState({
    date: "",
    time: "",
    candidateName: "",
    position: "",
    company: "",
    type: "video",
    status: "scheduled",
    notes: "",
  });

  const [errors, setErrors] = useState({});
  const firstFieldRef = useRef(null);
  const modalStyles = getModalStyles(scale);
  const formFieldStyles = getFormFieldStyles(scale);
  const titleStyles = getModalTitleStyles(scale);

  // Initialize form data
  useEffect(() => {
    if (isOpen) {
      if (mode === "edit" && interview) {
        setFormData(interview);
      } else if (mode === "add") {
        setFormData({
          date: preSelectedDate || new Date().toISOString().split("T")[0],
          time: "10:00 AM",
          candidateName: "",
          position: "",
          company: "",
          type: "video",
          status: "scheduled",
          notes: "",
        });
      }
      setErrors({});

      // Focus first field
      if (firstFieldRef.current) {
        setTimeout(() => firstFieldRef.current.focus(), 100);
      }

      // Handle Escape key
      const handleKeyDown = (e) => {
        if (e.key === "Escape") onClose();
      };
      document.addEventListener("keydown", handleKeyDown);
      return () => document.removeEventListener("keydown", handleKeyDown);
    }
  }, [isOpen, mode, interview, preSelectedDate, onClose]);

  // Validate form
  const validateForm = () => {
    const newErrors = {};

    if (!formData.date) newErrors.date = "Date is required";
    if (!formData.time) newErrors.time = "Time is required";
    if (!formData.candidateName.trim())
      newErrors.candidateName = "Candidate name is required";
    if (!formData.position.trim()) newErrors.position = "Position is required";
    if (!formData.company.trim()) newErrors.company = "Company is required";

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle input change
  const handleChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  // Handle save
  const handleSaveClick = () => {
    if (validateForm()) {
      onSave(formData);
    }
  };

  if (!isOpen) return null;

  const padding = getScaledValue(24, scale);
  const gap = getScaledValue(16, scale);
  const inputPadding = getScaledValue(10, scale);

  return (
    <div
      style={modalStyles.overlay}
      role="dialog"
      aria-modal="true"
      onClick={onClose}
    >
      <div
        style={{
          ...modalStyles.panel,
          maxWidth: `${getScaledValue(500, scale)}px`,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Title */}
        <h2 style={titleStyles}>
          {mode === "add" ? "Schedule New Interview" : "Edit Interview"}
        </h2>

        {/* Form Fields */}
        <div style={{ display: "flex", flexDirection: "column", gap }}>
          {/* Date Field */}
          <div>
            <label style={formFieldStyles.label}>Date *</label>
            <input
              ref={firstFieldRef}
              type="date"
              value={formData.date}
              onChange={(e) => handleChange("date", e.target.value)}
              style={{
                ...formFieldStyles.input,
                borderColor: errors.date ? "#B21101" : undefined,
              }}
            />
            {errors.date && (
              <div style={{ ...formFieldStyles.error, marginTop: "4px" }}>
                {errors.date}
              </div>
            )}
          </div>

          {/* Time Field */}
          <div>
            <label style={formFieldStyles.label}>Time *</label>
            <input
              type="time"
              value={formData.time}
              onChange={(e) => handleChange("time", e.target.value)}
              style={{
                ...formFieldStyles.input,
                borderColor: errors.time ? "#B21101" : undefined,
              }}
            />
            {errors.time && (
              <div style={{ ...formFieldStyles.error, marginTop: "4px" }}>
                {errors.time}
              </div>
            )}
          </div>

          {/* Candidate Name Field */}
          <div>
            <label style={formFieldStyles.label}>Candidate Name *</label>
            <input
              type="text"
              placeholder="John Smith"
              value={formData.candidateName}
              onChange={(e) => handleChange("candidateName", e.target.value)}
              style={{
                ...formFieldStyles.input,
                borderColor: errors.candidateName ? "#B21101" : undefined,
              }}
            />
            {errors.candidateName && (
              <div style={{ ...formFieldStyles.error, marginTop: "4px" }}>
                {errors.candidateName}
              </div>
            )}
          </div>

          {/* Position Field */}
          <div>
            <label style={formFieldStyles.label}>Position *</label>
            <input
              type="text"
              placeholder="Chief Engineer"
              value={formData.position}
              onChange={(e) => handleChange("position", e.target.value)}
              style={{
                ...formFieldStyles.input,
                borderColor: errors.position ? "#B21101" : undefined,
              }}
            />
            {errors.position && (
              <div style={{ ...formFieldStyles.error, marginTop: "4px" }}>
                {errors.position}
              </div>
            )}
          </div>

          {/* Company Field */}
          <div>
            <label style={formFieldStyles.label}>Company *</label>
            <input
              type="text"
              placeholder="ABC Corporation"
              value={formData.company}
              onChange={(e) => handleChange("company", e.target.value)}
              style={{
                ...formFieldStyles.input,
                borderColor: errors.company ? "#B21101" : undefined,
              }}
            />
            {errors.company && (
              <div style={{ ...formFieldStyles.error, marginTop: "4px" }}>
                {errors.company}
              </div>
            )}
          </div>

          {/* Interview Type */}
          <div>
            <label style={formFieldStyles.label}>Interview Type</label>
            <select
              value={formData.type}
              onChange={(e) => handleChange("type", e.target.value)}
              style={formFieldStyles.input}
            >
              <option value="video">Video Call</option>
              <option value="phone">Phone Call</option>
              <option value="in-person">In-Person</option>
            </select>
          </div>

          {/* Status */}
          <div>
            <label style={formFieldStyles.label}>Status</label>
            <select
              value={formData.status}
              onChange={(e) => handleChange("status", e.target.value)}
              style={formFieldStyles.input}
            >
              <option value="scheduled">Scheduled</option>
              <option value="confirmed">Confirmed</option>
              <option value="pending">Pending</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          {/* Notes */}
          <div>
            <label style={formFieldStyles.label}>Notes (Optional)</label>
            <textarea
              placeholder="Add any notes..."
              value={formData.notes}
              onChange={(e) => handleChange("notes", e.target.value)}
              style={{
                ...formFieldStyles.input,
                minHeight: `${getScaledValue(100, scale)}px`,
                fontFamily: "Inter, sans-serif",
                resize: "vertical",
              }}
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div
          style={{
            display: "flex",
            gap: `${getScaledValue(12, scale)}px`,
            justifyContent: "flex-end",
            marginTop: `${getScaledValue(24, scale)}px`,
          }}
        >
          <Button variant="outline" onClick={onClose} scale={scale}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSaveClick} scale={scale}>
            {mode === "add" ? "Schedule" : "Update"}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default InterviewModal;
