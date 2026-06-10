// 
// 问卷数据模型
// 定义问卷相关的数据结构



class Survey {
  final int id;
  final String title;
  final String description;
  final String status;
  final DateTime createdAt;
  final int questionCount;
  final List<Question>? questions;
  
  Survey({
    required this.id,
    required this.title,
    required this.description,
    required this.status,
    required this.createdAt,
    required this.questionCount,
    this.questions,
  });
  
  factory Survey.fromJson(Map<String, dynamic> json) {
    return Survey(
      id: json['id'],
      title: json['title'],
      description: json['description'] ?? '',
      status: json['status'] ?? 'active',
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
      questionCount: json['question_count'] ?? 0,
      questions: json['questions'] != null
          ? (json['questions'] as List)
              .map((q) => Question.fromJson(q))
              .toList()
          : null,
    );
  }
}

class Question {
  final int id;
  final String type;  // single_choice, multiple_choice, scale
  final String content;
  final List<dynamic> options;
  final int sortOrder;
  
  Question({
    required this.id,
    required this.type,
    required this.content,
    required this.options,
    required this.sortOrder,
  });
  
  factory Question.fromJson(Map<String, dynamic> json) {
    return Question(
      id: json['id'],
      type: json['type'],
      content: json['content'],
      options: json['options'] ?? [],
      sortOrder: json['sort_order'] ?? 0,
    );
  }
  
  String get typeName {
    switch (type) {
      case 'single_choice':
        return '单选题';
      case 'multiple_choice':
        return '多选题';
      case 'scale':
        return '量表题';
      default:
        return '未知';
    }
  }
}

class SurveyAnswer {
  final int questionId;
  dynamic answer;  // 单选为int，多选为List<int>，量表为int
  
  SurveyAnswer({
    required this.questionId,
    required this.answer,
  });
  
  Map<String, dynamic> toJson() {
    return {
      'question_id': questionId,
      'answer': answer,
    };
  }
}

class HistoryItem {
  final int surveyId;
  final String surveyTitle;
  final DateTime submittedAt;
  final int totalQuestions;
  final int answeredQuestions;
  
  HistoryItem({
    required this.surveyId,
    required this.surveyTitle,
    required this.submittedAt,
    required this.totalQuestions,
    required this.answeredQuestions,
  });
  
  factory HistoryItem.fromJson(Map<String, dynamic> json) {
    return HistoryItem(
      surveyId: json['survey_id'],
      surveyTitle: json['survey_title'],
      submittedAt: DateTime.tryParse(json['submitted_at'] ?? '') ?? DateTime.now(),
      totalQuestions: json['total_questions'] ?? 0,
      answeredQuestions: json['answered_questions'] ?? 0,
    );
  }
}
