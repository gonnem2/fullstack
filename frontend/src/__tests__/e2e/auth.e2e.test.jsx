// src/__tests__/e2e/auth.e2e.test.jsx
/**
 * E2E-сценарии аутентификации.
 * Тесты работают в jsdom, fetch полностью мокируется.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

vi.mock('../../hooks/usePageMeta', () => ({ usePageMeta: vi.fn() }));

// Мок api.js
vi.mock('../../api/api', () => {
  const auth = {
    login: vi.fn(),
    logout: vi.fn(),
    register: vi.fn(),
    isAuthenticated: vi.fn(() => false),
  };
  const api = {
    auth,
    getProfile: vi.fn(),
    getCategories: vi.fn(() => Promise.resolve({ categories: [] })),
    getSpendings: vi.fn(() => Promise.resolve({ data: { expenses: [] }, total: 0 })),
    getIncomes: vi.fn(() => Promise.resolve({ data: { incomes: [] }, total: 0 })),
    getExpenseStats: vi.fn(() => Promise.resolve({ categories: [], total: 0 })),
    getDynamicStats: vi.fn(() => Promise.resolve([])),
    updateUserLimit: vi.fn(),
  };
  return { default: api, auth };
});

import api, { auth } from '../../api/api';
import { AuthProvider } from '../../contexts/AuthContext';
import Login from '../../pages/Login';
import Register from '../../pages/Register';

function App() {
  return (
    <AuthProvider>
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login"    element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<div>Dashboard Page</div>} />
        </Routes>
      </MemoryRouter>
    </AuthProvider>
  );
}

describe('E2E: Аутентификация', () => {

  beforeEach(() => {
    vi.clearAllMocks();
    auth.isAuthenticated.mockReturnValue(false);
    api.getProfile.mockResolvedValue({
      id: 1,
      username: 'testuser',
      email: 'test@test.com',
      role: 'user',
      day_expense_limit: 1000,
    });
  });

  it('Сценарий: успешный вход → попадаем на dashboard', async () => {
    auth.login.mockResolvedValue({
      access_token: 'fake-token',
      refresh_token: 'fake-refresh',
    });

    render(<App />);

    fireEvent.change(screen.getByPlaceholderText(/имя пользователя/i), {
      target: { value: 'testuser' },
    });
    fireEvent.change(screen.getByPlaceholderText(/пароль/i), {
      target: { value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /войти/i }));

    await waitFor(() => {
      expect(screen.getByText('Dashboard Page')).toBeInTheDocument();
    });

    expect(auth.login).toHaveBeenCalledWith({
      username: 'testuser',
      password: 'password123',
    });
  });

  it('Сценарий: неверные данные → остаёмся на login с ошибкой', async () => {
    auth.login.mockRejectedValue(new Error('Неверный логин или пароль'));

    render(<App />);

    fireEvent.change(screen.getByPlaceholderText(/имя пользователя/i), {
      target: { value: 'baduser' },
    });
    fireEvent.change(screen.getByPlaceholderText(/пароль/i), {
      target: { value: 'badpass' },
    });
    fireEvent.click(screen.getByRole('button', { name: /войти/i }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    // Всё ещё на странице login
    expect(screen.getByRole('button', { name: /войти/i })).toBeInTheDocument();
  });

  it('Сценарий: регистрация → автологин → dashboard', async () => {
    auth.register.mockResolvedValue({ id: 2, username: 'newuser' });
    auth.login.mockResolvedValue({
      access_token: 'token',
      refresh_token: 'refresh',
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/register']}>
          <Routes>
            <Route path="/login"     element={<Login />} />
            <Route path="/register"  element={<Register />} />
            <Route path="/dashboard" element={<div>Dashboard Page</div>} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    fireEvent.change(screen.getByPlaceholderText(/имя пользователя/i), {
      target: { value: 'newuser' },
    });
    fireEvent.change(screen.getByPlaceholderText(/email/i), {
      target: { value: 'new@example.com' },
    });
    // Находим поля пароля по порядку
    const passFields = screen.getAllByPlaceholderText(/пароль/i);
    fireEvent.change(passFields[0], { target: { value: 'secret123' } });
    fireEvent.change(passFields[1], { target: { value: 'secret123' } });

    fireEvent.click(screen.getByRole('button', { name: /зарегистрироваться/i }));

    await waitFor(() => {
      expect(screen.getByText('Dashboard Page')).toBeInTheDocument();
    });
  });

  it('Сценарий: регистрация с несовпадающими паролями → ошибка', async () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/register']}>
          <Routes>
            <Route path="/register" element={<Register />} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    fireEvent.change(screen.getByPlaceholderText(/имя пользователя/i), {
      target: { value: 'user' },
    });
    fireEvent.change(screen.getByPlaceholderText(/email/i), {
      target: { value: 'u@u.com' },
    });
    const passFields = screen.getAllByPlaceholderText(/пароль/i);
    fireEvent.change(passFields[0], { target: { value: 'pass1' } });
    fireEvent.change(passFields[1], { target: { value: 'pass2' } });

    fireEvent.click(screen.getByRole('button', { name: /зарегистрироваться/i }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText(/пароли не совпадают/i)).toBeInTheDocument();
    });

    // Внешний API не вызывался
    expect(auth.register).not.toHaveBeenCalled();
  });
});