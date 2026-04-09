// src/components/TransactionModal.jsx
// Модальное окно: создание и редактирование транзакции с клиентской валидацией

import { useState } from "react";
import { TransactionAPI } from "../api";

const CATEGORIES = [
  "Еда и продукты",
  "Транспорт",
  "Жильё и ЖКХ",
  "Развлечения",
  "Здоровье",
  "Одежда",
  "Зарплата",
  "Фриланс",
  "Инвестиции",
  "Переводы",
  "Другое",
];

// ─── Клиентская валидация ──────────────────────────────────────────────────
function validate(form) {
  const errors = {};
  if (!form.type) errors.type = "Выберите тип";
  if (!form.amount || Number(form.amount) <= 0)
    errors.amount = "Сумма должна быть больше нуля";
  if (!form.category) errors.category = "Выберите категорию";
  if (!form.date) errors.date = "Укажите дату";
  if (form.description && form.description.length > 500)
    errors.description = "Максимум 500 символов";
  return errors;
}

export default function TransactionModal({ initial, onClose, onSaved }) {
  const isEditing = !!initial;

  const [form, setForm] = useState({
    type:        initial?.type        ?? "expense",
    amount:      initial?.amount      ?? "",
    category:    initial?.category    ?? "",
    description: initial?.description ?? "",
    date:        initial?.date        ?? new Date().toISOString().slice(0, 10),
  });
  const [errors, setErrors]           = useState({});
  const [serverError, setServerError] = useState(null);
  const [saving, setSaving]           = useState(false);

  const set = (key) => (e) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async () => {
    const errs = validate(form);
    setErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setSaving(true);
    setServerError(null);
    try {
      const payload = { ...form, amount: Number(form.amount) };
      if (isEditing) {
        await TransactionAPI.update(initial.id, payload);
      } else {
        await TransactionAPI.create(payload);
      }
      onSaved();
    } catch (e) {
      setServerError(e.message);
    } finally {
      setSaving(false);
    }
  };

  // Закрыть по клику на оверлей
  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) onClose();
  };

  return (
    <div
      className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
      onClick={handleOverlayClick}
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        {/* ── Header ── */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="text-lg font-bold text-gray-800">
            {isEditing ? "Редактировать транзакцию" : "Новая транзакция"}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none"
          >
            ✕
          </button>
        </div>

        {/* ── Body ── */}
        <div className="px-6 py-5 space-y-4">
          {/* Server error */}
          {serverError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {serverError}
            </div>
          )}

          {/* 1. Тип */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Тип <span className="text-red-500">*</span>
            </label>
            <div className="flex gap-2">
              {[
                { value: "income",  label: "↑ Доход",  active: "bg-green-600 border-green-600 text-white" },
                { value: "expense", label: "↓ Расход", active: "bg-red-500 border-red-500 text-white" },
              ].map(({ value, label, active }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setForm((f) => ({ ...f, type: value }))}
                  className={`flex-1 py-2 rounded-lg text-sm font-semibold border transition ${
                    form.type === value
                      ? active
                      : "border-gray-300 text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
            {errors.type && (
              <p className="text-red-500 text-xs mt-1">{errors.type}</p>
            )}
          </div>

          {/* 2. Сумма */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Сумма (₽) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="0.01"
              step="0.01"
              placeholder="0.00"
              value={form.amount}
              onChange={set("amount")}
              className={`w-full border rounded-lg px-3 py-2 text-sm
                focus:outline-none focus:ring-2 focus:ring-indigo-400 ${
                  errors.amount ? "border-red-400" : "border-gray-300"
                }`}
            />
            {errors.amount && (
              <p className="text-red-500 text-xs mt-1">{errors.amount}</p>
            )}
          </div>

          {/* 3. Категория */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Категория <span className="text-red-500">*</span>
            </label>
            <select
              value={form.category}
              onChange={set("category")}
              className={`w-full border rounded-lg px-3 py-2 text-sm
                focus:outline-none focus:ring-2 focus:ring-indigo-400 ${
                  errors.category ? "border-red-400" : "border-gray-300"
                }`}
            >
              <option value="">— выберите —</option>
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
            {errors.category && (
              <p className="text-red-500 text-xs mt-1">{errors.category}</p>
            )}
          </div>

          {/* 4. Дата */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Дата <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              value={form.date}
              onChange={set("date")}
              className={`w-full border rounded-lg px-3 py-2 text-sm
                focus:outline-none focus:ring-2 focus:ring-indigo-400 ${
                  errors.date ? "border-red-400" : "border-gray-300"
                }`}
            />
            {errors.date && (
              <p className="text-red-500 text-xs mt-1">{errors.date}</p>
            )}
          </div>

          {/* 5. Описание */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Описание{" "}
              <span className="text-gray-400 font-normal">
                ({form.description.length}/500)
              </span>
            </label>
            <textarea
              rows={2}
              placeholder="Необязательно…"
              value={form.description}
              onChange={set("description")}
              className={`w-full border rounded-lg px-3 py-2 text-sm resize-none
                focus:outline-none focus:ring-2 focus:ring-indigo-400 ${
                  errors.description ? "border-red-400" : "border-gray-300"
                }`}
            />
            {errors.description && (
              <p className="text-red-500 text-xs mt-1">{errors.description}</p>
            )}
          </div>
        </div>

        {/* ── Footer ── */}
        <div className="flex gap-3 px-6 py-4 border-t border-gray-100">
          <button
            onClick={onClose}
            className="flex-1 border border-gray-300 text-gray-700 rounded-lg py-2 text-sm
                       hover:bg-gray-50 transition"
          >
            Отмена
          </button>
          <button
            onClick={handleSubmit}
            disabled={saving}
            className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60
                       text-white rounded-lg py-2 text-sm font-semibold transition"
          >
            {saving ? "Сохранение…" : isEditing ? "Сохранить" : "Создать"}
          </button>
        </div>
      </div>
    </div>
  );
}
