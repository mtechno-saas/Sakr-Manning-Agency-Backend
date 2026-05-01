// components/forms/modals/HealthModal.jsx
import React, { useEffect, useState } from "react";
import { useForm, FormProvider } from "react-hook-form";
import PropTypes from "prop-types";
import { Modal } from "../../common/Modal";
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { TextDateInput } from "../inputs/DateInput";
import { TextArea } from "../inputs/TextArea";
import { FileUpload } from "../inputs/FileUpload";
import { VACCINATION_OPTIONS, HEALTH_FIELD_DEFAULTS, FORM_FIELDS } from "../../../config/formConfig";
import { MODAL_VALIDATION } from "../../../config/modalValidation";
import { resolveFileUrl } from "../../../utils/fileHelpers";

const V = MODAL_VALIDATION.HEALTH;

export function HealthModal({ isOpen, onClose, onSave, initialData = null }) {
    const [uploadedFile, setUploadedFile] = useState(null);
    const [noExpiry, setNoExpiry] = useState(false);
    const [noSecondDose, setNoSecondDose] = useState(false);

    const methods = useForm({ defaultValues: HEALTH_FIELD_DEFAULTS });
    const { handleSubmit, reset, setValue, getValues } = methods;
    const isEditMode = !!initialData;

    useEffect(() => {
        if (isOpen) {
            if (initialData) {
                const populated = {};
                Object.keys(HEALTH_FIELD_DEFAULTS).forEach((key) => {
                    populated[key] = initialData[key] || "";
                });
                reset(populated);
                setUploadedFile(null);
            } else {
                reset(HEALTH_FIELD_DEFAULTS);
                setUploadedFile(null);
                setNoExpiry(false);
                setNoSecondDose(false);
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
        setNoSecondDose(false);
        onClose();
    };

    return (
        <Modal isOpen={isOpen} onClose={handleClose} title="" size="xl">
            <FormProvider {...methods}>
                <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-5">
                    {/* Title */}
                    <h2 className="text-xl font-extrabold text-gray-900 uppercase tracking-wide mb-4">
                        {isEditMode ? "Edit Health Record" : "Health Certificates & Vaccinations"}
                    </h2>

                    {/* Row 1: Vaccination Name | Number | Issue Date */}
                    <div className="grid grid-cols-3 gap-3">
                        <Select
                            name={FORM_FIELDS.HEALTH.NAME}
                            required
                            options={VACCINATION_OPTIONS}
                            placeholder="Vaccination name"
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.HEALTH.NUMBER}
                            rules={V[FORM_FIELDS.HEALTH.NUMBER]}
                            placeholder="Number"
                            variant="modal"
                        />
                        <TextDateInput
                            name={FORM_FIELDS.HEALTH.ISSUE_DATE}
                            required
                            rules={V[FORM_FIELDS.HEALTH.ISSUE_DATE]}
                            placeholder="Issue Date"
                            variant="modal"
                        />
                    </div>

                    {/* Row 2: Expiry Date | Issued By | Issued At */}
                    <div className="grid grid-cols-3 gap-3">
                        {noExpiry ? (
                            <div className="flex items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50 text-gray-400 text-sm px-3 h-10">
                                No Expiry
                            </div>
                        ) : (
                            <TextDateInput
                                name={FORM_FIELDS.HEALTH.EXPIRY_DATE}
                                placeholder="Expiry Date"
                                variant="modal"
                                rules={{
                                    validate: (val) => {
                                        if (!val) return true;
                                        const issueDate = getValues(FORM_FIELDS.HEALTH.ISSUE_DATE);
                                        if (issueDate && val <= issueDate) return "Expiry date must be after issue date";
                                        return true;
                                    },
                                }}
                            />
                        )}
                        <BaseInput
                            name={FORM_FIELDS.HEALTH.ISSUED_BY}
                            rules={V[FORM_FIELDS.HEALTH.ISSUED_BY]}
                            placeholder="Issued by"
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.HEALTH.ISSUED_AT}
                            rules={V[FORM_FIELDS.HEALTH.ISSUED_AT]}
                            placeholder="Issued at"
                            variant="modal"
                        />
                    </div>

                    {/* No Expiry Checkbox */}
                    <div className="flex items-center gap-2">
                        <input
                            type="checkbox"
                            id="health-no-expiry"
                            checked={noExpiry}
                            onChange={(e) => {
                                setNoExpiry(e.target.checked);
                                if (e.target.checked) setValue(FORM_FIELDS.HEALTH.EXPIRY_DATE, "");
                            }}
                            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <label htmlFor="health-no-expiry" className="text-sm text-gray-600 select-none">
                            No expiry date (unlimited)
                        </label>
                    </div>

                    {/* Row 3: First Dose | Second Dose */}
                    <div className="grid grid-cols-2 gap-3">
                        <TextDateInput
                            name={FORM_FIELDS.HEALTH.FIRST_DATE}
                            placeholder="First Dose"
                            variant="modal"
                        />
                        {noSecondDose ? (
                            <div className="flex items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50 text-gray-400 text-sm px-3 h-10">
                                No Second Dose
                            </div>
                        ) : (
                            <TextDateInput
                                name={FORM_FIELDS.HEALTH.LAST_DATE}
                                placeholder="Second Dose"
                                variant="modal"
                                rules={{
                                    validate: (val) => {
                                        if (!val) return true;
                                        const firstDose = getValues(FORM_FIELDS.HEALTH.FIRST_DATE);
                                        if (firstDose && val <= firstDose) return "Second dose must be after first dose";
                                        return true;
                                    },
                                }}
                            />
                        )}
                    </div>

                    {/* No Second Dose Checkbox */}
                    <div className="flex items-center gap-2">
                        <input
                            type="checkbox"
                            id="health-no-second-dose"
                            checked={noSecondDose}
                            onChange={(e) => {
                                setNoSecondDose(e.target.checked);
                                if (e.target.checked) setValue(FORM_FIELDS.HEALTH.LAST_DATE, "");
                            }}
                            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <label htmlFor="health-no-second-dose" className="text-sm text-gray-600 select-none">
                            No second dose
                        </label>
                    </div>

                    {/* Row 4: Remarks — full width */}
                    <TextArea
                        name={FORM_FIELDS.HEALTH.REMARKS}
                        rules={V[FORM_FIELDS.HEALTH.REMARKS]}
                        rows={1}
                        placeholder="Remarks"
                        variant="modal"
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

HealthModal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    onSave: PropTypes.func.isRequired,
    initialData: PropTypes.object,
};