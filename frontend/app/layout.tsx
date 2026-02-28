import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { PortfolioProvider } from "@/context/PortfolioContext";

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
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <PortfolioProvider>
          <nav className="bg-white border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex items-center">
                  <a href="/" className="text-xl font-bold text-blue-600">
                    KlyrSignals
                  </a>
                  <div className="hidden md:ml-8 md:flex md:space-x-4">
                    <a href="/" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                      Dashboard
                    </a>
                    <a href="/import" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                      Import
                    </a>
                    <a href="/holdings" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                      Holdings
                    </a>
                    <a href="/analysis" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                      Analysis
                    </a>
                    <a href="/settings" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                      Settings
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </nav>
          {children}
          <footer className="bg-white border-t border-gray-200 mt-8">
            <div className="max-w-7xl mx-auto px-4 py-6">
              <p className="text-center text-sm text-gray-500">
                ⚠️ Investment advice disclaimer: KlyrSignals provides analysis only and is not a registered investment advisor.
                All investments involve risk. Past performance does not guarantee future results.
              </p>
            </div>
          </footer>
        </PortfolioProvider>
      </body>
    </html>
  );
}
