import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AnalysisView from './pages/AnalysisView';
import BugDetailView from './pages/BugDetailView';
import ProjectViewer from './pages/ProjectViewer';
import ModelPerformance from './pages/ModelPerformance';

import Layout from './components/Layout';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects/:projectId" element={<ProjectViewer />} />
          <Route path="/analysis/:runId" element={<AnalysisView />} />
          <Route path="/prediction/:id" element={<BugDetailView />} />
          <Route path="/models/performance" element={<ModelPerformance />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
