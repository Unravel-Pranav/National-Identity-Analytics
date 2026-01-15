import { useQuery } from '@tanstack/react-query';
import apiService from '../services/api';
import { AlertTriangle, MapPin, TrendingUp } from 'lucide-react';

export default function AnomaliesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['anomalies'],
    queryFn: () => apiService.getAnomalies(100),
  });

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  const anomalies = data?.anomalies || [];
  const summary = data?.summary || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-display font-bold text-gray-900">
          Anomaly Detection
        </h1>
        <p className="mt-1 text-sm text-gray-600">
          Machine learning-based detection of unusual patterns in pincode data
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="gov-card bg-gradient-to-br from-red-50 to-white border-red-200">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Total Anomalies</h3>
            <AlertTriangle className="h-5 w-5 text-red-600" />
          </div>
          <p className="text-3xl font-bold text-red-900">
            {summary.total_anomalies?.toLocaleString('en-IN')}
          </p>
        </div>

        <div className="gov-card bg-gradient-to-br from-yellow-50 to-white border-yellow-200">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Anomaly Rate</h3>
            <TrendingUp className="h-5 w-5 text-yellow-600" />
          </div>
          <p className="text-3xl font-bold text-yellow-900">
            {summary.anomaly_percentage}%
          </p>
        </div>

        <div className="gov-card bg-gradient-to-br from-blue-50 to-white border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Total Pincodes</h3>
            <MapPin className="h-5 w-5 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-blue-900">
            {summary.total_pincodes?.toLocaleString('en-IN')}
          </p>
        </div>
      </div>

      {/* Anomalies Table */}
      <div className="gov-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Top 100 Anomalous Pincodes
        </h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Pincode
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  State
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  District
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Anomaly Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  IVI
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  BSI
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Updates
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {anomalies.map((anomaly) => (
                <tr key={anomaly.pincode} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {anomaly.pincode}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {anomaly.state}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {anomaly.district}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      {anomaly.anomaly_score}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {anomaly.ivi}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {anomaly.bsi}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {anomaly.total_updates.toLocaleString('en-IN')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="h-12 bg-gray-200 rounded skeleton w-64"></div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[1, 2, 3].map(i => (
          <div key={i} className="gov-card h-24 skeleton"></div>
        ))}
      </div>
      <div className="gov-card h-96 skeleton"></div>
    </div>
  );
}

