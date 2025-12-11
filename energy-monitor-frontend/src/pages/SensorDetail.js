import React, { useState, useEffect, useRef, useCallback } from 'react'; // Import useCallback
import { useParams, Link } from 'react-router-dom';
import apiClient from '../services/api';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js';
import { useAuth } from '../context/AuthContext'; // Import useAuth

// Rejestracja komponentów Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

// Hook do auto-odświeżania (interwału)
const useInterval = (callback, delay) => {
  const savedCallback = useRef();

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    function tick() {
      savedCallback.current();
    }
    if (delay !== null) {
      let id = setInterval(tick, delay);
      return () => clearInterval(id);
    }
  }, [delay]);
};

// NOWY KOMPONENT: Zakładka ustawień czujnika
const SensorSettingsTab = ({ sensor, onSensorUpdate }) => {
  const [formData, setFormData] = useState({
    power_threshold: sensor.power_threshold || '',
    current_max_threshold: sensor.current_max_threshold || '',
    voltage_min_threshold: sensor.voltage_min_threshold || '',
    voltage_max_threshold: sensor.voltage_max_threshold || '',
    offline_threshold_seconds: sensor.offline_threshold_seconds || 30,
  });
  const [message, setMessage] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setMessage(null);

    // Przygotuj dane (zamień puste stringi na null)
    const payload = {};
    for (const key in formData) {
      payload[key] = formData[key] === '' ? null : formData[key];
    }
    
    // POPRAWKA: Używamy apiClient.patch z poprawnym URL
    apiClient.patch(`/user/sensors/${sensor.id}/`, payload)
      .then(res => {
        onSensorUpdate(res.data); // Zaktualizuj stan nadrzędny
        setMessage({ type: 'success', text: 'Zapisano ustawienia czujnika!' });
      })
      .catch(err => {
        setMessage({ type: 'error', text: 'Błąd zapisu.' });
      });
  };

  return (
    <div className="settings-section" style={{ marginTop: '2rem' }}>
      <h2 className="section-title"><i className="fas fa-cogs"></i> Ustawienia Alertów dla Czujnika</h2>
      {message && (
        <div className={message.type === 'success' ? 'success-message' : 'error-message'} 
             style={{ padding: '1rem', borderRadius: '0.5rem', margin: '1rem 0' }}>
          {message.text}
        </div>
      )}
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label>Próg Mocy (W)</label>
            <input type="number" name="power_threshold" value={formData.power_threshold} onChange={handleChange} className="form-control" />
          </div>
          <div className="form-group">
            <label>Próg Prądu (A)</label>
            <input type="number" name="current_max_threshold" value={formData.current_max_threshold} onChange={handleChange} className="form-control" />
          </div>
          <div className="form-group">
            <label>Min. Napięcie (V)</label>
            <input type="number" name="voltage_min_threshold" value={formData.voltage_min_threshold} onChange={handleChange} className="form-control" />
          </div>
          <div className="form-group">
            <label>Max. Napięcie (V)</label>
            <input type="number" name="voltage_max_threshold" value={formData.voltage_max_threshold} onChange={handleChange} className="form-control" />
          </div>
          <div className="form-group full-width">
            <label>Próg Offline (s)</label>
            <input type="number" name="offline_threshold_seconds" value={formData.offline_threshold_seconds} onChange={handleChange} className="form-control" />
          </div>
        </div>
        <button type="submit" className="btn-save" style={{ marginTop: '1rem' }}>
          <i className="fas fa-save"></i> Zapisz Ustawienia Czujnika
        </button>
      </form>
    </div>
  );
};


