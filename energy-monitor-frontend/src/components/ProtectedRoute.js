import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Layout from './Layout'; // Importujemy główny layout

const ProtectedRoute = () => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    // Użytkownik nie jest zalogowany, przekieruj do /login
    return <Navigate to="/login" replace />;
  }

  // Użytkownik jest zalogowany, wyświetl stronę wewnątrz głównego Layoutu
  return (
    <Layout>
      <Outlet />
    </Layout>
  );
};

export default ProtectedRoute;
