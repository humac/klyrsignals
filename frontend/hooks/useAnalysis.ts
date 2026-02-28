/**
 * Custom hook for portfolio analysis
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { Holding, PortfolioAnalysis } from '@/types/portfolio';
import { analyzePortfolio } from '@/lib/api';

interface UseAnalysisReturn {
  data: PortfolioAnalysis | null;
  loading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
}

export function useAnalysis(holdings: Holding[]): UseAnalysisReturn {
  const [data, setData] = useState<PortfolioAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchAnalysis = useCallback(async () => {
    if (holdings.length === 0) {
      setData(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await analyzePortfolio(holdings);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Analysis failed'));
    } finally {
      setLoading(false);
    }
  }, [holdings]);

  useEffect(() => {
    fetchAnalysis();
  }, [fetchAnalysis]);

  return {
    data,
    loading,
    error,
    refresh: fetchAnalysis,
  };
}
