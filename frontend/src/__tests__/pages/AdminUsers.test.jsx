import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AdminUsers from '../../pages/AdminUsers';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../api/api';

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}));
vi.mock('../../api/api', () => ({
  default: {
    getAllUsers: vi.fn(),
    updateUserRole: vi.fn(),
  },
}));

describe('AdminUsers', () => {
  const mockUsers = [
    { id: 1, username: 'user1', email: 'user1@ex.com', role: 'user' },
    { id: 2, username: 'admin1', email: 'admin@ex.com', role: 'admin' },
  ];
  const mockCurrentUser = { id: 1, role: 'admin' };

  beforeEach(() => {
    vi.clearAllMocks();
    useAuth.mockReturnValue({ user: mockCurrentUser });
    api.getAllUsers.mockResolvedValue(mockUsers);
    api.updateUserRole.mockResolvedValue({});
  });

  it('отображает список пользователей', async () => {
    render(<AdminUsers />);
    await waitFor(() => {
      expect(screen.getByText('user1')).toBeInTheDocument();
      expect(screen.getByText('admin1')).toBeInTheDocument();
    });
  });

  it('меняет роль пользователя', async () => {
    render(<AdminUsers />);
    await waitFor(() => {
      expect(screen.getByText('user1')).toBeInTheDocument();
    });
    const changeBtn = screen.getAllByText('Сменить')[0];
    fireEvent.click(changeBtn);
    await waitFor(() => {
      expect(api.updateUserRole).toHaveBeenCalledWith(1, 'admin');
    });
  });
});