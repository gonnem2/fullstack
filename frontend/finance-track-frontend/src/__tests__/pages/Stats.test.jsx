import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Stats from '../../pages/Stats';
import api from '../../api/api';

vi.mock('../../api/api', () => ({
  default: {
    getExpenseStats: vi.fn(),
    getDynamicStats: vi.fn(),
  },
}));

describe('Stats Page', () => {
  const mockCategories = { categories: [{ title: 'Еда', amount: 300 }], total: 300 };
  const mockDynamic = [{ date: '2025-01-01', amount: 100 }, { date: '2025-01-02', amount: 200 }];

  beforeEach(() => {
    vi.clearAllMocks();
    api.getExpenseStats.mockResolvedValue(mockCategories);
    api.getDynamicStats.mockResolvedValue(mockDynamic);
  });

  const renderWithRouter = (ui) => render(<MemoryRouter>{ui}</MemoryRouter>);

  it('загружает и отображает статистику', async () => {
    renderWithRouter(<Stats />);
    await waitFor(() => {
      expect(screen.getByText('Расходы за период — 300 ₽')).toBeInTheDocument();
      expect(screen.getByText('Еда')).toBeInTheDocument();
      expect(screen.getByText('300 ₽')).toBeInTheDocument();
    });
  });

  it('меняет период при клике', async () => {
    renderWithRouter(<Stats />);
    const weekBtn = await screen.findByText('Неделя');
    fireEvent.click(weekBtn);
    await waitFor(() => {
      expect(api.getExpenseStats).toHaveBeenCalledWith('week');
      expect(api.getDynamicStats).toHaveBeenCalledWith('week');
    });
  });
});