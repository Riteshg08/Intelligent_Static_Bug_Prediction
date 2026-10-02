import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, Link } from 'react-router-dom';
import { AlertTriangle, ShieldCheck, Activity } from 'lucide-react';

export default function AnalysisView() {
  const { runId } = useParams();
  const [status, setStatus] = useState('queued');
  const [predictions, setPredictions] = useState([]);
  const token = localStorage.getItem('token');

  useEffect(() => {
    let interval;
    if (status === 'queued' || status === 'running') {
      interval = setInterval(checkStatus, 3000);
    }
    return () => clearInterval(interval);
  }, [status]);

  useEffect(() => {
    if (status === 'completed') {
      fetchPredictions();
    }
  }, [status]);

  const checkStatus = async () => {
    const res = await axios.get(`/api/v1/analysis/${runId}/status`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setStatus(res.data.status);
  };

  const fetchPredictions = async () => {
    const res = await axios.get(`/api/v1/analysis/${runId}/predictions`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setPredictions(res.data.sort((a, b) => b.risk_score - a.risk_score));
  };

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
        <Activity className="text-indigo-600" /> Analysis Run #{runId}
      </h1>
      
      <div className="bg-white p-6 rounded-md shadow mb-6">
        <h2 className="text-lg font-medium mb-2">Status: <span className="capitalize">{status}</span></h2>
        {(status === 'queued' || status === 'running') && (
          <div className="w-full bg-gray-200 rounded-full h-2.5 mt-4">
            <div className="bg-indigo-600 h-2.5 rounded-full" style={{ width: status === 'queued' ? '20%' : '60%' }}></div>
          </div>
        )}
      </div>

      {status === 'completed' && (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {predictions.map(pred => (
              <li key={pred.id} className="px-6 py-4 hover:bg-gray-50 flex justify-between items-center">
                <div>
                  <Link to={`/prediction/${pred.id}`} className="font-medium text-indigo-600 hover:underline">
                    {pred.function_name} <span className="text-sm text-gray-500">({pred.language})</span>
                  </Link>
                  <div className="text-sm text-gray-500 mt-1">Score: {(pred.risk_score * 100).toFixed(1)}%</div>
                </div>
                <div>
                  {pred.risk_level === 'High' && <span className="inline-flex items-center gap-1 text-red-600 bg-red-50 px-2 py-1 rounded"><AlertTriangle size={16}/> High Risk</span>}
                  {pred.risk_level === 'Medium' && <span className="inline-flex items-center gap-1 text-yellow-600 bg-yellow-50 px-2 py-1 rounded"><AlertTriangle size={16}/> Medium Risk</span>}
                  {pred.risk_level === 'Low' && <span className="inline-flex items-center gap-1 text-green-600 bg-green-50 px-2 py-1 rounded"><ShieldCheck size={16}/> Low Risk</span>}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
