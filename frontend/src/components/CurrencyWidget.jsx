import { useEffect, useState } from 'react';

const API_BASE = import.meta.env.VITE_API_URL?.replace('/api/v1', '') ?? 'http://localhost:8000';

/**
 * Виджет курсов валют — сторонний API через бэкенд-прокси.
 * Если бэкенд недоступен — graceful degradation (ничего не рендерит).
 */
export default function CurrencyWidget() {
  const [rates, setRates] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    fetch(`${API_BASE}/api/v1/currency/rates`, { signal: controller.signal })
      .then((r) => {
        if (!r.ok) throw new Error('bad response');
        return r.json();
      })
      .then((data) => {
        if (!cancelled) setRates(data);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      })
      .finally(() => {
        clearTimeout(timeout);
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
      controller.abort();
    };
  }, []);

  // Graceful degradation: если ошибка — не показываем виджет вообще
  if (error) return null;

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-4 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/2 mb-3" />
        <div className="h-3 bg-gray-100 rounded w-3/4 mb-2" />
        <div className="h-3 bg-gray-100 rounded w-2/3" />
      </div>
    );
  }

  if (!rates) return null;

  const items = [
    { code: 'USD', label: 'Доллар США',    value: rates.usd },
    { code: 'EUR', label: 'Евро',           value: rates.eur },
    { code: 'CNY', label: 'Юань',           value: rates.cny },
  ].filter((i) => i.value != null);

  if (items.length === 0) return null;

  return (
    <section
      className="bg-white rounded-2xl shadow-lg p-4"
      aria-label="Курсы валют"
    >
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
        Курсы валют к рублю
      </h3>
      <ul className="space-y-2">
        {items.map(({ code, label, value }) => (
          <li key={code} className="flex justify-between items-center text-sm">
            <span className="text-gray-700">{label}</span>
            <span className="font-semibold text-gray-900">
              {value.toFixed(2)} ₽
            </span>
          </li>
        ))}
      </ul>
      {rates.updated_at && (
        <p className="text-xs text-gray-400 mt-3">
          Обновлено: {new Date(rates.updated_at).toLocaleString('ru-RU')}
        </p>
      )}
    </section>
  );
}
