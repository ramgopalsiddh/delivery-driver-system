import React, { useEffect, useState } from 'react';
import api from '../services/api';
import DriverTable from '../components/DriverTable';
import OrderList from '../components/OrderList';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Pie } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

const Dashboard = () => {
  const [drivers, setDrivers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [kpis, setKpis] = useState(null); // New state for KPIs
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const driversResponse = await api.get('/drivers');
        setDrivers(driversResponse.data);

        const ordersResponse = await api.get('/orders');
        setOrders(ordersResponse.data);

        // Fetch optimized schedule to get latest KPIs
        const optimizedScheduleResponse = await api.get('/optimized_schedule');
        if (optimizedScheduleResponse.data && optimizedScheduleResponse.data.kpis) {
          setKpis(optimizedScheduleResponse.data.kpis);
        } else if (optimizedScheduleResponse.data && optimizedScheduleResponse.data.length > 0) {
            // If optimized_schedule returns assignments, but not KPIs directly, 
            // we might need a separate endpoint for KPIs or re-run optimization to get them.
            // For now, assuming optimized_schedule will eventually return KPIs or we'll add a dedicated KPI endpoint.
            // For simplicity, I'll just display the message if no KPIs are directly available from /optimized_schedule
            console.warn("KPIs not directly available from /optimized_schedule. Run optimization first.");
        }

        setLoading(false);
      } catch (err) {
        setError('Failed to fetch data');
        setLoading(false);
        console.error(err);
      }
    };

    fetchData();
  }, []);

  const onTimeLateData = kpis ? {
    labels: ['On-time Deliveries', 'Late Deliveries'],
    datasets: [
      {
        data: [kpis.on_time_deliveries, kpis.late_deliveries],
        backgroundColor: ['#36A2EB', '#FF6384'],
        hoverBackgroundColor: ['#36A2EB', '#FF6384'],
      },
    ],
  } : {};

  const fuelCostData = kpis ? {
    labels: ['Total Fuel Cost', 'Other Costs'], // Assuming 'Other Costs' is total profit - fuel cost
    datasets: [
      {
        data: [kpis.total_fuel_cost, kpis.total_profit - kpis.total_fuel_cost],
        backgroundColor: ['#FFCE56', '#4BC0C0'],
        hoverBackgroundColor: ['#FFCE56', '#4BC0C0'],
      },
    ],
  } : {};

  if (loading) return <div className="text-center text-gray-600">Loading dashboard data...</div>;
  if (error) return <div className="text-center text-red-500">Error: {error}</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Dashboard</h1>

      {kpis && (
        <section className="mb-8 p-4 bg-white shadow-md rounded-lg">
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">Key Performance Indicators</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-gray-50 p-3 rounded-lg shadow-sm">
              <p className="text-gray-600 text-sm">Total Profit</p>
              <p className="text-xl font-bold text-green-600">₹{kpis.total_profit.toFixed(2)}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg shadow-sm">
              <p className="text-gray-600 text-sm">Efficiency Score</p>
              <p className="text-xl font-bold text-blue-600">{kpis.efficiency_score.toFixed(2)}%</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg shadow-sm">
              <p className="text-gray-600 text-sm">Total Deliveries</p>
              <p className="text-xl font-bold text-gray-800">{kpis.total_deliveries}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg shadow-sm">
              <p className="text-gray-600 text-sm">On-time Deliveries</p>
              <p className="text-xl font-bold text-green-600">{kpis.on_time_deliveries}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg shadow-sm">
              <p className="text-gray-600 text-sm">Late Deliveries</p>
              <p className="text-xl font-bold text-red-600">{kpis.late_deliveries}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg shadow-sm">
              <p className="text-gray-600 text-sm">Total Fuel Cost</p>
              <p className="text-xl font-bold text-red-600">₹{kpis.total_fuel_cost.toFixed(2)}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
            <div className="bg-white p-4 shadow-md rounded-lg">
              <h3 className="text-xl font-semibold text-gray-700 mb-4">On-time vs Late Deliveries</h3>
              <Pie data={onTimeLateData} />
            </div>
            <div className="bg-white p-4 shadow-md rounded-lg">
              <h3 className="text-xl font-semibold text-gray-700 mb-4">Fuel Cost Breakdown</h3>
              <Pie data={fuelCostData} />
            </div>
          </div>
        </section>
      )}

      <section className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">Drivers Overview</h2>
        <DriverTable drivers={drivers} />
      </section>

      <section>
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">Orders Overview</h2>
        <OrderList orders={orders} />
      </section>
    </div>
  );
};

export default Dashboard;
