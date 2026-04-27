// components/forms/steps/DeclarationForm.jsx
import React from "react";
import { useFormContext, Controller } from "react-hook-form";
import { StepSaveButton } from "../layout/StepSaveButton";

/**
 * DeclarationForm Component - Step 11
 * 
 * Health declaration with YES/NO questions and conditional detail fields.
 * This is a SINGLE OBJECT (not a collection), stored directly in form data.
 * 
 * Fields:
 * - has_disease (boolean) + disease_details (text)
 * - has_accident (boolean) + accident_details (text)
 * - has_psychiatric_treatment (boolean) + psychiatric_treatment_details (text)
 * - has_addiction (boolean) + addiction_details (text)
 * - consent_given (boolean)
 * - declaration_place, declaration_date, signature
 */
export function DeclarationForm() {
    const { control, watch } = useFormContext();

    // Watch boolean fields to show/hide detail text areas
    const hasDisease = watch("declaration.has_disease");
    const hasAccident = watch("declaration.has_accident");
    const hasPsychiatricTreatment = watch("declaration.has_psychiatric_treatment");
    const hasAddiction = watch("declaration.has_addiction");

    return (
        <div className="w-full space-y-6">
            <StepSaveButton />

            {/* Main Content Card */}
            <div className="bg-white rounded-lg p-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-6">
                    Declaration
                </h2>

                <p className="text-gray-700 mb-6">
                    Please answer the following questions:
                </p>

                {/* Question 1: Disease */}
                <div className="mb-8">
                    <div className="flex items-start justify-between gap-4 mb-3">
                        <label className="text-gray-800 flex-1">
                            Did you suffer, or presently suffer from, any disease likely to render you unfit for
                            services at sea or likely to endanger the health of other persons on board? If yes,
                            please provide details
                        </label>
                        <Controller
                            name="declaration.has_disease"
                            control={control}
                            defaultValue={false}
                            render={({ field }) => (
                                <div className="flex items-center gap-4">
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            checked={field.value === true}
                                            onChange={() => field.onChange(true)}
                                            className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                                        />
                                        <span className="text-gray-700 font-medium">YES</span>
                                    </label>
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            checked={field.value === false}
                                            onChange={() => field.onChange(false)}
                                            className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                                        />
                                        <span className="text-gray-700 font-medium">NO</span>
                                    </label>
                                </div>
                            )}
                        />
                    </div>
                    {hasDisease && (
                        <Controller
                            name="declaration.disease_details"
                            control={control}
                            defaultValue=""
                            render={({ field }) => (
                                <textarea
                                    {...field}
                                    rows={3}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    placeholder="Please provide details..."
                                />
                            )}
                        />
                    )}
                    <div className="border-t border-gray-300 mt-4"></div>
                </div>

                {/* Question 2: Accident */}
                <div className="mb-8">
                    <div className="flex items-start justify-between gap-4 mb-3">
                        <label className="text-gray-800 flex-1">
                            Did you suffer any accident, which rendered you temporary and/or partially disabled?
                        </label>
                        <Controller
                            name="declaration.has_accident"
                            control={control}
                            defaultValue={false}
                            render={({ field }) => (
                                <div className="flex items-center gap-4">
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            checked={field.value === true}
                                            onChange={() => field.onChange(true)}
                                            className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                                        />
                                        <span className="text-gray-700 font-medium">YES</span>
                                    </label>
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            checked={field.value === false}
                                            onChange={() => field.onChange(false)}
                                            className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                                        />
                                        <span className="text-gray-700 font-medium">NO</span>
                                    </label>
                                </div>
                            )}
                        />
                    </div>
                    {hasAccident && (
                        <Controller
                            name="declaration.accident_details"
                            control={control}
                            defaultValue=""
                            render={({ field }) => (
                                <textarea
                                    {...field}
                                    rows={3}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    placeholder="Please provide details..."
                                />
                            )}
                        />
                    )}
                    <div className="border-t border-gray-300 mt-4"></div>
                </div>

                {/* Question 3: Psychiatric Treatment */}
                <div className="mb-8">
                    <div className="flex items-start justify-between gap-4 mb-3">
                        <label className="text-gray-800 flex-1">
                            Did you ever undergo psychiatric treatment
                        </label>
                        <Controller
                            name="declaration.has_psychiatric_treatment"
                            control={control}
                            defaultValue={false}
                            render={({ field }) => (
                                <div className="flex items-center gap-4">
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            checked={field.value === true}
                                            onChange={() => field.onChange(true)}
                                            className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                                        />
                                        <span className="text-gray-700 font-medium">YES</span>
                                    </label>
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            checked={field.value === false}
                                            onChange={() => field.onChange(false)}
                                            className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                                        />
                                        <span className="text-gray-700 font-medium">NO</span>
                                    </label>
                                </div>
                            )}
                        />
                    </div>
                    {hasPsychiatricTreatment && (
                        <Controller
                            name="declaration.psychiatric_treatment_details"
                            control={control}
                            defaultValue=""
                            render={({ field }) => (
                                <textarea
                                    {...field}
                                    rows={3}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    placeholder="Please provide details..."
                                />
                            )}
                        />
                    )}
                    <div className="border-t border-gray-300 mt-4"></div>
                </div>

                {/* Question 4: Addiction */}
                <div className="mb-8">
                    <div className="flex items-start justify-between gap-4 mb-3">
                        <label className="text-gray-800 flex-1">
                            Are you addicted to alcohol or drugs of any kind?
                        </label>
                        <Controller
                            name="declaration.has_addiction"
                            control={control}
                            defaultValue={false}
                            render={({ field }) => (
                                <div className="flex items-center gap-4">
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            checked={field.value === true}
                                            onChange={() => field.onChange(true)}
                                            className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                                        />
                                        <span className="text-gray-700 font-medium">YES</span>
                                    </label>
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            checked={field.value === false}
                                            onChange={() => field.onChange(false)}
                                            className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                                        />
                                        <span className="text-gray-700 font-medium">NO</span>
                                    </label>
                                </div>
                            )}
                        />
                    </div>
                    {hasAddiction && (
                        <Controller
                            name="declaration.addiction_details"
                            control={control}
                            defaultValue=""
                            render={({ field }) => (
                                <textarea
                                    {...field}
                                    rows={3}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    placeholder="Please provide details..."
                                />
                            )}
                        />
                    )}
                </div>

                {/* Consent Section */}
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-6">
                    <p className="text-sm text-gray-700 leading-relaxed mb-4">
                        I hereby declare that the above facts and information are true and accurate. I further consent to the holding and processing
                        by (i) the owners of any vessel on which I may be assigned from time to time and (ii) the Managers and any direct or indirect
                        parent or subsidiary or associated or affiliated company of the Managers (together referred to as "the Companies") for the
                        purposes of my employment, of personal data about me contained herein, or provided to any of the Companies at a later
                        date, including with respect to personal and pensions administration, employee management and as required to comply
                        with any laws, regulations or contracts applicable to any of the Companies or their businesses. I understand that this data will
                        be stored in the Managers' database for the purposes of my current or future employment arranged by the Managers. Further,
                        I confirm that the above may involve the transfer of my personal data within the Managers' organization.
                    </p>

                    <Controller
                        name="declaration.consent_given"
                        control={control}
                        defaultValue={false}
                        render={({ field }) => (
                            <label className="flex items-start gap-3 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={field.value}
                                    onChange={(e) => field.onChange(e.target.checked)}
                                    className="w-5 h-5 mt-0.5 text-blue-600 focus:ring-blue-500 rounded"
                                />
                                <span className="text-gray-800 font-medium">
                                    I consent to the above terms and conditions
                                </span>
                            </label>
                        )}
                    />
                </div>

                {/* Signature Section */}
                <div className="grid grid-cols-3 gap-6">
                    <Controller
                        name="declaration.declaration_place"
                        control={control}
                        defaultValue=""
                        render={({ field }) => (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Place
                                </label>
                                <input
                                    {...field}
                                    type="text"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    placeholder="Enter place"
                                />
                            </div>
                        )}
                    />

                    <Controller
                        name="declaration.declaration_date"
                        control={control}
                        defaultValue=""
                        render={({ field }) => (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Date
                                </label>
                                <input
                                    {...field}
                                    type="date"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                />
                            </div>
                        )}
                    />

                    <Controller
                        name="declaration.signature"
                        control={control}
                        defaultValue=""
                        render={({ field }) => (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Signature
                                </label>
                                <input
                                    {...field}
                                    type="text"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    placeholder="Enter your name"
                                />
                            </div>
                        )}
                    />
                </div>
            </div>
        </div>
    );
}
