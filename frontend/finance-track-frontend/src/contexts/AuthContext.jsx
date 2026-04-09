import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../api/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (api.auth.isAuthenticated()) {
      api.getProfile()
        .then((data) => {
          setUser(data);
          setLoading(false);
        })
        .catch(() => {
          api.auth.logout();
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (credentials) => {
    await api.auth.login(credentials);
    const profile = await api.getProfile();
    setUser(profile);
    return profile;
  };

  const logout = () => {
    api.auth.logout();
    setUser(null);
  };

  // Обновить данные пользователя в контексте (например, после смены лимита)
  const updateUser = (updatedUser) => {
    setUser(updatedUser);
  };

  const value = {
    user,
    loading,
    login,
    logout,
    updateUser,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
