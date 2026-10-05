import React from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Bug, LayoutDashboard, FolderOpen, Code2, Table2, Bell, Plus, Moon, LogOut, ChevronDown, Activity } from 'lucide-react';

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();

  React.useEffect(() => {
    if (!localStorage.getItem('token')) {
      navigate('/login');
    }
  }, [navigate, location.pathname]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  // Determine current active section for top bar breadcrumbs
  let currentSection = "Projects";
  if (location.pathname.includes('/projects/') || location.pathname.includes('/runs/')) {
    currentSection = "Code review";
  } else if (location.pathname.includes('/analysis/')) {
    currentSection = "Results";
  } else if (location.pathname.includes('/models/performance')) {
    currentSection = "Model";
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col font-sans">
      {/* Top Bar */}
      <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-4 z-20">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2 text-indigo-700 font-bold text-xl cursor-pointer" onClick={() => navigate('/')}>
            <Bug className="w-6 h-6" />
            <span>BugSight</span>
          </div>
          <div className="hidden md:flex items-center space-x-1 text-sm font-medium">
            <button className={`px-3 py-1.5 rounded-md ${currentSection === 'Projects' ? 'text-gray-900 bg-gray-100' : 'text-gray-600 hover:bg-gray-50'}`} onClick={() => navigate('/')}>
              <FolderOpen className="w-4 h-4 inline mr-2 mb-0.5" />
              Projects
            </button>
            <button className={`px-3 py-1.5 rounded-md ${currentSection === 'Code review' ? 'text-gray-900 bg-gray-100' : 'text-gray-600 hover:bg-gray-50'}`}>
              <Code2 className="w-4 h-4 inline mr-2 mb-0.5" />
              Code review
            </button>
            <button className={`px-3 py-1.5 rounded-md ${currentSection === 'Results' ? 'text-gray-900 bg-gray-100' : 'text-gray-600 hover:bg-gray-50'}`}>
              <Table2 className="w-4 h-4 inline mr-2 mb-0.5" />
              Results
            </button>
            <button className={`px-3 py-1.5 rounded-md ${currentSection === 'Model' ? 'text-gray-900 bg-gray-100' : 'text-gray-600 hover:bg-gray-50'}`} onClick={() => navigate('/models/performance')}>
              <Activity className="w-4 h-4 inline mr-2 mb-0.5" />
              Model
            </button>
          </div>
        </div>
        
        <div className="flex items-center space-x-3 text-sm">
          <button className="text-gray-500 hover:text-gray-700 p-1.5">
            <Bell className="w-5 h-5" />
          </button>
          <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 rounded-md font-medium flex items-center shadow-sm">
            <Plus className="w-4 h-4 mr-1" />
            New scan
          </button>
          <button className="text-gray-500 hover:text-gray-700 p-1.5">
            <Moon className="w-5 h-5" />
          </button>
          <button onClick={handleLogout} className="text-gray-500 hover:text-gray-700 p-1.5" title="Logout">
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 bg-[#F8FAFC] border-r border-gray-200 flex flex-col pt-4 overflow-y-auto shrink-0">
          <div className="px-4 mb-6">
            <h3 className="text-xs font-bold text-gray-400 tracking-wider mb-3 uppercase">Workspace</h3>
            <button className="w-full flex items-center justify-between bg-white border border-gray-200 rounded-md px-3 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50">
              <div className="flex items-center">
                <Code2 className="w-4 h-4 text-indigo-600 mr-2" />
                <span className="truncate">My workspace</span>
              </div>
              <ChevronDown className="w-4 h-4 text-gray-400" />
            </button>
          </div>

          <div className="px-3 mb-8 space-y-0.5 text-sm font-medium">
            <NavLink to="/" end className={({ isActive }) => `flex items-center px-3 py-2 rounded-md ${isActive && currentSection === 'Projects' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-100'}`}>
              <LayoutDashboard className="w-5 h-5 mr-3" />
              Overview
            </NavLink>
            <NavLink to="/" end className={({ isActive }) => `flex items-center px-3 py-2 rounded-md ${isActive && currentSection === 'Projects' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-100'}`}>
              <FolderOpen className="w-5 h-5 mr-3" />
              Projects
            </NavLink>
            <div className={`flex items-center px-3 py-2 rounded-md cursor-pointer ${currentSection === 'Code review' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-100'}`}>
              <Code2 className="w-5 h-5 mr-3" />
              Code review
            </div>
            <div className={`flex items-center px-3 py-2 rounded-md cursor-pointer ${currentSection === 'Results' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-100'}`}>
              <Table2 className="w-5 h-5 mr-3" />
              Results
            </div>
            <NavLink to="/models/performance" className={({ isActive }) => `flex items-center px-3 py-2 rounded-md ${isActive ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-100'}`}>
              <Activity className="w-5 h-5 mr-3" />
              Model Performance
            </NavLink>
          </div>

          <div className="px-3 space-y-0.5 text-sm font-medium">
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 flex flex-col bg-white overflow-hidden shadow-[-1px_0_10px_rgba(0,0,0,0.02)]">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
