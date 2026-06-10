// 
// 存储服务
// 处理本地存储功能


import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  static const String _tokenKey = 'auth_token';
  static const String _userKey = 'user_info';
  static const String _surveyCacheKey = 'survey_cache';
  
  late SharedPreferences _prefs;
  
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }
  
  Future<void> saveToken(String token) async {
    await _prefs.setString(_tokenKey, token);
  }
  
  String? getToken() {
    return _prefs.getString(_tokenKey);
  }
  
  Future<void> removeToken() async {
    await _prefs.remove(_tokenKey);
  }
  
  Future<void> saveUser(Map<String, dynamic> user) async {
    await _prefs.setString(_userKey, user.toString());
  }
  
  Map<String, dynamic>? getUser() {
    final userStr = _prefs.getString(_userKey);
    if (userStr == null) return null;
    return {};
  }
  
  Future<void> removeUser() async {
    await _prefs.remove(_userKey);
  }
  
  Future<void> cacheSurvey(int surveyId, String data) async {
    await _prefs.setString('${_surveyCacheKey}_$surveyId', data);
  }
  
  String? getCachedSurvey(int surveyId) {
    return _prefs.getString('${_surveyCacheKey}_$surveyId');
  }
  
  Future<void> clearCache() async {
    await _prefs.clear();
  }
}
