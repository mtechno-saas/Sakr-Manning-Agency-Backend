import React from "react";
import { BaseInput, SuggestionInput } from "../inputs/BaseInput";
import { PhoneInput } from "../inputs/PhoneInput";
import { CONTACT_RULES } from "../../../utils/RHFvalidationRules";
import { StepSaveButton } from "../layout/StepSaveButton";
import { FORM_FIELDS, POPULAR_COUNTRIES } from "../../../config/formConfig";

export function ContactForm() {
  return (
    <div className="w-full space-y-6">
      <StepSaveButton />
      {/* Contact Details Section */}
      <div className="bg-white rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Contact Details
        </h2>

        {/* Row 1: Address | Country | City */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <BaseInput
            name={FORM_FIELDS.CONTACT.ADDRESS}
            placeholder="Enter your full home address"
            required
            variant="outlined"
            rules={CONTACT_RULES.home_address}
          />
          <SuggestionInput
            name={FORM_FIELDS.CONTACT.COUNTRY}
            placeholder="Enter your Country"
            required
            variant="outlined"
            suggestions={POPULAR_COUNTRIES}
          />
          <BaseInput
            name={FORM_FIELDS.CONTACT.CITY}
            placeholder="Enter your city"
            required
            variant="outlined"
          />
        </div>

        {/* Row 2: Email | Mobile | Mobile 2 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <BaseInput
            name={FORM_FIELDS.CONTACT.EMAIL}
            placeholder="Enter your email address"
            type="email"
            required
            variant="outlined"
            rules={CONTACT_RULES.email}
          />

          <PhoneInput
            name={FORM_FIELDS.CONTACT.MOBILE}
            selectName={FORM_FIELDS.CONTACT.MOBILE_CODE}
            placeholder="Mobile number"
            defaultCountry="EG"
            variant="outlined"
            required
            rules={CONTACT_RULES.mobile}
          />

          <PhoneInput
            name={FORM_FIELDS.CONTACT.MOBILE_2}
            selectName={FORM_FIELDS.CONTACT.MOBILE_2_CODE}
            placeholder="Second mobile (optional)"
            defaultCountry="EG"
            variant="outlined"
          />
        </div>
      </div>
    </div>
  );
}