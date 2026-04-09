import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import TransactionList from '../../pages/TransactionList';
import { TransactionAPI } from '../../api/api';
import { useFilters } from '../../hooks/useFilters';

vi.mock('../../api/api', () => ({
  TransactionAPI: {
    list: vi.fn(),
    delete: vi.fn(),
    categories: vi.fn(),
  },
}));
vi.mock('../../hooks/useFilters', () => ({
  useFilters: vi.fn(),
}));
vi.mock('../../components/FilterPanel', () => ({ default: () => <div>FilterPanel</div> }));
vi.mock('../../components/Pagination', () => ({ default: () => <div>Pagination</div> }));
vi.mock('../../components/TransactionModal', () => ({ default: () => <div>TransactionModal</div> }));

describe('TransactionList', () => {
  const mockFilters = { filters: { page: 1, page_size: 20, sort_by: 'date', sort_order: 'desc' }, setFilter: vi.fn(), toQueryString: vi.fn(() => ''), resetFilters: vi.fn() };
  const mockData = { items: [{ id: 1, type: 'expense', date: '2025-01-01', category: 'Еда', amount: 150, description: 'Обед' }], total: 1, pages: 1 };
  const mockCategories = ['Еда', 'Транспорт'];

  beforeEach(() => {
    vi.clearAllMocks();
    useFilters.mockReturnValue(mockFilters);
    TransactionAPI.list.mockResolvedValue(mockData);
    TransactionAPI.categories.mockResolvedValue(mockCategories);
  });

  const renderWithRouter = (ui) => render(<MemoryRouter>{ui}</MemoryRouter>);

  it('отображает список транзакций', async () => {
    renderWithRouter(<TransactionList />);
    await waitFor(() => {
      expect(screen.getByText('Обед')).toBeInTheDocument();
      // В таблице сумма отображается как "−150,00 ₽" (с пробелом и запятой)
      expect(screen.getByText(/150,00/)).toBeInTheDocument();
      expect(screen.getByText('Еда')).toBeInTheDocument();
    });
  });

  it('открывает модалку создания новой транзакции', async () => {
    renderWithRouter(<TransactionList />);
    const addBtn = await screen.findByText('+ Новая транзакция');
    fireEvent.click(addBtn);
    await waitFor(() => {
      expect(screen.getByText('TransactionModal')).toBeInTheDocument();
    });
  });
});