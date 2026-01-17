import { useQuery } from '@tanstack/react-query';
import { useState, useMemo } from 'react';
import apiService from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine, Area, AreaChart } from 'recharts';
import { TrendingUp, Calendar, ArrowUp, ArrowDown, Activity, AlertCircle, BarChart3, Info, Fingerprint, FileText, UserPlus } from 'lucide-react';

export default function ForecastPage() {
  const [metric, setMetric] = useState('bio');
  const [days, setDays] = useState(30);

  const { data, isLoading } = useQuery({
    queryKey: ['forecast', metric, days],
    queryFn: () => apiService.getForecast(metric, days),
  });

  const metricNames = {
    bio: 'Biometric Updates',
    demo: 'Demographic Updates',
    enrol: 'New Enrolments',
  };

  // Transform and combine historical and forecast data
  const chartData = useMemo(() => {
    if (!data) return [];
    
    // Transform historical data (ds, y) -> (date, value)
    const historical = (data.historical || []).map(d => {
      const date = new Date(typeof d.ds === 'string' ? d.ds : (d.date || ''));
      return {
        date: d.ds || d.date,
        displayDate: formatDateForChart(date),
        value: d.y || d.value || 0,
        type: 'historical'
      };
    });
    
    // Transform forecast data
    const forecast = (data.forecast || []).map(d => {
      const date = new Date(typeof d.ds === 'string' ? d.ds : (d.date || ''));
      return {
        date: d.ds || d.date,
        displayDate: formatDateForChart(date),
        forecast: d.yhat || d.forecast || 0,
        lower_bound: d.yhat_lower || d.lower_bound || 0,
        upper_bound: d.yhat_upper || d.upper_bound || 0,
        type: 'forecast'
      };
    });
    
    return [...historical, ...forecast];
  }, [data]);

  // Calculate insights
  const insights = useMemo(() => {
    if (!data || !chartData.length) return null;

    const historicalData = chartData.filter(d => d.type === 'historical' && d.value);
    const forecastData = chartData.filter(d => d.type === 'forecast' && d.forecast);

    if (!historicalData.length || !forecastData.length) return null;

    const lastHistorical = historicalData[historicalData.length - 1].value;
    const avgForecast = forecastData.reduce((sum, d) => sum + d.forecast, 0) / forecastData.length;
    const maxForecast = Math.max(...forecastData.map(d => d.forecast));
    const minForecast = Math.min(...forecastData.map(d => d.forecast));
    
    const trend = avgForecast - lastHistorical;
    const trendPercent = (trend / lastHistorical) * 100;
    
    const lastForecast = forecastData[forecastData.length - 1];
    const confidenceRange = lastForecast.upper_bound - lastForecast.lower_bound;
    const confidencePercent = (confidenceRange / lastForecast.forecast) * 100;

    return {
      lastHistorical,
      avgForecast,
      maxForecast,
      minForecast,
      trend,
      trendPercent,
      confidencePercent,
      isIncreasing: trend > 0
    };
  }, [chartData, data]);

  // Get split point between historical and forecast
  const splitDate = useMemo(() => {
    const forecastStart = chartData.find(d => d.type === 'forecast');
    return forecastStart ? forecastStart.displayDate : null;
  }, [chartData]);

  return (
    <div className="space-y-6">
      {/* Header with Explanation */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-600 rounded-xl p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-white rounded-xl shadow-sm">
            <BarChart3 className="h-7 w-7 text-blue-600" />
          </div>
          <div className="flex-1">
            <h1 className="text-3xl font-display font-bold text-gray-900 mb-2">
              Demand Forecasting
            </h1>
            <p className="text-sm text-gray-700 leading-relaxed">
              Predict future Aadhaar service demand using AI. The <span className="font-semibold text-blue-700">blue line</span> shows past actual data, 
              the <span className="font-semibold text-green-700">green line</span> shows AI predictions, 
              and <span className="font-semibold text-orange-700">orange bands</span> show the expected range (confidence interval).
            </p>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="gov-card">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-3">
              <BarChart3 className="h-4 w-4 text-gov-blue-600" />
              What to Forecast
            </label>
            <select
              value={metric}
              onChange={(e) => setMetric(e.target.value)}
              className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 text-base font-medium focus:ring-2 focus:ring-gov-blue-500 focus:border-gov-blue-500 transition-all"
            >
              <option value="bio">Biometric Updates (Fingerprint/Iris)</option>
              <option value="demo">Demographic Updates (Address/Name)</option>
              <option value="enrol">New Enrolments</option>
            </select>
          </div>

          <div>
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-3">
              <Calendar className="h-4 w-4 text-gov-blue-600" />
              How Far Ahead
            </label>
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 text-base font-medium focus:ring-2 focus:ring-gov-blue-500 focus:border-gov-blue-500 transition-all"
            >
              <option value="7">1 Week (7 days)</option>
              <option value="14">2 Weeks (14 days)</option>
              <option value="30">1 Month (30 days)</option>
              <option value="60">2 Months (60 days)</option>
              <option value="90">3 Months (90 days)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Insights Cards */}
      {insights && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
          {/* Current Trend */}
          <div className="gov-card bg-gradient-to-br from-blue-50 to-blue-100 border-l-4 border-blue-500">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-blue-700 uppercase tracking-wider">Last Recorded</span>
              <Activity className="h-5 w-5 text-blue-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900 mb-1">
              {formatNumber(insights.lastHistorical)}
            </p>
            <p className="text-xs text-gray-600">Actual {metricNames[metric].toLowerCase()}</p>
          </div>

          {/* Forecast Trend */}
          <div className={`gov-card bg-gradient-to-br ${insights.isIncreasing ? 'from-green-50 to-green-100 border-l-4 border-green-500' : 'from-orange-50 to-orange-100 border-l-4 border-orange-500'}`}>
            <div className="flex items-center justify-between mb-3">
              <span className={`text-xs font-bold uppercase tracking-wider ${insights.isIncreasing ? 'text-green-700' : 'text-orange-700'}`}>
                Expected Trend
              </span>
              {insights.isIncreasing ? <ArrowUp className="h-5 w-5 text-green-600" /> : <ArrowDown className="h-5 w-5 text-orange-600" />}
            </div>
            <p className={`text-3xl font-bold mb-1 ${insights.isIncreasing ? 'text-green-900' : 'text-orange-900'}`}>
              {insights.trendPercent > 0 ? '+' : ''}{insights.trendPercent.toFixed(1)}%
            </p>
            <p className="text-xs text-gray-600">
              {insights.isIncreasing ? 'Increasing' : 'Decreasing'} demand forecast
            </p>
          </div>

          {/* Average Forecast */}
          <div className="gov-card bg-gradient-to-br from-purple-50 to-purple-100 border-l-4 border-purple-500">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-purple-700 uppercase tracking-wider">Avg Forecast</span>
              <TrendingUp className="h-5 w-5 text-purple-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900 mb-1">
              {formatNumber(insights.avgForecast)}
            </p>
            <p className="text-xs text-gray-600">Expected daily average</p>
          </div>

          {/* Confidence */}
          <div className="gov-card bg-gradient-to-br from-indigo-50 to-indigo-100 border-l-4 border-indigo-500">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-indigo-700 uppercase tracking-wider">Confidence</span>
              <AlertCircle className="h-5 w-5 text-indigo-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900 mb-1">
              {(100 - insights.confidencePercent).toFixed(0)}%
            </p>
            <p className="text-xs text-gray-600">Prediction accuracy</p>
          </div>
        </div>
      )}

      {/* Forecast Chart with Better UX */}
      <div className="gov-card">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h3 className="flex items-center gap-2 text-xl font-bold text-gray-900 mb-1">
              <TrendingUp className="h-5 w-5 text-gov-blue-600" />
              Visual Forecast
            </h3>
            <p className="text-sm text-gray-600">
              Past performance vs. AI-predicted future demand
            </p>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-8 h-1 bg-blue-500"></div>
              <span className="font-medium text-gray-700">Past (Actual)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-1 bg-green-500 border-t-2 border-dashed"></div>
              <span className="font-medium text-gray-700">Future (Predicted)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-1 bg-orange-400 border-t-2 border-dashed"></div>
              <span className="font-medium text-gray-700">Range</span>
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="h-[500px] flex items-center justify-center text-gray-400">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gov-blue-600 mx-auto mb-4"></div>
              <p className="text-lg font-medium text-gray-700">Loading forecast data...</p>
              <p className="text-sm text-gray-500 mt-2">Analyzing {metricNames[metric].toLowerCase()}...</p>
            </div>
          </div>
        ) : chartData.length === 0 ? (
          <div className="h-[500px] flex items-center justify-center text-gray-500">
            <div className="text-center">
              <TrendingUp className="h-16 w-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium">No forecast data available</p>
              <p className="text-sm text-gray-400 mt-2">Try selecting a different metric or period</p>
            </div>
          </div>
        ) : (
          <div>
            <ResponsiveContainer width="100%" height={500}>
              <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.01}/>
                  </linearGradient>
                  <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.01}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="displayDate" 
                  tick={{ fontSize: 11, fill: '#6b7280' }}
                  stroke="#9ca3af"
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis 
                  tick={{ fontSize: 12, fill: '#6b7280' }}
                  stroke="#9ca3af"
                  tickFormatter={formatNumber}
                  label={{ 
                    value: metricNames[metric], 
                    angle: -90, 
                    position: 'insideLeft',
                    style: { fontSize: 13, fontWeight: 600, fill: '#374151' }
                  }}
                />
                <Tooltip content={<CustomTooltip metricName={metricNames[metric]} />} />
                
                {/* Vertical line separating historical from forecast */}
                {splitDate && (
                  <ReferenceLine 
                    x={splitDate} 
                    stroke="#6b7280" 
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    label={{ 
                      value: '← Past | Future →', 
                      position: 'top',
                      fill: '#374151',
                      fontSize: 12,
                      fontWeight: 600
                    }}
                  />
                )}

                {/* Confidence interval area */}
                <Area
                  type="monotone"
                  dataKey="upper_bound"
                  stroke="none"
                  fill="#fed7aa"
                  fillOpacity={0.3}
                />
                <Area
                  type="monotone"
                  dataKey="lower_bound"
                  stroke="none"
                  fill="#ffffff"
                  fillOpacity={1}
                />
                
                {/* Historical line with area */}
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#3b82f6"
                  strokeWidth={3}
                  fill="url(#colorValue)"
                  dot={false}
                  name="Past (Actual)"
                />
                
                {/* Forecast line with area */}
                <Area
                  type="monotone"
                  dataKey="forecast"
                  stroke="#10b981"
                  strokeWidth={3}
                  strokeDasharray="8 4"
                  fill="url(#colorForecast)"
                  dot={false}
                  name="Future (Predicted)"
                />
                
                {/* Bound lines */}
                <Line 
                  type="monotone" 
                  dataKey="lower_bound" 
                  stroke="#f59e0b" 
                  strokeWidth={1.5}
                  strokeDasharray="3 3"
                  dot={false}
                  name="Min Expected"
                />
                <Line 
                  type="monotone" 
                  dataKey="upper_bound" 
                  stroke="#f59e0b" 
                  strokeWidth={1.5}
                  strokeDasharray="3 3"
                  dot={false}
                  name="Max Expected"
                />
              </AreaChart>
            </ResponsiveContainer>

            {/* Chart Explanation */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <div className="w-4 h-1 bg-blue-600 rounded"></div>
                </div>
                <div>
                  <p className="text-sm font-bold text-gray-900">Past (Blue Solid)</p>
                  <p className="text-xs text-gray-600 mt-1">Historical actual data showing what already happened</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center flex-shrink-0">
                  <div className="w-4 h-1 bg-green-600 rounded border-t-2 border-dashed border-green-600"></div>
                </div>
                <div>
                  <p className="text-sm font-bold text-gray-900">Future (Green Dashed)</p>
                  <p className="text-xs text-gray-600 mt-1">AI prediction of expected {metricNames[metric].toLowerCase()}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-orange-100 flex items-center justify-center flex-shrink-0">
                  <div className="w-4 h-1 bg-orange-400 rounded border-t-2 border-dashed border-orange-400"></div>
                </div>
                <div>
                  <p className="text-sm font-bold text-gray-900">Range (Orange Band)</p>
                  <p className="text-xs text-gray-600 mt-1">Best/worst case scenarios (80% confidence)</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* What This Means Section */}
      {insights && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Actionable Insights */}
          <div className="gov-card bg-gradient-to-br from-blue-50 to-white">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Info className="h-5 w-5 text-blue-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">What This Means</h3>
            </div>
            <ul className="space-y-3 text-sm">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold mt-0.5">•</span>
                <span className="text-gray-700">
                  <strong>Currently:</strong> Recording {formatNumber(insights.lastHistorical)} {metricNames[metric].toLowerCase()} per day
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold mt-0.5">•</span>
                <span className="text-gray-700">
                  <strong>Forecast:</strong> Expecting average of {formatNumber(insights.avgForecast)} per day over next {days} days
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-orange-600 font-bold mt-0.5">•</span>
                <span className="text-gray-700">
                  <strong>Range:</strong> Between {formatNumber(insights.minForecast)} (minimum) and {formatNumber(insights.maxForecast)} (maximum)
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className={`${insights.isIncreasing ? 'text-green-600' : 'text-red-600'} font-bold mt-0.5`}>•</span>
                <span className="text-gray-700">
                  <strong>Trend:</strong> Demand is {insights.isIncreasing ? 'increasing' : 'decreasing'} by {Math.abs(insights.trendPercent).toFixed(1)}%
                </span>
              </li>
            </ul>
          </div>

          {/* Recommendations */}
          <div className="gov-card bg-gradient-to-br from-indigo-50 to-white">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <TrendingUp className="h-5 w-5 text-indigo-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">Action Items</h3>
            </div>
            <ul className="space-y-3 text-sm text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-indigo-600 font-bold mt-0.5">1.</span>
                <span>
                  <strong>Staffing:</strong> Plan for {insights.isIncreasing ? 'more' : 'fewer'} staff to handle {insights.isIncreasing ? 'increased' : 'decreased'} demand
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-indigo-600 font-bold mt-0.5">2.</span>
                <span>
                  <strong>Resources:</strong> Prepare for peak demand of {formatNumber(insights.maxForecast)} per day
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-indigo-600 font-bold mt-0.5">3.</span>
                <span>
                  <strong>Capacity:</strong> Ensure enrollment centers can handle {Math.round(insights.avgForecast * 1.2).toLocaleString()} per day (with buffer)
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-indigo-600 font-bold mt-0.5">4.</span>
                <span>
                  <strong>Monitor:</strong> Track actual vs. predicted to adjust plans if needed
                </span>
              </li>
            </ul>
          </div>
        </div>
      )}

      {/* Technical Details */}
      {data && (
        <div className="bg-gray-50 border border-gray-200 rounded-xl p-5">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-white rounded-lg shadow-sm">
              <BarChart3 className="h-5 w-5 text-gray-600" />
            </div>
            <div className="flex-1">
              <h4 className="text-sm font-bold text-gray-900 mb-2">Forecast Algorithm</h4>
              <p className="text-sm text-gray-600 leading-relaxed">
                Using <strong className="text-gray-900">{data.method === 'prophet' ? 'Facebook Prophet' : 'Moving Average'}</strong> machine learning model 
                to analyze {chartData.filter(d => d.type === 'historical').length} days of historical data and predict {days} days ahead. 
                The model considers weekly patterns and trends to generate accurate forecasts with 80% confidence intervals.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper function to format dates for chart display
function formatDateForChart(date) {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return `${months[date.getMonth()]} ${date.getDate()}`;
}

// Helper function to format numbers
function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return Math.round(num).toLocaleString();
}

// Custom tooltip
function CustomTooltip({ active, payload, metricName }) {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const isHistorical = data.type === 'historical';
    
    return (
      <div className="bg-white p-4 border-2 border-gray-200 rounded-xl shadow-xl">
        <p className="font-bold text-gray-900 mb-2">{data.displayDate}</p>
        <div className="space-y-1.5">
          {isHistorical ? (
            <div className="flex items-center justify-between gap-4">
              <span className="text-sm text-gray-600 flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                Actual:
              </span>
              <span className="text-sm font-bold text-gray-900">
                {formatNumber(data.value)} {metricName.toLowerCase()}
              </span>
            </div>
          ) : (
            <>
              <div className="flex items-center justify-between gap-4">
                <span className="text-sm text-gray-600 flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  Predicted:
                </span>
                <span className="text-sm font-bold text-green-900">
                  {formatNumber(data.forecast)} {metricName.toLowerCase()}
                </span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span className="text-xs text-gray-500 pl-5">Max:</span>
                <span className="text-xs font-semibold text-orange-700">
                  {formatNumber(data.upper_bound)}
                </span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span className="text-xs text-gray-500 pl-5">Min:</span>
                <span className="text-xs font-semibold text-orange-700">
                  {formatNumber(data.lower_bound)}
                </span>
              </div>
            </>
          )}
        </div>
      </div>
    );
  }
  return null;
}
