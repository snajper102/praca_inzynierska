import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../services/api';

const AdminSensors = () => {
  const [sensors, setSensors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    // Pobieramy wszystkie czujniki z endpointu admina
    apiClient.get('/admin/sensors/')
      .then(res => {
        setSensors(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError("Błąd ładowania czujników.");
        setLoading(false);
      });
  }, []);

  return (
    <div className="sensor-list-container">
      <div className="sensor-list-header">
        <h1><i className="fas fa-plug"></i> Zarządzanie Czujnikami</h1>
        {/* TODO: Przycisk dodawania nowego czujnika */}
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Aktywne Czujniki w Systemie</h2>
        </div>
        
        <table className="sensor-table">
          <thead>
            <tr>
              <th>Nazwa</th>
              <th>Lokalizacja</th>
              <th>Dom</th>
              <th>Status</th>
              <th>ID Czujnika</th>
              <th>Ostatni pomiar</th>
              <th>Akcja</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="7">Ładowanie...</td></tr>
            ) : error ? (
              <tr><td colSpan="7" style={{ color: 'var(--danger)'}}>{error}</td></tr>
            ) : (
              sensors.map(sensor => (
                <tr key={sensor.id}>
                  <td><strong>{sensor.name}</strong></td>
                  <td>{sensor.location || "-"}</td>
                  <td>{sensor.house?.name || sensor.house}</td>
                  <td>
                    {sensor.is_online ? (
                      <span className="status-online">● Online</span>
                    ) : (
                      <span className="status-offline">● Offline</span>
                    )}
                  </td>
                  <td>{sensor.sensor_id}</td>
                  <td>
                    {sensor.last_reading ? 
                      new Date(sensor.last_reading.timestamp).toLocaleString('pl-PL') : 
                      'Brak danych'}
                  </td>
                  <td>
                    {/* POPRAWKA: Dynamiczny link */}
                    <Link to={`/sensor/${sensor.id}`} className="btn-edit" style={{ fontSize: '0.9rem' }}>
                      Szczegóły
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminSensors;
