import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Tab = ({ to, children }) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      'px-3 py-2 rounded-md text-sm font-medium ' +
      (isActive ? 'bg-indigo-600 text-white' : 'text-gray-200 hover:bg-indigo-500 hover:text-white')
    }
  >
    {children}
  </NavLink>
);

export default function Header() {
  const { isAuthenticated, isAdmin, logout } = useAuth();

  return (
    <header className="bg-gray-900">
      <div className="max-w-6xl mx-auto flex items-center justify-between p-4">
        <div className="flex items-center gap-3">
          <div className="text-2xl">📈</div>
          <div className="text-white font-bold">FinanceTrack</div>
        </div>
        <nav className="flex items-center gap-2">
          <Tab to="/dashboard">Главная</Tab>
          <Tab to="/stats">Статистика</Tab>
          {isAdmin && <Tab to="/admin/users">Админ</Tab>}
          {isAuthenticated ? (
            <button onClick={logout} className="text-sm text-red-300 hover:text-red-100">
              Выйти
            </button>
          ) : (
            <Tab to="/login">Войти</Tab>
          )}
        </nav>
      </div>
    </header>
  );
}