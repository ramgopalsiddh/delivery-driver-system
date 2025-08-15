import React, { useEffect, useState } from 'react';
import api from '../services/api';
import RouteDetails from '../components/RouteDetails';

const RoutesPage = () => {
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
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

    fetchRoutes();
  }, []);

  if (loading) return <div className="text-center text-gray-600">Loading routes...</div>;
  if (error) return <div className="text-center text-red-500">Error: {error}</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Routes</h1>
      <RouteDetails routes={routes} />
    </div>
  );
};

export default RoutesPage;
