// src/__tests__/setup.js
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// ── Мок localStorage ─────────────────────────────────────────────────────────
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] ?? null,
    setItem: (key, val) => { store[key] = String(val); },
    removeItem: (key) => { delete store[key]; },
    clear: () => { store = {}; },
  };
})();

Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// ── Мок window.confirm ────────────────────────────────────────────────────────
window.confirm = vi.fn(() => true);

// ── Мок fetch (глобальный) ────────────────────────────────────────────────────
// Каждый тест переопределяет vi.fn() сам при необходимости
global.fetch = vi.fn();

afterEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});