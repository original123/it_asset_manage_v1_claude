<template>
  <div class="main-layout">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="header-left">
        <div class="logo">
          <svg viewBox="0 0 32 32" fill="none" class="logo-icon">
            <rect x="2" y="6" width="28" height="20" rx="2" stroke="currentColor" stroke-width="1.5"/>
            <rect x="5" y="10" width="8" height="5" rx="1" fill="currentColor" opacity="0.6"/>
            <rect x="5" y="17" width="8" height="5" rx="1" fill="currentColor" opacity="0.4"/>
            <line x1="16" y1="10" x2="27" y2="10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="16" y1="14" x2="24" y2="14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>
            <line x1="16" y1="18" x2="27" y2="18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="16" y1="22" x2="21" y2="22" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>
          </svg>
          <span class="logo-text">IT Asset Manager</span>
        </div>
      </div>

      <div class="header-center">
        <nav class="main-nav">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: isActive(item.path) }"
          >
            <el-icon class="nav-icon"><component :is="item.icon" /></el-icon>
            <span>{{ item.label }}</span>
          </router-link>
        </nav>
      </div>

      <div class="header-right">
        <!-- 全局搜索 -->
        <div class="search-wrapper">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索 IP / 端口 / 名称..."
            :prefix-icon="Search"
            class="global-search"
            @keyup.enter="handleSearch"
            clearable
          />
        </div>

        <!-- 用户菜单 -->
        <el-dropdown trigger="click" @command="handleUserCommand">
          <div class="user-menu">
            <el-avatar :size="32" class="user-avatar">
              {{ userInitial }}
            </el-avatar>
            <span class="user-name">{{ authStore.user?.display_name }}</span>
            <el-icon class="arrow"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item disabled>
                <span class="dropdown-label">{{ authStore.user?.username }}</span>
                <el-tag size="small" :type="authStore.isAdmin ? 'danger' : 'info'">
                  {{ authStore.isAdmin ? '管理员' : '用户' }}
                </el-tag>
              </el-dropdown-item>
              <el-dropdown-item divided command="settings" v-if="authStore.isAdmin">
                <el-icon><Setting /></el-icon>
                系统设置
              </el-dropdown-item>
              <el-dropdown-item command="password">
                <el-icon><Key /></el-icon>
                修改密码
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 系统设置弹窗 -->
    <SettingsDialog v-model="settingsVisible" />

    <!-- 修改密码弹窗 -->
    <PasswordDialog v-model="passwordVisible" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Search, ArrowDown, Setting, Key, SwitchButton,
  Monitor, DataBoard, Document, FolderOpened
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import SettingsDialog from '@/components/SettingsDialog.vue'
import PasswordDialog from '@/components/PasswordDialog.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const searchKeyword = ref('')
const settingsVisible = ref(false)
const passwordVisible = ref(false)

const navItems = [
  { path: '/explorer', label: '资产浏览器', icon: FolderOpened },
  { path: '/assets', label: '资产管理', icon: Monitor },
  { path: '/overview', label: '机房总览', icon: DataBoard },
  { path: '/audit', label: '审计日志', icon: Document }
]

const userInitial = computed(() => {
  const name = authStore.user?.display_name || ''
  return name.charAt(0).toUpperCase()
})

const isActive = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push({ path: '/assets', query: { keyword: searchKeyword.value } })
  }
}

const handleUserCommand = (command) => {
  switch (command) {
    case 'settings':
      settingsVisible.value = true
      break
    case 'password':
      passwordVisible.value = true
      break
    case 'logout':
      authStore.logout()
      break
  }
}
</script>

<style lang="scss" scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500&family=Inter:wght@400;500;600&display=swap');

.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}

// 顶部导航
.header {
  height: 60px;
  background: linear-gradient(135deg, #1a1f2e 0%, #252b3d 100%);
  display: flex;
  align-items: center;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.header-left {
  flex-shrink: 0;

  .logo {
    display: flex;
    align-items: center;
    gap: 10px;

    .logo-icon {
      width: 28px;
      height: 28px;
      color: #00d4ff;
    }

    .logo-text {
      font-family: 'Orbitron', sans-serif;
      font-size: 15px;
      font-weight: 500;
      color: #fff;
      letter-spacing: 1px;
    }
  }
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;

  .main-nav {
    display: flex;
    gap: 8px;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 20px;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.6);
    text-decoration: none;
    transition: all 0.2s;

    .nav-icon {
      font-size: 16px;
    }

    &:hover {
      color: #fff;
      background: rgba(255, 255, 255, 0.08);
    }

    &.active {
      color: #00d4ff;
      background: rgba(0, 212, 255, 0.1);
    }
  }
}

.header-right {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 16px;

  .search-wrapper {
    .global-search {
      width: 260px;

      :deep(.el-input__wrapper) {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        box-shadow: none;

        &:hover {
          border-color: rgba(255, 255, 255, 0.2);
        }

        &.is-focus {
          background: rgba(255, 255, 255, 0.12);
          border-color: rgba(0, 212, 255, 0.5);
        }
      }

      :deep(.el-input__inner) {
        color: #fff;
        font-size: 13px;

        &::placeholder {
          color: rgba(255, 255, 255, 0.4);
        }
      }

      :deep(.el-input__prefix) {
        color: rgba(255, 255, 255, 0.4);
      }
    }
  }

  .user-menu {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.2s;

    &:hover {
      background: rgba(255, 255, 255, 0.08);
    }

    .user-avatar {
      background: linear-gradient(135deg, #00d4ff, #0099cc);
      font-family: 'Inter', sans-serif;
      font-weight: 600;
      font-size: 13px;
    }

    .user-name {
      color: #fff;
      font-family: 'Inter', sans-serif;
      font-size: 13px;
      font-weight: 500;
    }

    .arrow {
      color: rgba(255, 255, 255, 0.5);
      font-size: 12px;
    }
  }
}

.dropdown-label {
  margin-right: 8px;
}

// 主内容
.main-content {
  flex: 1;
  padding: 24px;
  overflow: auto;
}

// 过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
