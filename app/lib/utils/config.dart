class ApiConfig {
  static const String baseUrl = 'https://microwave-brokers-relevant-affects.trycloudflare.com';  // 公网后端
  
  static const String apiPrefix = '/api';
  
  static const String login = '$apiPrefix/auth/login';
  static const String sendCode = '$apiPrefix/auth/send-code';
  static const String register = '$apiPrefix/auth/register';
  static const String profile = '$apiPrefix/user/profile';
  static const String history = '$apiPrefix/user/history';
  
  static const String surveys = '$apiPrefix/surveys';
  static String surveyDetail(int id) => '$apiPrefix/surveys/$id';
  static String submitSurvey(int id) => '$apiPrefix/surveys/$id/submit';
  static String surveyResult(int id) => '$apiPrefix/surveys/$id/result';
  
  static const String adminStats = '$apiPrefix/admin/stats';
  
  static const int connectTimeout = 30000;
  static const int receiveTimeout = 30000;
}
