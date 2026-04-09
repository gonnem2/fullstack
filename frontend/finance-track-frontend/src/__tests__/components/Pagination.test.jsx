// src/__tests__/components/Pagination.test.jsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Pagination from '../../components/Pagination';

describe('Pagination', () => {

  it('не рендерится при pages <= 1', () => {
    const { container } = render(
      <Pagination page={1} pages={1} onPageChange={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('рендерит кнопки при pages > 1', () => {
    render(<Pagination page={2} pages={5} onPageChange={vi.fn()} />);
    expect(screen.getByText('← Назад')).toBeInTheDocument();
    expect(screen.getByText('Вперёд →')).toBeInTheDocument();
  });

  it('кнопка "Назад" задизейблена на первой странице', () => {
    render(<Pagination page={1} pages={5} onPageChange={vi.fn()} />);
    expect(screen.getByText('← Назад')).toBeDisabled();
  });

  it('кнопка "Вперёд" задизейблена на последней странице', () => {
    render(<Pagination page={5} pages={5} onPageChange={vi.fn()} />);
    expect(screen.getByText('Вперёд →')).toBeDisabled();
  });

  it('клик по кнопке страницы вызывает onPageChange', () => {
    const onPageChange = vi.fn();
    render(<Pagination page={1} pages={5} onPageChange={onPageChange} />);
    fireEvent.click(screen.getByText('2'));
    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  it('клик "Вперёд" вызывает onPageChange(page + 1)', () => {
    const onPageChange = vi.fn();
    render(<Pagination page={2} pages={5} onPageChange={onPageChange} />);
    fireEvent.click(screen.getByText('Вперёд →'));
    expect(onPageChange).toHaveBeenCalledWith(3);
  });

  it('клик "Назад" вызывает onPageChange(page - 1)', () => {
    const onPageChange = vi.fn();
    render(<Pagination page={3} pages={5} onPageChange={onPageChange} />);
    fireEvent.click(screen.getByText('← Назад'));
    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  it('текущая страница выделена визуально', () => {
    render(<Pagination page={3} pages={5} onPageChange={vi.fn()} />);
    const current = screen.getByText('3');
    expect(current).toHaveAttribute('aria-current', 'page');
  });
});