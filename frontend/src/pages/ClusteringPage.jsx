import { useQuery } from '@tanstack/react-query';
import apiService from '../services/api';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Cell, BarChart, Bar, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';
import { Layers, TrendingUp, AlertCircle, Users, Activity, BarChart3, Target, Info, ChevronRight, Zap, Shield } from 'lucide-react';

const CLUSTER_CONFIGS = {
  0: { 
    color: '#3b82f6', 
    bgLight: 'bg-blue-50',
    borderColor: 'border-blue-500',
    textColor: 'text-blue-700',
    icon: Zap,
    gradient: 'from-blue-500 to-blue-600'
  },
  1: { 
    color: '#10b981', 
    bgLight: 'bg-green-50',
    borderColor: 'border-green-500',
    textColor: 'text-green-700',
    icon: Shield,
    gradient: 'from-green-500 to-green-600'
  },
  2: { 
    color: '#f59e0b', 
    bgLight: 'bg-orange-50',
    borderColor: 'border-orange-500',
    textColor: 'text-orange-700',
    icon: Activity,
    gradient: 'from-orange-500 to-orange-600'
  },
  3: { 
    color: '#ef4444', 
    bgLight: 'bg-red-50',
    borderColor: 'border-red-500',
    textColor: 'text-red-700',
    icon: AlertCircle,
    gradient: 'from-red-500 to-red-600'
  },
};

