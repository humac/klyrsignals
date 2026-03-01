import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from '@/context/ThemeContext';
import { ThemeToggle } from '@/components/ThemeToggle';
import { PortfolioProvider } from '@/context/PortfolioContext';

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "KlyrSignals - Portfolio Analyst",
  description: "AI-powered financial portfolio analyst for blind spot detection and over-exposure warnings",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ThemeProvider>
          <PortfolioProvider>
            <nav className="bg-white dark:bg-dark-surface border-b border-gray-200 dark:border-dark-border">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                  <div className="flex items-center">
                    <a href="/" className="text-xl font-bold text-blue-600 dark:text-dark-text">
                      KlyrSignals
                    </a>
                    <div className="hidden md:ml-8 md:flex md:space-x-4">
                      <a href="/" className="text-gray-700 dark:text-dark-text hover:text-blue-600 dark:hover:text-dark-text px-3 py-2 rounded-md text-sm font-medium">
                        Dashboard
                      </a>
                      <a href="/import" className="text-gray-700 dark:text-dark-text hover:text-blue-600 dark:hover:text-dark-text px-3 py-2 rounded-md text-sm font-medium">
                        Import
                      </a>
                      <a href="/holdings" className="text-gray-700 dark:text-dark-text hover:text-blue-600 dark:hover:text-dark-text px-3 py-2 rounded-md text-sm font-medium">
                        Holdings
                      </a>
                      <a href="/analysis" className="text-gray-700 dark:text-dark-text hover:text-blue-600 dark:hover:text-dark-text px-3 py-2 rounded-md text-sm font-medium">
                        Analysis
                      </a>
                      <a href="/settings" className="text-gray-700 dark:text-dark-text hover:text-blue-600 dark:hover:text-dark-text px-3 py-2 rounded-md text-sm font-medium">
                        Settings
                      </a>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <ThemeToggle />
                  </div>
                </div>
              </div>
            </nav>
            {children}
            <footer className="bg-white dark:bg-dark-surface border-t border-gray-200 dark:border-dark-border mt-8">
              <div className="max-w-7xl mx-auto px-4 py-6">
                <p className="text-center text-sm text-gray-500 dark:text-dark-muted">
                  ⚠️ Investment advice disclaimer: KlyrSignals provides analysis only and is not a registered investment advisor.
                  All investments involve risk. Past performance does not guarantee future results.
                </p>
              </div>
            </footer>
          </PortfolioProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
