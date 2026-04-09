import React, { useState } from 'react';
import Modal from './Modal';
import api from '../api/api';

export default function EditLimitModal({ isOpen, onClose, onSave, currentLimit }) {
  const [newLimit, setNewLimit] = useState(currentLimit ?? 0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSave = async () => {
    const value = Number(newLimit);
    if (isNaN(value) || value < 0) {
      setError('Введите корректное значение');
      return;
    }
    try {
      setLoading(true);
      setError('');
      const updated = await api.updateUserLimit(value);
      onSave(updated);
      onClose();
    } catch (err) {
      console.error('Ошибка при изменении лимита:', err);
      setError('Не удалось сохранить лимит');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <h2 className="text-lg font-semibold mb-4 text-gray-800">Изменить дневной лимит</h2>

      {error && (
        <div className="mb-3 p-2 bg-red-50 text-red-600 rounded text-sm">{error}</div>
      )}

      <input
        type="number"
        min="0"
        className="w-full border rounded-lg px-3 py-2 mb-4 focus:ring focus:ring-purple-200"
        value={newLimit}
        onChange={(e) => setNewLimit(e.target.value)}
        disabled={loading}
      />
      <button
        onClick={handleSave}
        disabled={loading}
        className="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white font-medium py-2 rounded-lg"
      >
        {loading ? 'Сохранение...' : 'Сохранить'}
      </button>
    </Modal>
  );
}
