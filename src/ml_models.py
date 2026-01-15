"""
Machine Learning Models Module
Implements anomaly detection, clustering, and forecasting for Aadhaar data.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy import stats


class AnomalyDetector:
    """Detect anomalies in Aadhaar update patterns."""
    
    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self._is_fitted = False
    
    def fit_predict(self, df: pd.DataFrame, features: List[str]) -> pd.DataFrame:
        """Fit model and predict anomalies."""
        df = df.copy()
        X = df[features].fillna(0)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit and predict (-1 for anomaly, 1 for normal)
        predictions = self.model.fit_predict(X_scaled)
        scores = self.model.decision_function(X_scaled)
        
        df['is_anomaly'] = predictions == -1
        df['anomaly_score'] = -scores  # Higher = more anomalous
        
        self._is_fitted = True
        return df
    
    def detect_pincode_anomalies(self, pincode_df: pd.DataFrame) -> pd.DataFrame:
        """Detect anomalous pincodes based on update patterns."""
        features = [
            'total_bio_updates', 'total_demo_updates', 'total_enrolments',
            'identity_velocity_index', 'biometric_stress_index'
        ]
        return self.fit_predict(pincode_df, features)
    
    def detect_temporal_anomalies(self, daily_df: pd.DataFrame) -> pd.DataFrame:
        """Detect temporal anomalies in daily data."""
        df = daily_df.copy()
        
        # Calculate Z-scores for each metric
        for col in ['total_bio_updates', 'total_demo_updates', 'total_enrolments']:
            if col in df.columns:
                z_scores = np.abs(stats.zscore(df[col].fillna(0)))
                df[f'{col}_zscore'] = z_scores
                df[f'{col}_anomaly'] = z_scores > 2.5  # Flag if > 2.5 std
        
        # Overall anomaly flag
        anomaly_cols = [c for c in df.columns if c.endswith('_anomaly')]
        if anomaly_cols:
            df['is_anomaly'] = df[anomaly_cols].any(axis=1)
        
        return df
    
    def get_anomaly_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary of detected anomalies."""
        if 'is_anomaly' not in df.columns:
            return {'error': 'No anomaly detection performed'}
        
        anomalies = df[df['is_anomaly']]
        return {
            'total_records': len(df),
            'anomaly_count': len(anomalies),
            'anomaly_percentage': len(anomalies) / len(df) * 100,
            'top_anomalies': anomalies.nlargest(10, 'anomaly_score').to_dict('records') if 'anomaly_score' in df.columns else []
        }


