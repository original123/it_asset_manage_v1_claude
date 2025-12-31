<template>
  <div class="asset-explorer">
    <!-- 顶部工具栏 -->
    <div class="top-toolbar">
      <div class="toolbar-left">
        <span class="app-title">
          <el-icon><FolderOpened /></el-icon>
          IT资产管理器
        </span>
      </div>

      <div class="toolbar-center">
        <el-autocomplete
          v-model="searchKeyword"
          :fetch-suggestions="fetchSuggestions"
          placeholder="搜索资产... (Ctrl+K)"
          clearable
          class="search-input"
          :trigger-on-focus="true"
          :debounce="300"
          @select="handleSelectSuggestion"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
          <template #default="{ item }">
            <div class="search-suggestion-item">
              <el-icon v-if="item.type === 'history'" class="suggestion-icon history">
                <Clock />
              </el-icon>
              <el-icon v-else-if="item.type === 'server'" class="suggestion-icon server">
                <Monitor />
              </el-icon>
              <el-icon v-else-if="item.type === 'container'" class="suggestion-icon container">
                <Box />
              </el-icon>
              <el-icon v-else class="suggestion-icon">
                <Document />
              </el-icon>
              <div class="suggestion-content">
                <span class="suggestion-name">{{ item.name }}</span>
                <span class="suggestion-desc">{{ item.description }}</span>
              </div>
              <el-button
                v-if="item.type === 'history'"
                type="text"
                size="small"
                class="remove-history-btn"
                @click.stop="removeHistoryItem(item.value)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </template>
        </el-autocomplete>
      </div>

      <div class="toolbar-right">
        <!-- 筛选下拉 -->
        <el-select
          v-model="filterEnvironment"
          placeholder="环境"
          clearable
          size="default"
          class="filter-select"
        >
          <el-option
            v-for="env in explorerStore.environments"
            :key="env.id"
            :label="env.name"
            :value="env.id"
          />
        </el-select>

        <el-select
          v-model="filterDatacenter"
          placeholder="机房"
          clearable
          size="default"
          class="filter-select"
        >
          <el-option
            v-for="dc in explorerStore.datacenters"
            :key="dc.id"
            :label="dc.name"
            :value="dc.id"
          />
        </el-select>

        <!-- 视图切换 -->
        <el-button-group class="view-toggle">
          <el-tooltip content="列表视图" placement="bottom">
            <el-button
              :type="explorerStore.viewMode === 'list' ? 'primary' : 'default'"
              @click="explorerStore.setViewMode('list')"
            >
              <el-icon><List /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="网格视图" placement="bottom">
            <el-button
              :type="explorerStore.viewMode === 'grid' ? 'primary' : 'default'"
              @click="explorerStore.setViewMode('grid')"
            >
              <el-icon><Grid /></el-icon>
            </el-button>
          </el-tooltip>
        </el-button-group>

        <!-- 新增按钮 -->
        <el-button type="primary" @click="showAddServerDialog" v-if="authStore.isAdmin">
          <el-icon><Plus /></el-icon>
          添加服务器
        </el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧导航面板 -->
      <div
        class="navigation-panel"
        :style="{ width: explorerStore.preferences.panelWidth + 'px' }"
      >
        <NavigationPanel />
      </div>

      <!-- 可拖拽分隔线 -->
      <div
        class="resizer"
        @mousedown="startResize"
      />

      <!-- 右侧内容面板 -->
      <div class="content-panel">
        <!-- 面包屑导航 -->
        <Breadcrumb />

        <!-- 内容展示区 -->
        <ContentArea />

        <!-- 详情/操作栏 -->
        <DetailBar v-if="explorerStore.preferences.showDetailBar" />
      </div>
    </div>

    <!-- 底部状态栏 -->
    <StatusBar />

    <!-- 服务器表单弹窗 -->
    <ServerFormDialog
      v-model="serverFormVisible"
      :server="null"
      @success="handleRefresh"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { FolderOpened, Search, List, Grid, Plus, Clock, Delete, Monitor, Box, Document } from '@element-plus/icons-vue'
import { useExplorerStore } from '@/stores/explorer'
import { useAuthStore } from '@/stores/auth'
import { assetsApi } from '@/api/assets'
import NavigationPanel from './NavigationPanel.vue'
import Breadcrumb from './Breadcrumb.vue'
import ContentArea from './ContentArea.vue'
import DetailBar from './DetailBar.vue'
import StatusBar from './StatusBar.vue'
import ServerFormDialog from '@/components/ServerFormDialog.vue'

