// src/components/FilterPanel.jsx
// Панель с 6 параметрами фильтрации + кнопка сброса

import { useState } from "react";

export default function FilterPanel({ filters, categories, onChange, onReset }) {
  const [open, setOpen] = useState(true);

  const hasActive =
    filters.search ||
    filters.type ||
    filters.category ||
    filters.date_from ||
    filters.date_to ||
    filters.amount_min ||
    filters.amount_max;

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm mb-4">
      {/* ── Toggle ── */}
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-4 py-3 text-sm font-semibold text-gray-700 hover:bg-gray-50 rounded-xl transition"
      >
        <span className="flex items-center gap-2">
          {/* Filter icon */}
          <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2a1 1 0 01-.293.707L13 13.414V19a1 1 0 01-.553.894l-4 2A1 1 0 017 21v-7.586L3.293 6.707A1 1 0 013 6V4z"
            />
          </svg>
          Фильтры
          {hasActive && (
            <span className="bg-indigo-100 text-indigo-700 text-xs font-bold px-2 py-0.5 rounded-full">
              активны
            </span>
          )}
        </span>
        <span className="text-gray-400 text-xs">{open ? "▲ скрыть" : "▼ показать"}</span>
      </button>

      {/* ── Form ── */}
      {open && (
        <div className="px-4 pb-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">

          {/* 1. Поиск по описанию */}
          <div className="lg:col-span-3">
            <label className="block text-xs font-medium text-gray-500 mb-1">
              Поиск по описанию
            </label>
            <div className="relative">
              <input
                type="text"
                placeholder="Введите текст…"
                value={filters.search}
                onChange={(e) => onChange({ search: e.target.value })}
                className="w-full border border-gray-300 rounded-lg pl-9 pr-3 py-2 text-sm
                           focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
              <svg className="absolute left-2.5 top-2.5 w-4 h-4 text-gray-400"
                fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          {/* 2. Тип */}
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Тип</label>
            <select
              value={filters.type}
              onChange={(e) => onChange({ type: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
                         focus:outline-none focus:ring-2 focus:ring-indigo-400"
            >
              <option value="">Все типы</option>
              <option value="income">Доходы</option>
              <option value="expense">Расходы</option>
            </select>
          </div>

          {/* 3. Категория */}
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Категория</label>
            <select
              value={filters.category}
              onChange={(e) => onChange({ category: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
                         focus:outline-none focus:ring-2 focus:ring-indigo-400"
            >
              <option value="">Все категории</option>
              {categories.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {/* 4a. Дата от */}
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Дата от</label>
            <input
              type="date"
              value={filters.date_from}
              onChange={(e) => onChange({ date_from: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
                         focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>

          {/* 4b. Дата до */}
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Дата до</label>
            <input
              type="date"
              value={filters.date_to}
              onChange={(e) => onChange({ date_to: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
                         focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>

          {/* 5a. Сумма мин */}
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Сумма от</label>
            <input
              type="number"
              min="0"
              step="0.01"
              placeholder="0"
              value={filters.amount_min}
              onChange={(e) => onChange({ amount_min: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
                         focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>

          {/* 5b. Сумма макс */}
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Сумма до</label>
            <input
              type="number"
              min="0"
              step="0.01"
              placeholder="∞"
              value={filters.amount_max}
              onChange={(e) => onChange({ amount_max: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
                         focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>

          {/* Сброс */}
          {hasActive && (
            <div className="flex items-end">
              <button
                onClick={onReset}
                className="w-full border border-red-300 text-red-600 hover:bg-red-50
                           rounded-lg px-3 py-2 text-sm font-medium transition"
              >
                ✕ Сбросить фильтры
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
