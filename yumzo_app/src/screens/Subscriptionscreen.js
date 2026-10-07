import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import DateTimePicker from '@react-native-community/datetimepicker';
import { getMySubscription, pauseSubscription } from '../api/endpoints';

export default function SubscriptionScreen({ navigation }) {
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showPausePicker, setShowPausePicker] = useState(false);
  const [pauseFrom, setPauseFrom] = useState(new Date());
  const [pauseTo, setPauseTo] = useState(new Date());
  const [pickerStep, setPickerStep] = useState('from'); // 'from' then 'to'
  const [submittingPause, setSubmittingPause] = useState(false);

  const loadSubscription = useCallback(async () => {
    try {
      const { data } = await getMySubscription();
      setSubscription(data);
    } catch (e) {
      setSubscription(null); // 404 = no active subscription, handled below
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadSubscription();
    }, [loadSubscription])
  );

  const handlePauseDateChange = (event, selectedDate) => {
    setShowPausePicker(false);
    if (!selectedDate) return;

    if (pickerStep === 'from') {
      setPauseFrom(selectedDate);
      setPauseTo(selectedDate);
      setPickerStep('to');
      setTimeout(() => setShowPausePicker(true), 300); // ask for end date next
    } else {
      setPauseTo(selectedDate);
      setPickerStep('from');
      confirmPause(pauseFrom, selectedDate);
    }
  };

  const confirmPause = (from, to) => {
    Alert.alert(
      'Pause subscription?',
      `No meals will be delivered from ${from.toDateString()} to ${to.toDateString()}.`,
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Confirm Pause', onPress: () => submitPause(from, to) },
      ]
    );
  };

  const submitPause = async (from, to) => {
    setSubmittingPause(true);
    try {
      await pauseSubscription({
        subscription: subscription.id,
        pause_from: from.toISOString().split('T')[0],
        pause_to: to.toISOString().split('T')[0],
      });
      Alert.alert('Paused', 'Your subscription has been paused for the selected dates.');
      loadSubscription();
    } catch (e) {
      Alert.alert('Error', 'Could not pause subscription. Please try again.');
    } finally {
      setSubmittingPause(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#F4623A" />
      </View>
    );
  }

  if (!subscription) {
    return (
      <View style={styles.centered}>
        <Text style={styles.emptyTitle}>No active subscription</Text>
        <Text style={styles.emptyText}>Subscribe to a plan to get daily meals delivered.</Text>
        <TouchableOpacity style={styles.ctaButton} onPress={() => navigation.navigate('Plans')}>
          <Text style={styles.ctaButtonText}>Browse Plans</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 20 }}>
      <View style={styles.statusCard}>
        <Text style={styles.tier}>{subscription.plan.tier} Plan</Text>
        <View style={[styles.statusBadge, statusStyle(subscription.status)]}>
          <Text style={styles.statusBadgeText}>{subscription.status}</Text>
        </View>
        <Text style={styles.meals}>{subscription.plan.meals_per_day} meals/day</Text>
        <Text style={styles.dateRange}>
          {subscription.start_date} → {subscription.end_date}
        </Text>
      </View>

      <View style={styles.mealRow}>
        <MealChip label="Breakfast" enabled={subscription.breakfast_enabled} />
        <MealChip label="Lunch" enabled={subscription.lunch_enabled} />
        <MealChip label="Dinner" enabled={subscription.dinner_enabled} />
      </View>

      <Text style={styles.sectionTitle}>Delivery Address</Text>
      <Text style={styles.addressText}>{subscription.delivery_address}</Text>

      <TouchableOpacity
        style={styles.pauseButton}
        onPress={() => {
          setPickerStep('from');
          setShowPausePicker(true);
        }}
        disabled={submittingPause}
      >
        {submittingPause ? (
          <ActivityIndicator color="#F4623A" />
        ) : (
          <Text style={styles.pauseButtonText}>⏸ Pause meals for a date range</Text>
        )}
      </TouchableOpacity>

      <Text style={styles.hint}>
        Going home or have exams? Pause your deliveries — you won't be charged or
        delivered meals during the paused period.
      </Text>

      {showPausePicker && (
        <DateTimePicker
          value={pickerStep === 'from' ? pauseFrom : pauseTo}
          mode="date"
          minimumDate={pickerStep === 'from' ? new Date() : pauseFrom}
          onChange={handlePauseDateChange}
        />
      )}
    </ScrollView>
  );
}

function MealChip({ label, enabled }) {
  return (
    <View style={[styles.mealChip, enabled ? styles.mealChipOn : styles.mealChipOff]}>
      <Text style={enabled ? styles.mealChipTextOn : styles.mealChipTextOff}>{label}</Text>
    </View>
  );
}

function statusStyle(status) {
  const map = {
    ACTIVE: { backgroundColor: '#E7F5EC' },
    PAUSED: { backgroundColor: '#FFF3E0' },
    EXPIRED: { backgroundColor: '#F2F0EC' },
    CANCELLED: { backgroundColor: '#F2F0EC' },
  };
  return map[status] || {};
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF7ED' },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24, backgroundColor: '#FFF7ED' },
  emptyTitle: { fontSize: 18, fontWeight: '700', color: '#1F1B16', marginBottom: 6 },
  emptyText: { fontSize: 14, color: '#6B6355', textAlign: 'center', marginBottom: 20 },
  ctaButton: { backgroundColor: '#F4623A', borderRadius: 10, paddingVertical: 12, paddingHorizontal: 28 },
  ctaButtonText: { color: '#fff', fontWeight: '600' },
  statusCard: {
    backgroundColor: '#fff',
    borderRadius: 14,
    padding: 20,
    borderWidth: 1,
    borderColor: '#F0E9DC',
    marginBottom: 16,
  },
  tier: { fontSize: 20, fontWeight: '700', color: '#1F1B16' },
  statusBadge: { alignSelf: 'flex-start', borderRadius: 20, paddingVertical: 4, paddingHorizontal: 12, marginTop: 8 },
  statusBadgeText: { fontSize: 12, fontWeight: '700', color: '#1F1B16' },
  meals: { fontSize: 14, color: '#6B6355', marginTop: 10 },
  dateRange: { fontSize: 12, color: '#9A9284', marginTop: 4 },
  mealRow: { flexDirection: 'row', gap: 8, marginBottom: 20 },
  mealChip: { paddingVertical: 8, paddingHorizontal: 14, borderRadius: 20, marginRight: 8 },
  mealChipOn: { backgroundColor: '#2F8F5B' },
  mealChipOff: { backgroundColor: '#F2F0EC' },
  mealChipTextOn: { color: '#fff', fontWeight: '600', fontSize: 12 },
  mealChipTextOff: { color: '#9A9284', fontSize: 12 },
  sectionTitle: { fontSize: 14, fontWeight: '700', color: '#1F1B16', marginBottom: 4 },
  addressText: { fontSize: 14, color: '#6B6355', marginBottom: 24 },
  pauseButton: {
    borderWidth: 1,
    borderColor: '#F4623A',
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
  },
  pauseButtonText: { color: '#F4623A', fontWeight: '600' },
  hint: { fontSize: 12, color: '#9A9284', marginTop: 10, lineHeight: 18 },
});