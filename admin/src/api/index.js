/**
 * API 封装
 * 基于 Axios 的 HTTP 请求工具
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 后端API地址（同域名部署，使用相对路径）
const API_BASE = ''

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE + '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// 管理员登录
export const adminLogin = (data) => {
  return axios.post(API_BASE + '/api/auth/admin/login', data, {
    headers: { 'Content-Type': 'application/json' }
  }).then(res => res.data)
}

// ============ 统计相关 ============
export const getStats = () => api.get('/admin/stats')

// ============ 问卷相关 ============
export const getSurveyList = (params) => api.get('/admin/surveys', { params })
export const createSurvey = (data) => api.post('/admin/surveys', null, { params: data })
export const updateSurvey = (id, data) => api.put(`/admin/surveys/${id}`, null, { params: data })
export const deleteSurvey = (id) => api.delete(`/admin/surveys/${id}`)
export const getSurveyStats = (id) => api.get(`/admin/surveys/${id}/stats`)

// ============ 用户相关 ============
export const getUserList = (params) => api.get('/admin/users', { params })

// ============ 导出相关 ============
export const exportSurveyData = (surveyId) => {
  return api.get(`/admin/export/${surveyId}`, {
    responseType: 'blob'
  })
}

export default api
