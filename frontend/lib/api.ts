/**
 * API client for KlyrSignals backend
 */

import { Holding, PortfolioAnalysis } from '@/types/portfolio';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Analyze portfolio holdings
 */
export async function analyzePortfolio(holdings: Holding[]): Promise<PortfolioAnalysis> {
  const response = await fetch(`${API_BASE}/api/v1/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ holdings }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: { message: 'Analysis failed' } }));
    throw new Error(error.detail?.message || 'Analysis failed');
  }

  return response.json();
}

/**
 * Get current prices for multiple symbols
 */
export async function getPrices(symbols: string[]): Promise<Record<string, number | null>> {
  const response = await fetch(`${API_BASE}/api/v1/prices?symbols=${symbols.join(',')}`);
  
  if (!response.ok) {
    throw new Error('Price fetch failed');
  }

  const data = await response.json();
  return data.prices;
}

/**
 * Health check
 */
export async function healthCheck(): Promise<{ status: string; timestamp: string }> {
  const response = await fetch(`${API_BASE}/api/health`);
  
  if (!response.ok) {
    throw new Error('Health check failed');
  }

  return response.json();
}
