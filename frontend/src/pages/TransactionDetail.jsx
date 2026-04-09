// src/pages/TransactionDetail.jsx
// Страница детального просмотра транзакции + управление прикреплёнными файлами

import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { TransactionAPI } from "../api";
import FileUpload from "../components/FileUpload";
import TransactionModal from "../components/TransactionModal";

const fmtMoney = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
});
const fmtDate = (d) => new Date(d).toLocaleDateString("ru-RU");
const fmtDateTime = (d) => new Date(d).toLocaleString("ru-RU");

export default function TransactionDetail() {
  const { id }       = useParams();
  const navigate     = useNavigate();
  const [tx, setTx]  = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);
  const [editing, setEditing] = useState(false);

  const loadTx = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await TransactionAPI.get(id);
      setTx(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadTx(); }, [id]);

  const handleDelete = async () => {
    if (!confirm("Удалить эту транзакцию? Все прикреплённые файлы также будут удалены.")) return;
    try {
      await TransactionAPI.delete(id);
      navigate("/transactions");
    } catch (e) {
      alert(e.message);
    }
  };

  // ── Loading ──────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
      </div>
    );
  }

  // ── Error ────────────────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          ⚠️ {error}
        </div>
        <Link
          to="/transactions"
          className="mt-4 inline-block text-sm text-indigo-600 hover:underline"
        >
          ← Вернуться к списку
        </Link>
      </div>
    );
  }

  const isIncome = tx.type === "income";

  return (
    <div className="max-w-2xl mx-auto px-4 py-6">
      {/* Breadcrumb */}
      <Link
        to="/transactions"
        className="text-sm text-indigo-600 hover:underline flex items-center gap-1 mb-4"
      >
        ← К списку транзакций
      </Link>

      {/* Card */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">

        {/* ── Шапка транзакции ── */}
        <div className="flex items-start justify-between">
          <div>
            <span className={`inline-block text-xs font-semibold px-2 py-0.5 rounded-full mb-2 ${
              isIncome ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"
            }`}>
              {isIncome ? "Доход" : "Расход"}
            </span>
            <p className={`text-3xl font-bold ${
              isIncome ? "text-green-600" : "text-red-500"
            }`}>
              {isIncome ? "+" : "−"}{fmtMoney.format(tx.amount)}
            </p>
          </div>

          <span className="bg-gray-100 text-gray-700 text-sm font-medium px-3 py-1 rounded-full">
            {tx.category}
          </span>
        </div>

        {/* ── Детали ── */}
        <dl className="mt-5 space-y-2 text-sm">
          {[
            { label: "Дата",      value: fmtDate(tx.date) },
            { label: "Описание",  value: tx.description || "—" },
            { label: "Создано",   value: fmtDateTime(tx.created_at) },
            { label: "ID",        value: `#${tx.id}` },
          ].map(({ label, value }) => (
            <div key={label} className="flex gap-3">
              <dt className="w-24 font-medium text-gray-500 shrink-0">{label}:</dt>
              <dd className="text-gray-700">{value}</dd>
            </div>
          ))}
        </dl>

        {/* ── Кнопки ── */}
        <div className="flex gap-3 mt-5">
          <button
            onClick={() => setEditing(true)}
            className="flex-1 border border-indigo-300 text-indigo-700 hover:bg-indigo-50
                       rounded-lg py-2 text-sm font-medium transition"
          >
            ✏️ Редактировать
          </button>
          <button
            onClick={handleDelete}
            className="flex-1 border border-red-300 text-red-600 hover:bg-red-50
                       rounded-lg py-2 text-sm font-medium transition"
          >
            🗑 Удалить
          </button>
        </div>

        {/* ── Разделитель ── */}
        <hr className="my-6 border-gray-100" />

        {/* ── Файлы ── */}
        <FileUpload transactionId={tx.id} />
      </div>

      {/* Edit modal */}
      {editing && (
        <TransactionModal
          initial={tx}
          onClose={() => setEditing(false)}
          onSaved={() => {
            setEditing(false);
            loadTx();
          }}
        />
      )}
    </div>
  );
}
