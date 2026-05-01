import { useState, useCallback, useEffect, useMemo } from "react";
import { useForm, FormProvider } from "react-hook-form";
import { ASSETS } from "../../utils/constants";
import { Sidebar } from "./layout/Sidebar";
import { FormNavigation } from "./layout/FormNavigation";
import { useUserForm } from "../../hooks/useUserForm";
import { useReferenceData } from "../../hooks/useReferenceData";
import { cleanDraftFields, validateNoDrafts } from "../../utils/draftUtils";
import { useSaveLock } from "../../hooks/useSaveLock";
import { ReferenceDataProvider } from "../../context/ReferenceDataContext";
import { ToastProvider, useToast } from "../../context/ToastContext";

import { FormSaveProvider } from "../../context/FormSaveContext";

// Import form components
import { PositionPersonalForm } from "./steps/PositionPersonalForm";
import { EducationForm } from "./steps/EducationForm";
import { ContactForm } from "./steps/ContactForm";
import { EmergencyForm } from "./steps/EmergencyForm";
import { DocumentsForm } from "./steps/DocumentsForm";
import { CertificatesForm } from "./steps/CertificatesForm";
import { HealthForm } from "./steps/HealthForm";
import { CoursesForm } from "./steps/CoursesForm";
import { SeaServiceForm } from "./steps/SeaServiceForm";
import { ReferencesForm } from "./steps/ReferencesForm"; // NEW
import { DeclarationForm } from "./steps/DeclarationForm"; // NEW
import { SubmitForm } from "./steps/SubmitForm";
import { FORM_FIELDS } from "../../config/formConfig";

const steps = [
  { label: "Position & Personal", icon: ASSETS.ICONS, component: PositionPersonalForm },
  { label: "Education", icon: ASSETS.ICONS, component: EducationForm },
  { label: "Contact", icon: ASSETS.ICONS, component: ContactForm },
  { label: "Emergency", icon: ASSETS.ICONS, component: EmergencyForm },
  { label: "Documents", icon: ASSETS.ICONS, component: DocumentsForm },
  { label: "Certificates", icon: ASSETS.ICONS, component: CertificatesForm },
  { label: "Health & Marine", icon: ASSETS.ICONS, component: HealthForm },
  { label: "Courses", icon: ASSETS.ICONS, component: CoursesForm },
  { label: "Sea Service", icon: ASSETS.ICONS, component: SeaServiceForm },
  { label: "References", icon: ASSETS.ICONS, component: ReferencesForm }, // NEW - Step 10
  { label: "Declaration", icon: ASSETS.ICONS, component: DeclarationForm }, // NEW - Step 11
  { label: "Submit", icon: ASSETS.ICONS, component: SubmitForm },
];

export default function SakrForm({ userId, onLogout }) {
  return (
    <ToastProvider>
      <SakrFormInner userId={userId} onLogout={onLogout} />
    </ToastProvider>
  );
}

