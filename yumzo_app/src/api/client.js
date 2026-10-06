import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Point this at your Django backend. Use your machine's LAN IP (not localhost)
// when testing on a physical phone, e.g. http://192.168.1.5:8000
export const BASE_URL = 'http://10.21.165.192:8000'; // 10.0.2.2 = Android emulator's localhost alias

const apiClient = axios.create({
  baseURL: `${BASE_URL}/api`,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// Attach access token to every request
apiClient.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// On 401, try refreshing the token once, then retry the original request
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = await AsyncStorage.getItem('refresh_token');
        const { data } = await axios.post(`${BASE_URL}/api/token/refresh/`, {
          refresh: refreshToken,
        });
        await AsyncStorage.setItem('access_token', data.access);
        originalRequest.headers.Authorization = `Bearer ${data.access}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        await AsyncStorage.multiRemove(['access_token', 'refresh_token']);
        // Navigation to Login screen is handled by AuthContext watching storage state
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;