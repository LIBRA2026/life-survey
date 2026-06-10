// 问卷填写页面
// 逐题展示问卷内容

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../models/survey_model.dart';
import '../utils/theme.dart';
import 'result_page.dart';

class SurveyPage extends StatefulWidget {
  final int surveyId;

  const SurveyPage({super.key, required this.surveyId});

  @override
  State<SurveyPage> createState() => _SurveyPageState();
}

class _SurveyPageState extends State<SurveyPage> {
  Survey? _survey;
  int _currentIndex = 0;
  Map<int, dynamic> _answers = {};
  bool _isLoading = true;
  bool _isSubmitting = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadSurvey();
  }

  Future<void> _loadSurvey() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final authService = Provider.of<AuthService>(context, listen: false);
      final apiService = Provider.of<ApiService>(context, listen: false);
      apiService.setToken(authService.token);

      final data = await apiService.getSurveyDetail(widget.surveyId);
      setState(() {
        _survey = Survey.fromJson(data);
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  void _selectAnswer(int questionId, dynamic answer) {
    setState(() {
      _answers[questionId] = answer;
    });
  }

  void _toggleMultiChoice(int questionId, int optionIndex) {
    final current = List<int>.from(_answers[questionId] as List? ?? []);
    setState(() {
      if (current.contains(optionIndex)) {
        current.remove(optionIndex);
      } else {
        current.add(optionIndex);
      }
      _answers[questionId] = current;
    });
  }

  void _nextQuestion() {
    if (_survey == null) return;
    final question = _survey!.questions![_currentIndex];

    if (_answers[question.id] == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请先选择答案'), backgroundColor: AppTheme.warningColor),
      );
      return;
    }

    if (_currentIndex < _survey!.questions!.length - 1) {
      setState(() {
        _currentIndex++;
      });
    }
  }

  void _previousQuestion() {
    if (_currentIndex > 0) {
      setState(() {
        _currentIndex--;
      });
    }
  }

  Future<void> _submitSurvey() async {
    if (_survey == null) return;
    final question = _survey!.questions![_currentIndex];

    if (_answers[question.id] == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请先选择答案'), backgroundColor: AppTheme.warningColor),
      );
      return;
    }

    setState(() {
      _isSubmitting = true;
    });

    try {
      final authService = Provider.of<AuthService>(context, listen: false);
      final apiService = Provider.of<ApiService>(context, listen: false);
      apiService.setToken(authService.token);

      final answersList = _answers.entries
          .map((e) => SurveyAnswer(questionId: e.key, answer: e.value).toJson())
          .toList();

      await apiService.submitSurvey(widget.surveyId, answersList);

      if (mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => ResultPage(surveyId: widget.surveyId),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString()), backgroundColor: AppTheme.errorColor),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: const Text('加载中...')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_error != null) {
      return Scaffold(
        appBar: AppBar(title: const Text('问卷')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: AppTheme.errorColor),
              const SizedBox(height: 16),
              Text(_error!, textAlign: TextAlign.center),
              const SizedBox(height: 16),
              ElevatedButton(onPressed: _loadSurvey, child: const Text('重试')),
            ],
          ),
        ),
      );
    }

    if (_survey == null || _survey!.questions == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('问卷')),
        body: const Center(child: Text('问卷内容为空')),
      );
    }

    final questions = _survey!.questions!;
    final currentQuestion = questions[_currentIndex];
    final progress = (_currentIndex + 1) / questions.length;

    return Scaffold(
      appBar: AppBar(
        title: Text(_survey!.title),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Column(
        children: [
          LinearProgressIndicator(
            value: progress,
            backgroundColor: AppTheme.textHint.withOpacity(0.2),
            valueColor: const AlwaysStoppedAnimation<Color>(AppTheme.primaryColor),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '第${_currentIndex + 1}题 / 共${questions.length}题',
                  style: const TextStyle(color: AppTheme.textSecondary, fontWeight: FontWeight.w500),
                ),
                Text(
                  '${(progress * 100).toInt()}%',
                  style: const TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: _buildQuestionCard(currentQuestion),
            ),
          ),
          _buildBottomButtons(questions),
        ],
      ),
    );
  }

  Widget _buildQuestionCard(Question question) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: _getQuestionTypeColor(question.type).withOpacity(0.1),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                question.typeName,
                style: TextStyle(
                  color: _getQuestionTypeColor(question.type),
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              question.content,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600, height: 1.5),
            ),
            const SizedBox(height: 24),
            ..._buildOptions(question),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildOptions(Question question) {
    switch (question.type) {
      case 'single_choice':
        return _buildSingleChoiceOptions(question);
      case 'multiple_choice':
        return _buildMultipleChoiceOptions(question);
      case 'scale':
        return _buildScaleOptions(question);
      default:
        return [const Text('不支持的题目类型')];
    }
  }

  List<Widget> _buildSingleChoiceOptions(Question question) {
    final selected = _answers[question.id] as int?;
    return question.options.asMap().entries.map((entry) {
      final index = entry.key;
      final option = entry.value.toString();
      final isSelected = selected == index;
      return Padding(
        padding: const EdgeInsets.only(bottom: 12),
        child: InkWell(
          onTap: () => _selectAnswer(question.id, index),
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isSelected ? AppTheme.primaryColor.withOpacity(0.1) : Colors.grey.withOpacity(0.05),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: isSelected ? AppTheme.primaryColor : Colors.grey.withOpacity(0.2),
                width: isSelected ? 2 : 1,
              ),
            ),
            child: Row(
              children: [
                Container(
                  width: 24, height: 24,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isSelected ? AppTheme.primaryColor : Colors.transparent,
                    border: Border.all(
                      color: isSelected ? AppTheme.primaryColor : AppTheme.textHint, width: 2,
                    ),
                  ),
                  child: isSelected ? const Icon(Icons.check, size: 14, color: Colors.white) : null,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    option,
                    style: TextStyle(
                      fontSize: 15,
                      color: isSelected ? AppTheme.primaryColor : AppTheme.textPrimary,
                      fontWeight: isSelected ? FontWeight.w500 : FontWeight.normal,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }).toList();
  }

  List<Widget> _buildMultipleChoiceOptions(Question question) {
    final selected = List<int>.from(_answers[question.id] as List? ?? []);
    List<Widget> widgets = [];
    widgets.add(Text('（可多选）', style: TextStyle(color: AppTheme.textHint, fontSize: 13)));
    widgets.add(const SizedBox(height: 8));
    for (var entry in question.options.asMap().entries) {
      final index = entry.key;
      final option = entry.value.toString();
      final isSelected = selected.contains(index);
      widgets.add(Padding(
        padding: const EdgeInsets.only(bottom: 12),
        child: InkWell(
          onTap: () => _toggleMultiChoice(question.id, index),
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isSelected ? AppTheme.secondaryColor.withOpacity(0.1) : Colors.grey.withOpacity(0.05),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: isSelected ? AppTheme.secondaryColor : Colors.grey.withOpacity(0.2),
                width: isSelected ? 2 : 1,
              ),
            ),
            child: Row(
              children: [
                Container(
                  width: 24, height: 24,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(6),
                    color: isSelected ? AppTheme.secondaryColor : Colors.transparent,
                    border: Border.all(
                      color: isSelected ? AppTheme.secondaryColor : AppTheme.textHint, width: 2,
                    ),
                  ),
                  child: isSelected ? const Icon(Icons.check, size: 14, color: Colors.white) : null,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    option,
                    style: TextStyle(
                      fontSize: 15,
                      color: isSelected ? AppTheme.secondaryColor : AppTheme.textPrimary,
                      fontWeight: isSelected ? FontWeight.w500 : FontWeight.normal,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ));
    }
    return widgets;
  }

  List<Widget> _buildScaleOptions(Question question) {
    final selected = _answers[question.id] as int?;
    return [
      Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: const [
          Text('非常不同意', style: TextStyle(color: AppTheme.textHint, fontSize: 12)),
          Text('非常同意', style: TextStyle(color: AppTheme.textHint, fontSize: 12)),
        ],
      ),
      const SizedBox(height: 12),
      Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: List.generate(5, (index) {
          final value = index + 1;
          final isSelected = selected == value;
          return InkWell(
            onTap: () => _selectAnswer(question.id, value),
            borderRadius: BorderRadius.circular(12),
            child: Container(
              width: 56, height: 56,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isSelected ? AppTheme.primaryColor : Colors.grey.withOpacity(0.1),
                border: Border.all(
                  color: isSelected ? AppTheme.primaryColor : AppTheme.textHint.withOpacity(0.3), width: 2,
                ),
              ),
              child: Center(
                child: Text(
                  '$value',
                  style: TextStyle(
                    fontSize: 18, fontWeight: FontWeight.bold,
                    color: isSelected ? Colors.white : AppTheme.textPrimary,
                  ),
                ),
              ),
            ),
          );
        }),
      ),
      const SizedBox(height: 16),
      Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppTheme.primaryColor.withOpacity(0.05),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            const Icon(Icons.info_outline, size: 16, color: AppTheme.primaryColor),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                selected != null ? '您的选择：$selected' : '请选择1-5之间的数值',
                style: const TextStyle(color: AppTheme.primaryColor, fontSize: 13),
              ),
            ),
          ],
        ),
      ),
    ];
  }

  Color _getQuestionTypeColor(String type) {
    switch (type) {
      case 'single_choice': return AppTheme.primaryColor;
      case 'multiple_choice': return AppTheme.secondaryColor;
      case 'scale': return AppTheme.accentColor;
      default: return AppTheme.textSecondary;
    }
  }

  Widget _buildBottomButtons(List<Question> questions) {
    final isLastQuestion = _currentIndex == questions.length - 1;
    final isFirstQuestion = _currentIndex == 0;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, -5)),
        ],
      ),
      child: Row(
        children: [
          if (!isFirstQuestion)
            Expanded(child: OutlinedButton(onPressed: _previousQuestion, child: const Text('上一题'))),
          if (!isFirstQuestion) const SizedBox(width: 16),
          Expanded(
            flex: isFirstQuestion ? 2 : 1,
            child: ElevatedButton(
              onPressed: _isSubmitting ? null : (isLastQuestion ? _submitSurvey : _nextQuestion),
              child: _isSubmitting
                  ? const SizedBox(
                      width: 20, height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2, valueColor: AlwaysStoppedAnimation<Color>(Colors.white)),
                    )
                  : Text(isLastQuestion ? '提交问卷' : '下一题'),
            ),
          ),
        ],
      ),
    );
  }
}
