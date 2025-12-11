import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    const success = await login(username, password);
    
    if (success) {
      navigate('/dashboard');
    } else {
      setError('Nieprawidłowa nazwa użytkownika lub hasło.');
    }
  };

  // Używamy klas CSS z Twojego oryginalnego login.html dla spójności
  return (
    <div className="login-body"> {/* Dodaj klasę do body lub głównego div-a */}
      <div className="login-container">
        <div className="logo">
          <i className="fas fa-bolt"></i>
          <h1>Energy Monitor</h1>
          <p>System monitorowania energii</p>
        </div>

        {error && (
          <div className="error-message">
            <i className="fas fa-exclamation-circle"></i>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Nazwa użytkownika</label>
            <div className="input-wrapper">
              <i className="fas fa-user"></i>
              <input
                type="text"
                id="username"
                className="form-control"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Wprowadź nazwę użytkownika"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">Hasło</label>
            <div className="input-wrapper">
              <i className="fas fa-lock"></i>
              <input
                type="password"
                id="password"
                className="form-control"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Wprowadź hasło"
                required
              />
            </div>
          </div>

          <button type="submit" className="btn-submit">
            <i className="fas fa-sign-in-alt"></i> Zaloguj się
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
