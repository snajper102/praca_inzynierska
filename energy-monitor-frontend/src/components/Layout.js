import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Layout = ({ children }) => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="navbar-brand">
          <i className="fas fa-bolt"></i> Energy Monitor
        </div>
        <div className="navbar-menu">
          <NavLink to="/dashboard" className="nav-link">
            <i className="fas fa-chart-line"></i> Dashboard
          </NavLink>
          <NavLink to="/alerts" className="nav-link">
            <i className="fas fa-bell"></i> Alerty
          </NavLink>
          <NavLink to="/settings" className="nav-link">
            <i className="fas fa-user"></i> Ustawienia
          </NavLink>
          {/* Tu można dodać linki admina widoczne tylko dla 'user.is_staff' */}
          <button onClick={handleLogout} className="btn-logout">
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

export default Layout;
