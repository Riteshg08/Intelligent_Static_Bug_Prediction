import React, { useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../lib/api';
import { UploadCloud, X, AlertCircle } from 'lucide-react';

export default function UploadModal({ onClose }) {
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const allowedExtensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.c', '.h', '.cpp', '.hpp', '.cc', '.cs', '.zip', '.tar.gz', '.tgz'];

  const validateFile = (f: File) => {
    const ext = f.name.substring(f.name.lastIndexOf('.')).toLowerCase();
    const isTarGz = f.name.toLowerCase().endsWith('.tar.gz');
    
    let valid = false;
    if (isTarGz) valid = true;
    else if (allowedExtensions.includes(ext)) valid = true;

    if (!valid) {
      setError(`Invalid file type. Allowed: ${allowedExtensions.join(', ')}`);
      return false;
    }
    
    // 50MB max upload size
    if (f.size > 50 * 1024 * 1024) {
      setError('File is too large (max 50MB).');
      return false;
    }
    
    setError(null);
    return true;
  };

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      if (validateFile(droppedFile)) {
        setFile(droppedFile);
        if (!name) setName(droppedFile.name.split('.')[0]);
      }
    }
  }, [name]);

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
        if (!name) setName(selectedFile.name.split('.')[0]);
      }
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || !name) {
      setError("Project name and file are required.");
      return;
    }
    
    setLoading(true);
    setProgress(10);
    const formData = new FormData();
    formData.append('name', name);
    formData.append('file', file);
    
    try {
      const res = await api.post('/projects', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const p = Math.round((progressEvent.loaded * 100) / (progressEvent.total || file.size));
          setProgress(p);
        }
      });
      
      const projectId = res.data.id;
      
      // Start analysis right away
      api.post(`/projects/${projectId}/analyze`).catch(err => {
        console.error("Failed to start analysis:", err);
      });
      
      onClose();
      navigate(`/projects/${projectId}`);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to upload project");
      setLoading(false);
      setProgress(0);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" onClick={onClose}></div>

        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <div className="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-xl sm:w-full">
          <div className="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4 relative">
            
            <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 focus:outline-none">
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-xl leading-6 font-bold text-gray-900 dark:text-white mb-6" id="modal-title">
              Upload Codebase
            </h3>
            
            {error && (
              <div className="mb-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-md p-3 flex items-start">
                <AlertCircle className="w-5 h-5 text-red-500 mr-2 shrink-0 mt-0.5" />
                <span className="text-sm text-red-700 dark:text-red-300">{error}</span>
              </div>
            )}

            <form onSubmit={handleUpload}>
              <div className="mb-5">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Project Name</label>
                <input 
                  type="text" 
                  required 
                  value={name} 
                  onChange={e => setName(e.target.value)} 
                  placeholder="e.g. my-awesome-project"
                  className="p-2.5 border border-gray-300 dark:border-gray-600 rounded-md w-full bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" 
                />
              </div>
              
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Source Code</label>
                
                <div 
                  className={`mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-lg transition-colors ${
                    isDragging ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20' : 
                    file ? 'border-green-400 bg-green-50 dark:bg-green-900/10' :
                    'border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => !file && fileInputRef.current?.click()}
                  style={{ cursor: file ? 'default' : 'pointer' }}
                >
                  <div className="space-y-2 text-center">
                    <UploadCloud className={`mx-auto h-12 w-12 ${file ? 'text-green-500' : 'text-gray-400'}`} />
                    
                    {file ? (
                      <div className="flex flex-col items-center">
                        <span className="text-sm font-medium text-gray-900 dark:text-white">{file.name}</span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">{(file.size / (1024 * 1024)).toFixed(2)} MB</span>
                        <button 
                          type="button" 
                          onClick={(e) => { e.stopPropagation(); setFile(null); }}
                          className="mt-3 text-sm text-red-500 hover:text-red-700 font-medium"
                        >
                          Remove file
                        </button>
                      </div>
                    ) : (
                      <>
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                          <label htmlFor="file-upload" className="relative cursor-pointer bg-white dark:bg-gray-800 rounded-md font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 focus-within:outline-none">
                            <span>Upload a file</span>
                            <input 
                              id="file-upload" 
                              name="file-upload" 
                              type="file" 
                              className="sr-only"
                              ref={fileInputRef}
                              onChange={handleFileSelect}
                            />
                          </label>
                          <span className="pl-1">or drag and drop</span>
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                          ZIP, TAR.GZ or single source file up to 50MB
                        </p>
                        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1 max-w-xs mx-auto">
                          Valid types: {allowedExtensions.join(', ')}
                        </p>
                      </>
                    )}
                  </div>
                </div>
              </div>
              
              {loading && progress > 0 && (
                <div className="mb-6">
                  <div className="flex justify-between text-xs mb-1 text-gray-600 dark:text-gray-300">
                    <span>Uploading...</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="bg-indigo-600 h-2 rounded-full transition-all duration-300" style={{ width: `${progress}%` }}></div>
                  </div>
                </div>
              )}
              
              <div className="mt-5 sm:mt-6 sm:flex sm:flex-row-reverse gap-3">
                <button 
                  type="submit" 
                  disabled={loading || !file || !name}
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? 'Processing...' : 'Upload & Analyze'}
                </button>
                <button 
                  type="button" 
                  onClick={onClose}
                  disabled={loading}
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 dark:border-gray-600 shadow-sm px-4 py-2 bg-white dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none sm:mt-0 sm:w-auto sm:text-sm"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
