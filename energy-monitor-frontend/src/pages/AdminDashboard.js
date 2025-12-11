import React from 'react';
import { Link } from 'react-router-dom';

// TODO: W przyszłości te dane powinny być pobierane z API
// np. z /api/admin/statistics/ oraz /api/admin/activity-log/
const stats = {
  total_users: 12,
  total_houses: 8,
  online_sensors: 20,
  offline_sensors: 3,
  unread_alerts: 5,
  critical_alerts: 2,
};

const recent_activity = [
  { id: 1, action: 'create', description: 'Utworzono dom: Dom Testowy', user: 'admin', ip: '127.0.0.1', created_at: new Date().toISOString() },
  { id: 2, action: 'assign', description: 'Przypisano czujnik "Garaż" do Dom Testowy', user: 'admin', ip: '127.0.0.1', created_at: new Date().toISOString() },
  { id: 3, action: 'alert', description: 'Alert: Przekroczono próg mocy', user: 'system', ip: '', created_at: new Date().toISOString() },
];

const top_users = [
  { user: { username: 'jkowalski' }, houses: 2, kwh: 340.5 },
  { user: { username: 'anowak' }, houses: 1, kwh: 210.1 },
];

const AdminDashboard = () => {
  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1><i className="fas fa-crown"></i> Panel Administracyjny</h1>
        <p>Zarządzaj systemem, użytkownikami i monitoruj aktywność</p>
        <div className="quick-actions">
          <Link to="/admin/sensors" className="btn-action">
            <i className="fas fa-plug"></i> Zarządzaj Czujnikami
          </Link>
          <Link to="/admin/houses" className="btn-action">
            <i className="fas fa-plus-circle"></i> Przypisz dom
          </Link>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card"><div className="stat-label">Użytkownicy</div><div className="stat-value">{stats.total_users}</div></div>
        <div className="stat-card"><div className="stat-label">Domy</div><div className="stat-value">{stats.total_houses}</div></div>
        <div className="stat-card"><div className="stat-label">Czujniki online</div><div className="stat-value" style={{color: 'var(--success)'}}>{stats.online_sensors}</div></div>
        <div className="stat-card"><div className="stat-label">Czujniki offline</div><div className="stat-value" style={{color: 'var(--danger)'}}>{stats.offline_sensors}</div></div>
        <div className="stat-card"><div className="stat-label">Alerty krytyczne</div><div className="stat-value">{stats.critical_alerts}</div></div>
      </div>
      
      <div className="content-grid">
        <div className="panel">
          <div className="panel-header"><h2><i className="fas fa-history"></i> Ostatnia aktywność</h2></div>
          <div className="activity-list">
            {recent_activity.map(log => (
              <div className="activity-item" key={log.id}>
                {/* POPRAWKA: Dynamiczna klasa */}
                <div className={`activity-icon ${log.action}`}><i className="fas fa-plus"></i></div>
                <div className="activity-content">
                  <div className="activity-description">{log.description}</div>
                  <div className="activity-meta">{log.user} • {new Date(log.created_at).toLocaleString('pl-PL')}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="panel">
          <div className="panel-header"><h2><i className="fas fa-chart-bar"></i> Top użytkownicy</h2></div>
          <div className="top-users-list">
            {top_users.map((item, index) => (
              <div className="user-item" key={item.user.username}>
                <div className={`user-rank top${index + 1}`}>{index + 1}</div>
                <div className="user-info">
                  <div className="user-name">{item.user.username}</div>
                  <div className="user-houses">{item.houses} dom(y)</div>
                </div>
                <div className="user-consumption">
                  <div className="user-kwh">{item.kwh} kWh</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
