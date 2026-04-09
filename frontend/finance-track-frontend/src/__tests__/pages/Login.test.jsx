// src/__tests__/pages/Login.test.jsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import Login from '../../pages/Login';

// Мокируем useAuth
vi.mock('../../contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}));

// Мокируем usePageMeta чтобы не менял document.title
vi.mock('../../hooks/usePageMeta', () => ({
  usePageMeta: vi.fn(),
}));

import { useAuth } from '../../contexts/AuthContext';

function renderLogin() {
  return render(
    <MemoryRouter initialEntries={['/login']}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<div>Dashboard</div>} />
      </Routes>
    </MemoryRouter>
  );
}

describe('Login page', () => {

  it('рендерит форму входа', () => {
    useAuth.mockReturnValue({ login: vi.fn() });
    renderLogin();
    expect(screen.getByPlaceholderText(/имя пользователя/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/пароль/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /войти/i })).toBeInTheDocument();
  });

  it('кнопка задизейблена во время загрузки', async () => {
    const login = vi.fn(() => new Promise(() => {})); // никогда не резолвится
    useAuth.mockReturnValue({ login });

    renderLogin();

    fireEvent.change(screen.getByPlaceholderText(/имя пользователя/i), {
      target: { value: 'user' },
    });
    fireEvent.change(screen.getByPlaceholderText(/пароль/i), {
      target: { value: 'pass' },
    });
    fireEvent.click(screen.getByRole('button', { name: /войти/i }));

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /вход\.\.\./i })).toBeDisabled();
    });
  });

  it('показывает ошибку при неверных учётных данных', async () => {
    const login = vi.fn(() => Promise.reject(new Error('Неверный пароль')));
    useAuth.mockReturnValue({ login });

    renderLogin();

    fireEvent.change(screen.getByPlaceholderText(/имя пользователя/i), {
      target: { value: 'user' },
    });
    fireEvent.change(screen.getByPlaceholderText(/пароль/i), {
      target: { value: 'wrongpass' },
    });
    fireEvent.click(screen.getByRole('button', { name: /войти/i }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText(/неверный пароль/i)).toBeInTheDocument();
    });
  });

  it('редиректит на /dashboard после успешного входа', async () => {
    const login = vi.fn(() => Promise.resolve());
    useAuth.mockReturnValue({ login });

    renderLogin();

    fireEvent.change(screen.getByPlaceholderText(/имя пользователя/i), {
      target: { value: 'user' },
    });
    fireEvent.change(screen.getByPlaceholderText(/пароль/i), {
      target: { value: 'pass123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /войти/i }));

    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });
  });

  it('есть ссылка на регистрацию', () => {
    useAuth.mockReturnValue({ login: vi.fn() });
    renderLogin();
    expect(screen.getByRole('link', { name: /зарегистрироваться/i })).toBeInTheDocument();
  });
});