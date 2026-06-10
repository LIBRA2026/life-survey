// API服务
// 处理所有与后端的HTTP请求


import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../utils/config.dart';

class ApiService extends ChangeNotifier {
  String? _token;
  
  void setToken(String? token) {
    _token = token;
  }
  
  Future<Map<String, dynamic>> get(String path, {Map<String, String>? params}) async {
    try {
      Uri uri = Uri.parse('${ApiConfig.baseUrl}$path');
      if (params != null && params.isNotEmpty) {
        uri = uri.replace(queryParameters: params);
      }
      
      final response = await http.get(
        uri,
        headers: _getHeaders(),
      ).timeout(const Duration(milliseconds: ApiConfig.connectTimeout));
      
      return _handleResponse(response);
    } catch (e) {
      throw ApiException('网络错误: ${e.toString()}');
    }
  }
  
  Future<Map<String, dynamic>> post(String path, {Map<String, dynamic>? body}) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}$path'),
        headers: _getHeaders(),
        body: body != null ? jsonEncode(body) : null,
      ).timeout(const Duration(milliseconds: ApiConfig.connectTimeout));
      
      return _handleResponse(response);
    } catch (e) {
      throw ApiException('网络错误: ${e.toString()}');
    }
  }
  
  Future<List<dynamic>> getSurveyList() async {
    final response = await get(ApiConfig.surveys);
    return response as List<dynamic>;
  }
  
  Future<Map<String, dynamic>> getSurveyDetail(int surveyId) async {
    final response = await get(ApiConfig.surveyDetail(surveyId));
    return response as Map<String, dynamic>;
  }
  
  Future<bool> submitSurvey(int surveyId, List<Map<String, dynamic>> answers) async {
    try {
      final response = await post(
        ApiConfig.submitSurvey(surveyId),
        body: {'answers': answers},
      );
      return response['message'] == '提交成功';
    } catch (e) {
      rethrow;
    }
  }
  
  Future<Map<String, dynamic>> getProfile() async {
    final response = await get(ApiConfig.profile);
    return response as Map<String, dynamic>;
  }
  
  Future<List<dynamic>> getHistory() async {
    final response = await get(ApiConfig.history);
    return response as List<dynamic>;
  }
  
  Future<Map<String, dynamic>> getSurveyResult(int surveyId) async {
    final response = await get(ApiConfig.surveyResult(surveyId));
    return response as Map<String, dynamic>;
  }
  
  Map<String, String> _getHeaders() {
    final headers = {
      'Content-Type': 'application/json',
    };
    if (_token != null) {
      headers['Authorization'] = 'Bearer $_token';
    }
    return headers;
  }
  
  Map<String, dynamic> _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isEmpty) {
        return {};
      }
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else if (response.statusCode == 401) {
      throw ApiException('请先登录', code: 401);
    } else {
      final data = jsonDecode(response.body);
      throw ApiException(
        data['detail'] ?? '请求失败',
        code: response.statusCode,
      );
    }
  }
}

class ApiException implements Exception {
  final String message;
  final int? code;
  
  ApiException(this.message, {this.code});
  
  @override
  String toString() => message;
}
