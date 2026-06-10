# 人生观调研APP

## 当前部署状态 ✅

### 后端API
- **地址**: https://functional-problems-delivering-pas.trycloudflare.com
- **API文档**: https://functional-problems-delivering-pas.trycloudflare.com/docs
- **健康检查**: https://functional-problems-delivering-pas.trycloudflare.com/health

### 后台管理系统
- **地址**: https://functional-problems-delivering-pas.trycloudflare.com/admin
- **用户名**: admin
- **密码**: admin

### Flutter APP
- 源码在 `app/` 目录
- 已配置连接上述后端API地址
- 构建方式见下方说明

---

## 系统架构

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│  Flutter APP │────▶│  FastAPI后端  │────▶│   SQLite数据库   │
│  (用户端)     │     │  (API服务)    │     │                │
└─────────────┘     └──────┬───────┘     └────────────────┘
                           │
                    ┌──────▼───────┐
                    │  Vue3后台管理  │
                    │  (管理端)     │
                    └──────────────┘
```

## 快速启动

### 1. 启动后端
```bash
cd backend
pip install -r requirements.txt
python init_data.py    # 初始化问卷数据 + admin用户
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 访问后台管理
后台管理已集成在后端中，直接访问 http://localhost:8000/admin
- 用户名: admin
- 密码: admin

### 3. 构建Flutter APP
```bash
cd app
flutter pub get
flutter run                    # 调试模式
flutter build apk --release    # 构建Android APK
flutter build web --release    # 构建Web版本
```

## API接口

| 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|
| /api/auth/login | POST | 手机号+验证码登录 | 否 |
| /api/auth/admin/login | POST | 管理员登录 | 否 |
| /api/surveys | GET | 问卷列表 | 是 |
| /api/surveys/{id} | GET | 问卷详情 | 是 |
| /api/surveys/{id}/submit | POST | 提交答案 | 是 |
| /api/admin/stats | GET | 统计概览 | 是(管理员) |
| /api/admin/surveys/{id}/stats | GET | 单问卷统计 | 是(管理员) |
| /api/admin/users | GET | 用户列表 | 是(管理员) |

## 初始数据

- 1套人生观调研问卷（25道题，7个维度）
- 管理员账户: admin/admin

## 注意事项

- 当前使用Cloudflare Tunnel暴露服务，URL可能随重启变化
- 生产环境建议部署到正式服务器（Render/Railway/阿里云等）
- 数据库使用SQLite，生产环境建议切换为PostgreSQL
- 验证码为模拟方式（固定123456），生产环境需接入短信服务
