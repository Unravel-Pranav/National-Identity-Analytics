import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import StatesPage from './pages/StatesPage';
import StateDetailPage from './pages/StateDetailPage';
import ClusteringPage from './pages/ClusteringPage';
import AnomaliesPage from './pages/AnomaliesPage';
import ForecastPage from './pages/ForecastPage';
import HighRiskPage from './pages/HighRiskPage';

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

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/states" element={<StatesPage />} />
            <Route path="/states/:stateName" element={<StateDetailPage />} />
            <Route path="/clustering" element={<ClusteringPage />} />
            <Route path="/anomalies" element={<AnomaliesPage />} />
            <Route path="/forecast" element={<ForecastPage />} />
            <Route path="/high-risk" element={<HighRiskPage />} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
}

export default App;

