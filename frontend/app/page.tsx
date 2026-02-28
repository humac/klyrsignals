'use client';

import { usePortfolio } from '@/hooks/usePortfolio';
import { useAnalysis } from '@/hooks/useAnalysis';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';

export default function DashboardPage() {
  const searchParams = useSearchParams();
  const { holdings, totalValue, lastUpdated, importHoldings } = usePortfolio();
  const { data: analysis, loading, error } = useAnalysis(holdings);

  const loadDemoData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/mock/load', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      localStorage.setItem('klyrsignals_portfolio', JSON.stringify({
        holdings: data.portfolio.holdings,
        lastUpdated: new Date().toISOString()
      }));
      localStorage.setItem('analysis', JSON.stringify(data.analysis));
      window.location.reload();
    } catch (err) {
      console.error('Failed to load demo data:', err);
      alert('Failed to load demo data. Make sure backend is running.');
    }
  };

  if (holdings.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Welcome to KlyrSignals</h1>
          <p className="text-gray-600 mb-8">
            AI-powered portfolio analysis to detect blind spots and over-exposure risks.
          </p>
          <div className="space-y-4">
            <Link
              href="/import"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition"
            >
              Import Your Portfolio
            </Link>
            {searchParams.get('demo') === 'true' && (
              <div>
                <button
                  onClick={loadDemoData}
                  className="inline-block bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 transition"
                >
                  📊 Load Demo Data
                </button>
                <p className="text-sm text-gray-500 mt-2">Load a $250k demo portfolio for testing</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            {lastUpdated ? `Last updated: ${lastUpdated.toLocaleString()}` : 'No recent updates'}
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Total Value */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-sm font-medium text-gray-600 mb-2">Total Value</h2>
            <p className="text-3xl font-bold text-gray-900">
              ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
          </div>

          {/* Risk Score */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-sm font-medium text-gray-600 mb-2">Risk Score</h2>
            {loading ? (
              <p className="text-3xl font-bold text-gray-400">Loading...</p>
            ) : error ? (
              <p className="text-3xl font-bold text-red-500">Error</p>
            ) : analysis ? (
              <div>
                <p className={`text-3xl font-bold ${
                  analysis.risk_score < 40 ? 'text-green-500' :
                  analysis.risk_score < 70 ? 'text-yellow-500' : 'text-red-500'
                }`}>
                  {analysis.risk_score}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  {analysis.risk_score < 40 ? 'Low Risk' :
                   analysis.risk_score < 70 ? 'Medium Risk' : 'High Risk'}
                </p>
              </div>
            ) : (
              <p className="text-3xl font-bold text-gray-400">N/A</p>
            )}
          </div>

          {/* Holdings Count */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-sm font-medium text-gray-600 mb-2">Holdings</h2>
            <p className="text-3xl font-bold text-gray-900">{holdings.length}</p>
            <p className="text-sm text-gray-500 mt-1">positions</p>
          </div>
        </div>

        {/* Warnings */}
        {analysis && analysis.warnings.length > 0 && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Warnings</h2>
            <div className="space-y-3">
              {analysis.warnings.map((warning, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border-l-4 ${
                    warning.severity === 'critical' ? 'bg-red-50 border-red-500' :
                    warning.severity === 'high' ? 'bg-orange-50 border-orange-500' :
                    'bg-yellow-50 border-yellow-500'
                  }`}
                >
                  <p className={`font-medium ${
                    warning.severity === 'critical' ? 'text-red-800' :
                    warning.severity === 'high' ? 'text-orange-800' : 'text-yellow-800'
                  }`}>
                    {warning.message}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            href="/import"
            className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition text-center"
          >
            <h3 className="font-semibold text-gray-900">Add Holdings</h3>
            <p className="text-sm text-gray-600 mt-1">Import or manually add</p>
          </Link>
          <Link
            href="/holdings"
            className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition text-center"
          >
            <h3 className="font-semibold text-gray-900">View All</h3>
            <p className="text-sm text-gray-600 mt-1">Manage positions</p>
          </Link>
          <Link
            href="/analysis"
            className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition text-center"
          >
            <h3 className="font-semibold text-gray-900">Full Analysis</h3>
            <p className="text-sm text-gray-600 mt-1">Deep dive insights</p>
          </Link>
        </div>
      </div>
    </div>
  );
}
