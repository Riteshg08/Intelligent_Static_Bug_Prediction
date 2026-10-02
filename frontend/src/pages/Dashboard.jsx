import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [file, setFile] = useState(null);
  const [name, setName] = useState('');
  const navigate = useNavigate();

  const token = localStorage.getItem('token');

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchProjects();
  }, [token, navigate]);

  const fetchProjects = async () => {
    const res = await axios.get('/api/v1/projects', {
      headers: { Authorization: `Bearer ${token}` }
    });
    setProjects(res.data);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('name', name);
    formData.append('file', file);
    await axios.post('/api/v1/projects', formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    });
    setName('');
    setFile(null);
    fetchProjects();
  };

  const startAnalysis = async (projectId) => {
    const res = await axios.post(`/api/v1/projects/${projectId}/analyze`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    navigate(`/analysis/${res.data.run_id}`);
  };

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Projects</h1>
      
      <div className="bg-white shadow overflow-hidden sm:rounded-md mb-8 p-6">
        <h2 className="text-lg font-medium mb-4">Upload New Codebase</h2>
        <form onSubmit={handleUpload} className="flex gap-4 items-end">
          <div>
            <label className="block text-sm font-medium text-gray-700">Project Name</label>
            <input type="text" required value={name} onChange={e => setName(e.target.value)} className="mt-1 p-2 border rounded-md" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Zip/Tar File</label>
            <input type="file" required onChange={e => setFile(e.target.files[0])} className="mt-1" />
          </div>
          <button type="submit" className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700">Upload</button>
        </form>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {projects.map(project => (
            <li key={project.id} className="px-6 py-4 flex justify-between items-center hover:bg-gray-50">
              <span className="font-medium text-gray-900">{project.name}</span>
              <button onClick={() => startAnalysis(project.id)} className="text-indigo-600 hover:text-indigo-900 font-medium">Analyze</button>
            </li>
          ))}
          {projects.length === 0 && <li className="px-6 py-4 text-gray-500">No projects found.</li>}
        </ul>
      </div>
    </div>
  );
}
