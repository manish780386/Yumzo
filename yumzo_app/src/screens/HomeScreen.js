import React, { useState, useCallback, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { useAuth } from '../context/AuthContext';
import { getTodayMenu, skipMeal, claimDeal } from '../api/endpoints';

const MEAL_META = {
  BREAKFAST: { label: 'Breakfast', icon: '🌅' },
  LUNCH: { label: 'Lunch', icon: '🍛' },
  DINNER: { label: 'Dinner', icon: '🌙' },
};

const STATUS_META = {
  SCHEDULED: { text: 'Scheduled', color: '#6B6355' },
  PREPARING: { text: 'Being prepared', color: '#B7791F' },
  OUT_FOR_DELIVERY: { text: 'Out for delivery', color: '#F4623A' },
  DELIVERED: { text: 'Delivered', color: '#2F8F5B' },
  SKIPPED: { text: 'Skipped', color: '#9A9284' },
  CANCELLED: { text: 'Cancelled', color: '#C94B3C' },
};

export default function HomeScreen({ navigation }) {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [busyId, setBusyId] = useState(null);
  const intervalRef = useRef(null);

  const loadData = useCallback(async () => {
    try {
      const res = await getTodayMenu();
      setData(res.data);
    } catch (e) {
      // keep whatever we already had on screen
    } finally {
      setLoading(false);
    }
  }, []);

  // Load on focus, and re-check every minute so deals flip to "live" at 12:00
  // without the user having to pull to refresh.
  useFocusEffect(
    useCallback(() => {
      loadData();
      intervalRef.current = setInterval(loadData, 60000);
      return () => clearInterval(intervalRef.current);
    }, [loadData])
  );

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleSkip = (meal) => {
    Alert.alert('Skip this meal?', `${MEAL_META[meal.meal_type].label} won't be delivered today.`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Skip',
        style: 'destructive',
        onPress: async () => {
          setBusyId(meal.order.id);
          try {
            await skipMeal(meal.order.id);
            await loadData();
          } catch (e) {
            const msg = e.response?.data?.error || 'Could not skip this meal';
            Alert.alert('Cannot skip', msg);
          } finally {
            setBusyId(null);
          }
        },
      },
    ]);
  };

  const handleClaim = (deal) => {
    Alert.alert(
      'Grab this deal?',
      `${deal.item_name} for ₹${deal.discounted_price} (pay on delivery).`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Yes, order',
          onPress: async () => {
            setBusyId(deal.id);
            try {
              await claimDeal(deal.id);
              Alert.alert('Done!', 'Your meal is on its way soon.');
              await loadData();
            } catch (e) {
              Alert.alert('Could not order', e.response?.data?.error || 'Please try again.');
              await loadData();
            } finally {
              setBusyId(null);
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#F4623A" />
      </View>
    );
  }

  const liveDeals = (data?.deals || []).filter((d) => d.is_live);
  const upcomingDeals = (data?.deals || []).filter((d) => !d.is_live);

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={{ padding: 20, paddingBottom: 40 }}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <Text style={styles.greeting}>Hi {user?.first_name || 'there'} 👋</Text>
      <Text style={styles.subGreeting}>
        {data?.weekday}
        {data?.kitchen ? ` · ${data.kitchen.name}` : ''}
      </Text>

      {!data?.has_subscription && (
        <TouchableOpacity style={styles.ctaBanner} onPress={() => navigation.navigate('Plans')}>
          <Text style={styles.ctaBannerText}>Get daily meals — subscribe to a plan →</Text>
        </TouchableOpacity>
      )}

      {!data?.kitchen && (
        <Text style={styles.emptyText}>
          No kitchen serves your location yet. Set your location in your profile.
        </Text>
      )}

      {/* ---------- Last-call deals ---------- */}
      {liveDeals.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🔥 Last-call deals</Text>
          {liveDeals.map((deal) => (
            <View key={deal.id} style={styles.dealCard}>
              <View style={styles.dealBadge}>
                <Text style={styles.dealBadgeText}>{deal.discount_percent}% OFF</Text>
              </View>
              <Text style={styles.dealMeal}>{MEAL_META[deal.meal_type]?.label}</Text>
              <Text style={styles.dealName}>{deal.item_name}</Text>
              <View style={styles.priceRow}>
                <Text style={styles.dealPrice}>₹{deal.discounted_price}</Text>
                <Text style={styles.dealOldPrice}>₹{deal.original_price}</Text>
                <Text style={styles.portions}>{deal.portions_left} left</Text>
              </View>
              <TouchableOpacity
                style={styles.grabButton}
                onPress={() => handleClaim(deal)}
                disabled={busyId === deal.id}
              >
                {busyId === deal.id ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <Text style={styles.grabButtonText}>Grab it</Text>
                )}
              </TouchableOpacity>
            </View>
          ))}
        </View>
      )}

      {liveDeals.length === 0 && upcomingDeals.length > 0 && (
        <View style={styles.teaser}>
          <Text style={styles.teaserText}>
            🔥 {upcomingDeals.length} last-call deal{upcomingDeals.length > 1 ? 's' : ''} unlock at{' '}
            {upcomingDeals[0].unlocks_at} — {upcomingDeals[0].discount_percent}% off, limited portions
          </Text>
        </View>
      )}

      {/* ---------- Today's menu ---------- */}
      {data?.meals?.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Today's menu</Text>
          {data.meals.map((meal) => {
            const meta = MEAL_META[meal.meal_type];
            const status = meal.order ? STATUS_META[meal.order.status] : null;
            return (
              <View key={meal.meal_type} style={styles.card}>
                <View style={styles.cardHeader}>
                  <Text style={styles.mealType}>
                    {meta.icon} {meta.label}
                  </Text>
                  {status && <Text style={[styles.status, { color: status.color }]}>{status.text}</Text>}
                </View>
                <Text style={styles.itemName}>{meal.item_name}</Text>
                {!!meal.description && <Text style={styles.description}>{meal.description}</Text>}

                {meal.order?.status === 'SCHEDULED' && meal.can_skip && (
                  <View style={styles.skipRow}>
                    <TouchableOpacity onPress={() => handleSkip(meal)} disabled={busyId === meal.order.id}>
                      <Text style={styles.skipText}>Skip this meal</Text>
                    </TouchableOpacity>
                    <Text style={styles.cutoffText}>until {meal.skip_cutoff}</Text>
                  </View>
                )}
                {meal.order?.status === 'SCHEDULED' && !meal.can_skip && (
                  <Text style={styles.cutoffText}>Skip window closed (kitchen is preparing)</Text>
                )}
              </View>
            );
          })}
        </View>
      )}

      {/* ---------- Tomorrow ---------- */}
      {data?.tomorrow?.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Tomorrow's menu</Text>
          <View style={styles.tomorrowCard}>
            {data.tomorrow.map((m) => (
              <Text key={m.meal_type} style={styles.tomorrowRow}>
                <Text style={styles.tomorrowMeal}>{MEAL_META[m.meal_type].label}: </Text>
                {m.item_name}
              </Text>
            ))}
          </View>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF7ED' },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#FFF7ED' },
  greeting: { fontSize: 22, fontWeight: '700', color: '#1F1B16' },
  subGreeting: { fontSize: 14, color: '#6B6355', marginTop: 2, marginBottom: 16 },
  ctaBanner: { backgroundColor: '#F4623A', borderRadius: 10, padding: 14, marginBottom: 16 },
  ctaBannerText: { color: '#fff', fontWeight: '600', textAlign: 'center' },
  emptyText: { textAlign: 'center', color: '#9A9284', marginVertical: 24 },
  section: { marginTop: 8, marginBottom: 12 },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#1F1B16', marginBottom: 10 },

  dealCard: {
    backgroundColor: '#FFF1E6',
    borderRadius: 14,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#F9C9A8',
  },
  dealBadge: {
    alignSelf: 'flex-start',
    backgroundColor: '#2F8F5B',
    borderRadius: 6,
    paddingVertical: 3,
    paddingHorizontal: 8,
    marginBottom: 8,
  },
  dealBadgeText: { color: '#fff', fontSize: 12, fontWeight: '800' },
  dealMeal: { fontSize: 12, color: '#6B6355' },
  dealName: { fontSize: 16, fontWeight: '700', color: '#1F1B16', marginTop: 2 },
  priceRow: { flexDirection: 'row', alignItems: 'baseline', marginTop: 8 },
  dealPrice: { fontSize: 22, fontWeight: '800', color: '#F4623A' },
  dealOldPrice: { fontSize: 14, color: '#9A9284', textDecorationLine: 'line-through', marginLeft: 8 },
  portions: { fontSize: 12, color: '#C94B3C', fontWeight: '700', marginLeft: 'auto' },
  grabButton: { backgroundColor: '#F4623A', borderRadius: 10, paddingVertical: 12, alignItems: 'center', marginTop: 12 },
  grabButtonText: { color: '#fff', fontWeight: '700' },
  teaser: { backgroundColor: '#FFF1E6', borderRadius: 12, padding: 14, marginBottom: 12 },
  teaserText: { color: '#8A4B1F', fontSize: 13, fontWeight: '600' },

  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#F0E9DC',
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  mealType: { fontSize: 14, fontWeight: '700', color: '#1F1B16' },
  status: { fontSize: 12, fontWeight: '700' },
  itemName: { fontSize: 15, color: '#1F1B16' },
  description: { fontSize: 12, color: '#9A9284', marginTop: 2 },
  skipRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginTop: 10 },
  skipText: { color: '#F4623A', fontSize: 13, fontWeight: '700' },
  cutoffText: { fontSize: 11, color: '#9A9284', marginTop: 6 },

  tomorrowCard: { backgroundColor: '#fff', borderRadius: 12, padding: 14, borderWidth: 1, borderColor: '#F0E9DC' },
  tomorrowRow: { fontSize: 13, color: '#1F1B16', marginBottom: 4 },
  tomorrowMeal: { fontWeight: '700', color: '#6B6355' },
});