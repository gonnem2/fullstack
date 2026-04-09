import React, { useEffect, useState } from 'react';
import Card from '../components/Card';
import EditIncomeModal from '../components/EditIncomeModal';
import { IncomeAPI, CategoryAPI } from '../api/api';

export default function Income() {
  const [rows, setRows] = useState([]);
  const [categories, setCategories] = useState({});
  const [loading, setLoading] = useState(true);

  const [selectedItem, setSelectedItem] = useState(null);
  const [isModalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    try {
      const catRes = await CategoryAPI.list();

      const catMap = {};
      catRes.categories.forEach(c => {
        catMap[c.id] = c.title;
      });
      setCategories(catMap);

      const res = await IncomeAPI.list("limit=50");

      const mapped = res.data.incomes.map(i => ({
        id: i.id,
        date: i.income_date,
        time: new Date(i.income_date).toLocaleTimeString(),
        type: catMap[i.category_id] || '—',
        amount: i.value,
        comment: i.comment,
      }));

      setRows(mapped);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (item) => {
    setSelectedItem(item);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    await IncomeAPI.delete(id);
    setRows(prev => prev.filter(r => r.id !== id));
  };

  if (loading) return <div className="p-6 text-center">Загрузка...</div>;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-semibold mb-6 text-center">Доходы</h2>

      <Card>
        <div className="space-y-3">
          {rows.map((r) => (
            <div
              key={r.id}
              onClick={() => handleOpenModal(r)}
              className="flex justify-between p-3 bg-green-50 rounded-xl cursor-pointer"
            >
              <div>{r.time}</div>
              <div className="flex-1 px-4">
                <div>{r.type}</div>
                <div className="text-sm text-gray-500">{r.comment}</div>
              </div>
              <div>{r.amount} ₽</div>
            </div>
          ))}
        </div>
      </Card>

      {isModalOpen && (
        <EditIncomeModal
          isOpen={isModalOpen}
          onClose={() => setModalOpen(false)}
          item={selectedItem}
          onDelete={handleDelete}
        />
      )}
    </div>
  );
}