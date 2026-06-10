# Vue3 后台管理系统 - 人生观调研

基于 Vue3 + Element Plus 构建的后台管理系统。

## 功能特性

- 仪表盘统计
- 问卷管理（创建、编辑、删除）
- 数据分析（图表可视化）
- 用户管理
- 数据导出Excel

## 技术栈

- **框架**: Vue3 (Composition API)
- **路由**: Vue Router 4
- **UI组件**: Element Plus
- **图表**: ECharts 5
- **HTTP**: Axios
- **构建**: Vite 5

## 安装

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问地址：http://localhost:5173

### 3. 构建生产版本

```bash
npm run build
```

## 项目结构

```
admin/
├── index.html              # HTML入口
├── package.json            # 项目配置
├── vite.config.js          # Vite配置
├── src/
│   ├── main.js             # 入口文件
│   ├── App.vue             # 根组件
│   ├── style.css           # 全局样式
│   ├── api/
│   │   └── index.js        # API封装
│   ├── components/
│   │   └── Layout.vue      # 布局组件
│   ├── router/
│   │   └── index.js        # 路由配置
│   └── views/
│       ├── Login.vue        # 登录页
│       ├── Dashboard.vue    # 仪表盘
│       ├── SurveyList.vue   # 问卷列表
│       ├── SurveyEdit.vue   # 问卷编辑
│       ├── DataAnalysis.vue # 数据分析
│       └── UserList.vue     # 用户管理
└── README.md
```

## 登录说明

演示模式下，任意账号密码均可登录。

## API代理

Vite 配置了 API 代理，将 `/api` 请求转发到后端服务：

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
}
```

确保后端服务运行在 http://localhost:8000
