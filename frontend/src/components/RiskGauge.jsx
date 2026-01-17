import { AlertCircle, Activity } from 'lucide-react';

export function RiskGauge({ value, max, type, label }) {
  const percentage = (value / max) * 100;
  
  // Determine risk level and colors
  let riskLevel, color, bgColor, textColor, icon;
  
  if (type === 'ivi') {
    if (value < 100) {
      riskLevel = 'Very Stable';
      color = 'bg-green-500';
      bgColor = 'bg-green-50';
      textColor = 'text-green-800';
      icon = <Activity className="h-4 w-4" />;
    } else if (value < 500) {
      riskLevel = 'Moderate';
      color = 'bg-blue-500';
      bgColor = 'bg-blue-50';
      textColor = 'text-blue-800';
      icon = <Activity className="h-4 w-4" />;
    } else if (value < 1000) {
      riskLevel = 'High Activity';
      color = 'bg-yellow-500';
      bgColor = 'bg-yellow-50';
      textColor = 'text-yellow-800';
      icon = <AlertCircle className="h-4 w-4" />;
    } else {
      riskLevel = 'Critical';
      color = 'bg-red-500';
      bgColor = 'bg-red-50';
      textColor = 'text-red-800';
      icon = <AlertCircle className="h-4 w-4" />;
    }
  } else { // BSI
    if (value < 0.5) {
      riskLevel = 'Low Stress';
      color = 'bg-green-500';
      bgColor = 'bg-green-50';
      textColor = 'text-green-800';
      icon = <Activity className="h-4 w-4" />;
    } else if (value < 1.5) {
      riskLevel = 'Moderate';
      color = 'bg-blue-500';
      bgColor = 'bg-blue-50';
      textColor = 'text-blue-800';
      icon = <Activity className="h-4 w-4" />;
    } else if (value < 3.0) {
      riskLevel = 'High Stress';
      color = 'bg-yellow-500';
      bgColor = 'bg-yellow-50';
      textColor = 'text-yellow-800';
      icon = <AlertCircle className="h-4 w-4" />;
    } else {
      riskLevel = 'Critical';
      color = 'bg-red-500';
      bgColor = 'bg-red-50';
      textColor = 'text-red-800';
      icon = <AlertCircle className="h-4 w-4" />;
    }
  }

  const cappedPercentage = Math.min(percentage, 100);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <div className={`flex items-center space-x-1 px-2 py-1 rounded-full ${bgColor} ${textColor}`}>
          {icon}
          <span className="text-xs font-semibold">{riskLevel}</span>
        </div>
      </div>
      
      <div className="flex items-center space-x-3">
        <div className="flex-1 bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className={`h-full ${color} transition-all duration-500 rounded-full relative`}
            style={{ width: `${cappedPercentage}%` }}
          >
            <div className="absolute inset-0 bg-white opacity-20 animate-pulse"></div>
          </div>
        </div>
        <div className="text-right min-w-[60px]">
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-xs text-gray-500">/{max}</p>
        </div>
      </div>
    </div>
  );
}

