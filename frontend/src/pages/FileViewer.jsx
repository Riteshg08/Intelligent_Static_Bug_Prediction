import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { AlertTriangle, AlertCircle, Info, ChevronRight, ChevronLeft, ChevronDown, FileCode, CheckCircle2, FileWarning, Search } from 'lucide-react';

const api = axios.create({
  baseURL: '/api/v1'
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

const ITEM_HEIGHT = 22; // px per line
const BUFFER = 20;

export default function FileViewer() {
  const { runId, fileId } = useParams();
  const navigate = useNavigate();

  const [files, setFiles] = useState([]);
  const [sourceCode, setSourceCode] = useState('');
  const [annotations, setAnnotations] = useState({ functions: [], hotspots: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [fileError, setFileError] = useState(null);

  // Toolbar state
  const [viewMode, setViewMode] = useState('whole'); // 'whole' | 'function'
  const [selectedFunc, setSelectedFunc] = useState(null);
  const [severityFilter, setSeverityFilter] = useState('all'); // 'all' | 'high' | 'warning' | 'info'
  const [showHotspots, setShowHotspots] = useState(true);
  
  const scrollContainerRef = useRef(null);
  const [scrollTop, setScrollTop] = useState(0);

  useEffect(() => {
    // Load file list for sidebar
    api.get(`/analysis/${runId}/files`)
      .then(res => setFiles(res.data))
      .catch(err => console.error("Failed to load files", err));
  }, [runId]);

  useEffect(() => {
    if (!fileId) return;
    setLoading(true);
    setFileError(null);
    setSourceCode('');
    setAnnotations({ functions: [], hotspots: [] });
    
    Promise.all([
      api.get(`/files/${fileId}/source`).then(res => res.data.source).catch(err => {
        throw new Error(err.response?.status === 404 ? "File not found or unsupported" : "Failed to load source");
      }),
      api.get(`/files/${fileId}/annotations?run_id=${runId}`).then(res => res.data).catch(() => ({ functions: [], hotspots: [] }))
    ])
    .then(([source, ann]) => {
      setSourceCode(source);
      setAnnotations(ann);
      setLoading(false);
    })
    .catch(err => {
      setFileError(err.message);
      setLoading(false);
    });
  }, [fileId, runId]);

  const lines = useMemo(() => sourceCode.split('\n'), [sourceCode]);

  const filteredHotspots = useMemo(() => {
    let hs = annotations.hotspots || [];
    if (!showHotspots) hs = [];
    else if (severityFilter !== 'all') {
      hs = hs.filter(h => h.severity === severityFilter);
    }
    
    // Sort by line
    hs.sort((a, b) => a.start_line - b.start_line);
    return hs;
  }, [annotations.hotspots, showHotspots, severityFilter]);

  // Virtualization
  const containerHeight = 600; // default px
  const visibleCount = Math.ceil(containerHeight / ITEM_HEIGHT) + BUFFER * 2;
  const startIndex = Math.max(0, Math.floor(scrollTop / ITEM_HEIGHT) - BUFFER);
  const endIndex = Math.min(lines.length, startIndex + visibleCount);
  
  const visibleLines = useMemo(() => {
    const arr = [];
    for (let i = startIndex; i < endIndex; i++) {
      arr.push({ index: i, text: lines[i] });
    }
    return arr;
  }, [startIndex, endIndex, lines]);

  const scrollToLine = (lineNum) => {
    if (scrollContainerRef.current) {
      const top = (lineNum - 1) * ITEM_HEIGHT - (containerHeight / 2);
      scrollContainerRef.current.scrollTo({ top: Math.max(0, top), behavior: 'smooth' });
    }
  };

  useEffect(() => {
    if (!loading && window.location.hash && annotations.functions.length > 0) {
      const funcName = decodeURIComponent(window.location.hash.substring(1));
      const func = annotations.functions.find(f => f.name === funcName);
      if (func) {
        setTimeout(() => scrollToLine(func.start_line), 100);
      }
    }
  }, [loading, annotations.functions, fileId]);

  const nextRiskyLine = () => {
    if (!filteredHotspots.length) return;
    const currentLine = Math.floor(scrollTop / ITEM_HEIGHT) + 1;
    const next = filteredHotspots.find(h => h.start_line > currentLine + 5);
    if (next) scrollToLine(next.start_line);
    else scrollToLine(filteredHotspots[0].start_line); // wrap around
  };
  
  const prevRiskyLine = () => {
    if (!filteredHotspots.length) return;
    const currentLine = Math.floor(scrollTop / ITEM_HEIGHT) + 1;
    const prevs = filteredHotspots.filter(h => h.start_line < currentLine - 5);
    if (prevs.length) scrollToLine(prevs[prevs.length - 1].start_line);
    else scrollToLine(filteredHotspots[filteredHotspots.length - 1].start_line);
  };

  const getRiskColor = (level, opacity = 1) => {
    if (level === 'high') return `rgba(239, 68, 68, ${opacity})`;
    if (level === 'medium' || level === 'warning') return `rgba(245, 158, 11, ${opacity})`;
    if (level === 'low' || level === 'info') return `rgba(59, 130, 246, ${opacity})`;
    return `rgba(34, 197, 94, ${opacity})`; // clean
  };

  // Group findings
  const findingsGrouped = { high: [], warning: [], info: [] };
  filteredHotspots.forEach(h => {
    const sev = h.severity === 'high' ? 'high' : (h.severity === 'warning' || h.severity === 'medium' ? 'warning' : 'info');
    findingsGrouped[sev].push(h);
  });

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-white overflow-hidden">
      {/* Sidebar: File List */}
      <div className="w-64 border-r border-gray-200 flex flex-col bg-gray-50 overflow-hidden">
        <div className="p-4 border-b border-gray-200 bg-white">
          <h2 className="text-lg font-medium text-gray-900">Files</h2>
          <p className="text-sm text-gray-500">{files.length} analyzed</p>
        </div>
        <div className="flex-1 overflow-y-auto p-2">
          {files.map(f => {
            const isSelected = f.id.toString() === fileId;
            let icon = <CheckCircle2 className="w-4 h-4 text-green-500" />;
            if (f.risk_counts.high > 0) icon = <AlertTriangle className="w-4 h-4 text-red-500" />;
            else if (f.risk_counts.medium > 0) icon = <AlertCircle className="w-4 h-4 text-amber-500" />;
            
            return (
              <button
                key={f.id}
                onClick={() => navigate(`/runs/${runId}/files/${f.id}`)}
                className={`w-full flex items-center p-2 mb-1 rounded-md text-left text-sm truncate ${isSelected ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700 hover:bg-gray-100'}`}
                title={f.path}
              >
                <span className="mr-2 flex-shrink-0">{icon}</span>
                <span className="truncate">{f.path.split(/[/\\]/).pop()}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {!fileId ? (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            Select a file from the left to view its source.
          </div>
        ) : loading ? (
          <div className="flex-1 flex items-center justify-center text-gray-500">Loading...</div>
        ) : (
          <>
            {/* Toolbar */}
            <div className="h-14 border-b border-gray-200 bg-white flex items-center justify-between px-4">
              <div className="flex items-center space-x-4">
                <span className="font-medium text-gray-900 truncate max-w-sm">
                  {files.find(f => f.id.toString() === fileId)?.path}
                </span>
                <div className="h-4 w-px bg-gray-300" />
                <div className="flex items-center space-x-2 text-sm">
                  <label className="flex items-center space-x-1 cursor-pointer">
                    <input type="checkbox" checked={showHotspots} onChange={e => setShowHotspots(e.target.checked)} className="rounded text-indigo-600 focus:ring-indigo-500" />
                    <span>Show Hotspots</span>
                  </label>
                  <select 
                    value={severityFilter} 
                    onChange={e => setSeverityFilter(e.target.value)}
                    className="ml-2 block w-full pl-3 pr-10 py-1 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                  >
                    <option value="all">All Severities</option>
                    <option value="high">High Risk</option>
                    <option value="warning">Warnings</option>
                  </select>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button onClick={prevRiskyLine} className="p-1 rounded bg-gray-100 hover:bg-gray-200 text-gray-600" title="Previous risky line">
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button onClick={nextRiskyLine} className="p-1 rounded bg-gray-100 hover:bg-gray-200 text-gray-600" title="Next risky line">
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="bg-yellow-50 border-b border-yellow-200 p-2 text-xs text-yellow-800 text-center flex justify-center items-center">
              <Info className="w-4 h-4 mr-1" />
              Highlights are risky patterns from static analysis, not confirmed bugs. Scores are probabilities.
            </div>

            {fileError && (
              <div className="bg-red-50 border-l-4 border-red-400 p-4 m-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <FileWarning className="h-5 w-5 text-red-400" aria-hidden="true" />
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-red-700">
                      Skipped or unsupported file: {fileError}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {!fileError && (
              <div className="flex-1 flex overflow-hidden">
                {/* Source code viewer */}
                <div className="flex-1 flex flex-col bg-[#1e1e1e] overflow-hidden">
                  <div 
                    ref={scrollContainerRef}
                    onScroll={e => setScrollTop(e.target.scrollTop)}
                    className="flex-1 overflow-auto font-mono text-[14px] leading-[22px] text-gray-300"
                    style={{ position: 'relative' }}
                  >
                    <div style={{ height: lines.length * ITEM_HEIGHT, position: 'relative' }}>
                      <div style={{ transform: `translateY(${startIndex * ITEM_HEIGHT}px)`, position: 'absolute', top: 0, left: 0, right: 0 }}>
                        {visibleLines.map(({index, text}) => {
                          const lineNum = index + 1;
                          
                          // Check if line is inside a function
                          const func = annotations.functions.find(f => lineNum >= f.start_line && lineNum <= f.end_line);
                          
                          // Check for hotspots
                          const hotspot = filteredHotspots.find(h => lineNum >= h.start_line && lineNum <= h.end_line);
                          
                          let bgStyle = {};
                          if (func) {
                            bgStyle = { backgroundColor: getRiskColor(func.risk_level || 'low', 0.1) };
                          }
                          
                          let gutterHighlight = null;
                          if (hotspot) {
                            bgStyle = { ...bgStyle, backgroundColor: getRiskColor(hotspot.severity, 0.2) };
                            gutterHighlight = (
                              <div 
                                className="absolute left-0 top-0 bottom-0 w-1 cursor-pointer" 
                                style={{ backgroundColor: getRiskColor(hotspot.severity, 1) }}
                                title={`${hotspot.rule_id}: ${hotspot.message}`}
                              />
                            );
                          }
                          
                          // Function label on first line
                          let funcLabel = null;
                          if (func && lineNum === func.start_line) {
                            funcLabel = (
                              <div className="absolute right-4 text-xs px-2 py-0.5 rounded opacity-80 z-10" style={{ backgroundColor: getRiskColor(func.risk_level, 0.8), color: '#fff' }}>
                                {func.name} {(func.risk_score * 100).toFixed(0)}%
                              </div>
                            );
                          }

                          return (
                            <div key={lineNum} className="flex relative hover:bg-white/5" style={{ height: ITEM_HEIGHT, ...bgStyle }}>
                              {gutterHighlight}
                              <div className="w-12 flex-shrink-0 text-right pr-4 text-gray-500 select-none border-r border-gray-700">
                                {lineNum}
                              </div>
                              <div className="pl-4 whitespace-pre overflow-x-hidden" style={{ width: 'calc(100% - 3rem)' }}>
                                {text || ' '}
                              </div>
                              {funcLabel}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Side panel: Risky findings */}
                <div className="w-72 border-l border-gray-200 bg-white flex flex-col overflow-hidden">
                  <div className="p-3 border-b border-gray-200 font-medium text-sm text-gray-900 bg-gray-50">
                    Risky Findings
                  </div>
                  <div className="flex-1 overflow-y-auto">
                    {['high', 'warning', 'info'].map(sev => (
                      findingsGrouped[sev].length > 0 && (
                        <div key={sev} className="mb-4">
                          <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider bg-gray-50 border-y border-gray-100 flex items-center">
                            {sev === 'high' && <AlertTriangle className="w-3 h-3 mr-1 text-red-500" />}
                            {sev === 'warning' && <AlertCircle className="w-3 h-3 mr-1 text-amber-500" />}
                            {sev === 'info' && <Info className="w-3 h-3 mr-1 text-blue-500" />}
                            {sev} ({findingsGrouped[sev].length})
                          </div>
                          <ul className="divide-y divide-gray-100">
                            {findingsGrouped[sev].map(h => (
                              <li 
                                key={h.id} 
                                className="p-3 hover:bg-gray-50 cursor-pointer transition-colors"
                                onClick={() => scrollToLine(h.start_line)}
                              >
                                <div className="text-xs font-medium text-gray-900 break-words mb-1">
                                  {h.message}
                                </div>
                                <div className="text-xs text-gray-500 flex justify-between">
                                  <span>{h.rule_id}</span>
                                  <span>Line {h.start_line}</span>
                                </div>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )
                    ))}
                    {filteredHotspots.length === 0 && (
                      <div className="p-4 text-sm text-gray-500 text-center">
                        No findings match the current filters.
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
