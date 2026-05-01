import React from "react";

export function Pagination({ page = 1, pageSize = 10, total = 0, onChange }) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const pages = [];
  for (let i = 1; i <= totalPages; i++) pages.push(i);

  return (
    <div className="flex items-center gap-2 text-sm">
      <button
        onClick={() => onChange(Math.max(1, page - 1))}
        className="px-2 py-1 rounded-md bg-white border"
        disabled={page <= 1}
        aria-label="Previous page"
      >
        Prev
      </button>

      <div className="flex items-center gap-1">
        {pages.map((p) => (
          <button
            key={p}
            onClick={() => onChange(p)}
            className={`px-3 py-1 rounded-md ${
              p === page ? "bg-[#056BB6] text-white" : "bg-white border"
            }`}
            aria-current={p === page ? "page" : undefined}
          >
            {p}
          </button>
        ))}
      </div>

      <button
        onClick={() => onChange(Math.min(totalPages, page + 1))}
        className="px-2 py-1 rounded-md bg-white border"
        disabled={page >= totalPages}
        aria-label="Next page"
      >
        Next
      </button>
    </div>
  );
}
