'use client';

import { usePortfolio } from '@/hooks/usePortfolio';
import { useState } from 'react';

export default function SettingsPage() {
  const { holdings, clearPortfolio } = usePortfolio();
  const [showConfirm, setShowConfirm] = useState(false);

  const handleExport = () => {
    const csv = [
      ['symbol', 'quantity', 'purchase_price', 'purchase_date', 'asset_class'].join(','),
      ...holdings.map(h =>
        [h.symbol, h.quantity, h.purchase_price, h.purchase_date || '', h.asset_class || 'stock'].join(',')
      ),
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'klyrsignals_portfolio.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleClear = () => {
    if (showConfirm) {
      clearPortfolio();
      setShowConfirm(false);
    } else {
      setShowConfirm(true);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>

        {/* Data Management */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Data Management</h2>
          
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600 mb-2">Current Holdings: {holdings.length}</p>
              <button
                onClick={handleExport}
                disabled={holdings.length === 0}
                className="bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                Export to CSV
              </button>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-2">Clear all portfolio data</p>
              <button
                onClick={handleClear}
                disabled={holdings.length === 0}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  showConfirm
                    ? 'bg-red-600 text-white hover:bg-red-700'
                    : 'bg-red-100 text-red-700 hover:bg-red-200'
                } disabled:bg-gray-400 disabled:cursor-not-allowed`}
              >
                {showConfirm ? 'Click again to confirm' : 'Clear Portfolio'}
              </button>
              {showConfirm && (
                <p className="text-sm text-red-600 mt-2">
                  This action cannot be undone. All holdings will be permanently deleted.
                </p>
              )}
            </div>
          </div>
        </div>

        {/* About */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">About KlyrSignals</h2>
          <div className="space-y-2 text-sm text-gray-600">
            <p><strong>Version:</strong> 1.0.0</p>
            <p><strong>Build:</strong> 2026-02-28</p>
            <p>
              <strong>Description:</strong> AI-powered financial portfolio analyst for blind spot 
              detection and over-exposure warnings.
            </p>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-yellow-900 mb-3">⚠️ Investment Disclaimer</h2>
          <p className="text-sm text-yellow-800 leading-relaxed">
            KlyrSignals provides portfolio analysis and insights only. We are not a registered 
            investment advisor. The information provided should not be considered as investment 
            advice or a recommendation to buy or sell any security. All investments involve risk, 
            including the potential loss of principal. Past performance does not guarantee future 
            results. Please consult with a qualified financial advisor before making any investment 
            decisions.
          </p>
        </div>
      </div>
    </div>
  );
}
