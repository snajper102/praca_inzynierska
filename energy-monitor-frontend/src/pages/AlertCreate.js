import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../services/api';

const AlertCreate = () => {
  const [formData, setFormData] = useState({
    house: '',
    sensor: '',
    alert_type: 'anomaly',
    severity: 'warning',
    message: '',
    value: '',
    threshold: ''
  });
  const [houses, setHouses] = useState([]);
  const [sensors, setSensors] = useState([]);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Pobierz domy, aby wypełnić select
    apiClient.get('/user/houses/')
      .then(res => setHouses(res.data))
      .catch(err => console.error(err));
      
    // Pobierz wszystkie czujniki usera
    apiClient.get('/user/sensors/')
      .then(res => setSensors(res.data))
      .catch(err => console.error(err));
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };
  
  // Filtruj czujniki na podstawie wybranego domu
  const sensorsInHouse = formData.house
    ? sensors.filter(s => s.house.toString() === formData.house)
    : sensors;

  const handleSubmit = (e) => {
    e.preventDefault();
    setError(null);
    
    // Przygotuj dane do wysłania (usuń puste pola)
    const payload = { ...formData };
    if (!payload.sensor) delete payload.sensor;
    if (!payload.value) delete payload.value;
    if (!payload.threshold) delete payload.threshold;

    apiClient.post('/user/alerts/', payload)
      .then(res => {
        // Sukces, wróć do listy alertów
        navigate('/alerts');
      })
      .catch(err => {
        setError(err.response?.data?.message || "Wystąpił błąd. Sprawdź formularz.");
      });
  };

  return (
    <div className="form-container">
      <div className="form-header">
        <h1><i className="fas fa-plus-circle"></i> Utwórz nowy alert</h1>
      </div>
      
      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="house">Dom *</label>
            <select name="house" id="house" value={formData.house} onChange={handleChange} className="form-control" required>
              <option value="">Wybierz dom</option>
              {houses.map(h => (
                <option key={h.id} value={h.id}>{h.name}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="sensor">Czujnik (opcjonalnie)</label>
            <select name="sensor" id="sensor" value={formData.sensor} onChange={handleChange} className="form-control" disabled={!formData.house}>
              <option value="">(Cały dom)</option>
              {sensorsInHouse.map(s => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="alert_type">Typ alertu *</label>
            <select name="alert_type" id="alert_type" value={formData.alert_type} onChange={handleChange} className="form-control" required>
              <option value="anomaly">Inna anomalia</option>
              <option value="power_high">Przekroczenie mocy</option>
              <option value="current_high">Przekroczenie prądu</option>
              <option value="voltage_anomaly">Anomalia napięcia</option>
              <option value="monthly_limit">Limit miesięczny</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="severity">Ważność *</label>
            <select name="severity" id="severity" value={formData.severity} onChange={handleChange} className="form-control" required>
              <option value="info">Informacja</option>
              <option value="warning">Ostrzeżenie</option>
              <option value="critical">Krytyczny</option>
            </select>
          </div>

          <div className="form-group full-width">
            <label htmlFor="message">Wiadomość *</label>
            <textarea name="message" id="message" value={formData.message} onChange={handleChange} className="form-control" required></textarea>
          </div>
          
          <div className="form-group">
            <label htmlFor="value">Wartość (opcjonalnie)</label>
            <input type="number" step="0.1" name="value" id="value" value={formData.value} onChange={handleChange} className="form-control" />
          </div>
          
          <div className="form-group">
            <label htmlFor="threshold">Próg (opcjonalnie)</label>
            <input type="number" step="0.1" name="threshold" id="threshold" value={formData.threshold} onChange={handleChange} className="form-control" />
          </div>
        </div>
        
        <button type="submit" className="btn-submit">
          <i className="fas fa-save"></i> Zapisz Alert
        </button>
      </form>
    </div>
  );
};

export default AlertCreate;
