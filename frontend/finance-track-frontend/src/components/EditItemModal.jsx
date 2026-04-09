import { useState, useEffect } from "react";

export default function EditItemModal({ 
  isOpen, 
  onClose, 
  item, 
  onUpdate, 
  onDelete 
}) {
  const [form, setForm] = useState({
    date: "",
    time: "",
    amount: "",
    comment: "",
    category: "",
  });

  useEffect(() => {
    if (item) {
      setForm({
        date: item.date || "",
        time: item.time || "",
        amount: item.amount?.toString() || "",
        comment: item.comment || "",
        category: item.category || "",
      });
    } else {
      setForm({
        date: "",
        time: "",
        amount: "",
        comment: "",
        category: "",
      });
    }
  }, [item]);

  if (!isOpen) return null;

  const handleChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
    const updated = {
      id: item?.id || Date.now(),
      date: form.date,
      time: form.time,
      amount: parseFloat(form.amount) || 0,
      comment: form.comment,
      category: form.category,
    };

    if (typeof onUpdate === "function") {
      onUpdate(updated);
    }
    onClose();
  };

  const handleDelete = () => {
    if (item && item.id && typeof onDelete === "function") {
      onDelete(item.id);
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white rounded-3xl p-6 w-[340px] shadow-lg flex flex-col gap-3">
        <h2 className="text-center text-lg font-semibold">
          {item ? "Редактировать трату" : "Добавить трату"}
        </h2>

        <label className="text-sm">Дата</label>
        <input
          type="date"
          value={form.date}
          onChange={(e) => handleChange("date", e.target.value)}
          className="border rounded-xl px-3 py-2"
        />

        <label className="text-sm">Время</label>
        <input
          type="time"
          value={form.time}
          onChange={(e) => handleChange("time", e.target.value)}
          className="border rounded-xl px-3 py-2"
        />

        <label className="text-sm">Категория</label>
        <input
          type="text"
          value={form.category}
          onChange={(e) => handleChange("category", e.target.value)}
          placeholder="Например: Еда, Транспорт"
          className="border rounded-xl px-3 py-2"
        />

        <label className="text-sm">Сумма</label>
        <input
          type="number"
          value={form.amount}
          onChange={(e) => handleChange("amount", e.target.value)}
          className="border rounded-xl px-3 py-2"
        />

        <label className="text-sm">Комментарий</label>
        <input
          type="text"
          value={form.comment}
          onChange={(e) => handleChange("comment", e.target.value)}
          className="border rounded-xl px-3 py-2"
        />

        <div className="flex gap-2 mt-3">
          <button
            onClick={handleSave}
            className="flex-1 bg-[#7b61ff] text-white py-2 rounded-xl hover:bg-[#674de0]"
          >
            Готово
          </button>
          {item && (
            <button
              onClick={handleDelete}
              className="flex-1 bg-red-100 text-red-600 py-2 rounded-xl hover:bg-red-200"
            >
              Удалить
            </button>
          )}
        </div>

        <button
          onClick={onClose}
          className="text-center text-sm text-gray-500 mt-2 underline"
        >
          Отмена
        </button>
      </div>
    </div>
  );
}
