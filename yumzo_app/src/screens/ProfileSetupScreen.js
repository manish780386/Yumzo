import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import * as Location from 'expo-location';
import { updateProfile } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';

const DIET_OPTIONS = [
  { value: 'VEG', label: 'Vegetarian' },
  { value: 'NON_VEG', label: 'Non-Vegetarian' },
  { value: 'JAIN', label: 'Jain' },
  { value: 'EGG', label: 'Eggetarian' },
];

export default function ProfileSetupScreen({ navigation }) {
  const { setUser } = useAuth();
  const [firstName, setFirstName] = useState('');
  const [diet, setDiet] = useState('VEG');
  const [address, setAddress] = useState('');
  const [coords, setCoords] = useState(null);
  const [locating, setLocating] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleUseCurrentLocation = async () => {
    setLocating(true);
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission needed', 'Location permission is required to find nearby kitchens.');
        return;
      }
      const position = await Location.getCurrentPositionAsync({});
      setCoords({
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
      });

      // Reverse geocode for a human-readable address to prefill the field
      const [place] = await Location.reverseGeocodeAsync({
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
      });
      if (place) {
        setAddress(`${place.name || ''} ${place.street || ''}, ${place.city || ''}`.trim());
      }
    } catch (e) {
      Alert.alert('Error', 'Could not fetch location. Please enter your address manually.');
    } finally {
      setLocating(false);
    }
  };

  const handleSave = async () => {
    if (!firstName.trim()) {
      Alert.alert('Name required', 'Please enter your name');
      return;
    }
    if (!coords) {
      Alert.alert('Location required', 'Please share your location so we can find kitchens near you');
      return;
    }

    setSaving(true);
    try {
      const { data } = await updateProfile({
        first_name: firstName.trim(),
        diet_preference: diet,
        address_line: address,
        latitude: coords.latitude,
        longitude: coords.longitude,
      });
      setUser(data);
      navigation.replace('Home');
    } catch (e) {
      Alert.alert('Error', 'Could not save your profile. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 24 }}>
      <Text style={styles.title}>Tell us about yourself</Text>
      <Text style={styles.subtitle}>This helps us match you with the right kitchen</Text>

      <Text style={styles.label}>Your Name</Text>
      <TextInput
        style={styles.input}
        placeholder="e.g. Manish"
        value={firstName}
        onChangeText={setFirstName}
      />

      <Text style={styles.label}>Diet Preference</Text>
      <View style={styles.dietRow}>
        {DIET_OPTIONS.map((option) => (
          <TouchableOpacity
            key={option.value}
            style={[styles.dietChip, diet === option.value && styles.dietChipActive]}
            onPress={() => setDiet(option.value)}
          >
            <Text style={[styles.dietChipText, diet === option.value && styles.dietChipTextActive]}>
              {option.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.label}>Delivery Location</Text>
      <TouchableOpacity style={styles.locationButton} onPress={handleUseCurrentLocation}>
        {locating ? (
          <ActivityIndicator color="#F4623A" />
        ) : (
          <Text style={styles.locationButtonText}>
            {coords ? '📍 Location captured — tap to refresh' : '📍 Use my current location'}
          </Text>
        )}
      </TouchableOpacity>

      <TextInput
        style={styles.input}
        placeholder="PG/Hostel name, street, area"
        value={address}
        onChangeText={setAddress}
        multiline
      />

      <TouchableOpacity
        style={[styles.saveButton, saving && styles.saveButtonDisabled]}
        onPress={handleSave}
        disabled={saving}
      >
        {saving ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.saveButtonText}>Continue</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF7ED' },
  title: { fontSize: 22, fontWeight: '700', color: '#1F1B16' },
  subtitle: { fontSize: 14, color: '#6B6355', marginTop: 4, marginBottom: 24 },
  label: { fontSize: 13, fontWeight: '600', color: '#1F1B16', marginBottom: 6, marginTop: 14 },
  input: {
    borderWidth: 1,
    borderColor: '#E5DDD0',
    borderRadius: 10,
    backgroundColor: '#fff',
    padding: 14,
    fontSize: 15,
    color: '#1F1B16',
  },
  dietRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  dietChip: {
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#E5DDD0',
    backgroundColor: '#fff',
    marginRight: 8,
    marginBottom: 8,
  },
  dietChipActive: { backgroundColor: '#F4623A', borderColor: '#F4623A' },
  dietChipText: { fontSize: 13, color: '#1F1B16' },
  dietChipTextActive: { color: '#fff', fontWeight: '600' },
  locationButton: {
    borderWidth: 1,
    borderColor: '#2F8F5B',
    borderRadius: 10,
    padding: 14,
    alignItems: 'center',
    marginBottom: 12,
  },
  locationButtonText: { color: '#2F8F5B', fontWeight: '600' },
  saveButton: {
    backgroundColor: '#F4623A',
    borderRadius: 10,
    paddingVertical: 15,
    alignItems: 'center',
    marginTop: 28,
  },
  saveButtonDisabled: { opacity: 0.6 },
  saveButtonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
});