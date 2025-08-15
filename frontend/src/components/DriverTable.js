import React from 'react';

const DriverTable = ({ drivers }) => {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
        <thead className="bg-gray-200 text-gray-700">
          <tr>
            <th className="py-3 px-4 text-left">Driver ID</th>
            <th className="py-3 px-4 text-left">Name</th>
            <th className="py-3 px-4 text-left">Shift Hours Today</th>
            <th className="py-3 px-4 text-left">Hours Worked Past Week</th>
          </tr>
        </thead>
        <tbody className="text-gray-600">
          {drivers.map((driver) => (
            <tr key={driver.id} className="border-b border-gray-200 hover:bg-gray-50">
              <td className="py-3 px-4">{driver.id}</td>
              <td className="py-3 px-4">{driver.name}</td>
              <td className="py-3 px-4">{driver.shift_hours_today}</td>
              <td className="py-3 px-4">{driver.hours_worked_past_week}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DriverTable;
