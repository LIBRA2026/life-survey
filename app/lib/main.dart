import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/auth_service.dart';
import 'services/api_service.dart';
import 'pages/splash_page.dart';
import 'pages/login_page.dart';
import 'pages/home_page.dart';
import 'pages/survey_page.dart';
import 'pages/result_page.dart';
import 'pages/profile_page.dart';
import 'utils/theme.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthService()),
        ChangeNotifierProvider(create: (_) => ApiService()),
      ],
      child: const LifeSurveyApp(),
    ),
  );
}

class LifeSurveyApp extends StatelessWidget {
  const LifeSurveyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '人生观调研',
      theme: AppTheme.lightTheme,
      debugShowCheckedModeBanner: false,
      home: const SplashPage(),
      onGenerateRoute: (settings) {
        switch (settings.name) {
          case '/login':
            return MaterialPageRoute(builder: (_) => const LoginPage());
          case '/home':
            return MaterialPageRoute(builder: (_) => const HomePage());
          case '/survey':
            final args = settings.arguments as Map<String, dynamic>?;
            return MaterialPageRoute(
              builder: (_) => SurveyPage(surveyId: args?['surveyId'] ?? 1),
            );
          case '/result':
            final args = settings.arguments as Map<String, dynamic>?;
            return MaterialPageRoute(
              builder: (_) => ResultPage(surveyId: args?['surveyId'] ?? 1),
            );
          case '/profile':
            return MaterialPageRoute(builder: (_) => const ProfilePage());
          default:
            return MaterialPageRoute(builder: (_) => const SplashPage());
        }
      },
    );
  }
}
