import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { verifyOTP as verifyOTPRequest, getProfile } from '../api/endpoints';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    bootstrapAuth();
  }, []);

  // On app launch, check if we already have a valid token and fetch the profile.
  const bootstrapAuth = async () => {
    try {
      const token = await AsyncStorage.getItem('access_token');
      if (token) {
        const { data } = await getProfile();
        setUser(data);
      }
    } catch (e) {
      // Token invalid/expired — user will be sent to login screen
      await AsyncStorage.multiRemove(['access_token', 'refresh_token']);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (phoneNumber, otpCode) => {
    const { data } = await verifyOTPRequest(phoneNumber, otpCode);
    await AsyncStorage.setItem('access_token', data.access);
    await AsyncStorage.setItem('refresh_token', data.refresh);
    setUser(data.user);
    return data;
  };

  const logout = async () => {
    await AsyncStorage.multiRemove(['access_token', 'refresh_token']);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, setUser, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);