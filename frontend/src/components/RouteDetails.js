import React from 'react';

const RouteDetails = ({ routes }) => {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
        <thead className="bg-gray-200 text-gray-700">
          <tr>
            <th className="py-3 px-4 text-left">Route ID</th>
            <th className="py-3 px-4 text-left">Distance (km)</th>
            <th className="py-3 px-4 text-left">Traffic Level</th>
            <th className="py-3 px-4 text-left">Base Time (min)</th>
          </tr>
        </thead>
        <tbody className="text-gray-600">
          {routes.map((route) => (
            <tr key={route.id} className="border-b border-gray-200 hover:bg-gray-50">
              <td className="py-3 px-4">{route.route_id}</td>
              <td className="py-3 px-4">{route.distance_km}</td>
              <td className="py-3 px-4">{route.traffic_level}</td>
              <td className="py-3 px-4">{route.base_time_minutes}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default RouteDetails;
