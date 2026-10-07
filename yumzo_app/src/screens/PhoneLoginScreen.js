import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { requestOTP } from '../api/endpoints';

export default function PhoneLoginScreen({ navigation }) {
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSendOTP = async () => {
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length !== 10) {
      Alert.alert('Invalid number', 'Enter a valid 10-digit phone number');
      return;
    }

    setLoading(true);
    try {
      const { data } = await requestOTP(cleaned);
      // TEMPORARY: backend has no SMS gateway yet, so it returns the OTP in
      // the response (otp_debug) instead of texting it. Remove this Alert
      // once MSG91/Twilio is integrated — see RequestOTPView in users/views.py.
      if (data.otp_debug) {
        Alert.alert('Dev Mode — OTP', `Your OTP is: ${data.otp_debug}`);
      }
      navigation.navigate('OTPVerify', { phone: cleaned });
    } catch (error) {
      Alert.alert('Error', 'Could not send OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <Text style={styles.logo}>Yumzo</Text>
      <Text style={styles.subtitle}>Ghar jaisa khana, roz.</Text>

      <Text style={styles.label}>Phone Number</Text>
      <View style={styles.inputRow}>
        <Text style={styles.prefix}>+91</Text>
        <TextInput
          style={styles.input}
          placeholder="98765 43210"
          keyboardType="phone-pad"
          maxLength={10}
          value={phone}
          onChangeText={setPhone}
        />
      </View>

      <TouchableOpacity
        style={[styles.button, loading && styles.buttonDisabled]}
        onPress={handleSendOTP}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Send OTP</Text>
        )}
      </TouchableOpacity>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 24, backgroundColor: '#FFF7ED' },
  logo: { fontSize: 36, fontWeight: '700', color: '#F4623A', textAlign: 'center' },
  subtitle: { fontSize: 14, color: '#6B6355', textAlign: 'center', marginBottom: 40 },
  label: { fontSize: 13, color: '#1F1B16', marginBottom: 6 },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5DDD0',
    borderRadius: 10,
    backgroundColor: '#fff',
    marginBottom: 24,
  },
  prefix: { paddingLeft: 14, fontSize: 16, color: '#1F1B16' },
  input: { flex: 1, padding: 14, fontSize: 16, color: '#1F1B16' },
  button: {
    backgroundColor: '#F4623A',
    borderRadius: 10,
    paddingVertical: 15,
    alignItems: 'center',
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
});