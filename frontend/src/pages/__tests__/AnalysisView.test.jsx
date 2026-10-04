import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import AnalysisView from '../AnalysisView';
import axios from 'axios';

vi.mock('axios');

describe('AnalysisView E2E-like flow', () => {
  it('opens AnalysisView, verifies risk colors, and has link to FileViewer', async () => {
    // Mock the status endpoint
    axios.get.mockImplementation((url) => {
      if (url.includes('/status')) {
        return Promise.resolve({ data: { status: 'completed' } });
      }
      if (url.includes('/predictions')) {
        return Promise.resolve({
          data: [
            {
              id: 1,
              run_id: 10,
              file_id: 20,
              function_name: 'test_func',
              language: 'Python',
              risk_score: 0.9,
              risk_level: 'High'
            },
            {
              id: 2,
              run_id: 10,
              file_id: 21,
              function_name: 'safe_func',
              language: 'Python',
              risk_score: 0.1,
              risk_level: 'Low'
            }
          ]
        });
      }
      return Promise.reject(new Error('not found'));
    });

    render(
      <MemoryRouter initialEntries={['/analysis/10']}>
        <Routes>
          <Route path="/analysis/:runId" element={<AnalysisView />} />
        </Routes>
      </MemoryRouter>
    );

    // Wait for predictions to load
    await waitFor(() => {
      expect(screen.getByText('test_func')).toBeDefined();
    });

    // Verify risk colors/labels
    expect(screen.getByText('High Risk')).toBeDefined();
    expect(screen.getByText('Low Risk')).toBeDefined();

    // Verify link to FileViewer
    const link = screen.getByText('test_func').closest('a');
    expect(link.getAttribute('href')).toBe('/runs/10/files/20#test_func');
  });
});
