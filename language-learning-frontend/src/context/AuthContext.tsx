'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { api, setAuthToken, getAuthToken } from '@/lib/api/api';
import { toast } from 'sonner';
import { ApiError } from '@/types/api';

interface AuthContextType {
  isAuthenticated: boolean;
  user: { username: string } | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<{ username: string } | null>(null);
  const router = useRouter();

  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      setAuthToken(token);
      setIsAuthenticated(true);
      // Try to get username from saved data if available
      const savedUsername = localStorage.getItem('username');
      if (savedUsername) {
        setUser({ username: savedUsername });
      }
    }
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const response = await api.post('/login', { username, password });
      const { token } = response.data;
      
      if (!token) {
        throw new Error('Token not received from server');
      }
      
      // For debugging
      console.log('Token received:', typeof token, token.substring(0, 10) + '...');
      
      setAuthToken(token);
      setIsAuthenticated(true);
      setUser({ username });
      
      // Save username for later use
      localStorage.setItem('username', username);
      
      toast.success('Logged in successfully');
      router.push('/chat');
    } catch (error: unknown) {
      const apiError = error as ApiError;
      const errorMessage = apiError.response?.data?.message || apiError.message || 'Login failed';
      toast.error(errorMessage);
      console.error('Login error:', error);
      throw error;
    }
  };

  const register = async (username: string, email: string, password: string) => {
    try {
      await api.post('/register', { username, email, password });
      toast.success('Registered successfully! Please log in.');
      router.push('/login');
    } catch (error: unknown) {
      const apiError = error as ApiError;
      const errorMessage = apiError.response?.data?.message || apiError.message || 'Registration failed';
      toast.error(errorMessage);
      console.error('Registration error:', error);
      throw error;
    }
  };

  const logout = () => {
    setAuthToken(null);
    setIsAuthenticated(false);
    setUser(null);
    toast.info('Logged out');
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};