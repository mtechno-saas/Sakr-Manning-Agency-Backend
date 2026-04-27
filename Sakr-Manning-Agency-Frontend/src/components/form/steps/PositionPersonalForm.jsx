import React from "react";
import { useFormContext } from "react-hook-form";
import { BaseInput, SuggestionInput } from "../inputs/BaseInput";
import { Select } from "../inputs/Select";
import { TextDateInput } from "../inputs/DateInput";
import { ImageUpload } from "../inputs/ImageUpload";
import { FormSection } from "../inputs/FormSection";
import { POSITION_PERSONAL_RULES } from "../../../utils/RHFvalidationRules";
import { StepSaveButton } from "../layout/StepSaveButton";
import { FORM_FIELDS, BLOOD_TYPE_OPTIONS, VISA_STATUS_OPTIONS, POPULAR_NATIONALITIES } from "../../../config/formConfig";
import { useReferenceDataContext } from "../../../context/ReferenceDataContext";

const CURRENCY_OPTIONS = [
  { value: "USD", label: "USD" },
  { value: "EUR", label: "EUR" },
  { value: "EGP", label: "EGP" },
];

/* ------------------ Options Data ------------------ */
const OTHER_POSITION_OPTIONS = [
  { value: "radio_officer", label: "Radio Officer" },
  { value: "purser", label: "Purser" },
  { value: "cadet", label: "Cadet" },
  { value: "trainee", label: "Trainee" },
  { value: "other", label: "Other" },
];

const MARITAL_STATUS_OPTIONS = [
  { value: "single", label: "Single" },
  { value: "married", label: "Married" },
  { value: "divorced", label: "Divorced" },
  { value: "widowed", label: "Widowed" },
];

const CLOTHING_SIZE_OPTIONS = [
  { value: "S", label: "S" },
  { value: "M", label: "M" },
  { value: "L", label: "L" },
  { value: "XL", label: "XL" },
  { value: "XXL", label: "XXL" },
  { value: "XXXL", label: "XXXL" },
];

const SHOE_SIZE_OPTIONS = Array.from({ length: 10 }, (_, i) => {
  const size = (38 + i).toString();
  return { value: size, label: size };
});


