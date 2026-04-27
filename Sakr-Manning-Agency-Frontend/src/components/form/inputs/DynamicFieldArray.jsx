import React, { useState, useCallback, useEffect } from "react";
import { useFormContext, useFieldArray } from "react-hook-form";
import {
  ChevronDown,
  ChevronUp,
  X,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { BaseInput } from "./BaseInput";
import { TextArea } from "./TextArea";
import { Select } from "./Select";
import { DateInput } from "./DateInput";
// --- VARIANTS ---
// Block 3 base styling + Block 2 extended design options
const variants = {
  plain: `
    h-auto bg-transparent p-14 px-6 py-14
  `,
  spacious: `
    h-auto bg-transparent flex flex-col gap-6 text-start px-6 py-14
  `,
  card: `
    h-auto bg-white
    shadow-[0px_11px_13.2px_rgba(0,0,0,0.1)]
    rounded-xl md:rounded-[15px]
    md:p-10 px-6 py-14
  `,
  gradient: `
    flex flex-col gap-2
    w-full h-auto
    bg-gradient-to-r from-[#DBE9F5] to-[#AFD1EE]
    px-6 pt-2 pb-7
    text-center
    rounded-[15px]
    font-[Poppins,Inter,system-ui,sans-serif]
    antialiased
    leading-relaxed
    
  `,
  compact: `
    h-auto flex flex-col gap-2 bg-transparent px-6 py-14
  `,
  default: `
    h-auto bg-white border border-gray-200
    rounded-xl p-6 md:p-8 text-start mb-10 px-6 py-14
  `,

  // --- NEW variants (from Block 2 high design) ---
  badge: `
    bg-white border border-gray-200 rounded-xl
    shadow-sm hover:shadow-md transition-shadow
    p-4 md:p-6
  `,
  highlight: `
    bg-gradient-to-r from-blue-50 to-indigo-100
    border border-blue-200
    rounded-xl p-6 shadow-md
  `,
};

export function DynamicFieldArray({
  name,
  fieldsConfig = [],
  title,
  subtitle = title,
  className = "",
  variant = "default",
  maxItems = 10,
  itemsPerPage = 1,
}) {
  const {
    control,
    formState: { errors },
  } = useFormContext();

  const { fields, append, remove } = useFieldArray({ control, name });

  // State
  const [currentPage, setCurrentPage] = useState(0);
  const [collapsedItems, setCollapsedItems] = useState(new Set());

  // Pagination logic
  const totalPages = Math.ceil(fields.length / itemsPerPage);
  const startIndex = currentPage * itemsPerPage;
  const endIndex = Math.min(startIndex + itemsPerPage, fields.length);
  const visibleFields = fields.slice(startIndex, endIndex);

  // Collapse toggle
  const toggleCollapse = (itemIndex) => {
    const actualIndex = startIndex + itemIndex;
    setCollapsedItems((prev) => {
      const newCollapsed = new Set(prev);
      newCollapsed.has(actualIndex)
        ? newCollapsed.delete(actualIndex)
        : newCollapsed.add(actualIndex);
      return newCollapsed;
    });
  };
  // Render field item
  const renderItem = (cfg, index) => {
    const fieldName = `${name}.${index}.${cfg.name}`;
    const error = errors?.[name]?.[index]?.[cfg.name]?.message;

    const common = {
      name: fieldName,
      label: cfg.label,
      required: cfg.required,
      placeholder: cfg.placeholder,
      rules: cfg.rules,
      variant: cfg.variant ?? "default",
      error,
      ...(cfg.props || {}),
    };

    if (typeof cfg.component === "function") {
      const Comp = cfg.component;
      return <Comp key={cfg.name} {...common} />;
    }

    switch (cfg.component) {
      case "textarea":
        return <TextArea key={cfg.name} rows={cfg.rows ?? 4} {...common} />;
      case "select":
        return (
          <Select
            key={cfg.name}
            options={cfg.options ?? []}
            searchable
            required={cfg.required}
            {...common}
          />
        );
      case "date":
        return <DateInput key={cfg.name} required={cfg.required} {...common} />;
      case "input":
      default:
        return (
          <BaseInput
            key={cfg.name}
            type={cfg.type ?? "text"}
            required={cfg.required}
            rules={cfg.rules}
            {...common}
          />
        );
    }
  };

  // Default values for new item
  const defaultsFromConfig = useCallback(
    () => fieldsConfig.reduce((acc, cfg) => ({ ...acc, [cfg.name]: "" }), {}),
    [fieldsConfig]
  );

  // Ensure at least 1 item
  useEffect(() => {
    if (fields.length === 0) {
      append(defaultsFromConfig());
    }
  }, [fields, append, defaultsFromConfig]);

  return (
    <div className="space-y-6 flex flex-col justify-center">
      {/* Items with pagination */}
      {visibleFields.map((field, itemIndex) => {
        const actualIndex = startIndex + itemIndex;
        const isCollapsed = collapsedItems.has(actualIndex);

        return (
          <div
            key={field.id}
            className={`rounded-xl relative ${className} ${variants[variant]}`}
          >
            {title && (
              <h1 className="text-2xl font-semibold text-center font-poppins text-[#0065AF]">
                {title}
              </h1>
            )}
            {/* Header */}
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-800 text-sm">
                {subtitle
                  ? `${subtitle} #${actualIndex + 1}`
                  : `Item #${actualIndex + 1}`}
              </h4>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => toggleCollapse(itemIndex)}
                  className="p-1.5 hover:bg-gray-100 rounded-full transition-colors"
                  aria-label={isCollapsed ? "Expand item" : "Collapse item"}
                >
                  {isCollapsed ? (
                    <ChevronDown className="w-4 h-4 text-gray-600" />
                  ) : (
                    <ChevronUp className="w-4 h-4 text-gray-600" />
                  )}
                </button>
                {fields.length > 1 && (
                  <button
                    type="button"
                    aria-label="Remove group"
                    onClick={() => {
                      remove(actualIndex);
                      if (visibleFields.length === 1 && currentPage > 0) {
                        setCurrentPage(currentPage - 1);
                      }
                    }}
                    className="p-1.5 bg-red-500 hover:bg-red-600 text-white rounded-full text-xs"
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </div>
            </div>

            {/* Content */}
            {!isCollapsed && (
              <div className="grid grid-cols-2 gap-x-12 gap-y-6">
                {fieldsConfig.map((cfg) => (
                  <div
                    key={cfg.name}
                    className={`space-y-1 ${
                      cfg.variant === "full" ? "col-span-2" : " "
                    }`}
                  >
                    {renderItem(cfg, actualIndex)}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 py-1">
          <button
            type="button"
            disabled={currentPage === 0}
            onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
            className="p-2 border border-gray-300 rounded-full disabled:opacity-50 flex items-center justify-center"
          >
            <ChevronLeft className="w-5 h-5 text-gray-700" />
          </button>

          <div className="flex gap-1">
            {Array.from({ length: Math.min(totalPages, 5) }).map((_, i) => {
              let pageNum = i;
              if (totalPages > 5) {
                if (currentPage < 3) pageNum = i;
                else if (currentPage > totalPages - 3)
                  pageNum = totalPages - 5 + i;
                else pageNum = currentPage - 2 + i;
              }
              return (
                <button
                  key={pageNum}
                  type="button"
                  onClick={() => setCurrentPage(pageNum)}
                  className={`w-8 h-8 text-sm rounded ${
                    currentPage === pageNum
                      ? "bg-[#1976D2] text-white"
                      : "border border-gray-300 hover:bg-gray-50"
                  }`}
                >
                  {pageNum + 1}
                </button>
              );
            })}
          </div>

          <button
            type="button"
            disabled={currentPage >= totalPages - 1}
            onClick={() =>
              setCurrentPage(Math.min(totalPages - 1, currentPage + 1))
            }
            className="p-2 border border-gray-300 rounded-full disabled:opacity-50 flex items-center justify-center"
          >
            <ChevronRight className="w-5 h-5 text-gray-700" />
          </button>
        </div>
      )}

      {/* Add button */}
      <div className="flex items-center justify-center">
        <button
          type="button"
          onClick={() => {
            if (fields.length >= maxItems) {
              alert(`Maximum ${maxItems} items allowed`);
              return;
            }
            append(defaultsFromConfig());
            const newPage = Math.floor(fields.length / itemsPerPage);
            if (newPage !== currentPage) {
              setCurrentPage(newPage);
            }
          }}
          disabled={fields.length >= maxItems}
          className="px-6 py-2 bg-[#1976D2] hover:bg-[#0065AF] text-white rounded-full font-medium text-sm disabled:bg-gray-400"
        >
          Add Another ({fields.length}/{maxItems})
        </button>
      </div>
    </div>
  );
}
