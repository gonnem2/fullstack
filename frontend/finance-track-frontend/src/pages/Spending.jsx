import React, { useEffect, useState, useCallback, useMemo } from 'react';
import Card from '../components/Card';
import EditItemModal from '../components/EditItemModal';
import { SpendingAPI, CategoryAPI } from '../api/api';

export default function Spending() {
  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);
  const [categories, setCategories] = useState({});
  const [loading, setLoading] = useState(true);

  // Состояния фильтров
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('expense_date'); // expense_date | value
  const [sortOrder, setSortOrder] = useState('desc');    // desc | asc
  const [selectedCategoryId, setSelectedCategoryId] = useState('');
  const [dateFrom, setDateFrom] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() - 1);
    return d.toISOString().slice(0, 10);
  });
  const [dateTo, setDateTo] = useState(() => new Date().toISOString().slice(0, 10));

  const [selectedItem, setSelectedItem] = useState(null);
  const [isModalOpen, setModalOpen] = useState(false);

  // Загрузка категорий один раз
  useEffect(() => {
    CategoryAPI.list().then(res => {
      const catMap = {};
      res.categories.forEach(c => { catMap[c.id] = c.title; });
      setCategories(catMap);
    }).catch(console.error);
  }, []);

  // Загрузка данных с фильтрами
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        from_date: new Date(dateFrom).toISOString(),
        to_date: new Date(dateTo).toISOString(),
        skip: 0,
        limit: 100,
        sort_by: sortBy,
        sort_order: sortOrder,
      };
      if (search.trim()) params.search = search.trim();
      if (selectedCategoryId) params.category_id = Number(selectedCategoryId);

      const qs = new URLSearchParams(params).toString();
      const res = await SpendingAPI.list(qs);

      // бэкенд возвращает { data: { expenses, skip, limit }, total }
      const expenses = res.data?.expenses || [];
      setTotal(res.total || 0);

      const mapped = expenses.map(e => ({
        id: e.id,
        date: e.expense_date,
        time: new Date(e.expense_date).toLocaleTimeString(),
        type: categories[e.category_id] || '—',
        cost: e.value,
        comment: e.comment,
      }));
      setRows(mapped);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [search, sortBy, sortOrder, selectedCategoryId, dateFrom, dateTo, categories]);

  // Debounce для поиска
  useEffect(() => {
    const timer = setTimeout(() => {
      loadData();
    }, 500);
    return () => clearTimeout(timer);
  }, [search, sortBy, sortOrder, selectedCategoryId, dateFrom, dateTo, loadData]);

  const handleOpenModal = (item) => {
    setSelectedItem(item);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    await SpendingAPI.delete(id);
    loadData(); // перезагрузить после удаления
  };

  // Сброс фильтров
  const handleReset = () => {
    setSearch('');
    setSortBy('expense_date');
    setSortOrder('desc');
    setSelectedCategoryId('');
    const from = new Date();
    from.setDate(from.getDate() - 1);
    setDateFrom(from.toISOString().slice(0, 10));
    setDateTo(new Date().toISOString().slice(0, 10));
  };

  // Компонент кнопки сортировки
  const SortButton = ({ field, label }) => (
    <button
      onClick={() => {
        if (sortBy === field) {
          setSortOrder(prev => (prev === 'asc' ? 'desc' : 'asc'));
        } else {
          setSortBy(field);
          setSortOrder('desc');
        }
      }}
      className={`px-3 py-1 rounded-md text-sm font-medium transition ${
        sortBy === field
          ? 'bg-blue-600 text-white'
          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
      }`}
    >
      {label} {sortBy === field && (sortOrder === 'asc' ? '↑' : '↓')}
    </button>
  );

  if (loading && rows.length === 0) return <div className="p-6 text-center">Загрузка...</div>;

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h2 className="text-2xl font-semibold mb-6 text-center">Траты</h2>

      {/* Панель фильтров */}
      <Card>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Поиск (комментарий)</label>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="комментарий..."
              className="mt-1 w-full px-3 py-2 border rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Категория</label>
            <select
              value={selectedCategoryId}
              onChange={(e) => setSelectedCategoryId(e.target.value)}
              className="mt-1 w-full px-3 py-2 border rounded-md"
            >
              <option value="">Все категории</option>
              {Object.entries(categories).map(([id, title]) => (
                <option key={id} value={id}>{title}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Дата от</label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="mt-1 w-full px-3 py-2 border rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Дата до</label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="mt-1 w-full px-3 py-2 border rounded-md"
            />
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div className="flex gap-2">
            <SortButton field="expense_date" label="По дате" />
            <SortButton field="value" label="По сумме" />
          </div>
          <button
            onClick={handleReset}
            className="px-4 py-1 text-sm bg-gray-300 rounded-md hover:bg-gray-400"
          >
            Сбросить фильтры
          </button>
        </div>

        <div className="text-sm text-gray-500 mb-2">Найдено: {total}</div>

        <div className="space-y-3">
          {rows.map((r) => (
            <div
              key={r.id}
              onClick={() => handleOpenModal(r)}
              className="flex justify-between p-3 bg-gray-50 rounded-xl cursor-pointer hover:bg-gray-100 transition"
            >
              <div className="w-20 text-gray-500">{r.time}</div>
              <div className="flex-1 px-4">
                <div className="font-medium">{r.type}</div>
                <div className="text-sm text-gray-500">{r.comment}</div>
              </div>
              <div className="font-semibold">{r.cost} ₽</div>
            </div>
          ))}
          {rows.length === 0 && !loading && (
            <div className="text-center text-gray-500 py-8">Нет трат за выбранный период</div>
          )}
        </div>
      </Card>

      {isModalOpen && (
        <EditItemModal
          isOpen={isModalOpen}
          onClose={() => setModalOpen(false)}
          item={selectedItem}
          onDelete={handleDelete}
        />
      )}
    </div>
  );
}