import React, { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import Header from './components/Header';

// ── Lazy-загрузка страниц (performance + SEO: меньше initial bundle) ──────────
const Login           = lazy(() => import('./pages/Login'));
const Register        = lazy(() => import('./pages/Register'));
const Dashboard       = lazy(() => import('./pages/Dashboard'));
const Stats           = lazy(() => import('./pages/Stats'));
const AdminUsers      = lazy(() => import('./pages/AdminUsers'));
const TransactionList = lazy(() => import('./pages/TransactionList'));
const TransactionDetail = lazy(() => import('./pages/TransactionDetail'));
const Spending        = lazy(() => import('./pages/Spending'));
const Income          = lazy(() => import('./pages/Income'));

function PageLoader() {
  return (
    <div className="flex items-center justify-center py-24" aria-live="polite">
      <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* ── Публичные ── */}
            <Route path="/login"    element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* ── Защищённые ── */}
            <Route
              path="/dashboard"
              element={<ProtectedRoute><Dashboard /></ProtectedRoute>}
            />
            <Route
              path="/stats"
              element={<ProtectedRoute><Stats /></ProtectedRoute>}
            />
            <Route
              path="/admin/users"
              element={<ProtectedRoute requiredRole="admin"><AdminUsers /></ProtectedRoute>}
            />

            {/* ── Транзакции ── */}
            <Route
              path="/transactions"
              element={<ProtectedRoute><TransactionList /></ProtectedRoute>}
            />
            <Route
              path="/transactions/:id"
              element={<ProtectedRoute><TransactionDetail /></ProtectedRoute>}
            />
            <Route
              path="/spending"
              element={<ProtectedRoute><Spending /></ProtectedRoute>}
            />
            <Route
              path="/income"
              element={<ProtectedRoute><Income /></ProtectedRoute>}
            />

            {/* ── Fallback ── */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </div>
    </AuthProvider>
  );
}

export default App;
