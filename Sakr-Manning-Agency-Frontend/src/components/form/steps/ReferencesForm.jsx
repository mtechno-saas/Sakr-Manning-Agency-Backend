// components/forms/steps/ReferencesForm.jsx
import React, { useState } from "react";
import { useFormContext, useFieldArray } from "react-hook-form";
import { Plus } from "lucide-react";
import { ReferenceModal } from "../modals/ReferenceModal";
import { CrudTable } from "../layout/FormTable";
import { StepSaveButton } from "../layout/StepSaveButton";

/**
 * ReferencesForm Component - Step 10
 * 
 * Manages professional references from previous employers or supervisors.
 * 
 * Features:
 * - Modal-based add/edit
 * - Table display with all reference details
 * - CRUD operations via field array
 */
export function ReferencesForm() {
    const { control, getValues } = useFormContext();
    const { fields, append, update, remove } = useFieldArray({
        control,
        name: "references",
    });

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingReference, setEditingReference] = useState(null);
    const [editingIndex, setEditingIndex] = useState(null);

    // Generate unique ID for new references
    const generateId = () => `ref-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

    const handleAdd = () => {
        setEditingReference(null);
        setIsModalOpen(true);
    };

    const handleEdit = (reference) => {
        const index = fields.findIndex((f) => f.id === reference.id);
        setEditingIndex(index);
        const realData = getValues(`references.${index}`);
        setEditingReference({ ...reference, _originalId: realData?.id || reference.id });
        setIsModalOpen(true);
    };

    const handleSave = (referenceData) => {
        if (editingIndex !== null) {
            // Update existing reference
            update(editingIndex, {
                ...referenceData,
                id: editingReference._originalId,
            });
        } else {
            // Add new reference
            append({
                ...referenceData,
                id: generateId(),
            });
        }
    };

    const handleDelete = (id) => {
        if (!window.confirm("Are you sure you want to delete this reference?")) {
            return;
        }
        const index = fields.findIndex((f) => f.id === id);
        if (index !== -1) {
            remove(index);
        }
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setEditingReference(null);
        setEditingIndex(null);
    };

    // Table columns definition
    const columns = [
        { key: "name", label: "Name" },
        { key: "company_name", label: "Company" },
        { key: "position", label: "Position" },
        { key: "email", label: "Email" },
        { key: "tel", label: "Telephone" },
    ];

    return (
        <div className="w-full space-y-6">
            <StepSaveButton />

            {/* Header Section */}
            <div className="bg-[#E8F4FD] rounded-lg p-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-semibold text-gray-900">
                            References
                        </h2>
                        <p className="text-sm text-gray-600 mt-1">
                            Add professional references from previous employers or supervisors
                        </p>
                    </div>
                    <button
                        type="button"
                        onClick={handleAdd}
                        className="flex items-center gap-2 px-5 py-2.5 bg-[#CFDBEC] text-gray-800 rounded-lg hover:bg-[#b8c9de] transition-colors font-medium shadow-sm"
                    >
                        <Plus className="w-5 h-5" />
                        Add Reference
                    </button>
                </div>
            </div>

            {/* References Table */}
            {fields.length > 0 && (
                <CrudTable
                    data={fields}
                    columns={columns}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                    showAttachment={false}
                    emptyMessage="No references added yet. Click 'Add Reference' to get started."
                />
            )}

            {/* Empty State
            {fields.length === 0 && (
                <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                    <p className="text-gray-500 text-lg">
                        No references added yet. Click "Add Reference" to get started.
                    </p>
                </div>
            )} */}

            {/* Reference Modal */}
            <ReferenceModal
                isOpen={isModalOpen}
                onClose={handleCloseModal}
                onSave={handleSave}
                initialData={editingReference}
            />
        </div>
    );
}
