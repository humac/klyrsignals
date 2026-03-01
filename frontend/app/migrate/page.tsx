'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';

interface Holding {
  symbol: string;
  quantity: number;
  purchase_price: number;
  purchase_date?: string;
  asset_class?: string;
}

interface MigrationStats {
  holdingsCount: number;
  totalValue: number;
}

export default function MigratePage() {
  const [isMigrating, setIsMigrating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [migrationStats, setMigrationStats] = useState<MigrationStats | null>(null);
  const [progress, setProgress] = useState(0);
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();

  // Check for localStorage data on mount
  useEffect(() => {
    const localData = localStorage.getItem('klyrsignals_portfolio');
    if (localData) {
      try {
        const portfolio = JSON.parse(localData);
        const holdings = portfolio.holdings || [];
        
        // Calculate stats
        const totalValue = holdings.reduce((sum: number, h: Holding) => {
          return sum + (h.quantity * h.purchase_price);
        }, 0);

        setMigrationStats({
          holdingsCount: holdings.length,
          totalValue: totalValue
        });
      } catch (err) {
        console.error('Failed to parse localStorage data:', err);
      }
    }
  }, []);

  const handleMigrate = async () => {
    setIsMigrating(true);
    setError('');
    setProgress(10);

    try {
      // Get localStorage data
      const localData = localStorage.getItem('klyrsignals_portfolio');
      if (!localData) {
        setSuccess(true);
        setTimeout(() => {
          router.push('/dashboard');
        }, 2000);
        return;
      }

      const portfolio = JSON.parse(localData);
      const holdings = portfolio.holdings || [];
      
      if (holdings.length === 0) {
        throw new Error('No holdings found in localStorage');
      }

      setProgress(30);

      // Send to backend migration endpoint
      const token = localStorage.getItem('klyrsignals_access_token');
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const response = await fetch(`${API_URL}/api/v1/migrate/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          holdings: holdings,
          metadata: {
            source: 'localStorage',
            migratedAt: new Date().toISOString(),
            clientVersion: '1.6.0'
          }
        }),
      });

      setProgress(70);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Migration failed');
      }

      const result = await response.json();
      setProgress(90);

      // Clear localStorage after successful migration
      localStorage.removeItem('klyrsignals_portfolio');
      setSuccess(true);
      setProgress(100);
      
      // Show success message briefly then redirect
      setTimeout(() => {
        router.push('/dashboard');
      }, 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Migration failed');
      setProgress(0);
    } finally {
      setIsMigrating(false);
    }
  };

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated && typeof window !== 'undefined') {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-dark-bg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-dark-muted">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-dark-bg py-12 px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-900/30 mb-4">
            <svg className="w-8 h-8 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-dark-text mb-2">
            Migrate Your Portfolio
          </h2>
          <p className="text-gray-600 dark:text-dark-muted">
            Transfer your local portfolio data to the cloud
          </p>
        </div>

        {migrationStats && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
            <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-300 mb-2">
              Found Local Portfolio Data
            </h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-blue-600 dark:text-blue-400 font-medium">Holdings:</span>
                <span className="ml-2 text-gray-900 dark:text-dark-text">{migrationStats.holdingsCount}</span>
              </div>
              <div>
                <span className="text-blue-600 dark:text-blue-400 font-medium">Est. Value:</span>
                <span className="ml-2 text-gray-900 dark:text-dark-text">${migrationStats.totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
              </div>
            </div>
          </div>
        )}
        
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded-lg mb-4">
            <div className="flex items-start">
              <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              {error}
            </div>
          </div>
        )}
        
        {success && (
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-600 dark:text-green-400 px-4 py-3 rounded-lg mb-4">
            <div className="flex items-start">
              <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="font-semibold">Migration successful!</p>
                <p className="text-sm mt-1">Redirecting to your dashboard...</p>
              </div>
            </div>
          </div>
        )}

        {isMigrating && (
          <div className="mb-6">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-600 dark:text-dark-muted">Migrating...</span>
              <span className="text-gray-600 dark:text-dark-muted">{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-dark-surface rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 dark:text-dark-muted mt-2 text-center">
              {progress < 30 && 'Preparing data...'}
              {progress >= 30 && progress < 70 && 'Uploading to cloud...'}
              {progress >= 70 && progress < 90 && 'Verifying migration...'}
              {progress >= 90 && 'Finalizing...'}
            </p>
          </div>
        )}

        <div className="bg-gray-50 dark:bg-dark-surface rounded-lg p-4 mb-6">
          <h4 className="text-sm font-semibold text-gray-900 dark:text-dark-text mb-2">
            What happens during migration?
          </h4>
          <ul className="text-sm text-gray-600 dark:text-dark-muted space-y-2">
            <li className="flex items-start">
              <svg className="w-4 h-4 mr-2 mt-0.5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Your holdings are securely transferred to the cloud
            </li>
            <li className="flex items-start">
              <svg className="w-4 h-4 mr-2 mt-0.5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Duplicate symbols are automatically merged
            </li>
            <li className="flex items-start">
              <svg className="w-4 h-4 mr-2 mt-0.5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Local data is cleared after successful migration
            </li>
            <li className="flex items-start">
              <svg className="w-4 h-4 mr-2 mt-0.5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Migration is logged for security audit
            </li>
          </ul>
        </div>

        <div className="space-y-3">
          <button
            onClick={handleMigrate}
            disabled={isMigrating || success || !migrationStats}
            className="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isMigrating ? 'Migrating...' : !migrationStats ? 'No Local Data Found' : 'Migrate to Cloud'}
          </button>
          <button
            onClick={() => router.push('/dashboard')}
            disabled={isMigrating}
            className="w-full py-3 px-4 bg-gray-200 dark:bg-dark-surface text-gray-900 dark:text-dark-text font-medium rounded-md hover:bg-gray-300 dark:hover:bg-dark-border disabled:opacity-50 transition-colors"
          >
            Skip (Start Fresh)
          </button>
        </div>

        {!migrationStats && (
          <p className="text-center text-sm text-gray-500 dark:text-dark-muted mt-4">
            No local portfolio data found. You can start building your portfolio in the dashboard.
          </p>
        )}
      </div>
    </div>
  );
}
