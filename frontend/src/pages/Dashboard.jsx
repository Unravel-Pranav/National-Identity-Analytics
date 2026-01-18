import { useState, useEffect } from 'react';
import { useQuery, keepPreviousData } from '@tanstack/react-query';
import apiService from '../services/api';
import { 
  Users, 
  FileText, 
  Fingerprint, 
  MapPin, 
  TrendingUp,
  AlertCircle,
  Activity,
  BarChart3,
  Filter,
  ChevronDown,
  RefreshCw
} from 'lucide-react';
import { 
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer
} from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

export default function Dashboard() {
  const [selectedDate, setSelectedDate] = useState({ year: '', month: '' });

  // Fetch available dates
  const { data: dateData } = useQuery({
    queryKey: ['availableDates'],
    queryFn: apiService.getAvailableDates,
  });

  // Set default to latest available when loaded
  useEffect(() => {
    if (dateData?.latest && !selectedDate.year) {
      setSelectedDate({ 
        year: String(dateData.latest.year), 
        month: String(dateData.latest.month) 
      });
    }
  }, [dateData]);

  // Prepare params for queries - ensure valid numbers
  const queryParams = (selectedDate.year && selectedDate.month) ? { 
    year: parseInt(selectedDate.year), 
    month: parseInt(selectedDate.month) 
  } : {};

  // Fetch data with params
  const { 
    data: summary, 
    isLoading: loadingSummary,
    isFetching: fetchingSummary,
    isError: errorSummary,
    error: summaryErrorDetails
  } = useQuery({
    queryKey: ['summary', queryParams],
    queryFn: () => apiService.getSummary(queryParams),
    enabled: !!dateData,
    placeholderData: keepPreviousData
  });

  const { data: dailyTrends, isLoading: loadingTrends } = useQuery({
    queryKey: ['dailyTrends', queryParams],
    queryFn: () => apiService.getDailyTrends(30, queryParams),
    enabled: !!dateData,
    placeholderData: keepPreviousData
  });

  const { data: states, isLoading: loadingStates } = useQuery({
    queryKey: ['states', queryParams],
    queryFn: () => apiService.getAllStates(queryParams),
    enabled: !!dateData,
    placeholderData: keepPreviousData
  });

  useEffect(() => {
    if (errorSummary) console.error("Summary API Error:", summaryErrorDetails);
    if (summary) console.log("Summary Data:", summary);
    if (dailyTrends) console.log("Daily Trends Data:", dailyTrends);
    if (states) console.log("States Data:", states);
  }, [summary, dailyTrends, states, errorSummary, summaryErrorDetails]);

  if (loadingSummary && !summary) {
    return <LoadingSkeleton />;
  }

  if (errorSummary) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] text-center">
        <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
        <h3 className="text-lg font-semibold text-gray-900">Failed to load dashboard data</h3>
        <p className="text-gray-500 mb-4">
          {summaryErrorDetails?.message || "Please check your connection and try again."}
        </p>
        <button 
          onClick={() => window.location.reload()} 
          className="gov-button-primary"
        >
          Reload Page
        </button>
      </div>
    );
  }

  const metrics = summary?.metrics || {};
  const indices = summary?.indices || {};
  const topPerformers = summary?.top_performers || {};

  // Extract unique years from available dates
  const availableYears = dateData?.dates 
    ? [...new Set(dateData.dates.map(d => d.year))].sort((a, b) => b - a)
    : [];

  // Get months for selected year
  const availableMonths = dateData?.dates
    ? dateData.dates
        .filter(d => d.year === parseInt(selectedDate.year))
        .map(d => d.month)
        .sort((a, b) => b - a)
    : [];

  const handleYearChange = (e) => {
    const newYear = e.target.value;
    const monthsForYear = dateData?.dates
      .filter(d => d.year === parseInt(newYear))
      .map(d => d.month)
      .sort((a, b) => b - a);
    const defaultMonth = monthsForYear && monthsForYear.length > 0 ? String(monthsForYear[0]) : '';
    setSelectedDate({ year: newYear, month: defaultMonth });
  };

  // Prepare top states for chart - Safe access
  const rawStatesList = states?.states || [];
  const topStatesData = Array.isArray(rawStatesList) ? rawStatesList.slice(0, 10).map(s => {
    const safeName = s.name || "Unknown";
    return {
      name: safeName.length > 15 ? safeName.substring(0, 12) + '...' : safeName,
      updates: s.total_updates || 0,
      ivi: s.ivi || 0,
      bsi: s.bsi || 0,
    };
  }) : [];

  // Prepare trend data - Safe access
  const rawTrendsList = dailyTrends?.trends || [];
  const trendData = Array.isArray(rawTrendsList) ? rawTrendsList.map(t => {
    try {
      const d = new Date(t.date);
      return {
        date: isNaN(d.getTime()) ? t.date : d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }),
        bio: t.bio_updates || 0,
        demo: t.demo_updates || 0,
        enrol: t.enrolments || 0,
      };
    } catch (e) {
      return {
        date: t.date,
        bio: t.bio_updates || 0,
        demo: t.demo_updates || 0,
        enrol: t.enrolments || 0,
      };
    }
  }) : [];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header & Filter */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-display font-bold text-gray-900 flex items-center gap-3">
            Executive Dashboard
            {fetchingSummary && (
              <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />
            )}
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Real-time analytics and insights for Aadhaar identity system
          </p>
        </div>

        <div className="flex items-center gap-3 bg-white p-1.5 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex items-center px-3 py-2 bg-gray-50 rounded-lg">
            <Filter className="h-4 w-4 text-gov-blue-600 mr-2" />
            <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Filter</span>
          </div>
          
          <div className="relative">
            <select 
              value={selectedDate.year}
              onChange={handleYearChange}
              className="appearance-none pl-3 pr-8 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent hover:bg-gray-50 transition-colors cursor-pointer"
            >
              {availableYears.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
          </div>

          <div className="relative">
            <select 
              value={selectedDate.month}
              onChange={(e) => setSelectedDate(prev => ({ ...prev, month: e.target.value }))}
              className="appearance-none pl-3 pr-8 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent hover:bg-gray-50 transition-colors cursor-pointer min-w-[120px]"
            >
              {availableMonths.map(month => (
                <option key={month} value={month}>
                  {new Date(2000, month - 1).toLocaleString('default', { month: 'long' })}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
          </div>
        </div>
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
          <p className="text-3xl font-bold text-gray-900">{indices.avg_ivi || 0}</p>
          <p className="text-xs text-gray-500 mt-2">Identity Velocity Index</p>
          <div className="mt-3 flex items-center">
            <span className={`stat-badge ${getIVIBadgeClass(indices.avg_ivi || 0)}`}>
              {getIVIStatus(indices.avg_ivi || 0)}
            </span>
          </div>
        </div>

        <div className="gov-card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Avg BSI</h3>
            <AlertCircle className="h-5 w-5 text-orange-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{indices.avg_bsi || 0}</p>
          <p className="text-xs text-gray-500 mt-2">Biometric Stress Index</p>
          <div className="mt-3 flex items-center">
            <span className={`stat-badge ${getBSIBadgeClass(indices.avg_bsi || 0)}`}>
              {getBSIStatus(indices.avg_bsi || 0)}
            </span>
          </div>
        </div>

        <div className="gov-card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Coverage</h3>
            <BarChart3 className="h-5 w-5 text-green-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{metrics.unique_states || 0}</p>
          <p className="text-xs text-gray-500 mt-2">States/UTs Covered</p>
          <div className="mt-3">
            <div className="text-sm text-gray-600">
              {(metrics.unique_districts || 0).toLocaleString('en-IN')} Districts
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="gov-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Last 30 Days Activity</h3>
          {trendData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#9ca3af" />
                <YAxis tick={{ fontSize: 11 }} stroke="#9ca3af" />
                <Tooltip contentStyle={{ backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '8px' }} />
                <Legend />
                <Area type="monotone" dataKey="bio" stackId="1" stroke="#3b82f6" fill="#3b82f6" name="Biometric" fillOpacity={0.6} />
                <Area type="monotone" dataKey="demo" stackId="1" stroke="#10b981" fill="#10b981" name="Demographic" fillOpacity={0.6} />
                <Area type="monotone" dataKey="enrol" stackId="1" stroke="#f59e0b" fill="#f59e0b" name="Enrolments" fillOpacity={0.6} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-400 bg-gray-50 rounded-lg">
              {loadingTrends ? 'Loading trends...' : 'No activity data available for this period'}
            </div>
          )}
        </div>

        <div className="gov-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top 10 States by Total Updates</h3>
          {topStatesData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topStatesData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis type="number" tick={{ fontSize: 11 }} stroke="#9ca3af" />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} stroke="#9ca3af" width={80} />
                <Tooltip contentStyle={{ backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '8px' }} />
                <Bar dataKey="updates" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-400 bg-gray-50 rounded-lg">
              {loadingStates ? 'Loading states...' : 'No state data available'}
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
              <p className="text-2xl font-bold text-gov-blue-700 mt-1">{topPerformers.top_state || 'N/A'}</p>
              <p className="text-xs text-gray-500 mt-1">Highest total updates</p>
            </div>
            <TrendingUp className="h-12 w-12 text-blue-400" />
          </div>
        </div>

        <div className="gov-card bg-gradient-to-br from-orange-50 to-white border-orange-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">High Stress State</p>
              <p className="text-2xl font-bold text-orange-700 mt-1">{topPerformers.high_stress_state || 'N/A'}</p>
              <p className="text-xs text-gray-500 mt-1">Highest biometric stress</p>
            </div>
            <AlertCircle className="h-12 w-12 text-orange-400" />
          </div>
        </div>
      </div>
    </div>
  );
}

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
        {trend && <span className="text-xs font-medium text-green-600">{trend}</span>}
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
          <div key={i} className="gov-card h-24 bg-gray-200 rounded skeleton"></div>
        ))}
      </div>
    </div>
  );
}

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