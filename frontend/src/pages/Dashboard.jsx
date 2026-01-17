import { useQuery } from '@tanstack/react-query';
import apiService from '../services/api';
import { 
  Users, 
  FileText, 
  Fingerprint, 
  MapPin, 
  TrendingUp,
  AlertCircle,
  Activity,
  BarChart3
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

export default function Dashboard() {
  // Fetch data
  const { data: summary, isLoading: loadingSummary } = useQuery({
    queryKey: ['summary'],
    queryFn: apiService.getSummary,
  });

  const { data: dailyTrends, isLoading: loadingTrends } = useQuery({
    queryKey: ['dailyTrends'],
    queryFn: () => apiService.getDailyTrends(30),
  });

  const { data: states } = useQuery({
    queryKey: ['states'],
    queryFn: apiService.getAllStates,
  });

  if (loadingSummary) {
    return <LoadingSkeleton />;
  }

  const metrics = summary?.metrics || {};
  const indices = summary?.indices || {};
  const topPerformers = summary?.top_performers || {};

  // Prepare top states for chart
  const topStatesData = states?.states?.slice(0, 10).map(s => ({
    name: s.name.length > 15 ? s.name.substring(0, 12) + '...' : s.name,
    updates: s.total_updates,
    ivi: s.ivi,
    bsi: s.bsi,
  })) || [];

  // Prepare trend data
  const trendData = dailyTrends?.trends?.map(t => ({
    date: new Date(t.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }),
    bio: t.bio_updates,
    demo: t.demo_updates,
    enrol: t.enrolments,
  })) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-display font-bold text-gray-900">
          Executive Dashboard
        </h1>
        <p className="mt-1 text-sm text-gray-600">
          Real-time analytics and insights for Aadhaar identity system
        </p>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Biometric Updates"
          value={metrics.total_bio_updates?.toLocaleString('en-IN')}
          icon={Fingerprint}
          color="blue"
          trend="+12.5%"
        />
        <MetricCard
          title="Demographic Updates"
          value={metrics.total_demo_updates?.toLocaleString('en-IN')}
          icon={FileText}
          color="green"
          trend="+8.3%"
        />
        <MetricCard
          title="Total Enrolments"
          value={metrics.total_enrolments?.toLocaleString('en-IN')}
          icon={Users}
          color="purple"
          trend="+5.2%"
        />
        <MetricCard
          title="Active Pincodes"
          value={metrics.unique_pincodes?.toLocaleString('en-IN')}
          icon={MapPin}
          color="orange"
        />
      </div>

      {/* Indices Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="gov-card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Avg IVI</h3>
            <Activity className="h-5 w-5 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{indices.avg_ivi}</p>
          <p className="text-xs text-gray-500 mt-2">Identity Velocity Index</p>
          <div className="mt-3 flex items-center">
            <span className={`stat-badge ${getIVIBadgeClass(indices.avg_ivi)}`}>
              {getIVIStatus(indices.avg_ivi)}
            </span>
          </div>
        </div>

        <div className="gov-card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Avg BSI</h3>
            <AlertCircle className="h-5 w-5 text-orange-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{indices.avg_bsi}</p>
          <p className="text-xs text-gray-500 mt-2">Biometric Stress Index</p>
          <div className="mt-3 flex items-center">
            <span className={`stat-badge ${getBSIBadgeClass(indices.avg_bsi)}`}>
              {getBSIStatus(indices.avg_bsi)}
            </span>
          </div>
        </div>

        <div className="gov-card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Coverage</h3>
            <BarChart3 className="h-5 w-5 text-green-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{metrics.unique_states}</p>
          <p className="text-xs text-gray-500 mt-2">States/UTs Covered</p>
          <div className="mt-3">
            <div className="text-sm text-gray-600">
              {metrics.unique_districts?.toLocaleString('en-IN')} Districts
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Trends */}
        <div className="gov-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Last 30 Days Activity
          </h3>
          {!loadingTrends && trendData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 11 }}
                  stroke="#9ca3af"
                />
                <YAxis tick={{ fontSize: 11 }} stroke="#9ca3af" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="bio" 
                  stackId="1"
                  stroke="#3b82f6" 
                  fill="#3b82f6" 
                  name="Biometric"
                  fillOpacity={0.6}
                />
                <Area 
                  type="monotone" 
                  dataKey="demo" 
                  stackId="1"
                  stroke="#10b981" 
                  fill="#10b981" 
                  name="Demographic"
                  fillOpacity={0.6}
                />
                <Area 
                  type="monotone" 
                  dataKey="enrol" 
                  stackId="1"
                  stroke="#f59e0b" 
                  fill="#f59e0b" 
                  name="Enrolments"
                  fillOpacity={0.6}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-400">
              Loading trends...
            </div>
          )}
        </div>

        {/* Top States by Updates */}
        <div className="gov-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Top 10 States by Total Updates
          </h3>
          {topStatesData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topStatesData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis type="number" tick={{ fontSize: 11 }} stroke="#9ca3af" />
                <YAxis 
                  type="category" 
                  dataKey="name" 
                  tick={{ fontSize: 11 }}
                  stroke="#9ca3af"
                  width={80}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px'
                  }}
                />
                <Bar dataKey="updates" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-400">
              Loading states...
            </div>
          )}
        </div>
      </div>

      {/* Top Performers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="gov-card bg-gradient-to-br from-blue-50 to-white border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Most Active State</p>
              <p className="text-2xl font-bold text-gov-blue-700 mt-1">
                {topPerformers.top_state || 'N/A'}
              </p>
              <p className="text-xs text-gray-500 mt-1">Highest total updates</p>
            </div>
            <TrendingUp className="h-12 w-12 text-blue-400" />
          </div>
        </div>

        <div className="gov-card bg-gradient-to-br from-orange-50 to-white border-orange-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">High Stress State</p>
              <p className="text-2xl font-bold text-orange-700 mt-1">
                {topPerformers.high_stress_state || 'N/A'}
              </p>
              <p className="text-xs text-gray-500 mt-1">Highest biometric stress</p>
            </div>
            <AlertCircle className="h-12 w-12 text-orange-400" />
          </div>
        </div>
      </div>
    </div>
  );
}

// Helper Components
function MetricCard({ title, value, icon: Icon, color, trend }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
  };

  return (
    <div className="metric-card">
      <div className="flex items-center justify-between mb-3">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
        {trend && (
          <span className="text-xs font-medium text-green-600">{trend}</span>
        )}
      </div>
      <h3 className="text-sm font-medium text-gray-600">{title}</h3>
      <p className="text-2xl font-bold text-gray-900 mt-2">{value || '0'}</p>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="h-12 bg-gray-200 rounded skeleton w-64"></div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="gov-card">
            <div className="h-24 bg-gray-200 rounded skeleton"></div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Helper functions
function getIVIStatus(ivi) {
  if (ivi < 100) return 'Very Stable';
  if (ivi < 500) return 'Moderate';
  if (ivi < 1000) return 'High Activity';
  return 'Critical';
}

function getIVIBadgeClass(ivi) {
  if (ivi < 100) return 'stat-badge-success';
  if (ivi < 500) return 'stat-badge-info';
  if (ivi < 1000) return 'stat-badge-warning';
  return 'stat-badge-danger';
}

function getBSIStatus(bsi) {
  if (bsi < 0.5) return 'Low Stress';
  if (bsi < 1.5) return 'Moderate';
  if (bsi < 3.0) return 'High Stress';
  return 'Critical';
}

function getBSIBadgeClass(bsi) {
  if (bsi < 0.5) return 'stat-badge-success';
  if (bsi < 1.5) return 'stat-badge-info';
  if (bsi < 3.0) return 'stat-badge-warning';
  return 'stat-badge-danger';
}

