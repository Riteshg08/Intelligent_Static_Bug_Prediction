import React, { useEffect, useState, useCallback } from 'react';
import api from '../lib/api';
import { useNavigate } from 'react-router-dom';
import { Info, Folder, AlertCircle, AlertTriangle, CheckCircle2, MoreHorizontal, Clock, Plus } from 'lucide-react';

export default function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [showUpload, setShowUpload] = useState(false);
  const [file, setFile] = useState(null);
  const [name, setName] = useState('');
  const navigate = useNavigate();

  const token = localStorage.getItem('token');

  const fetchProjects = useCallback(async () => {
    try {
      const res = await api.get('/projects');
      setProjects(res.data);
    } catch (err) {
      console.error(err);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const handleUpload = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('name', name);
    formData.append('file', file);
    
    try {
      const res = await api.post('/projects', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      const projectId = res.data.id;
      
      // Start analysis right away
      await api.post(`/projects/${projectId}/analyze`);
      
      setName('');
      setFile(null);
      setShowUpload(false);
      
      navigate(`/projects/${projectId}`);
    } catch (err) {
      console.error(err);
      alert("Failed to upload project");
    }
  };

  const viewProject = (projectId) => {
    navigate(`/projects/${projectId}`);
  };

  const totalHigh = projects.reduce((acc, p) => acc + (p.risk_counts?.high || 0), 0);
  const totalMedium = projects.reduce((acc, p) => acc + (p.risk_counts?.medium || 0), 0);
  const totalLow = projects.reduce((acc, p) => acc + (p.risk_counts?.low || 0), 0);

  const formatTimeAgo = (dateStr) => {
    if (!dateStr) return 'Never';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((now - date) / 60000);
    if (diff < 1) return 'Just now';
    if (diff < 60) return `${diff} minutes ago`;
    if (diff < 1440) return `${Math.floor(diff/60)} hours ago`;
    return 'Yesterday';
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 p-8 pt-6">
      <div className="flex items-center text-sm text-gray-500 mb-2">
        <span>Workspace</span>
        <span className="mx-2">&gt;</span>
        <span className="text-gray-900 font-medium">Projects</span>
      </div>
      
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-slate-800">Projects</h1>
        <button onClick={() => setShowUpload(!showUpload)} className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md font-medium flex items-center shadow-sm">
          <Plus className="w-4 h-4 mr-1.5" />
          New analysis
        </button>
      </div>

      <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-md flex mb-8 text-sm">
        <Info className="w-5 h-5 text-blue-500 mr-2 shrink-0" />
        <span className="text-blue-900"><span className="font-semibold">Risk scores are predictions, not confirmed bugs.</span> Treat probabilities as triage signals and verify findings in context.</span>
      </div>

      {showUpload && (
        <div className="bg-white shadow overflow-hidden sm:rounded-md mb-8 p-6 border border-gray-200">
          <h2 className="text-lg font-medium mb-4">Upload New Codebase</h2>
          <form onSubmit={handleUpload} className="flex gap-4 items-end">
            <div>
              <label className="block text-sm font-medium text-gray-700">Project Name</label>
              <input type="text" required value={name} onChange={e => setName(e.target.value)} className="mt-1 p-2 border border-gray-300 rounded-md w-64" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Zip/Tar File</label>
              <input type="file" required onChange={e => setFile(e.target.files[0])} className="mt-1" />
            </div>
            <button type="submit" className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 shadow-sm">Upload</button>
          </form>
        </div>
      )}

      {/* Top Cards */}
      <div className="grid grid-cols-4 gap-4 mb-10">
        <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-sm flex flex-col justify-between h-28">
          <div className="flex justify-between items-start">
            <span className="text-sm font-medium text-gray-500">Projects</span>
            <Folder className="w-5 h-5 text-gray-400" />
          </div>
          <div>
            <div className="text-3xl font-bold text-slate-800">{projects.length}</div>
            <div className="text-xs text-gray-400 mt-1">Across your workspace</div>
          </div>
        </div>
        <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-sm flex flex-col justify-between h-28">
          <div className="flex justify-between items-start">
            <span className="text-sm font-medium text-gray-500">High risk</span>
            <div className="w-6 h-6 rounded-full border border-red-500 flex items-center justify-center">
              <span className="text-red-500 font-bold text-xs">!</span>
            </div>
          </div>
          <div>
            <div className="text-3xl font-bold text-slate-800">{totalHigh}</div>
            <div className="text-xs text-gray-400 mt-1">Review these first</div>
          </div>
        </div>
        <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-sm flex flex-col justify-between h-28">
          <div className="flex justify-between items-start">
            <span className="text-sm font-medium text-gray-500">Medium risk</span>
            <AlertTriangle className="w-5 h-5 text-amber-500" />
          </div>
          <div>
            <div className="text-3xl font-bold text-slate-800">{totalMedium}</div>
            <div className="text-xs text-gray-400 mt-1">Worth a closer look</div>
          </div>
        </div>
        <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-sm flex flex-col justify-between h-28">
          <div className="flex justify-between items-start">
            <span className="text-sm font-medium text-gray-500">Low risk</span>
            <CheckCircle2 className="w-5 h-5 text-green-500" />
          </div>
          <div>
            <div className="text-3xl font-bold text-slate-800">{totalLow}</div>
            <div className="text-xs text-gray-400 mt-1">4 recent analyses</div>
          </div>
        </div>
      </div>

      <div className="flex justify-between items-end mb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Your projects</h2>
          <p className="text-sm text-gray-500">Source analyses and recent risk counts</p>
        </div>
        <div className="flex space-x-2">
          <button className="px-3 py-1.5 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 shadow-sm">
            All results
          </button>
          <button className="px-3 py-1.5 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 shadow-sm flex items-center">
            <span className="font-mono text-xs mr-1">&lt;/&gt;</span> Open workbench
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {projects.map(project => (
          <div key={project.id} onClick={() => viewProject(project.id)} className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm hover:shadow-md cursor-pointer transition-shadow flex flex-col h-48">
            <div className="flex justify-between items-start mb-3">
              <div className="w-8 h-8 rounded bg-indigo-50 flex items-center justify-center">
                <Folder className="w-4 h-4 text-indigo-500" />
              </div>
              <button className="text-gray-400 hover:text-gray-600">
                <MoreHorizontal className="w-5 h-5" />
              </button>
            </div>
            
            <div className="flex items-center mb-2">
              <h3 className="text-base font-bold text-gray-900 mr-2 truncate">{project.name}</h3>
            </div>
            
            <div className="flex flex-wrap gap-1 mb-4">
              {(project.languages || []).map(lang => (
                <span key={lang} className="text-xs bg-gray-50 text-gray-600 px-1.5 py-0.5 border border-gray-200 rounded">
                  {lang}
                </span>
              ))}
            </div>
            
            <div className="flex justify-between mt-auto pt-4">
              <div className="flex flex-col">
                <span className="text-red-500 font-bold text-lg leading-tight">{project.risk_counts?.high || 0}</span>
                <span className="text-[10px] text-gray-400 uppercase tracking-wider">High</span>
              </div>
              <div className="flex flex-col">
                <span className="text-amber-500 font-bold text-lg leading-tight">{project.risk_counts?.medium || 0}</span>
                <span className="text-[10px] text-gray-400 uppercase tracking-wider">Medium</span>
              </div>
              <div className="flex flex-col text-right">
                <span className="text-green-500 font-bold text-lg leading-tight">{project.risk_counts?.low || 0}</span>
                <span className="text-[10px] text-gray-400 uppercase tracking-wider">Low</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center mt-4 pt-3 border-t border-gray-100 text-xs text-gray-400 font-medium">
              <div className="flex items-center">
                <Clock className="w-3.5 h-3.5 mr-1 text-gray-300" />
                {formatTimeAgo(project.last_updated)}
              </div>
              <div>
                {project.function_count || 0} functions
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {projects.length === 0 && !showUpload && (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200 shadow-sm mt-4">
          <Folder className="mx-auto h-12 w-12 text-gray-300" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No projects</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by creating a new analysis.</p>
          <div className="mt-6">
            <button
              onClick={() => setShowUpload(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              <Plus className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
              New Analysis
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
