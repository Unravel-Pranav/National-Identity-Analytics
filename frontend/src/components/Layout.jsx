import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Map, 
  AlertTriangle, 
  TrendingUp, 
  Layers,
  Shield,
  Menu,
  X,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { useState } from 'react';
import AIAssistant from './AIAssistant';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'States Analysis', href: '/states', icon: Map },
  { name: 'State Clustering', href: '/clustering', icon: Layers },
  { name: 'Anomaly Detection', href: '/anomalies', icon: AlertTriangle },
  { name: 'Demand Forecast', href: '/forecast', icon: TrendingUp },
  { name: 'High Risk Areas', href: '/high-risk', icon: Shield },
];

export default function Layout({ children }) {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true); // Desktop sidebar expanded by default
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false); // Mobile overlay
  const [sidebarHover, setSidebarHover] = useState(false); // Hover state for edge trigger
  
  // Handle navigation click - close sidebar on desktop for full-screen view
  const handleNavClick = () => {
    setSidebarOpen(false); // Auto-close sidebar on desktop
    setMobileSidebarOpen(false); // Close mobile sidebar
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Government Header */}
      <header className="bg-white border-b-4 border-gov-orange-500 shadow-sm sticky top-0 z-50">
        <div className="mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo & Title */}
            <div className="flex items-center">
              {/* Mobile Hamburger */}
              <button
                onClick={() => setMobileSidebarOpen(!mobileSidebarOpen)}
                className="lg:hidden p-2 rounded-md text-gray-600 hover:bg-gray-100 transition-colors"
                aria-label="Toggle mobile menu"
              >
                {mobileSidebarOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
              
              <div className="flex items-center ml-4 lg:ml-0">
                <div className="flex items-center space-x-2">
                  <div className="w-12 h-12 bg-gradient-to-br from-gov-orange-500 via-white to-gov-green-500 rounded-lg flex items-center justify-center shadow-md">
                    <span className="text-gov-navy-500 font-bold text-xl">आ</span>
                  </div>
                  <div>
                    <h1 className="text-xl font-display font-bold text-gov-navy-500">
                      Aadhaar Intelligence Platform
                    </h1>
                    <p className="text-xs text-gray-600">Government of India</p>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Right side info */}
            <div className="hidden md:flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">Ministry of Electronics & IT</p>
                <p className="text-xs text-gray-600">Unique Identification Authority</p>
              </div>
              <img 
                src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/64px-Emblem_of_India.svg.png"
                alt="Emblem of India"
                className="h-12 w-12"
              />
            </div>
          </div>
        </div>
      </header>

      <div className="flex relative">
        {/* Desktop Sidebar */}
        <aside className={`
          hidden lg:block
          fixed inset-y-0 left-0 z-40
          ${sidebarOpen ? 'w-80' : 'w-0'}
          bg-white border-r border-gray-200 shadow-lg
          transition-all duration-300 ease-in-out
          mt-16
          overflow-hidden
        `}>
          <nav className="h-full overflow-y-auto py-6 px-4">
            {/* Menu Button - Inside Sidebar */}
            <div className="mb-6 pb-4 border-b-2 border-gray-200">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="flex items-center gap-3 w-full px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-xl transition-all duration-200 group"
                aria-label="Toggle sidebar"
              >
                <div className="flex items-center justify-center w-9 h-9 bg-gov-blue-50 rounded-lg group-hover:bg-gov-blue-100 transition-colors">
                  <ChevronLeft className="h-5 w-5 text-gov-blue-600" />
                </div>
                <div className="flex-1 text-left">
                  <p className="text-sm font-bold text-gray-900 uppercase tracking-wide">MENU</p>
                  <p className="text-xs text-gray-500">Click to hide menu</p>
                </div>
              </button>
            </div>

            {/* Navigation Items */}
            <div className="space-y-1">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                const Icon = item.icon;
                
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={handleNavClick}
                    className={`
                      flex items-center px-4 py-3.5 text-sm font-medium rounded-xl
                      transition-all duration-200
                      ${isActive
                        ? 'bg-gov-blue-50 text-gov-blue-700 border-l-4 border-gov-blue-600 shadow-sm'
                        : 'text-gray-700 hover:bg-gray-50 hover:text-gov-blue-600'
                      }
                      group
                    `}
                  >
                    <Icon className="mr-3 h-5 w-5 flex-shrink-0" />
                    <span className="transition-opacity duration-200">
                      {item.name}
                    </span>
                  </Link>
                );
              })}
            </div>
            
            {/* Version info */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <div className="px-4 space-y-2">
                <p className="text-xs text-gray-500">Platform Version</p>
                <p className="text-sm font-semibold text-gov-navy-500">v2.0.0</p>
                <p className="text-xs text-gray-500 mt-2">Powered by AI & ML</p>
              </div>
            </div>
          </nav>
        </aside>

        {/* Edge Trigger - Shows when sidebar is closed (Desktop only) */}
        {!sidebarOpen && (
          <div
            className="hidden lg:block fixed left-0 top-20 bottom-0 w-1 z-50 bg-gov-blue-600 hover:w-2 transition-all duration-200"
            onMouseEnter={() => setSidebarHover(true)}
            onMouseLeave={() => setSidebarHover(false)}
            onClick={() => setSidebarOpen(true)}
            style={{ cursor: 'pointer' }}
          />
        )}

        {/* Hover Sidebar Preview (Desktop only, when closed) */}
        {!sidebarOpen && sidebarHover && (
          <div
            className="hidden lg:block fixed left-0 top-16 bottom-0 w-16 z-45 bg-white border-r border-gray-200 shadow-xl"
            onMouseEnter={() => setSidebarHover(true)}
            onMouseLeave={() => setSidebarHover(false)}
          >
            <div className="flex flex-col items-center py-6 space-y-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="flex items-center justify-center w-12 h-12 bg-gov-blue-50 hover:bg-gov-blue-100 rounded-xl transition-colors"
                title="Open Menu"
              >
                <ChevronRight className="h-6 w-6 text-gov-blue-600" />
              </button>
              
              {navigation.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.href;
                
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={handleNavClick}
                    className={`
                      flex items-center justify-center w-12 h-12 rounded-xl transition-all
                      ${isActive 
                        ? 'bg-gov-blue-50 text-gov-blue-700' 
                        : 'text-gray-600 hover:bg-gray-100'
                      }
                    `}
                    title={item.name}
                  >
                    <Icon className="h-5 w-5" />
                  </Link>
                );
              })}
            </div>
          </div>
        )}

        {/* Mobile Sidebar Overlay */}
        <aside className={`
          lg:hidden
          fixed inset-y-0 left-0 z-40
          ${mobileSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          w-80
          bg-white border-r border-gray-200 shadow-2xl
          transition-transform duration-300 ease-in-out
          mt-16
        `}>
          <nav className="h-full overflow-y-auto py-6 px-4">
            {/* Mobile Header */}
            <div className="mb-6 pb-4 border-b-2 border-gray-200">
              <div className="flex items-center gap-3 px-4">
                <div className="flex items-center justify-center w-9 h-9 bg-gov-blue-50 rounded-lg">
                  <Menu className="h-5 w-5 text-gov-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-bold text-gray-900 uppercase tracking-wide">MENU</p>
                  <p className="text-xs text-gray-500">Navigation</p>
                </div>
              </div>
            </div>

            {/* Navigation Items */}
            <div className="space-y-1">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                const Icon = item.icon;
                
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={handleNavClick}
                    className={`
                      flex items-center px-4 py-3.5 text-sm font-medium rounded-xl
                      transition-all duration-200
                      ${isActive
                        ? 'bg-gov-blue-50 text-gov-blue-700 border-l-4 border-gov-blue-600 shadow-sm'
                        : 'text-gray-700 hover:bg-gray-50 hover:text-gov-blue-600'
                      }
                    `}
                  >
                    <Icon className="mr-3 h-5 w-5" />
                    {item.name}
                  </Link>
                );
              })}
            </div>
            
            {/* Version info */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <div className="px-4 space-y-2">
                <p className="text-xs text-gray-500">Platform Version</p>
                <p className="text-sm font-semibold text-gov-navy-500">v2.0.0</p>
                <p className="text-xs text-gray-500 mt-2">Powered by AI & ML</p>
              </div>
            </div>
          </nav>
        </aside>

        {/* Main Content */}
        <main className={`
          flex-1 min-h-screen transition-all duration-300
          ${sidebarOpen ? 'lg:ml-80' : 'lg:ml-0'}
        `}>
          <div className="mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </div>
        </main>
      </div>

      {/* Mobile overlay backdrop */}
      {mobileSidebarOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30 mt-16"
          onClick={() => setMobileSidebarOpen(false)}
        />
      )}

      {/* AI Assistant */}
      <AIAssistant />
    </div>
  );
}
