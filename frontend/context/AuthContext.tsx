'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  email: string;
  name: string;
  avatarUrl?: string;
  emailVerified?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (data: Partial<User>) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  loginWithGitHub: () => Promise<void>;
  handleOAuthCallback: (code: string, state: string, provider: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Load user from token on mount
  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem('klyrsignals_access_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const response = await fetch(`${API_URL}/api/v1/auth/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          // Token expired, clear it
          localStorage.removeItem('klyrsignals_access_token');
          localStorage.removeItem('klyrsignals_refresh_token');
        }
      } catch (error) {
        console.error('Failed to load user:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    localStorage.setItem('klyrsignals_access_token', data.access_token);
    localStorage.setItem('klyrsignals_refresh_token', data.refresh_token);
    setUser(data.user);
    router.push('/dashboard');
  };

  const register = async (email: string, password: string, name: string) => {
    const response = await fetch(`${API_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, name }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    const data = await response.json();
    localStorage.setItem('klyrsignals_access_token', data.access_token);
    localStorage.setItem('klyrsignals_refresh_token', data.refresh_token);
    setUser(data.user);
    router.push('/dashboard');
  };

  const logout = async () => {
    const token = localStorage.getItem('klyrsignals_access_token');
    if (token) {
      await fetch(`${API_URL}/api/v1/auth/logout`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
    }
    localStorage.removeItem('klyrsignals_access_token');
    localStorage.removeItem('klyrsignals_refresh_token');
    setUser(null);
    router.push('/login');
  };

  const updateUser = async (data: Partial<User>) => {
    const token = localStorage.getItem('klyrsignals_access_token');
    if (!token) throw new Error('Not authenticated');

    const response = await fetch(`${API_URL}/api/v1/users/me`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) throw new Error('Failed to update user');

    const userData = await response.json();
    setUser(userData);
  };

  const loginWithGoogle = async () => {
    // Initialize OAuth flow
    const response = await fetch(`${API_URL}/api/v1/oauth/google/init`);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Google OAuth initialization failed');
    }
    const data = await response.json();
    
    // Redirect to Google authorization URL
    window.location.href = data.authorization_url;
  };

  const loginWithGitHub = async () => {
    // Initialize OAuth flow
    const response = await fetch(`${API_URL}/api/v1/oauth/github/init`);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'GitHub OAuth initialization failed');
    }
    const data = await response.json();
    
    // Redirect to GitHub authorization URL
    window.location.href = data.authorization_url;
  };

  const handleOAuthCallback = async (code: string, state: string, provider: string) => {
    // Exchange code for tokens
    const response = await fetch(
      `${API_URL}/api/v1/oauth/${provider}/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state)}`
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `${provider} OAuth failed`);
    }
    
    const data = await response.json();
    localStorage.setItem('klyrsignals_access_token', data.access_token);
    localStorage.setItem('klyrsignals_refresh_token', data.refresh_token);
    setUser(data.user);
    router.push('/dashboard');
  };

  const value = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    updateUser,
    loginWithGoogle,
    loginWithGitHub,
    handleOAuthCallback,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
