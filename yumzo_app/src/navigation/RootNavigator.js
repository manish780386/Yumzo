import React from 'react';
import { View, ActivityIndicator, StyleSheet, Text } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useAuth } from '../context/AuthContext';

import PhoneLoginScreen from '../screens/PhoneLoginScreen';
import OTPVerifyScreen from '../screens/OTPVerifyScreen';
import ProfileSetupScreen from '../screens/ProfileSetupScreen';
import HomeScreen from '../screens/HomeScreen';
import PlansScreen from '../screens/PlansScreen';
import SubscriptionScreen from '../screens/Subscriptionscreen.js';
import OrderHistoryScreen from '../screens/Orderhistoryscreen.js';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function AuthStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="PhoneLogin" component={PhoneLoginScreen} />
      <Stack.Screen name="OTPVerify" component={OTPVerifyScreen} />
    </Stack.Navigator>
  );
}

// Simple text-based tab icon so we don't pull in an icon library just yet.
function TabIcon({ label, focused }) {
  return (
    <Text style={{ fontSize: 11, color: focused ? '#F4623A' : '#9A9284', fontWeight: focused ? '700' : '400' }}>
      {label}
    </Text>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#F4623A',
        tabBarInactiveTintColor: '#9A9284',
        tabBarStyle: { borderTopColor: '#F0E9DC' },
      }}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{ tabBarIcon: ({ focused }) => <TabIcon label="🏠" focused={focused} /> }}
      />
      <Tab.Screen
        name="Subscription"
        component={SubscriptionScreen}
        options={{
          title: 'My Plan',
          tabBarIcon: ({ focused }) => <TabIcon label="📋" focused={focused} />,
        }}
      />
      <Tab.Screen
        name="Orders"
        component={OrderHistoryScreen}
        options={{
          title: 'Order History',
          tabBarIcon: ({ focused }) => <TabIcon label="🧾" focused={focused} />,
        }}
      />
    </Tab.Navigator>
  );
}

function AppStack() {
  // ProfileSetup lives here, not in AuthStack: by the time OTPVerifyScreen
  // navigates to it, `user` is already set, so RootNavigator has already
  // switched from AuthStack to AppStack. Keeping it here is what makes
  // navigation.replace('ProfileSetup') actually resolve.
  return (
    <Stack.Navigator initialRouteName="MainTabs">
      <Stack.Screen name="MainTabs" component={MainTabs} options={{ headerShown: false }} />
      <Stack.Screen name="Plans" component={PlansScreen} options={{ title: 'Choose a Plan' }} />
      <Stack.Screen
        name="ProfileSetup"
        component={ProfileSetupScreen}
        options={{ title: 'Set up your profile', headerBackVisible: false }}
      />
    </Stack.Navigator>
  );
}

export default function RootNavigator() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#F4623A" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      {user ? <AppStack /> : <AuthStack />}
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#FFF7ED' },
});