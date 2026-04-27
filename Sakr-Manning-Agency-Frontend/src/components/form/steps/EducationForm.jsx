// components/forms/sections/EducationForm.jsx
import React, { useState } from "react";
import { useFormContext, useFieldArray, Controller } from "react-hook-form";
import { Plus } from "lucide-react";
import { BaseInput } from "../inputs/BaseInput";
import { TextDateInput } from "../inputs/DateInput";
import { RadioGroup } from "../inputs/RadioGroup";
import { EDUCATION_RULES } from "../../../utils/RHFvalidationRules";
import { LanguageModal } from "../modals/LanguageModal";
import { CrudTable } from "../layout/FormTable";
import { StepSaveButton } from "../layout/StepSaveButton";
import { FileUpload } from "../inputs/FileUpload";
import { FORM_FIELDS } from "../../../config/formConfig";

/**
 * EducationForm Component
 * 
 * Features:
 * - Education and Marlins Test sections
 * - Modal-based CRUD for languages
 * - Integrated with useFieldArray for languages
 */
export function EducationForm() {
  const { control, getValues } = useFormContext();

  const {
    fields: languageFields,
    append: appendLanguage,
    update: updateLanguage,
    remove: removeLanguage,
  } = useFieldArray({
    control,
    name: "languages",
  });

  const [isLanguageModalOpen, setIsLanguageModalOpen] = useState(false);
  const [editingLanguage, setEditingLanguage] = useState(null);
  const [editingLanguageIndex, setEditingLanguageIndex] = useState(null);

  const generateId = (prefix = "item") =>
    `${prefix}-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

  /* ---------------- Language handlers ---------------- */
  const handleAddLanguage = () => {
    setEditingLanguage(null);
    setIsLanguageModalOpen(true);
  };

  const handleEditLanguage = (language) => {
    const index = languageFields.findIndex((f) => f.id === language.id);
    setEditingLanguageIndex(index);
    const realData = getValues(`languages.${index}`);
    setEditingLanguage({ ...language, _originalId: realData?.id || language.id });
    setIsLanguageModalOpen(true);
  };

  const handleSaveLanguage = (languageData) => {
    if (editingLanguageIndex !== null) {
      updateLanguage(editingLanguageIndex, {
        ...languageData,
        id: editingLanguage._originalId,
      });
    } else {
      appendLanguage({
        ...languageData,
        id: generateId("lang"),
      });
    }
  };

  const handleDeleteLanguage = (id) => {
    if (!window.confirm("Are you sure you want to delete this language?")) {
      return;
    }
    const idx = languageFields.findIndex((f) => f.id === id);
    if (idx !== -1) removeLanguage(idx);
  };

  const handleCloseLanguageModal = () => {
    setIsLanguageModalOpen(false);
    setEditingLanguage(null);
    setEditingLanguageIndex(null);
  };

  // Language table columns - using snake_case to match backend/modal data
  const languageColumns = [
    { key: "language", label: "Language" },
    { key: "general_remarks", label: "General Marks" },
    { key: "speaking_level", label: "Speaking" },
    { key: "writing_level", label: "Writing" },
    { key: "reading_level", label: "Reading" },
    { key: "cefr_level", label: "CEFR Level" },
    // { key: "attachment", label: "Attachment" },
  ];

  return (
    <div className="w-full space-y-6">
      <StepSaveButton />
      {/* Education, Marlins Test, CES Test — single card */}
      <div className="bg-white rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Education
        </h2>
        <BaseInput
          name={FORM_FIELDS.EDUCATION.SCHOOL}
          placeholder="Enter your College | School"
          required
          variant="outlined"
          rules={EDUCATION_RULES.education_school}
        />

        {/* Marlins Test */}
        <h3 className="text-lg font-semibold text-gray-800 mt-8 mb-4">
          Marlins Test
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <BaseInput
            name={FORM_FIELDS.EDUCATION.MARINE_RESULT}
            placeholder="Result %"
            required
            type="number"
            variant="outlined"
          // rules={EDUCATION_RULES.marine_result}
          />
          <TextDateInput
            name={FORM_FIELDS.EDUCATION.MARINE_ISSUED_DATE}
            placeholder="DD-MM-YYYY"
            // required
            variant="outlined"
          // rules={EDUCATION_RULES.marine_issued_date}
          />
          <BaseInput
            name={FORM_FIELDS.EDUCATION.MARINE_ISSUED_BY}
            placeholder="Issued By (Authority)"
            // required
            variant="outlined"
          // rules={EDUCATION_RULES.marine_issued_by}
          />
        </div>
        <BaseInput
          name={FORM_FIELDS.EDUCATION.MARINE_ISSUED_AT}
          placeholder="Issued At"
          // required
          variant="outlined"
        // rules={EDUCATION_RULES.marine_issued_at}
        />
        <div className="mt-4 flex justify-center">
          <div className="w-2/3">
            <Controller
              name="marlins_test_attachment"
              control={control}
              render={({ field }) => (
                <FileUpload
                  value={field.value}
                  onChange={field.onChange}
                  // label="Attach Marlins Test File"
                  existingFileUrl={typeof field.value === 'string' ? field.value : null}
                  existingFileName={typeof field.value === 'string' ? 'Marlins Test File' : null}
                />
              )}
            />
          </div>
        </div>

        {/* CES Test */}
        <h3 className="text-lg font-semibold text-gray-800 mt-8 mb-4">
          CES Test
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <BaseInput
            name={FORM_FIELDS.CES_TEST.RESULT}
            placeholder="Test Result"
            variant="outlined"
          />
          <TextDateInput
            name={FORM_FIELDS.CES_TEST.ISSUED_DATE}
            placeholder="Issued Date"
            variant="outlined"
          />
          <BaseInput
            name={FORM_FIELDS.CES_TEST.ISSUED_BY}
            placeholder="Issued By"
            variant="outlined"
          />
        </div>
        <BaseInput
          name={FORM_FIELDS.CES_TEST.ISSUED_AT}
          placeholder="Issued At"
          variant="outlined"
        />
        <div className="mt-4 flex justify-center">
          <div className="w-2/3">
            <Controller
              name="ces_test_attachment"
              control={control}
              render={({ field }) => (
                <FileUpload
                  value={field.value}
                  onChange={field.onChange}
                  // label="Attach CES Test File"
                  existingFileUrl={typeof field.value === 'string' ? field.value : null}
                  existingFileName={typeof field.value === 'string' ? 'CES Test File' : null}
                />
              )}
            />
          </div>
        </div>
      </div>

      {/* Languages Section - CRUD Table */}
      <div className="bg-[#E8F4FD] rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Languages
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Add your language proficiency details
            </p>
          </div>
          <button
            type="button"
            onClick={handleAddLanguage}
            className="flex items-center gap-2 px-5 py-2.5 bg-[#CFDBEC] text-gray-800 rounded-lg hover:bg-[#b8c9de] transition-colors font-medium shadow-sm"
          >
            <Plus className="w-5 h-5" />
            Add Language
          </button>
        </div>
      </div>

      {/* Languages Table */}
      {languageFields.length > 0 && (
        <CrudTable
          data={languageFields}
          columns={languageColumns}
          onEdit={handleEditLanguage}
          onDelete={handleDeleteLanguage}
          emptyMessage="No languages added yet. Click 'Add Language' to get started."
          showAttachment={false}
        />
      )}

      {/* Language Modal */}
      <LanguageModal
        isOpen={isLanguageModalOpen}
        onClose={handleCloseLanguageModal}
        onSave={handleSaveLanguage}
        initialData={editingLanguage}
      />
    </div>
  );
}