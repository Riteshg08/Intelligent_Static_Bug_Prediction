import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../lib/api';
import { AlertTriangle, Info, FileCode, CheckCircle2, Folder, ChevronUp, ChevronDown, AlignLeft } from 'lucide-react';

const ITEM_HEIGHT = 22; // px per line
const BUFFER = 20;

export default function ProjectViewer() {
  const { projectId } = useParams();
  const navigate = useNavigate();

  const [files, setFiles] = useState([]);
  const [fileId, setFileId] = useState(null);
  const [runId, setRunId] = useState(null);
  const [runStatus, setRunStatus] = useState(null);
  const [projectName, setProjectName] = useState('');
  
  const [sourceCode, setSourceCode] = useState('');
  const [annotations, setAnnotations] = useState({ functions: [], hotspots: [] });
  const [loading, setLoading] = useState(true);
  const [fileError, setFileError] = useState(null);

  const [severityFilter, setSeverityFilter] = useState('all');
  
  const scrollContainerRef = useRef(null);
  const [scrollTop, setScrollTop] = useState(0);

  const fetchFiles = () => {
    api.get(`/projects/${projectId}/files`)
      .then(res => {
        setFiles(res.data.files);
        setRunId(res.data.run_id);
        setRunStatus(res.data.run_status);
        if (!fileId && res.data.files.length > 0) {
          setFileId(res.data.files[0].id.toString());
        }
      })
      .catch(err => console.error("Failed to load files", err));
  };

  useEffect(() => {
    // Also fetch project name for the explorer
    api.get('/projects').then(res => {
      const p = res.data.find(x => x.id.toString() === projectId);
      if (p) setProjectName(p.name);
    }).catch(() => {});
    fetchFiles();
  }, [projectId]);

  useEffect(() => {
    let interval;
    if (runStatus === 'queued' || runStatus === 'running') {
      interval = setInterval(fetchFiles, 2000);
    }
    return () => clearInterval(interval);
  }, [runStatus, projectId]);

  useEffect(() => {
    if (!fileId) return;
    setLoading(true);
    setFileError(null);
    setSourceCode('');
    setAnnotations({ functions: [], hotspots: [] });
    
    const fetchSource = api.get(`/files/${fileId}/source`).then(res => res.data.source).catch(err => {
      throw new Error(err.response?.status === 404 ? "File not found or unsupported" : "Failed to load source");
    });
    
    const fetchAnn = runId && (runStatus === 'analyzed' || runStatus === 'running') 
      ? api.get(`/files/${fileId}/annotations?run_id=${runId}`).then(res => res.data).catch(() => ({ functions: [], hotspots: [] }))
      : Promise.resolve({ functions: [], hotspots: [] });
      
    Promise.all([fetchSource, fetchAnn])
    .then(([source, ann]) => {
      setSourceCode(source);
      setAnnotations(ann);
      setLoading(false);
    })
    .catch(err => {
      setFileError(err.message);
      setLoading(false);
    });
  }, [fileId, runId, files.find(f => f.id.toString() === fileId)?.status]);

  const lines = useMemo(() => sourceCode.split('\n'), [sourceCode]);

  const filteredHotspots = useMemo(() => {
    let hs = annotations.hotspots || [];
    if (severityFilter !== 'all') {
      hs = hs.filter(h => h.severity === severityFilter);
    }
    hs.sort((a, b) => a.start_line - b.start_line);
    return hs;
  }, [annotations.hotspots, severityFilter]);

  const containerHeight = 600;
  const visibleItemCount = Math.ceil(containerHeight / ITEM_HEIGHT) + 2 * BUFFER;
  const startIndex = Math.max(0, Math.floor(scrollTop / ITEM_HEIGHT) - BUFFER);
  const endIndex = Math.min(lines.length - 1, startIndex + visibleItemCount);

  const visibleLines = useMemo(() => {
    return lines.slice(startIndex, endIndex + 1).map((text, i) => ({
      index: startIndex + i,
      text
    }));
  }, [lines, startIndex, endIndex]);

  const scrollToLine = (lineNum) => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = Math.max(0, (lineNum - 5) * ITEM_HEIGHT);
    }
  };

  const nextRiskyLine = () => {
    if (!filteredHotspots.length) return;
    const currentLine = Math.floor(scrollTop / ITEM_HEIGHT) + 1;
    const nexts = filteredHotspots.filter(h => h.start_line > currentLine + 10);
    if (nexts.length) scrollToLine(nexts[0].start_line);
    else scrollToLine(filteredHotspots[0].start_line);
  };

  const prevRiskyLine = () => {
    if (!filteredHotspots.length) return;
    const currentLine = Math.floor(scrollTop / ITEM_HEIGHT) + 1;
    const prevs = filteredHotspots.filter(h => h.start_line < currentLine - 5);
    if (prevs.length) scrollToLine(prevs[prevs.length - 1].start_line);
    else scrollToLine(filteredHotspots[filteredHotspots.length - 1].start_line);
  };

  const getRiskColor = (level, opacity = 1) => {
    level = level.toLowerCase();
    if (level === 'high') return `rgba(239, 68, 68, ${opacity})`;
    if (level === 'medium' || level === 'warning') return `rgba(245, 158, 11, ${opacity})`;
    if (level === 'low' || level === 'info') return `rgba(59, 130, 246, ${opacity})`;
    return `rgba(34, 197, 94, ${opacity})`;
  };

  const findingsGrouped = { high: [], warning: [], info: [] };
  filteredHotspots.forEach(h => {
    const sev = h.severity === 'high' ? 'high' : (h.severity === 'warning' || h.severity === 'medium' ? 'warning' : 'info');
    findingsGrouped[sev].push(h);
  });

  const selectedFile = files.find(f => f.id.toString() === fileId);

  return (
    <div className="flex-1 flex flex-col min-w-0 h-full p-8 pt-6 overflow-hidden">
      <div className="flex flex-col shrink-0">
        <div className="flex items-center text-sm text-gray-500 mb-2">
          <span>Workspace</span>
          <span className="mx-2">&gt;</span>
          <span className="text-gray-900 font-medium">Code review</span>
        </div>
        
        <h1 className="text-3xl font-bold text-slate-800 mb-6">Code review</h1>

        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-md flex mb-6 text-sm">
          <Info className="w-5 h-5 text-blue-500 mr-2 shrink-0" />
          <span className="text-blue-900"><span className="font-semibold">Risk scores are predictions, not confirmed bugs.</span> Treat probabilities as triage signals and verify findings in context.</span>
        </div>

        {(runStatus === 'queued' || runStatus === 'running') && (
          <div className="bg-indigo-50 border-l-4 border-indigo-500 p-3 rounded-r-md flex mb-6 text-sm text-indigo-900 flex items-center">
            <span className="animate-pulse mr-2 h-2.5 w-2.5 rounded-full bg-indigo-600"></span>
            <span className="font-medium mr-1">Analysis running...</span>
            {files.filter(f => f.status === 'analyzed' || f.status === 'skipped').length} of {files.length} files done
          </div>
        )}
      </div>

      <div className="flex flex-1 overflow-hidden border-t border-gray-200 mt-2">
        {/* Sidebar */}
        <div className="w-64 border-r border-gray-200 flex flex-col bg-[#F8FAFC] overflow-hidden shrink-0">
          <div className="px-4 py-3 border-b border-gray-200">
            <h3 className="text-xs font-bold text-gray-400 tracking-wider uppercase">Explorer</h3>
          </div>
          
          <div className="p-3">
            <div className="flex items-center px-2 py-1.5 text-sm font-medium text-gray-700 bg-gray-100/50 rounded-md mb-2">
              <Folder className="w-4 h-4 text-indigo-500 mr-2 shrink-0" />
              <span className="truncate">{projectName || 'project'}</span>
            </div>
            
            <div className="space-y-0.5 mt-1">
              {files.map(f => {
                const isSelected = f.id.toString() === fileId;
                const findingsCount = (f.risk_counts?.high || 0) + (f.risk_counts?.medium || 0);
                
                return (
                  <button
                    key={f.id}
                    onClick={() => setFileId(f.id.toString())}
                    className={`w-full flex items-center justify-between px-2 py-1.5 rounded-md text-left text-sm ${isSelected ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-gray-600 hover:bg-gray-100'}`}
                    title={f.path}
                  >
                    <div className="flex items-center truncate">
                      <FileCode className="w-4 h-4 mr-2 text-gray-400 shrink-0" />
                      <span className="truncate">{f.path.split(/[/\\]/).pop()}</span>
                    </div>
                    {findingsCount > 0 && (
                      <span className="flex-shrink-0 ml-2 w-5 h-5 flex items-center justify-center rounded-full border border-red-200 text-[10px] font-bold text-red-500 bg-white">
                        {findingsCount}
                      </span>
                    )}
                    {findingsCount === 0 && f.status === 'analyzed' && (
                      <span className="flex-shrink-0 ml-2 text-[10px] text-green-500"><CheckCircle2 className="w-4 h-4" /></span>
                    )}
                    {f.status === 'skipped' && (
                      <span className="flex-shrink-0 ml-2 px-1 text-[9px] bg-orange-100 text-orange-600 rounded">skipped</span>
                    )}
                    {f.status === 'unsupported' && (
                      <span className="flex-shrink-0 ml-2 px-1 text-[9px] bg-gray-200 text-gray-500 rounded">unsupported</span>
                    )}
                  </button>
                )
              })}
            </div>
          </div>

          <div className="px-4 py-3 border-t border-gray-200 mt-auto flex-shrink-0">
            <h3 className="text-xs font-bold text-gray-400 tracking-wider uppercase mb-3">Functions</h3>
            <div className="space-y-1 overflow-y-auto max-h-48">
              {annotations.functions.length === 0 ? (
                <div className="text-xs text-gray-400 px-2">No functions detected</div>
              ) : (
                annotations.functions.map((fn, idx) => (
                  <button key={idx} onClick={() => scrollToLine(fn.start_line)} className="w-full flex items-center justify-between px-2 py-1.5 hover:bg-gray-100 rounded text-sm text-gray-600">
                    <div className="flex items-center truncate">
                      <span className="font-mono text-xs mr-2 text-gray-400">&lt;/&gt;</span>
                      <span className="truncate">{fn.name}</span>
                    </div>
                    <span className="text-xs font-medium" style={{ color: getRiskColor(fn.risk_level || 'low') }}>
                      {(fn.risk_score * 100).toFixed(0)}%
                    </span>
                  </button>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Code Viewer Area */}
        <div className="flex-1 flex flex-col min-w-0 bg-white border-r border-gray-200">
          {!fileId ? (
            <div className="flex-1 flex items-center justify-center text-gray-400">Select a file to view</div>
          ) : loading ? (
            <div className="flex-1 flex items-center justify-center text-gray-400">Loading source...</div>
          ) : (
            <>
              {/* File Header */}
              <div className="h-12 border-b border-gray-200 flex items-center justify-between px-4 bg-gray-50">
                <div className="flex items-center text-sm">
                  <span className="text-gray-500">{projectName || 'project'} &gt;</span>
                  <span className="ml-2 font-medium text-gray-900">{selectedFile?.path}</span>
                  <span className="ml-3 px-2 py-0.5 bg-white border border-gray-200 rounded text-xs text-gray-500">{selectedFile?.language || 'Unknown'}</span>
                </div>
                <div className="flex items-center space-x-3 text-sm">
                  <button onClick={prevRiskyLine} className="p-1 hover:bg-gray-200 rounded text-gray-500"><ChevronUp className="w-4 h-4" /></button>
                  <span className="text-gray-500">1 / {filteredHotspots.length || 1}</span>
                  <button onClick={nextRiskyLine} className="p-1 hover:bg-gray-200 rounded text-gray-500"><ChevronDown className="w-4 h-4" /></button>
                  <button 
                    onClick={() => runId && navigate(`/analysis/${runId}`)}
                    className={`flex items-center px-2.5 py-1.5 border rounded shadow-sm text-gray-700 ml-4 ${runId ? 'border-gray-200 bg-white hover:bg-gray-50' : 'border-gray-100 bg-gray-50 opacity-50 cursor-not-allowed'}`}
                    disabled={!runId}
                  >
                    <AlignLeft className="w-4 h-4 mr-1.5" />
                    Results
                  </button>
                </div>
              </div>

              {fileError && (
                <div className="bg-orange-50 border-y border-orange-200 p-2 text-xs text-orange-800 flex items-center">
                  <AlertTriangle className="w-4 h-4 mr-2 shrink-0 text-orange-500" />
                  Skipped files: {selectedFile?.path} — {fileError}
                </div>
              )}

              {/* Code Editor Area */}
              <div className="flex-1 flex flex-col bg-[#FDFDFD] overflow-hidden relative">
                <div 
                  ref={scrollContainerRef}
                  onScroll={e => setScrollTop(e.target.scrollTop)}
                  className="flex-1 overflow-auto font-mono text-[13px] leading-[22px] text-gray-800 outline-none"
                  style={{ position: 'relative' }}
                >
                  <div style={{ height: lines.length * ITEM_HEIGHT, position: 'relative' }}>
                    <div style={{ transform: `translateY(${startIndex * ITEM_HEIGHT}px)`, position: 'absolute', top: 0, left: 0, right: 0 }}>
                      {visibleLines.map(({index, text}) => {
                        const lineNum = index + 1;
                        
                        // Check if inside function
                        const func = annotations.functions.find(f => lineNum >= f.start_line && lineNum <= f.end_line);
                        // Check for hotspot
                        const hotspot = filteredHotspots.find(h => lineNum >= h.start_line && lineNum <= h.end_line);
                        
                        let bgStyle = {};
                        if (func && func.risk_level === 'High') bgStyle = { backgroundColor: 'rgba(239, 68, 68, 0.05)' };
                        else if (func && func.risk_level === 'Medium') bgStyle = { backgroundColor: 'rgba(245, 158, 11, 0.05)' };

                        let gutterHighlight = null;
                        let inlineLabel = null;
                        let functionHeader = null;

                        if (hotspot) {
                          bgStyle = { ...bgStyle, backgroundColor: getRiskColor(hotspot.severity, 0.15) };
                          gutterHighlight = (
                            <div className="absolute left-0 top-0 bottom-0 w-1" style={{ backgroundColor: getRiskColor(hotspot.severity, 1) }} />
                          );
                          if (lineNum === hotspot.start_line) {
                            inlineLabel = (
                              <div className="inline-flex items-center ml-4 px-2 py-0.5 rounded text-[11px] font-sans border shadow-sm" style={{ backgroundColor: '#fff', borderColor: getRiskColor(hotspot.severity, 0.5), color: '#333' }}>
                                <AlertTriangle className="w-3 h-3 mr-1" style={{ color: getRiskColor(hotspot.severity, 1) }} />
                                <span className="font-bold mr-1">{hotspot.severity.charAt(0).toUpperCase() + hotspot.severity.slice(1)}</span>
                                <span className="text-gray-600">{hotspot.message}</span>
                              </div>
                            );
                          }
                        }

                        if (func && lineNum === func.start_line) {
                          functionHeader = (
                            <div className="absolute right-4 top-1 text-[11px] px-2 py-0.5 rounded-full font-sans font-medium text-indigo-700 bg-indigo-50 border border-indigo-100 shadow-sm z-10 flex items-center">
                              {func.name} - {(func.risk_score * 100).toFixed(0)}%
                            </div>
                          );
                        }

                        return (
                          <div key={lineNum} className="flex relative hover:bg-gray-50/50 group" style={{ height: ITEM_HEIGHT, ...bgStyle }}>
                            {gutterHighlight}
                            <div className="w-12 flex-shrink-0 text-right pr-4 text-gray-400 select-none bg-gray-50 border-r border-gray-200">
                              {lineNum}
                            </div>
                            <div className="pl-4 whitespace-pre overflow-x-hidden relative flex items-center" style={{ width: 'calc(100% - 3rem)' }}>
                              <span>{text || ' '}</span>
                              {inlineLabel}
                              {functionHeader}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Right Sidebar: Findings */}
        <div className="w-72 bg-white flex flex-col shrink-0">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center mb-1">
              <h2 className="text-lg font-bold text-gray-900">Findings</h2>
              <span className="ml-2 bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded text-xs font-bold">{filteredHotspots.length}</span>
            </div>
            <p className="text-xs text-gray-500 truncate">{selectedFile?.path.split(/[/\\]/).pop()} - {filteredHotspots.length} predicted hotspots</p>
            
            <div className="flex mt-4 space-x-1">
              <button onClick={() => setSeverityFilter('all')} className={`flex-1 py-1 text-xs font-medium rounded border ${severityFilter === 'all' ? 'bg-gray-100 border-gray-300 text-gray-800' : 'bg-white border-gray-200 text-gray-500'}`}>All</button>
              <button onClick={() => setSeverityFilter('high')} className={`flex-1 py-1 text-xs font-medium rounded border ${severityFilter === 'high' ? 'bg-red-50 border-red-200 text-red-700' : 'bg-white border-gray-200 text-gray-500'}`}>High</button>
              <button onClick={() => setSeverityFilter('medium')} className={`flex-1 py-1 text-xs font-medium rounded border ${severityFilter === 'medium' ? 'bg-amber-50 border-amber-200 text-amber-700' : 'bg-white border-gray-200 text-gray-500'}`}>Medium</button>
              <button onClick={() => setSeverityFilter('low')} className={`flex-1 py-1 text-xs font-medium rounded border ${severityFilter === 'low' ? 'bg-green-50 border-green-200 text-green-700' : 'bg-white border-gray-200 text-gray-500'}`}>Low</button>
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {['high', 'warning', 'info'].map(sev => (
              findingsGrouped[sev].length > 0 && (
                <div key={sev} className="space-y-3">
                  <div className="flex items-center text-sm font-bold pb-2 border-b border-gray-100" style={{ color: getRiskColor(sev, 1) }}>
                    <AlertTriangle className="w-4 h-4 mr-1.5" />
                    {sev === 'high' ? 'High' : (sev === 'warning' ? 'Medium' : 'Low')}
                    <span className="ml-2 text-xs text-gray-400 font-normal">{findingsGrouped[sev].length} findings</span>
                  </div>
                  
                  {findingsGrouped[sev].map((h, i) => {
                    // find parent function
                    const func = annotations.functions.find(f => h.start_line >= f.start_line && h.start_line <= f.end_line);
                    return (
                      <div key={i} className="bg-white border border-gray-200 rounded-md p-3 shadow-sm hover:border-gray-300 transition-colors">
                        <div className="flex justify-between items-start mb-1">
                          <span className="font-bold text-gray-800 text-sm">{func?.name || 'Global scope'}</span>
                          <span className="text-xs text-gray-400 font-mono">L{h.start_line}</span>
                        </div>
                        <p className="text-xs text-gray-600 mb-3 leading-relaxed">{h.message}</p>
                        <button onClick={() => scrollToLine(h.start_line)} className="text-indigo-600 hover:text-indigo-800 text-xs font-medium flex items-center">
                          <span className="font-mono mr-1">&lt;/&gt;</span> Go to line {h.start_line}
                        </button>
                      </div>
                    );
                  })}
                </div>
              )
            ))}
            {filteredHotspots.length === 0 && (
              <div className="text-center py-8 text-sm text-gray-500">
                No findings match the current filter.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
