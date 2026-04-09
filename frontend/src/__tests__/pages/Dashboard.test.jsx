import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Dashboard from '../../pages/Dashboard';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../api/api';

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}));
vi.mock('../../api/api', () => ({
  default: {
    getCategories: vi.fn(),
    getSpendings: vi.fn(),
    getIncomes: vi.fn(),
    getExpenseStats: vi.fn(),
    deleteSpending: vi.fn(),
    deleteIncome: vi.fn(),
    updateUserLimit: vi.fn(),
    createCategory: vi.fn(),
    updateCategory: vi.fn(),
    deleteCategory: vi.fn(),
  },
}));
vi.mock('../../components/CurrencyWidget', () => ({
  default: () => <div data-testid="currency-widget">CurrencyWidget Mock</div>,
}));
vi.mock('../../components/EditExpenseModal', () => ({
  default: ({ isOpen }) => (isOpen ? <div data-testid="edit-expense-modal">Edit Expense Modal</div> : null),
}));
vi.mock('../../components/EditIncomeModal', () => ({
  default: ({ isOpen }) => (isOpen ? <div data-testid="edit-income-modal">Edit Income Modal</div> : null),
}));
vi.mock('../../components/ImageViewerModal', () => ({
  default: ({ isOpen }) => (isOpen ? <div data-testid="image-viewer">Image Viewer</div> : null),
}));

describe('Dashboard', () => {
  const mockUser = { id: 1, username: 'testuser', day_expense_limit: 1000, role: 'user' };
  const mockCategories = [{ id: 1, title: 'Еда', type_of_category: 'expense' }];
  const mockSpendings = [{ id: 1, expense_date: '2025-01-01T12:00:00', category_id: 1, value: 150, comment: 'Обед' }];
  const mockIncomes = [{ id: 1, income_date: '2025-01-01T10:00:00', category_id: 1, value: 500, comment: 'Зарплата' }];
  const mockStats = { total: 150, categories: [{ title: 'Еда', amount: 150 }] };

  beforeEach(() => {
    vi.clearAllMocks();
    useAuth.mockReturnValue({ user: mockUser, isAdmin: false, logout: vi.fn(), updateUser: vi.fn() });
    api.getCategories.mockResolvedValue({ categories: mockCategories });
    api.getSpendings.mockResolvedValue({ data: { expenses: mockSpendings } });
    api.getIncomes.mockResolvedValue({ data: { incomes: mockIncomes } });
    api.getExpenseStats.mockResolvedValue(mockStats);
  });

  it('отображает заголовок и кнопки навигации после загрузки', async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText('FinanceTrack')).toBeInTheDocument();
      expect(screen.getByText('Все траты')).toBeInTheDocument();
      expect(screen.getByText('Все доходы')).toBeInTheDocument();
      expect(screen.getByText(/Привет, testuser/)).toBeInTheDocument();
    });
  });

  it('загружает и отображает расходы и доходы', async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText('Обед')).toBeInTheDocument();
      // "Зарплата" встречается дважды, используем getAllByText
      expect(screen.getAllByText('Зарплата').length).toBeGreaterThan(0);
    });
  });

  it('открывает модалку добавления расхода', async () => {
    render(<Dashboard />);
    // Находим первую кнопку "+ Добавить" (она в блоке расходов)
    const addButtons = await screen.findAllByText('+ Добавить');
    fireEvent.click(addButtons[0]);
    expect(screen.getByTestId('edit-expense-modal')).toBeInTheDocument();
  });

  it('открывает модалку изменения лимита', async () => {
    render(<Dashboard />);
    const changeLimitBtn = await screen.findByText('Изменить лимит');
    fireEvent.click(changeLimitBtn);
    expect(screen.getByText('Изменить дневной лимит')).toBeInTheDocument();
  });

  it('удаляет расход при подтверждении', async () => {
    window.confirm = vi.fn(() => true);
    api.deleteSpending.mockResolvedValue({});
    render(<Dashboard />);
    const deleteBtns = await screen.findAllByText('Удалить');
    fireEvent.click(deleteBtns[0]);
    await waitFor(() => {
      expect(api.deleteSpending).toHaveBeenCalledWith(1);
    });
  });
  // Добавьте в описание Dashboard
// Добавьте после существующих тестов (например, после "удаляет расход при подтверждении")

it('создаёт новую категорию', async () => {
  api.createCategory.mockResolvedValue({ id: 2, title: 'Новая', type_of_category: 'expense' });
  render(<Dashboard />);
  await waitFor(() => expect(screen.queryByText('Загрузка...')).not.toBeInTheDocument());
  // Находим все кнопки "+ Добавить", последняя относится к категориям
  const addButtons = screen.getAllByText('+ Добавить');
  const addCategoryBtn = addButtons[addButtons.length - 1];
  fireEvent.click(addCategoryBtn);
  // Ждём появления поля ввода названия категории
  const titleInput = await screen.findByPlaceholderText('Название');
  fireEvent.change(titleInput, { target: { value: 'Новая' } });
  const createBtn = screen.getByText('Создать');
  fireEvent.click(createBtn);
  await waitFor(() => {
    expect(api.createCategory).toHaveBeenCalledWith({ title: 'Новая', type_of_category: 'expense' });
  });
});

it('удаляет категорию', async () => {
  api.deleteCategory.mockResolvedValue({});
  window.confirm = vi.fn(() => true);
  render(<Dashboard />);
  await waitFor(() => expect(screen.queryByText('Загрузка...')).not.toBeInTheDocument());
  // Находим все кнопки "Удал." (удаление категорий)
  const deleteCatBtns = screen.getAllByText('Удал.');
  fireEvent.click(deleteCatBtns[0]);
  await waitFor(() => {
    expect(api.deleteCategory).toHaveBeenCalledWith(1);
  });
});

it('открывает модалку добавления дохода', async () => {
  render(<Dashboard />);
  await waitFor(() => expect(screen.queryByText('Загрузка...')).not.toBeInTheDocument());
  // Вторая кнопка "+ Добавить" относится к доходам (индекс 1)
  const addButtons = screen.getAllByText('+ Добавить');
  const addIncomeBtn = addButtons[1];
  fireEvent.click(addIncomeBtn);
  expect(screen.getByTestId('edit-income-modal')).toBeInTheDocument();
});
});