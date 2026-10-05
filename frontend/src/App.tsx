import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import ProjectsView from './pages/ProjectsView';
import AnalysisView from './pages/AnalysisView';
import BugDetailView from './pages/BugDetailView';
import ProjectViewer from './pages/ProjectViewer';
import NotFound from './pages/NotFound';
import { Toaster } from 'react-hot-toast';

import Layout from './components/Layout';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/projects" replace />} />
          <Route path="/projects" element={<ProjectsView />} />
          <Route path="/projects/:projectId" element={<ProjectViewer />} />
          <Route path="/projects/:projectId/files/:fileId" element={<ProjectViewer />} />
          <Route path="/analysis/:runId" element={<AnalysisView />} />
          <Route path="/prediction/:id" element={<BugDetailView />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
      <Toaster position="bottom-right" />
    </BrowserRouter>
  );
}

export default App;
