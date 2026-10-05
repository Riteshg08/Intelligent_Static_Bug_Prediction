import React, { useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Bug, FolderOpen, Activity, Plus, Moon, Sun, LogOut } from 'lucide-react';
import { useTheme } from './ThemeProvider';
import UploadModal from './UploadModal'; // We will create this

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const [showUpload, setShowUpload] = useState(false);

  React.useEffect(() => {
    if (!localStorage.getItem('token')) {
      navigate('/login');
    }
  }, [navigate, location.pathname]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  let currentSection = "Projects";
  if (location.pathname.includes('/projects/') || location.pathname.includes('/analysis/')) {
    currentSection = "Code review";
  } else if (location.pathname.includes('/models/performance')) {
    currentSection = "Model";
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-gray-900 flex flex-col font-sans transition-colors duration-200">
      {/* Top Bar */}
      <header className="h-14 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-4 z-20">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2 text-indigo-700 dark:text-indigo-400 font-bold text-xl cursor-pointer" onClick={() => navigate('/')}>
            <Bug className="w-6 h-6" />
            <span>BugSight</span>
          </div>
          <div className="hidden md:flex items-center space-x-1 text-sm font-medium">
            <button className={`px-3 py-1.5 rounded-md ${currentSection === 'Projects' ? 'text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700' : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}`} onClick={() => navigate('/projects')}>
              <FolderOpen className="w-4 h-4 inline mr-2 mb-0.5" />
              Projects
            </button>
            <button className={`px-3 py-1.5 rounded-md ${currentSection === 'Model' ? 'text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700' : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}`} onClick={() => navigate('/models/performance')}>
              <Activity className="w-4 h-4 inline mr-2 mb-0.5" />
              Model
            </button>
          </div>
        </div>
        
        <div className="flex items-center space-x-3 text-sm">
          <button id="new-scan-btn" onClick={() => setShowUpload(true)} className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 rounded-md font-medium flex items-center shadow-sm">
            <Plus className="w-4 h-4 mr-1" />
            New scan
          </button>
          <button onClick={toggleTheme} className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 p-1.5">
            {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
          <button onClick={handleLogout} className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 p-1.5" title="Logout">
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 bg-[#F8FAFC] dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 flex flex-col pt-4 overflow-y-auto shrink-0">
          <div className="px-3 mb-8 space-y-0.5 text-sm font-medium">
            <NavLink to="/projects" end className={({ isActive }) => `flex items-center px-3 py-2 rounded-md ${isActive ? 'bg-indigo-50 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300' : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'}`}>
              <FolderOpen className="w-5 h-5 mr-3" />
              Projects
            </NavLink>
            <NavLink to="/models/performance" className={({ isActive }) => `flex items-center px-3 py-2 rounded-md ${isActive ? 'bg-indigo-50 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300' : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'}`}>
              <Activity className="w-5 h-5 mr-3" />
              Model Performance
            </NavLink>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 flex flex-col bg-white dark:bg-gray-800 overflow-hidden shadow-[-1px_0_10px_rgba(0,0,0,0.02)]">
          <Outlet />
        </main>
      </div>

      {showUpload && <UploadModal onClose={() => setShowUpload(false)} />}
    </div>
  );
}
