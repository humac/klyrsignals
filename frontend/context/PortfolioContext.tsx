/**
 * Portfolio Context - State management for portfolio holdings
 */

'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Holding } from '@/types/portfolio';

const STORAGE_KEY = 'klyrsignals_portfolio';

interface PortfolioContextType {
  holdings: Holding[];
  totalValue: number;
  lastUpdated: Date | null;
  addHolding: (holding: Holding) => void;
  updateHolding: (symbol: string, updates: Partial<Holding>) => void;
  removeHolding: (symbol: string) => void;
  importHoldings: (holdings: Holding[]) => void;
  clearPortfolio: () => void;
  refreshPrices: () => Promise<void>;
}

const PortfolioContext = createContext<PortfolioContextType | undefined>(undefined);

export function PortfolioProvider({ children }: { children: React.ReactNode }) {
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [totalValue, setTotalValue] = useState(0);

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        setHoldings(parsed.holdings || []);
        setLastUpdated(parsed.lastUpdated ? new Date(parsed.lastUpdated) : null);
      }
    } catch (error) {
      console.error('Failed to load portfolio from localStorage:', error);
    }
  }, []);

  // Save to localStorage on changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        holdings,
        lastUpdated: lastUpdated?.toISOString(),
      }));
    } catch (error) {
      console.error('Failed to save portfolio to localStorage:', error);
    }
  }, [holdings, lastUpdated]);

  // Calculate total value
  useEffect(() => {
    // Simple calculation using purchase price (real value requires API call)
    const value = holdings.reduce((sum, h) => sum + h.quantity * h.purchase_price, 0);
    setTotalValue(value);
  }, [holdings]);

  const addHolding = useCallback((holding: Holding) => {
    setHoldings(prev => {
      const existing = prev.find(h => h.symbol === holding.symbol);
      if (existing) {
        return prev.map(h =>
          h.symbol === holding.symbol
            ? { ...h, quantity: h.quantity + holding.quantity }
            : h
        );
      }
      return [...prev, holding];
    });
    setLastUpdated(new Date());
  }, []);

  const updateHolding = useCallback((symbol: string, updates: Partial<Holding>) => {
    setHoldings(prev => prev.map(h => (h.symbol === symbol ? { ...h, ...updates } : h)));
    setLastUpdated(new Date());
  }, []);

  const removeHolding = useCallback((symbol: string) => {
    setHoldings(prev => prev.filter(h => h.symbol !== symbol));
    setLastUpdated(new Date());
  }, []);

  const importHoldings = useCallback((newHoldings: Holding[]) => {
    setHoldings(newHoldings);
    setLastUpdated(new Date());
  }, []);

  const clearPortfolio = useCallback(() => {
    setHoldings([]);
    setLastUpdated(null);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const refreshPrices = useCallback(async () => {
    // This would trigger a re-fetch from the API
    // For now, just update the timestamp
    setLastUpdated(new Date());
  }, []);

  return (
    <PortfolioContext.Provider
      value={{
        holdings,
        totalValue,
        lastUpdated,
        addHolding,
        updateHolding,
        removeHolding,
        importHoldings,
        clearPortfolio,
        refreshPrices,
      }}
    >
      {children}
    </PortfolioContext.Provider>
  );
}

export function usePortfolio() {
  const context = useContext(PortfolioContext);
  if (context === undefined) {
    throw new Error('usePortfolio must be used within a PortfolioProvider');
  }
  return context;
}
