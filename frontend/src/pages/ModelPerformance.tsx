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
        if (err.response?.status === 404) {
          setModelData(null);
        } else {
          console.error(err);
          setError("Failed to load model performance data.");
        }
      } finally {
        setLoading(false);
      }
    };
    fetchModelInfo();
  }, []);

  if (loading) return <div className="p-8 text-center text-gray-500 dark:text-gray-400">Loading model performance...</div>;
  if (error) return <div className="p-8 text-center text-red-500">{error}</div>;

  if (!modelData) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-w-0 p-8 h-full overflow-hidden">
        <Activity className="w-16 h-16 text-gray-300 dark:text-gray-600 mb-4" />
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200">Model not trained</h2>
        <p className="text-gray-500 dark:text-gray-400 mt-2 text-center max-w-md">
          There is no active model trained on the dataset yet. Please complete the data extraction and training process.
        </p>
      </div>
    );
  }

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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
                {modelData?.metadata?.metrics && Object.entries(modelData.metadata.metrics).map(([key, value]) => {
                  if (key === 'confusion_matrix') return null; // Rendered separately
                  return (
                    <tr key={key}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{key.replace(/_/g, ' ').toUpperCase()}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {typeof value === 'number' ? value.toFixed(4) : String(value)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          
          {modelData?.metadata?.metrics?.confusion_matrix && (
            <div className="mt-8">
              <h3 className="text-md font-bold text-slate-800 dark:text-white mb-3">Confusion Matrix</h3>
              <div className="grid grid-cols-3 gap-2 text-center text-sm max-w-sm">
                <div></div>
                <div className="font-semibold text-gray-600 dark:text-gray-400">Pred: Clean</div>
                <div className="font-semibold text-gray-600 dark:text-gray-400">Pred: Buggy</div>
                
                <div className="font-semibold text-gray-600 dark:text-gray-400 text-right pr-2">Actual: Clean</div>
                <div className="bg-green-100 dark:bg-green-900/30 p-2 rounded text-gray-900 dark:text-white border border-green-200 dark:border-green-800">
                  {modelData.metadata.metrics.confusion_matrix[0][0]} <br/><span className="text-xs text-gray-500">(TN)</span>
                </div>
                <div className="bg-red-100 dark:bg-red-900/30 p-2 rounded text-gray-900 dark:text-white border border-red-200 dark:border-red-800">
                  {modelData.metadata.metrics.confusion_matrix[0][1]} <br/><span className="text-xs text-gray-500">(FP)</span>
                </div>
                
                <div className="font-semibold text-gray-600 dark:text-gray-400 text-right pr-2">Actual: Buggy</div>
                <div className="bg-orange-100 dark:bg-orange-900/30 p-2 rounded text-gray-900 dark:text-white border border-orange-200 dark:border-orange-800">
                  {modelData.metadata.metrics.confusion_matrix[1][0]} <br/><span className="text-xs text-gray-500">(FN)</span>
                </div>
                <div className="bg-blue-100 dark:bg-blue-900/30 p-2 rounded text-gray-900 dark:text-white border border-blue-200 dark:border-blue-800">
                  {modelData.metadata.metrics.confusion_matrix[1][1]} <br/><span className="text-xs text-gray-500">(TP)</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {modelData?.metadata?.feature_importance && (
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-bold text-slate-800 dark:text-white mb-4">Feature Importance</h2>
            <div className="space-y-4">
              {Object.entries(modelData.metadata.feature_importance)
                .sort(([, a], [, b]) => Number(b) - Number(a))
                .slice(0, 10)
                .map(([feature, importance]) => {
                  const numImportance = Number(importance);
                  const maxImportance = Math.max(...Object.values(modelData.metadata.feature_importance).map(Number));
                  const percent = maxImportance > 0 ? (numImportance / maxImportance) * 100 : 0;
                  return (
                    <div key={feature}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-700 dark:text-gray-300 font-medium">{feature.replace(/_/g, ' ')}</span>
                        <span className="text-gray-500">{numImportance.toFixed(4)}</span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div className="bg-indigo-500 h-2 rounded-full" style={{ width: `${percent}%` }}></div>
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