const explorerStore = useExplorerStore()
const authStore = useAuthStore()

// 搜索和筛选
const searchKeyword = ref('')
const filterEnvironment = ref(null)
const filterDatacenter = ref(null)

// 搜索增强
const searchSuggestions = ref([])
const searchHistory = ref([])
const showSearchDropdown = ref(false)
const searchLoading = ref(false)
const SEARCH_HISTORY_KEY = 'asset_search_history'
const MAX_HISTORY_ITEMS = 10

// 加载搜索历史
function loadSearchHistory() {
  try {
    const saved = localStorage.getItem(SEARCH_HISTORY_KEY)
    if (saved) {
      searchHistory.value = JSON.parse(saved)
    }
  } catch (e) {
    console.warn('加载搜索历史失败:', e)
  }
}

// 保存搜索历史
function saveSearchHistory(keyword) {
  if (!keyword || keyword.trim().length < 2) return
  const trimmed = keyword.trim()
  // 移除重复项
  searchHistory.value = searchHistory.value.filter(h => h !== trimmed)
  // 添加到开头
  searchHistory.value.unshift(trimmed)
  // 限制数量
  if (searchHistory.value.length > MAX_HISTORY_ITEMS) {
    searchHistory.value = searchHistory.value.slice(0, MAX_HISTORY_ITEMS)
  }
  // 保存到 localStorage
  try {
    localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(searchHistory.value))
  } catch (e) {
    console.warn('保存搜索历史失败:', e)
  }
}

// 清除搜索历史
function clearSearchHistory() {
  searchHistory.value = []
  localStorage.removeItem(SEARCH_HISTORY_KEY)
}

// 删除单条搜索历史
function removeHistoryItem(keyword) {
  searchHistory.value = searchHistory.value.filter(h => h !== keyword)
  try {
    localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(searchHistory.value))
  } catch (e) {
    console.warn('保存搜索历史失败:', e)
  }
}

// 获取搜索建议
async function fetchSuggestions(queryString, cb) {
  if (!queryString || queryString.trim().length < 2) {
    // 显示搜索历史
    const historyItems = searchHistory.value.map(h => ({
      value: h,
      type: 'history',
      name: h,
      description: '搜索历史'
    }))
    cb(historyItems)
    return
  }

  searchLoading.value = true
  try {
    const res = await assetsApi.quickSearch(queryString.trim())
    if (res.code === 0 && res.data) {
      const suggestions = res.data.map(item => ({
        value: item.name,
        type: item.type,
        id: item.id,
        name: item.name,
        description: item.description
      }))
      cb(suggestions)
    } else {
      cb([])
    }
  } catch (e) {
    console.warn('获取搜索建议失败:', e)
    cb([])
  } finally {
    searchLoading.value = false
  }
}

// 选择搜索建议
async function handleSelectSuggestion(item) {
  if (!item) return

  // 保存到搜索历史
  saveSearchHistory(item.value)

  // 如果是资产建议，直接导航到该资产
  if (item.type === 'server') {
    await explorerStore.loadServerContent(item.id)
  } else if (item.type === 'container') {
    // 容器需要先加载所属服务器
    // 暂时只执行搜索
    executeSearch(item.value)
  } else if (item.type === 'history') {
    // 历史记录，执行搜索
    searchKeyword.value = item.value
    executeSearch(item.value)
  } else {
    executeSearch(item.value)
  }
}

// 执行搜索
async function executeSearch(keyword) {
  if (!keyword || keyword.trim().length < 1) return

  const trimmed = keyword.trim()
  saveSearchHistory(trimmed)

  try {
    const res = await assetsApi.search(trimmed)
    if (res.code === 0 && res.data) {
      // 将搜索结果设置到 explorer store 中
      explorerStore.setSearchResults(res.data, trimmed)
    }
  } catch (e) {
    console.warn('搜索失败:', e)
  }
}

// 弹窗状态
const serverFormVisible = ref(false)

// 拖拽调整宽度
let isResizing = false
let startX = 0
let startWidth = 0

