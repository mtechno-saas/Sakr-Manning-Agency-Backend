// components/forms/sections/LanguagesForm.jsx
import React, { useState } from "react";
import { useFormContext, useFieldArray } from "react-hook-form";
import { Plus } from "lucide-react";
import { LanguageModal } from "../modals/LanguageModal";
import { CrudTable } from "../layout/FormTable";

/**
 * LanguagesForm Component
 * 
 * Backend: /api/users/user-languages/
 * 
 * Features:
 * - Modal-based add/edit
 * - CEFR level support
 * - Speaking, writing, reading scores
 */
export function LanguagesForm() {
    const { control, getValues } = useFormContext();
    const { fields, append, update, remove } = useFieldArray({
        control,
        name: "languages",
    });

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingLanguage, setEditingLanguage] = useState(null);
    const [editingIndex, setEditingIndex] = useState(null);

    // Generate unique ID for new languages
    const generateId = () => `lang-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

    /**
     * Handle opening modal for adding new language
     */
    const handleAdd = () => {
        setEditingLanguage(null);
        setIsModalOpen(true);
    };

    /**
     * Handle opening modal for editing existing language
     */
    const handleEdit = (language) => {
        const index = fields.findIndex((f) => f.id === language.id);
        setEditingIndex(index);
        const realData = getValues(`languages.${index}`);
        setEditingLanguage({ ...language, _originalId: realData?.id || language.id });
        setIsModalOpen(true);
    };

    /**
     * Handle saving language (both add and edit)
     */
    const handleSave = (languageData) => {
        if (editingIndex !== null) {
            // Editing existing language
            update(editingIndex, {
                ...languageData,
                id: editingLanguage._originalId,
            });
        } else {
            // Adding new language
            append({
                ...languageData,
                id: generateId(),
            });
        }
    };

    /**
     * Handle deleting language with confirmation
     */
    const handleDelete = (id) => {
        if (!window.confirm("Are you sure you want to delete this language?")) {
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
        setEditingLanguage(null);
        setEditingIndex(null);
    };

    // Table columns configuration - using snake_case to match backend/modal data
    const columns = [
        { key: "language", label: "Language" },
        { key: "cefr_level", label: "CEFR Level" },
        { key: "general_remarks", label: "General %" },
        { key: "speaking_level", label: "Speaking" },
        { key: "writing_level", label: "Writing" },
        { key: "reading_level", label: "Reading" },
        { key: "attachment", label: "Attachment" },
    ];

    return (
        <div className="w-full space-y-6">
            {/* Header Section with Add Button */}
            <div className="bg-[#E8F4FD] rounded-lg p-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-semibold text-gray-900">
                            Language Proficiency
                        </h2>
                        <p className="text-sm text-gray-600 mt-1">
                            Add your language skills with CEFR levels
                        </p>
                    </div>
                    <button
                        type="button"
                        onClick={handleAdd}
                        className="flex items-center gap-2 px-5 py-2.5 bg-[#CFDBEC] text-gray-800 rounded-lg hover:bg-[#b8c9de] transition-colors font-medium shadow-sm"
                    >
                        <Plus size={18} />
                        Add Language
                    </button>
                </div>
            </div>

            {/* Table Section */}
            <CrudTable
                columns={columns}
                data={fields}
                onEdit={handleEdit}
                onDelete={handleDelete}
                emptyMessage="No languages added yet"
            />

            {/* Language Modal */}
            <LanguageModal
                isOpen={isModalOpen}
                onClose={handleCloseModal}
                onSave={handleSave}
                initialData={editingLanguage}
            />
        </div>
    );
}