export default function ClusteringPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['clustering'],
    queryFn: apiService.getClustering,
  });

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  const clusters = data?.clusters || [];
  const profiles = data?.profiles || [];
  
  // Calculate global statistics
  const totalStates = clusters.length;
  const totalUpdates = clusters.reduce((sum, s) => sum + s.total_updates, 0);
  const avgIVI = clusters.reduce((sum, s) => sum + s.ivi, 0) / totalStates;
  const avgBSI = clusters.reduce((sum, s) => sum + s.bsi, 0) / totalStates;

  return (
    <div className="space-y-8">
      {/* Premium Header Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-gov-blue-600 to-gov-blue-700 opacity-5"></div>
        <div className="relative">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-3 bg-gov-blue-100 rounded-xl">
                  <Layers className="h-7 w-7 text-gov-blue-600" />
                </div>
                <div>
                  <h1 className="text-3xl font-display font-bold text-gray-900">
                    State Clustering Analysis
                  </h1>
                  <p className="mt-1 text-sm text-gray-600">
                    AI-Powered State Segmentation Based on Identity Update Patterns
                  </p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 rounded-xl border border-blue-200">
              <BarChart3 className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-semibold text-blue-700">K-Means + PCA</span>
            </div>
          </div>
        </div>
      </div>

      {/* Executive Summary Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="gov-card bg-gradient-to-br from-blue-50 to-blue-100 border-l-4 border-blue-500">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2.5 bg-white rounded-lg shadow-sm">
              <Users className="h-5 w-5 text-blue-600" />
            </div>
            <span className="text-xs font-semibold text-blue-700 uppercase tracking-wider">Total States</span>
          </div>
          <div className="text-3xl font-bold text-gray-900">{totalStates}</div>
          <div className="text-xs text-gray-600 mt-1">Across {profiles.length} distinct clusters</div>
        </div>

        <div className="gov-card bg-gradient-to-br from-purple-50 to-purple-100 border-l-4 border-purple-500">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2.5 bg-white rounded-lg shadow-sm">
              <Activity className="h-5 w-5 text-purple-600" />
            </div>
            <span className="text-xs font-semibold text-purple-700 uppercase tracking-wider">Total Updates</span>
          </div>
          <div className="text-3xl font-bold text-gray-900">{(totalUpdates / 1000000).toFixed(1)}M</div>
          <div className="text-xs text-gray-600 mt-1">Combined identity changes</div>
        </div>

        <div className="gov-card bg-gradient-to-br from-indigo-50 to-indigo-100 border-l-4 border-indigo-500">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2.5 bg-white rounded-lg shadow-sm">
              <TrendingUp className="h-5 w-5 text-indigo-600" />
            </div>
            <span className="text-xs font-semibold text-indigo-700 uppercase tracking-wider">Avg IVI</span>
          </div>
          <div className="text-3xl font-bold text-gray-900">{avgIVI.toFixed(2)}</div>
          <div className="text-xs text-gray-600 mt-1">Identity velocity index</div>
        </div>

        <div className="gov-card bg-gradient-to-br from-orange-50 to-orange-100 border-l-4 border-orange-500">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2.5 bg-white rounded-lg shadow-sm">
              <AlertCircle className="h-5 w-5 text-orange-600" />
            </div>
            <span className="text-xs font-semibold text-orange-700 uppercase tracking-wider">Avg BSI</span>
          </div>
          <div className="text-3xl font-bold text-gray-900">{avgBSI.toFixed(2)}</div>
          <div className="text-xs text-gray-600 mt-1">Biometric stress index</div>
        </div>
      </div>

      {/* Premium Cluster Profile Cards */}
      <div>
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-xl font-bold text-gray-900">Cluster Profiles</h2>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Info className="h-4 w-4" />
            <span>Hover for detailed insights</span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {profiles.map((profile) => {
            const config = CLUSTER_CONFIGS[profile.id];
            const Icon = config.icon;
            const percentage = ((profile.count / totalStates) * 100).toFixed(1);
            const totalClusterUpdates = clusters
              .filter(c => c.cluster === profile.id)
              .reduce((sum, s) => sum + s.total_updates, 0);
            
            return (
              <div 
                key={profile.id} 
                className="bg-white rounded-2xl shadow-lg border-t-4 hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 overflow-hidden group"
                style={{ borderTopColor: config.color }}
              >
                {/* Gradient Header */}
                <div className={`bg-gradient-to-r ${config.gradient} px-5 py-4`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 bg-white bg-opacity-20 backdrop-blur-sm rounded-xl">
                        <Icon className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-white">{profile.label}</h3>
                        <p className="text-xs text-white text-opacity-90">{profile.count} states • {percentage}%</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Card Content */}
                <div className="p-5">
                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between text-xs mb-1.5">
                      <span className="font-semibold text-gray-700">State Distribution</span>
                      <span className="font-bold" style={{ color: config.color }}>{percentage}%</span>
                    </div>
                    <div className="h-2.5 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full rounded-full transition-all duration-500"
                        style={{ 
                          width: `${percentage}%`,
                          backgroundColor: config.color
                        }}
                      />
                    </div>
                  </div>

                  {/* Key Metrics Grid */}
                  <div className="grid grid-cols-2 gap-3 mb-4">
                    {/* IVI Metric */}
                    <div className={`${config.bgLight} rounded-xl p-3 border ${config.borderColor} border-opacity-30`}>
                      <div className="flex items-center gap-1.5 mb-1">
                        <TrendingUp className="h-3.5 w-3.5" style={{ color: config.color }} />
                        <span className="text-xs font-semibold text-gray-600">IVI</span>
                      </div>
                      <p className="text-xl font-bold text-gray-900">{profile.avg_ivi}</p>
                      <p className={`text-xs mt-0.5 ${config.textColor} font-medium`}>
                        {profile.avg_ivi >= 1000 ? 'Critical' : profile.avg_ivi >= 500 ? 'High' : 'Moderate'}
                      </p>
                    </div>

                    {/* BSI Metric */}
                    <div className={`${config.bgLight} rounded-xl p-3 border ${config.borderColor} border-opacity-30`}>
                      <div className="flex items-center gap-1.5 mb-1">
                        <AlertCircle className="h-3.5 w-3.5" style={{ color: config.color }} />
                        <span className="text-xs font-semibold text-gray-600">BSI</span>
                      </div>
                      <p className="text-xl font-bold text-gray-900">{profile.avg_bsi}</p>
                      <p className={`text-xs mt-0.5 ${config.textColor} font-medium`}>
                        {profile.avg_bsi >= 3.0 ? 'Critical' : profile.avg_bsi >= 1.5 ? 'High' : 'Normal'}
                      </p>
                    </div>
                  </div>

                  {/* Total Updates */}
                  <div className="bg-gray-50 rounded-xl p-3 mb-4 border border-gray-200">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-gray-600">Total Updates</span>
                      <Activity className="h-3.5 w-3.5 text-gray-500" />
                    </div>
                    <p className="text-lg font-bold text-gray-900 mt-1">
                      {(totalClusterUpdates / 1000000).toFixed(2)}M
                    </p>
                  </div>

                  {/* Example States */}
                  <div className="border-t border-gray-200 pt-4">
                    <p className="text-xs font-bold text-gray-700 mb-2 uppercase tracking-wide">Member States</p>
                    <div className="flex flex-wrap gap-2">
                      {profile.states.slice(0, 4).map((state, idx) => (
                        <span 
                          key={idx} 
                          className="text-xs font-medium px-2.5 py-1.5 rounded-lg border"
                          style={{ 
                            backgroundColor: config.color + '15',
                            borderColor: config.color + '40',
                            color: config.color
                          }}
                        >
                          {state}
                        </span>
                      ))}
                      {profile.states.length > 4 && (
                        <span className="text-xs font-medium text-gray-500 px-2.5 py-1.5">
                          +{profile.states.length - 4} more
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Cluster Insight */}
                  <div className={`mt-4 ${config.bgLight} rounded-xl p-3 border ${config.borderColor} border-opacity-20`}>
                    <div className="flex items-start gap-2">
                      <Target className="h-4 w-4 mt-0.5 flex-shrink-0" style={{ color: config.color }} />
                      <p className="text-xs text-gray-700 leading-relaxed">
                        {getClusterInsight(profile.label, profile.avg_ivi, profile.avg_bsi)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Advanced Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cluster Comparison Chart */}
        <div className="gov-card">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-gov-blue-600" />
            Cluster Metrics Comparison
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={profiles}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="label" tick={{ fontSize: 11 }} stroke="#9ca3af" />
              <YAxis tick={{ fontSize: 11 }} stroke="#9ca3af" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '12px'
                }}
              />
              <Legend />
              <Bar dataKey="avg_ivi" name="Avg IVI" fill="#3b82f6" radius={[8, 8, 0, 0]} />
              <Bar dataKey="avg_bsi" name="Avg BSI" fill="#f59e0b" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Cluster Size Distribution */}
        <div className="gov-card">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Users className="h-5 w-5 text-gov-blue-600" />
            State Distribution by Cluster
          </h3>
          <div className="space-y-4 pt-2">
            {profiles.map((profile) => {
              const config = CLUSTER_CONFIGS[profile.id];
              const percentage = ((profile.count / totalStates) * 100).toFixed(1);
              return (
                <div key={profile.id}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: config.color }}
                      />
                      <span className="text-sm font-semibold text-gray-900">{profile.label}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-bold text-gray-900">{profile.count} states</span>
                      <span className="text-sm font-bold" style={{ color: config.color }}>
                        {percentage}%
                      </span>
                    </div>
                  </div>
                  <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full rounded-full transition-all duration-500"
                      style={{ 
                        width: `${percentage}%`,
                        backgroundColor: config.color
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* PCA Scatter Plot - Enhanced */}
      <div className="gov-card">
        <div className="mb-5">
          <h3 className="text-lg font-bold text-gray-900 mb-1 flex items-center gap-2">
            <Target className="h-5 w-5 text-gov-blue-600" />
            State Similarity Map (PCA Visualization)
          </h3>
          <p className="text-sm text-gray-600">
            States positioned closer together share similar identity update patterns • Click and drag to explore
          </p>
        </div>
        <ResponsiveContainer width="100%" height={550}>
          <ScatterChart margin={{ top: 20, right: 30, bottom: 40, left: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              type="number" 
              dataKey="pca_x" 
              name="Component 1"
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
              label={{ 
                value: 'Principal Component 1 (Identity Velocity)', 
                position: 'insideBottom', 
                offset: -15,
                style: { fontSize: 12, fontWeight: 600, fill: '#374151' }
              }}
            />
            <YAxis 
              type="number" 
              dataKey="pca_y" 
              name="Component 2"
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
              label={{ 
                value: 'Principal Component 2 (Biometric Stress)', 
                angle: -90, 
                position: 'insideLeft',
                style: { fontSize: 12, fontWeight: 600, fill: '#374151' }
              }}
            />
            <Tooltip 
              cursor={{ strokeDasharray: '3 3' }}
              content={<EnhancedTooltip />}
            />
            <Legend 
              wrapperStyle={{ paddingTop: '20px' }}
              iconType="circle"
            />
            {profiles.map((profile) => {
              const clusterData = clusters.filter(c => c.cluster === profile.id);
              return (
                <Scatter 
                  key={profile.id}
                  name={`${profile.label} (${profile.count})`}
                  data={clusterData}
                  fill={CLUSTER_CONFIGS[profile.id].color}
                  shape="circle"
                />
              );
            })}
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed State Listing */}
      <div className="gov-card">
        <h3 className="text-lg font-bold text-gray-900 mb-5 flex items-center gap-2">
          <Layers className="h-5 w-5 text-gov-blue-600" />
          Complete State Classification
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {profiles.map((profile) => {
            const config = CLUSTER_CONFIGS[profile.id];
            const clusterStates = clusters.filter(c => c.cluster === profile.id);
            
            return (
              <div key={profile.id} className={`${config.bgLight} rounded-xl p-4 border ${config.borderColor} border-opacity-30`}>
                <div className="flex items-center gap-2 mb-4 pb-3 border-b" style={{ borderColor: config.color + '30' }}>
                  <div 
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: config.color }}
                  />
                  <h4 className="font-bold text-sm text-gray-900">{profile.label}</h4>
                  <span className={`ml-auto text-xs font-bold px-2 py-1 rounded-full ${config.bgLight}`} style={{ color: config.color }}>
                    {profile.count}
                  </span>
                </div>
                <div className="space-y-2 max-h-96 overflow-y-auto custom-scrollbar">
                  {clusterStates
                    .sort((a, b) => b.total_updates - a.total_updates)
                    .map((state) => (
                      <div 
                        key={state.state} 
                        className="bg-white rounded-lg p-2.5 text-sm hover:shadow-md transition-shadow cursor-pointer border border-gray-200"
                      >
                        <div className="font-semibold text-gray-900">{state.state}</div>
                        <div className="flex items-center justify-between mt-1 text-xs text-gray-600">
                          <span>IVI: <strong>{state.ivi}</strong></span>
                          <span>BSI: <strong>{state.bsi}</strong></span>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Methodology Note */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-white rounded-xl shadow-sm">
            <Info className="h-6 w-6 text-blue-600" />
          </div>
          <div className="flex-1">
            <h4 className="text-lg font-bold text-gray-900 mb-2">Analysis Methodology</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-700">
              <div>
                <span className="font-semibold text-blue-700">K-Means Clustering:</span> Groups states with similar IVI and BSI patterns into distinct segments.
              </div>
              <div>
                <span className="font-semibold text-indigo-700">PCA Dimensionality Reduction:</span> Visualizes multi-dimensional state characteristics in 2D space.
              </div>
              <div>
                <span className="font-semibold text-purple-700">Silhouette Analysis:</span> Validates cluster quality and separation for optimal grouping.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function getClusterInsight(label, ivi, bsi) {
  if (label.includes('High Stress')) {
    return 'States facing significant biometric authentication challenges. Requires infrastructure upgrades and field support enhancement.';
  } else if (label.includes('Stable')) {
    if (ivi < 500) {
      return 'Low update activity with stable identity patterns. Ideal for maintaining current service standards.';
    } else {
      return 'Moderate update activity with balanced metrics. Monitor for emerging patterns and maintain quality.';
    }
  } else {
    return 'Requires detailed analysis to determine optimal intervention strategies.';
  }
}

function EnhancedTooltip({ active, payload }) {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const config = CLUSTER_CONFIGS[data.cluster];
    
    return (
      <div className="bg-white p-4 border-2 rounded-xl shadow-xl" style={{ borderColor: config.color }}>
        <div className="flex items-center gap-2 mb-3 pb-2 border-b" style={{ borderColor: config.color + '30' }}>
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: config.color }} />
          <p className="font-bold text-gray-900">{data.state}</p>
        </div>
        <div className={`text-xs font-semibold mb-3 px-2 py-1 rounded ${config.bgLight}`} style={{ color: config.color }}>
          {data.cluster_label}
        </div>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between gap-4">
            <span className="text-gray-600">Total Updates:</span>
            <span className="font-bold text-gray-900">{data.total_updates.toLocaleString('en-IN')}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-gray-600">IVI:</span>
            <span className="font-bold" style={{ color: config.color }}>{data.ivi}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-gray-600">BSI:</span>
            <span className="font-bold" style={{ color: config.color }}>{data.bsi}</span>
          </div>
        </div>
      </div>
    );
  }
  return null;
}

function LoadingSkeleton() {
  return (
    <div className="space-y-8">
      <div className="h-20 bg-gray-200 rounded-xl skeleton"></div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="h-32 bg-gray-200 rounded-xl skeleton"></div>
        ))}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="h-96 bg-gray-200 rounded-2xl skeleton"></div>
        ))}
      </div>
      <div className="h-96 bg-gray-200 rounded-xl skeleton"></div>
    </div>
  );
}
