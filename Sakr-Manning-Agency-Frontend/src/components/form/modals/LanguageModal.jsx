// components/forms/modals/LanguageModal.jsx
import React, { useEffect, useState } from "react";
import { useForm, FormProvider } from "react-hook-form";
import PropTypes from "prop-types";
import { Modal } from "../../common/Modal";
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { TextArea } from "../inputs/TextArea";
import { FileUpload } from "../inputs/FileUpload";
import { LANGUAGE_OPTIONS, CEFR_LEVELS, LANGUAGE_LEVELS, LANGUAGE_FIELD_DEFAULTS, FORM_FIELDS } from "../../../config/formConfig";
import { MODAL_VALIDATION } from "../../../config/modalValidation";
import { resolveFileUrl } from "../../../utils/fileHelpers";

const V = MODAL_VALIDATION.LANGUAGE;

export function LanguageModal({ isOpen, onClose, onSave, initialData = null }) {
    const [uploadedFile, setUploadedFile] = useState(null);

    const methods = useForm({ defaultValues: LANGUAGE_FIELD_DEFAULTS });
    const { handleSubmit, reset, watch, setValue } = methods;
    const isEditMode = !!initialData;
    const selectedLevel = watch(FORM_FIELDS.LANGUAGES.LEVEL);

    useEffect(() => {
        if (selectedLevel) {
            const levelData = CEFR_LEVELS.find((l) => l.value === selectedLevel);
            if (levelData) {
                setValue(FORM_FIELDS.LANGUAGES.DESCRIPTION, levelData.description);
            }
        }
    }, [selectedLevel, setValue]);

    useEffect(() => {
        if (isOpen) {
            if (initialData) {
                const populated = {};
                Object.keys(LANGUAGE_FIELD_DEFAULTS).forEach((key) => {
                    populated[key] = initialData[key] || "";
                });
                reset(populated);
                setUploadedFile(initialData.file || null);
            } else {
                reset(LANGUAGE_FIELD_DEFAULTS);
                setUploadedFile(null);
            }
        }
    }, [isOpen, initialData, reset]);

    const existingUrl = resolveFileUrl(initialData);

    const handleFormSubmit = (data) => {
        const fileValue = uploadedFile || (existingUrl ? existingUrl : null);
        onSave({ ...data, file: fileValue, ...(initialData?.id && { id: initialData.id }) });
        handleClose();
    };

    const handleClose = () => {
        reset();
        setUploadedFile(null);
        onClose();
    };

    return (
        <Modal isOpen={isOpen} onClose={handleClose} title="" size="lg">
            <FormProvider {...methods}>
                <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-5">
                    {/* Title */}
                    <h2 className="text-xl font-bold text-gray-900 mb-4">
                        {isEditMode ? "Edit Language" : "Add Language"}
                    </h2>

                    {/* Row 1: Language | General Marks | Speaking */}
                    <div className="grid grid-cols-3 gap-3">
                        <Select
                            name={FORM_FIELDS.LANGUAGES.LANGUAGE}
                            required
                            options={LANGUAGE_OPTIONS}
                            placeholder="Language"
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.LANGUAGES.GENERAL}
                            type="number"
                            rules={V[FORM_FIELDS.LANGUAGES.GENERAL]}
                            placeholder="General remarks"
                            min="0"
                            max="100"
                            variant="modal"
                        />
                        <Select
                            name={FORM_FIELDS.LANGUAGES.SPEAKING}
                            placeholder="Speaking"
                            variant="modal"
                            options={LANGUAGE_LEVELS}
                        />
                    </div>

                    {/* Row 2: Writing | Reading | CEFR Level */}
                    <div className="grid grid-cols-3 gap-3">
                        <Select
                            name={FORM_FIELDS.LANGUAGES.WRITING}
                            placeholder="Writing"
                            variant="modal"
                            options={LANGUAGE_LEVELS}
                        />
                        <Select
                            name={FORM_FIELDS.LANGUAGES.READING}
                            placeholder="Reading"
                            variant="modal"
                            options={LANGUAGE_LEVELS}
                        />
                        <Select
                            name={FORM_FIELDS.LANGUAGES.LEVEL}
                            required
                            options={CEFR_LEVELS}
                            placeholder="CEFR Level"
                            searchable={false}
                            variant="modal"
                        />
                    </div>

                    {/* Row 3: Description — full width */}
                    <TextArea
                        name={FORM_FIELDS.LANGUAGES.DESCRIPTION}
                        rows={1}
                        placeholder="Description of selected CEFR Level"
                        readOnly
                        variant="modal"
                        className="bg-gray-50 text-gray-500"
                    />

                    {/* File Upload */}
                    <div className="flex justify-center">
                        <div className="w-2/3">
                            <FileUpload
                                value={uploadedFile}
                                onChange={setUploadedFile}
                                existingFileUrl={existingUrl}
                            />
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex justify-end gap-3 pt-2">
                        <button
                            type="button"
                            onClick={handleClose}
                            className="px-8 py-2.5 border border-[#0065AF] text-[#0065AF] rounded-full font-semibold hover:bg-blue-50 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="px-8 py-2.5 bg-[#0065AF] text-white rounded-full font-semibold hover:bg-[#2477C3] transition-colors"
                        >
                            {isEditMode ? "Save Changes" : "Add"}
                        </button>
                    </div>
                </form>
            </FormProvider>
        </Modal>
    );
}

LanguageModal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    onSave: PropTypes.func.isRequired,
    initialData: PropTypes.object,
};