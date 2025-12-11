import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import apiClient from '../services/api';

// Zakładka 1: Profil (z profile.html)
const ProfileTab = ({ user, houses }) => (
  <div className="profile-section">
    <div className="section-header">
      <h2><i className="fas fa-user"></i> Informacje o koncie</h2>
    </div>
    <div className="info-grid">
      <div className="info-item">
        <span className="info-label">Nazwa użytkownika</span>
        <span className="info-value">{user.username}</span>
      </div>
      <div className="info-item">
        <span className="info-label">Email</span>
        <span className="info-value">{user.email || "Nie ustawiono"}</span>
      </div>
      <div className="info-item">
        <span className="info-label">Data rejestracji</span>
        <span className="info-value">{new Date(user.date_joined).toLocaleDateString('pl-PL')}</span>
      </div>
    </div>
    
    <div className="section-header" style={{ marginTop: '2rem' }}>
      <h2><i className="fas fa-home"></i> Moje domy</h2>
    </div>
    <div className="houses-list">
      {houses.map(house => (
        <div className="house-item" key={house.id}>
          <div className="house-item-header">
            <div className="house-name"><i className="fas fa-home"></i> {house.name}</div>
            {/* Poprawka: house.sensors jest teraz tablicą */}
            <span className="sensor-count">{house.sensors ? house.sensors.length : 0} czujników</span>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Zakładka 2: Ustawienia (z settings.html)
const SettingsTab = ({ settings, onSave }) => {
  const [formData, setFormData] = useState(settings);

  useEffect(() => {
    setFormData(settings);
  }, [settings]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  if (!formData) return <p>Ładowanie ustawień...</p>;

  return (
    <div className="settings-section">
      <form onSubmit={handleSubmit}>
        <div className="settings-section">
          <h2 className="section-title"><i className="fas fa-palette"></i> Personalizacja</h2>
          {/* Tu dodaj resztę pól z settings.html, np. motyw */}
          <div className="form-group">
            <label>Odświeżanie live widget (s)</label>
            <input 
              type="range" 
              name="live_refresh_interval" 
              min="1" max="60" 
              value={formData.live_refresh_interval || 5}
              onChange={handleChange}
              className="range-slider"
            />
            <span className="range-value">{formData.live_refresh_interval || 5}s</span>
          </div>
        </div>

        <div className="settings-section">
          <h2 className="section-title"><i className="fas fa-bell"></i> Alerty</h2>
          <div className="form-group">
            <div className="toggle-group">
              <label>Alerty email</label>
              <input 
                type="checkbox" 
                name="email_alerts" 
                checked={formData.email_alerts}
                onChange={handleChange}
              />
            </div>
          </div>
          <div className="form-group">
            <label>Częstotliwość alertów</label>
            <select name="alert_frequency" value={formData.alert_frequency} onChange={handleChange} className="form-control">
              <option value="immediate">Natychmiast</option>
              <option value="hourly">Co godzinę</option>
              <option value="daily">Raz dziennie</option>
            </select>
          </div>
        </div>
        
        {/* Tu dodaj sekcję 'Cele i predykcje' */}

        <button type="submit" className="btn-save">
          <i className="fas fa-save"></i> Zapisz ustawienia
        </button>
      </form>
    </div>
  );
};


const Settings = () => {
  const { user, userSettings, updateSettings } = useAuth();
  const [houses, setHouses] = useState([]);
  const [activeTab, setActiveTab] = useState('profile');
  const [message, setMessage] = useState(null);

  useEffect(() => {
    // Pobierz domy (do zakładki profil)
    apiClient.get('/user/houses/')
      .then(res => setHouses(res.data))
      .catch(err => console.error(err));
  }, []);

  const handleSaveSettings = (newSettings) => {
    setMessage(null);
    // Używamy endpointu /api/user/settings/ (który działa na ID usera)
    // POPRAWKA: Dynamiczny URL
    apiClient.put(`/user/settings/${userSettings.id}/`, newSettings)
      .then(res => {
        updateSettings(res.data); // Aktualizuj globalny stan
        setMessage({ type: 'success', text: 'Ustawienia zapisane!' });
      })
      .catch(err => {
        setMessage({ type: 'error', text: 'Błąd zapisu ustawień.' });
      });
  };

  if (!user || !userSettings) {
    return <div className="container">Ładowanie...</div>;
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <div className="profile-avatar">{user.username.charAt(0).toUpperCase()}</div>
        <div className="profile-info">
          <h1>{user.username}</h1>
          <p>{user.email}</p>
        </div>
      </div>
      
      {message && (
        <div className={message.type === 'success' ? 'success-message' : 'error-message'} 
             style={{ padding: '1rem', borderRadius: '0.5rem', margin: '1rem 0' }}>
          {message.text}
        </div>
      )}

      {/* Taby */}
      <div className="tabs" style={{ marginBottom: '2rem' }}>
        <button className={`tab ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => setActiveTab('profile')}>
          <i className="fas fa-user"></i> Profil
        </button>
        <button className={`tab ${activeTab === 'settings' ? 'active' : ''}`} onClick={() => setActiveTab('settings')}>
          <i className="fas fa-cog"></i> Ustawienia
        </button>
      </div>

      {activeTab === 'profile' && <ProfileTab user={user} houses={houses} />}
      {activeTab === 'settings' && <SettingsTab settings={userSettings} onSave={handleSaveSettings} />}
    </div>
  );
};

export default Settings;
