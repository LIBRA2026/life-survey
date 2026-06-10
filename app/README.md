# Flutter APP - 人生观调研

基于 Flutter 构建的人生观调研移动端应用。

## 功能特性

- 启动页展示
- 手机号+验证码登录
- 问卷列表浏览
- 问卷填写（单选/多选/量表题）
- 人生观画像结果展示
- 个人中心与历史记录

## 技术栈

- **框架**: Flutter
- **状态管理**: Provider
- **HTTP**: http package
- **本地存储**: SharedPreferences

## 安装

### 1. 确保 Flutter 环境

```bash
flutter --version
```

### 2. 安装依赖

```bash
flutter pub get
```

### 3. 运行应用

```bash
# Android模拟器
flutter run

# iOS模拟器
flutter run -d iPhone

# 真机调试
flutter run -d <设备ID>
```

## 项目结构

```
app/
├── lib/
│   ├── main.dart              # 应用入口
│   ├── models/                # 数据模型
│   │   ├── survey_model.dart  # 问卷模型
│   │   └── user_model.dart    # 用户模型
│   ├── pages/                 # 页面
│   │   ├── splash_page.dart   # 启动页
│   │   ├── login_page.dart    # 登录页
│   │   ├── home_page.dart     # 首页
│   │   ├── survey_page.dart   # 问卷填写页
│   │   ├── result_page.dart  # 结果页
│   │   └── profile_page.dart  # 个人中心
│   ├── services/              # 服务层
│   │   ├── api_service.dart   # API服务
│   │   ├── auth_service.dart  # 认证服务
│   │   └── storage_service.dart# 存储服务
│   └── utils/                  # 工具
│       ├── theme.dart          # 主题配置
│       └── config.dart         # API配置
└── pubspec.yaml               # 项目配置
```

## API配置

在 `lib/utils/config.dart` 中配置后端API地址：

```dart
static const String baseUrl = 'http://localhost:8000';
```

**注意**：
- Android模拟器使用 `10.0.2.2` 访问宿主机
- iOS模拟器使用 `localhost` 访问宿主机
- 真机调试需要使用电脑的局域网IP地址

## 默认账号

- **验证码**: `123456`（演示模式固定验证码）

## 截图预览

应用包含以下页面：
1. 启动页 - 品牌展示
2. 登录页 - 手机号验证码登录
3. 首页 - 问卷列表
4. 问卷填写页 - 逐题展示
5. 结果页 - 人生观画像
6. 个人中心 - 用户信息与历史
