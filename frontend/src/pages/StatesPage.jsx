import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import apiService from '../services/api';
import { Search, TrendingUp, AlertCircle, ChevronRight, Grid, List, Filter, AlertTriangle, CheckCircle, Activity } from 'lucide-react';
import { useState, useMemo } from 'react';

export default function StatesPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('updates');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'table'
  const [filterCategory, setFilterCategory] = useState('all'); // 'all', 'critical', 'high', 'stable'
  const [showCount, setShowCount] = useState(12); // Pagination

  const { data, isLoading } = useQuery({
    queryKey: ['states'],
    queryFn: apiService.getAllStates,
  });

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  const states = data?.states || [];

  // Calculate summary statistics (MUTUALLY EXCLUSIVE - same logic as getCardStyle)
  const summary = useMemo(() => {
    // Count each state only once in its primary category
    const critical = states.filter(s => s.ivi >= 1000 || s.bsi >= 3.0);
    const highRisk = states.filter(s => 
      (s.ivi >= 500 || s.bsi >= 1.5) && // Meets high risk criteria
      !(s.ivi >= 1000 || s.bsi >= 3.0)   // But NOT critical
    );
    const stable = states.filter(s => 
      s.ivi < 500 && s.bsi < 1.5 // Below both thresholds
    );
    
    return {
      total: states.length,
      critical: critical.length,
      highRisk: highRisk.length,
      stable: stable.length,
      totalUpdates: states.reduce((sum, s) => sum + s.total_updates, 0),
    };
  }, [states]);

  // Filter and sort (MUTUALLY EXCLUSIVE)
  let filteredStates = states.filter(s => {
    const matchesSearch = s.name.toLowerCase().includes(searchTerm.toLowerCase());
    
    if (filterCategory === 'all') return matchesSearch;
    
    // Critical: IVI >= 1000 OR BSI >= 3.0
    if (filterCategory === 'critical') {
      return matchesSearch && (s.ivi >= 1000 || s.bsi >= 3.0);
    }
    
    // High Risk: Meets high criteria BUT NOT critical
    if (filterCategory === 'high') {
      return matchesSearch && 
             (s.ivi >= 500 || s.bsi >= 1.5) && 
             !(s.ivi >= 1000 || s.bsi >= 3.0);
    }
    
    // Stable: Below both high thresholds
    if (filterCategory === 'stable') {
      return matchesSearch && (s.ivi < 500 && s.bsi < 1.5);
    }
    
    return matchesSearch;
  });

  if (sortBy === 'updates') {
    filteredStates.sort((a, b) => b.total_updates - a.total_updates);
  } else if (sortBy === 'ivi') {
    filteredStates.sort((a, b) => b.ivi - a.ivi);
  } else if (sortBy === 'bsi') {
    filteredStates.sort((a, b) => b.bsi - a.bsi);
  }

  const displayedStates = filteredStates.slice(0, showCount);
  const hasMore = filteredStates.length > showCount;

  // Helper function to get card styling based on state metrics (MUTUALLY EXCLUSIVE)
  const getCardStyle = (state) => {
    // Priority-based classification (only ONE category per state):
    // 1. Critical: IVI >= 1000 OR BSI >= 3.0
    // 2. High Risk: IVI >= 500 OR BSI >= 1.5 (but not Critical)
    // 3. Stable: Everything else
    
    if (state.ivi >= 1000 || state.bsi >= 3.0) {
      return {
        borderColor: 'border-red-500',
        headerBg: 'bg-gradient-to-r from-red-50 to-red-100',
        statusBadge: 'bg-red-500 text-white',
        statusText: '🔴 Critical',
        statusColor: 'red',
      };
    } else if (state.ivi >= 500 || state.bsi >= 1.5) {
      return {
        borderColor: 'border-orange-500',
        headerBg: 'bg-gradient-to-r from-orange-50 to-orange-100',
        statusBadge: 'bg-orange-500 text-white',
        statusText: '🟠 High Risk',
        statusColor: 'orange',
      };
    } else {
      return {
        borderColor: 'border-green-500',
        headerBg: 'bg-gradient-to-r from-green-50 to-green-100',
        statusBadge: 'bg-green-500 text-white',
        statusText: '🟢 Stable',
        statusColor: 'green',
      };
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-display font-bold text-gray-900">
          State-wise Analysis
        </h1>
        <p className="mt-1 text-sm text-gray-600">
          Comprehensive analytics for all {states.length} states and union territories
        </p>
      </div>

      {/* Professional Summary Bar */}
      <div className="gov-card bg-gradient-to-r from-gray-50 to-white">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 items-center">
          {/* Critical */}
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-red-100 flex items-center justify-center">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
            </div>
            <div>
              <div className="text-xs font-medium text-gray-600 uppercase tracking-wide">Critical</div>
              <div className="text-2xl font-bold text-red-600">{summary.critical}</div>
            </div>
          </div>

          {/* High Risk */}
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center">
              <div className="w-3 h-3 rounded-full bg-orange-500"></div>
            </div>
            <div>
              <div className="text-xs font-medium text-gray-600 uppercase tracking-wide">High Risk</div>
              <div className="text-2xl font-bold text-orange-600">{summary.highRisk}</div>
            </div>
          </div>

          {/* Stable */}
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
            </div>
            <div>
              <div className="text-xs font-medium text-gray-600 uppercase tracking-wide">Stable</div>
              <div className="text-2xl font-bold text-green-600">{summary.stable}</div>
            </div>
          </div>

          {/* Total Updates */}
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
              <Activity className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <div className="text-xs font-medium text-gray-600 uppercase tracking-wide">Total Updates</div>
              <div className="text-2xl font-bold text-blue-600">{(summary.totalUpdates / 1000000).toFixed(1)}M</div>
            </div>
          </div>
        </div>
      </div>

      {/* Professional Controls Bar */}
      <div className="gov-card">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-center">
          {/* Search - Takes more space */}
          <div className="lg:col-span-5">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search states by name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-gov-blue-500 focus:border-gov-blue-500 transition-all"
              />
            </div>
          </div>

          {/* Filter */}
          <div className="lg:col-span-3">
            <div className="relative">
              <Filter className="absolute left-4 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-500 pointer-events-none" />
              <select
                value={filterCategory}
                onChange={(e) => { setFilterCategory(e.target.value); setShowCount(12); }}
                className="w-full appearance-none pl-11 pr-10 py-3 border-2 border-gray-200 rounded-xl font-medium text-gray-700 focus:ring-2 focus:ring-gov-blue-500 focus:border-gov-blue-500 bg-white cursor-pointer transition-all hover:border-gray-300"
              >
                <option value="all">All States ({states.length})</option>
                <option value="critical">🔴 Critical ({summary.critical})</option>
                <option value="high">🟠 High Risk ({summary.highRisk})</option>
                <option value="stable">🟢 Stable ({summary.stable})</option>
              </select>
              <div className="absolute right-4 top-1/2 transform -translate-y-1/2 pointer-events-none">
                <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </div>
            </div>
          </div>

          {/* Sort */}
          <div className="lg:col-span-3">
            <div className="relative">
              <TrendingUp className="absolute left-4 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-500 pointer-events-none" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full appearance-none pl-11 pr-10 py-3 border-2 border-gray-200 rounded-xl font-medium text-gray-700 focus:ring-2 focus:ring-gov-blue-500 focus:border-gov-blue-500 bg-white cursor-pointer transition-all hover:border-gray-300"
              >
                <option value="updates">Sort by Updates</option>
                <option value="ivi">Sort by IVI</option>
                <option value="bsi">Sort by BSI</option>
              </select>
              <div className="absolute right-4 top-1/2 transform -translate-y-1/2 pointer-events-none">
                <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </div>
            </div>
          </div>

          {/* View Toggle */}
          <div className="lg:col-span-1 flex justify-end lg:pl-4">
            <div className="inline-flex items-center gap-1 bg-gray-100 rounded-xl p-1 shadow-inner">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2.5 rounded-lg transition-all ${
                  viewMode === 'grid' 
                    ? 'bg-white shadow-sm text-gov-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
                title="Grid View"
              >
                <Grid className="h-5 w-5" />
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`p-2.5 rounded-lg transition-all ${
                  viewMode === 'table' 
                    ? 'bg-white shadow-sm text-gov-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
                title="Table View"
              >
                <List className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
        
        {/* Results counter with styling */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">
              Showing <span className="font-bold text-gray-900">{displayedStates.length}</span> of <span className="font-bold text-gray-900">{filteredStates.length}</span> states
            </span>
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="text-gov-blue-600 hover:text-gov-blue-700 font-medium"
              >
                Clear search
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Grid View - Premium Design */}
      {viewMode === 'grid' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {displayedStates.map((state) => {
            const cardStyle = getCardStyle(state);
            return (
              <Link
                key={state.name}
                to={`/states/${encodeURIComponent(state.name)}`}
                className={`bg-white rounded-2xl shadow-md border-t-4 ${cardStyle.borderColor} hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 group overflow-hidden`}
              >
                {/* Colored Header */}
                <div className={`${cardStyle.headerBg} px-5 py-4 border-b border-opacity-20`}>
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-bold text-gray-900 group-hover:text-gov-blue-700 transition-colors truncate">
                        {state.name}
                      </h3>
                      <p className="text-xs text-gray-600 mt-0.5 font-medium">
                        {state.total_updates.toLocaleString('en-IN')} updates
                      </p>
                    </div>
                  </div>
                </div>

                {/* Card Content */}
                <div className="p-5">
                  {/* Metrics with Better Layout - IVI wider than BSI */}
                  <div className="flex gap-3 mb-5">
                    {/* IVI Metric - Wider (60%) */}
                    <div className="flex-[3] bg-blue-50 rounded-xl p-4 border border-blue-100">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="h-4 w-4 text-blue-600" />
                        <span className="text-xs font-semibold text-blue-700 uppercase tracking-wide">IVI</span>
                      </div>
                      <p className="text-xl font-bold text-gray-900">{state.ivi}</p>
                    </div>

                    {/* BSI Metric - Narrower (40%) */}
                    <div className="flex-[2] bg-orange-50 rounded-xl p-4 border border-orange-100">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertCircle className="h-4 w-4 text-orange-600" />
                        <span className="text-xs font-semibold text-orange-700 uppercase tracking-wide">BSI</span>
                      </div>
                      <p className="text-xl font-bold text-gray-900">{state.bsi}</p>
                    </div>
                  </div>

                  {/* View Details Button */}
                  <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                    <span className="text-xs text-gray-500 font-medium">Click for details</span>
                    <div className="flex items-center text-gov-blue-600 group-hover:text-gov-blue-700 font-semibold text-sm">
                      View
                      <ChevronRight className="h-4 w-4 ml-1 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}

      {/* Table View */}
      {viewMode === 'table' && (
        <div className="gov-card overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  State / UT
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Updates
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  IVI
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  BSI
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {displayedStates.map((state) => {
                const cardStyle = getCardStyle(state);
                return (
                  <tr key={state.name} className={`hover:bg-gray-50 border-l-4 ${cardStyle.borderColor}`}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <div className="font-semibold text-gray-900">{state.name}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="text-sm font-semibold text-gray-900">
                        {state.total_updates.toLocaleString('en-IN')}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <div className="text-sm font-bold text-gray-900">
                        {state.ivi}
                      </div>
                      <div className="text-xs text-gray-500">{getIVIStatus(state.ivi)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <div className="text-sm font-bold text-gray-900">
                        {state.bsi}
                      </div>
                      <div className="text-xs text-gray-500">{getBSIStatus(state.bsi)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center justify-center">
                        <span className={`${cardStyle.statusBadge} px-3 py-1 rounded-full text-xs font-bold`}>
                          {cardStyle.statusText}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <Link
                        to={`/states/${encodeURIComponent(state.name)}`}
                        className="text-gov-blue-600 hover:text-gov-blue-800 font-medium text-sm inline-flex items-center"
                      >
                        View Details
                        <ChevronRight className="h-4 w-4 ml-1" />
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Load More Button */}
      {hasMore && (
        <div className="text-center">
          <button
            onClick={() => setShowCount(prev => prev + 12)}
            className="gov-button-primary"
          >
            Load More States ({filteredStates.length - showCount} remaining)
          </button>
        </div>
      )}

      {/* No Results */}
      {filteredStates.length === 0 && (
        <div className="gov-card text-center py-12">
          <AlertCircle className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-lg font-medium text-gray-900 mb-2">No states found</p>
          <p className="text-gray-500">No states match your search "{searchTerm}"</p>
          <button
            onClick={() => { setSearchTerm(''); setFilterCategory('all'); }}
            className="mt-4 gov-button-secondary"
          >
            Clear Filters
          </button>
        </div>
      )}
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div>
        <div className="h-10 bg-gray-200 rounded skeleton w-80 mb-2"></div>
        <div className="h-4 bg-gray-200 rounded skeleton w-96"></div>
      </div>

      {/* Summary bar skeleton */}
      <div className="gov-card h-16 skeleton"></div>

      {/* Search bar skeleton */}
      <div className="gov-card h-24 skeleton"></div>

      {/* Cards grid skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
          <div key={i} className="bg-white rounded-lg border-t-4 border-gray-200 shadow-sm">
            <div className="bg-gray-100 h-14 rounded-t-lg skeleton"></div>
            <div className="p-4 space-y-3">
              <div className="h-4 bg-gray-200 rounded skeleton w-3/4"></div>
              <div className="grid grid-cols-2 gap-4">
                <div className="h-16 bg-gray-200 rounded skeleton"></div>
                <div className="h-16 bg-gray-200 rounded skeleton"></div>
              </div>
              <div className="h-6 bg-gray-200 rounded skeleton w-1/2"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Helper functions for colored circles (visual indicators)
function getIVICircleColor(ivi) {
  if (ivi >= 1000) return 'bg-red-500';
  if (ivi >= 500) return 'bg-orange-500';
  return 'bg-green-500';
}

function getBSICircleColor(bsi) {
  if (bsi >= 3.0) return 'bg-red-500';
  if (bsi >= 1.5) return 'bg-orange-500';
  return 'bg-green-500';
}

// Keep these for table view
function getIVIStatus(ivi) {
  if (ivi >= 1000) return 'Critical';
  if (ivi >= 500) return 'High';
  return 'Stable';
}

function getIVIBadgeClass(ivi) {
  if (ivi >= 1000) return 'stat-badge-danger';
  if (ivi >= 500) return 'stat-badge-warning';
  return 'stat-badge-success';
}

function getBSIStatus(bsi) {
  if (bsi >= 3.0) return 'Critical';
  if (bsi >= 1.5) return 'High';
  return 'Moderate';
}

function getBSIBadgeClass(bsi) {
  if (bsi >= 3.0) return 'stat-badge-danger';
  if (bsi >= 1.5) return 'stat-badge-warning';
  return 'stat-badge-success';
}

