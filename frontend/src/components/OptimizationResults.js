import React from 'react';
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

const OptimizationResults = ({ schedule }) => {
  if (!schedule || schedule.length === 0) {
    return <p>No optimized schedule available. Run optimization first.</p>;
  }

  // Process data for workload distribution chart
  const driverWorkload = {};
  schedule.forEach(item => {
    if (item.driver_name) {
      const deliveryTime = new Date(item.estimated_delivery_time);
      const assignedTime = new Date(item.assigned_at);
      const durationMinutes = (deliveryTime - assignedTime) / (1000 * 60);
      driverWorkload[item.driver_name] = (driverWorkload[item.driver_name] || 0) + durationMinutes;
    }
  });

  const chartData = {
    labels: Object.keys(driverWorkload),
    datasets: [
      {
        label: 'Workload (minutes)',
        data: Object.values(driverWorkload),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Driver Workload Distribution',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Minutes',
        },
      },
    },
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-800">Optimized Schedule</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
          <thead className="bg-gray-200 text-gray-700">
            <tr>
              <th className="py-3 px-4 text-left">Order ID</th>
              <th className="py-3 px-4 text-left">Driver Name</th>
              <th className="py-3 px-4 text-left">Estimated Delivery Time</th>
              <th className="py-3 px-4 text-left">Assigned At</th>
            </tr>
          </thead>
          <tbody className="text-gray-600">
            {schedule.map((item, index) => (
              <tr key={index} className="border-b border-gray-200 hover:bg-gray-50">
                <td className="py-3 px-4">{item.order_id}</td>
                <td className="py-3 px-4">{item.driver_name}</td>
                <td className="py-3 px-4">{new Date(item.estimated_delivery_time).toLocaleString()}</td>
                <td className="py-3 px-4">{new Date(item.assigned_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-8 p-4 bg-white shadow-md rounded-lg">
        <Bar data={chartData} options={chartOptions} />
      </div>
    </div>
  );
};

export default OptimizationResults;
