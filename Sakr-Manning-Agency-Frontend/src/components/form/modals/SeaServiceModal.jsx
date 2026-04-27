import React, { useEffect, useMemo, useState } from "react";
import { useForm, FormProvider } from "react-hook-form";
import PropTypes from "prop-types";
import { Modal } from "../../common/Modal";
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { TextDateInput } from "../inputs/DateInput";
import { FileUpload } from "../inputs/FileUpload";
import { FORM_FIELDS, SEA_SERVICE_FIELD_DEFAULTS } from "../../../config/formConfig";
import { MODAL_VALIDATION } from "../../../config/modalValidation";
import { resolveFileUrl } from "../../../utils/fileHelpers";

const V = MODAL_VALIDATION.SEA_SERVICE;

export function SeaServiceModal({ isOpen, onClose, onSave, initialData = null, referenceData = {} }) {
    const [uploadedFile, setUploadedFile] = useState(null);
    const methods = useForm({ defaultValues: SEA_SERVICE_FIELD_DEFAULTS });
    const { handleSubmit, reset, getValues } = methods;
    const isEditMode = !!initialData;

    const rankOptions = useMemo(() => {
        return referenceData?.positions || [];
    }, [referenceData]);

    const flagOptions = useMemo(() => {
        return referenceData?.flags || [];
    }, [referenceData]);

    const vesselTypeOptions = useMemo(() => {
        return referenceData?.vesselTypes || [];
    }, [referenceData]);

    useEffect(() => {
        if (isOpen) {
            if (initialData) {
                const populated = {};
                Object.keys(SEA_SERVICE_FIELD_DEFAULTS).forEach((key) => {
                    populated[key] = initialData[key] || "";
                });
                reset(populated);
                setUploadedFile(null);
            } else {
                reset(SEA_SERVICE_FIELD_DEFAULTS);
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
        <Modal isOpen={isOpen} onClose={handleClose} title="" size="xl">
            <FormProvider {...methods}>
                <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-5">
                    {/* Title */}
                    <h2 className="text-xl font-extrabold text-gray-900 uppercase tracking-wide mb-4">
                        {isEditMode ? "Edit Service Details" : "Service Details"}
                    </h2>

                    {/* Row 1: Company Name | Rank | Vessel Name */}
                    <div className="grid grid-cols-3 gap-3">
                        <BaseInput
                            name={FORM_FIELDS.SEA_SERVICE.COMPANY}
                            required
                            rules={V[FORM_FIELDS.SEA_SERVICE.COMPANY]}
                            placeholder="Company Name"
                            variant="modal"
                        />
                        <Select
                            name={FORM_FIELDS.SEA_SERVICE.RANK}
                            required
                            options={rankOptions}
                            placeholder="Rank"
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.SEA_SERVICE.VESSEL_NAME}
                            required
                            rules={V[FORM_FIELDS.SEA_SERVICE.VESSEL_NAME]}
                            placeholder="Vessel Name"
                            variant="modal"
                        />
                    </div>

                    {/* Row 2: IMO Number | Vessel Type | Flag */}
                    <div className="grid grid-cols-3 gap-3">
                        <BaseInput
                            name={FORM_FIELDS.SEA_SERVICE.IMO_NUMBER}
                            placeholder="IMO Number"
                            variant="modal"
                        />
                        <Select
                            name={FORM_FIELDS.SEA_SERVICE.VESSEL_TYPE}
                            options={vesselTypeOptions}
                            placeholder="Vessel Type"
                            variant="modal"
                        />
                        <Select
                            name={FORM_FIELDS.SEA_SERVICE.FLAG}
                            options={flagOptions}
                            placeholder="Flag"
                            variant="modal"
                        />
                    </div>

                    {/* Row 3: Signed On | Signed Off */}
                    <div className="grid grid-cols-2 gap-3">
                        <TextDateInput
                            name={FORM_FIELDS.SEA_SERVICE.SIGNED_ON}
                            placeholder="Signed On"
                            variant="modal"
                        />
                        <TextDateInput
                            name={FORM_FIELDS.SEA_SERVICE.SIGNED_OFF}
                            placeholder="Signed Off"
                            variant="modal"
                            rules={{
                                validate: (val) => {
                                    if (!val) return true;
                                    const signedOn = getValues(FORM_FIELDS.SEA_SERVICE.SIGNED_ON);
                                    if (signedOn && val <= signedOn) return "Signed Off must be after Signed On";
                                    return true;
                                },
                            }}
                        />
                    </div>

                    {/* Row 4: DWT | GRT */}
                    <div className="grid grid-cols-2 gap-3">
                        <BaseInput
                            name={FORM_FIELDS.SEA_SERVICE.DWT}
                            rules={V[FORM_FIELDS.SEA_SERVICE.DWT]}
                            placeholder="D.W.T"
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.SEA_SERVICE.GRT}
                            rules={V[FORM_FIELDS.SEA_SERVICE.GRT]}
                            placeholder="G.R.T"
                            variant="modal"
                        />
                    </div>

                    {/* Row 5: Engine Type | BH | KW */}
                    <div className="grid grid-cols-3 gap-3">
                        <BaseInput
                            name={FORM_FIELDS.SEA_SERVICE.ENGINE_TYPE}
                            rules={V[FORM_FIELDS.SEA_SERVICE.ENGINE_TYPE]}
                            placeholder="Engine Type"
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.SEA_SERVICE.BH}
                            rules={V[FORM_FIELDS.SEA_SERVICE.BH]}
                            placeholder="B.H."
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.SEA_SERVICE.KW}
                            rules={V[FORM_FIELDS.SEA_SERVICE.KW]}
                            placeholder="K.W."
                            variant="modal"
                        />
                    </div>

                    {/* Row 6: Reason for Sign-Off */}
                    <div className="grid grid-cols-1">
                        <BaseInput
                            name={FORM_FIELDS.SEA_SERVICE.REASON}
                            rules={V[FORM_FIELDS.SEA_SERVICE.REASON]}
                            placeholder="Reason for Sign Off"
                            variant="modal"
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

SeaServiceModal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    onSave: PropTypes.func.isRequired,
    initialData: PropTypes.object,
    referenceData: PropTypes.object,
};