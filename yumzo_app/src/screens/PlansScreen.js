import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { getPlans, getNearbyKitchens, createSubscription } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';

export default function PlansScreen({ navigation }) {
  const { user } = useAuth();
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [subscribingId, setSubscribingId] = useState(null);

  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    try {
      const { data } = await getPlans();
      setPlans(data);
    } catch (e) {
      Alert.alert('Error', 'Could not load plans. Pull down to retry.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (plan) => {
    if (!user?.latitude || !user?.longitude) {
      Alert.alert(
        'Location needed',
        'Please set your delivery location in your profile before subscribing.'
      );
      return;
    }

    setSubscribingId(plan.id);
    try {
      // Find a kitchen that covers this location
      const { data: kitchens } = await getNearbyKitchens(user.latitude, user.longitude);
      if (!kitchens.length) {
        Alert.alert('No kitchens nearby', 'No cloud kitchen currently serves your area.');
        return;
      }

      const nearestKitchen = kitchens[0];
      const today = new Date().toISOString().split('T')[0];

      await createSubscription({
        plan: plan.id,
        kitchen: nearestKitchen.id,
        start_date: today,
        breakfast_enabled: plan.meals_per_day >= 3,
        lunch_enabled: true,
        dinner_enabled: plan.meals_per_day >= 2,
        delivery_latitude: user.latitude,
        delivery_longitude: user.longitude,
        delivery_address: user.address_line || 'My location',
      });

      Alert.alert('Subscribed!', `You're on the ${plan.tier} plan now.`, [
        { text: 'OK', onPress: () => navigation.navigate('Home') },
      ]);
    } catch (e) {
      Alert.alert('Error', 'Could not create subscription. Please try again.');
    } finally {
      setSubscribingId(null);
    }
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#F4623A" />
      </View>
    );
  }

  const renderPlan = ({ item }) => (
    <View style={styles.card}>
      <Text style={styles.tier}>{item.tier}</Text>
      <Text style={styles.meals}>{item.meals_per_day} meal{item.meals_per_day > 1 ? 's' : ''}/day</Text>
      <Text style={styles.price}>₹{item.price}</Text>
      <Text style={styles.duration}>for {item.duration_days} days</Text>

      <TouchableOpacity
        style={styles.subscribeButton}
        onPress={() => handleSubscribe(item)}
        disabled={subscribingId === item.id}
      >
        {subscribingId === item.id ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.subscribeButtonText}>Choose this plan</Text>
        )}
      </TouchableOpacity>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Choose your plan</Text>
      <FlatList
        data={plans}
        keyExtractor={(item) => item.id}
        renderItem={renderPlan}
        ListEmptyComponent={
          <Text style={styles.emptyText}>No plans available right now</Text>
        }
        contentContainerStyle={{ paddingBottom: 24 }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF7ED', padding: 20 },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#FFF7ED' },
  header: { fontSize: 20, fontWeight: '700', color: '#1F1B16', marginBottom: 16 },
  card: {
    backgroundColor: '#fff',
    borderRadius: 14,
    padding: 20,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: '#F0E9DC',
  },
  tier: { fontSize: 18, fontWeight: '700', color: '#1F1B16' },
  meals: { fontSize: 14, color: '#6B6355', marginTop: 2 },
  price: { fontSize: 24, fontWeight: '700', color: '#F4623A', marginTop: 10 },
  duration: { fontSize: 12, color: '#9A9284', marginBottom: 14 },
  subscribeButton: {
    backgroundColor: '#F4623A',
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
  },
  subscribeButtonText: { color: '#fff', fontWeight: '600' },
  emptyText: { textAlign: 'center', color: '#9A9284', marginTop: 40 },
});