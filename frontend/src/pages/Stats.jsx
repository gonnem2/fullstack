import React, { useEffect, useState } from 'react';
import {
  PieChart, Pie, Cell,
  LineChart, Line,
  CartesianGrid, XAxis, YAxis, Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Link } from 'react-router-dom';
import api from '../api/api';
import { usePageMeta } from '../hooks/usePageMeta';

// JSON-LD структурированные данные для страницы статистики
function StatsJsonLd() {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    name: 'Статистика расходов — FinanceTrack',
    description: 'Анализ расходов по категориям и динамика трат за выбранный период.',
    url: 'https://financetrack.example.com/stats',
    isPartOf: {
      '@type': 'WebSite',
      name: 'FinanceTrack',
      url: 'https://financetrack.example.com',
    },
  };
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  );
}

export default function Stats() {
  usePageMeta('Статистика', 'Анализ расходов по категориям и динамика трат за выбранный период.');

  const [period, setPeriod] = useState('today');
  const [categories, setCategories] = useState([]);
  const [dynamic, setDynamic] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const PERIOD_MAP = { 'Сегодня': 'today', 'Неделя': 'week', 'Месяц': 'month', 'Год': 'year' };
  const COLORS = ['#7b61ff', '#61a0ff', '#61ffc7', '#ffb661', '#ff6161', '#9c61ff'];

  async function loadStats() {
    try {
      setLoading(true);
      setError(null);
      const [catRes, dynRes] = await Promise.all([
        api.getExpenseStats(period),
        api.getDynamicStats(period),
      ]);
      setCategories(catRes.categories || []);
      setTotal(catRes.total || 0);
      setDynamic(Array.isArray(dynRes) ? dynRes : []);
    } catch (e) {
      setError('Не удалось загрузить статистику');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadStats(); }, [period]);

  return (
    <>
      <StatsJsonLd />
      <div className="max-w-6xl mx-auto py-8">
        <header className="bg-white shadow mb-8">
          <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <Link to="/dashboard" className="text-xl font-bold text-[#7b61ff] hover:opacity-80 transition">
              FinanceTrack
            </Link>
            <h1 className="text-xl font-semibold text-gray-700">Статистика</h1>
          </div>
        </header>

        <nav aria-label="Период статистики" className="flex justify-center gap-3 mb-8">
          {Object.keys(PERIOD_MAP).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(PERIOD_MAP[p])}
              aria-pressed={PERIOD_MAP[p] === period}
              className={`px-4 py-1 rounded-full text-sm font-medium transition ${
                PERIOD_MAP[p] === period
                  ? 'bg-[#7b61ff] text-white shadow-md'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {p}
            </button>
          ))}
        </nav>

        {loading ? (
          <div className="text-center text-gray-500" aria-live="polite">Загрузка...</div>
        ) : error ? (
          <div className="text-center text-red-500" role="alert">{error}</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Круговая диаграмма */}
            <section className="bg-white shadow-lg rounded-2xl p-4 flex flex-col items-center">
              <h2 className="text-lg font-semibold mb-2 text-gray-700">
                Расходы за период — {total} ₽
              </h2>
              {categories.length === 0 ? (
                <p className="text-gray-400 py-16">Нет данных за выбранный период</p>
              ) : (
                <>
                  <ResponsiveContainer width="100%" height={320}>
                    <PieChart>
                      <Pie
                        data={categories}
                        cx="50%"
                        cy="50%"
                        outerRadius={110}
                        dataKey="amount"
                        label={(e) => `${e.title}: ${((e.amount / (total || 1)) * 100).toFixed(0)}%`}
                      >
                        {categories.map((_, i) => (
                          <Cell key={i} fill={COLORS[i % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(v) => `${v} ₽`} />
                    </PieChart>
                  </ResponsiveContainer>
                  <ul className="mt-4 space-y-2 w-full">
                    {categories.map((c, i) => (
                      <li key={i} className="flex items-center gap-2 text-sm">
                        <span className="w-4 h-4 rounded" style={{ background: COLORS[i % COLORS.length] }} />
                        <span className="font-medium">{c.title}</span>
                        <span className="text-gray-600 ml-auto">{c.amount} ₽</span>
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </section>

            {/* Линейный график */}
            <section className="bg-white shadow-lg rounded-2xl p-4">
              <h2 className="text-lg font-semibold mb-4 text-gray-700">Динамика расходов</h2>
              {dynamic.length === 0 ? (
                <p className="text-gray-400 flex items-center justify-center h-64">Нет данных</p>
              ) : (
                <ResponsiveContainer width="100%" height={320}>
                  <LineChart data={dynamic}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tickFormatter={(d) => String(d).slice(5, 10)} />
                    <YAxis />
                    <Tooltip formatter={(v) => `${v} ₽`} labelFormatter={(v) => `Дата: ${v}`} />
                    <Line type="monotone" dataKey="amount" stroke="#7b61ff" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </section>
          </div>
        )}
      </div>
    </>
  );
}
