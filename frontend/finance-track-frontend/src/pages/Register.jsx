import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { auth } from '../api/api.js';
import { usePageMeta } from '../hooks/usePageMeta';

export default function Register() {
  usePageMeta('Регистрация', 'Создайте аккаунт FinanceTrack и начните вести учёт своих финансов.');

  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const nav = useNavigate();

  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (form.password !== form.confirmPassword) {
      setError('Пароли не совпадают');
      setLoading(false);
      return;
    }

    try {
      await auth.register({ username: form.username, email: form.email, password: form.password });
      await auth.login({ username: form.username, password: form.password });
      nav('/dashboard');
    } catch (err) {
      setError(err.message || 'Ошибка регистрации. Попробуйте снова.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex items-center justify-center min-h-[70vh]">
      <div className="w-[380px] bg-white p-6 rounded-xl shadow">
        <h1 className="text-xl font-semibold mb-4">Регистрация</h1>

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
            type="email"
            value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })}
            className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Email"
            autoComplete="email"
            disabled={loading}
            aria-label="Email"
          />
          <input
            required
            value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })}
            type="password"
            className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Пароль"
            autoComplete="new-password"
            disabled={loading}
            aria-label="Пароль"
          />
          <input
            required
            value={form.confirmPassword}
            onChange={e => setForm({ ...form, confirmPassword: e.target.value })}
            type="password"
            className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Подтвердите пароль"
            autoComplete="new-password"
            disabled={loading}
            aria-label="Подтвердите пароль"
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-3 rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Регистрация...' : 'Зарегистрироваться'}
          </button>
        </form>

        <p className="text-sm text-gray-500 mt-3">
          Уже есть аккаунт?{' '}
          <Link to="/login" className="text-indigo-600 hover:text-indigo-800">
            Войти
          </Link>
        </p>
      </div>
    </main>
  );
}
