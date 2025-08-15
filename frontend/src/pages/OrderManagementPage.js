import React, { useEffect, useState } from 'react';
import api from '../services/api';

const OrderManagementPage = () => {
  const [orders, setOrders] = useState([]);
  const [routes, setRoutes] = useState([]); // To populate route_id dropdown
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    order_id: '',
    value: '',
    route_id: '',
    delivery_time: '',
    assigned_driver_id: '',
  });
  const [isEditing, setIsEditing] = useState(false);
  const [currentOrderId, setCurrentOrderId] = useState(null);

  useEffect(() => {
    fetchOrdersAndRoutes();
  }, []);

  const fetchOrdersAndRoutes = async () => {
    try {
      const ordersResponse = await api.get('/orders');
      setOrders(ordersResponse.data);

      const routesResponse = await api.get('/routes');
      setRoutes(routesResponse.data);

      setLoading(false);
    } catch (err) {
      setError('Failed to fetch data');
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
      const payload = {
        ...formData,
        value: parseFloat(formData.value),
        // delivery_time needs to be in ISO format for backend
        delivery_time: new Date(formData.delivery_time).toISOString(),
      };

      if (isEditing) {
        await api.put(`/orders/${currentOrderId}`, payload);
      } else {
        await api.post('/orders', payload);
      }
      setFormData({
        order_id: '',
        value: '',
        route_id: '',
        delivery_time: '',
        assigned_driver_id: '',
      });
      setIsEditing(false);
      setCurrentOrderId(null);
      fetchOrdersAndRoutes(); // Refresh list
    } catch (err) {
      setError('Failed to save order');
      console.error(err);
    }
  };

  const handleEdit = (order) => {
    setFormData({
      order_id: order.order_id,
      value: order.value,
      route_id: order.route_id,
      // Convert ISO string back to YYYY-MM-DDTHH:MM for datetime-local input
      delivery_time: order.delivery_time ? new Date(order.delivery_time).toISOString().slice(0, 16) : '',
      assigned_driver_id: order.assigned_driver_id || '',
    });
    setIsEditing(true);
    setCurrentOrderId(order.order_id);
  };

  const handleDelete = async (orderId) => {
    if (window.confirm(`Are you sure you want to delete order ${orderId}?`)) {
      try {
        await api.delete(`/orders/${orderId}`);
        fetchOrdersAndRoutes(); // Refresh list
      } catch (err) {
        setError('Failed to delete order');
        console.error(err);
      }
    }
  };

  if (loading) return <div className="text-center text-gray-600">Loading orders...</div>;
  if (error) return <div className="text-center text-red-500">Error: {error}</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Order Management</h1>

      <div className="mb-8 p-4 bg-white shadow-md rounded-lg">
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">{isEditing ? 'Edit Order' : 'Add New Order'}</h2>
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="order_id" className="block text-gray-700 text-sm font-bold mb-2">Order ID:</label>
            <input
              type="text"
              id="order_id"
              name="order_id"
              value={formData.order_id}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="e.g., order123"
              required
              disabled={isEditing} // Disable editing order_id
            />
          </div>
          <div>
            <label htmlFor="value" className="block text-gray-700 text-sm font-bold mb-2">Value:</label>
            <input
              type="number"
              id="value"
              name="value"
              value={formData.value}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="e.g., 150.75"
              step="0.01"
              required
            />
          </div>
          <div>
            <label htmlFor="route_id" className="block text-gray-700 text-sm font-bold mb-2">Route ID:</label>
            <select
              id="route_id"
              name="route_id"
              value={formData.route_id}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              required
            >
              <option value="">Select Route</option>
              {routes.map(route => (
                <option key={route.route_id} value={route.route_id}>{route.route_id}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="delivery_time" className="block text-gray-700 text-sm font-bold mb-2">Delivery Time:</label>
            <input
              type="datetime-local"
              id="delivery_time"
              name="delivery_time"
              value={formData.delivery_time}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              required
            />
          </div>
          <div>
            <label htmlFor="assigned_driver_id" className="block text-gray-700 text-sm font-bold mb-2">Assigned Driver ID (Optional):</label>
            <input
              type="text"
              id="assigned_driver_id"
              name="assigned_driver_id"
              value={formData.assigned_driver_id}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="e.g., 1"
            />
          </div>
          <div className="md:col-span-2">
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            >
              {isEditing ? 'Update Order' : 'Add Order'}
            </button>
            {isEditing && (
              <button
                type="button"
                onClick={() => {
                  setIsEditing(false);
                  setCurrentOrderId(null);
                  setFormData({
                    order_id: '',
                    value: '',
                    route_id: '',
                    delivery_time: '',
                    assigned_driver_id: '',
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
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Route ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Delivery Time</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assigned Driver</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {orders.map((order) => (
              <tr key={order.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{order.order_id}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{order.value}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{order.route_id}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(order.delivery_time).toLocaleString()}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{order.assigned_driver_id || 'Unassigned'}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => handleEdit(order)}
                    className="text-indigo-600 hover:text-indigo-900 mr-4"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(order.order_id)}
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

export default OrderManagementPage;
