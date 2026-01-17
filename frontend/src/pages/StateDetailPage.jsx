import { useQuery } from '@tanstack/react-query';
import { useParams, Link } from 'react-router-dom';
import apiService from '../services/api';
import { ArrowLeft, Users, Fingerprint, FileText, TrendingUp, AlertCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b'];

export default function StateDetailPage() {
  const { stateName } = useParams();

  const { data, isLoading, error } = useQuery({
    queryKey: ['state', stateName],
    queryFn: () => apiService.getStateDetail(stateName),
  });

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">State Not Found</h2>
        <p className="text-gray-600 mb-6">{error.detail || 'State data could not be loaded'}</p>
        <Link to="/states" className="gov-button-primary">
          Back to States
        </Link>
      </div>
    );
  }

  const state = data;

  // Prepare data for charts
  const ageGroupData = [
    { name: 'Age 0-5', value: state.enrolments.age_0_5, color: COLORS[2] },
    { name: 'Age 5-17', value: state.enrolments.age_5_17, color: COLORS[1] },
    { name: 'Age 18+', value: state.enrolments.age_18_plus, color: COLORS[0] },
  ];

  const updateTypeData = [
    { name: 'Biometric', youth: state.biometric_updates.youth_5_17, adult: state.biometric_updates.adult_17_plus },
    { name: 'Demographic', youth: state.demographic_updates.youth_5_17, adult: state.demographic_updates.adult_17_plus },
  ];

  return (
    <div className="space-y-6">
      {/* Header with Back Button */}
      <div>
        <Link to="/states" className="inline-flex items-center text-gov-blue-600 hover:text-gov-blue-700 mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to States
        </Link>
        <h1 className="text-3xl font-display font-bold text-gray-900">
          {state.state}
        </h1>
        <p className="mt-1 text-sm text-gray-600">
          Detailed analytics and insights
        </p>
      </div>

      {/* Key Indices */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="gov-card bg-gradient-to-br from-blue-50 to-white">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">IVI</h3>
            <TrendingUp className="h-5 w-5 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-blue-900">{state.indices.ivi}</p>
          <p className="text-xs text-gray-500 mt-1">Identity Velocity</p>
          <span className={`stat-badge mt-2 ${getIVIBadgeClass(state.indices.ivi)}`}>
            {getIVIStatus(state.indices.ivi)}
          </span>
        </div>

        <div className="gov-card bg-gradient-to-br from-orange-50 to-white">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">BSI</h3>
            <AlertCircle className="h-5 w-5 text-orange-600" />
          </div>
          <p className="text-3xl font-bold text-orange-900">{state.indices.bsi}</p>
          <p className="text-xs text-gray-500 mt-1">Biometric Stress</p>
          <span className={`stat-badge mt-2 ${getBSIBadgeClass(state.indices.bsi)}`}>
            {getBSIStatus(state.indices.bsi)}
          </span>
        </div>

        <div className="gov-card bg-gradient-to-br from-green-50 to-white">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Youth Ratio</h3>
            <Users className="h-5 w-5 text-green-600" />
          </div>
          <p className="text-3xl font-bold text-green-900">{state.indices.youth_ratio}%</p>
          <p className="text-xs text-gray-500 mt-1">5-17 Age Group</p>
        </div>

        <div className="gov-card bg-gradient-to-br from-purple-50 to-white">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Stability</h3>
            <AlertCircle className="h-5 w-5 text-purple-600" />
          </div>
          <p className="text-3xl font-bold text-purple-900">{state.indices.stability_score}</p>
          <p className="text-xs text-gray-500 mt-1">Out of 100</p>
        </div>
      </div>

      {/* Update Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="gov-card">
          <div className="flex items-center mb-4">
            <Fingerprint className="h-6 w-6 text-blue-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">Biometric Updates</h3>
          </div>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600">Total</p>
              <p className="text-2xl font-bold text-gray-900">
                {state.biometric_updates.total.toLocaleString('en-IN')}
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4 pt-3 border-t">
              <div>
                <p className="text-xs text-gray-500">Youth (5-17)</p>
                <p className="text-lg font-semibold text-gray-900">
                  {state.biometric_updates.youth_5_17.toLocaleString('en-IN')}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Adult (17+)</p>
                <p className="text-lg font-semibold text-gray-900">
                  {state.biometric_updates.adult_17_plus.toLocaleString('en-IN')}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="gov-card">
          <div className="flex items-center mb-4">
            <FileText className="h-6 w-6 text-green-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">Demographic Updates</h3>
          </div>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600">Total</p>
              <p className="text-2xl font-bold text-gray-900">
                {state.demographic_updates.total.toLocaleString('en-IN')}
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4 pt-3 border-t">
              <div>
                <p className="text-xs text-gray-500">Youth (5-17)</p>
                <p className="text-lg font-semibold text-gray-900">
                  {state.demographic_updates.youth_5_17.toLocaleString('en-IN')}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Adult (17+)</p>
                <p className="text-lg font-semibold text-gray-900">
                  {state.demographic_updates.adult_17_plus.toLocaleString('en-IN')}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="gov-card">
          <div className="flex items-center mb-4">
            <Users className="h-6 w-6 text-purple-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">Enrolments</h3>
          </div>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600">Total</p>
              <p className="text-2xl font-bold text-gray-900">
                {state.enrolments.total.toLocaleString('en-IN')}
              </p>
            </div>
            <div className="grid grid-cols-3 gap-2 pt-3 border-t">
              <div>
                <p className="text-xs text-gray-500">0-5</p>
                <p className="text-sm font-semibold text-gray-900">
                  {(state.enrolments.age_0_5 / 1000).toFixed(0)}K
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">5-17</p>
                <p className="text-sm font-semibold text-gray-900">
                  {(state.enrolments.age_5_17 / 1000).toFixed(0)}K
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">18+</p>
                <p className="text-sm font-semibold text-gray-900">
                  {(state.enrolments.age_18_plus / 1000).toFixed(0)}K
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Enrolments by Age Group */}
        <div className="gov-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Enrolments by Age Group
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={ageGroupData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {ageGroupData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Updates by Type and Age */}
        <div className="gov-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Updates by Type & Age Group
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={updateTypeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} stroke="#9ca3af" />
              <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Bar dataKey="youth" fill="#10b981" name="Youth (5-17)" />
              <Bar dataKey="adult" fill="#3b82f6" name="Adult (17+)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="h-12 bg-gray-200 rounded skeleton w-64"></div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="gov-card h-32 skeleton"></div>
        ))}
      </div>
    </div>
  );
}

function getIVIStatus(ivi) {
  if (ivi < 100) return 'Stable';
  if (ivi < 500) return 'Moderate';
  if (ivi < 1000) return 'High';
  return 'Critical';
}

function getIVIBadgeClass(ivi) {
  if (ivi < 100) return 'stat-badge-success';
  if (ivi < 500) return 'stat-badge-info';
  if (ivi < 1000) return 'stat-badge-warning';
  return 'stat-badge-danger';
}

function getBSIStatus(bsi) {
  if (bsi < 0.5) return 'Low';
  if (bsi < 1.5) return 'Moderate';
  if (bsi < 3.0) return 'High';
  return 'Critical';
}

function getBSIBadgeClass(bsi) {
  if (bsi < 0.5) return 'stat-badge-success';
  if (bsi < 1.5) return 'stat-badge-info';
  if (bsi < 3.0) return 'stat-badge-warning';
  return 'stat-badge-danger';
}

