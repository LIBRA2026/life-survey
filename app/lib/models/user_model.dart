// 
// 用户数据模型
// 定义用户相关的数据结构



class User {
  final int id;
  final String phone;
  final String nickname;
  final String avatar;
  final DateTime createdAt;
  
  User({
    required this.id,
    required this.phone,
    required this.nickname,
    required this.avatar,
    required this.createdAt,
  });
  
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      phone: json['phone'],
      nickname: json['nickname'] ?? '',
      avatar: json['avatar'] ?? '',
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'phone': phone,
      'nickname': nickname,
      'avatar': avatar,
      'created_at': createdAt.toIso8601String(),
    };
  }
}
