import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../services/api_service.dart';

class AuthProvider extends ChangeNotifier {
  final _storage = const FlutterSecureStorage();
  bool _isAuthenticated = false;
  Map<String, dynamic>? _profile;

  bool get isAuthenticated => _isAuthenticated;
  Map<String, dynamic>? get profile => _profile;

  Future<void> loginWithEmail(String email, String password) async {
    final response = await ApiService.post('/auth/login/email', {
      'email': email,
      'password': password,
    });
    await _storeTokens(response);
    _isAuthenticated = true;
    notifyListeners();
  }

  Future<void> register(String email, String password, String fullName) async {
    await ApiService.post('/auth/register', {
      'email': email,
      'password': password,
      'full_name': fullName,
    });
  }

  Future<String> initiatePhoneOtp(String phoneNumber) async {
    final response = await ApiService.post('/auth/login/phone', {
      'phone_number': phoneNumber,
    });
    return response['session'];
  }

  Future<void> verifyPhoneOtp(String phoneNumber, String otp) async {
    final response = await ApiService.post('/auth/login/phone/verify', {
      'phone_number': phoneNumber,
      'otp_code': otp,
    });
    await _storeTokens(response);
    _isAuthenticated = true;
    notifyListeners();
  }

  Future<void> loadProfile() async {
    _profile = await ApiService.get('/auth/profile');
    notifyListeners();
  }

  Future<void> logout() async {
    await ApiService.post('/auth/logout', {});
    await _storage.deleteAll();
    _isAuthenticated = false;
    _profile = null;
    notifyListeners();
  }

  Future<void> _storeTokens(Map<String, dynamic> response) async {
    await _storage.write(key: 'access_token', value: response['access_token']);
    await _storage.write(key: 'refresh_token', value: response['refresh_token']);
  }
}
