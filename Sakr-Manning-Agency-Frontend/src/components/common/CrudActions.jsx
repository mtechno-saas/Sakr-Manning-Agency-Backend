import React from "react";
import { Save, X } from "lucide-react";

export function CrudActions({ editingId, handlers, labels = {} }) {
  return (
    <div className="flex gap-3 justify-center">
      {editingId ? (
        <>
          <button
            type="button"
            onClick={handlers.save}
            className="flex items-center gap-2 px-6 py-2 text-lg font-medium bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Save className="w-6 h-6" />
            {labels.save || "Save Changes"}
          </button>
          <button
            type="button"
            onClick={handlers.cancel}
            className="flex items-center gap-2 px-6 py-2 text-lg font-medium border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <X className="w-6 h-6" />
            {labels.cancel || "Cancel"}
          </button>
        </>
      ) : (
        <button
          type="button"
          onClick={handlers.add}
          className="px-16 py-3 bg-[#0065AF] text-white text-lg font-medium rounded-lg hover:bg-[#0060AF] transition-colors"
        >
          {labels.add || "Add Item"}
        </button>
      )}
    </div>
  );
}
