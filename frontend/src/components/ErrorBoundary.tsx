import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export default class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-red-50 dark:bg-red-900 px-4">
          <div className="max-w-md w-full space-y-8 text-center p-6 bg-white dark:bg-gray-800 rounded-lg shadow-xl">
            <h2 className="text-2xl font-bold text-red-600 dark:text-red-400">Something went wrong</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">{this.state.error?.message || "An unexpected error occurred."}</p>
            <button
              onClick={() => window.location.href = '/projects'}
              className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
            >
              Return Home
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
