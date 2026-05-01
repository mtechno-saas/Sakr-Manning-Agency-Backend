import React, { useState } from "react";
import { useFormContext, useFieldArray } from "react-hook-form";
import { Plus } from "lucide-react";
import { Select } from "../inputs/Select";
import { BaseInput, SuggestionInput } from "../inputs/BaseInput";
import { PhoneInput } from "../inputs/PhoneInput";
import { EMERGENCY_RULES } from "../../../utils/RHFvalidationRules";
import { StepSaveButton } from "../layout/StepSaveButton";
import { FORM_FIELDS, RELATIONSHIP_OPTIONS } from "../../../config/formConfig";
import { NextOfKinModal } from "../modals/NextOfKinModal";
import { CrudTable } from "../layout/FormTable";

const POPULAR_COUNTRIES = [
  "United States",
  "Canada",
  "United Kingdom",
  "Australia",
  "Germany",
  "France",
  "India",
  "China",
  "Japan",
  "Brazil",
  "South Africa",
  "Egypt",
  "United Arab Emirates",
  "Saudi Arabia",
  "Turkey",
  "Italy",
  "Spain",
  "Netherlands",
  "Sweden",
  "Greece",
  "Russia",
];

export function EmergencyForm() {
  const { control, getValues } = useFormContext();

  /* ---------- Next of Kin (additional contacts) ---------- */
  const {
    fields: nokFields,
    append: appendNok,
    update: updateNok,
    remove: removeNok,
  } = useFieldArray({
    control,
    name: "next_of_kin",
  });

  const [isNokModalOpen, setIsNokModalOpen] = useState(false);
  const [editingNok, setEditingNok] = useState(null);
  const [editingNokIndex, setEditingNokIndex] = useState(null);

  const generateId = (prefix = "item") =>
    `${prefix}-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

  const handleAddNok = () => {
    setEditingNok(null);
    setIsNokModalOpen(true);
  };

  const handleEditNok = (nok) => {
    const index = nokFields.findIndex((f) => f.id === nok.id);
    setEditingNokIndex(index);
    const realData = getValues(`next_of_kin.${index}`);
    setEditingNok({ ...nok, _originalId: realData?.id || nok.id });
    setIsNokModalOpen(true);
  };

  const handleSaveNok = (nokData) => {
    if (editingNokIndex !== null) {
      updateNok(editingNokIndex, {
        ...nokData,
        id: editingNok._originalId,
      });
    } else {
      appendNok({
        ...nokData,
        id: generateId("nok"),
      });
    }
  };

  const handleDeleteNok = (id) => {
    if (!window.confirm("Are you sure you want to delete this emergency contact?")) {
      return;
    }
    const idx = nokFields.findIndex((f) => f.id === id);
    if (idx !== -1) removeNok(idx);
  };

  const handleCloseNokModal = () => {
    setIsNokModalOpen(false);
    setEditingNok(null);
    setEditingNokIndex(null);
  };

  const nokColumns = [
    { key: "full_name", label: "Full Name" },
    { key: "relationship", label: "Relationship" },
    { key: "address_country", label: "Address / Country" },
    { key: "phone", label: "Phone" },
    { key: "email", label: "Email" },
  ];

  return (
    <div className="w-full space-y-6">
      <StepSaveButton />
      {/* Primary Emergency Contact Section */}
      <div className="bg-white rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Next of Kin / Emergency Contact
        </h2>

        {/* Row 1: Full Name | Address */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <BaseInput
            name={FORM_FIELDS.EMERGENCY.FULL_NAME}
            placeholder="Enter Full Name"
            required
            variant="outlined"
            rules={EMERGENCY_RULES.kin_full_name}
          />
          <SuggestionInput
            name={FORM_FIELDS.EMERGENCY.ADDRESS}
            placeholder="Enter Address / Country"
            required
            variant="outlined"
            suggestions={POPULAR_COUNTRIES}
            rules={EMERGENCY_RULES.kin_address}
          />
        </div>

        {/* Row 2: Relationship | Phone | Email */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Select
            name={FORM_FIELDS.EMERGENCY.RELATIONSHIP}
            placeholder="Select Relationship"
            required
            options={RELATIONSHIP_OPTIONS}
            variant="outlined"
          />

          <PhoneInput
            name={FORM_FIELDS.EMERGENCY.PHONE}
            selectName={FORM_FIELDS.EMERGENCY.PHONE_CODE}
            placeholder="Mobile number"
            defaultCountry="EG"
            variant="outlined"
            required
            rules={EMERGENCY_RULES.kin_phone}
          />

          <BaseInput
            name={FORM_FIELDS.EMERGENCY.EMAIL}
            placeholder="Enter Email"
            type="email"
            // required
            variant="outlined"
          // rules={EMERGENCY_RULES.kin_email}
          />
        </div>
      </div>

      {/* Additional Emergency Contacts Section */}
      <div className="bg-[#E8F4FD] rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Additional Emergency Contacts
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Add more emergency contacts if needed
            </p>
          </div>
          <button
            type="button"
            onClick={handleAddNok}
            className="flex items-center gap-2 px-5 py-2.5 bg-[#CFDBEC] text-gray-800 rounded-lg hover:bg-[#b8c9de] transition-colors font-medium shadow-sm"
          >
            <Plus className="w-5 h-5" />
            Add Emergency Contact
          </button>
        </div>
      </div>

      {/* Additional Emergency Contacts Table */}
      {nokFields.length > 0 && (
        <CrudTable
          data={nokFields}
          columns={nokColumns}
          onEdit={handleEditNok}
          onDelete={handleDeleteNok}
          emptyMessage="No additional emergency contacts yet."
          showAttachment={false}
        />
      )}

      {/* Next of Kin Modal */}
      <NextOfKinModal
        isOpen={isNokModalOpen}
        onClose={handleCloseNokModal}
        onSave={handleSaveNok}
        initialData={editingNok}
      />
    </div>
  );
}