import React, { useEffect, useState } from 'react';
import api from '../lib/api';
import { Activity, ShieldCheck, TrendingUp, Info } from 'lucide-react';

export default function ModelPerformance() {
  const [modelData, setModelData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchModelInfo = async () => {
      try {
        const res = await api.get('/models/current');
        setModelData(res.data);
      } catch (err) {
        console.error(err);
        setError("Failed to load model performance data.");
      } finally {
        setLoading(false);
      }
    };
    fetchModelInfo();
  }, []);

  if (loading) return <div className="p-8 text-center text-gray-500 dark:text-gray-400">Loading model performance...</div>;
  if (error) return <div className="p-8 text-center text-red-500">{error}</div>;

  return (
    <div className="flex-1 flex flex-col min-w-0 p-8 pt-6 overflow-y-auto">
      <div className="flex items-center text-sm text-gray-500 dark:text-gray-400 mb-2">
        <span>Workspace</span>
        <span className="mx-2">&gt;</span>
        <span className="text-gray-900 dark:text-white font-medium">Model Performance</span>
      </div>
      
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-slate-800 dark:text-white">Model Performance</h1>
      </div>

      <div className="bg-blue-50 dark:bg-blue-900/30 border-l-4 border-blue-500 p-4 rounded-r-md flex mb-8 text-sm">
        <Info className="w-5 h-5 text-blue-500 mr-2 shrink-0" />
        <span className="text-blue-900 dark:text-blue-200">
          This dashboard shows the current metrics of the active BugSight prediction model. 
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-between">
          <div className="flex justify-between items-start mb-2">
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Active Model</span>
            <ShieldCheck className="w-5 h-5 text-indigo-500" />
          </div>
          <div className="text-xl font-bold text-slate-800 dark:text-white break-all">{modelData?.active_model || 'Unknown'}</div>
          <div className="text-xs text-gray-400 mt-2">Latest deployed version</div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-between">
          <div className="flex justify-between items-start mb-2">
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Last Trained</span>
            <Activity className="w-5 h-5 text-green-500" />
          </div>
          <div className="text-xl font-bold text-slate-800 dark:text-white">
            {modelData?.metadata?.training_date ? new Date(modelData.metadata.training_date).toLocaleDateString() : 'Unknown'}
          </div>
          <div className="text-xs text-gray-400 mt-2">Time of last model update</div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-between">
          <div className="flex justify-between items-start mb-2">
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Test AUC</span>
            <TrendingUp className="w-5 h-5 text-amber-500" />
          </div>
          <div className="text-xl font-bold text-slate-800 dark:text-white">
            {modelData?.metadata?.metrics?.roc_auc ? (modelData.metadata.metrics.roc_auc * 100).toFixed(2) + '%' : 'N/A'}
          </div>
          <div className="text-xs text-gray-400 mt-2">Area Under Curve metric</div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-bold text-slate-800 dark:text-white mb-4">Detailed Metrics</h2>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Metric</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Value</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200">
              {modelData?.metadata?.metrics && Object.entries(modelData.metadata.metrics).map(([key, value]) => (
                <tr key={key}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{key.replace(/_/g, ' ')}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {typeof value === 'number' ? value.toFixed(4) : value}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
