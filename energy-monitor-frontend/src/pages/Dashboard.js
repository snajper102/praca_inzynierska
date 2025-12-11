import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../services/api';

const Dashboard = () => {
  const [houses, setHouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    apiClient.get('/user/houses/') // Ten endpoint zwraca teraz domy z czujnikami
      .then(res => {
        setHouses(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Błąd pobierania domów:", err);
        setError("Nie można załadować danych. Spróbuj odświeżyć stronę.");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="container">Ładowanie danych...</div>;
  }

  if (error) {
    return <div className="container error-message">{error}</div>;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header" style={{ marginBottom: '2rem' }}>
        <h1><i className="fas fa-chart-line"></i> Dashboard</h1>
        <p>Witaj! Zarządzaj swoimi urządzeniami.</p>
      </div>

      {/* Tu można dodać karty KPI (Statystyki globalne) */}

      <div className="houses-grid">
        {houses.length > 0 ? (
          houses.map(house => (
            <div key={house.id} className="house-card">
              <div className="house-header">
                <div className="house-title">
                  <i className="fas fa-home"></i>
                  <h2>{house.name}</h2>
                </div>
                {house.address && (
                  <div className="house-address">
                    <i className="fas fa-map-marker-alt"></i>
                    <span>{house.address}</span>
                  </div>
                )}
              </div>
              
              {/* TODO: Wstawić podsumowanie kosztów i mocy dla domu */}
              <div style={{ padding: '1rem 1.5rem', background: 'rgba(15, 23, 42, 0.4)', borderBottom: '1px solid var(--border)' }}>
                {/* Tu wstawisz dane z /statistics/ */}
                <p>Koszt w tym m-cu: -- PLN</p>
                <p>Moc teraz: -- W</p>
              </div>

              <div className="sensors-list" style={{ padding: '1.5rem' }}>
                {house.sensors && house.sensors.length > 0 ? (
                  house.sensors.map(sensor => (
                    <div key={sensor.id} className="sensor-item">
                      <div className="sensor-header">
                        <div className="sensor-name">
                          {/* POPRAWKA: Dynamiczna klasa ikony */}
                          <i className={`fas fa-${sensor.icon || 'microchip'}`} style={{ color: sensor.color }}></i>
                          <h3>{sensor.name}</h3>
                        </div>
                        {/* POPRAWKA: Dynamiczna klasa statusu */}
                        <div className={`sensor-status ${sensor.is_online ? 'online' : 'offline'}`}>
                          <span className="status-dot"></span>
                          {sensor.is_online ? 'Online' : 'Offline'}
                        </div>
                      </div>
                      <div className="sensor-actions">
                        <Link to={`/sensor/${sensor.id}`} className="btn-details">
                          <i className="fas fa-chart-area"></i>
                          Szczegóły
                        </Link>
                        <Link to={`/house/${house.id}`} className="btn-settings" style={{ padding: '0.75rem 1rem' }}>
                          <i className="fas fa-chart-bar"></i>
                        </Link>
                      </div>
                    </div>
                  ))
                ) : (
                  <p style={{ textAlign: 'center', color: '#94a3b8', padding: '2rem' }}>
                    Brak czujników w tym domu
                  </p>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <i className="fas fa-home"></i>
            <h3>Nie masz jeszcze dodanych domów</h3>
            <p>Skontaktuj się z administratorem, aby dodać pierwsze urządzenie.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
