import React, { useState, useCallback } from 'react';
import { View, Text, StyleSheet, FlatList, ActivityIndicator, RefreshControl } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { getOrderHistory } from '../api/endpoints';

export default function OrderHistoryScreen() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadOrders = useCallback(async () => {
    try {
      const { data } = await getOrderHistory();
      setOrders(data);
    } catch (e) {
      // keep previous state on failure
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadOrders();
    }, [loadOrders])
  );

  const onRefresh = () => {
    setRefreshing(true);
    loadOrders();
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#F4623A" />
      </View>
    );
  }

  const renderItem = ({ item }) => (
    <View style={styles.card}>
      <View style={styles.row}>
        <Text style={styles.date}>{item.scheduled_date}</Text>
        <Text style={[styles.status, statusColor(item.status)]}>{item.status}</Text>
      </View>
      <Text style={styles.mealType}>{item.meal_type}</Text>
      <Text style={styles.kitchen}>{item.kitchen_name}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={orders}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={<Text style={styles.emptyText}>No orders yet</Text>}
        contentContainerStyle={{ padding: 20, paddingBottom: 40 }}
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
    CANCELLED: { color: '#C94B3C' },
  };
  return map[status] || {};
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF7ED' },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#FFF7ED' },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#F0E9DC',
  },
  row: { flexDirection: 'row', justifyContent: 'space-between' },
  date: { fontSize: 13, color: '#6B6355' },
  status: { fontSize: 12, fontWeight: '700' },
  mealType: { fontSize: 15, fontWeight: '700', color: '#1F1B16', marginTop: 4 },
  kitchen: { fontSize: 13, color: '#9A9284', marginTop: 2 },
  emptyText: { textAlign: 'center', color: '#9A9284', marginTop: 60 },
});