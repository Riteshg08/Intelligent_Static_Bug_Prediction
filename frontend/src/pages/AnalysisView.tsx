import React, { useEffect, useState, useCallback, useMemo } from 'react';
import api from '../lib/api';
import { useParams, useNavigate } from 'react-router-dom';
import { AlertTriangle, CheckCircle2, Download, Search, Info, Activity, Filter, ChevronLeft, ChevronRight, FileCode } from 'lucide-react';

export default function AnalysisView() {
  const { runId } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('queued');
  const [predictions, setPredictions] = useState([]);
  const [filesData, setFilesData] = useState([]);
  
  // Filters and state
  const [search, setSearch] = useState('');
  const [filterLevel, setFilterLevel] = useState('All');
  const [filterLang, setFilterLang] = useState('All');
  const [filterSeverity, setFilterSeverity] = useState('All');
  const [sortKey, setSortKey] = useState('priority');
  const [sortDir, setSortDir] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 15;
  const [activeTab, setActiveTab] = useState('functions'); // 'functions' or 'files'

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
      setPredictions(res.data);
      
      // Compute file-level data
      const filesMap = {};
      res.data.forEach(p => {
        if (!filesMap[p.file_path]) {
          filesMap[p.file_path] = { path: p.file_path, language: p.language, max_risk: 0, high_count: 0, med_count: 0, pattern_count: 0 };
        }
        filesMap[p.file_path].max_risk = Math.max(filesMap[p.file_path].max_risk, p.risk_score);
        if (p.risk_level === 'High') filesMap[p.file_path].high_count++;
        if (p.risk_level === 'Medium') filesMap[p.file_path].med_count++;
        if (p.pattern_severity && p.pattern_severity !== 'none') filesMap[p.file_path].pattern_count++;
      });
      setFilesData(Object.values(filesMap).sort((a, b) => b.max_risk - a.max_risk));
      
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
  const maxScore = predictions.length > 0 ? Math.max(...predictions.map(p => p.risk_score)) : 0;
  const maxScoreFunc = predictions.length > 0 ? predictions.find(p => p.risk_score === maxScore)?.function_name : '';

  // Language chart data
  const langCounts = {};
  predictions.forEach(p => {
    langCounts[p.language] = (langCounts[p.language] || 0) + 1;
  });
  const topLangs = Object.entries(langCounts).sort((a, b) => b[1] - a[1]).slice(0, 5);

  const getRiskColor = (level, bg = false) => {
    level = level?.toLowerCase() || 'low';
    if (level === 'high') return bg ? 'bg-red-50 dark:bg-red-900/30 text-red-700 border-red-200' : '#ef4444';
    if (level === 'medium' || level === 'warning') return bg ? 'bg-amber-50 dark:bg-amber-900/30 text-amber-700 border-amber-200' : '#f59e0b';
    if (level === 'low' || level === 'info') return bg ? 'bg-green-50 dark:bg-green-900/30 text-green-700 border-green-200' : '#22c55e';
    return bg ? 'bg-gray-50 dark:bg-gray-900 text-gray-700 dark:text-gray-200 border-gray-200 dark:border-gray-700' : '#6b7280';
  };

  const getSevLevel = (val) => {
    if (!val) return 'none';
    if (val.includes('high')) return 'high';
    if (val.includes('warning')) return 'warning';
    if (val.includes('info')) return 'info';
    return 'none';
  };

  const filteredAndSortedPredictions = useMemo(() => {
    let result = predictions.filter(p => {
      const matchSearch = p.function_name.toLowerCase().includes(search.toLowerCase()) || 
                          (p.file_path && p.file_path.toLowerCase().includes(search.toLowerCase()));
      const matchLevel = filterLevel === 'All' || p.risk_level === filterLevel;
      const matchLang = filterLang === 'All' || p.language === filterLang;
      const sev = getSevLevel(p.pattern_severity);
      const matchSev = filterSeverity === 'All' || (filterSeverity === 'High' && sev === 'high') || (filterSeverity === 'Warning' && sev === 'warning') || (filterSeverity === 'None' && sev === 'none');
      return matchSearch && matchLevel && matchLang && matchSev;
    });

    const severityScore = { 'high': 3, 'warning': 2, 'info': 1, 'none': 0 };

    result.sort((a, b) => {
      let aVal, bVal;
      if (sortKey === 'priority') {
        const aSev = severityScore[getSevLevel(a.pattern_severity)];
        const bSev = severityScore[getSevLevel(b.pattern_severity)];
        if (aSev !== bSev) return sortDir === 'asc' ? aSev - bSev : bSev - aSev;
        return sortDir === 'asc' ? a.risk_score - b.risk_score : b.risk_score - a.risk_score;
      } else if (sortKey === 'score') {
        aVal = a.risk_score;
        bVal = b.risk_score;
      } else if (sortKey === 'function') {
        aVal = a.function_name.toLowerCase();
        bVal = b.function_name.toLowerCase();
      } else if (sortKey === 'language') {
        aVal = a.language;
        bVal = b.language;
      }
      
      if (aVal < bVal) return sortDir === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
    
    return result;
  }, [predictions, search, filterLevel, filterLang, filterSeverity, sortKey, sortDir]);

  // Pagination
  const totalPages = Math.ceil(filteredAndSortedPredictions.length / itemsPerPage);
  const paginatedPredictions = filteredAndSortedPredictions.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const toggleSort = (key) => {
    if (sortKey === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
    setCurrentPage(1); // Reset to first page
  };

  const handleExport = async (format = 'json') => {
    setExporting(true);
    try {
      const res = await api.get(`/analysis/${runId}/export?format=${format}`);
      const blob = new Blob([format === 'json' ? JSON.stringify(res.data, null, 2) : res.data], { type: format === 'json' ? 'application/json' : 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analysis_${runId}_export.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("Failed to export.");
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 p-8 pt-6 overflow-y-auto">
      <div className="flex items-center text-sm text-gray-500 dark:text-gray-400 mb-2">
        <span>Workspace</span>
        <span className="mx-2">&gt;</span>
        <span className="text-gray-900 dark:text-white font-medium">Analysis results</span>
      </div>
      
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-slate-800 dark:text-white">Analysis results</h1>
        <div className="flex space-x-3">
          <button onClick={() => handleExport('csv')} disabled={exporting || status !== 'completed' && status !== 'analyzed'} className="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:bg-gray-900 text-gray-700 dark:text-gray-200 px-4 py-2 rounded-md font-medium flex items-center shadow-sm disabled:opacity-50">
            <Download className="w-4 h-4 mr-1.5" />
            CSV
          </button>
          <button onClick={() => handleExport('json')} disabled={exporting || status !== 'completed' && status !== 'analyzed'} className="bg-indigo-600 border border-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md font-medium flex items-center shadow-sm disabled:opacity-50">
            <Download className="w-4 h-4 mr-1.5" />
            JSON
          </button>
        </div>
      </div>

      <div className="bg-blue-50 dark:bg-blue-900/30 border-l-4 border-blue-500 p-4 rounded-r-md flex mb-8 text-sm">
        <Info className="w-5 h-5 text-blue-500 mr-2 shrink-0" />
        <span className="text-blue-900 dark:text-blue-200"><span className="font-semibold">Risk scores are predictions, not confirmed bugs.</span> Treat probabilities as triage signals and verify findings in context.</span>
      </div>

      {(status === 'queued' || status === 'running') && (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-md shadow-sm border border-gray-200 dark:border-gray-700 mb-6 flex flex-col items-center">
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
        <div className="bg-white dark:bg-gray-800 p-5 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-between h-28">
          <div className="flex justify-between items-start">
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Functions analyzed</span>
            <Activity className="w-5 h-5 text-gray-400" />
          </div>
          <div>
            <div className="text-3xl font-bold text-slate-800 dark:text-white">{totalFunctions}</div>
            <div className="text-xs text-gray-400 mt-1">Across {languages.length} source languages</div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-5 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-between h-28">
          <div className="flex justify-between items-start">
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">High risk</span>
            <div className="w-6 h-6 rounded-full border border-red-500 flex items-center justify-center">
              <span className="text-red-500 font-bold text-xs">!</span>
            </div>
          </div>
          <div>
            <div className="text-3xl font-bold text-slate-800 dark:text-white">{highRiskCount}</div>
            <div className="text-xs text-gray-400 mt-1">65% probability and above</div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-5 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-between h-28">
          <div className="flex justify-between items-start">
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Medium risk</span>
            <AlertTriangle className="w-5 h-5 text-amber-500" />
          </div>
          <div>
            <div className="text-3xl font-bold text-slate-800 dark:text-white">{mediumRiskCount}</div>
            <div className="text-xs text-gray-400 mt-1">35-64% estimated probability</div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-5 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-between h-28">
          <div className="flex justify-between items-start">
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Low risk</span>
            <CheckCircle2 className="w-5 h-5 text-green-500" />
          </div>
          <div>
            <div className="text-3xl font-bold text-slate-800 dark:text-white">{lowRiskCount}</div>
            <div className="text-xs text-gray-400 mt-1">Below 35% estimated probability</div>
          </div>
        </div>
      </div>

      <div className="flex flex-col xl:flex-row gap-6">
        {/* Main Table Area */}
        <div className="flex-1 flex flex-col bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm">
          
          <div className="border-b border-gray-200 dark:border-gray-700 flex">
            <button 
              onClick={() => { setActiveTab('functions'); setCurrentPage(1); }} 
              className={`px-6 py-3 text-sm font-medium border-b-2 ${activeTab === 'functions' ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'}`}
            >
              Function risk ranking
            </button>
            <button 
              onClick={() => { setActiveTab('files'); setCurrentPage(1); }} 
              className={`px-6 py-3 text-sm font-medium border-b-2 ${activeTab === 'files' ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'}`}
            >
              File-Level Risk
            </button>
          </div>

          <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex flex-col xl:flex-row xl:items-center justify-between gap-4 bg-gray-50/50 dark:bg-gray-900/50">
            {activeTab === 'functions' ? (
              <div className="flex flex-wrap items-center gap-3">
                <div className="relative">
                  <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                  <input 
                    type="text" 
                    placeholder="Search functions..." 
                    value={search}
                    onChange={(e) => { setSearch(e.target.value); setCurrentPage(1); }}
                    className="pl-9 pr-4 py-1.5 border border-gray-300 dark:border-gray-600 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 w-48 bg-white dark:bg-gray-800"
                  />
                </div>
                
                <div className="flex items-center space-x-2">
                  <Filter className="w-4 h-4 text-gray-400" />
                  <select 
                    value={filterLevel} 
                    onChange={e => { setFilterLevel(e.target.value); setCurrentPage(1); }}
                    className="border border-gray-300 dark:border-gray-600 rounded-md text-sm py-1.5 pl-2 pr-8 bg-white dark:bg-gray-800"
                  >
                    <option value="All">All Levels</option>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                  <select 
                    value={filterSeverity} 
                    onChange={e => { setFilterSeverity(e.target.value); setCurrentPage(1); }}
                    className="border border-gray-300 dark:border-gray-600 rounded-md text-sm py-1.5 pl-2 pr-8 bg-white dark:bg-gray-800"
                  >
                    <option value="All">All Findings</option>
                    <option value="High">High Patterns</option>
                    <option value="Warning">Warning Patterns</option>
                    <option value="None">No Patterns</option>
                  </select>
                  <select 
                    value={filterLang} 
                    onChange={e => { setFilterLang(e.target.value); setCurrentPage(1); }}
                    className="border border-gray-300 dark:border-gray-600 rounded-md text-sm py-1.5 pl-2 pr-8 bg-white dark:bg-gray-800"
                  >
                    <option value="All">All Languages</option>
                    {languages.map(l => <option key={l} value={l}>{l}</option>)}
                  </select>
                </div>
              </div>
            ) : (
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Showing risk aggregated by file</p>
              </div>
            )}
          </div>

          <div className="overflow-x-auto flex-1 flex flex-col justify-between">
            {activeTab === 'functions' ? (
              <table className="w-full text-left border-collapse min-w-[800px]">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider bg-gray-50 dark:bg-gray-900">
                    <th className="px-6 py-3 font-medium cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800" onClick={() => toggleSort('function')}>
                      Function {sortKey === 'function' && (sortDir === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="px-6 py-3 font-medium cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800" onClick={() => toggleSort('priority')}>
                      Review Priority {sortKey === 'priority' && (sortDir === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="px-6 py-3 font-medium cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800" onClick={() => toggleSort('language')}>
                      Language {sortKey === 'language' && (sortDir === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="px-6 py-3 font-medium cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800" onClick={() => toggleSort('score')}>
                      Probability {sortKey === 'score' && (sortDir === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="px-6 py-3"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-700 bg-white dark:bg-gray-800">
                  {paginatedPredictions.map(p => (
                    <tr key={p.id} className="hover:bg-gray-50 dark:bg-gray-900 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-bold text-gray-900 dark:text-white truncate max-w-[200px]" title={p.function_name}>{p.function_name}</div>
                        <div className="text-xs text-gray-400 mt-0.5 truncate max-w-[200px]" title={p.file_path}>{p.file_path}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-col space-y-1.5">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border w-fit ${getRiskColor(p.risk_level, true)}`}>
                            {p.risk_level === 'High' && <div className="w-3 h-3 rounded-full border border-current flex items-center justify-center mr-1 text-[8px] font-bold">!</div>}
                            {p.risk_level === 'Medium' && <AlertTriangle className="w-3 h-3 mr-1" />}
                            {p.risk_level === 'Low' && <CheckCircle2 className="w-3 h-3 mr-1" />}
                            {p.risk_level} Risk
                          </span>
                          {p.pattern_severity && p.pattern_severity !== 'none' && (
                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border w-fit ${
                              p.pattern_severity.includes('high') ? 'bg-red-50 dark:bg-red-900/30 text-red-700 border-red-200' :
                              p.pattern_severity.includes('warning') ? 'bg-amber-50 dark:bg-amber-900/30 text-amber-700 border-amber-200' :
                              'bg-blue-50 dark:bg-blue-900/30 text-blue-700 border-blue-200'
                            }`}>
                              <Info className="w-3 h-3 mr-1" />
                              {p.pattern_severity.includes('high') ? 'High Findings' : 'Warning Findings'}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-2.5 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs rounded border border-gray-200 dark:border-gray-600">{p.language}</span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center min-w-[120px]">
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 mr-3 overflow-hidden">
                            <div className="h-1.5 rounded-full" style={{ width: `${p.risk_score * 100}%`, backgroundColor: getRiskColor(p.risk_level) }}></div>
                          </div>
                          <span className="font-bold text-gray-700 dark:text-gray-200 text-sm">{(p.risk_score * 100).toFixed(0)}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button onClick={() => navigate(`/prediction/${p.id}`)} className="text-gray-400 hover:text-indigo-600 transition-colors">
                          <span className="font-mono text-lg font-bold">&gt;</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                  {paginatedPredictions.length === 0 && (
                    <tr>
                      <td colSpan="5" className="px-6 py-10 text-center text-gray-500 dark:text-gray-400">
                        No functions match the criteria.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            ) : (
              <table className="w-full text-left border-collapse min-w-[800px]">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700 text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider bg-gray-50 dark:bg-gray-900">
                    <th className="px-6 py-3 font-medium">File Path</th>
                    <th className="px-6 py-3 font-medium">Language</th>
                    <th className="px-6 py-3 font-medium">Max Probability</th>
                    <th className="px-6 py-3 font-medium">High / Med Risks</th>
                    <th className="px-6 py-3 font-medium">Functions w/ Patterns</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-700 bg-white dark:bg-gray-800">
                  {filesData.map((f, i) => (
                    <tr key={i} className="hover:bg-gray-50 dark:bg-gray-900 transition-colors">
                      <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white flex items-center">
                        <FileCode className="w-4 h-4 text-gray-400 mr-2 shrink-0"/> {f.path}
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-2.5 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs rounded border border-gray-200 dark:border-gray-600">{f.language}</span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`font-bold ${f.max_risk > 0.65 ? 'text-red-600' : f.max_risk > 0.35 ? 'text-amber-600' : 'text-green-600'}`}>
                          {(f.max_risk * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-2">
                          <span className="px-2 py-0.5 bg-red-50 text-red-700 rounded text-xs font-bold">{f.high_count}</span>
                          <span className="px-2 py-0.5 bg-amber-50 text-amber-700 rounded text-xs font-bold">{f.med_count}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-gray-600 dark:text-gray-300 font-medium">{f.pattern_count}</span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button onClick={() => navigate(`/projects/${project_id}/files/${f.id}`)} className="text-gray-400 hover:text-indigo-600 transition-colors">
                          <span className="font-mono text-lg font-bold">&gt;</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                  {filesData.length === 0 && (
                    <tr>
                      <td colSpan="5" className="px-6 py-10 text-center text-gray-500 dark:text-gray-400">
                        No files analyzed.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            )}

            {/* Pagination Controls */}
            {activeTab === 'functions' && totalPages > 1 && (
              <div className="border-t border-gray-200 dark:border-gray-700 px-4 py-3 flex items-center justify-between bg-gray-50 dark:bg-gray-900">
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Showing <span className="font-medium text-gray-900 dark:text-white">{(currentPage - 1) * itemsPerPage + 1}</span> to <span className="font-medium text-gray-900 dark:text-white">{Math.min(currentPage * itemsPerPage, filteredAndSortedPredictions.length)}</span> of <span className="font-medium text-gray-900 dark:text-white">{filteredAndSortedPredictions.length}</span> results
                </div>
                <div className="flex items-center space-x-2">
                  <button 
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                    className="p-1 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 text-gray-600 dark:text-gray-300"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300 px-2">Page {currentPage} of {totalPages}</span>
                  <button 
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                    className="p-1 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 text-gray-600 dark:text-gray-300"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Sidebar Charts */}
        <div className="w-full xl:w-72 flex flex-col gap-6 shrink-0">
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-5 shadow-sm">
            <h3 className="font-bold text-gray-900 dark:text-white text-base mb-1">Risk distribution</h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-6">Function-level predictions</p>
            
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
                  <span className="text-lg font-bold text-slate-800 dark:text-white leading-none">{totalFunctions}</span>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center text-gray-700 dark:text-gray-200">
                    <div className="w-3 h-3 rounded-full border border-red-500 flex items-center justify-center mr-2"><span className="text-[8px] font-bold text-red-500">!</span></div>
                    High
                  </div>
                  <span className="font-medium ml-4">{highRiskCount}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center text-gray-700 dark:text-gray-200">
                    <AlertTriangle className="w-3 h-3 text-amber-500 mr-2" />
                    Medium
                  </div>
                  <span className="font-medium ml-4">{mediumRiskCount}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center text-gray-700 dark:text-gray-200">
                    <CheckCircle2 className="w-3 h-3 text-green-500 mr-2" />
                    Low
                  </div>
                  <span className="font-medium ml-4">{lowRiskCount}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-5 shadow-sm">
            <h3 className="font-bold text-gray-900 dark:text-white text-base mb-1">Languages</h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">Functions analyzed per language</p>
            <div className="space-y-3 mt-4">
              {topLangs.map(([lang, count]) => (
                <div key={lang}>
                  <div className="flex justify-between text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    <span>{lang}</span>
                    <span>{count}</span>
                  </div>
                  <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-1.5">
                    <div className="bg-indigo-500 h-1.5 rounded-full" style={{ width: `${(count / totalFunctions) * 100}%` }}></div>
                  </div>
                </div>
              ))}
              {topLangs.length === 0 && <div className="text-sm text-gray-500">No data</div>}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-5 shadow-sm">
            <div className="flex justify-between items-start mb-1">
              <div>
                <h3 className="font-bold text-gray-900 dark:text-white text-base">Highest score</h3>
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-6">Current run maximum</p>
              </div>
              <div className="text-indigo-600 bg-indigo-50 dark:bg-indigo-900/30 p-1.5 rounded">
                <Activity className="w-4 h-4" />
              </div>
            </div>
            
            <div className="mb-2 text-3xl font-bold text-slate-800 dark:text-white text-right">
              {(maxScore * 100).toFixed(0)}%
            </div>
            <div className="font-bold text-gray-800 dark:text-gray-100 text-sm mb-3 text-right truncate" title={maxScoreFunc}>{maxScoreFunc || '-'}</div>
            
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div className="bg-red-500 h-2 rounded-full" style={{ width: `${maxScore * 100}%` }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