/* ------------------ Component ------------------ */
export function PositionPersonalForm() {
  const { register, watch } = useFormContext();
  const refData = useReferenceDataContext();
  const positionOptions = refData?.positions || [];

  return (
    <div className="w-full space-y-8">
      <StepSaveButton />

      <div className="bg-white rounded-lg p-6">
        {/* Position Information Section */}
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Position Information
        </h2>
        <div className="mb-6">
          <Select
            name={FORM_FIELDS.POSITION.APPLICATION}
            placeholder="Application For Position as"
            options={positionOptions}
            required
            searchable
            variant="outlined"
            rules={POSITION_PERSONAL_RULES.application_for_position}
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

          <BaseInput
            name={FORM_FIELDS.POSITION.OTHER}
            placeholder="Other Position (If Any)"
            variant="outlined"
          />

          <TextDateInput
            name={FORM_FIELDS.POSITION.AVAILABLE_DATE}
            placeholder="Available Date (DD-MM-YYYY)"
            required
            variant="outlined"
            rules={{
              required: "Available date is required",
              validate: (isoVal) => {
                if (!isoVal) return "Available date is required";
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                const maxDate = new Date(today);
                maxDate.setDate(today.getDate() + 180);
                const selected = new Date(isoVal);
                selected.setHours(0, 0, 0, 0);
                if (selected < today) return "Date cannot be in the past";
                // if (selected > maxDate) return "Date must be within 6 months from today";
                return true;
              },
            }}
          />
          <div className="flex gap-2 items-start">
            <div className="flex-1">
              <BaseInput
                name={FORM_FIELDS.POSITION.EXPECTED_SALARY}
                placeholder="Expected Salary"
                type="number"
                required
                variant="outlined"
                rules={POSITION_PERSONAL_RULES.expected_salary}
              />
            </div>
            <div className="w-[100px] pt-[1px]">
              <Select
                name={FORM_FIELDS.POSITION.EXPECTED_SALARY_CURRENCY}
                options={CURRENCY_OPTIONS}
                placeholder="Curr."
                variant="outlined"
              />
            </div>
          </div>
        </div>

        {/* Personal Details Section */}
        <h2 className="text-xl font-semibold text-gray-900 mb-6 mt-6">
          PERSONAL DETAILS
        </h2>

        {/* Full Name - Full Width */}
        <div className="mb-6">
          <BaseInput
            name={FORM_FIELDS.PERSONAL.FULL_NAME}
            placeholder="Enter your full name as in Passport"
            required
            variant="outlined"
            rules={POSITION_PERSONAL_RULES.full_name}
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <SuggestionInput
            name={FORM_FIELDS.PERSONAL.NATIONALITY}
            placeholder="Enter your Nationality"
            required
            variant="outlined"
            suggestions={POPULAR_NATIONALITIES}
            rules={POSITION_PERSONAL_RULES.nationality}
          />
          <SuggestionInput
            name={FORM_FIELDS.PERSONAL.PLACE_OF_BIRTH}
            placeholder="Enter your Place of Birth"
            required
            variant="outlined"
            suggestions={POPULAR_NATIONALITIES}
            rules={POSITION_PERSONAL_RULES.place_of_birth}
          />
        </div>

        {/* 3-Column Grid for Personal Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <TextDateInput
            name={FORM_FIELDS.PERSONAL.DATE_OF_BIRTH}
            placeholder="Enter your birth date (DD/MM/YYYY)"
            required
            variant="outlined"
            rules={POSITION_PERSONAL_RULES.date_of_birth}
          />
          <BaseInput
            name={FORM_FIELDS.PERSONAL.NEAREST_PORT}
            placeholder="Enter your Nearest Air Port"
            required
            variant="outlined"
            rules={POSITION_PERSONAL_RULES.nearest_port}
          />
          <Select
            name={FORM_FIELDS.PERSONAL.MARITAL_STATUS}
            options={MARITAL_STATUS_OPTIONS}
            placeholder="Enter your Marital Status"
            required
            searchable
            variant="outlined"
            rules={POSITION_PERSONAL_RULES.marital_status}
          />

          <BaseInput
            name={FORM_FIELDS.PERSONAL.WEIGHT}
            placeholder="Enter your Weight (Kg)"
            type="number"
            required
            variant="outlined"
            rules={POSITION_PERSONAL_RULES.weight}
          />

          <BaseInput
            name={FORM_FIELDS.PERSONAL.HEIGHT}
            placeholder="Enter your Height (Cm)"
            type="number"
            required
            variant="outlined"
            rules={POSITION_PERSONAL_RULES.height}
          />
          <Select
            name={FORM_FIELDS.PERSONAL.OVERALL_SIZE}
            placeholder="Overall Size"
            options={CLOTHING_SIZE_OPTIONS}
            required
            variant="outlined"
            rules={POSITION_PERSONAL_RULES.overall_size}
          />
          <Select
            name={FORM_FIELDS.PERSONAL.SHIRT_SIZE}
            placeholder="T-Shirt Size"
            options={CLOTHING_SIZE_OPTIONS}
            required
            variant="outlined"
          />
          <BaseInput
            name={FORM_FIELDS.PERSONAL.TROUSER_SIZE}
            placeholder="Enter your Trouser Size"
            required
            variant="outlined"
          // rules={POSITION_PERSONAL_RULES.trouser_size}
          />
          <BaseInput
            name={FORM_FIELDS.PERSONAL.SHOES_SIZE}
            placeholder="Enter your Shoes Size"
            required
            variant="outlined"
          // rules={POSITION_PERSONAL_RULES.shoes_size}
          />
        </div>
      </div>
    </div>
  );
}