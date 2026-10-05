import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { useAuth } from '../context/AuthContext';
import { getTodayOrders, getMySubscription, skipMeal } from '../api/endpoints';

export default function HomeScreen({ navigation }) {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [subscription, setSubscription] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const [ordersRes, subRes] = await Promise.allSettled([
        getTodayOrders(),
        getMySubscription(),
      ]);
      if (ordersRes.status === 'fulfilled') setOrders(ordersRes.value.data);
      if (subRes.status === 'fulfilled') setSubscription(subRes.value.data);
    } catch (e) {
      // Silently ignore — empty state UI below handles no-data case
    }
  }, []);

  // Refetch every time the screen comes into focus (e.g. after skipping a meal)
  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [loadData])
  );

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleSkip = (orderId) => {
    Alert.alert('Skip this meal?', 'You will not be delivered this meal today.', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Skip',
        style: 'destructive',
        onPress: async () => {
          try {
            await skipMeal(orderId);
            loadData();
          } catch (e) {
            Alert.alert('Error', 'Could not skip this meal');
          }
        },
      },
    ]);
  };

  const renderMealCard = ({ item }) => (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.mealType}>{item.meal_type}</Text>
        <Text style={[styles.status, statusColor(item.status)]}>{item.status}</Text>
      </View>
      <Text style={styles.kitchenName}>{item.kitchen_name}</Text>
      <Text style={styles.address}>{item.delivery_address}</Text>

      {item.status === 'SCHEDULED' && (
        <TouchableOpacity style={styles.skipButton} onPress={() => handleSkip(item.id)}>
          <Text style={styles.skipButtonText}>Skip this meal</Text>
        </TouchableOpacity>
      )}
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.headerRow}>
        <View>
          <Text style={styles.greeting}>Hi {user?.first_name || 'there'} 👋</Text>
          <Text style={styles.subGreeting}>
            {subscription ? `${subscription.plan.tier} plan active` : 'No active plan'}
          </Text>
        </View>
      </View>

      {!subscription && (
        <TouchableOpacity
          style={styles.ctaBanner}
          onPress={() => navigation.navigate('Plans')}
        >
          <Text style={styles.ctaBannerText}>Subscribe to a meal plan →</Text>
        </TouchableOpacity>
      )}

      <Text style={styles.sectionTitle}>Today's Meals</Text>

      <FlatList
        data={orders}
        keyExtractor={(item) => item.id}
        renderItem={renderMealCard}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={
          <Text style={styles.emptyText}>No meals scheduled for today</Text>
        }
        contentContainerStyle={{ paddingBottom: 24 }}
      />
    </View>
  );
}

function statusColor(status) {
  const map = {
    DELIVERED: { color: '#2F8F5B' },
    OUT_FOR_DELIVERY: { color: '#F4623A' },
    SKIPPED: { color: '#9A9284' },
    SCHEDULED: { color: '#6B6355' },
  };
  return map[status] || {};
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF7ED', padding: 20 },
  headerRow: { marginBottom: 16 },
  greeting: { fontSize: 22, fontWeight: '700', color: '#1F1B16' },
  subGreeting: { fontSize: 14, color: '#6B6355', marginTop: 2 },
  ctaBanner: {
    backgroundColor: '#F4623A',
    borderRadius: 10,
    padding: 14,
    marginBottom: 20,
  },
  ctaBannerText: { color: '#fff', fontWeight: '600', textAlign: 'center' },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#1F1B16', marginBottom: 10 },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#F0E9DC',
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  mealType: { fontSize: 15, fontWeight: '700', color: '#1F1B16' },
  status: { fontSize: 12, fontWeight: '600' },
  kitchenName: { fontSize: 14, color: '#1F1B16', marginBottom: 2 },
  address: { fontSize: 12, color: '#9A9284' },
  skipButton: { marginTop: 10, alignSelf: 'flex-start' },
  skipButtonText: { color: '#F4623A', fontSize: 13, fontWeight: '600' },
  emptyText: { textAlign: 'center', color: '#9A9284', marginTop: 40 },
});