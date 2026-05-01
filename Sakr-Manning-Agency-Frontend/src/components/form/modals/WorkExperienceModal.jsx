// components/forms/modals/WorkExperienceModal.jsx
import React, { useEffect } from "react";
import { useForm, FormProvider } from "react-hook-form";
import PropTypes from "prop-types";
import { Modal } from "../../common/Modal";
import { TextArea } from "../inputs/TextArea";
import { FORM_FIELDS, WORK_EXPERIENCE_FIELD_DEFAULTS } from "../../../config/formConfig";
import { MODAL_VALIDATION } from "../../../config/modalValidation";

const V = MODAL_VALIDATION.WORK_EXPERIENCE;

/**
 * Work Experience Modal Component
 *
 * Modal for adding/editing work experience descriptions
 */
export function WorkExperienceModal({ isOpen, onClose, onSave, initialData = null }) {
    const methods = useForm({
        defaultValues: WORK_EXPERIENCE_FIELD_DEFAULTS,
    });

    const { handleSubmit, reset } = methods;

    const isEditMode = !!initialData;

    useEffect(() => {
        if (isOpen) {
            if (initialData) {
                const populated = {};
                Object.keys(WORK_EXPERIENCE_FIELD_DEFAULTS).forEach((key) => {
                    populated[key] = initialData[key] || "";
                });
                reset(populated);
            } else {
                reset(WORK_EXPERIENCE_FIELD_DEFAULTS);
            }
        }
    }, [isOpen, initialData, reset]);

    const handleFormSubmit = (data) => {
        const expData = {
            ...data,
            ...(initialData?.id && { id: initialData.id }),
        };
        onSave(expData);
        handleClose();
    };

    const handleClose = () => {
        reset();
        onClose();
    };

    return (
        <Modal
            isOpen={isOpen}
            onClose={handleClose}
            title={isEditMode ? "Edit Work Experience" : "Add Work Experience"}
            size="md"
        >
            <FormProvider {...methods}>
                <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
                    {/* Experience Description */}
                    <TextArea
                        name={FORM_FIELDS.WORK_EXPERIENCE.EXPERIENCE}
                        label="Experience Description"
                        required
                        rules={V[FORM_FIELDS.WORK_EXPERIENCE.EXPERIENCE]}
                        rows={6}
                        placeholder="Describe your work experience in detail..."
                        variant="modal"
                    />

                    {/* Action Buttons */}
                    <div className="flex justify-end gap-3 pt-4">
                        <button
                            type="button"
                            onClick={handleClose}
                            className="px-6 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="px-6 py-2.5 bg-[#CFDBEC] text-gray-800 rounded-lg hover:bg-[#b8c9de] transition-colors font-medium"
                        >
                            {isEditMode ? "Save Changes" : "Add Work Experience"}
                        </button>
                    </div>
                </form>
            </FormProvider>
        </Modal>
    );
}

WorkExperienceModal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    onSave: PropTypes.func.isRequired,
    initialData: PropTypes.object,
};
