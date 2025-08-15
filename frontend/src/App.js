import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import OrdersPage from './pages/OrdersPage';
import RoutesPage from './pages/RoutesPage';
import OptimizationPage from './pages/OptimizationPage';
import DriverManagementPage from './pages/DriverManagementPage';
import RouteManagementPage from './pages/RouteManagementPage';
import OrderManagementPage from './pages/OrderManagementPage';
import SimulationHistoryPage from './pages/SimulationHistoryPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/login" />;
};

function App() {
  const [token, setToken] = useState(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem('token');
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        {token && (
          <nav className="bg-gray-800 p-4 text-white">
            <ul className="flex space-x-4">
              <li><Link to="/" className="hover:text-gray-300">Dashboard</Link></li>
              <li><Link to="/orders" className="hover:text-gray-300">Orders</Link></li>
              <li><Link to="/routes" className="hover:text-gray-300">Routes</Link></li>
              <li><Link to="/optimization" className="hover:text-gray-300">Optimization</Link></li>
              <li><Link to="/manage-drivers" className="hover:text-gray-300">Manage Drivers</Link></li>
              <li><Link to="/manage-routes" className="hover:text-gray-300">Manage Routes</Link></li>
              <li><Link to="/manage-orders" className="hover:text-gray-300">Manage Orders</Link></li>
              <li><Link to="/simulation-history" className="hover:text-gray-300">Simulation History</Link></li>
              <li><button onClick={handleLogout} className="hover:text-gray-300">Logout</button></li>
            </ul>
          </nav>
        )}

        <main className="p-4">
          <Routes>
            <Route path="/login" element={<LoginPage setToken={setToken} />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/orders" element={<ProtectedRoute><OrdersPage /></ProtectedRoute>} />
            <Route path="/routes" element={<ProtectedRoute><RoutesPage /></ProtectedRoute>} />
            <Route path="/optimization" element={<ProtectedRoute><OptimizationPage /></ProtectedRoute>} />
            <Route path="/manage-drivers" element={<ProtectedRoute><DriverManagementPage /></ProtectedRoute>} />
            <Route path="/manage-routes" element={<ProtectedRoute><RouteManagementPage /></ProtectedRoute>} />
            <Route path="/manage-orders" element={<ProtectedRoute><OrderManagementPage /></ProtectedRoute>} />
            <Route path="/simulation-history" element={<ProtectedRoute><SimulationHistoryPage /></ProtectedRoute>} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;