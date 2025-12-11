import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../services/api';

const AlertCard = ({ alert, onUpdate }) => {
  const handleMarkRead = () => {
    apiClient.post(`/user/alerts/${alert.id}/mark_read/`)
      .then(res => onUpdate(alert.id, { is_read: true }));
  };
  
  const handleResolve = () => {
    apiClient.post(`/user/alerts/${alert.id}/mark_resolved/`)
      .then(res => onUpdate(alert.id, { is_resolved: true }));
  };

  // POPRAWKA: Zdefiniowanie zmiennej
  const alertClass = `alert-card ${!alert.is_read ? 'unread' : ''} ${alert.severity}`;

  return (
    <div className={alertClass}>
      <div className="alert-header">
        <div className="alert-title">
          <span className={`severity-badge ${alert.severity}`}>
            {alert.severity_display}
          </span>
          <span className="alert-type">{alert.alert_type_display}</span>
        </div>
        <div className="alert-badges">
          {!alert.is_read && <span className="badge unread">Nowy</span>}
          {alert.is_resolved && <span className="badge resolved">Rozwiązany</span>}
        </div>
      </div>
      <p className="alert-message">{alert.message}</p>
      {alert.value && (
        <div className="alert-value">
          <div className="value-box">
            <label>Wartość</label>
            <div className="value">{alert.value.toFixed(1)}</div>
          </div>
          <div className="value-box">
            <label>Próg</label>
            <div className="value">{alert.threshold.toFixed(1)}</div>
          </div>
        </div>
      )}
      <div className="alert-meta">
        <div className="alert-location">
          <i className="fas fa-home"></i> {alert.house_name}
          {alert.sensor_name && <span> → <i className="fas fa-microchip"></i> {alert.sensor_name}</span>}
        </div>
        <div className="alert-time">
          {new Date(alert.created_at).toLocaleString('pl-PL')}
        </div>
      </div>
      {!alert.is_read || !alert.is_resolved ? (
        <div className="alert-actions">
          {!alert.is_read && <button onClick={handleMarkRead}>Oznacz jako przeczytane</button>}
          {!alert.is_resolved && <button onClick={handleResolve} className="btn-resolve">Oznacz jako rozwiązane</button>}
        </div>
      ) : null}
    </div>
  );
};

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ type: '', severity: '', status: '' });

  useEffect(() => {
    setLoading(true);
    apiClient.get('/user/alerts/', { params: filters })
      .then(res => {
        setAlerts(res.data);
        setLoading(false);
      })
      .catch(err => setLoading(false));
  }, [filters]);

  const handleFilterChange = (e) => {
    setFilters(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleAlertUpdate = (alertId, updates) => {
    setAlerts(prevAlerts => 
      prevAlerts.map(a => a.id === alertId ? { ...a, ...updates } : a)
    );
  };

  return (
    <div className="alerts-container">
      <div className="alerts-header">
        <h1><i className="fas fa-bell"></i> Alerty i powiadomienia</h1>
        <Link to="/alerts/create" className="btn-create">
          <i className="fas fa-plus-circle"></i> Dodaj alert
        </Link>
      </div>

      <div className="filters">
        <div className="filter-group">
          <label>Typ</label>
          <select name="type" value={filters.type} onChange={handleFilterChange} className="filter-select">
            <option value="">Wszystkie</option>
            <option value="power_high">Przekroczenie mocy</option>
            <option value="current_high">Przekroczenie prądu</option>
            <option value="sensor_offline">Czujnik offline</option>
            {/* Dodaj resztę typów */}
          </select>
        </div>
        <div className="filter-group">
          <label>Ważność</label>
          <select name="severity" value={filters.severity} onChange={handleFilterChange} className="filter-select">
            <option value="">Wszystkie</option>
            <option value="info">Informacja</option>
            <option value="warning">Ostrzeżenie</option>
            <option value="critical">Krytyczny</option>
          </select>
        </div>
        <div className="filter-group">
          <label>Status</label>
          <select name="status" value={filters.status} onChange={handleFilterChange} className="filter-select">
            <option value="">Wszystkie</option>
            <option value="unread">Nieprzeczytane</option>
            <option value="active">Aktywne (nierozwiązane)</option>
            <option value="resolved">Rozwiązane</option>
          </select>
        </div>
      </div>

      {loading ? (
        <p>Ładowanie alertów...</p>
      ) : (
        <div className="alerts-list">
          {alerts.length > 0 ? (
            alerts.map(alert => (
              <AlertCard key={alert.id} alert={alert} onUpdate={handleAlertUpdate} />
            ))
          ) : (
            <div className="empty-state">
              <i className="fas fa-bell-slash"></i>
              <h3>Brak alertów</h3>
              <p>Nie masz żadnych alertów spełniających wybrane kryteria.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Alerts;
