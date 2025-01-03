import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";
import { authService } from "../services/auth.service";

interface User {
  id: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check for existing token on mount
  useEffect(() => {
    const token = authService.getToken();
    if (token) {
      // You might want to validate the token with your backend here
      // For now, we'll just set up the axios interceptor
      setupAxiosInterceptor(token);
    }
    setLoading(false);
  }, []);

  const setupAxiosInterceptor = (token: string) => {
    axios.interceptors.request.use((config) => {
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await authService.login(email, password);

      // Save the token
      authService.setToken(response.token);

      // Set up axios interceptor for future requests
      setupAxiosInterceptor(response.token);

      // Update user state
      setUser(response.user);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 401) {
          throw new Error("Invalid email or password");
        }
      }
      throw new Error("An error occurred during login");
    }
  };

  const register = async (email: string, password: string) => {
    try {
        
      const response = await authService.register(email, password);

      // Save the token
      authService.setToken(response.token);

      // Set up axios interceptor for future requests
      setupAxiosInterceptor(response.token);

      // Update user state
      setUser(response.user);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 409) {
          throw new Error("Email already exists");
        }
      }
      throw new Error("An error occurred during registration");
    }
  };

  const logout = () => {
    // Clear token from localStorage
    authService.removeToken();

    // Clear user state
    setUser(null);

    // Remove axios interceptor
    axios.interceptors.request.use((config) => {
      delete config.headers.Authorization;
      return config;
    });
  };

  const value = {
    user,
    login,
    register,
    logout,
  };

  if (loading) {
    return <div>Loading...</div>; // Or your loading component
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
