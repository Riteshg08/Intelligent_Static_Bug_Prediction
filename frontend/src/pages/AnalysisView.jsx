import React, { useEffect, useState, useCallback } from 'react';
import api from '../lib/api';
import { useParams, useNavigate } from 'react-router-dom';
import { AlertTriangle, CheckCircle2, Download, Search, Info, Activity } from 'lucide-react';

export default function AnalysisView() {
  const { runId } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('queued');
  const [predictions, setPredictions] = useState([]);
  const [search, setSearch] = useState('');
  const [error, setError] = useState(null);
  const [exporting, setExporting] = useState(false);

  const checkStatus = useCallback(async () => {
    try {
      const res = await api.get(`/analysis/${runId}/status`);
      setStatus(res.data.status);
    } catch (e) {
      console.error(e);
      setError("Failed to load analysis status.");
    }
  }, [runId]);

  const fetchPredictions = useCallback(async () => {
    try {
      const res = await api.get(`/analysis/${runId}/predictions`);
      setPredictions(res.data.sort((a, b) => b.risk_score - a.risk_score));
    } catch (e) {
      console.error(e);
      setError("Failed to load predictions.");
    }
  }, [runId]);

  useEffect(() => {
    let interval;
    if (status === 'queued' || status === 'running') {
      interval = setInterval(checkStatus, 3000);
    }
    return () => clearInterval(interval);
  }, [status, checkStatus]);

  useEffect(() => {
    if (status === 'analyzed' || status === 'completed') {
      fetchPredictions();
    }
  }, [status, fetchPredictions]);

  const highRiskCount = predictions.filter(p => p.risk_level === 'High').length;
  const mediumRiskCount = predictions.filter(p => p.risk_level === 'Medium').length;
  const lowRiskCount = predictions.filter(p => p.risk_level === 'Low').length;
  const totalFunctions = predictions.length;

  const languages = [...new Set(predictions.map(p => p.language))];
  const maxScore = predictions.length > 0 ? predictions[0].risk_score : 0;
  const maxScoreFunc = predictions.length > 0 ? predictions[0].function_name : '';

  const getRiskColor = (level, bg = false) => {
    level = level.toLowerCase();
    if (level === 'high') return bg ? 'bg-red-50 text-red-700 border-red-200' : '#ef4444';
    if (level === 'medium' || level === 'warning') return bg ? 'bg-amber-50 text-amber-700 border-amber-200' : '#f59e0b';
    if (level === 'low' || level === 'info') return bg ? 'bg-green-50 text-green-700 border-green-200' : '#22c55e';
    return bg ? 'bg-gray-50 text-gray-700 border-gray-200' : '#6b7280';
  };

  const filteredPredictions = predictions.filter(p => 
    p.function_name.toLowerCase().includes(search.toLowerCase()) || 
    (p.file_path && p.file_path.toLowerCase().includes(search.toLowerCase()))
  );

  const handleExport = async () => {
    setExporting(true);
    try {
      const res = await api.get(`/analysis/${runId}/export`);
      const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analysis_${runId}_export.json`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("Failed to export JSON.");
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 p-8 pt-6 overflow-y-auto">
      <div className="flex items-center text-sm text-gray-500 mb-2">
        <span>Workspace</span>
        <span className="mx-2">&gt;</span>
        <span className="text-gray-900 font-medium">Analysis results</span>
      </div>
      
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-slate-800">Analysis results</h1>
        <button onClick={handleExport} disabled={exporting || status !== 'completed' && status !== 'analyzed'} className="bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-md font-medium flex items-center shadow-sm disabled:opacity-50">
          <Download className="w-4 h-4 mr-1.5" />
          {exporting ? 'Exporting...' : 'Export JSON'}
        </button>
      </div>

      <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-md flex mb-8 text-sm">
        <Info className="w-5 h-5 text-blue-500 mr-2 shrink-0" />
        <span className="text-blue-900"><span className="font-semibold">Risk scores are predictions, not confirmed bugs.</span> Treat probabilities as triage signals and verify findings in context.</span>
      </div>

      {(status === 'queued' || status === 'running') && (
        <div className="bg-white p-6 rounded-md shadow-sm border border-gray-200 mb-6 flex flex-col items-center">
          <div className="flex items-center text-indigo-600 font-bold mb-4">
            <span className="animate-pulse mr-2 h-3 w-3 rounded-full bg-indigo-600"></span>
            Analysis running...
          </div>
          <div className="w-full max-w-md bg-gray-200 rounded-full h-2">
            <div className="bg-indigo-600 h-2 rounded-full" style={{ width: status === 'queued' ? '30%' : '70%' }}></div>
          </div>
        </div>
      )}

      {/* Top Cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-sm flex flex-col justify-between h-28">
          <div className="flex justify-between items-start">
            <span className="text-sm font-medium text-gray-500">Functions analyzed</span>
            <Activity className="w-5 h-5 text-gray-400" />
          </div>
          <div>
            <div className="text-3xl font-bold text-slate-800">{totalFunctions}</div>
            <div className="text-xs text-gray-400 mt-1">Across {languages.length} source languages</div>
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
            <div className="text-3xl font-bold text-slate-800">{highRiskCount}</div>
            <div className="text-xs text-gray-400 mt-1">65% probability and above</div>
          </div>
        </div>
        <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-sm flex flex-col justify-between h-28">
          <div className="flex justify-between items-start">
            <span className="text-sm font-medium text-gray-500">Medium risk</span>
            <AlertTriangle className="w-5 h-5 text-amber-500" />
          </div>
          <div>
            <div className="text-3xl font-bold text-slate-800">{mediumRiskCount}</div>
            <div className="text-xs text-gray-400 mt-1">35-64% estimated probability</div>
          </div>
        </div>
        <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-sm flex flex-col justify-between h-28">
          <div className="flex justify-between items-start">
            <span className="text-sm font-medium text-gray-500">Low risk</span>
            <CheckCircle2 className="w-5 h-5 text-green-500" />
          </div>
          <div>
            <div className="text-3xl font-bold text-slate-800">{lowRiskCount}</div>
            <div className="text-xs text-gray-400 mt-1">Below 35% estimated probability</div>
          </div>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Main Table Area */}
        <div className="flex-1 flex flex-col bg-white border border-gray-200 rounded-lg shadow-sm">
          <div className="p-4 border-b border-gray-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-bold text-slate-800">Function risk ranking</h2>
              <p className="text-sm text-gray-500">Highest estimated probabilities first</p>
            </div>
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                <input 
                  type="text" 
                  placeholder="Search functions..." 
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-9 pr-4 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 w-48"
                />
              </div>
              <select className="border border-gray-300 rounded-md text-sm py-1.5 px-3 bg-white text-gray-700 outline-none">
                <option>All</option>
              </select>
              <select className="border border-gray-300 rounded-md text-sm py-1.5 px-3 bg-white text-gray-700 outline-none">
                <option>All</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-gray-200 text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-50">
                  <th className="px-6 py-3 font-medium">Function ↑↓</th>
                  <th className="px-6 py-3 font-medium">File</th>
                  <th className="px-6 py-3 font-medium">Language ↑↓</th>
                  <th className="px-6 py-3 font-medium">Probability ↓</th>
                  <th className="px-6 py-3 font-medium">Risk</th>
                  <th className="px-6 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 bg-white">
                {filteredPredictions.map(p => (
                  <tr key={p.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-bold text-gray-900">{p.function_name}</div>
                      <div className="text-xs text-gray-400 mt-0.5">L{p.start_line}-{p.end_line}</div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">{p.file_path || 'Unknown'}</td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 bg-gray-100 text-gray-600 text-xs rounded border border-gray-200">{p.language}</span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="w-24 bg-gray-200 rounded-full h-1.5 mr-3 overflow-hidden">
                          <div className="h-1.5 rounded-full" style={{ width: `${p.risk_score * 100}%`, backgroundColor: getRiskColor(p.risk_level) }}></div>
                        </div>
                        <span className="font-bold text-gray-700 text-sm">{(p.risk_score * 100).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${getRiskColor(p.risk_level, true)}`}>
                        {p.risk_level === 'High' && <div className="w-3 h-3 rounded-full border border-current flex items-center justify-center mr-1 text-[8px] font-bold">!</div>}
                        {p.risk_level === 'Medium' && <AlertTriangle className="w-3 h-3 mr-1" />}
                        {p.risk_level === 'Low' && <CheckCircle2 className="w-3 h-3 mr-1" />}
                        {p.risk_level}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button onClick={() => navigate(`/prediction/${p.id}`)} className="text-gray-400 hover:text-indigo-600 transition-colors">
                        <span className="font-mono text-lg">&lt;/&gt;</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredPredictions.length === 0 && status !== 'queued' && status !== 'running' && (
              <div className="text-center py-10 text-gray-500">
                No functions match the criteria.
              </div>
            )}
          </div>
        </div>

        {/* Right Sidebar Charts */}
        <div className="w-full lg:w-72 flex flex-col gap-6 shrink-0">
          <div className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm">
            <h3 className="font-bold text-gray-900 text-base mb-1">Risk distribution</h3>
            <p className="text-xs text-gray-500 mb-6">Function-level predictions</p>
            
            <div className="flex items-center justify-between">
              <div className="relative w-20 h-20">
                <svg viewBox="0 0 36 36" className="w-full h-full transform -rotate-90">
                  <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#f3f4f6" strokeWidth="4"></circle>
                  {totalFunctions > 0 && (
                    <>
                      <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#ef4444" strokeWidth="4" strokeDasharray={`${(highRiskCount/totalFunctions)*100} ${100 - (highRiskCount/totalFunctions)*100}`} strokeDashoffset="0"></circle>
                      <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#f59e0b" strokeWidth="4" strokeDasharray={`${(mediumRiskCount/totalFunctions)*100} ${100 - (mediumRiskCount/totalFunctions)*100}`} strokeDashoffset={`-${(highRiskCount/totalFunctions)*100}`}></circle>
                      <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#22c55e" strokeWidth="4" strokeDasharray={`${(lowRiskCount/totalFunctions)*100} ${100 - (lowRiskCount/totalFunctions)*100}`} strokeDashoffset={`-${((highRiskCount + mediumRiskCount)/totalFunctions)*100}`}></circle>
                    </>
                  )}
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-lg font-bold text-slate-800 leading-none">{totalFunctions}</span>
                  <span className="text-[9px] text-gray-500 mt-1 uppercase tracking-wider">Functions</span>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center text-gray-700">
                    <div className="w-3 h-3 rounded-full border border-red-500 flex items-center justify-center mr-2"><span className="text-[8px] font-bold text-red-500">!</span></div>
                    High
                  </div>
                  <span className="font-medium ml-4">{highRiskCount}/{totalFunctions}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center text-gray-700">
                    <AlertTriangle className="w-3 h-3 text-amber-500 mr-2" />
                    Medium
                  </div>
                  <span className="font-medium ml-4">{mediumRiskCount}/{totalFunctions}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center text-gray-700">
                    <CheckCircle2 className="w-3 h-3 text-green-500 mr-2" />
                    Low
                  </div>
                  <span className="font-medium ml-4">{lowRiskCount}/{totalFunctions}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm">
            <div className="flex justify-between items-start mb-1">
              <div>
                <h3 className="font-bold text-gray-900 text-base">Highest score</h3>
                <p className="text-xs text-gray-500 mb-6">Current project maximum</p>
              </div>
              <div className="text-indigo-600 bg-indigo-50 p-1.5 rounded">
                <Activity className="w-4 h-4" />
              </div>
            </div>
            
            <div className="mb-2 text-3xl font-bold text-slate-800 text-right">
              {(maxScore * 100).toFixed(0)}%
            </div>
            <div className="font-bold text-gray-800 text-sm mb-3 text-right">{maxScoreFunc}</div>
            
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div className="bg-red-500 h-2 rounded-full" style={{ width: `${maxScore * 100}%` }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
