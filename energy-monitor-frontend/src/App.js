import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Import komponentów-strażników
import ProtectedRoute from './components/ProtectedRoute';
import AdminRoute from './components/AdminRoute';

// Import stron (Pages)
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import SensorDetail from './pages/SensorDetail';
import HouseDetail from './pages/HouseDetail';
import Alerts from './pages/Alerts';
import AlertCreate from './pages/AlertCreate';
import Settings from './pages/Settings';

// Import Stron Admina
import AdminDashboard from './pages/AdminDashboard';
import AdminHouses from './pages/AdminHouses';
import AdminSensors from './pages/AdminSensors';

function App() {
  return (
    <Routes>
      {/* Strony publiczne */}
      <Route path="/login" element={<Login />} />
      {/* TODO: <Route path="/register" element={<Register />} /> */}

      {/* Strony chronione (Użytkownik) */}
      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/sensor/:sensorId" element={<SensorDetail />} />
        <Route path="/house/:houseId" element={<HouseDetail />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/alerts/create" element={<AlertCreate />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
      
      {/* Strony chronione (Admin) */}
      <Route element={<AdminRoute />}>
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
        <Route path="/admin/houses" element={<AdminHouses />} />
        <Route path="/admin/sensors" element={<AdminSensors />} />
      </Route>

      {/* Domyślne przekierowanie */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
