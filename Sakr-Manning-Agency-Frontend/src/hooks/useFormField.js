import { useFormContext } from "react-hook-form";

/**
 * Auto-detect react-hook-form and expose a unified interface.
 * Works for both native-registrable inputs (register) and custom inputs (setValue/watch).
 */
export function useFormField(name) {
  const form = useFormContext?.();
  if (!form || !name) return { inForm: false, error: null };

  const {
    register,
    watch,
    setValue,
    getValues,
    trigger,
    formState: { errors },
  } = form;

  return {
    inForm: true,
    register,
    setValue,
    trigger,
    getValues,
    value: watch(name) || getValues(name),
    error: errors?.[name]?.message ?? null,
  };
}

/** Utility for merging class strings */
export function cx(...args) {
  return args.filter(Boolean).join(" ");
}
