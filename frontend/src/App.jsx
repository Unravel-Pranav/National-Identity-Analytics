import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { lazy, Suspense } from 'react';
import Layout from './components/Layout';

// Lazy load pages
const Dashboard = lazy(() => import('./pages/Dashboard'));
const StatesPage = lazy(() => import('./pages/StatesPage'));
const StateDetailPage = lazy(() => import('./pages/StateDetailPage'));
const ClusteringPage = lazy(() => import('./pages/ClusteringPage'));
const AnomaliesPage = lazy(() => import('./pages/AnomaliesPage'));
const ForecastPage = lazy(() => import('./pages/ForecastPage'));
const HighRiskPage = lazy(() => import('./pages/HighRiskPage'));

// Create a client with optimized settings
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function LoadingFallback() {
  return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Suspense fallback={<LoadingFallback />}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/states" element={<StatesPage />} />
              <Route path="/states/:stateName" element={<StateDetailPage />} />
              <Route path="/clustering" element={<ClusteringPage />} />
              <Route path="/anomalies" element={<AnomaliesPage />} />
              <Route path="/forecast" element={<ForecastPage />} />
              <Route path="/high-risk" element={<HighRiskPage />} />
            </Routes>
          </Suspense>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
}

export default App;

