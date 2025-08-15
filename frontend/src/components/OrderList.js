import React from 'react';

const OrderList = ({ orders }) => {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
        <thead className="bg-gray-200 text-gray-700">
          <tr>
            <th className="py-3 px-4 text-left">Order ID</th>
            <th className="py-3 px-4 text-left">Value</th>
            <th className="py-3 px-4 text-left">Route ID</th>
            <th className="py-3 px-4 text-left">Delivery Time</th>
            <th className="py-3 px-4 text-left">Assigned Driver</th>
          </tr>
        </thead>
        <tbody className="text-gray-600">
          {orders.map((order) => (
            <tr key={order.id} className="border-b border-gray-200 hover:bg-gray-50">
              <td className="py-3 px-4">{order.order_id}</td>
              <td className="py-3 px-4">${order.value.toFixed(2)}</td>
              <td className="py-3 px-4">{order.route_id}</td>
              <td className="py-3 px-4">{new Date(order.delivery_time).toLocaleString()}</td>
              <td className="py-3 px-4">{order.assigned_driver_id || 'Unassigned'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default OrderList;
