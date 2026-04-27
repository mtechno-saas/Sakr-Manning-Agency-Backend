// components/forms/modals/DocumentModal.jsx
import React, { useEffect, useState } from "react";
import { useForm, FormProvider } from "react-hook-form";
import PropTypes from "prop-types";
import { Modal } from "../../common/Modal";
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { TextDateInput } from "../inputs/DateInput";
import { FileUpload } from "../inputs/FileUpload";
import { DOCUMENT_TYPE_OPTIONS, DOCUMENT_FIELD_DEFAULTS, FORM_FIELDS } from "../../../config/formConfig";
import { MODAL_VALIDATION } from "../../../config/modalValidation";
import { resolveFileUrl } from "../../../utils/fileHelpers";

const V = MODAL_VALIDATION.DOCUMENT;

export function DocumentModal({ isOpen, onClose, onSave, initialData = null }) {
    const [uploadedFile, setUploadedFile] = useState(null);

    const methods = useForm({ defaultValues: DOCUMENT_FIELD_DEFAULTS });
    const { handleSubmit, reset, getValues } = methods;
    const isEditMode = !!initialData;

    useEffect(() => {
        if (isOpen) {
            if (initialData) {
                const populated = {};
                Object.keys(DOCUMENT_FIELD_DEFAULTS).forEach((key) => {
                    populated[key] = initialData[key] || "";
                });
                reset(populated);
                setUploadedFile(initialData.file || null);
            } else {
                reset(DOCUMENT_FIELD_DEFAULTS);
                setUploadedFile(null);
            }
        }
    }, [isOpen, initialData, reset]);

    const existingUrl = resolveFileUrl(initialData);

    const handleFormSubmit = (data) => {
        // Preserve existing file reference if user didn't upload a new one
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
                        {isEditMode ? "Edit Travel Document" : "Add Travel Documents"}
                    </h2>

                    {/* Row 1: Document Name | Document Number | Country of Issue */}
                    <div className="grid grid-cols-3 gap-3">
                        <Select
                            name={FORM_FIELDS.DOCUMENTS.TYPE}
                            required
                            options={DOCUMENT_TYPE_OPTIONS}
                            placeholder="Document name"
                            searchable={true}
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.DOCUMENTS.NUMBER}
                            required
                            rules={V[FORM_FIELDS.DOCUMENTS.NUMBER]}
                            placeholder="Document number"
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.DOCUMENTS.PLACE_OF_ISSUE}
                            placeholder="Place of issue"
                            variant="modal"
                        />
                    </div>

                    {/* Row 2: Issue Date | Expiry Date */}
                    <div className="grid grid-cols-2 gap-3">

                        <TextDateInput
                            name={FORM_FIELDS.DOCUMENTS.ISSUE_DATE}
                            required
                            rules={V[FORM_FIELDS.DOCUMENTS.ISSUE_DATE]}
                            placeholder="Issue Date"
                            variant="modal"
                        />
                        <TextDateInput
                            name={FORM_FIELDS.DOCUMENTS.EXPIRY_DATE}
                            required
                            placeholder="Expiry Date"
                            variant="modal"
                            rules={{
                                ...V[FORM_FIELDS.DOCUMENTS.EXPIRY_DATE],
                                validate: (val) => {
                                    if (!val) return true;
                                    const issueDate = getValues(FORM_FIELDS.DOCUMENTS.ISSUE_DATE);
                                    if (issueDate && val <= issueDate) return "Expiry date must be after issue date";
                                    return true;
                                },
                            }}
                        />
                    </div>

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

DocumentModal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    onSave: PropTypes.func.isRequired,
    initialData: PropTypes.object,
};