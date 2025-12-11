import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const AdminLayout = ({ children }) => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <nav className="navbar" style={{ background: 'var(--danger)' }}>
        <div className="navbar-brand">
          <i className="fas fa-crown"></i> Admin Panel
        </div>
        <div className="navbar-menu">
          <NavLink to="/admin/dashboard" className="nav-link">
            <i className="fas fa-chart-bar"></i> Podsumowanie
          </NavLink>
          <NavLink to="/admin/houses" className="nav-link">
            <i className="fas fa-user-plus"></i> Przypisz Domy
          </NavLink>
          <NavLink to="/admin/sensors" className="nav-link">
            <i className="fas fa-plug"></i> Zarządzaj Czujnikami
          </NavLink>
          <NavLink to="/dashboard" className="nav-link" style={{ background: 'rgba(255,255,255,0.1)'}}>
            <i className="fas fa-arrow-left"></i> Wróć do widoku usera
          </NavLink>
          <button onClick={handleLogout} className="btn-logout" style={{ background: 'var(--bg-tertiary)'}}>
            <i className="fas fa-sign-out-alt"></i> Wyloguj
          </button>
        </div>
      </nav>
      <div className="container">
        {children}
      </div>
    </div>
  );
};

export default AdminLayout;
