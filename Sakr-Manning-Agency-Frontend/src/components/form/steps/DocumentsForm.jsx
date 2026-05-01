// components/forms/sections/DocumentsForm.jsx
import React, { useState } from "react";
import { useFormContext, useFieldArray } from "react-hook-form";
import { Plus } from "lucide-react";
import { DocumentModal } from "../modals/DocumentModal";
import { CrudTable } from "../layout/FormTable";
import { StepSaveButton } from "../layout/StepSaveButton";
import { BaseInput } from "../inputs/BaseInput";
import { TextDateInput } from "../inputs/DateInput";
import { FORM_FIELDS } from "../../../config/formConfig";

/**
 * DocumentsForm Component
 *
 * Features:
 * - Passport Details inline fields (flat user fields)
 * - Seaman Book inline fields (flat user fields)
 * - Modal-based CRUD for travel documents (array)
 */
export function DocumentsForm() {
  const { control, getValues } = useFormContext();
  const { fields, append, update, remove } = useFieldArray({
    control,
    name: "documents",
  });

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingDocument, setEditingDocument] = useState(null);
  const [editingIndex, setEditingIndex] = useState(null);

  const generateId = () => `doc-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

  const handleAdd = () => {
    setEditingDocument(null);
    setIsModalOpen(true);
  };

  const handleEdit = (document) => {
    const index = fields.findIndex((f) => f.id === document.id);
    setEditingIndex(index);
    // Read the real stored data (with original backend/temp ID) from form values
    const realData = getValues(`documents.${index}`);
    setEditingDocument({ ...document, _originalId: realData?.id || document.id });
    setIsModalOpen(true);
  };

  const handleSave = (documentData) => {
    if (editingIndex !== null) {
      update(editingIndex, { ...documentData, id: editingDocument._originalId });
    } else {
      append({ ...documentData, id: generateId() });
    }
  };

  const handleDelete = (id) => {
    if (!window.confirm("Are you sure you want to delete this document?")) return;
    const index = fields.findIndex((f) => f.id === id);
    if (index !== -1) remove(index);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingDocument(null);
    setEditingIndex(null);
  };

  const columns = [
    { key: "document_type", label: "Document Type" },
    { key: "document_number", label: "Document No." },
    { key: "issue_date", label: "Issue Date" },
    { key: "expiry_date", label: "Expiry Date" },
    { key: "issuing_country", label: "Place of Issue" },
  ];

  return (
    <div className="w-full space-y-6">
      <StepSaveButton />

      {/* ===== PASSPORT DETAILS (flat user fields) ===== */}
      <div className="bg-white rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Passport Details
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <BaseInput
            name={FORM_FIELDS.PASSPORT.NUMBER}
            placeholder="Passport Number"
            variant="outlined"
          />
          <BaseInput
            name={FORM_FIELDS.PASSPORT.ISSUED_BY}
            placeholder="Issued By"
            variant="outlined"
          />
          <BaseInput
            name={FORM_FIELDS.PASSPORT.PLACE_OF_ISSUE}
            placeholder="Place of Issue"
            variant="outlined"
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <TextDateInput
            name={FORM_FIELDS.PASSPORT.ISSUE_DATE}
            placeholder="Issue Date"
            variant="outlined"
          />
          <TextDateInput
            name={FORM_FIELDS.PASSPORT.EXPIRY_DATE}
            placeholder="Expiry Date"
            variant="outlined"
            rules={{
              validate: (val) => {
                if (!val) return true;
                const issueDate = getValues(FORM_FIELDS.PASSPORT.ISSUE_DATE);
                if (issueDate && val <= issueDate) return "Expiry date must be after issue date";
                return true;
              }
            }}
          />
        </div>
      </div>

      {/* ===== SEAMAN BOOK (flat user fields) ===== */}
      <div className="bg-white rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Seaman Book
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <BaseInput
            name={FORM_FIELDS.SEAMAN_BOOK.NUMBER}
            placeholder="Seaman Book Number"
            variant="outlined"
          />
          <BaseInput
            name={FORM_FIELDS.SEAMAN_BOOK.ISSUED_BY}
            placeholder="Issued By"
            variant="outlined"
          />
          <BaseInput
            name={FORM_FIELDS.SEAMAN_BOOK.PLACE_OF_ISSUE}
            placeholder="Place of Issue"
            variant="outlined"
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <TextDateInput
            name={FORM_FIELDS.SEAMAN_BOOK.ISSUE_DATE}
            placeholder="Issue Date"
            variant="outlined"
          />
          <TextDateInput
            name={FORM_FIELDS.SEAMAN_BOOK.EXPIRY_DATE}
            placeholder="Expiry Date"
            variant="outlined"
            rules={{
              validate: (val) => {
                if (!val) return true;
                const issueDate = getValues(FORM_FIELDS.SEAMAN_BOOK.ISSUE_DATE);
                if (issueDate && val <= issueDate) return "Expiry date must be after issue date";
                return true;
              }
            }}
          />
        </div>
      </div>

      {/* ===== TRAVEL DOCUMENTS CRUD TABLE ===== */}
      <div className="bg-[#E8F4FD] rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Travel Documents
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Add your travel documents and identification
            </p>
          </div>
          <button
            type="button"
            onClick={handleAdd}
            className="flex items-center gap-2 px-5 py-2.5 bg-[#CFDBEC] text-gray-800 rounded-lg hover:bg-[#b8c9de] transition-colors font-medium shadow-sm"
          >
            <Plus className="w-5 h-5" />
            Add Travel Documents
          </button>
        </div>
      </div>

      {fields.length > 0 && (
        <CrudTable
          data={fields}
          columns={columns}
          onEdit={handleEdit}
          onDelete={handleDelete}
          emptyMessage="No travel documents added yet. Click 'Add Travel Documents' to get started."
        />
      )}

      <DocumentModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSave={handleSave}
        initialData={editingDocument}
      />
    </div>
  );
}