/// <reference types="vite/client" />
import axios from 'axios';

export interface Project {
  id: number;
  name: string;
  languages: string[];
  risk_counts: {
    high: number;
    medium: number;
    low: number;
  };
  function_count: number;
  last_updated: string | null;
  latest_run_id: number | null;
}

export interface Prediction {
  id: number;
  function_name: string;
  language: string;
  start_line: number;
  end_line: number;
  risk_score: number;
  risk_level: string;
  file_id: number;
  file_path: string;
}

export interface PredictionReport {
  id: number;
  function_name: string;
  language: string;
  risk_score: number;
  risk_level: string;
  confidence_note: string;
  explanation: Record<string, any>;
  hotspots: Array<{
    severity: string;
    rule_id: string;
    message: string;
    start_line: number;
    end_line: number;
  }>;
  file_id: number;
}

export interface FileData {
  id: number;
  path: string;
  language: string;
  line_count: number;
  status: string;
  risk_level: string;
}

export interface AnalysisFile {
  id: number;
  path: string;
  language: string;
  max_risk_score: number;
  risk_counts: {
    high: number;
    medium: number;
    low: number;
  };
}

export interface FunctionAnnotation {
  id: number;
  name: string;
  start_line: number;
  end_line: number;
  risk_score: number;
  risk_level: string;
}

export interface Hotspot {
  id: number;
  start_line: number;
  end_line: number;
  severity: string;
  rule_id: string;
  message: string;
}

export interface AnnotationsResponse {
  functions: FunctionAnnotation[];
  hotspots: Hotspot[];
}

export interface ProjectFilesResponse {
  run_id: number | null;
  run_status: string | null;
  files: FileData[];
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface ExportResponse {
  run_id: number;
  project_id: number;
  findings: PredictionReport[];
}

export interface LanguagesResponse {
  languages: string[];
}


const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1'
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
