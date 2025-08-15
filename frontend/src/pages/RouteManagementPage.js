import React, { useEffect, useState } from 'react';
import api from '../services/api';

const RouteManagementPage = () => {
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    route_id: '',
    distance_km: '',
    traffic_level: '',
    base_time_minutes: '',
  });
  const [isEditing, setIsEditing] = useState(false);
  const [currentRouteId, setCurrentRouteId] = useState(null);

  useEffect(() => {
    fetchRoutes();
  }, []);

  const fetchRoutes = async () => {
    try {
      const response = await api.get('/routes');
      setRoutes(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch routes');
      setLoading(false);
      console.error(err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isEditing) {
        await api.put(`/routes/${currentRouteId}`, formData);
      } else {
        await api.post('/routes', formData);
      }
      setFormData({
        route_id: '',
        distance_km: '',
        traffic_level: '',
        base_time_minutes: '',
      });
      setIsEditing(false);
      setCurrentRouteId(null);
      fetchRoutes(); // Refresh list
    } catch (err) {
      setError('Failed to save route');
      console.error(err);
    }
  };

  const handleEdit = (route) => {
    setFormData({
      route_id: route.route_id,
      distance_km: route.distance_km,
      traffic_level: route.traffic_level,
      base_time_minutes: route.base_time_minutes,
    });
    setIsEditing(true);
    setCurrentRouteId(route.route_id);
  };

  const handleDelete = async (routeId) => {
    if (window.confirm(`Are you sure you want to delete route ${routeId}?`)) {
      try {
        await api.delete(`/routes/${routeId}`);
        fetchRoutes(); // Refresh list
      } catch (err) {
        setError('Failed to delete route');
        console.error(err);
      }
    }
  };

  if (loading) return <div className="text-center text-gray-600">Loading routes...</div>;
  if (error) return <div className="text-center text-red-500">Error: {error}</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Route Management</h1>

      <div className="mb-8 p-4 bg-white shadow-md rounded-lg">
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">{isEditing ? 'Edit Route' : 'Add New Route'}</h2>
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="route_id" className="block text-gray-700 text-sm font-bold mb-2">Route ID:</label>
            <input
              type="text"
              id="route_id"
              name="route_id"
              value={formData.route_id}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="e.g., routeA"
              required
              disabled={isEditing} // Disable editing route_id
            />
          </div>
          <div>
            <label htmlFor="distance_km" className="block text-gray-700 text-sm font-bold mb-2">Distance (km):</label>
            <input
              type="number"
              id="distance_km"
              name="distance_km"
              value={formData.distance_km}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="e.g., 10.5"
              step="0.1"
              required
            />
          </div>
          <div>
            <label htmlFor="traffic_level" className="block text-gray-700 text-sm font-bold mb-2">Traffic Level:</label>
            <select
              id="traffic_level"
              name="traffic_level"
              value={formData.traffic_level}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              required
            >
              <option value="">Select Traffic Level</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
          <div>
            <label htmlFor="base_time_minutes" className="block text-gray-700 text-sm font-bold mb-2">Base Time (minutes):</label>
            <input
              type="number"
              id="base_time_minutes"
              name="base_time_minutes"
              value={formData.base_time_minutes}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="e.g., 15"
              required
            />
          </div>
          <div className="md:col-span-2">
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            >
              {isEditing ? 'Update Route' : 'Add Route'}
            </button>
            {isEditing && (
              <button
                type="button"
                onClick={() => {
                  setIsEditing(false);
                  setCurrentRouteId(null);
                  setFormData({
                    route_id: '',
                    distance_km: '',
                    traffic_level: '',
                    base_time_minutes: '',
                  });
                }}
                className="ml-4 bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      </div>

      <div className="overflow-x-auto bg-white shadow-md rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Route ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Distance (km)</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Traffic Level</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Base Time (min)</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {routes.map((route) => (
              <tr key={route.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{route.route_id}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{route.distance_km}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{route.traffic_level}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{route.base_time_minutes}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => handleEdit(route)}
                    className="text-indigo-600 hover:text-indigo-900 mr-4"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(route.route_id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default RouteManagementPage;
