import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';

const AdminHouses = () => {
  const [houses, setHouses] = useState([]);
  const [users, setUsers] = useState([]); // Lista userów do przypisania
  const [formData, setFormData] = useState({
    user: '',
    name: '',
    address: '',
    price_per_kwh: 0.80
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Pobierz listę domów i użytkowników
  const fetchData = () => {
    setLoading(true);
    const fetchHouses = apiClient.get('/admin/houses/');
    // Potrzebujemy endpointu do listowania userów. Użyjemy /api/user/me/ ale to hack
    // TODO: Zbuduj endpoint /api/admin/users/
    const fetchUsers = apiClient.get('/admin/houses/'); // Placeholder

    Promise.all([fetchHouses, fetchUsers])
      .then(([housesRes, usersRes]) => {
        setHouses(housesRes.data);
        // Prawidłowo: setUsers(usersRes.data)
        // Na razie wyciągamy userów z domów (hack)
        const allUsers = housesRes.data.map(h => h.user);
        setUsers(allUsers.filter((u, i, self) => self.findIndex(t => t.id === u.id) === i && u.username));
        setLoading(false);
      })
      .catch(err => setError("Błąd ładowania danych"));
  };
  
  useEffect(fetchData, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    setError(null);
    apiClient.post('/admin/houses/', formData)
      .then(res => {
        // Sukces, odśwież listę
        fetchData();
        setFormData({ user: '', name: '', address: '', price_per_kwh: 0.80 });
      })
      .catch(err => setError(err.response?.data?.message || "Błąd zapisu."));
  };

  return (
    <div className="assign-container">
      <div className="assign-header">
        <h1><i className="fas fa-user-plus"></i> Przypisz dom do użytkownika</h1>
      </div>

      <div className="form-panel">
        <h2><i className="fas fa-plus-circle"></i> Nowy dom</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="user">Użytkownik *</label>
              <select name="user" id="user" value={formData.user} onChange={handleChange} className="form-control" required>
                <option value="">Wybierz użytkownika</option>
                {users.map(user => (
                  <option key={user.id} value={user.id}>{user.username}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="name">Nazwa domu *</label>
              <input type="text" name="name" id="name" value={formData.name} onChange={handleChange} className="form-control" required />
            </div>
            <div className="form-group">
              <label htmlFor="address">Adres</label>
              <input type="text" name="address" id="address" value={formData.address} onChange={handleChange} className="form-control" />
            </div>
            <div className="form-group">
              <label htmlFor="price_per_kwh">Cena za kWh (PLN) *</label>
              <input type="number" step="0.01" name="price_per_kwh" id="price_per_kwh" value={formData.price_per_kwh} onChange={handleChange} className="form-control" required />
            </div>
            <div className="form-group full-width">
              <button type="submit" className="btn-submit">
                <i className="fas fa-check"></i> Przypisz dom
              </button>
            </div>
          </div>
        </form>
      </div>
      
      <div className="houses-list panel">
         <h2><i className="fas fa-list"></i> Ostatnio dodane domy</h2>
         <table className="houses-table">
            <thead>
              <tr>
                <th>Nazwa</th><th>Użytkownik</th><th>Czujniki</th><th>Cena/kWh</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="4">Ładowanie...</td></tr>
              ) : (
                houses.map(house => (
                  <tr key={house.id}>
                    <td><strong>{house.name}</strong></td>
                    <td>{house.user?.username || 'Brak'}</td>
                    <td>{house.sensor_count}</td>
                    <td>{house.price_per_kwh} PLN</td>
                  </tr>
                ))
              )}
            </tbody>
         </table>
      </div>
    </div>
  );
};

export default AdminHouses;
