import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AnalysisView from './pages/AnalysisView';
import BugDetailView from './pages/BugDetailView';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <span className="text-xl font-bold text-indigo-600">BugPredictor</span>
              </div>
              <div className="flex items-center">
                <button 
                  onClick={() => {
                    localStorage.removeItem('token');
                    window.location.href = '/login';
                  }} 
                  className="text-gray-500 hover:text-gray-700 font-medium"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>

        <main>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Dashboard />} />
            <Route path="/analysis/:runId" element={<AnalysisView />} />
            <Route path="/prediction/:id" element={<BugDetailView />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
