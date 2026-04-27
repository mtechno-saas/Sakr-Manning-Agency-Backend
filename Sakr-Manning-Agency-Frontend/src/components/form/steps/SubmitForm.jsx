import React from "react";
import { useFormContext } from "react-hook-form";
import { useFormSave } from "../../../context/FormSaveContext";
import {
  checkAllStepsCompletion,
  formatMissingFields,
  isFormReadyForSubmission,
} from "../../../utils/formCompletionChecker";

export function SubmitForm() {
  const { getValues } = useFormContext();
  const { goToStep } = useFormSave();
  const formData = getValues();

  const completionStatus = checkAllStepsCompletion(formData);
  const submissionReadiness = isFormReadyForSubmission(formData);

  const handleStepClick = (index) => {
    if (goToStep && index < 11) { // 11 is the Submit step index, don't navigate to itself
      goToStep(index);
    }
  };

  return (
    <div className="w-full space-y-6">
      {/* Overall Progress Card */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold">Application Progress</h2>
          <span className="text-4xl font-bold">
            {completionStatus.overallCompletion}%
          </span>
        </div>

        <div className="w-full bg-blue-300 rounded-full h-4 mb-4">
          <div
            className="bg-white h-4 rounded-full transition-all duration-500 shadow-sm"
            style={{ width: `${completionStatus.overallCompletion}%` }}
          />
        </div>

        <p className="text-blue-50 text-sm">
          {completionStatus.completedSteps} of {completionStatus.totalSteps}{" "}
          sections completed
        </p>
      </div>

      {/* Section Breakdown */}
      <div className="bg-white rounded-lg p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">
          Section Status
        </h3>

        <div className="space-y-4">
          {completionStatus.steps.map((step, index) => (
            <div
              key={index}
              onClick={() => handleStepClick(index)}
              className={`border-2 rounded-lg p-4 transition-all duration-200 cursor-pointer hover:shadow-md ${step.isComplete
                ? "border-green-300 bg-green-50 hover:border-green-400"
                : step.completedFields > 0
                  ? "border-yellow-300 bg-yellow-50 hover:border-yellow-400"
                  : index > 3
                    ? "border-yellow-300 bg-yellow-50 hover:border-yellow-400"
                    : "border-red-300 bg-red-50 hover:border-red-400"
                }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  {/* Status Icon */}
                  <div className="flex-shrink-0 mt-1">
                    <div
                      className={`w-6 h-6 rounded-full flex items-center justify-center ${step.isComplete
                        ? "bg-green-500"
                        : step.completedFields > 0
                          ? "bg-yellow-500"
                          : index > 3
                            ? "bg-yellow-500"
                            : "bg-red-500"
                        }`}
                    >
                      {step.isComplete ? (
                        <svg
                          className="w-4 h-4 text-white"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={3}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      ) : (
                        <span className="text-white text-xs font-bold">
                          {step.completedFields > 0 || index > 3 ? "!" : "×"}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Step Info */}
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-1">
                      {step.stepName}
                    </h4>
                    <p className="text-sm text-gray-600">
                      {step.completedFields} of {step.totalFields} fields
                      completed
                    </p>
                  </div>
                </div>

                {/* Progress Badge and Navigation Arrow */}
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <div
                      className={`text-lg font-bold mb-1 ${step.isComplete
                        ? "text-green-600"
                        : step.completedFields > 0
                          ? "text-yellow-600"
                          : index > 3
                            ? "text-yellow-600"
                            : "text-red-600"
                        }`}
                    >
                      {step.completionPercentage}%
                    </div>

                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${step.isComplete
                          ? "bg-green-500"
                          : step.completedFields > 0
                            ? "bg-yellow-500"
                            : index > 3
                              ? "bg-yellow-500"
                              : "bg-red-500"
                          }`}
                        style={{ width: `${step.completionPercentage}%` }}
                      />
                    </div>
                  </div>

                  {/* Navigation Arrow */}
                  <svg
                    className="w-5 h-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </div>
              </div>

              {/* Missing Fields */}
              {!step.isComplete && step.missingFields.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Missing fields:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {formatMissingFields(step.missingFields).map(
                      (fieldName, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-white border border-gray-300 rounded-full text-xs text-gray-700 shadow-sm"
                        >
                          {fieldName}
                        </span>
                      )
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Submission Readiness */}
      <div
        className={`rounded-lg p-6 border-2 ${submissionReadiness.isReady
          ? "border-green-300 bg-green-50"
          : "border-orange-300 bg-orange-50"
          }`}
      >
        <div className="flex items-start gap-4">
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${submissionReadiness.isReady
              ? "bg-green-500"
              : "bg-orange-500"
              }`}
          >
            {submissionReadiness.isReady ? (
              <svg
                className="w-5 h-5 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            ) : (
              <span className="text-white text-xl font-bold">!</span>
            )}
          </div>

          <div className="flex-1">
            <h3
              className={`text-lg font-semibold mb-2 ${submissionReadiness.isReady
                ? "text-green-800"
                : "text-orange-800"
                }`}
            >
              {submissionReadiness.isReady
                ? "✓ Ready for Submission"
                : "⚠ Action Required"}
            </h3>
            <p
              className={`text-sm ${submissionReadiness.isReady
                ? "text-green-700"
                : "text-orange-700"
                }`}
            >
              {submissionReadiness.isReady
                ? "All critical sections are complete. You can now submit your application."
                : "Please complete the required sections before submitting your application."}
            </p>
          </div>
        </div>
      </div>

      {/* Info Message */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex gap-3">
          <svg
            className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="text-sm text-blue-800">
            Click on any section above to navigate and complete it. Once submitted, your
            application will be processed and you'll receive a confirmation.
          </p>
        </div>
      </div>
    </div>
  );
}