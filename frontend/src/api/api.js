const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1';

// ─── HELPERS ───────────────────────────────────────────

function getToken() {
  return localStorage.getItem('access_token');
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handleResponse(res) {
  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) message = JSON.stringify(body.detail);
    } catch {}
    throw new Error(message);
  }
  if (res.status === 204) return null;
  return res.json();
}

// ─── AUTH ──────────────────────────────────────────────

export const auth = {
  login: async ({ username, password }) => {
    const form = new URLSearchParams();
    form.append('username', username);
    form.append('password', password);
    const res = await fetch(`${BASE}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form,
    });
    const data = await handleResponse(res);
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return data;
  },

  register: (payload) =>
    fetch(`${BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(handleResponse),

  logout: async () => {
    const refresh = localStorage.getItem('refresh_token');
    if (refresh) {
      await fetch(`${BASE}/auth/logout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify({ refresh_token: refresh }),
      }).catch(() => {});
    }
    localStorage.clear();
  },

  isAuthenticated: () => !!getToken(),
};

// ─── BASE HTTP ─────────────────────────────────────────

const api = {
  get: (url) =>
    fetch(`${BASE}${url}`, { headers: authHeaders() }).then(handleResponse),

  post: (url, body) =>
    fetch(`${BASE}${url}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(body),
    }).then(handleResponse),

  put: (url, body) =>
    fetch(`${BASE}${url}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(body),
    }).then(handleResponse),

  patch: (url, body) =>
    fetch(`${BASE}${url}`, {
      method: 'PATCH',
      headers: body
        ? { 'Content-Type': 'application/json', ...authHeaders() }
        : authHeaders(),
      body: body ? JSON.stringify(body) : undefined,
    }).then(handleResponse),

  delete: (url) =>
    fetch(`${BASE}${url}`, { method: 'DELETE', headers: authHeaders() }).then(handleResponse),

  upload: (url, formData) =>
    fetch(`${BASE}${url}`, {
      method: 'POST',
      headers: authHeaders(),
      body: formData,
    }).then(handleResponse),

  auth,

  // ── Profile ──────────────────────────────────────────
  getProfile: () =>
    fetch(`${BASE}/users/me`, { headers: authHeaders() }).then(handleResponse),

  // ── Spendings ─────────────────────────────────────────
  getSpendings: (params = {}) => {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '')
    );
    return api.get(`/spending?${qs}`);
  },

  // POST /spending принимает multipart/form-data
  addSpending: (data) => {
    const fd = new FormData();
    fd.append('expense_date', data.expense_date);
    fd.append('category_id', String(data.category_id));
    fd.append('cost', String(data.cost));
    if (data.comment) fd.append('comment', data.comment);
    if (data.image) fd.append('image', data.image);
    return api.upload('/spending', fd);
  },

  updateSpending: (id, data) => api.put(`/spending/${id}`, data),
  deleteSpending: (id) => api.delete(`/spending/${id}`),

  // ── Incomes ───────────────────────────────────────────
  getIncomes: (params = {}) => {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '')
    );
    return api.get(`/income?${qs}`);
  },

  // POST /income принимает multipart/form-data
  addIncome: (data) => {
    const fd = new FormData();
    fd.append('income_date', data.income_date);
    fd.append('category_id', String(data.category_id));
    fd.append('value', String(data.value));
    if (data.comment) fd.append('comment', data.comment);
    if (data.image) fd.append('image', data.image);
    return api.upload('/income', fd);
  },

  updateIncome: (id, data) => api.put(`/income/${id}`, data),
  deleteIncome: (id) => api.delete(`/income/${id}`),

  // ── Categories ────────────────────────────────────────
  getCategories: (limit = 100) => api.get(`/categories/?limit=${limit}`),
  createCategory: (data) => api.post('/categories/', data),
  updateCategory: (id, data) => api.put(`/categories/${id}`, data),
  deleteCategory: (id) => api.delete(`/categories/${id}`),

  // ── Users ─────────────────────────────────────────────
  updateUserLimit: (newLimit) =>
    api.patch(`/users/change_limit?new_limit=${newLimit}`),

  getAllUsers: (skip = 0, limit = 100) =>
    api.get(`/users/admin/all?skip=${skip}&limit=${limit}`),

  updateUserRole: (userId, role) =>
    api.patch(`/users/admin/${userId}`, { user_role: role }),

  // ── Stats ─────────────────────────────────────────────
  getExpenseStats: (period) => api.get(`/stats/expenses?period=${period}`),
  getDynamicStats: (period) => api.get(`/stats/dynamic?period=${period}`),
};

export default api;

// ─── INCOME API ────────────────────────────────────────

export const IncomeAPI = {
  list: (params = '') => api.get(`/income?${params}`),
  create: (formData) => api.upload('/income', formData),
  update: (id, data) => api.put(`/income/${id}`, data),
  delete: (id) => api.delete(`/income/${id}`),
};

// ─── SPENDING API ──────────────────────────────────────

export const SpendingAPI = {
  list: (params = '') => api.get(`/spending?${params}`),
  create: (formData) => api.upload('/spending', formData),
  update: (id, data) => api.put(`/spending/${id}`, data),
  delete: (id) => api.delete(`/spending/${id}`),
};

// ─── CATEGORIES ────────────────────────────────────────

export const CategoryAPI = {
  list: (limit = 100) => api.get(`/categories/?limit=${limit}`),
};

// ─── FILE API ──────────────────────────────────────────
// transactionId может быть составным ("income_5") или числом

function extractRealId(transactionId) {
  const s = String(transactionId);
  if (s.includes('_')) return parseInt(s.split('_')[1]);
  return parseInt(s);
}

export const FileAPI = {
  list: (transactionId) =>
    api.get(`/files/transaction/${extractRealId(transactionId)}`),

  upload: (transactionId, file) => {
    const fd = new FormData();
    fd.append('transaction_id', extractRealId(transactionId));
    fd.append('file', file);
    return api.upload('/files/upload', fd);
  },

  downloadUrl: (fileId) => api.get(`/files/${fileId}/download-url`),

  delete: (fileId) => api.delete(`/files/${fileId}`),
};

// ─── TRANSACTION API ───────────────────────────────────
// Адаптер, объединяющий income + spending в единый «транзакционный» интерфейс.
// Составной ID формат: "income_{id}" или "expense_{id}"

function parseCompositeId(compositeId) {
  const parts = String(compositeId).split('_');
  return { type: parts[0], id: parseInt(parts[1]) };
}

async function buildCategoryMap() {
  try {
    const res = await api.getCategories(100);
    const map = {};
    (res.categories || []).forEach((c) => { map[c.id] = c.title; });
    return map;
  } catch {
    return {};
  }
}

function incomeToTx(income, catMap) {
  return {
    id: `income_${income.id}`,
    _realId: income.id,
    type: 'income',
    amount: income.value,
    category: catMap[income.category_id] || `Категория ${income.category_id}`,
    category_id: income.category_id,
    description: income.comment || '',
    date: income.income_date,
    created_at: income.income_date,
  };
}

function expenseToTx(expense, catMap) {
  return {
    id: `expense_${expense.id}`,
    _realId: expense.id,
    type: 'expense',
    amount: expense.value,
    category: catMap[expense.category_id] || `Категория ${expense.category_id}`,
    category_id: expense.category_id,
    description: expense.comment || '',
    date: expense.expense_date,
    created_at: expense.expense_date,
  };
}

export const TransactionAPI = {
  // Возвращает { items, total, pages } — объединённый список
  list: async (queryString = '') => {
    const params = new URLSearchParams(queryString);
    const page = parseInt(params.get('page') || '1');
    const pageSize = parseInt(params.get('page_size') || '20');
    const skip = (page - 1) * pageSize;
    const typeFilter = params.get('type') || '';
    const categoryFilter = params.get('category') || '';
    const sortBy = params.get('sort_by') || 'date';
    const sortOrder = params.get('sort_order') || 'desc';

    const catMap = await buildCategoryMap();

    // Общие параметры запроса
    const baseParams = { skip: 0, limit: 100 };
    if (params.get('search')) baseParams.search = params.get('search');
    if (params.get('date_from')) {
      baseParams.from_date = new Date(params.get('date_from')).toISOString();
    }
    if (params.get('date_to')) {
      const d = new Date(params.get('date_to'));
      d.setHours(23, 59, 59, 999);
      baseParams.to_date = d.toISOString();
    }
    if (params.get('amount_min')) baseParams.min_value = params.get('amount_min');
    if (params.get('amount_max')) baseParams.max_value = params.get('amount_max');

    let items = [];

    if (!typeFilter || typeFilter === 'income') {
      const qs = new URLSearchParams({
        ...baseParams,
        sort_by: sortBy === 'amount' ? 'value' : 'income_date',
        sort_order: sortOrder,
      });
      try {
        const res = await api.get(`/income?${qs}`);
        items.push(...(res.data?.incomes || []).map((i) => incomeToTx(i, catMap)));
      } catch {}
    }

    if (!typeFilter || typeFilter === 'expense') {
      const qs = new URLSearchParams({
        ...baseParams,
        sort_by: sortBy === 'amount' ? 'value' : 'expense_date',
        sort_order: sortOrder,
      });
      try {
        const res = await api.get(`/spending?${qs}`);
        items.push(...(res.data?.expenses || []).map((e) => expenseToTx(e, catMap)));
      } catch {}
    }

    // При смешанном режиме — сортируем по дате
    if (!typeFilter) {
      items.sort((a, b) =>
        sortOrder === 'desc'
          ? new Date(b.date) - new Date(a.date)
          : new Date(a.date) - new Date(b.date)
      );
    }

    // Фильтр по категории (клиентский, т.к. категория — строка)
    if (categoryFilter) {
      items = items.filter((tx) => tx.category === categoryFilter);
    }

    const total = items.length;
    const pages = Math.max(1, Math.ceil(total / pageSize));

    // Пагинация на клиенте
    const paged = items.slice((page - 1) * pageSize, page * pageSize);

    return { items: paged, total, pages };
  },

  // Возвращает массив названий категорий для FilterPanel
  categories: async () => {
    try {
      const res = await api.getCategories(100);
      return (res.categories || []).map((c) => c.title);
    } catch {
      return [];
    }
  },

  // Получить одну транзакцию по составному ID
  get: async (compositeId) => {
    const { type, id } = parseCompositeId(compositeId);
    const catMap = await buildCategoryMap();
    if (type === 'income') {
      const income = await api.get(`/income/${id}`);
      return incomeToTx(income, catMap);
    } else {
      const expense = await api.get(`/spending/${id}`);
      return expenseToTx(expense, catMap);
    }
  },

  // Создать транзакцию
  // payload: { type, amount, category, description, date }
  create: async (payload) => {
    const catRes = await api.getCategories(100);
    const cat = (catRes.categories || []).find((c) => c.title === payload.category);
    const categoryId = cat?.id;

    if (payload.type === 'income') {
      const fd = new FormData();
      fd.append('income_date', new Date(payload.date).toISOString());
      if (categoryId) fd.append('category_id', categoryId);
      fd.append('value', payload.amount);
      if (payload.description) fd.append('comment', payload.description);
      return api.upload('/income', fd);
    } else {
      const fd = new FormData();
      fd.append('expense_date', new Date(payload.date).toISOString());
      if (categoryId) fd.append('category_id', categoryId);
      fd.append('cost', payload.amount);
      if (payload.description) fd.append('comment', payload.description);
      return api.upload('/spending', fd);
    }
  },

  // Обновить транзакцию
  update: async (compositeId, payload) => {
    const { type, id } = parseCompositeId(compositeId);
    const catRes = await api.getCategories(100);
    const cat = (catRes.categories || []).find((c) => c.title === payload.category);
    const categoryId = cat?.id || payload.category_id;

    if (type === 'income') {
      return api.put(`/income/${id}`, {
        income_date: new Date(payload.date).toISOString(),
        category_id: categoryId,
        value: Number(payload.amount),
        comment: payload.description || '',
      });
    } else {
      return api.put(`/spending/${id}`, {
        expense_date: new Date(payload.date).toISOString(),
        category_id: categoryId,
        cost: Number(payload.amount),
        comment: payload.description || '',
      });
    }
  },




  // Удалить транзакцию
  delete: async (compositeId) => {
    const { type, id } = parseCompositeId(compositeId);
    if (type === 'income') return api.delete(`/income/${id}`);
    return api.delete(`/spending/${id}`);
  },
};
