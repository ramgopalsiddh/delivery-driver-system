import React, { useEffect, useState } from 'react';
import api from '../services/api';

const DriverManagementPage = () => {
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    driver_id: '',
    name: '',
    shift_hours_today: '',
    hours_worked_past_week: '',
  });
  const [isEditing, setIsEditing] = useState(false);
  const [currentDriverId, setCurrentDriverId] = useState(null);

  useEffect(() => {
    fetchDrivers();
  }, []);

  const fetchDrivers = async () => {
    try {
      const response = await api.get('/drivers');
      setDrivers(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch drivers');
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
        await api.put(`/drivers/${currentDriverId}`, formData);
      } else {
        await api.post('/drivers', formData);
      }
      setFormData({
        driver_id: '',
        name: '',
        shift_hours_today: '',
        hours_worked_past_week: '',
      });
      setIsEditing(false);
      setCurrentDriverId(null);
      fetchDrivers(); // Refresh list
    } catch (err) {
      setError('Failed to save driver');
      console.error(err);
    }
  };

  const handleEdit = (driver) => {
    setFormData({
      driver_id: driver.driver_id,
      name: driver.name,
      shift_hours_today: driver.shift_hours_today,
      hours_worked_past_week: driver.hours_worked_past_week,
    });
    setIsEditing(true);
    setCurrentDriverId(driver.driver_id);
  };

  const handleDelete = async (driverId) => {
    if (window.confirm(`Are you sure you want to delete driver ${driverId}?`)) {
      try {
        await api.delete(`/drivers/${driverId}`);
        fetchDrivers(); // Refresh list
      } catch (err) {
        setError('Failed to delete driver');
        console.error(err);
      }
    }
  };

  if (loading) return <div className="text-center text-gray-600">Loading drivers...</div>;
  if (error) return <div className="text-center text-red-500">Error: {error}</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Driver Management</h1>

      <div className="mb-8 p-4 bg-white shadow-md rounded-lg">
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">{isEditing ? 'Edit Driver' : 'Add New Driver'}</h2>
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="driver_id" className="block text-gray-700 text-sm font-bold mb-2">Driver ID:</label>
            <input
              type="text"
              id="driver_id"
              name="driver_id"
              value={formData.driver_id}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="e.g., driver123"
              required
              disabled={isEditing} // Disable editing driver_id
            />
          </div>
          <div>
            <label htmlFor="name" className="block text-gray-700 text-sm font-bold mb-2">Name:</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="e.g., John Doe"
              required
            />
          </div>
          <div>
            <label htmlFor="shift_hours_today" className="block text-gray-700 text-sm font-bold mb-2">Shift Hours Today:</label>
            <input
              type="number"
              id="shift_hours_today"
              name="shift_hours_today"
              value={formData.shift_hours_today}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="e.g., 8"
              step="0.1"
              required
            />
          </div>
          <div>
            <label htmlFor="hours_worked_past_week" className="block text-gray-700 text-sm font-bold mb-2">Hours Worked Past Week:</label>
            <input
              type="number"
              id="hours_worked_past_week"
              name="hours_worked_past_week"
              value={formData.hours_worked_past_week}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="e.g., 40"
              step="0.1"
              required
            />
          </div>
          <div className="md:col-span-2">
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            >
              {isEditing ? 'Update Driver' : 'Add Driver'}
            </button>
            {isEditing && (
              <button
                type="button"
                onClick={() => {
                  setIsEditing(false);
                  setCurrentDriverId(null);
                  setFormData({
                    driver_id: '',
                    name: '',
                    shift_hours_today: '',
                    hours_worked_past_week: '',
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
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Driver ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Shift Hours Today</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hours Worked Past Week</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {drivers.map((driver) => (
              <tr key={driver.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{driver.driver_id}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{driver.name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{driver.shift_hours_today}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{driver.hours_worked_past_week}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => handleEdit(driver)}
                    className="text-indigo-600 hover:text-indigo-900 mr-4"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(driver.driver_id)}
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

export default DriverManagementPage;
