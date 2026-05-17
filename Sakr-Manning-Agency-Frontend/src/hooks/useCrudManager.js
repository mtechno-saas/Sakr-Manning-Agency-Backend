import React, { useState, useCallback, useEffect } from "react";
/**
 * useCrudManager
 *
 * Centralised CRUD manager for collection-like form sections.
 * Integrates with react-hook-form (expects `form` from useFormContext()).
 *
 * Options:
 *  - form: react-hook-form context (required to auto-sync)
 *  - fields: array of field names that belong to the item (e.g. ['documentType', 'documentNo'])
 *  - idPrefix: string for generated ids
 *  - transformOnSave: (values) => object // optional transform before saving/adding
 *  - confirmDelete: (item) => boolean // optional custom delete confirmation
 *  - parentFieldName: string|null // if provided, hook will persist items -> form.setValue(parentFieldName, items)
 *  - registerField: boolean // if true (default) the hook will attempt to register the parent field
 */
export function useCrudManager({
  form,
  fields = [],
  idPrefix = "item",
  transformOnSave,
  confirmDelete,
  parentFieldName = null,
  registerField = true,
}) {
  const generateId = useCallback(
    () => `${idPrefix}-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
    [idPrefix]
  );

  // initialise items from parent field if available
  const [items, setItems] = useState(() => {
    try {
      if (form && parentFieldName) {
        const initial = form.getValues(parentFieldName);
        if (Array.isArray(initial)) {
          // ensure each item has an id
          return initial.map((it) =>
            it && it.id ? it : { ...it, id: generateId() }
          );
        }
      }
    } catch {
      return [];
    }
    return [];
  });

  const [editingId, setEditingId] = useState(null);

  // auto-register the parent field (safe-guard)
  useEffect(() => {
    if (!form || !parentFieldName || !registerField) return;
    try {
      // register as a field so RHF knows about it (useful for default values & submission)
      if (typeof form.register === "function") {
        form.register(parentFieldName);
      }
    } catch {
      return;
    }
  }, [form, parentFieldName, registerField]);

  // persist to parent form field when items change
  useEffect(() => {
    if (!form || !parentFieldName) return;
    try {
      form.setValue(parentFieldName, items, {
        shouldDirty: true,
        shouldValidate: true,
      });
    } catch {
      return;
    }
  }, [items, form, parentFieldName]);

  const clearForm = useCallback(() => {
    if (!form) return;
    const resetValues = fields.reduce((acc, f) => {
      acc[f] = "";
      return acc;
    }, {});
    form.reset(resetValues);
  }, [form, fields]);

  const validateRequired = useCallback(
    (values) => {
      for (let name of fields) {
        // fields array only lists keys; if you want required info add validation upstream in RHF rules
        // here we simply ensure not empty strings for the keys that exist in the form
        const val = values[name];
        if (val === undefined || val === null || String(val).trim() === "") {
          // we don't throw here to keep this generic; caller can add stricter behaviour
          return {
            ok: false,
            message: `Please fill ${name}`,
            missingField: name,
          };
        }
      }
      return { ok: true };
    },
    [fields]
  );

  const buildItemFromValues = useCallback(
    (values) => {
      const item = fields.reduce((acc, name) => {
        acc[name] = values[name];
        return acc;
      }, {});
      return transformOnSave ? transformOnSave(item) : item;
    },
    [fields, transformOnSave]
  );

  const add = useCallback(() => {
    if (!form) return;
    const values = form.getValues();
    // lightweight validation: only check fields that were passed to the hook
    const v = validateRequired(values);
    if (!v.ok) {
      // keep behaviour compatible with your previous code
      alert(v.message);
      return;
    }

    const newItem = { id: generateId(), ...buildItemFromValues(values) };
    setItems((prev) => [...prev, newItem]);
    clearForm();
  }, [form, validateRequired, generateId, buildItemFromValues, clearForm]);

  const edit = useCallback(
    (item) => {
      if (!form) return;
      setEditingId(item.id);
      fields.forEach((name) => form.setValue(name, item[name] ?? ""));
    },
    [form, fields]
  );

  const save = useCallback(() => {
    if (!form || !editingId) return;
    const values = form.getValues();
    const v = validateRequired(values);
    if (!v.ok) {
      alert(v.message);
      return;
    }
    const updated = buildItemFromValues(values);
    setItems((prev) =>
      prev.map((it) => (it.id === editingId ? { ...it, ...updated } : it))
    );
    setEditingId(null);
    clearForm();
  }, [form, editingId, validateRequired, buildItemFromValues, clearForm]);

  const cancel = useCallback(() => {
    setEditingId(null);
    clearForm();
  }, [clearForm]);

  const remove = useCallback(
    (itemId) => {
      const item = items.find((i) => i.id === itemId);
      const confirmed =
        typeof confirmDelete === "function"
          ? confirmDelete(item)
          : window.confirm("Are you sure you want to delete this item?");
      if (!confirmed) return;
      setItems((prev) => prev.filter((it) => it.id !== itemId));
      if (editingId === itemId) {
        setEditingId(null);
        clearForm();
      }
    },
    [items, confirmDelete, editingId, clearForm]
  );

  return {
    items,
    setItems,
    editingId,
    setEditingId,
    handlers: {
      add,
      edit,
      save,
      cancel,
      delete: remove,
      clearForm,
    },
  };
}
