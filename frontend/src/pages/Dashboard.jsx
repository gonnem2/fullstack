// Lab 4: SEO + CurrencyWidget
import React, { useEffect, useState, useMemo } from "react";
import { usePageMeta } from '../hooks/usePageMeta';
import CurrencyWidget from '../components/CurrencyWidget';
import { useAuth } from "../contexts/AuthContext";
import api from "../api/api";
import EditExpenseModal from "../components/EditExpenseModal";
import EditIncomeModal from "../components/EditIncomeModal";
import ImageViewerModal from "../components/ImageViewerModal";

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1';


function Modal({ open, onClose, title, children }) {
  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center transition-opacity ${open ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`} aria-hidden={!open}>
      <div onClick={onClose} className={`absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity ${open ? 'opacity-100' : 'opacity-0'}`} />
      <div className={`relative z-10 w-full max-w-lg mx-4 bg-white rounded-2xl shadow-2xl p-6 transform transition-all ${open ? 'translate-y-0 opacity-100' : 'translate-y-6 opacity-0'}`}>
        <h3 className="text-center font-semibold text-lg mb-4">{title}</h3>
        <div>{children}</div>
      </div>
    </div>
  );
}

function usePeriodDates(period) {
  const now = new Date();
  const end = new Date(now);
  let start = new Date(now);
  let days = 1;

  if (period === 'today') {
    start.setHours(0,0,0,0);
    end.setHours(23,59,59,999);
    days = 1;
  } else if (period === 'week') {
    start.setDate(end.getDate() - 6);
    start.setHours(0,0,0,0);
    end.setHours(23,59,59,999);
    days = 7;
  } else if (period === 'month') {
    start.setDate(end.getDate() - 29);
    start.setHours(0,0,0,0);
    end.setHours(23,59,59,999);
    days = 30;
  } else if (period === 'year') {
    start.setDate(end.getDate() - 364);
    start.setHours(0,0,0,0);
    end.setHours(23,59,59,999);
    days = 365;
  }

  return {
    fromISO: start.toISOString(),
    toISO: end.toISOString(),
    days,
  };
}

function RingChart({ value = 0, limit = 1, size = 260, stroke = 22, onClickLimit }) {
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = limit > 0 ? Math.min(value / limit, 1) : 0;
  const offset = circumference * (1 - pct);

  return (
    <div className="flex flex-col items-center justify-center">
      <svg width={size} height={size}>
        <defs>
          <linearGradient id="grad2" x1="0%" x2="100%" y1="0%" y2="0%">
            <stop offset="0%" stopColor="#7c3aed" />
            <stop offset="100%" stopColor="#06b6d4" />
          </linearGradient>
        </defs>
        <g transform={`translate(${size/2}, ${size/2})`}>
          <circle r={radius} stroke="#f3f4f6" strokeWidth={stroke} fill="transparent" />
          <circle r={radius} stroke="url(#grad2)" strokeWidth={stroke} strokeLinecap="round" fill="transparent" strokeDasharray={`${circumference} ${circumference}`} strokeDashoffset={offset} transform={`rotate(-90)`} />

          <g>
            <circle r={radius - stroke} fill="#ffffff" />
            <foreignObject x={-(radius - stroke)} y={-(radius - stroke)} width={(radius - stroke) * 2} height={(radius - stroke) * 2}>
              <div className="w-full h-full flex flex-col items-center justify-center text-center p-2 select-none">
                <div className="text-xl font-bold">{value.toFixed(0)} ₽</div>
                <button type="button" onClick={onClickLimit} className="mt-2 text-sm px-3 py-1 rounded-full bg-gray-100 hover:bg-gray-200 transition-shadow">Изменить лимит</button>
              </div>
            </foreignObject>
          </g>
        </g>
      </svg>
    </div>
  );
}

export default function Dashboard() {
  usePageMeta('Главная', 'Управляйте доходами и расходами, следите за бюджетом.');
  const { user, isAdmin, logout, updateUser } = useAuth();
  const [spendings, setSpendings] = useState([]);
  const [incomes, setIncomes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [period, setPeriod] = useState('month');
  const periodDates = usePeriodDates(period);

  // Модалки для редактирования
  const [expenseModal, setExpenseModal] = useState({ isOpen: false, item: null });
  const [incomeModal, setIncomeModal] = useState({ isOpen: false, item: null });

  // Модалка для просмотра фото
  const [imageViewer, setImageViewer] = useState({ isOpen: false, url: '', title: '' });

  // Модалки для категорий и лимита
  const [openChangeLimit, setOpenChangeLimit] = useState(false);
  const [openCategoryModal, setOpenCategoryModal] = useState(false);
  const [openEditCategory, setOpenEditCategory] = useState(null);

  // формы
  const [limitInput, setLimitInput] = useState(0);
  const [categoryForm, setCategoryForm] = useState({ title: '', type_of_category: 'expense' });

  // Загрузка данных
  useEffect(() => {
    loadData();
  }, [period]);

  const categoriesById = useMemo(() => {
    const map = {};
    categories.forEach(cat => { map[cat.id] = cat; });
    return map;
  }, [categories]);

  const getCategoryName = (categoryId) => categoriesById[categoryId]?.title || `Категория ${categoryId}`;

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const categoriesData = await api.getCategories(100);
      setCategories(categoriesData.categories || []);

      const { fromISO, toISO } = periodDates;
      const spendingsData = await api.getSpendings({ from_date: fromISO, to_date: toISO, limit: 100 });
      const incomesData = await api.getIncomes({ from_date: fromISO, to_date: toISO, limit: 100 });

      setSpendings(spendingsData.data?.expenses || spendingsData.expenses || []);
      setIncomes(incomesData.data?.incomes || incomesData.incomes || []);

      try {
        const statsData = await api.getExpenseStats(period);
        setStats(statsData);
      } catch (e) { console.warn('Stats error', e); }
    } catch (e) {
      console.error(e);
      setError('Не удалось загрузить данные');
    } finally {
      setLoading(false);
    }
  }

  const refreshLists = () => loadData();

  // Удаление расходов и доходов (оставляем для кнопок в карточках)
  async function handleDeleteSpending(id) {
    if (!confirm('Удалить расход?')) return;
    try {
      await api.deleteSpending(id);
      await refreshLists();
    } catch (err) {
      console.error(err);
      alert('Не удалось удалить расход');
    }
  }

  async function handleDeleteIncome(id) {
    if (!confirm('Удалить доход?')) return;
    try {
      await api.deleteIncome(id);
      await refreshLists();
    } catch (err) {
      console.error(err);
      alert('Не удалось удалить доход');
    }
  }

  // Изменение лимита
  async function handleChangeLimit(e) {
    e.preventDefault();
    try {
      const newLimit = Number(limitInput);
      if (isNaN(newLimit)) return alert('Неверный лимит');
      const updated = await api.updateUserLimit(newLimit);
      updateUser(updated);
      setOpenChangeLimit(false);
    } catch (err) {
      console.error(err);
      alert('Не удалось изменить лимит');
    }
  }

  // Категории CRUD
  async function handleCreateCategory(e) {
    e.preventDefault();
    try {
      const created = await api.createCategory(categoryForm);
      setCategories(prev => [created, ...prev]);
      setOpenCategoryModal(false);
      setCategoryForm({ title: '', type_of_category: 'expense' });
    } catch (err) {
      console.error(err);
      alert('Не удалось создать категорию');
    }
  }

  async function handleSaveEditCategory(e) {
    e.preventDefault();
    try {
      const id = openEditCategory.id;
      const updated = await api.updateCategory(id, categoryForm);
      setCategories(prev => prev.map(c => c.id === updated.id ? updated : c));
      setOpenEditCategory(null);
      setCategoryForm({ title: '', type_of_category: 'expense' });
    } catch (err) {
      console.error(err);
      alert('Не удалось сохранить категорию');
    }
  }

  async function handleDeleteCategory(id) {
    if (!confirm('Удалить категорию?')) return;
    try {
      await api.deleteCategory(id);
      setCategories(prev => prev.filter(c => c.id !== id));
    } catch (err) {
      console.error(err);
      alert('Не удалось удалить категорию');
    }
  }

  // Получение URL изображения для просмотра
async function openImageViewer(id, type) {
  try {
    const token = localStorage.getItem('access_token');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    const endpoint = type === 'expense' ? `spending/${id}/image` : `income/${id}/image`;
    const response = await fetch(`${API_BASE}/${endpoint}`, { headers });
    if (!response.ok) throw new Error('Ошибка загрузки изображения');
    const data = await response.json(); // { url: "..." }
    const imageUrl = data;
    setImageViewer({
      isOpen: true,
      url: imageUrl,
      title: `${type === 'expense' ? 'Расход' : 'Доход'} #${id}`
    });
  } catch (err) {
    console.error(err);
    alert('Не удалось загрузить изображение');
  }
}

  // derived values
  const totalIncome = useMemo(() => incomes.reduce((s, it) => s + (it.value || it.amount || 0), 0), [incomes]);
  const totalSpending = useMemo(() => spendings.reduce((s, it) => s + (it.value || it.amount || 0), 0), [spendings]);
  const periodDays = periodDates.days;
  const periodLimit = (user?.day_expense_limit || 0) * periodDays;
  const balance = totalIncome - totalSpending;

  if (loading) return <div className="text-center mt-10">Загрузка...</div>;
  if (error) return <div className="text-center text-red-500 mt-10">{error}</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <header className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-6">
          <div className="text-2xl font-bold">FinanceTrack</div>
          <div className="flex gap-2">
            <button onClick={() => window.location.href = "/spending"} className="px-4 py-2 rounded-xl bg-blue-500 text-white hover:bg-blue-600">Все траты</button>
            <button onClick={() => window.location.href = "/income"} className="px-4 py-2 rounded-xl bg-green-500 text-white hover:bg-green-600">Все доходы</button>
          </div>
          {isAdmin && (
            <button onClick={() => window.location.href = "/stats"} className="px-4 py-2 rounded-xl bg-purple-600 text-white hover:bg-purple-700">Статистика</button>
          )}
        </div>
        <div>
          <span className="mr-4">Привет, {user?.username}</span>
          <button onClick={logout} className="text-sm text-red-600">Выйти</button>
        </div>
      </header>

      <div className="flex justify-center mb-8">
        <div className="inline-flex bg-white rounded-full shadow-lg p-1 border">
          {['today','week','month','year'].map(p => (
            <button key={p} onClick={() => setPeriod(p)} className={`px-6 py-2 rounded-full transition-all ${period === p ? 'bg-gradient-to-r from-purple-600 to-cyan-500 text-white shadow-md' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'}`}>
              {p === 'today' ? 'Сегодня' : p === 'week' ? 'Неделя' : p === 'month' ? 'Месяц' : 'Год'}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Расходы */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="font-bold text-xl text-gray-800">Расходы</h3>
            <button onClick={() => setExpenseModal({ isOpen: true, item: null })} className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-xl">+ Добавить</button>
          </div>
          <div className="space-y-3 max-h-[60vh] overflow-auto pr-2">
            {spendings.length === 0 && <div className="text-center text-gray-500 py-8">Нет расходов в выбранный период</div>}
            {spendings.map(s => (
              <div key={s.id} className="bg-red-50 rounded-xl p-4 border border-red-100 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <div className="text-xs text-gray-500 font-medium">{formatDateTime(s.expense_date)}</div>
                    <div className="text-sm font-semibold text-gray-800 mt-1">{getCategoryName(s.category_id)}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-red-600 text-lg">−{((s.value || s.amount) || 0).toFixed(2)} ₽</div>
                  </div>
                </div>
                {s.comment && <div className="text-xs text-gray-600 mt-2 bg-white/50 rounded px-2 py-1">{s.comment}</div>}
                <div className="flex gap-2 mt-3">
                  <button onClick={() => setExpenseModal({ isOpen: true, item: s })} className="flex-1 bg-white text-gray-700 px-3 py-2 rounded-lg text-sm border hover:bg-gray-50">Изменить</button>
                  <button onClick={() => handleDeleteSpending(s.id)} className="flex-1 bg-white text-red-600 px-3 py-2 rounded-lg text-sm border border-red-200 hover:bg-red-50">Удалить</button>
                  <button onClick={() => openImageViewer(s.id, 'expense')} className="bg-blue-100 text-blue-700 px-3 py-2 rounded-lg text-sm hover:bg-blue-200">Фото</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Центральная статистика */}
        <div className="flex flex-col items-center justify-start">
          <div className="w-full max-w-xs bg-white rounded-2xl shadow-lg p-6 mb-6">
            <div className="text-center">
              <div className="text-sm text-gray-500 font-medium">Лимит за период</div>
              <div className="text-2xl font-bold text-gray-800">{periodLimit.toFixed(0)} ₽</div>
            </div>
          </div>
          <RingChart value={totalSpending} limit={periodLimit || 1} onClickLimit={() => { setLimitInput(user?.day_expense_limit || 0); setOpenChangeLimit(true); }} />
          <CurrencyWidget />

          <div className="mt-6 text-center bg-white rounded-2xl shadow-lg p-6 w-full max-w-xs">
            <div className={`text-2xl font-bold ${balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>{balance.toFixed(2)} ₽</div>
            <div className="text-sm text-gray-500 mt-2">Доход: <span className="font-semibold text-green-600">{totalIncome.toFixed(0)} ₽</span></div>
            <div className="text-sm text-gray-500">Расход: <span className="font-semibold text-red-600">{totalSpending.toFixed(0)} ₽</span></div>
          </div>
        </div>

        {/* Доходы и категории */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="font-bold text-xl text-gray-800">Доходы</h3>
              <button onClick={() => setIncomeModal({ isOpen: true, item: null })} className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-xl">+ Добавить</button>
            </div>
            <div className="space-y-3 max-h-[50vh] overflow-auto pr-2">
              {incomes.length === 0 && <div className="text-center text-gray-500 py-8">Нет доходов в выбранный период</div>}
              {incomes.map(i => (
                <div key={i.id} className="bg-green-50 rounded-xl p-4 border border-green-100 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <div className="text-xs text-gray-500 font-medium">{formatDateTime(i.income_date)}</div>
                      <div className="text-sm font-semibold text-gray-800 mt-1">{i.comment || getCategoryName(i.category_id) || 'Доход'}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-green-600 text-lg">+{((i.value || i.amount) || 0).toFixed(2)} ₽</div>
                    </div>
                  </div>
                  {i.comment && i.comment !== getCategoryName(i.category_id) && <div className="text-xs text-gray-600 mt-2 bg-white/50 rounded px-2 py-1">{i.comment}</div>}
                  <div className="flex gap-2 mt-3">
                    <button onClick={() => setIncomeModal({ isOpen: true, item: i })} className="flex-1 bg-white text-gray-700 px-3 py-2 rounded-lg text-sm border hover:bg-gray-50">Изменить</button>
                    <button onClick={() => handleDeleteIncome(i.id)} className="flex-1 bg-white text-red-600 px-3 py-2 rounded-lg text-sm border border-red-200 hover:bg-red-50">Удалить</button>
                    <button onClick={() => openImageViewer(i.id, 'income')} className="bg-blue-100 text-blue-700 px-3 py-2 rounded-lg text-sm hover:bg-blue-200">Фото</button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Категории */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h4 className="font-bold text-lg text-gray-800">Категории</h4>
              <button onClick={() => setOpenCategoryModal(true)} className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded-lg text-sm">+ Добавить</button>
            </div>
            <div className="space-y-2 max-h-[40vh] overflow-auto">
              {categories.map(c => (
                <div key={c.id} className="flex items-center justify-between bg-gray-50 px-4 py-3 rounded-lg hover:bg-gray-100">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${c.type_of_category === 'expense' ? 'bg-red-500' : 'bg-green-500'}`}></div>
                    <div>
                      <div className="font-medium text-gray-800">{c.title}</div>
                      <div className="text-xs text-gray-500 capitalize">{c.type_of_category}</div>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button onClick={() => { setOpenEditCategory(c); setCategoryForm({ title: c.title, type_of_category: c.type_of_category }); }} className="bg-white px-2 py-1 rounded text-xs border">Изм.</button>
                    <button onClick={() => handleDeleteCategory(c.id)} className="bg-white px-2 py-1 rounded text-xs border border-red-200 text-red-600 hover:bg-red-50">Удал.</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Модалки */}
      <EditExpenseModal isOpen={expenseModal.isOpen} onClose={() => setExpenseModal({ isOpen: false, item: null })} item={expenseModal.item} onSuccess={refreshLists} />
      <EditIncomeModal isOpen={incomeModal.isOpen} onClose={() => setIncomeModal({ isOpen: false, item: null })} item={incomeModal.item} onSuccess={refreshLists} />
      <ImageViewerModal isOpen={imageViewer.isOpen} onClose={() => setImageViewer({ isOpen: false, url: '', title: '' })} imageUrl={imageViewer.url} title={imageViewer.title} />

      <Modal open={openChangeLimit} onClose={() => setOpenChangeLimit(false)} title="Изменить дневной лимит">
        <form onSubmit={handleChangeLimit} className="space-y-4">
          <input type="number" value={limitInput} onChange={e => setLimitInput(e.target.value)} className="w-full border rounded-lg px-3 py-2" placeholder="Новый лимит" />
          <div className="flex justify-end gap-3 pt-4">
            <button type="button" onClick={() => setOpenChangeLimit(false)} className="px-6 py-2 rounded-lg bg-gray-200">Отмена</button>
            <button type="submit" className="px-6 py-2 rounded-lg bg-violet-600 text-white">Сохранить</button>
          </div>
        </form>
      </Modal>

      <Modal open={openCategoryModal} onClose={() => setOpenCategoryModal(false)} title="Создать категорию">
        <form onSubmit={handleCreateCategory} className="space-y-4">
          <input type="text" value={categoryForm.title} onChange={e => setCategoryForm({ ...categoryForm, title: e.target.value })} className="w-full border rounded-lg px-3 py-2" placeholder="Название" />
          <select value={categoryForm.type_of_category} onChange={e => setCategoryForm({ ...categoryForm, type_of_category: e.target.value })} className="w-full border rounded-lg px-3 py-2">
            <option value="expense">Расход</option>
            <option value="income">Доход</option>
          </select>
          <div className="flex justify-end gap-3 pt-4">
            <button type="button" onClick={() => setOpenCategoryModal(false)} className="px-6 py-2 rounded-lg bg-gray-200">Отмена</button>
            <button type="submit" className="px-6 py-2 rounded-lg bg-green-600 text-white">Создать</button>
          </div>
        </form>
      </Modal>

      <Modal open={!!openEditCategory} onClose={() => setOpenEditCategory(null)} title="Редактировать категорию">
        {openEditCategory && (
          <form onSubmit={handleSaveEditCategory} className="space-y-4">
            <input type="text" defaultValue={openEditCategory.title} onChange={e => setCategoryForm(f => ({ ...f, title: e.target.value }))} className="w-full border rounded-lg px-3 py-2" />
            <select defaultValue={openEditCategory.type_of_category} onChange={e => setCategoryForm(f => ({ ...f, type_of_category: e.target.value }))} className="w-full border rounded-lg px-3 py-2">
              <option value="expense">Расход</option>
              <option value="income">Доход</option>
            </select>
            <div className="flex justify-end gap-3 pt-4">
              <button type="button" onClick={() => setOpenEditCategory(null)} className="px-6 py-2 rounded-lg bg-gray-200">Отмена</button>
              <button type="submit" className="px-6 py-2 rounded-lg bg-violet-600 text-white">Сохранить</button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
}