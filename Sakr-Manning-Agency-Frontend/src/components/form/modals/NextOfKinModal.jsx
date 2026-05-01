import React, { useEffect } from "react";
import { useForm, FormProvider } from "react-hook-form";
import PropTypes from "prop-types";
import { Modal } from "../../common/Modal";
import { BaseInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import {
    FORM_FIELDS,
    NEXT_OF_KIN_FIELD_DEFAULTS,
    RELATIONSHIP_OPTIONS,
} from "../../../config/formConfig";

export function NextOfKinModal({ isOpen, onClose, onSave, initialData = null }) {
    const methods = useForm({ defaultValues: NEXT_OF_KIN_FIELD_DEFAULTS });
    const { handleSubmit, reset } = methods;
    const isEditMode = !!initialData;

    useEffect(() => {
        if (isOpen) {
            if (initialData) {
                const populated = {};
                Object.keys(NEXT_OF_KIN_FIELD_DEFAULTS).forEach((key) => {
                    populated[key] = initialData[key] || "";
                });
                reset(populated);
            } else {
                reset(NEXT_OF_KIN_FIELD_DEFAULTS);
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
                    <h2 className="text-xl font-extrabold text-gray-900 uppercase tracking-wide mb-4">
                        {isEditMode ? "Edit Emergency Contact" : "Add Emergency Contact"}
                    </h2>

                    {/* Row 1: Full Name — full width */}
                    <BaseInput
                        name={FORM_FIELDS.NEXT_OF_KIN.FULL_NAME}
                        required
                        placeholder="Full Name"
                        variant="modal"
                    />

                    {/* Row 2: Relationship | Address/Country | Phone */}
                    <div className="grid grid-cols-3 gap-3">
                        <Select
                            name={FORM_FIELDS.NEXT_OF_KIN.RELATIONSHIP}
                            required
                            options={RELATIONSHIP_OPTIONS}
                            placeholder="Relationship"
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.NEXT_OF_KIN.ADDRESS_COUNTRY}
                            placeholder="Address / Country"
                            variant="modal"
                        />
                        <BaseInput
                            name={FORM_FIELDS.NEXT_OF_KIN.PHONE}
                            placeholder="Phone"
                            variant="modal"
                        />
                    </div>

                    {/* Row 3: Email — full width */}
                    <BaseInput
                        name={FORM_FIELDS.NEXT_OF_KIN.EMAIL}
                        placeholder="Email"
                        type="email"
                        variant="modal"
                    />

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

NextOfKinModal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    onSave: PropTypes.func.isRequired,
    initialData: PropTypes.object,
};
