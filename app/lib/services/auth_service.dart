import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../utils/config.dart';

class AuthService extends ChangeNotifier {
  String? _token;
  Map<String, dynamic>? _userInfo;
  bool _isLoading = false;
  String? _error;
  
  String? get token => _token;
  Map<String, dynamic>? get userInfo => _userInfo;
  bool get isLoading => _isLoading;
  bool get isLoggedIn => _token != null;
  String? get error => _error;
  
  Future<void> init() async {
  }
  
  Future<bool> sendCode(String phone) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.sendCode}'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'phone': phone}),
      ).timeout(const Duration(milliseconds: ApiConfig.connectTimeout));
      
      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _error = data['detail'] ?? '发送失败';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = '网络错误，请检查网络连接';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
  
  Future<bool> login(String phone, String code) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.login}'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'phone': phone,
          'code': code,
        }),
      ).timeout(const Duration(milliseconds: ApiConfig.connectTimeout));
      
      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        _token = data['access_token'];
        _userInfo = data['user'];
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _error = data['detail'] ?? '登录失败';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = '网络错误，请检查网络连接';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
  
  Future<void> logout() async {
    _token = null;
    _userInfo = null;
    notifyListeners();
  }
  
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
