// components/forms/modals/CertificateModal.jsx
import React, { useEffect, useState } from "react";
import { useForm, FormProvider } from "react-hook-form";
import PropTypes from "prop-types";
import { Modal } from "../../common/Modal";
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { TextDateInput } from "../inputs/DateInput";
import { FileUpload } from "../inputs/FileUpload";
import { FORM_FIELDS, CERTIFICATE_FIELD_DEFAULTS } from "../../../config/formConfig";
import { MODAL_VALIDATION } from "../../../config/modalValidation";
import { resolveFileUrl } from "../../../utils/fileHelpers";

const V = MODAL_VALIDATION.CERTIFICATE;

export function CertificateModal({ isOpen, onClose, onSave, initialData = null, certificateOptions = [] }) {
    const [uploadedFile, setUploadedFile] = useState(null);

    const methods = useForm({ defaultValues: CERTIFICATE_FIELD_DEFAULTS });
    const { handleSubmit, reset, getValues } = methods;
    const isEditMode = !!initialData;

    useEffect(() => {
        if (isOpen) {
            if (initialData) {
                const populated = {};
                Object.keys(CERTIFICATE_FIELD_DEFAULTS).forEach((key) => {
                    populated[key] = initialData[key] || "";
                });
                reset(populated);
                setUploadedFile(null);
            } else {
                reset(CERTIFICATE_FIELD_DEFAULTS);
                setUploadedFile(null);
            }
        }
    }, [isOpen, initialData, reset]);

    const existingUrl = resolveFileUrl(initialData);

    const handleFormSubmit = (data) => {
        const fileValue = uploadedFile || (existingUrl ? existingUrl : null);
        onSave({
            ...data,
            file: fileValue,
            ...(initialData?.id && { id: initialData.id }),
        });
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
                    {/* Header */}
                    <div className="flex items-center justify-between mb-2">
                        <h2 className="text-2xl font-bold text-gray-900">
                            {isEditMode ? "Edit certificate" : "Add certificates"}
                        </h2>
                        <button
                            type="button"
                            onClick={handleClose}
                            className="text-gray-400 hover:text-gray-600 transition-colors p-1"
                        >
                            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    {/* Row 1: Certificate Name | Certificate Number | Country of issue */}
                    <div className="grid grid-cols-3 gap-3">
                        <Select
                            name={FORM_FIELDS.CERTIFICATES.NAME}
                            required
                            options={certificateOptions}
                            placeholder="Document name"
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.CERTIFICATES.NUMBER}
                            required
                            rules={V[FORM_FIELDS.CERTIFICATES.NUMBER]}
                            placeholder="Document number"
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.CERTIFICATES.ISSUED_BY}
                            rules={V[FORM_FIELDS.CERTIFICATES.ISSUED_BY]}
                            placeholder="Country of issue"
                            variant="modal"
                        />
                    </div>

                    {/* Row 2: Issue Date | Expiry Date */}
                    <div className="grid grid-cols-2 gap-3 mb-6">
                        <TextDateInput
                            name={FORM_FIELDS.CERTIFICATES.ISSUE_DATE}
                            required
                            rules={V[FORM_FIELDS.CERTIFICATES.ISSUE_DATE]}
                            placeholder="Issue Date"
                            variant="modal"
                        />
                        <TextDateInput
                            name={FORM_FIELDS.CERTIFICATES.EXPIRY_DATE}
                            placeholder="Expiry Date"
                            variant="modal"
                            rules={{
                                validate: (val) => {
                                    if (!val) return true;
                                    const issueDate = getValues(FORM_FIELDS.CERTIFICATES.ISSUE_DATE);
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
                    <div className="flex justify-end gap-4 pt-4">
                        <button
                            type="button"
                            onClick={handleClose}
                            className="px-8 py-2.5 border-2 border-[#0065AF] text-[#0065AF] rounded-full font-semibold hover:bg-blue-50 transition-colors bg-white min-w-[120px]"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="px-8 py-2.5 bg-[#0065AF] text-white rounded-full font-semibold hover:bg-[#00528D] transition-colors min-w-[120px]"
                        >
                            {isEditMode ? "Save" : "Add"}
                        </button>
                    </div>
                </form>
            </FormProvider>
        </Modal>
    );
}

CertificateModal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    onSave: PropTypes.func.isRequired,
    initialData: PropTypes.object,
    certificateOptions: PropTypes.array,
};