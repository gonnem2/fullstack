import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import EditExpenseModal from '../../components/EditExpenseModal';
import { SpendingAPI, CategoryAPI, FileAPI } from '../../api/api';

vi.mock('../../api/api', () => ({
  SpendingAPI: {
    update: vi.fn(),
    create: vi.fn(),
    delete: vi.fn(),
  },
  CategoryAPI: {
    list: vi.fn(),
  },
  FileAPI: {
    upload: vi.fn(),
  },
}));

describe('EditExpenseModal', () => {
  const mockCategories = { categories: [{ id: 1, title: 'Еда', type_of_category: 'expense' }] };
  const mockItem = { id: 1, expense_date: '2025-01-01T12:00:00', category_id: 1, value: 150, comment: 'Обед' };

  beforeEach(() => {
    vi.clearAllMocks();
    CategoryAPI.list.mockResolvedValue(mockCategories);
  });

  it('открывается в режиме создания', () => {
    render(<EditExpenseModal isOpen={true} onClose={vi.fn()} item={null} onSuccess={vi.fn()} />);
    expect(screen.getByText('Добавить расход')).toBeInTheDocument();
    expect(screen.getByText('Готово')).toBeInTheDocument();
  });

  it('открывается в режиме редактирования', () => {
    render(<EditExpenseModal isOpen={true} onClose={vi.fn()} item={mockItem} onSuccess={vi.fn()} />);
    expect(screen.getByText('Редактировать расход')).toBeInTheDocument();
    expect(screen.getByDisplayValue('150')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Обед')).toBeInTheDocument();
  });

  it('сохраняет изменения', async () => {
    SpendingAPI.update.mockResolvedValue({});
    const onSuccess = vi.fn();
    const onClose = vi.fn();
    render(<EditExpenseModal isOpen={true} onClose={onClose} item={mockItem} onSuccess={onSuccess} />);
    const saveBtn = screen.getByText('Готово');
    fireEvent.click(saveBtn);
    await waitFor(() => {
      expect(SpendingAPI.update).toHaveBeenCalledWith(1, expect.objectContaining({ cost: 150 }));
      expect(onSuccess).toHaveBeenCalled();
      expect(onClose).toHaveBeenCalled();
    });
  });

  it('удаляет расход', async () => {
    SpendingAPI.delete.mockResolvedValue({});
    const onSuccess = vi.fn();
    const onClose = vi.fn();
    render(<EditExpenseModal isOpen={true} onClose={onClose} item={mockItem} onSuccess={onSuccess} />);
    const deleteBtn = screen.getByText('Удалить');
    window.confirm = vi.fn(() => true);
    fireEvent.click(deleteBtn);
    await waitFor(() => {
      expect(SpendingAPI.delete).toHaveBeenCalledWith(1);
      expect(onSuccess).toHaveBeenCalled();
      expect(onClose).toHaveBeenCalled();
    });
  });
});