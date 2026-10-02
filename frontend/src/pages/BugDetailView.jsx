import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import { Check, X } from 'lucide-react';

export default function BugDetailView() {
  const { id } = useParams();
  const [report, setReport] = useState(null);
  const [feedbackSaved, setFeedbackSaved] = useState(false);
  const token = localStorage.getItem('token');

  useEffect(() => {
    fetchReport();
  }, []);

  const fetchReport = async () => {
    const res = await axios.get(`/api/v1/predictions/${id}/report`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setReport(res.data);
  };

  const submitFeedback = async (isBug) => {
    await axios.post(`/api/v1/predictions/${id}/feedback?is_real_bug=${isBug}`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setFeedbackSaved(true);
  };

  if (!report) return <div className="p-8 text-center text-gray-500">Loading...</div>;

  const reasons = JSON.parse(report.explanation_json || "[]");

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <h1 className="text-2xl font-semibold text-gray-900 mb-2">Function: {report.function_name}</h1>
      <p className="text-gray-500 mb-6">File: {report.file.path} | Language: {report.language}</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white shadow rounded-md p-6">
          <h2 className="text-lg font-medium mb-4">Risk Assessment</h2>
          <div className="flex items-center gap-4 mb-4">
            <div className="text-3xl font-bold text-gray-900">{(report.risk_score * 100).toFixed(1)}%</div>
            <div className={`px-3 py-1 rounded text-sm font-medium ${
              report.risk_level === 'High' ? 'bg-red-100 text-red-800' : 
              report.risk_level === 'Medium' ? 'bg-yellow-100 text-yellow-800' : 
              'bg-green-100 text-green-800'
            }`}>
              {report.risk_level} Risk
            </div>
          </div>
          
          <h3 className="font-medium text-gray-700 mt-6 mb-2">Explanations</h3>
          <ul className="list-disc pl-5 space-y-2 text-gray-600">
            {reasons.map((r, idx) => (
              <li key={idx}>{r}</li>
            ))}
          </ul>
          
          <div className="mt-6 p-4 bg-gray-50 rounded text-sm text-gray-600">
            <strong>Note:</strong> {report.confidence_note}
          </div>
        </div>
        
        <div className="bg-white shadow rounded-md p-6">
          <h2 className="text-lg font-medium mb-4">Feedback</h2>
          {feedbackSaved ? (
            <div className="text-green-600 flex items-center gap-2">
              <Check /> Feedback saved successfully. Thank you!
            </div>
          ) : (
            <div>
              <p className="text-gray-600 mb-4">Is this actually a bug or highly risky code?</p>
              <div className="flex gap-4">
                <button onClick={() => submitFeedback(true)} className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">
                  <Check size={16}/> Yes, it's a bug
                </button>
                <button onClick={() => submitFeedback(false)} className="flex items-center gap-2 bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700">
                  <X size={16}/> No, false positive
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
