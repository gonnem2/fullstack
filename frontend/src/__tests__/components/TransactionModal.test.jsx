import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TransactionModal from '../../components/TransactionModal';
import { TransactionAPI } from '../../api/api';

vi.mock('../../api/api', () => ({
  TransactionAPI: {
    create: vi.fn(),
    update: vi.fn(),
  },
}));

describe('TransactionModal', () => {
  const onClose = vi.fn();
  const onSaved = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('валидирует пустые поля и показывает ошибки', async () => {
    render(<TransactionModal initial={null} onClose={onClose} onSaved={onSaved} />);
    const submitBtn = screen.getByText('Создать');
    fireEvent.click(submitBtn);
    // Ошибка "Выберите тип" не появляется, потому что тип по умолчанию "расход"
    // Ожидаем только ошибки суммы и категории
    await waitFor(() => {
      expect(screen.getByText('Сумма должна быть больше нуля')).toBeInTheDocument();
      expect(screen.getByText('Выберите категорию')).toBeInTheDocument();
    });
  });

  it('создаёт транзакцию при корректных данных', async () => {
    TransactionAPI.create.mockResolvedValue({});
    render(<TransactionModal initial={null} onClose={onClose} onSaved={onSaved} />);
    // Выбираем тип "Доход"
    fireEvent.click(screen.getByText('↑ Доход'));
    // Вводим сумму
    fireEvent.change(screen.getByPlaceholderText('0.00'), { target: { value: '100' } });
    // Выбираем категорию
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'Зарплата' } });
    // Устанавливаем дату (поле date)
    const dateInput = screen.getByDisplayValue(new Date().toISOString().slice(0, 10));
    fireEvent.change(dateInput, { target: { value: '2025-01-01' } });
    // Нажимаем создать
    fireEvent.click(screen.getByText('Создать'));
    await waitFor(() => {
      expect(TransactionAPI.create).toHaveBeenCalled();
      expect(onSaved).toHaveBeenCalled();
    });
  });
});