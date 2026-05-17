import { useState } from "react";
import { useFormContext } from "react-hook-form";
import { useFormSave } from "../../../context/FormSaveContext";
import { useToast } from "../../../context/ToastContext";
import { cleanDraftFields, validateNoDrafts } from "../../../utils/draftUtils";
import { useReferenceDataContext } from "../../../context/ReferenceDataContext";

export function StepSaveButton() {
    const { saveFormData, isSaving: isGlobalSaving } = useFormSave();
    const { notify } = useToast();
    const refData = useReferenceDataContext();
    const methods = useFormContext();
    const [isLocalSaving, setIsLocalSaving] = useState(false);

    const handleSave = async () => {
        if (isLocalSaving || isGlobalSaving) return;

        setIsLocalSaving(true);

        try {
            const formData = methods.getValues();
            const cleanData = cleanDraftFields(formData);

            if (!validateNoDrafts(cleanData)) {
                notify.error("Please complete any draft entries first");
                setIsLocalSaving(false);
                return;
            }

            const result = await saveFormData(cleanData);

            if (result.success) {
                notify.success("Progress saved!");

                // Surface sync errors as warnings
                if (result.syncErrors?.length > 0) {
                    const unique = [...new Set(result.syncErrors)];
                    unique.forEach((err) => notify.warning(err));
                }

                // Merge returned data with form
                if (result.data) {
                    let application_for_position = result.data.application_for_position;
                    if (application_for_position && typeof application_for_position === "string") {
                        const positionsOpts = refData?.positions || [];
                        const matchedOpt = positionsOpts.find(
                            (opt) =>
                                opt.label?.toLowerCase() === application_for_position.toLowerCase() ||
                                opt.value?.toString() === application_for_position
                        );
                        if (matchedOpt) {
                            application_for_position = matchedOpt.value;
                        }
                    }

                    const currentFormData = methods.getValues();
                    const mergedData = {
                        ...currentFormData,
                        ...result.data,
                        application_for_position,
                        documents: result.data.documents || currentFormData.documents || [],
                        certificates: result.data.certificates || currentFormData.certificates || [],
                        health: result.data.health || currentFormData.health || [],
                        courses: result.data.courses || currentFormData.courses || [],
                        seaServices: result.data.seaServices || currentFormData.seaServices || [],
                        workExperiences: result.data.workExperiences || currentFormData.workExperiences || [],
                    };
                    methods.reset(mergedData);
                }
            } else {
                notify.error(result.message || "Save failed");
            }
        } catch (error) {
            console.error("Save error:", error);
            notify.error("Save failed. Please try again.");
        } finally {
            setIsLocalSaving(false);
        }
    };

    const isSaving = isLocalSaving || isGlobalSaving;

    return (
        <div className="flex items-center gap-3 mb-4">
            <button
                type="button"
                onClick={handleSave}
                disabled={isSaving}
                className={`
          inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
          transition-all duration-200 shadow-sm
          ${isSaving
                        ? "bg-gray-200 text-gray-500 cursor-not-allowed"
                        : "bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800"
                    }
        `}
            >
                {isSaving ? (
                    <>
                        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                            <circle
                                className="opacity-25"
                                cx="12"
                                cy="12"
                                r="10"
                                stroke="currentColor"
                                strokeWidth="4"
                                fill="none"
                            />
                            <path
                                className="opacity-75"
                                fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            />
                        </svg>
                        Saving...
                    </>
                ) : (
                    <>
                        <svg
                            className="h-4 w-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"
                            />
                        </svg>
                        Save Progress
                    </>
                )}
            </button>
        </div>
    );
}

export default StepSaveButton;
