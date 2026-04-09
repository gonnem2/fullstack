import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import Income from '../../pages/Income';
import { IncomeAPI, CategoryAPI } from '../../api/api';

vi.mock('../../api/api', () => ({
  IncomeAPI: {
    list: vi.fn(),
    delete: vi.fn(),
  },
  CategoryAPI: {
    list: vi.fn(),
  },
}));

describe('Income Page', () => {
  const mockCategories = { categories: [{ id: 1, title: 'Зарплата' }] };
  const mockIncomes = {
    data: {
      incomes: [
        { id: 1, income_date: '2025-01-01T10:00:00', category_id: 1, value: 500, comment: 'Зарплата январь' }
      ]
    }
  };

  beforeEach(() => {
    vi.clearAllMocks();
    CategoryAPI.list.mockResolvedValue(mockCategories);
    IncomeAPI.list.mockResolvedValue(mockIncomes);
  });

  it('отображает список доходов', async () => {
    render(<Income />);
    await waitFor(() => {
      expect(screen.getByText('Зарплата')).toBeInTheDocument();
      expect(screen.getByText('500 ₽')).toBeInTheDocument();
      expect(screen.getByText('Зарплата январь')).toBeInTheDocument();
    });
  });
});