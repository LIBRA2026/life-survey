/**
 * 路由配置
 */
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    component: () => import('../components/Layout.vue'),
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'surveys',
        name: 'SurveyList',
        component: () => import('../views/SurveyList.vue'),
        meta: { title: '问卷管理' }
      },
      {
        path: 'surveys/:id/edit',
        name: 'SurveyEdit',
        component: () => import('../views/SurveyEdit.vue'),
        meta: { title: '编辑问卷' }
      },
      {
        path: 'analysis/:id',
        name: 'DataAnalysis',
        component: () => import('../views/DataAnalysis.vue'),
        meta: { title: '数据分析' }
      },
      {
        path: 'users',
        name: 'UserList',
        component: () => import('../views/UserList.vue'),
        meta: { title: '用户管理' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 人生观调研管理后台`
  }
  next()
})

export default router
