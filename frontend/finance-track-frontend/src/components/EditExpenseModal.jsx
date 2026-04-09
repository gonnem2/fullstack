import { useState, useEffect } from "react";
import { SpendingAPI, CategoryAPI, FileAPI } from "../api/api";

export default function EditExpenseModal({ isOpen, onClose, item, onSuccess }) {
  const [form, setForm] = useState({
    date: "",
    time: "",
    amount: "",
    comment: "",
    category_id: "",
  });
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState([]);

  // Загрузка категорий расходов при открытии
  useEffect(() => {
    if (isOpen) {
      CategoryAPI.list()
        .then((res) => {
          const expenseCats = res.categories.filter((c) => c.type_of_category === "expense");
          setCategories(expenseCats);
        })
        .catch(console.error);
    }
  }, [isOpen]);

  // Заполнение формы при редактировании
  useEffect(() => {
    if (item) {
      const dateStr = item.expense_date || item.date || "";
      setForm({
        date: dateStr.split("T")[0] || "",
        time: dateStr.split("T")[1]?.slice(0, 5) || "",
        amount: item.cost ?? item.value ?? item.amount ?? "",
        comment: item.comment || "",
        category_id: item.category_id ?? "",
      });
      if (item.image_key) {
        setPreview(`/api/v1/files/${item.image_key}/download-url`);
      } else {
        setPreview(null);
      }
    } else {
      setForm({
        date: "",
        time: "",
        amount: "",
        comment: "",
        category_id: "",
      });
      setSelectedFile(null);
      setPreview(null);
    }
  }, [item]);

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result);
      reader.readAsDataURL(file);
    } else {
      setPreview(null);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      let dateTime;
      if (form.date && form.time) {
        dateTime = `${form.date}T${form.time}:00`;
      } else if (form.date) {
        dateTime = `${form.date}T00:00:00`;
      } else {
        dateTime = new Date().toISOString();
      }

      if (item?.id) {
        // Редактирование: PUT JSON
        await SpendingAPI.update(item.id, {
          expense_date: dateTime,
          category_id: parseInt(form.category_id, 10),
          cost: parseFloat(form.amount),
          comment: form.comment || "",
        });
        // Если выбран новый файл – загружаем через FileAPI
        if (selectedFile) {
          await FileAPI.upload(`expense_${item.id}`, selectedFile);
        }
      } else {
        // Создание: FormData
        const fd = new FormData();
        fd.append("expense_date", dateTime);
        fd.append("category_id", String(parseInt(form.category_id, 10)));
        fd.append("cost", String(parseFloat(form.amount)));
        if (form.comment) fd.append("comment", form.comment);
        if (selectedFile) fd.append("image", selectedFile);
        await SpendingAPI.create(fd);
      }
      if (onSuccess) onSuccess();
      onClose();
    } catch (err) {
      console.error("Save expense error:", err);
      alert("Ошибка сохранения расхода");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!item?.id) return;
    if (!confirm("Удалить расход?")) return;
    setLoading(true);
    try {
      await SpendingAPI.delete(item.id);
      if (onSuccess) onSuccess();
      onClose();
    } catch (err) {
      console.error(err);
      alert("Ошибка удаления расхода");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white rounded-3xl p-6 w-[400px] shadow-lg flex flex-col gap-3">
        <h2 className="text-center text-lg font-semibold">
          {item ? "Редактировать расход" : "Добавить расход"}
        </h2>

        <label className="text-sm">Дата</label>
        <input
          type="date"
          value={form.date}
          onChange={(e) => setForm({ ...form, date: e.target.value })}
          className="border rounded-xl px-3 py-2"
        />

        <label className="text-sm">Время</label>
        <input
          type="time"
          value={form.time}
          onChange={(e) => setForm({ ...form, time: e.target.value })}
          className="border rounded-xl px-3 py-2"
        />

        <label className="text-sm">Категория</label>
        <select
          value={form.category_id}
          onChange={(e) => setForm({ ...form, category_id: e.target.value })}
          className="border rounded-xl px-3 py-2"
        >
          <option value="">Выберите категорию</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.title}
            </option>
          ))}
        </select>

        <label className="text-sm">Сумма</label>
        <input
          type="number"
          value={form.amount}
          onChange={(e) => setForm({ ...form, amount: e.target.value })}
          className="border rounded-xl px-3 py-2"
        />

        <label className="text-sm">Комментарий</label>
        <input
          type="text"
          value={form.comment}
          onChange={(e) => setForm({ ...form, comment: e.target.value })}
          className="border rounded-xl px-3 py-2"
        />

        <label className="text-sm">Изображение</label>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="border rounded-xl px-3 py-2"
        />
        {preview && (
          <img src={preview} alt="preview" className="w-20 h-20 object-cover rounded mt-2" />
        )}

        <div className="flex gap-2 mt-3">
          <button
            onClick={handleSave}
            disabled={loading}
            className="flex-1 bg-[#7b61ff] text-white py-2 rounded-xl hover:bg-[#674de0] disabled:opacity-50"
          >
            {loading ? "Сохранение..." : "Готово"}
          </button>
          {item && (
            <button
              onClick={handleDelete}
              disabled={loading}
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