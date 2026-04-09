import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import FileUpload from '../../components/FileUpload';
import { FileAPI } from '../../api/api';

vi.mock('../../api/api', () => ({
  FileAPI: {
    list: vi.fn(),
    upload: vi.fn(),
    delete: vi.fn(),
    downloadUrl: vi.fn(),
  },
}));

describe('FileUpload', () => {
  const mockFiles = [{ id: 1, original_name: 'file.pdf', size_bytes: 1024, content_type: 'application/pdf', uploaded_at: '2025-01-01T10:00:00' }];

  beforeEach(() => {
    vi.clearAllMocks();
    FileAPI.list.mockResolvedValue(mockFiles);
  });

  it('отображает загруженные файлы', async () => {
    render(<FileUpload transactionId={123} />);
    await waitFor(() => {
      expect(screen.getByText('file.pdf')).toBeInTheDocument();
    });
  });
});