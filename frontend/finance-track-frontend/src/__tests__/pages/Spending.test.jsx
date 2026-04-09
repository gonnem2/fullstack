import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Spending from '../../pages/Spending';
import { SpendingAPI, CategoryAPI } from '../../api/api';

vi.mock('../../api/api', () => ({
  SpendingAPI: {
    list: vi.fn(),
    delete: vi.fn(),
  },
  CategoryAPI: {
    list: vi.fn(),
  },
}));

describe('Spending Page', () => {
  const mockCategories = { categories: [{ id: 1, title: 'Еда', type_of_category: 'expense' }] };
  const mockExpenses = {
    data: { expenses: [{ id: 1, expense_date: '2025-01-01T12:00:00', category_id: 1, value: 150, comment: 'Обед' }] },
    total: 1,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    CategoryAPI.list.mockResolvedValue(mockCategories);
    SpendingAPI.list.mockResolvedValue(mockExpenses);
  });

  it('отображает список расходов', async () => {
    render(<Spending />);
    // Ждём, пока исчезнет "Загрузка..."
    await waitFor(() => {
      expect(screen.queryByText('Загрузка...')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Обед')).toBeInTheDocument();
    expect(screen.getByText('150 ₽')).toBeInTheDocument();
    // "Еда" встречается дважды (в select и в строке), поэтому используем getAllByText
    expect(screen.getAllByText('Еда').length).toBeGreaterThan(0);
  });

  it('фильтрует по поиску', async () => {
    render(<Spending />);
    await waitFor(() => expect(screen.queryByText('Загрузка...')).not.toBeInTheDocument());
    const searchInput = screen.getByPlaceholderText('комментарий...');
    fireEvent.change(searchInput, { target: { value: 'Обед' } });
    await waitFor(() => {
      expect(SpendingAPI.list).toHaveBeenCalledWith(expect.stringContaining('search=%D0%9E%D0%B1%D0%B5%D0%B4'));
    });
  });

  it('сбрасывает фильтры', async () => {
    render(<Spending />);
    await waitFor(() => expect(screen.queryByText('Загрузка...')).not.toBeInTheDocument());
    const resetBtn = screen.getByText('Сбросить фильтры');
    fireEvent.click(resetBtn);
    await waitFor(() => {
      expect(screen.getByPlaceholderText('комментарий...')).toHaveValue('');
    });
  });
});