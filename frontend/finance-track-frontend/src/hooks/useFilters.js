// src/hooks/useFilters.js
// Хранит состояние фильтров в URL query params — сохраняется при навигации и перезагрузке

import { useCallback, useMemo } from "react";
import { useSearchParams } from "react-router-dom";

/**
 * Пример URL с фильтрами:
 * /transactions?search=еда&type=expense&category=Food&date_from=2025-01-01&sort_by=amount&sort_order=desc&page=2
 */
export function useFilters() {
  const [searchParams, setSearchParams] = useSearchParams();

  const get = (key, fallback = "") => searchParams.get(key) ?? fallback;

  // Читаем из URL
  const filters = useMemo(
    () => ({
      search:     get("search"),
      type:       get("type"),          // "income" | "expense" | ""
      category:   get("category"),
      date_from:  get("date_from"),
      date_to:    get("date_to"),
      amount_min: get("amount_min"),
      amount_max: get("amount_max"),
      sort_by:    get("sort_by", "date"),
      sort_order: get("sort_order", "desc"),
      page:       Number(get("page", "1")),
      page_size:  Number(get("page_size", "20")),
    }),
    [searchParams]
  );

  /**
   * Обновить один или несколько фильтров.
   * При изменении любого фильтра (не страницы) — сбрасываем на page=1.
   */
  const setFilter = useCallback(
    (updates) => {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        Object.entries(updates).forEach(([key, value]) => {
          if (value === "" || value === null || value === undefined) {
            next.delete(key);
          } else {
            next.set(key, String(value));
          }
        });
        if (!("page" in updates)) next.set("page", "1");
        return next;
      });
    },
    [setSearchParams]
  );

  /** Собрать строку для API-запроса (все непустые параметры). */
  const toQueryString = useCallback(() => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== "" && value !== null && value !== undefined) {
        params.set(key, String(value));
      }
    });
    return params.toString();
  }, [filters]);

  const resetFilters = useCallback(() => {
    setSearchParams({});
  }, [setSearchParams]);

  return { filters, setFilter, toQueryString, resetFilters };
}
