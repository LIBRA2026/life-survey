# 后端API服务

基于 FastAPI 构建的人生观调研APP后端服务。

## 功能特性

- 用户认证（JWT）
- 问卷管理
- 答案提交
- 数据统计
- Excel数据导出

## 技术栈

- **框架**: FastAPI
- **数据库**: SQLite（开发）/ PostgreSQL（生产）
- **认证**: JWT
- **数据验证**: Pydantic

## 安装

### 1. 创建虚拟环境（推荐）

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 运行

### 1. 初始化数据库和示例数据

```bash
python init_data.py
```

这将创建SQLite数据库并初始化一套完整的人生观调研问卷（25道题目）。

### 2. 启动服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

或使用Python直接运行：

```bash
python main.py
```

### 3. 访问API文档

打开浏览器访问：http://localhost:8000/docs

## API接口

### 认证接口
- `POST /api/auth/send-code` - 发送验证码
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/me` - 获取当前用户

### 问卷接口
- `GET /api/surveys` - 获取问卷列表
- `GET /api/surveys/{id}` - 获取问卷详情
- `POST /api/surveys/{id}/submit` - 提交问卷答案
- `GET /api/user/history` - 获取参与历史
- `GET /api/surveys/{id}/result` - 获取问卷结果

### 管理接口
- `GET /api/admin/stats` - 统计概览
- `GET /api/admin/surveys` - 问卷列表（管理）
- `GET /api/admin/surveys/{id}/stats` - 问卷统计
- `GET /api/admin/users` - 用户列表
- `POST /api/admin/surveys` - 创建问卷
- `PUT /api/admin/surveys/{id}` - 更新问卷
- `POST /api/admin/surveys/{id}/questions` - 添加题目
- `DELETE /api/admin/surveys/{id}` - 删除问卷
- `GET /api/admin/export/{survey_id}` - 导出数据

## 默认账号

- **验证码**: `123456`（写死的模拟验证码）

## 目录结构

```
backend/
├── main.py           # 主入口
├── database.py       # 数据库配置
├── models.py         # ORM模型
├── schemas.py        # Pydantic模型
├── auth.py           # 认证工具
├── init_data.py      # 初始化数据
├── requirements.txt  # 依赖列表
├── routers/          # 路由模块
│   ├── __init__.py
│   ├── auth.py       # 认证路由
│   ├── survey.py     # 问卷路由
│   └── admin.py      # 管理路由
└── life_survey.db    # SQLite数据库文件
```

## 生产部署

1. 安装PostgreSQL数据库
2. 修改 `database.py` 中的 `DATABASE_URL`
3. 使用Gunicorn运行：`gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker`
