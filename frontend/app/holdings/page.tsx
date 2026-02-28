'use client';

import { useState } from 'react';
import { usePortfolio } from '@/hooks/usePortfolio';
import { useRouter } from 'next/navigation';

export default function HoldingsPage() {
  const router = useRouter();
  const { holdings, removeHolding } = usePortfolio();
  const [sortBy, setSortBy] = useState<'symbol' | 'value' | 'performance'>('symbol');
  const [filterAssetClass, setFilterAssetClass] = useState<string>('all');

  // Sort and filter holdings
  const filteredHoldings = holdings
    .filter(h => filterAssetClass === 'all' || h.asset_class === filterAssetClass)
    .sort((a, b) => {
      if (sortBy === 'symbol') {
        return a.symbol.localeCompare(b.symbol);
      } else if (sortBy === 'value') {
        return (b.quantity * b.purchase_price) - (a.quantity * a.purchase_price);
      }
      return 0;
    });

  const totalValue = holdings.reduce((sum, h) => sum + h.quantity * h.purchase_price, 0);

  if (holdings.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">No Holdings Yet</h1>
          <p className="text-gray-600 mb-8">Import your portfolio to get started.</p>
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

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Holdings</h1>

        {/* Summary */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Holdings</p>
              <p className="text-2xl font-bold text-gray-900">{holdings.length}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Value</p>
              <p className="text-2xl font-bold text-gray-900">
                ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Asset Classes</p>
              <p className="text-2xl font-bold text-gray-900">
                {new Set(holdings.map(h => h.asset_class)).size}
              </p>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-6 flex flex-wrap gap-4">
          <div>
            <label className="text-sm text-gray-600 mr-2">Sort by:</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="border border-gray-300 rounded-lg px-3 py-1 focus:ring-2 focus:ring-blue-500"
            >
              <option value="symbol">Symbol</option>
              <option value="value">Value</option>
            </select>
          </div>
          <div>
            <label className="text-sm text-gray-600 mr-2">Asset Class:</label>
            <select
              value={filterAssetClass}
              onChange={(e) => setFilterAssetClass(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-1 focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All</option>
              <option value="stock">Stock</option>
              <option value="etf">ETF</option>
              <option value="crypto">Crypto</option>
              <option value="mutual_fund">Mutual Fund</option>
            </select>
          </div>
        </div>

        {/* Holdings Table */}
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Asset Class</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredHoldings.map((holding) => (
                <tr key={holding.symbol} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                    {holding.symbol}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-500">
                    {holding.quantity}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-500">
                    ${holding.purchase_price.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-900 font-medium">
                    ${(holding.quantity * holding.purchase_price).toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-500 capitalize">
                    {holding.asset_class}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <button
                      onClick={() => removeHolding(holding.symbol)}
                      className="text-red-600 hover:text-red-800 text-sm font-medium"
                    >
                      Remove
                    </button>
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
