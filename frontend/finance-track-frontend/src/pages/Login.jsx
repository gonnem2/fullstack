import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { usePageMeta } from '../hooks/usePageMeta';

export default function Login() {
  usePageMeta('Вход', 'Войдите в свой аккаунт FinanceTrack для управления финансами.');

  const [form, setForm] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login(form);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Ошибка входа. Проверьте логин и пароль.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex items-center justify-center min-h-[70vh]">
      <div className="w-[380px] bg-white p-6 rounded-xl shadow">
        <h1 className="text-xl font-semibold mb-4">Вход в аккаунт</h1>

        {error && (
          <div role="alert" className="mb-4 p-3 bg-red-50 text-red-700 rounded-md text-sm">
            {error}
          </div>
        )}

        <form onSubmit={submit} className="space-y-3" noValidate>
          <input
            required
            value={form.username}
            onChange={e => setForm({ ...form, username: e.target.value })}
            className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Имя пользователя"
            autoComplete="username"
            disabled={loading}
            aria-label="Имя пользователя"
          />
          <input
            required
            value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })}
            type="password"
            className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Пароль"
            autoComplete="current-password"
            disabled={loading}
            aria-label="Пароль"
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-3 rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Вход...' : 'Войти'}
          </button>
        </form>

        <p className="text-sm text-gray-500 mt-3">
          Нет аккаунта?{' '}
          <Link to="/register" className="text-indigo-600 hover:text-indigo-800">
            Зарегистрироваться
          </Link>
        </p>
      </div>
    </main>
  );
}
