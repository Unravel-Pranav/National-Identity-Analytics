import { useQuery } from '@tanstack/react-query';
import apiService from '../services/api';
import { Shield, MapPin, AlertTriangle } from 'lucide-react';

export default function HighRiskPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['highRisk'],
    queryFn: () => apiService.getHighRiskPincodes(100),
  });

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  const highRiskPincodes = data?.high_risk_pincodes || [];
  const count = data?.count || 0;

  // Group by risk level
  const criticalRisk = highRiskPincodes.filter(p => p.risk_level === 'Critical');
  const highRisk = highRiskPincodes.filter(p => p.risk_level === 'High');
  const mediumRisk = highRiskPincodes.filter(p => p.risk_level === 'Medium');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-display font-bold text-gray-900">
          High Risk Areas
        </h1>
        <p className="mt-1 text-sm text-gray-600">
          Pincodes with high probability of identity updates - priority areas for intervention
        </p>
      </div>

      {/* Risk Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="gov-card bg-gradient-to-br from-gray-50 to-white">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Total Analyzed</h3>
            <MapPin className="h-5 w-5 text-gray-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{count}</p>
        </div>

        <div className="gov-card bg-gradient-to-br from-red-50 to-white border-red-200">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Critical Risk</h3>
            <AlertTriangle className="h-5 w-5 text-red-600" />
          </div>
          <p className="text-3xl font-bold text-red-900">{criticalRisk.length}</p>
        </div>

        <div className="gov-card bg-gradient-to-br from-orange-50 to-white border-orange-200">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">High Risk</h3>
            <AlertTriangle className="h-5 w-5 text-orange-600" />
          </div>
          <p className="text-3xl font-bold text-orange-900">{highRisk.length}</p>
        </div>

        <div className="gov-card bg-gradient-to-br from-yellow-50 to-white border-yellow-200">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Medium Risk</h3>
            <Shield className="h-5 w-5 text-yellow-600" />
          </div>
          <p className="text-3xl font-bold text-yellow-900">{mediumRisk.length}</p>
        </div>
      </div>

      {/* High Risk Table */}
      <div className="gov-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Top 100 High-Risk Pincodes
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
                  Risk Level
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Probability
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  IVI
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  BSI
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Updates
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {highRiskPincodes.map((pincode) => (
                <tr key={pincode.pincode} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {pincode.pincode}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {pincode.state}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {pincode.district}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskBadgeClass(pincode.risk_level)}`}>
                      {pincode.risk_level}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                    {(pincode.update_probability * 100).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {pincode.ivi}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {pincode.bsi}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {pincode.total_updates.toLocaleString('en-IN')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Action Recommendations */}
      <div className="gov-card bg-gradient-to-br from-blue-50 to-white border-blue-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          🎯 Recommended Actions
        </h3>
        <div className="space-y-3 text-sm text-gray-700">
          <div className="flex items-start">
            <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-red-100 text-red-600 text-xs font-bold mr-3 flex-shrink-0">1</span>
            <div>
              <strong>Critical Risk Areas ({criticalRisk.length} pincodes):</strong> Immediate intervention required. Deploy mobile enrollment centers and biometric update camps.
            </div>
          </div>
          <div className="flex items-start">
            <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-orange-100 text-orange-600 text-xs font-bold mr-3 flex-shrink-0">2</span>
            <div>
              <strong>High Risk Areas ({highRisk.length} pincodes):</strong> Schedule regular outreach programs. Increase awareness campaigns.
            </div>
          </div>
          <div className="flex items-start">
            <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-yellow-100 text-yellow-600 text-xs font-bold mr-3 flex-shrink-0">3</span>
            <div>
              <strong>Medium Risk Areas ({mediumRisk.length} pincodes):</strong> Monitor trends. Plan preventive measures.
            </div>
          </div>
          <div className="flex items-start">
            <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-blue-100 text-blue-600 text-xs font-bold mr-3 flex-shrink-0">4</span>
            <div>
              <strong>Resource Allocation:</strong> Use this data to optimize staff deployment and infrastructure planning.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function getRiskBadgeClass(riskLevel) {
  switch (riskLevel) {
    case 'Critical':
      return 'bg-red-100 text-red-800';
    case 'High':
      return 'bg-orange-100 text-orange-800';
    case 'Medium':
      return 'bg-yellow-100 text-yellow-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="h-12 bg-gray-200 rounded skeleton w-64"></div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="gov-card h-24 skeleton"></div>
        ))}
      </div>
      <div className="gov-card h-96 skeleton"></div>
    </div>
  );
}

