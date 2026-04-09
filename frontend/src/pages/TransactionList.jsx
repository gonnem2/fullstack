// src/pages/TransactionList.jsx
// Главная страница транзакций: фильтры, поиск, сортировка, пагинация, CRUD

import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { TransactionAPI } from "../api";
import { useFilters } from "../hooks/useFilters";
import FilterPanel from "../components/FilterPanel";
import Pagination from "../components/Pagination";
import TransactionModal from "../components/TransactionModal";

// ─── Форматирование ───────────────────────────────────────────────────────────
const fmtMoney = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  minimumFractionDigits: 2,
});
const fmtDate = (d) => new Date(d).toLocaleDateString("ru-RU");

// ─── Строка таблицы ───────────────────────────────────────────────────────────
function TxRow({ tx, onEdit, onDelete }) {
  const isIncome = tx.type === "income";
  return (
    <tr className="hover:bg-gray-50 transition">
      <td className="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">
        {fmtDate(tx.date)}
      </td>
      <td className="px-4 py-3">
        <span className="inline-block bg-gray-100 text-gray-700 text-xs font-medium px-2 py-0.5 rounded-full">
          {tx.category}
        </span>
      </td>
      <td className="px-4 py-3 text-sm text-gray-700 max-w-[240px] truncate">
        {tx.description || (
          <span className="italic text-gray-400">без описания</span>
        )}
      </td>
      <td className={`px-4 py-3 text-sm font-semibold whitespace-nowrap ${
        isIncome ? "text-green-600" : "text-red-500"
      }`}>
        {isIncome ? "+" : "−"}{fmtMoney.format(tx.amount)}
      </td>
      <td className="px-4 py-3">
        <span className={`inline-block text-xs font-semibold px-2 py-0.5 rounded-full ${
          isIncome
            ? "bg-green-100 text-green-700"
            : "bg-red-100 text-red-600"
        }`}>
          {isIncome ? "Доход" : "Расход"}
        </span>
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-3">
          <button
            onClick={onEdit}
            className="text-indigo-600 hover:text-indigo-800 text-xs font-medium transition"
          >
            Изменить
          </button>
          <button
            onClick={onDelete}
            className="text-red-500 hover:text-red-700 text-xs font-medium transition"
          >
            Удалить
          </button>
          <Link
            to={`/transactions/${tx.id}`}
            className="text-gray-500 hover:text-gray-700 text-xs font-medium transition"
          >
            Файлы →
          </Link>
        </div>
      </td>
    </tr>
  );
}

// ─── Заголовок колонки с сортировкой ─────────────────────────────────────────
function SortTh({ label, field, currentField, currentOrder, onSort }) {
  const active = field && currentField === field;
  return (
    <th
      onClick={field ? () => onSort(field) : undefined}
      className={`px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide
        ${field ? "cursor-pointer select-none hover:text-indigo-600" : ""}`}
    >
      {label}
      {active && (
        <span className="ml-1 text-indigo-500">
          {currentOrder === "asc" ? "↑" : "↓"}
        </span>
      )}
    </th>
  );
}

// ─── Страница ─────────────────────────────────────────────────────────────────
export default function TransactionList() {
  const { filters, setFilter, toQueryString, resetFilters } = useFilters();

  const [data, setData]           = useState({ items: [], total: 0, pages: 1 });
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState(null);
  const [categories, setCategories] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editTarget, setEditTarget] = useState(null); // null = create, tx = edit

  // ── Загрузка данных ──────────────────────────────────────────────────────────
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await TransactionAPI.list(toQueryString());
      setData(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [toQueryString]);

  useEffect(() => { fetchData(); }, [fetchData]);

  useEffect(() => {
    TransactionAPI.categories().then(setCategories).catch(() => {});
  }, []);

  // ── Действия ─────────────────────────────────────────────────────────────────
  const openCreate = () => { setEditTarget(null); setShowModal(true); };
  const openEdit   = (tx) => { setEditTarget(tx); setShowModal(true); };
  const closeModal = () => setShowModal(false);
  const afterSave  = () => { setShowModal(false); fetchData(); };

  const handleDelete = async (id) => {
    if (!confirm("Удалить транзакцию?")) return;
    try {
      await TransactionAPI.delete(id);
      fetchData();
    } catch (e) {
      alert(e.message);
    }
  };

  const handleSort = (field) => {
    if (filters.sort_by === field) {
      setFilter({ sort_order: filters.sort_order === "asc" ? "desc" : "asc" });
    } else {
      setFilter({ sort_by: field, sort_order: "desc" });
    }
  };

  // ── Рендер ───────────────────────────────────────────────────────────────────
  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Транзакции</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Управление доходами и расходами
          </p>
        </div>
        <button
          onClick={openCreate}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2
                     rounded-lg text-sm font-semibold transition shadow-sm"
        >
          + Новая транзакция
        </button>
      </div>

      {/* Filter panel */}
      <FilterPanel
        filters={filters}
        categories={categories}
        onChange={setFilter}
        onReset={resetFilters}
      />

      {/* Error */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Summary + page-size */}
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm text-gray-500">
          {loading ? "Загрузка…" : `Найдено: ${data.total}`}
        </p>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <span>Записей на странице:</span>
          <select
            value={filters.page_size}
            onChange={(e) => setFilter({ page_size: e.target.value })}
            className="border border-gray-300 rounded px-2 py-1 text-sm"
          >
            {[10, 20, 50, 100].map((n) => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                <SortTh label="Дата"      field="date"       currentField={filters.sort_by} currentOrder={filters.sort_order} onSort={handleSort} />
                <SortTh label="Категория" field="category"   currentField={filters.sort_by} currentOrder={filters.sort_order} onSort={handleSort} />
                <SortTh label="Описание"  field={null}       currentField={filters.sort_by} currentOrder={filters.sort_order} onSort={handleSort} />
                <SortTh label="Сумма"     field="amount"     currentField={filters.sort_by} currentOrder={filters.sort_order} onSort={handleSort} />
                <SortTh label="Тип"       field={null}       currentField={filters.sort_by} currentOrder={filters.sort_order} onSort={handleSort} />
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan={6} className="text-center py-14 text-gray-400">
                    <div className="flex flex-col items-center gap-2">
                      <div className="w-7 h-7 border-4 border-indigo-200 border-t-indigo-500 rounded-full animate-spin" />
                      Загрузка…
                    </div>
                  </td>
                </tr>
              ) : data.items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-14 text-gray-400">
                    Транзакции не найдены. Попробуйте изменить фильтры.
                  </td>
                </tr>
              ) : (
                data.items.map((tx) => (
                  <TxRow
                    key={tx.id}
                    tx={tx}
                    onEdit={() => openEdit(tx)}
                    onDelete={() => handleDelete(tx.id)}
                  />
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      <Pagination
        page={filters.page}
        pages={data.pages}
        onPageChange={(p) => setFilter({ page: p })}
      />

      {/* Modal */}
      {showModal && (
        <TransactionModal
          initial={editTarget}
          onClose={closeModal}
          onSaved={afterSave}
        />
      )}
    </div>
  );
}