function startResize(e) {
  isResizing = true
  startX = e.clientX
  startWidth = explorerStore.preferences.panelWidth
  document.addEventListener('mousemove', doResize)
  document.addEventListener('mouseup', stopResize)
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

function doResize(e) {
  if (!isResizing) return
  const diff = e.clientX - startX
  explorerStore.setPanelWidth(startWidth + diff)
}

function stopResize() {
  isResizing = false
  document.removeEventListener('mousemove', doResize)
  document.removeEventListener('mouseup', stopResize)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

// 键盘快捷键
function handleKeydown(e) {
  // 检查目标是否是输入框
  const isInputFocused = e.target && e.target.matches && e.target.matches('input, textarea')

  // Ctrl+K 或 / 聚焦搜索框
  if ((e.ctrlKey && e.key === 'k') || (e.key === '/' && !isInputFocused)) {
    e.preventDefault()
    document.querySelector('.search-input input')?.focus()
  }

  // Backspace 返回上一级
  if (e.key === 'Backspace' && !isInputFocused) {
    e.preventDefault()
    explorerStore.navigateBack()
  }

  // F5 刷新
  if (e.key === 'F5') {
    e.preventDefault()
    handleRefresh()
  }

  // Escape 清除选择
  if (e.key === 'Escape') {
    explorerStore.clearSelection()
  }

  // Ctrl+A 全选
  if (e.ctrlKey && e.key === 'a' && !isInputFocused) {
    e.preventDefault()
    explorerStore.selectAll()
  }

  // 方向键导航
  if (!isInputFocused) {
    if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
      e.preventDefault()
      explorerStore.selectNext()
    }

    if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
      e.preventDefault()
      explorerStore.selectPrevious()
    }

    // Enter 打开选中项
    if (e.key === 'Enter') {
      e.preventDefault()
      explorerStore.openSelected()
    }

    // Delete 删除选中项
    if (e.key === 'Delete') {
      // TODO: 实现删除功能
      console.log('删除选中项:', explorerStore.selectedItems)
    }
  }
}

function handleSearch() {
  executeSearch(searchKeyword.value)
}

function showAddServerDialog() {
  serverFormVisible.value = true
}

async function handleRefresh() {
  await explorerStore.loadNavigationTree()
  if (explorerStore.currentNode?.type === 'server') {
    await explorerStore.loadServerContent(explorerStore.currentNode.nodeId)
  }
}

onMounted(async () => {
  // 加载搜索历史
  loadSearchHistory()

  // 加载用户偏好
  explorerStore.loadPreferences()
  explorerStore.loadState()

  // 加载导航树（内部会同时更新快捷访问数据）
  await explorerStore.loadNavigationTree()

  // 注册键盘快捷键
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style lang="scss" scoped>
.asset-explorer {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

// 顶部工具栏
.top-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  height: 56px;
  flex-shrink: 0;

  .toolbar-left {
    display: flex;
    align-items: center;

    .app-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;
      color: #303133;

      .el-icon {
        font-size: 20px;
        color: #409EFF;
      }
    }
  }

  .toolbar-center {
    flex: 1;
    max-width: 400px;
    margin: 0 24px;

    .search-input {
      width: 100%;
    }
  }

  .toolbar-right {
    display: flex;
    align-items: center;
    gap: 12px;

    .filter-select {
      width: 120px;
    }

    .view-toggle {
      margin-left: 8px;
    }
  }
}

// 主内容区
.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

// 左侧导航面板
.navigation-panel {
  flex-shrink: 0;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

// 可拖拽分隔线
.resizer {
  width: 4px;
  cursor: col-resize;
  background: transparent;
  transition: background 0.2s;

  &:hover {
    background: #409EFF;
  }
}

// 右侧内容面板
.content-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f5f7fa;
}

// 搜索建议样式
.search-suggestion-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  gap: 10px;

  .suggestion-icon {
    font-size: 16px;
    color: #909399;

    &.history {
      color: #909399;
    }

    &.server {
      color: #409EFF;
    }

    &.container {
      color: #67C23A;
    }
  }

  .suggestion-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
    overflow: hidden;

    .suggestion-name {
      font-size: 14px;
      color: #303133;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .suggestion-desc {
      font-size: 12px;
      color: #909399;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  .remove-history-btn {
    padding: 4px;
    color: #909399;

    &:hover {
      color: #F56C6C;
    }
  }
}
</style>