class StateClustering:
    """Cluster states based on identity behavior patterns."""
    
    def __init__(self, n_clusters: int = 4):
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2)
        self._is_fitted = False
    
    def fit_predict(self, state_df: pd.DataFrame) -> pd.DataFrame:
        """Cluster states based on identity metrics."""
        df = state_df.copy()
        
        # Features for clustering
        features = ['IVI', 'BSI', 'youth_ratio', 'total_updates', 'total_enrolments']
        available_features = [f for f in features if f in df.columns]
        
        X = df[available_features].fillna(0)
        X_scaled = self.scaler.fit_transform(X)
        
        # Cluster
        df['cluster'] = self.model.fit_predict(X_scaled)
        
        # PCA for visualization
        if X_scaled.shape[1] >= 2:
            pca_result = self.pca.fit_transform(X_scaled)
            df['pca_x'] = pca_result[:, 0]
            df['pca_y'] = pca_result[:, 1]
        
        # Add cluster labels
        cluster_labels = self._generate_cluster_labels(df, available_features)
        df['cluster_label'] = df['cluster'].map(cluster_labels)
        
        self._is_fitted = True
        return df
    
    def _generate_cluster_labels(self, df: pd.DataFrame, features: List[str]) -> Dict[int, str]:
        """Generate descriptive labels for each cluster."""
        labels = {}
        
        for cluster_id in df['cluster'].unique():
            cluster_data = df[df['cluster'] == cluster_id]
            
            # Analyze cluster characteristics
            avg_ivi = cluster_data['IVI'].mean() if 'IVI' in df.columns else 0
            avg_bsi = cluster_data['BSI'].mean() if 'BSI' in df.columns else 0
            
            if avg_ivi > df['IVI'].median() and avg_bsi > df['BSI'].median():
                labels[cluster_id] = "High Stress - High Volatility"
            elif avg_ivi > df['IVI'].median():
                labels[cluster_id] = "High Volatility"
            elif avg_bsi > df['BSI'].median():
                labels[cluster_id] = "High Biometric Stress"
            else:
                labels[cluster_id] = "Stable"
        
        return labels
    
    def get_cluster_profiles(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get detailed profiles for each cluster."""
        if 'cluster' not in df.columns:
            return {'error': 'Clustering not performed'}
        
        profiles = {}
        for cluster_id in df['cluster'].unique():
            cluster_data = df[df['cluster'] == cluster_id]
            profiles[f"Cluster {cluster_id}"] = {
                'label': cluster_data['cluster_label'].iloc[0] if 'cluster_label' in df.columns else f"Cluster {cluster_id}",
                'states': cluster_data['state'].tolist(),
                'count': len(cluster_data),
                'avg_IVI': float(cluster_data['IVI'].mean()) if 'IVI' in df.columns else 0,
                'avg_BSI': float(cluster_data['BSI'].mean()) if 'BSI' in df.columns else 0,
                'total_updates': int(cluster_data['total_updates'].sum()) if 'total_updates' in df.columns else 0
            }
        
        return profiles


class DemandForecaster:
    """Forecast future Aadhaar service demand."""
    
    def __init__(self, forecast_days: int = 30):
        self.forecast_days = forecast_days
        self._prophet_available = False
        self._check_prophet()
    
    def _check_prophet(self) -> None:
        """Check if Prophet is available."""
        try:
            from prophet import Prophet
            self._prophet_available = True
        except ImportError:
            self._prophet_available = False
    
    def forecast_with_prophet(self, daily_df: pd.DataFrame, 
                               target_col: str = 'total_bio_updates') -> Dict[str, Any]:
        """Forecast using Prophet (if available)."""
        if not self._prophet_available:
            return self._simple_forecast(daily_df, target_col)
        
        from prophet import Prophet
        
        # Prepare data for Prophet
        df_prophet = daily_df[['date', target_col]].copy()
        df_prophet.columns = ['ds', 'y']
        df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])
        
        # Fit model
        model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=False
        )
        model.fit(df_prophet)
        
        # Make future dataframe
        future = model.make_future_dataframe(periods=self.forecast_days)
        forecast = model.predict(future)
        
        # Convert dates to strings for JSON serialization
        forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(self.forecast_days).copy()
        forecast_data['ds'] = forecast_data['ds'].dt.strftime('%Y-%m-%d')
        
        historical_data = df_prophet.copy()
        historical_data['ds'] = historical_data['ds'].dt.strftime('%Y-%m-%d')
        
        return {
            'method': 'prophet',
            'forecast': forecast_data.to_dict('records'),
            'historical': historical_data.to_dict('records')
        }
    
    def _simple_forecast(self, daily_df: pd.DataFrame, 
                         target_col: str = 'total_bio_updates') -> Dict[str, Any]:
        """Simple moving average forecast as fallback."""
        df = daily_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Calculate 7-day moving average
        ma_7 = df[target_col].rolling(window=7).mean().iloc[-1]
        
        # Generate forecast
        last_date = df['date'].max()
        forecast_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1), 
            periods=self.forecast_days
        )
        
        # Add some trend based on recent growth
        recent_growth = df[target_col].pct_change().tail(7).mean()
        forecasts = []
        current_value = ma_7
        
        for date in forecast_dates:
            current_value *= (1 + recent_growth * 0.5)  # Dampened growth
            forecasts.append({
                'ds': date.strftime('%Y-%m-%d'),
                'yhat': current_value,
                'yhat_lower': current_value * 0.8,
                'yhat_upper': current_value * 1.2
            })
        
        # Convert dates to strings for JSON serialization
        historical_data = df[['date', target_col]].copy()
        historical_data['date'] = pd.to_datetime(historical_data['date']).dt.strftime('%Y-%m-%d')
        
        return {
            'method': 'moving_average',
            'forecast': forecasts,
            'historical': historical_data.rename(columns={'date': 'ds', target_col: 'y'}).to_dict('records')
        }
    
    def forecast_all_metrics(self, daily_df: pd.DataFrame) -> Dict[str, Any]:
        """Forecast all metrics."""
        results = {}
        
        for metric in ['total_bio_updates', 'total_demo_updates', 'total_enrolments']:
            if metric in daily_df.columns:
                results[metric] = self.forecast_with_prophet(daily_df, metric)
        
        return results


class IdentityLifecyclePredictor:
    """Predict identity lifecycle events at pincode level."""
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def calculate_update_probability(self, pincode_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate probability of needing updates for each pincode."""
        df = pincode_df.copy()
        
        # Features that indicate high update probability
        if 'identity_velocity_index' in df.columns:
            # Normalize IVI to 0-1 range
            ivi_normalized = (df['identity_velocity_index'] - df['identity_velocity_index'].min()) / \
                           (df['identity_velocity_index'].max() - df['identity_velocity_index'].min() + 1e-6)
        else:
            ivi_normalized = 0.5
        
        if 'biometric_stress_index' in df.columns:
            bsi_normalized = (df['biometric_stress_index'] - df['biometric_stress_index'].min()) / \
                           (df['biometric_stress_index'].max() - df['biometric_stress_index'].min() + 1e-6)
        else:
            bsi_normalized = 0.5
        
        if 'youth_update_ratio' in df.columns:
            youth_normalized = df['youth_update_ratio']
        else:
            youth_normalized = 0.5
        
        # Composite probability score (weighted average)
        df['update_probability'] = (
            0.4 * ivi_normalized + 
            0.4 * bsi_normalized + 
            0.2 * youth_normalized
        )
        
        # Classify risk levels
        df['risk_level'] = pd.cut(
            df['update_probability'],
            bins=[0, 0.25, 0.5, 0.75, 1.0],
            labels=['Low', 'Medium', 'High', 'Critical']
        )
        
        return df
    
    def get_high_priority_pincodes(self, df: pd.DataFrame, top_n: int = 100) -> pd.DataFrame:
        """Get pincodes that need immediate attention."""
        if 'update_probability' not in df.columns:
            df = self.calculate_update_probability(df)
        
        return df.nlargest(top_n, 'update_probability')[[
            'pincode', 'state', 'district', 'total_updates', 
            'identity_velocity_index', 'biometric_stress_index',
            'update_probability', 'risk_level'
        ]]

