import React, { useEffect, useState, useCallback } from 'react';
import api from '../lib/api';
import { useParams, useNavigate } from 'react-router-dom';
import { Check, X, ArrowLeft, AlertTriangle, Info, CheckCircle2, ShieldCheck } from 'lucide-react';

export default function BugDetailView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [feedbackSaved, setFeedbackSaved] = useState(false);
  const [error, setError] = useState(null);

  const fetchReport = useCallback(async () => {
    try {
      const res = await api.get(`/predictions/${id}/report`);
      setReport(res.data);
    } catch (e) {
      console.error(e);
      setError("Failed to load bug details.");
    }
  }, [id]);

  useEffect(() => {
    fetchReport();
    
    // Check if we have feedback saved already
    api.get(`/predictions/${id}/feedback`)
      .then(res => {
        if (res.data) setFeedbackSaved(true);
      })
      .catch(() => {});
      

  }, [fetchReport, id]);

  const submitFeedback = async (isBug) => {
    try {
      await api.post(`/predictions/${id}/feedback`, { is_real_bug: isBug, comment: '' });
      setFeedbackSaved(true);
    } catch (err) {
      console.error(err);
      alert("Failed to save feedback");
    }
  };

  if (error) return <div className="p-8 text-center text-red-500">{error}</div>;
  if (!report) return <div className="p-8 text-center text-gray-500 dark:text-gray-400">Loading...</div>;

  const reasons = [];
  if (report.explanation?.reasons) {
    reasons.push(...report.explanation.reasons);
  } else if (report.explanation) {
    Object.values(report.explanation).forEach(val => {
      if (Array.isArray(val)) {
        reasons.push(...val);
      } else if (typeof val === 'string') {
        reasons.push(val);
      }
    });
  }
  
  // Show only 2 to 3 reasons
  const topReasons = reasons.slice(0, 3);
  
  const metrics = report.explanation?.metrics || {};

  const getRiskColor = (level, bg = false) => {
    level = level.toLowerCase();
    if (level === 'high') return bg ? 'bg-red-50 text-red-700 border-red-200' : '#ef4444';
    if (level === 'medium' || level === 'warning') return bg ? 'bg-amber-50 text-amber-700 border-amber-200' : '#f59e0b';
    if (level === 'low' || level === 'info') return bg ? 'bg-green-50 text-green-700 border-green-200' : '#22c55e';
    return bg ? 'bg-gray-50 text-gray-700 border-gray-200' : '#6b7280';
  };

  const scoreColor = getRiskColor(report.risk_level);
  
  // Language norms placeholders (this would realistically come from backend)
  const getNorm = (metric, lang) => {
    const norms = {
      length: 25,
      cyclomatic_complexity: 5,
      nesting_depth: 2,
      parameter_count: 2,
      branch_count: 3
    };
    return norms[metric] || 'N/A';
  };

  const jumpToLine = (line) => {
    navigate(`/projects/${report.file_id}`);
    // In a real implementation we would pass the line to scroll to via state or hash
  };

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <button 
          onClick={() => navigate(-1)} 
          className="flex items-center text-sm text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white mb-6 font-medium transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-1" /> Back to results
        </button>
        
        <div className="flex flex-col md:flex-row md:items-start justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
              <span className="font-mono text-xl mr-3 text-gray-400 bg-white dark:bg-gray-800 px-2 py-1 rounded border border-gray-200 dark:border-gray-700 shadow-sm">&lt;/&gt;</span>
              {report.function_name}
            </h1>
            <div className="flex items-center mt-3 space-x-3">
              <span className="bg-white dark:bg-gray-800 px-3 py-1 rounded-full text-sm font-medium border border-gray-200 dark:border-gray-700 shadow-sm text-gray-700 dark:text-gray-300">
                {report.language}
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400 font-medium">
                in {report.file_path || 'Unknown file'}
              </span>
            </div>
          </div>
          
          <div className="flex flex-col items-end">
            <div className="flex items-center">
              <div className="w-24 h-24 relative mr-4">
                <svg viewBox="0 0 36 36" className="w-full h-full transform -rotate-90 drop-shadow-sm">
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#e5e7eb"
                    strokeWidth="3.5"
                    strokeDasharray="100, 100"
                  />
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke={scoreColor}
                    strokeWidth="3.5"
                    strokeDasharray={`${report.risk_score * 100}, 100`}
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-xl font-bold text-gray-900 dark:text-white">{(report.risk_score * 100).toFixed(0)}</span>
                </div>
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Risk Level</span>
                <span className={`inline-flex items-center px-3 py-1 rounded-md text-sm font-bold border shadow-sm ${getRiskColor(report.risk_level, true)}`}>
                  {report.risk_level === 'High' && <div className="w-3.5 h-3.5 rounded-full border border-current flex items-center justify-center mr-1.5 text-[9px]">!</div>}
                  {report.risk_level === 'Medium' && <AlertTriangle className="w-4 h-4 mr-1.5" />}
                  {report.risk_level === 'Low' && <CheckCircle2 className="w-4 h-4 mr-1.5" />}
                  {report.risk_level}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                <h2 className="text-lg font-bold text-gray-900 dark:text-white">Why is this risky?</h2>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Plain-language explanation from the ML model</p>
              </div>
              <div className="p-6">
                {topReasons.length > 0 ? (
                  <ul className="space-y-4">
                    {topReasons.map((r, idx) => (
                      <li key={idx} className="flex items-start">
                        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center text-indigo-600 dark:text-indigo-400 font-bold text-xs mt-0.5 mr-3">
                          {idx + 1}
                        </div>
                        <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">{r}</p>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500 dark:text-gray-400 text-sm">No specific reasons were provided by the model.</p>
                )}
                
                {report.confidence_note && (
                  <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-md border border-blue-100 dark:border-blue-800/30 flex items-start">
                    <Info className="w-5 h-5 text-blue-500 mr-3 shrink-0 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-bold text-blue-900 dark:text-blue-300">Model Confidence</h4>
                      <p className="text-sm text-blue-800 dark:text-blue-200 mt-1">{report.confidence_note}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                <h2 className="text-lg font-bold text-gray-900 dark:text-white">Pattern Findings</h2>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Static analysis hotspots found in this function</p>
              </div>
              
              <div className="p-0">
                {report.hotspots && report.hotspots.length > 0 ? (
                  <ul className="divide-y divide-gray-100 dark:divide-gray-700">
                    {report.hotspots.map((h, i) => (
                      <li key={i} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-900/50 transition-colors">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start">
                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border mr-3 mt-0.5 ${getRiskColor(h.severity, true)}`}>
                              {h.severity}
                            </span>
                            <div>
                              <p className="text-sm text-gray-800 dark:text-gray-200 font-medium mb-1">{h.message}</p>
                              <p className="text-xs text-gray-500 dark:text-gray-400 font-mono">Rule: {h.rule_id}</p>
                            </div>
                          </div>
                          <button 
                            onClick={() => jumpToLine(h.start_line)}
                            className="flex items-center text-xs font-medium text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300 bg-indigo-50 dark:bg-indigo-900/30 px-3 py-1.5 rounded-md transition-colors"
                          >
                            <span className="font-mono mr-1.5">&lt;/&gt;</span>
                            Line {h.start_line}
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="p-8 text-center">
                    <CheckCircle2 className="w-10 h-10 text-green-400 mx-auto mb-3" />
                    <p className="text-gray-500 dark:text-gray-400 text-sm">No known risky patterns detected in this function.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                <h2 className="text-base font-bold text-gray-900 dark:text-white">Metrics vs Norms</h2>
              </div>
              <div className="p-0 overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-gray-50 dark:bg-gray-900/50 text-xs text-gray-500 dark:text-gray-400">
                    <tr>
                      <th className="px-5 py-3 font-medium">Metric</th>
                      <th className="px-5 py-3 font-medium">Value</th>
                      <th className="px-5 py-3 font-medium">Norm</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                    {Object.entries(metrics).map(([key, val]) => {
                      const norm = getNorm(key, report.language);
                      const isHigh = typeof val === 'number' && typeof norm === 'number' && val > norm * 1.5;
                      
                      return (
                        <tr key={key} className={isHigh ? 'bg-red-50/50 dark:bg-red-900/10' : ''}>
                          <td className="px-5 py-3 text-gray-700 dark:text-gray-300 capitalize">{key.replace(/_/g, ' ')}</td>
                          <td className={`px-5 py-3 font-mono font-medium ${isHigh ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-white'}`}>
                            {val}
                            {isHigh && <span className="ml-1 text-red-500">↑</span>}
                          </td>
                          <td className="px-5 py-3 text-gray-500 dark:text-gray-400 font-mono">{norm}</td>
                        </tr>
                      );
                    })}
                    {Object.keys(metrics).length === 0 && (
                      <tr>
                        <td colSpan="3" className="px-5 py-4 text-center text-gray-500 dark:text-gray-400 text-xs">No metrics available</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-base font-bold text-gray-900 dark:text-white">Developer Feedback</h2>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Help improve the model</p>
              </div>
              <div className="p-5">
                {feedbackSaved ? (
                  <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800/30 rounded-md p-4 text-center">
                    <Check className="w-8 h-8 text-green-500 mx-auto mb-2" />
                    <p className="text-sm font-medium text-green-800 dark:text-green-300">Feedback saved successfully</p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1">Thank you for improving BugSight!</p>
                  </div>
                ) : (
                  <div>
                    <p className="text-sm text-gray-700 dark:text-gray-300 mb-4 font-medium">Is this function actually risky or buggy?</p>
                    <div className="flex flex-col gap-3">
                      <button 
                        onClick={() => submitFeedback(true)} 
                        className="flex items-center justify-center gap-2 bg-white dark:bg-gray-800 border-2 border-red-200 dark:border-red-900 text-red-700 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 px-4 py-2.5 rounded-md font-bold transition-colors"
                      >
                        <Check size={18}/> Yes, Real Bug
                      </button>
                      <button 
                        onClick={() => submitFeedback(false)} 
                        className="flex items-center justify-center gap-2 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 px-4 py-2.5 rounded-md font-bold transition-colors"
                      >
                        <X size={18}/> No, False Alarm
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
            

          </div>
        </div>
      </div>
    </div>
  );
}
