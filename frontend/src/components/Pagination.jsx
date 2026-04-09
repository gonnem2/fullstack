// src/components/Pagination.jsx
// Пагинация с "умными" многоточиями

export default function Pagination({ page, pages, onPageChange }) {
  if (pages <= 1) return null;

  // Строим диапазон: всегда первая, последняя, и ±2 от текущей
  const buildPages = () => {
    const delta = 2;
    const range = [];
    for (
      let i = Math.max(2, page - delta);
      i <= Math.min(pages - 1, page + delta);
      i++
    ) {
      range.push(i);
    }

    const result = [1];
    if (range[0] > 2) result.push("...");
    result.push(...range);
    if (range[range.length - 1] < pages - 1) result.push("...");
    if (pages > 1) result.push(pages);
    return result;
  };

  return (
    <nav
      className="flex items-center justify-center gap-1 mt-6"
      aria-label="Pagination"
    >
      {/* Prev */}
      <button
        onClick={() => onPageChange(page - 1)}
        disabled={page === 1}
        className="px-3 py-1.5 rounded-lg border border-gray-300 text-sm text-gray-600
                   disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50 transition"
      >
        ← Назад
      </button>

      {/* Pages */}
      {buildPages().map((p, i) =>
        p === "..." ? (
          <span key={`dots-${i}`} className="px-2 py-1.5 text-gray-400 text-sm">
            …
          </span>
        ) : (
          <button
            key={p}
            onClick={() => onPageChange(p)}
            aria-current={p === page ? "page" : undefined}
            className={`min-w-[2rem] px-3 py-1.5 rounded-lg border text-sm font-medium transition ${
              p === page
                ? "bg-indigo-600 border-indigo-600 text-white shadow-sm"
                : "border-gray-300 text-gray-700 hover:bg-gray-50"
            }`}
          >
            {p}
          </button>
        )
      )}

      {/* Next */}
      <button
        onClick={() => onPageChange(page + 1)}
        disabled={page === pages}
        className="px-3 py-1.5 rounded-lg border border-gray-300 text-sm text-gray-600
                   disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50 transition"
      >
        Вперёд →
      </button>
    </nav>
  );
}
