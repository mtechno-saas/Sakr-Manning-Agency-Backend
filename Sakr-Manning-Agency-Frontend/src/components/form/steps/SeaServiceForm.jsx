// components/forms/sections/SeaServiceForm.jsx
import React, { useState } from "react";
import { useFormContext, useFieldArray } from "react-hook-form";
import { Plus } from "lucide-react";
import { SeaServiceModal } from "../modals/SeaServiceModal";
import { WorkExperienceModal } from "../modals/WorkExperienceModal";
import { CrudTable } from "../layout/FormTable";
import { StepSaveButton } from "../layout/StepSaveButton";
import { useReferenceDataContext } from "../../../context/ReferenceDataContext";

/**
 * SeaServiceForm Component - Refactored
 * 
 * Features:
 * - Modal-based add/edit for both sea service and work experience
 * - Clean table display
 * - Better UX with proper feedback
 */
export function SeaServiceForm() {
  const contextData = useReferenceDataContext();
  // Use the already-transformed context data (same as PositionPersonalForm)
  const referenceData = contextData || {};
  const { control, getValues } = useFormContext();

  /* ---------------- Sea Service handlers ---------------- */
  const {
    fields: seaFields,
    append: appendSea,
    update: updateSea,
    remove: removeSea,
  } = useFieldArray({
    control,
    name: "sea_services",
  });

  const {
    fields: workFields,
    append: appendWork,
    update: updateWork,
    remove: removeWork,
  } = useFieldArray({
    control,
    name: "work_experiences",
  });

  const [isSeaModalOpen, setIsSeaModalOpen] = useState(false);
  const [editingSeaService, setEditingSeaService] = useState(null);
  const [editingSeaIndex, setEditingSeaIndex] = useState(null);

  const [isWorkModalOpen, setIsWorkModalOpen] = useState(false);
  const [editingWorkExperience, setEditingWorkExperience] = useState(null);
  const [editingWorkIndex, setEditingWorkIndex] = useState(null);

  const generateId = (prefix = "item") =>
    `${prefix}-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

  /* ---------------- Sea Service handlers ---------------- */
  const handleAddSea = () => {
    setEditingSeaService(null);
    setIsSeaModalOpen(true);
  };

  const handleEditSea = (sea) => {
    const index = seaFields.findIndex((f) => f.id === sea.id);
    setEditingSeaIndex(index);
    const realData = getValues(`sea_services.${index}`);
    setEditingSeaService({ ...sea, _originalId: realData?.id || sea.id });
    setIsSeaModalOpen(true);
  };

  const handleSaveSea = (seaData) => {
    if (editingSeaIndex !== null) {
      updateSea(editingSeaIndex, {
        ...seaData,
        id: editingSeaService._originalId,
      });
    } else {
      appendSea({
        ...seaData,
        id: generateId("sea"),
      });
    }
  };

  const handleDeleteSea = (id) => {
    if (!window.confirm("Are you sure you want to delete this sea service?")) {
      return;
    }
    const idx = seaFields.findIndex((f) => f.id === id);
    if (idx !== -1) removeSea(idx);
  };

  const handleCloseSeaModal = () => {
    setIsSeaModalOpen(false);
    setEditingSeaService(null);
    setEditingSeaIndex(null);
  };

  /* ---------------- Work Experience handlers ---------------- */
  const handleAddWork = () => {
    setEditingWorkExperience(null);
    setIsWorkModalOpen(true);
  };

  const handleEditWork = (work) => {
    const index = workFields.findIndex((f) => f.id === work.id);
    setEditingWorkIndex(index);
    const realData = getValues(`work_experiences.${index}`);
    setEditingWorkExperience({ ...work, _originalId: realData?.id || work.id });
    setIsWorkModalOpen(true);
  };

  const handleSaveWork = (workData) => {
    if (editingWorkIndex !== null) {
      updateWork(editingWorkIndex, {
        ...workData,
        id: editingWorkExperience._originalId,
      });
    } else {
      appendWork({
        ...workData,
        id: generateId("work"),
      });
    }
  };

  const handleDeleteWork = (id) => {
    if (!window.confirm("Are you sure you want to delete this work experience?")) {
      return;
    }
    const idx = workFields.findIndex((f) => f.id === id);
    if (idx !== -1) removeWork(idx);
  };

  const handleCloseWorkModal = () => {
    setIsWorkModalOpen(false);
    setEditingWorkExperience(null);
    setEditingWorkIndex(null);
  };

  // Helper to resolve ID to label for table display
  const resolveLabel = (type, val) => {
    if (!val) return "";
    const items = referenceData?.[type] || [];
    const found = items.find((item) => String(item.value) === String(val));
    return found ? found.label : (val || "");
  };

  // Sea Service table columns - using snake_case to match backend/modal data
  const seaColumns = [
    { key: "company_name", label: "Company" },
    { key: "rank", label: "Rank", render: (val) => resolveLabel("positions", val) },
    { key: "vessel_name", label: "Vessel Name" },
    { key: "imo_number", label: "IMO Number" },
    { key: "signed_on", label: "Signed On" },
    { key: "signed_off", label: "Signed Off" },
    { key: "period", label: "Period", render: (val) => val || "" },
    { key: "flag", label: "Flag", render: (val) => resolveLabel("flags", val) },
    { key: "vessel_type", label: "Vessel Type", render: (val) => resolveLabel("vesselTypes", val) },
    { key: "dwt", label: "D.W.T" },
    { key: "grt", label: "G.R.T" },
    { key: "engine_type", label: "Engine Type" },
    { key: "bh", label: "B.H." },
    { key: "kw", label: "K.W." },
    { key: "reason_for_sign_off", label: "Reason for Sign Off" },
  ];

  // Work Experience table columns
  const workColumns = [
    { key: "experience", label: "Experience" },
  ];

  return (
    <div className="w-full space-y-6">
      <StepSaveButton />
      {/* Sea Service Section */}
      <div className="bg-[#E8F4FD] rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Complete Sea-Service Details
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Add your sea service records and vessel experience
            </p>
          </div>
          <button
            type="button"
            onClick={handleAddSea}
            className="flex items-center gap-2 px-5 py-2.5 bg-[#CFDBEC] text-gray-800 rounded-lg hover:bg-[#b8c9de] transition-colors font-medium shadow-sm"
          >
            <Plus className="w-5 h-5" />
            Add Sea Service
          </button>
        </div>
      </div>

      {/* Sea Service Table */}
      {seaFields.length > 0 && (
        <CrudTable
          data={seaFields}
          columns={seaColumns}
          onEdit={handleEditSea}
          onDelete={handleDeleteSea}
          emptyMessage="No sea service entries yet. Click 'Add Sea Service' to get started."
        />
      )}

      {/* Work Experience Section */}
      {/*
      <div className="bg-[#E8F4FD] rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Work Experience
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Add your other work experience
            </p>
          </div>
          <button
            type="button"
            onClick={handleAddWork}
            className="flex items-center gap-2 px-5 py-2.5 bg-[#CFDBEC] text-gray-800 rounded-lg hover:bg-[#b8c9de] transition-colors font-medium shadow-sm"
          >
            <Plus className="w-5 h-5" />
            Add Work Experience
          </button>
        </div>
      </div>
      */}
      {/* Work Experience Table */}
      {/*
      {workFields.length > 0 && (
        <CrudTable
          data={workFields}
          columns={workColumns}
          onEdit={handleEditWork}
          onDelete={handleDeleteWork}
          emptyMessage="No work experience entries yet. Click 'Add Work Experience' to get started."
        />
      )}
      */}

      {/* Sea Service Modal */}
      <SeaServiceModal
        isOpen={isSeaModalOpen}
        onClose={handleCloseSeaModal}
        onSave={handleSaveSea}
        initialData={editingSeaService}
        referenceData={referenceData}
      />

      {/* Work Experience Modal */}
      {/*
       <WorkExperienceModal
        isOpen={isWorkModalOpen}
        onClose={handleCloseWorkModal}
        onSave={handleSaveWork}
        initialData={editingWorkExperience}
      />
       */}
    </div>
  );
}