const SensorDetail = () => {
  const { sensorId } = useParams();
  const [sensor, setSensor] = useState(null); 
  const [liveData, setLiveData] = useState(null); 
  const [historicalData, setHistoricalData] = useState(null); 
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('live'); // 'live' lub 'settings'
  
  const { userSettings } = useAuth();
  const refreshInterval = userSettings ? userSettings.live_refresh_interval * 1000 : 5000;

  const fetchLiveData = useCallback(() => {
    apiClient.get(`/user/sensor/${sensorId}/live/`)
      .then(res => setLiveData(res.data))
      .catch(err => console.error("Błąd danych live:", err));
  }, [sensorId]);

  useEffect(() => {
    setLoading(true);
    const fetchSensorDetails = apiClient.get(`/user/sensors/${sensorId}/`);
    const fetchHistory = apiClient.get(`/user/sensor/${sensorId}/data/`); 

    Promise.all([fetchSensorDetails, fetchHistory])
      .then(([detailsRes, historyRes]) => {
        setSensor(detailsRes.data);
        
        const labels = historyRes.data.map(d => new Date(d.timestamp).toLocaleTimeString());
        const powerData = historyRes.data.map(d => d.power);
        
        setHistoricalData({
          labels,
          datasets: [{
            label: 'Moc (W)',
            data: powerData,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: true,
            tension: 0.3,
          }]
        });

        setLoading(false);
        fetchLiveData(); // Pobierz dane live po raz pierwszy
      })
      .catch(err => {
        console.error("Błąd ładowania czujnika:", err);
        setLoading(false);
      });
  }, [sensorId, fetchLiveData]);

  useInterval(fetchLiveData, refreshInterval);

  if (loading) {
    return <div>Ładowanie danych czujnika...</div>;
  }

  if (!sensor) {
    return <div>Nie znaleziono czujnika.</div>;
  }

  const isOnline = liveData ? liveData.is_online : sensor.is_online;

  // Sprawdzenie, czy 'house' jest wczytane (zagnieżdżone)
  const price_per_kwh = sensor.house?.price_per_kwh || 0.8; // Użyj 0.8 jako fallback

  return (
    <div>
      <Link to="/dashboard" className="back-button">
        <i className="fas fa-arrow-left"></i> Powrót do dashboardu
      </Link>

      <div className="sensor-header">
        <div className="sensor-title">
          <i className={`fas fa-${sensor.icon || 'microchip'}`} style={{ color: sensor.color }}></i>
          <h1>
            {sensor.name}
            <small>{sensor.location || 'Brak lokalizacji'}</small>
          </h1>
        </div>
        <div className={`live-indicator ${isOnline ? 'online' : 'offline'}`}>
          <div className="live-dot"></div>
          <span className="live-text">{isOnline ? 'ONLINE' : 'OFFLINE'}</span>
        </div>
      </div>
      
      {/* Taby do przełączania widoku */}
      <div className="tabs" style={{ marginBottom: '2rem' }}>
        <button className={`tab ${activeTab === 'live' ? 'active' : ''}`} onClick={() => setActiveTab('live')}>
          <i className="fas fa-tachometer-alt"></i> Dane na żywo
        </button>
        <button className={`tab ${activeTab === 'settings' ? 'active' : ''}`} onClick={() => setActiveTab('settings')}>
          <i className="fas fa-cogs"></i> Ustawienia Alertów
        </button>
      </div>

      {/* Widok LIVE */}
      {activeTab === 'live' && (
        <div id="live-view">
          <div className="stats-grid" style={{ marginBottom: '2rem' }}>
            <div className="stat-card">
              <h3><i className="fas fa-bolt"></i> Moc (Live)</h3>
              <span className="stat-value">{liveData ? liveData.power.toFixed(0) : '---'}</span>
              <span className="stat-unit">W</span>
            </div>
            <div className="stat-card">
              <h3><i className="fas fa-plug"></i> Napięcie (Live)</h3>
              <span className="stat-value">{liveData ? liveData.voltage.toFixed(1) : '---'}</span>
              <span className="stat-unit">V</span>
            </div>
            <div className="stat-card">
              <h3><i className="fas fa-wave-square"></i> Prąd (Live)</h3>
              <span className="stat-value">{liveData ? liveData.current.toFixed(2) : '---'}</span>
              <span className="stat-unit">A</span>
            </div>
            <div className="stat-card">
              <h3><i className="fas fa-dollar-sign"></i> Koszt / h (Live)</h3>
              <span className="stat-value">
                {liveData ? (liveData.power / 1000 * price_per_kwh).toFixed(3) : '---'}
              </span>
              <span className="stat-unit">PLN/h</span>
            </div>
          </div>

          <div className="data-table">
            <div className="table-header">
              <h2><i className="fas fa-chart-area"></i> Historia mocy (ostatnie odczyty)</h2>
            </div>
            <div style={{ padding: '1.5rem', height: '300px' }}>
              {historicalData ? (
                <Line data={historicalData} options={{ responsive: true, maintainAspectRatio: false }} />
              ) : (
                <p>Ładowanie wykresu...</p>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Widok USTAWIENIA */}
      {activeTab === 'settings' && (
        <SensorSettingsTab 
          sensor={sensor} 
          onSensorUpdate={(updatedSensor) => setSensor(updatedSensor)} // Aktualizuj stan sensora po zapisie
        />
      )}
    </div>
  );
};

export default SensorDetail;
