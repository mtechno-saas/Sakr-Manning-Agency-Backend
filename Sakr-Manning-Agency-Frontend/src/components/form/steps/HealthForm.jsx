// components/forms/sections/HealthForm.jsx
import React, { useState } from "react";
import { useFormContext, useFieldArray } from "react-hook-form";
import { Plus } from "lucide-react";
import { HealthModal } from "../modals/HealthModal";
import { CrudTable } from "../layout/FormTable";
import { StepSaveButton } from "../layout/StepSaveButton";
import { BaseInput } from "../inputs/BaseInput";
import { TextDateInput } from "../inputs/DateInput";
import { FORM_FIELDS } from "../../../config/formConfig";

/**
 * HealthForm Component
 *
 * Features:
 * - International Medical at the top
 * - Yellow Fever, Cholera, COVID inline fields
 * - Modal-based CRUD for health/vaccination records (array)
 */
export function HealthForm() {
  const { control, setValue, getValues } = useFormContext();
  const { fields, append, update, remove } = useFieldArray({
    control,
    name: "health",
  });

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingHealth, setEditingHealth] = useState(null);
  const [editingIndex, setEditingIndex] = useState(null);
  const [noExpiryYellowFever, setNoExpiryYellowFever] = useState(false);
  const [noExpiryCholera, setNoExpiryCholera] = useState(false);
  const [noExpiryCovid, setNoExpiryCovid] = useState(false);

  const generateId = () => `health-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

  const handleAdd = () => {
    setEditingHealth(null);
    setIsModalOpen(true);
  };

  const handleEdit = (health) => {
    const index = fields.findIndex((f) => f.id === health.id);
    setEditingIndex(index);
    const realData = getValues(`health.${index}`);
    setEditingHealth({ ...health, _originalId: realData?.id || health.id });
    setIsModalOpen(true);
  };

  const handleSave = (healthData) => {
    if (editingIndex !== null) {
      update(editingIndex, { ...healthData, id: editingHealth._originalId });
    } else {
      append({ ...healthData, id: generateId() });
    }
  };

  const handleDelete = (id) => {
    if (!window.confirm("Are you sure you want to delete this health record?")) return;
    const index = fields.findIndex((f) => f.id === id);
    if (index !== -1) remove(index);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingHealth(null);
    setEditingIndex(null);
  };

  const columns = [
    { key: "name", label: "Vaccination" },
    { key: "number", label: "Number" },
    { key: "issue_date", label: "Issue Date" },
    { key: "expiry_date", label: "Expiry Date" },
    { key: "issued_by", label: "Issued By" },
    { key: "issued_at", label: "Issued At" },
    { key: "first_date", label: "First Dose" },
    { key: "last_date", label: "Last Dose" },
    { key: "remarks", label: "Remarks" },
  ];

  return (
    <div className="w-full space-y-6">
      <StepSaveButton />

      {/* Health Records — single card */}
      <div className="bg-white rounded-lg p-6">
        {/* International Medical */}
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          International Medical
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <BaseInput
            name={FORM_FIELDS.INTERNATIONAL_MEDICAL.NUMBER}
            placeholder="Certificate Number"
            variant="outlined"
          />
          <TextDateInput
            name={FORM_FIELDS.INTERNATIONAL_MEDICAL.ISSUE_DATE}
            placeholder="Issue Date"
            variant="outlined"
          />
          <TextDateInput
            name={FORM_FIELDS.INTERNATIONAL_MEDICAL.EXPIRY_DATE}
            placeholder="Expiry Date"
            variant="outlined"
            rules={{
              validate: (val) => {
                if (!val) return true;
                const issueDate = getValues(FORM_FIELDS.INTERNATIONAL_MEDICAL.ISSUE_DATE);
                if (issueDate && val <= issueDate) return "Expiry date must be after issue date";
                return true;
              }
            }}
          />
        </div>

        {/* Yellow Fever */}
        <h3 className="text-lg font-semibold text-gray-800 mt-8 mb-4">
          Yellow Fever
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <BaseInput
            name={FORM_FIELDS.YELLOW_FEVER.NUMBER}
            placeholder="Certificate Number"
            variant="outlined"
          />
          <TextDateInput
            name={FORM_FIELDS.YELLOW_FEVER.ISSUE_DATE}
            placeholder="Issue Date"
            variant="outlined"
          />
          {noExpiryYellowFever ? (
            <div className="flex items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50 text-gray-400 text-sm px-3 h-10 mt-auto">
              No Expiry
            </div>
          ) : (
            <TextDateInput
              name={FORM_FIELDS.YELLOW_FEVER.EXPIRY_DATE}
              placeholder="Expiry Date"
              variant="outlined"
              rules={{
                validate: (val) => {
                  if (!val || noExpiryYellowFever) return true;
                  const issueDate = getValues(FORM_FIELDS.YELLOW_FEVER.ISSUE_DATE);
                  if (issueDate && val <= issueDate) return "Expiry date must be after issue date";
                  return true;
                }
              }}
            />
          )}
        </div>
        <div className="flex items-center gap-2 mt-2">
          <input
            type="checkbox"
            id="yf-no-expiry"
            checked={noExpiryYellowFever}
            onChange={(e) => {
              setNoExpiryYellowFever(e.target.checked);
              if (e.target.checked) setValue(FORM_FIELDS.YELLOW_FEVER.EXPIRY_DATE, "");
            }}
            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <label htmlFor="yf-no-expiry" className="text-sm text-gray-600 select-none">
            No expiry date (unlimited)
          </label>
        </div>

        {/* Cholera */}
        <h3 className="text-lg font-semibold text-gray-800 mt-8 mb-4">
          Cholera
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <BaseInput
            name={FORM_FIELDS.CHOLERA.NUMBER}
            placeholder="Certificate Number"
            variant="outlined"
          />
          <TextDateInput
            name={FORM_FIELDS.CHOLERA.ISSUE_DATE}
            placeholder="Issue Date"
            variant="outlined"
          />
          {noExpiryCholera ? (
            <div className="flex items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50 text-gray-400 text-sm px-3 h-10 mt-auto">
              No Expiry
            </div>
          ) : (
            <TextDateInput
              name={FORM_FIELDS.CHOLERA.EXPIRY_DATE}
              placeholder="Expiry Date"
              variant="outlined"
              rules={{
                validate: (val) => {
                  if (!val || noExpiryCholera) return true;
                  const issueDate = getValues(FORM_FIELDS.CHOLERA.ISSUE_DATE);
                  if (issueDate && val <= issueDate) return "Expiry date must be after issue date";
                  return true;
                }
              }}
            />
          )}
        </div>
        <div className="flex items-center gap-2 mt-2">
          <input
            type="checkbox"
            id="cholera-no-expiry"
            checked={noExpiryCholera}
            onChange={(e) => {
              setNoExpiryCholera(e.target.checked);
              if (e.target.checked) setValue(FORM_FIELDS.CHOLERA.EXPIRY_DATE, "");
            }}
            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <label htmlFor="cholera-no-expiry" className="text-sm text-gray-600 select-none">
            No expiry date (unlimited)
          </label>
        </div>

        {/* COVID Vaccination */}
        <h3 className="text-lg font-semibold text-gray-800 mt-8 mb-4">
          COVID Vaccination
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <BaseInput
            name={FORM_FIELDS.COVID.VACCINE_NAME}
            placeholder="Vaccine Name"
            variant="outlined"
          />
          <TextDateInput
            name={FORM_FIELDS.COVID.FIRST_DOSE}
            placeholder="First Dose Date"
            variant="outlined"
          />
          {noExpiryCovid ? (
            <div className="flex items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50 text-gray-400 text-sm px-3 h-10">
              No Second Dose
            </div>
          ) : (
            <TextDateInput
              name={FORM_FIELDS.COVID.SECOND_DOSE}
              placeholder="Second Dose Date"
              variant="outlined"
              rules={{
                validate: (val) => {
                  if (!val || noExpiryCovid) return true;
                  const firstDate = getValues(FORM_FIELDS.COVID.FIRST_DOSE);
                  if (firstDate && val <= firstDate) return "Second dose must be after first dose";
                  return true;
                }
              }}
            />
          )}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-1 gap-6">
          <BaseInput
            name={FORM_FIELDS.COVID.OTHER_DOSES_OR_REMARKS}
            placeholder="Other Doses / Remarks"
            variant="outlined"
          />
        </div>
        <div className="flex items-center gap-2 mt-2">
          <input
            type="checkbox"
            id="covid-no-second"
            checked={noExpiryCovid}
            onChange={(e) => {
              setNoExpiryCovid(e.target.checked);
              if (e.target.checked) setValue(FORM_FIELDS.COVID.SECOND_DOSE, "");
            }}
            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <label htmlFor="covid-no-second" className="text-sm text-gray-600 select-none">
            No second dose
          </label>
        </div>
      </div>

      {/* ===== VACCINATION RECORDS CRUD TABLE ===== */}
      <div className="bg-[#E8F4FD] rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Health Certificate & Vaccination
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Add your health certificates and vaccination records
            </p>
          </div>
          <button
            type="button"
            onClick={handleAdd}
            className="flex items-center gap-2 px-5 py-2.5 bg-[#CFDBEC] text-gray-800 rounded-lg hover:bg-[#b8c9de] transition-colors font-medium shadow-sm"
          >
            <Plus className="w-5 h-5" />
            Add Health Record
          </button>
        </div>
      </div>

      {fields.length > 0 && (
        <CrudTable
          data={fields}
          columns={columns}
          onEdit={handleEdit}
          onDelete={handleDelete}
          emptyMessage="No health records added yet. Click 'Add Health Record' to get started."
        />
      )}

      <HealthModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSave={handleSave}
        initialData={editingHealth}
      />
    </div>
  );
}

