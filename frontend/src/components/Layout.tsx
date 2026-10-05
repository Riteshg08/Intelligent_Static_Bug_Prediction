import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Bug, FolderOpen, Plus, Moon, Sun, LogOut } from 'lucide-react';
import { useTheme } from './ThemeProvider';
import UploadModal from './UploadModal';
import api from '../lib/api';
import toast from 'react-hot-toast';

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const [showUpload, setShowUpload] = useState(false);
  const [isValidating, setIsValidating] = useState(true);

  useEffect(() => {
    const validateToken = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login', { replace: true });
        return;
      }
      try {
        await api.get('/users/me');
      } catch (err) {
        // API interceptor will handle 401, but just in case:
        if (err.response?.status === 401) {
          localStorage.removeItem('token');
          toast.error("Session expired, please log in");
          navigate('/login', { replace: true });
        }
      } finally {
        setIsValidating(false);
      }
    };
    validateToken();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login', { replace: true });
  };

  if (isValidating) {
    return <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC] dark:bg-gray-900 text-gray-500">Loading...</div>;
  }

  let currentSection = "Projects";
  if (location.pathname.includes('/projects/') || location.pathname.includes('/analysis/')) {
    currentSection = "Code review";
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-gray-900 flex flex-col font-sans transition-colors duration-200">
      {/* Top Bar */}
      <header className="h-14 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-4 z-20">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2 text-indigo-700 dark:text-indigo-400 font-bold text-xl cursor-pointer" onClick={() => navigate('/projects')}>
            <Bug className="w-6 h-6" />
            <span>BugSight</span>
          </div>
        </div>
        
        <div className="flex items-center space-x-3 text-sm">
          <button id="new-scan-btn" onClick={() => setShowUpload(true)} className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 rounded-md font-medium flex items-center shadow-sm">
            <Plus className="w-4 h-4 mr-1" />
            New scan
          </button>
          <button onClick={toggleTheme} className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 p-1.5" title="Toggle dark mode">
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
            <NavLink to="/projects" end className={({ isActive }) => `flex items-center px-3 py-2 rounded-md ${isActive || location.pathname === '/' ? 'bg-indigo-50 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300' : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'}`}>
              <FolderOpen className="w-5 h-5 mr-3" />
              Projects
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
