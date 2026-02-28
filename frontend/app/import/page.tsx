'use client';

import { useState } from 'react';
import { usePortfolio } from '@/hooks/usePortfolio';
import { Holding } from '@/types/portfolio';
import { useRouter } from 'next/navigation';

export default function ImportPage() {
  const router = useRouter();
  const { importHoldings } = usePortfolio();
  const [step, setStep] = useState<'upload' | 'preview' | 'confirm'>('upload');
  const [parsedHoldings, setParsedHoldings] = useState<Holding[]>([]);
  const [csvText, setCsvText] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Manual entry form
  const [manualHolding, setManualHolding] = useState<Partial<Holding>>({
    asset_class: 'stock',
  });

  const parseCSV = (text: string) => {
    try {
      const lines = text.trim().split('\n');
      if (lines.length < 2) {
        throw new Error('CSV must have header row and at least one data row');
      }

      const headers = lines[0].toLowerCase().split(',').map(h => h.trim());
      const holdings: Holding[] = [];

      for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => v.trim());
        if (values.length < 2) continue;

        const row: Record<string, string> = {};
        headers.forEach((header, idx) => {
          if (idx < values.length) {
            row[header] = values[idx];
          }
        });

        const symbol = row.symbol || row.ticker || row[0];
        const quantity = parseFloat(row.quantity || row.shares || row[1] || '0');
        const purchasePrice = parseFloat(row.purchase_price || row.price || row.cost || row[2] || '0');

        if (symbol && quantity > 0 && purchasePrice > 0) {
          holdings.push({
            symbol: symbol.toUpperCase(),
            quantity,
            purchase_price: purchasePrice,
            purchase_date: row.purchase_date || row.date || undefined,
            asset_class: (row.asset_class as any) || 'stock',
          });
        }
      }

      if (holdings.length === 0) {
        throw new Error('No valid holdings found in CSV');
      }

      return holdings;
    } catch (err) {
      throw err;
    }
  };

  const handleCSVUpload = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value;
    setCsvText(text);
    setError(null);
  };

  const handlePreview = () => {
    try {
      const holdings = parseCSV(csvText);
      setParsedHoldings(holdings);
      setStep('preview');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to parse CSV');
    }
  };

  const handleManualAdd = () => {
    if (!manualHolding.symbol || !manualHolding.quantity || !manualHolding.purchase_price) {
      setError('Please fill in all required fields');
      return;
    }

    const newHolding: Holding = {
      symbol: manualHolding.symbol.toUpperCase(),
      quantity: manualHolding.quantity,
      purchase_price: manualHolding.purchase_price,
      purchase_date: manualHolding.purchase_date,
      asset_class: manualHolding.asset_class as any || 'stock',
    };

    setParsedHoldings([newHolding]);
    setStep('preview');
    setError(null);
  };

  const handleImport = () => {
    importHoldings(parsedHoldings);
    setStep('confirm');
  };

  if (step === 'confirm') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="text-6xl mb-4">✅</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Portfolio Imported!</h1>
          <p className="text-gray-600 mb-8">
            Successfully imported {parsedHoldings.length} holding{parsedHoldings.length !== 1 ? 's' : ''}.
          </p>
          <button
            onClick={() => router.push('/')}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Import Portfolio</h1>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
            {error}
          </div>
        )}

        {step === 'upload' && (
          <div className="space-y-8">
            {/* CSV Import */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">CSV Import</h2>
              <p className="text-gray-600 mb-4">
                Paste your CSV data below. Expected format: symbol, quantity, purchase_price
              </p>
              <textarea
                value={csvText}
                onChange={handleCSVUpload}
                placeholder="symbol,quantity,purchase_price,purchase_date&#10;AAPL,50,150.00,2024-01-15&#10;MSFT,30,280.00,2024-02-20"
                className="w-full h-48 p-4 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                onClick={handlePreview}
                disabled={!csvText.trim()}
                className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                Preview
              </button>
            </div>

            {/* Manual Entry */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Manual Entry</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Symbol *</label>
                  <input
                    type="text"
                    value={manualHolding.symbol || ''}
                    onChange={(e) => setManualHolding({ ...manualHolding, symbol: e.target.value })}
                    placeholder="AAPL"
                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Quantity *</label>
                  <input
                    type="number"
                    value={manualHolding.quantity || ''}
                    onChange={(e) => setManualHolding({ ...manualHolding, quantity: parseFloat(e.target.value) || 0 })}
                    placeholder="50"
                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Purchase Price *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={manualHolding.purchase_price || ''}
                    onChange={(e) => setManualHolding({ ...manualHolding, purchase_price: parseFloat(e.target.value) || 0 })}
                    placeholder="150.00"
                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Purchase Date</label>
                  <input
                    type="date"
                    value={manualHolding.purchase_date || ''}
                    onChange={(e) => setManualHolding({ ...manualHolding, purchase_date: e.target.value })}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Asset Class</label>
                  <select
                    value={manualHolding.asset_class || 'stock'}
                    onChange={(e) => setManualHolding({ ...manualHolding, asset_class: e.target.value as any })}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="stock">Stock</option>
                    <option value="etf">ETF</option>
                    <option value="crypto">Crypto</option>
                    <option value="mutual_fund">Mutual Fund</option>
                  </select>
                </div>
              </div>
              <button
                onClick={handleManualAdd}
                className="mt-4 bg-green-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-green-700 transition"
              >
                Add Holding
              </button>
            </div>
          </div>
        )}

        {step === 'preview' && (
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Preview</h2>
            <p className="text-gray-600 mb-4">Review your holdings before importing:</p>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Asset Class</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {parsedHoldings.map((holding, idx) => (
                    <tr key={idx}>
                      <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{holding.symbol}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-500">{holding.quantity}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-500">${holding.purchase_price.toFixed(2)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-500">
                        ${(holding.quantity * holding.purchase_price).toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-500 capitalize">{holding.asset_class}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-6 flex space-x-4">
              <button
                onClick={() => setStep('upload')}
                className="bg-gray-200 text-gray-800 px-6 py-2 rounded-lg font-medium hover:bg-gray-300 transition"
              >
                Back
              </button>
              <button
                onClick={handleImport}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition"
              >
                Import {parsedHoldings.length} Holding{parsedHoldings.length !== 1 ? 's' : ''}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
