'use client';

import { usePortfolio } from '@/hooks/usePortfolio';
import { useAnalysis } from '@/hooks/useAnalysis';
import { useRouter } from 'next/navigation';

export default function AnalysisPage() {
  const router = useRouter();
  const { holdings } = usePortfolio();
  const { data: analysis, loading, error, refresh } = useAnalysis(holdings);

  if (holdings.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">No Holdings to Analyze</h1>
          <p className="text-gray-600 mb-8">Import your portfolio first.</p>
          <button
            onClick={() => router.push('/import')}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition"
          >
            Import Portfolio
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Analyzing portfolio...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Analysis Failed</h1>
          <p className="text-gray-600 mb-8">{error.message}</p>
          <button
            onClick={refresh}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Portfolio Analysis</h1>
          <button
            onClick={refresh}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition"
          >
            Refresh
          </button>
        </div>

        {/* Risk Score */}
        <div className="bg-white rounded-xl shadow-sm p-8 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Risk Score</h2>
          <div className="flex items-center justify-center">
            <div className="relative w-48 h-48">
              <svg className="w-full h-full" viewBox="0 0 100 100">
                <circle
                  className="text-gray-200"
                  strokeWidth="8"
                  stroke="currentColor"
                  fill="transparent"
                  r="42"
                  cx="50"
                  cy="50"
                />
                <circle
                  className={
                    analysis.risk_score < 40 ? 'text-green-500' :
                    analysis.risk_score < 70 ? 'text-yellow-500' : 'text-red-500'
                  }
                  strokeWidth="8"
                  strokeDasharray={`${2 * Math.PI * 42}`}
                  strokeDashoffset={`${2 * Math.PI * 42 * (1 - analysis.risk_score / 100)}`}
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="transparent"
                  r="42"
                  cx="50"
                  cy="50"
                  transform="rotate(-90 50 50)"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center flex-col">
                <span className={`text-4xl font-bold ${
                  analysis.risk_score < 40 ? 'text-green-500' :
                  analysis.risk_score < 70 ? 'text-yellow-500' : 'text-red-500'
                }`}>
                  {analysis.risk_score}
                </span>
                <span className="text-sm text-gray-500">/ 100</span>
              </div>
            </div>
          </div>
          <div className="mt-6 grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-sm text-gray-600">Concentration</p>
              <p className="text-xl font-semibold text-gray-900">{analysis.risk_breakdown.concentration}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Volatility</p>
              <p className="text-xl font-semibold text-gray-900">{analysis.risk_breakdown.volatility}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Correlation</p>
              <p className="text-xl font-semibold text-gray-900">{analysis.risk_breakdown.correlation}</p>
            </div>
          </div>
        </div>

        {/* Warnings */}
        {analysis.warnings.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Warnings</h2>
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
                  {warning.affected_symbols.length > 0 && (
                    <p className="text-sm text-gray-600 mt-2">
                      Affected: {warning.affected_symbols.join(', ')}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Blind Spots */}
        {analysis.blind_spots.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Blind Spots</h2>
            <div className="space-y-4">
              {analysis.blind_spots.map((spot, idx) => (
                <div key={idx} className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium text-purple-900">{spot.message}</p>
                      <p className="text-sm text-purple-700 mt-1">
                        Confidence: {spot.confidence}%
                      </p>
                      {spot.affected_symbols.length > 0 && (
                        <p className="text-sm text-purple-600 mt-2">
                          Affected: {spot.affected_symbols.join(', ')}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {analysis.recommendations.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recommendations</h2>
            <div className="space-y-3">
              {analysis.recommendations.map((rec, idx) => (
                <div key={idx} className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium text-blue-900">
                        {rec.action.toUpperCase()} {rec.quantity} {rec.symbol}
                      </p>
                      <p className="text-sm text-blue-700 mt-1">{rec.reason}</p>
                      <p className="text-xs text-blue-600 mt-2">
                        Expected Impact: {rec.expected_impact}
                      </p>
                    </div>
                    <span className="bg-blue-600 text-white text-xs font-medium px-2 py-1 rounded">
                      Priority {rec.priority}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Allocation */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Asset Allocation</h2>
            <div className="space-y-2">
              {Object.entries(analysis.allocation).map(([assetClass, pct]) => (
                <div key={assetClass}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-700 capitalize">{assetClass}</span>
                    <span className="text-gray-900 font-medium">{pct.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Sector Allocation</h2>
            <div className="space-y-2">
              {Object.entries(analysis.sector_allocation).map(([sector, pct]) => (
                <div key={sector}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-700">{sector}</span>
                    <span className="text-gray-900 font-medium">{pct.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
