// components/forms/modals/ReferenceModal.jsx
import React, { useEffect } from "react";
import { useForm, FormProvider } from "react-hook-form";
import PropTypes from "prop-types";
import { Modal } from "../../common/Modal";
import { BaseInput } from "../inputs/BaseInput";
import { FORM_FIELDS, REFERENCE_FIELD_DEFAULTS } from "../../../config/formConfig";
import { MODAL_VALIDATION } from "../../../config/modalValidation";

const V = MODAL_VALIDATION.REFERENCE;

export function ReferenceModal({ isOpen, onClose, onSave, initialData = null }) {
    const methods = useForm({ defaultValues: REFERENCE_FIELD_DEFAULTS });
    const { handleSubmit, reset } = methods;
    const isEditMode = !!initialData;

    useEffect(() => {
        if (isOpen) {
            if (initialData) {
                const populated = {};
                Object.keys(REFERENCE_FIELD_DEFAULTS).forEach((key) => {
                    populated[key] = initialData[key] || "";
                });
                reset(populated);
            } else {
                reset(REFERENCE_FIELD_DEFAULTS);
            }
        }
    }, [isOpen, initialData, reset]);

    const handleFormSubmit = (data) => {
        onSave({ ...data, ...(initialData?.id && { id: initialData.id }) });
        handleClose();
    };

    const handleClose = () => {
        reset();
        onClose();
    };

    return (
        <Modal isOpen={isOpen} onClose={handleClose} title="" size="lg">
            <FormProvider {...methods}>
                <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-5">
                    {/* Title */}
                    <h2 className="text-xl font-bold text-gray-900 mb-4">
                        {isEditMode ? "Edit Reference" : "Add Reference"}
                    </h2>

                    {/* Row 1: Name | Company | Position */}
                    <div className="grid grid-cols-3 gap-3">
                        <BaseInput
                            name={FORM_FIELDS.REFERENCE.NAME}
                            required
                            rules={V[FORM_FIELDS.REFERENCE.NAME]}
                            placeholder="Full Name"
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.REFERENCE.COMPANY_NAME}
                            required
                            rules={V[FORM_FIELDS.REFERENCE.COMPANY_NAME]}
                            placeholder="Company Name"
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.REFERENCE.POSITION}
                            rules={V[FORM_FIELDS.REFERENCE.POSITION]}
                            placeholder="Position"
                            variant="modal"
                        />
                    </div>

                    {/* Row 2: Email | Telephone */}
                    <div className="grid grid-cols-2 gap-3">
                        <BaseInput
                            name={FORM_FIELDS.REFERENCE.EMAIL}
                            type="email"
                            rules={V[FORM_FIELDS.REFERENCE.EMAIL]}
                            placeholder="Email"
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.REFERENCE.TEL}
                            type="tel"
                            rules={V[FORM_FIELDS.REFERENCE.TEL]}
                            placeholder="Telephone"
                            variant="modal"
                        />
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

ReferenceModal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    onSave: PropTypes.func.isRequired,
    initialData: PropTypes.object,
};