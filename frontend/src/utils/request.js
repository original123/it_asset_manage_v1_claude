import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 直接从 localStorage 获取 token
    const token = localStorage.getItem('token')
    console.log('Request interceptor - URL:', config.url, 'Token exists:', !!token)
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const { response } = error
    if (response) {
      const { status, data } = response
      if (status === 401) {
        // 只有非登录请求才清除 token 并跳转
        if (!response.config.url.includes('/auth/login')) {
          localStorage.removeItem('token')
          router.push('/login')
          ElMessage.error('登录已过期，请重新登录')
        }
      } else if (status === 403) {
        ElMessage.error('无权限执行此操作')
      } else if (status === 404) {
        ElMessage.error('资源不存在')
      } else {
        ElMessage.error(data?.message || '请求失败')
      }
      return Promise.reject(data)
    }
    ElMessage.error('网络错误，请检查网络连接')
    return Promise.reject(error)
  }
)

export default request
