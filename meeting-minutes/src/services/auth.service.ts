import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL;

interface AuthResponse {
  token: string;
  user: {
    id: string;
    email: string;
  };
}

export const authService = {
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await axios.post(`${API_URL}/auth/login`, {
      email,
      password,
    });
    return response.data;
  },

  async register(email: string, password: string): Promise<AuthResponse> {
    const response = await axios.post(`${API_URL}/auth/register`, {
      email,
      password,
    });
    return response.data;
  },

  setToken(token: string) {
    localStorage.setItem("token", token);
  },

  getToken() {
    return localStorage.getItem("token");
  },

  removeToken() {
    localStorage.removeItem("token");
  },
};
