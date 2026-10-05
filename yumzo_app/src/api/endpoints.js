import apiClient from './client';

// --- Auth ---
export const requestOTP = (phone_number) =>
  apiClient.post('/users/auth/request-otp/', { phone_number });

export const verifyOTP = (phone_number, otp_code) =>
  apiClient.post('/users/auth/verify-otp/', { phone_number, otp_code });

export const getProfile = () => apiClient.get('/users/profile/');

export const updateProfile = (data) => apiClient.patch('/users/profile/', data);

// --- Kitchens ---
export const getNearbyKitchens = (lat, lng) =>
  apiClient.get('/kitchens/nearby/', { params: { lat, lng } });

export const getKitchenDetail = (id) => apiClient.get(`/kitchens/${id}/`);

// --- Subscriptions ---
export const getPlans = () => apiClient.get('/subscriptions/plans/');

export const createSubscription = (payload) =>
  apiClient.post('/subscriptions/subscribe/', payload);

export const getMySubscription = () => apiClient.get('/subscriptions/my-subscription/');

export const pauseSubscription = (payload) =>
  apiClient.post('/subscriptions/pause/', payload);

export const skipMeal = (order_id) =>
  apiClient.post('/subscriptions/skip-meal/', { order_id });

export const getWallet = () => apiClient.get('/subscriptions/wallet/');

// --- Orders ---
export const getTodayOrders = () => apiClient.get('/orders/today/');

export const getOrderHistory = () => apiClient.get('/orders/history/');