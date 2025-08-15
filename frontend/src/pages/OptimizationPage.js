import React, { useState } from 'react';
import api from '../services/api';
import OptimizationResults from '../components/OptimizationResults';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const OptimizationPage = () => {
  const [optimizedSchedule, setOptimizedSchedule] = useState(null);
  const [kpis, setKpis] = useState(null); // New state for KPIs
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [simulationInputs, setSimulationInputs] = useState({
    num_available_drivers: '',
    route_start_time: '',
    max_hours_per_driver_per_day: '',
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSimulationInputs({ ...simulationInputs, [name]: value });
  };

  const handleOptimize = async () => {
    setLoading(true);
    setError(null);
    setMessage(null);
    setOptimizedSchedule(null); // Clear previous results
    setKpis(null); // Clear previous KPIs

    try {
      const payload = {};
      if (simulationInputs.num_available_drivers !== '') {
        payload.num_available_drivers = parseInt(simulationInputs.num_available_drivers);
      }
      if (simulationInputs.route_start_time !== '') {
        payload.route_start_time = simulationInputs.route_start_time;
      }
      if (simulationInputs.max_hours_per_driver_per_day !== '') {
        payload.max_hours_per_driver_per_day = parseFloat(simulationInputs.max_hours_per_driver_per_day);
      }

      const response = await api.post('/assign_orders', payload);
      setMessage(response.data.message);
      setKpis(response.data.kpis); // Set KPIs

      const scheduleResponse = await api.get('/optimized_schedule');
      console.log("Optimized Schedule Response:", scheduleResponse.data); // DEBUG LOG
      setOptimizedSchedule(scheduleResponse.data);

    } catch (err) {
      setError('Failed to run optimization');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Chart data for On-time vs Late Deliveries
  const onTimeLateChartData = kpis ? {
    labels: ['On-time Deliveries', 'Late Deliveries'],
    datasets: [
      {
        label: 'Number of Deliveries',
        data: [kpis.on_time_deliveries, kpis.late_deliveries],
        backgroundColor: ['rgba(75, 192, 192, 0.6)', 'rgba(255, 99, 132, 0.6)'],
        borderColor: ['rgba(75, 192, 192, 1)', 'rgba(255, 99, 132, 1)'],
        borderWidth: 1,
      },
    ],
  } : {};

  const onTimeLateChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'On-time vs Late Deliveries',
      },
    },
  };

  // Chart data for Fuel Cost Breakdown (simplified for now, just total fuel cost)
  const fuelCostChartData = kpis ? {
    labels: ['Total Fuel Cost'],
    datasets: [
      {
        label: 'Cost (₹)',
        data: [kpis.total_fuel_cost],
        backgroundColor: ['rgba(255, 206, 86, 0.6)'],
        borderColor: ['rgba(255, 206, 86, 1)'],
        borderWidth: 1,
      },
    ],
  } : {};

  const fuelCostChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Fuel Cost Breakdown',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Cost (₹)',
        },
      },
    },
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Optimization</h1>

      <div className="mb-6 p-4 bg-white shadow-md rounded-lg">
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">Simulation Inputs</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label htmlFor="num_available_drivers" className="block text-gray-700 text-sm font-bold mb-2">Number of Available Drivers:</label>
            <input
              type="number"
              id="num_available_drivers"
              name="num_available_drivers"
              value={simulationInputs.num_available_drivers}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="e.g., 5"
            />
          </div>
          <div>
            <label htmlFor="route_start_time" className="block text-gray-700 text-sm font-bold mb-2">Route Start Time (HH:MM):</label>
            <input
              type="text"
              id="route_start_time"
              name="route_start_time"
              value={simulationInputs.route_start_time}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="e.g., 09:00"
            />
          </div>
          <div>
            <label htmlFor="max_hours_per_driver_per_day" className="block text-gray-700 text-sm font-bold mb-2">Max Hours Per Driver Per Day:</label>
            <input
              type="number"
              id="max_hours_per_driver_per_day"
              name="max_hours_per_driver_per_day"
              value={simulationInputs.max_hours_per_driver_per_day}
              onChange={handleInputChange}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="e.g., 8"
            />
          </div>
        </div>
        <button
          onClick={handleOptimize}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
          disabled={loading}
        >
          {loading ? 'Optimizing...' : 'Run Optimization'}
        </button>
        {message && <p className="mt-2 text-green-600">{message}</p>}
        {error && <p className className="mt-2 text-red-500">Error: {error}</p>}
      </div>

      {kpis && (
        <div className="mb-6 p-4 bg-white shadow-md rounded-lg">
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">Simulation Results (KPIs)</h2>
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
            <div className="bg-gray-50 p-3 rounded-lg shadow-sm">
              <p className="text-gray-600 text-sm">Total Penalties</p>
              <p className="text-xl font-bold text-red-600">₹{kpis.total_penalties.toFixed(2)}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg shadow-sm">
              <p className="text-gray-600 text-sm">Total Bonuses</p>
              <p className="text-xl font-bold text-green-600">₹{kpis.total_bonuses.toFixed(2)}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            <div className="p-4 bg-white shadow-md rounded-lg">
              <Bar data={onTimeLateChartData} options={onTimeLateChartOptions} />
            </div>
            <div className="p-4 bg-white shadow-md rounded-lg">
              <Bar data={fuelCostChartData} options={fuelCostChartOptions} />
            </div>
          </div>
        </div>
      )}

      {optimizedSchedule && optimizedSchedule.length > 0 && (
        <OptimizationResults schedule={optimizedSchedule} />
      )}
       {optimizedSchedule && optimizedSchedule.length === 0 && !loading && (
        <p className="text-center text-gray-600">No optimized schedule available. Run optimization first.</p>
      )}
    </div>
  );
};

export default OptimizationPage;
