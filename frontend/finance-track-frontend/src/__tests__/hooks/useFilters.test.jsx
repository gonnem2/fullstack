// src/__tests__/hooks/useFilters.test.jsx
import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { useFilters } from '../../hooks/useFilters';

// Обёртка с роутером (useFilters использует useSearchParams)
function wrapper({ children }) {
  return <MemoryRouter>{children}</MemoryRouter>;
}

describe('useFilters', () => {

  it('возвращает дефолтные значения при пустом URL', () => {
    const { result } = renderHook(() => useFilters(), { wrapper });
    const { filters } = result.current;

    expect(filters.search).toBe('');
    expect(filters.type).toBe('');
    expect(filters.sort_by).toBe('date');
    expect(filters.sort_order).toBe('desc');
    expect(filters.page).toBe(1);
    expect(filters.page_size).toBe(20);
  });

  it('setFilter обновляет конкретный фильтр', () => {
    const { result } = renderHook(() => useFilters(), { wrapper });

    act(() => {
      result.current.setFilter({ search: 'еда' });
    });

    expect(result.current.filters.search).toBe('еда');
  });

  it('setFilter сбрасывает страницу на 1 при изменении не-page поля', () => {
    const { result } = renderHook(() => useFilters(), { wrapper });

    // Сначала перейдём на страницу 3
    act(() => { result.current.setFilter({ page: 3 }); });
    expect(result.current.filters.page).toBe(3);

    // Теперь меняем фильтр — page должен вернуться к 1
    act(() => { result.current.setFilter({ type: 'expense' }); });
    expect(result.current.filters.page).toBe(1);
    expect(result.current.filters.type).toBe('expense');
  });

  it('resetFilters очищает все фильтры', () => {
    const { result } = renderHook(() => useFilters(), { wrapper });

    act(() => { result.current.setFilter({ search: 'test', type: 'income' }); });
    act(() => { result.current.resetFilters(); });

    expect(result.current.filters.search).toBe('');
    expect(result.current.filters.type).toBe('');
  });

  it('toQueryString включает только непустые параметры', () => {
    const { result } = renderHook(() => useFilters(), { wrapper });

    act(() => { result.current.setFilter({ search: 'обед', type: '' }); });

    const qs = result.current.toQueryString();
  expect(qs).toContain('search=%D0%BE%D0%B1%D0%B5%D0%B4');
    expect(qs).not.toContain('type=');
  });

  it('setFilter удаляет параметр при значении пустой строки', () => {
    const { result } = renderHook(() => useFilters(), { wrapper });

    act(() => { result.current.setFilter({ search: 'тест' }); });
    act(() => { result.current.setFilter({ search: '' }); });

    expect(result.current.toQueryString()).not.toContain('search');
  });
});