function SakrFormInner({ userId, onLogout }) {
  const { notify } = useToast();
  const methods = useForm({
    mode: "onChange",
    defaultValues: {
      documents: [],
      certificates: [],
      health: [],
      courses: [],
      seaServices: [],
      workExperiences: [],
      references: [], // NEW
      declaration: {  // NEW - Single object
        has_disease: false,
        disease_details: "",
        has_accident: false,
        accident_details: "",
        has_psychiatric_treatment: false,
        psychiatric_treatment_details: "",
        has_addiction: false,
        addiction_details: "",
        consent_given: false,
        declaration_place: "",
        declaration_date: "",
        signature: "",
      },
    },
  });

  const {
    isLoading: isLoadingBackend,
    isSaving,
    isSubmitting: isSubmittingBackend,
    error: backendError,
    lastSaved,
    loadFormData,
    saveFormData,
    submitForm,
    startAutoSave,
    stopAutoSave,
  } = useUserForm({
    autoSaveInterval: 300000, // 5 min
    enableAutoSave: true,
  });

  const {
    data: referenceData,
    isLoading: isLoadingReference,
    loadReferenceData,
  } = useReferenceData({
    loadOnMount: true,
  });

  const { isLocked: isSaveLocked, withLock } = useSaveLock();

  const [step, setStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  const CurrentForm = steps[step].component;

  const goToStep = (index) => {
    if (index >= 0 && index < steps.length) {
      setStep(index);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  // Get user profile data for sidebar
  const userProfile = {
    photo: methods.watch(FORM_FIELDS.PERSONAL.PHOTO),
    name: methods.watch(FORM_FIELDS.PERSONAL.FULL_NAME),
    position: methods.watch(FORM_FIELDS.POSITION.APPLICATION),
    availableDate: methods.watch(FORM_FIELDS.POSITION.AVAILABLE_DATE),
    expectedSalary: methods.watch(FORM_FIELDS.POSITION.EXPECTED_SALARY),
    expectedSalaryCurrency: methods.watch(FORM_FIELDS.POSITION.EXPECTED_SALARY_CURRENCY),
    email: methods.watch(FORM_FIELDS.CONTACT.EMAIL),
    registerId: methods.watch(FORM_FIELDS.POSITION.REGISTER_CODE),
    mobile: methods.watch("mobile"),
  }

  // Initialize form data on mount
  useEffect(() => {
    const initializeForm = async () => {
      try {
        await loadReferenceData();

        const result = await loadFormData();

        if (result?.success && result?.data) {
          methods.reset({
            ...result.data,
            documents: result.data.documents || [],
            certificates: result.data.certificates || [],
            health: result.data.health || [],
            courses: result.data.courses || [],
            seaServices: result.data.seaServices || [],
            workExperiences: result.data.workExperiences || [],
            references: result.data.references || [], // NEW
            declaration: result.data.declaration || { // NEW
              has_disease: false,
              disease_details: "",
              has_accident: false,
              accident_details: "",
              has_psychiatric_treatment: false,
              psychiatric_treatment_details: "",
              has_addiction: false,
              addiction_details: "",
              consent_given: false,
              declaration_place: "",
              declaration_date: "",
              signature: "",
            },
          });
        } else {
          methods.reset({
            documents: [],
            certificates: [],
            health: [],
            courses: [],
            seaServices: [],
            workExperiences: [],
            references: [], // NEW
            declaration: { // NEW
              has_disease: false,
              disease_details: "",
              has_accident: false,
              accident_details: "",
              has_psychiatric_treatment: false,
              psychiatric_treatment_details: "",
              has_addiction: false,
              addiction_details: "",
              consent_given: false,
              declaration_place: "",
              declaration_date: "",
              signature: "",
            },
          });
        }

        setIsInitialized(true);
      } catch (err) {
        console.error("Failed to initialize form:", err);
        notify.error("Failed to load form data");

        methods.reset({
          documents: [],
          certificates: [],
          health: [],
          courses: [],
          seaServices: [],
          workExperiences: [],
          references: [], // NEW
          declaration: { // NEW
            has_disease: false,
            disease_details: "",
            has_accident: false,
            accident_details: "",
            has_psychiatric_treatment: false,
            psychiatric_treatment_details: "",
            has_addiction: false,
            addiction_details: "",
            consent_given: false,
            declaration_place: "",
            declaration_date: "",
            signature: "",
          },
        });
        setIsInitialized(true);
      }
    };

    if (userId) {
      initializeForm();
    }
  }, [userId, loadFormData, loadReferenceData, methods]);

  // Auto-save with draft cleanup
  useEffect(() => {
    if (!isInitialized) return;

    const getLiveValues = () => {
      const values = methods.getValues();
      return cleanDraftFields(values);
    };

    startAutoSave(getLiveValues, () => step);

    return () => stopAutoSave();
  }, [isInitialized, methods, startAutoSave, step, stopAutoSave]);

  useEffect(() => {
    if (backendError) {
      notify.error(backendError);
    }
  }, [backendError]);

  const onNext = async () => {
    const isValid = await methods.trigger();
    if (!isValid && step < 4) {
      notify.error("Please fix validation errors before continuing.");
      return;
    }

    if (step < steps.length - 1) {
      setStep((s) => s + 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const onBack = () => {
    if (step > 0) {
      setStep((s) => s - 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handleStepChange = (newStep) => {
    setStep(newStep);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleManualSave = async () => {
    if (isSaveLocked) {
      notify.info("Save in progress, please wait...");
      return;
    }

    const result = await withLock(async () => {
      const formData = methods.getValues();
      const cleanData = cleanDraftFields(formData);

      if (!validateNoDrafts(cleanData)) {
        console.error("Draft validation failed!");
        return { success: false, message: "Invalid data structure" };
      }

      return await saveFormData(cleanData, step);
    }, "manual-save");

    if (result.success) {
      notify.success("Progress saved successfully!");

      // Surface sync errors as warnings
      if (result.syncErrors?.length > 0) {
        const unique = [...new Set(result.syncErrors)];
        unique.forEach((err) => notify.warning(err));
      }

      if (result.data) {
        const currentFormData = methods.getValues();
        const mergedData = {
          ...currentFormData,
          ...result.data,
          documents: result.data.documents || currentFormData.documents || [],
          certificates: result.data.certificates || currentFormData.certificates || [],
          health: result.data.health || currentFormData.health || [],
          courses: result.data.courses || currentFormData.courses || [],
          seaServices: result.data.seaServices || currentFormData.seaServices || [],
          workExperiences: result.data.workExperiences || currentFormData.workExperiences || [],
          references: result.data.references || currentFormData.references || [],
          declaration: result.data.declaration || currentFormData.declaration,
        };
        methods.reset(mergedData);
      }
    } else {
      notify.error(result.message || "Save failed");
    }
  };

  const onSubmit = async (data) => {
    if (isSaveLocked) {
      notify.info("Please wait for current save to complete...");
      return;
    }

    setIsSubmitting(true);

    try {
      const cleanData = cleanDraftFields(data);

      if (!validateNoDrafts(cleanData)) {
        notify.error("Please complete any draft entries first.");
        setIsSubmitting(false);
        return;
      }

      const result = await withLock(async () => {
        return await saveFormData(cleanData, step);
      }, "submit-save");

      if (result.success) {
        if (result.data) {
          const currentFormData = methods.getValues();
          const mergedData = {
            ...currentFormData,
            ...result.data,
            documents: result.data.documents || currentFormData.documents || [],
            certificates: result.data.certificates || currentFormData.certificates || [],
            health: result.data.health || currentFormData.health || [],
            courses: result.data.courses || currentFormData.courses || [],
            seaServices: result.data.seaServices || currentFormData.seaServices || [],
            workExperiences: result.data.workExperiences || currentFormData.workExperiences || [],
            references: result.data.references || currentFormData.references || [],
            declaration: result.data.declaration || currentFormData.declaration,
          };
          methods.reset(mergedData);
        }

        notify.success("Profile saved successfully!");

        // Surface sync errors as warnings
        if (result.syncErrors?.length > 0) {
          const unique = [...new Set(result.syncErrors)];
          unique.forEach((err) => notify.warning(err));
        }
      } else {
        notify.error(result.message || "Save failed");
      }
    } catch (error) {
      console.error("Save error:", error);
      notify.error(error.message || "Save failed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleLogout = () => {
    console.log("Logout clicked");
  };

  if (!isInitialized || isLoadingBackend) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your form data...</p>
        </div>
      </div>
    );
  }

  // Handle image change from sidebar
  const handleImageChange = (file) => {
    if (file) {
      methods.setValue(FORM_FIELDS.PERSONAL.PHOTO, file, { shouldDirty: true });
    } else {
      methods.setValue(FORM_FIELDS.PERSONAL.PHOTO, null, { shouldDirty: true });
    }
  };

  return (
    <ReferenceDataProvider data={referenceData} isLoading={isLoadingReference}>
      <FormProvider {...methods}>
        <FormSaveProvider
          userId={userId}
          currentStep={step}
          onStepChange={handleStepChange}
        >
          <div className="flex flex-col h-full w-full bg-gray-200 pb-2">
            {/* Minimal Fixed Header */}
            <div className="fixed top-0 left-0 right-0 bg-white shadow-sm z-40 px-12 py-3 flex items-center gap-4">
              <img src={ASSETS.LOGO} alt="Sakr Logo" className="w-10 h-10 object-contain" />
              <h1 className="text-lg font-bold text-gray-900">SAKR MANNING AGENCY</h1>
            </div>

            {/* Main Layout with padding for fixed header */}
            <div className="flex flex-1 pt-20 px-12">

              {/* Left Sidebar */}
              <Sidebar
                steps={steps}
                currentStep={step}
                goToStep={goToStep}
                userProfile={userProfile}
                onLogout={onLogout || handleLogout}
                onImageChange={handleImageChange}
              />

              {/* Main Content Area */}
              <div className="flex-1 overflow-hidden w-fit-content">
                <div className="w-full max-w-[1440px] ml-4 lg:ml-8 px-4 pr-8 rounded-lg">
                  {/* Current Form Step */}
                  <CurrentForm />

                  {/* Navigation Buttons */}
                  <FormNavigation
                    currentStep={step}
                    totalSteps={steps.length}
                    onNext={onNext}
                    onBack={onBack}
                    onSubmit={methods.handleSubmit(onSubmit)}
                    isLoading={isSubmitting || isSubmittingBackend || isSaveLocked}
                  />
                </div>
              </div>
            </div>
          </div>
        </FormSaveProvider>
      </FormProvider>
    </ReferenceDataProvider>
  );
}