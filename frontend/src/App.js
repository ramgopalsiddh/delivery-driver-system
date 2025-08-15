import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import OrdersPage from './pages/OrdersPage';
import RoutesPage from './pages/RoutesPage';
import OptimizationPage from './pages/OptimizationPage';
import DriverManagementPage from './pages/DriverManagementPage';
import RouteManagementPage from './pages/RouteManagementPage';
import OrderManagementPage from './pages/OrderManagementPage';
import SimulationHistoryPage from './pages/SimulationHistoryPage'; // New import

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <nav className="bg-gray-800 p-4 text-white">
          <ul className="flex space-x-4">
            <li>
              <Link to="/" className="hover:text-gray-300">Dashboard</Link>
            </li>
            <li>
              <Link to="/orders" className="hover:text-gray-300">Orders</Link>
            </li>
            <li>
              <Link to="/routes" className="hover:text-gray-300">Routes</Link>
            </li>
            <li>
              <Link to="/optimization" className="hover:text-gray-300">Optimization</Link>
            </li>
            <li>
              <Link to="/manage-drivers" className="hover:text-gray-300">Manage Drivers</Link>
            </li>
            <li>
              <Link to="/manage-routes" className="hover:text-gray-300">Manage Routes</Link>
            </li>
            <li>
              <Link to="/manage-orders" className="hover:text-gray-300">Manage Orders</Link>
            </li>
            <li>
              <Link to="/simulation-history" className="hover:text-gray-300">Simulation History</Link>
            </li>
          </ul>
        </nav>

        <main className="p-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/orders" element={<OrdersPage />} />
            <Route path="/routes" element={<RoutesPage />} />
            <Route path="/optimization" element={<OptimizationPage />} />
            <Route path="/manage-drivers" element={<DriverManagementPage />} />
            <Route path="/manage-routes" element={<RouteManagementPage />} />
            <Route path="/manage-orders" element={<OrderManagementPage />} />
            <Route path="/simulation-history" element={<SimulationHistoryPage />} /> {/* New Route */}
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
