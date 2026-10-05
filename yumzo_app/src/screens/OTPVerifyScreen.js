import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import { requestOTP } from '../api/endpoints';

export default function OTPVerifyScreen({ route, navigation }) {
  const { phone } = route.params;
  const { login } = useAuth();
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const inputRef = useRef(null);

  const handleVerify = async () => {
    if (otp.length !== 6) {
      Alert.alert('Invalid OTP', 'Enter the 6-digit code sent to your phone');
      return;
    }

    setLoading(true);
    try {
      const data = await login(phone, otp);
      // AuthContext now holds the user; RootNavigator switches to the app stack
      // automatically based on `user` being set — nothing else to do here.
      if (data.is_new_user) {
        navigation.replace('ProfileSetup');
      }
    } catch (error) {
      Alert.alert('Error', 'Incorrect or expired OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setResending(true);
    try {
      await requestOTP(phone);
      Alert.alert('OTP Sent', 'A new OTP has been sent to your phone');
    } catch (error) {
      Alert.alert('Error', 'Could not resend OTP');
    } finally {
      setResending(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Verify your number</Text>
      <Text style={styles.subtitle}>Enter the 6-digit code sent to +91 {phone}</Text>

      <TextInput
        ref={inputRef}
        style={styles.otpInput}
        placeholder="------"
        keyboardType="number-pad"
        maxLength={6}
        value={otp}
        onChangeText={setOtp}
        autoFocus
      />

      <TouchableOpacity
        style={[styles.button, loading && styles.buttonDisabled]}
        onPress={handleVerify}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Verify & Continue</Text>
        )}
      </TouchableOpacity>

      <TouchableOpacity onPress={handleResend} disabled={resending} style={styles.resendBtn}>
        <Text style={styles.resendText}>
          {resending ? 'Sending...' : "Didn't get the code? Resend"}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 24, backgroundColor: '#FFF7ED' },
  title: { fontSize: 22, fontWeight: '700', color: '#1F1B16', textAlign: 'center' },
  subtitle: { fontSize: 14, color: '#6B6355', textAlign: 'center', marginTop: 8, marginBottom: 32 },
  otpInput: {
    borderWidth: 1,
    borderColor: '#E5DDD0',
    borderRadius: 10,
    backgroundColor: '#fff',
    padding: 16,
    fontSize: 24,
    letterSpacing: 12,
    textAlign: 'center',
    marginBottom: 24,
  },
  button: {
    backgroundColor: '#F4623A',
    borderRadius: 10,
    paddingVertical: 15,
    alignItems: 'center',
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  resendBtn: { marginTop: 20, alignItems: 'center' },
  resendText: { color: '#2F8F5B', fontSize: 14, fontWeight: '500' },
});