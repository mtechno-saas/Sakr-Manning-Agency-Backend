// components/forms/modals/LicenseModal.jsx
import React, { useEffect, useState } from "react";
import { useForm, FormProvider } from "react-hook-form";
import PropTypes from "prop-types";
import { Modal } from "../../common/Modal";
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { TextDateInput } from "../inputs/DateInput";
import { FileUpload } from "../inputs/FileUpload";
import { LICENSE_OPTIONS, LICENSE_FIELD_DEFAULTS, FORM_FIELDS } from "../../../config/formConfig";
import { MODAL_VALIDATION } from "../../../config/modalValidation";
import { resolveFileUrl } from "../../../utils/fileHelpers";

const V = MODAL_VALIDATION.LICENSE;

export function LicenseModal({ isOpen, onClose, onSave, initialData = null }) {
    const [uploadedFile, setUploadedFile] = useState(null);
    const [noExpiry, setNoExpiry] = useState(false);

    const methods = useForm({ defaultValues: LICENSE_FIELD_DEFAULTS });
    const { handleSubmit, reset, setValue, getValues } = methods;
    const isEditMode = !!initialData;

    useEffect(() => {
        if (isOpen) {
            if (initialData) {
                const populated = {};
                Object.keys(LICENSE_FIELD_DEFAULTS).forEach((key) => {
                    populated[key] =
                        initialData[key] || initialData[key.replace(/_/g, "")] || "";
                });
                reset(populated);
                setUploadedFile(null);
            } else {
                reset(LICENSE_FIELD_DEFAULTS);
                setUploadedFile(null);
                setNoExpiry(false);
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
        setNoExpiry(false);
        onClose();
    };

    return (
        <Modal isOpen={isOpen} onClose={handleClose} title="" size="lg">
            <FormProvider {...methods}>
                <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-5">
                    {/* Title */}
                    <h2 className="text-xl font-bold text-gray-900 mb-4">
                        {isEditMode ? "Edit License" : "Add Licenses"}
                    </h2>

                    {/* Row 1: License Name | License Number | Country of Issue */}
                    <div className="grid grid-cols-3 gap-3">
                        <Select
                            name={FORM_FIELDS.LICENSES.NAME}
                            required
                            options={LICENSE_OPTIONS}
                            placeholder="Document name"
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.LICENSES.NUMBER}
                            required
                            rules={V[FORM_FIELDS.LICENSES.NUMBER]}
                            placeholder="Document number"
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.LICENSES.COUNTRY}
                            required
                            rules={V[FORM_FIELDS.LICENSES.COUNTRY]}
                            placeholder="Country of issue"
                            variant="modal"
                        />
                    </div>

                    {/* Row 2: Issue Date | Expiry Date */}
                    <div className="grid grid-cols-2 gap-3">
                        <TextDateInput
                            name={FORM_FIELDS.LICENSES.ISSUE_DATE}
                            required
                            rules={V[FORM_FIELDS.LICENSES.ISSUE_DATE]}
                            placeholder="Issue Date"
                            variant="modal"
                        />
                        {noExpiry ? (
                            <div className="flex items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50 text-gray-400 text-sm px-3">
                                No Expiry
                            </div>
                        ) : (
                            <TextDateInput
                                name={FORM_FIELDS.LICENSES.EXPIRY_DATE}
                                placeholder="Expiry Date"
                                variant="modal"
                                rules={{
                                    validate: (val) => {
                                        if (!val) return true;
                                        const issueDate = getValues(FORM_FIELDS.LICENSES.ISSUE_DATE);
                                        if (issueDate && val <= issueDate) return "Expiry date must be after issue date";
                                        return true;
                                    },
                                }}
                            />
                        )}
                    </div>

                    {/* No Expiry Checkbox */}
                    <div className="flex items-center gap-2">
                        <input
                            type="checkbox"
                            id="license-no-expiry"
                            checked={noExpiry}
                            onChange={(e) => {
                                setNoExpiry(e.target.checked);
                                if (e.target.checked) setValue(FORM_FIELDS.LICENSES.EXPIRY_DATE, "");
                            }}
                            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <label htmlFor="license-no-expiry" className="text-sm text-gray-600 select-none">
                            No expiry date (unlimited)
                        </label>
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

LicenseModal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    onSave: PropTypes.func.isRequired,
    initialData: PropTypes.object,
};