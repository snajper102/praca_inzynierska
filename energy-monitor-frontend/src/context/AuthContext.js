import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import apiClient from '../services/api';
import axios from 'axios'; 

const LOGIN_URL = 'http://127.0.0.1:8000/api-token-auth/';
const ME_URL = '/user/me/'; // Używamy apiClient, więc ścieżka względna

const AuthContext = createContext();

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  const [authToken, setAuthToken] = useState(() => localStorage.getItem('authToken'));
  const [user, setUser] = useState(null);
  const [userSettings, setUserSettings] = useState(null);
  const [loading, setLoading] = useState(true);

  // POPRAWKA: Używamy useCallback, aby 'logout' nie zmieniał się przy każdym renderze
  const logout = useCallback(() => {
    localStorage.removeItem('authToken');
    setAuthToken(null);
    setUser(null);
    setUserSettings(null);
  }, []); // Pusta tablica, bo nie ma zależności

  // POPRAWKA: Używamy useCallback, aby 'fetchUserData' nie zmieniał się przy każdym renderze
  const fetchUserData = useCallback(async () => {
    try {
      const response = await apiClient.get(ME_URL);
      setUser(response.data);
      setUserSettings(response.data.settings || null);
      return response.data;
    } catch (error) {
      console.error("Błąd pobierania danych użytkownika:", error);
      logout(); // Wyloguj, jeśli token jest zły
      return null;
    }
  }, [logout]); // Zależy od 'logout'

  useEffect(() => {
    if (authToken) {
      // POPRAWKA: Dodajemy 'fetchUserData' do tablicy zależności
      fetchUserData().finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [authToken, fetchUserData]); // <-- POPRAWKA TUTAJ

  const login = async (username, password) => {
    try {
      const response = await axios.post(LOGIN_URL, { username, password });
      const token = response.data.token;
      
      localStorage.setItem('authToken', token);
      setAuthToken(token); // To uruchomi useEffect i pobierze dane usera
      
      return true;
    } catch (error) {
      console.error('Błąd logowania:', error);
      return false;
    }
  };

  const updateSettings = (newSettings) => {
    setUserSettings(newSettings);
    setUser(prevUser => ({ ...prevUser, settings: newSettings }));
  };

  const value = {
    authToken,
    user,
    userSettings,
    login,
    logout,
    updateSettings, 
    isAuthenticated: !!authToken,
    isAdmin: user ? user.is_staff : false,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
