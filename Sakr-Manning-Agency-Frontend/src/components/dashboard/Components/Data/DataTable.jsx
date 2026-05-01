import React, { useMemo, useState } from "react";
import { Pagination } from "./Pagination";

export function DataTable({
  columns = [],
  data = [],
  rowKey = "id",
  className = "",
  style = {},
  initialSort = null, // { key, direction: 'asc'|'desc' }
  pageSize = 10,
  initialPage = 1,
  onSort = null,
  onRowClick = null,
  emptyState = null,
}) {
  const [sort, setSort] = useState(initialSort);
  const [page, setPage] = useState(initialPage);

  const sorted = useMemo(() => {
    if (!sort?.key) return data;
    const col = columns.find((c) => c.key === sort.key);
    const dir = sort.direction === "desc" ? -1 : 1;
    return [...data].sort((a, b) => {
      const va = col && col.sortValue ? col.sortValue(a) : a[sort.key];
      const vb = col && col.sortValue ? col.sortValue(b) : b[sort.key];
      if (va == null) return 1 * dir;
      if (vb == null) return -1 * dir;
      if (typeof va === "number" && typeof vb === "number")
        return (va - vb) * dir;
      return String(va).localeCompare(String(vb)) * dir;
    });
  }, [data, sort, columns]);

  const total = sorted.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const currentPage = Math.min(page, totalPages);
  const pageData = sorted.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  function handleHeaderClick(key, sortable) {
    if (!sortable) return;
    let dir = "asc";
    if (sort && sort.key === key)
      dir = sort.direction === "asc" ? "desc" : "asc";
    const newSort = { key, direction: dir };
    setSort(newSort);
    onSort && onSort(newSort);
  }

  if (!data || data.length === 0) {
    return emptyState ? (
      <div className={className} style={style}>
        {emptyState}
      </div>
    ) : (
      <div className={className} style={style}>
        <div className="w-full h-32 flex items-center justify-center text-gray-400">
          No data available.
        </div>
      </div>
    );
  }

  return (
    <div className={`w-full ${className}`} style={style}>
      {/* Desktop/table view */}
      <div className="overflow-x-auto hidden md:block">
        <table className="min-w-full bg-white rounded-lg overflow-hidden">
          <thead>
            <tr className="text-left text-sm text-gray-500">
              {columns.map((col) => (
                <th
                  key={col.key}
                  style={{ width: col.width }}
                  className={`px-4 py-3 ${col.className || ""} ${
                    col.sortable ? "cursor-pointer select-none" : ""
                  }`}
                  onClick={() => handleHeaderClick(col.key, col.sortable)}
                  scope="col"
                  aria-sort={
                    sort && sort.key === col.key ? sort.direction : "none"
                  }
                >
                  <div className="flex items-center gap-2">
                    <span>{col.title}</span>
                    {col.sortable && (
                      <span className="text-xs text-gray-400">
                        {sort && sort.key === col.key
                          ? sort.direction === "asc"
                            ? "▲"
                            : "▼"
                          : "↕"}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="text-sm text-gray-700">
            {pageData.map((row) => (
              <tr
                key={row[rowKey]}
                className="border-t last:border-b hover:bg-gray-50 cursor-default"
                onClick={() => onRowClick && onRowClick(row)}
              >
                {columns.map((col) => (
                  <td
                    key={col.key}
                    className={`px-4 py-4 align-middle ${
                      col.cellClassName || ""
                    }`}
                  >
                    {col.render ? col.render(row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Small screens: card list */}
      <div className="md:hidden flex flex-col gap-4">
        {pageData.map((row) => (
          <div key={row[rowKey]} onClick={() => onRowClick && onRowClick(row)}>
            {/* Use a simple stacked card: render first 3 columns as rows */}
            <div className="bg-white rounded-xl shadow p-4">
              {columns.map((col, idx) => (
                <div
                  key={col.key}
                  className={`flex justify-between py-1 ${
                    idx < columns.length - 1 ? "border-b border-gray-100" : ""
                  }`}
                >
                  <div className="text-xs text-gray-500">{col.title}</div>
                  <div className="text-sm text-gray-800">
                    {col.render ? col.render(row) : row[col.key]}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Pagination footer */}
      <div className="mt-4 flex items-center justify-end">
        <Pagination
          page={currentPage}
          pageSize={pageSize}
          total={total}
          onChange={(p) => setPage(p)}
        />
      </div>
    </div>
  );
}
