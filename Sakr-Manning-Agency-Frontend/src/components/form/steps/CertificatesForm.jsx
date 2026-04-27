// components/forms/sections/CertificatesForm.jsx
import React, { useState } from "react";
import { useFormContext, useFieldArray } from "react-hook-form";
import { Plus } from "lucide-react";
import { LicenseModal } from "../modals/LicenseModal";
import { CrudTable } from "../layout/FormTable";
import { StepSaveButton } from "../layout/StepSaveButton";
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { TextDateInput } from "../inputs/DateInput";
import { FORM_FIELDS, COC_OPTIONS } from "../../../config/formConfig";

/**
 * CertificatesForm Component
 *
 * Features:
 * - COC (Certificate of Competency) inline fields
 * - GOC (General Operator Certificate) inline fields
 * - CES Test inline fields
 * - CRUD table for professional licenses (array via /my-licenses/)
 */
export function CertificatesForm() {
  const { control, getValues } = useFormContext();
  const { fields, append, update, remove } = useFieldArray({
    control,
    name: "licenses",
  });

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingLicense, setEditingLicense] = useState(null);
  const [editingIndex, setEditingIndex] = useState(null);

  const generateId = () => `lic-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

  const handleAdd = () => {
    setEditingLicense(null);
    setIsModalOpen(true);
  };

  const handleEdit = (license) => {
    const index = fields.findIndex((f) => f.id === license.id);
    setEditingIndex(index);
    const realData = getValues(`licenses.${index}`);
    setEditingLicense({ ...license, _originalId: realData?.id || license.id });
    setIsModalOpen(true);
  };

  const handleSave = (licenseData) => {
    if (editingIndex !== null) {
      update(editingIndex, { ...licenseData, id: editingLicense._originalId });
    } else {
      append({ ...licenseData, id: generateId() });
    }
  };

  const handleDelete = (id) => {
    if (!window.confirm("Are you sure you want to delete this certificate/license?")) return;
    const index = fields.findIndex((f) => f.id === id);
    if (index !== -1) remove(index);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingLicense(null);
    setEditingIndex(null);
  };

  const columns = [
    { key: "document_name", label: "Certificate Name" },
    { key: "document_number", label: "Number" },
    { key: "issue_date", label: "Issued Date" },
    { key: "expiration_date", label: "Expiry Date" },
    { key: "country_of_issue", label: "Country" },
  ];

  return (
    <div className="w-full space-y-6">
      <StepSaveButton />

      {/* ===== COC - Certificate of Competency (flat user fields) ===== */}
      <div className="bg-white rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          COC — Certificate of Competency
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <Select
            name={FORM_FIELDS.COC.NAME}
            placeholder="Certificate Name"
            options={COC_OPTIONS}
            searchable
            variant="outlined"
          />
          <BaseInput
            name={FORM_FIELDS.COC.NUMBER}
            placeholder="Certificate Number"
            variant="outlined"
          />
          <BaseInput
            name={FORM_FIELDS.COC.ISSUED_BY}
            placeholder="Issued By"
            variant="outlined"
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <BaseInput
            name={FORM_FIELDS.COC.ISSUED_AT}
            placeholder="Issued At"
            variant="outlined"
          />
          <TextDateInput
            name={FORM_FIELDS.COC.ISSUE_DATE}
            placeholder="Issue Date"
            variant="outlined"
          />
          <TextDateInput
            name={FORM_FIELDS.COC.EXPIRY_DATE}
            placeholder="Expiry Date"
            variant="outlined"
            rules={{
              validate: (val) => {
                if (!val) return true;
                const issueDate = getValues(FORM_FIELDS.COC.ISSUE_DATE);
                if (issueDate && val <= issueDate) return "Expiry date must be after issue date";
                return true;
              },
            }}
          />
        </div>
      </div>

      {/* ===== GOC - General Operator Certificate (flat user fields) ===== */}
      <div className="bg-white rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          GOC — General Operator Certificate
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <BaseInput
            name={FORM_FIELDS.GOC.NUMBER}
            placeholder="Certificate Number"
            variant="outlined"
          />
          <BaseInput
            name={FORM_FIELDS.GOC.ISSUED_BY}
            placeholder="Issued By"
            variant="outlined"
          />
          <BaseInput
            name={FORM_FIELDS.GOC.ISSUED_AT}
            placeholder="Issued At"
            variant="outlined"
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <TextDateInput
            name={FORM_FIELDS.GOC.ISSUE_DATE}
            placeholder="Issue Date"
            variant="outlined"
          />
          <TextDateInput
            name={FORM_FIELDS.GOC.EXPIRY_DATE}
            placeholder="Expiry Date"
            variant="outlined"
            rules={{
              validate: (val) => {
                if (!val) return true;
                const issueDate = getValues(FORM_FIELDS.GOC.ISSUE_DATE);
                if (issueDate && val <= issueDate) return "Expiry date must be after issue date";
                return true;
              },
            }}
          />
        </div>
      </div>

      {/* ===== LICENSES CRUD TABLE ===== */}
      <div className="bg-[#E8F4FD] rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Professional Qualification / Certificate of Competency
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Add your professional certificates and qualifications
            </p>
          </div>
          <button
            type="button"
            onClick={handleAdd}
            className="flex items-center gap-2 px-5 py-2.5 bg-[#CFDBEC] text-gray-800 rounded-lg hover:bg-[#b8c9de] transition-colors font-medium shadow-sm"
          >
            <Plus className="w-5 h-5" />
            Add Certificate
          </button>
        </div>
      </div>

      {fields.length > 0 && (
        <CrudTable
          data={fields}
          columns={columns}
          onEdit={handleEdit}
          onDelete={handleDelete}
          emptyMessage="No certificates added yet. Click 'Add Certificate' to get started."
        />
      )}

      <LicenseModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSave={handleSave}
        initialData={editingLicense}
      />
    </div>
  );
}