// components/forms/sections/LicensesForm.jsx
import React, { useState } from "react";
import { useFormContext, useFieldArray } from "react-hook-form";
import { Plus } from "lucide-react";
import { LicenseModal } from "../modals/LicenseModal";
import { CrudTable } from "../layout/FormTable";

/**
 * LicensesForm Component
 * 
 * Backend: /api/my-licenses/
 * 
 * Features:
 * - Modal-based add/edit
 * - Clean table display
 * - STCW regulation license options
 */
export function LicensesForm() {
    const { control, getValues } = useFormContext();
    const { fields, append, update, remove } = useFieldArray({
        control,
        name: "licenses",
    });

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingLicense, setEditingLicense] = useState(null);
    const [editingIndex, setEditingIndex] = useState(null);

    // Generate unique ID for new licenses
    const generateId = () => `lic-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

    /**
     * Handle opening modal for adding new license
     */
    const handleAdd = () => {
        setEditingLicense(null);
        setIsModalOpen(true);
    };

    /**
     * Handle opening modal for editing existing license
     */
    const handleEdit = (license) => {
        const index = fields.findIndex((f) => f.id === license.id);
        setEditingIndex(index);
        const realData = getValues(`licenses.${index}`);
        setEditingLicense({ ...license, _originalId: realData?.id || license.id });
        setIsModalOpen(true);
    };

    /**
     * Handle saving license (both add and edit)
     */
    const handleSave = (licenseData) => {
        if (editingIndex !== null) {
            // Editing existing license
            update(editingIndex, {
                ...licenseData,
                id: editingLicense._originalId,
            });
        } else {
            // Adding new license
            append({
                ...licenseData,
                id: generateId(),
            });
        }
    };

    /**
     * Handle deleting license with confirmation
     */
    const handleDelete = (id) => {
        if (!window.confirm("Are you sure you want to delete this license?")) {
            return;
        }

        const index = fields.findIndex((f) => f.id === id);
        if (index !== -1) {
            remove(index);
        }
    };

    /**
     * Handle closing modal
     */
    const handleCloseModal = () => {
        setIsModalOpen(false);
        setEditingLicense(null);
        setEditingIndex(null);
    };

    // Table columns configuration - matching backend field names
    const columns = [
        { key: "document_name", label: "License Name" },
        { key: "document_number", label: "License Number" },
        { key: "country_of_issue", label: "Country" },
        { key: "issue_date", label: "Issue Date" },
        { key: "expiry_date", label: "Expiry Date" },
    ];

    return (
        <div className="w-full space-y-6">
            {/* Header Section with Add Button */}
            <div className="bg-[#E8F4FD] rounded-lg p-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-semibold text-gray-900">
                            STCW Licenses
                        </h2>
                        <p className="text-sm text-gray-600 mt-1">
                            Add your STCW professional licenses and endorsements
                        </p>
                    </div>
                    <button
                        type="button"
                        onClick={handleAdd}
                        className="flex items-center gap-2 px-5 py-2.5 bg-[#CFDBEC] text-gray-800 rounded-lg hover:bg-[#b8c9de] transition-colors font-medium shadow-sm"
                    >
                        <Plus size={18} />
                        Add License
                    </button>
                </div>
            </div>

            {/* Table Section */}
            <CrudTable
                columns={columns}
                data={fields}
                onEdit={handleEdit}
                onDelete={handleDelete}
                emptyMessage="No licenses added yet"
            />

            {/* License Modal */}
            <LicenseModal
                isOpen={isModalOpen}
                onClose={handleCloseModal}
                onSave={handleSave}
                initialData={editingLicense}
            />
        </div>
    );
}
