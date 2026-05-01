import Button from "../../common/Button";

export function FormNavigation({
  currentStep,
  totalSteps,
  onNext,
  onBack,
  onSubmit,
  isLoading,
}) {
  return (
    <div className="flex justify-end items-center gap-4 mt-8 pt-6 border-t border-gray-200">
      {currentStep > 0 && (
        <Button
          type="button"
          onClick={onBack}
          variant="outlined"
          className="px-8 py-2.5"
          disabled={isLoading}
        >
          Back
        </Button>
      )}

      {currentStep < totalSteps - 1 ? (
        <Button
          type="button"
          onClick={onNext}
          variant="primary"
          className="px-8 py-2.5 min-w-[120px]"
          disabled={isLoading}
        >
          Next
        </Button>
      ) : (
        <Button
          type="button"
          onClick={onSubmit}
          variant="primary"
          className="px-8 py-2.5 min-w-[120px]"
          loading={isLoading}
          disabled={isLoading}
        >
          Save
        </Button>
      )}
    </div>
  );
}