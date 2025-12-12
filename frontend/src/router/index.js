import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/assets'
      },
      {
        path: 'assets',
        name: 'Assets',
        component: () => import('@/views/Assets.vue'),
        meta: { title: '资产管理' }
      },
      {
        path: 'overview',
        name: 'Overview',
        component: () => import('@/views/Overview.vue'),
        meta: { title: '机房总览' }
      },
      {
        path: 'audit',
        name: 'Audit',
        component: () => import('@/views/Audit.vue'),
        meta: { title: '审计日志' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 等待 token 就绪的辅助函数
const waitForToken = async (maxWait = 500) => {
  const start = Date.now()
  while (!localStorage.getItem('token') && Date.now() - start < maxWait) {
    await new Promise(resolve => setTimeout(resolve, 20))
  }
  return !!localStorage.getItem('token')
}

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 如果是从登录页跳转过来，等待 token 就绪
  if (from.name === 'Login' && to.meta.requiresAuth !== false) {
    await waitForToken()
  }

  if (to.meta.requiresAuth !== false && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ path: '/' })
  } else {
    next()
  }
})

export default router
