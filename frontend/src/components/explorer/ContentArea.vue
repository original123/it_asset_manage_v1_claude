<template>
  <div class="content-area" v-loading="explorerStore.loading" @contextmenu.prevent="handleBackgroundContextMenu">
    <!-- 内容头部 -->
    <div class="content-header" v-if="explorerStore.currentNode">
      <div class="header-info">
        <h3 class="content-title">
          <el-icon class="title-icon">
            <component :is="getTitleIcon(explorerStore.currentNode.type)" />
          </el-icon>
          {{ explorerStore.currentNode.name }}
        </h3>
        <span class="content-subtitle" v-if="explorerStore.currentNode.type === 'server'">
          {{ getServerSubtitle(explorerStore.currentNode.data) }}
        </span>
      </div>

      <div class="header-actions">
        <!-- 排序 -->
        <el-dropdown @command="handleSort">
          <el-button text>
            <el-icon><Sort /></el-icon>
            排序
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="name">按名称</el-dropdown-item>
              <el-dropdown-item command="type">按类型</el-dropdown-item>
              <el-dropdown-item command="status">按状态</el-dropdown-item>
              <el-dropdown-item command="created">按创建时间</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- 刷新 -->
        <el-button text @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 内容主体 -->
    <div class="content-body" @click.self="handleBackgroundClick">
      <!-- 服务器内容：容器、GPU、服务 -->
      <template v-if="explorerStore.currentNode?.type === 'server'">
        <!-- 容器分组 -->
        <div class="content-section" v-if="explorerStore.currentContent.containers.length > 0">
          <div class="section-header">
            <el-icon><Box /></el-icon>
            <span>容器 ({{ explorerStore.currentContent.containers.length }})</span>
          </div>
          <div :class="['items-grid', explorerStore.viewMode]">
            <AssetCard
              v-for="container in explorerStore.currentContent.containers"
              :key="container.id"
              :item="container"
              type="container"
              :selected="isSelected(container.id, 'container')"
              @click="handleItemClick(container, 'container', $event)"
              @dblclick="handleItemDblClick(container, 'container')"
              @contextmenu.prevent.stop="handleContextMenu($event, container, 'container')"
            />
          </div>
        </div>

        <!-- GPU 分组 -->
        <div class="content-section" v-if="explorerStore.currentContent.gpus.length > 0">
          <div class="section-header">
            <el-icon><Cpu /></el-icon>
            <span>GPU ({{ explorerStore.currentContent.gpus.length }})</span>
          </div>
          <div :class="['items-grid', explorerStore.viewMode]">
            <AssetCard
              v-for="gpu in explorerStore.currentContent.gpus"
              :key="gpu.id"
              :item="gpu"
              type="gpu"
              :selected="isSelected(gpu.id, 'gpu')"
              @click="handleItemClick(gpu, 'gpu', $event)"
              @dblclick="handleItemDblClick(gpu, 'gpu')"
              @contextmenu.prevent.stop="handleContextMenu($event, gpu, 'gpu')"
            />
          </div>
        </div>

        <!-- 服务分组 -->
        <div class="content-section" v-if="explorerStore.currentContent.services.length > 0">
          <div class="section-header">
            <el-icon><Setting /></el-icon>
            <span>服务 ({{ explorerStore.currentContent.services.length }})</span>
          </div>
          <div :class="['items-grid', explorerStore.viewMode]">
            <AssetCard
              v-for="service in explorerStore.currentContent.services"
              :key="service.id"
              :item="service"
              type="service"
              :selected="isSelected(service.id, 'service')"
              @click="handleItemClick(service, 'service', $event)"
              @dblclick="handleItemDblClick(service, 'service')"
              @contextmenu.prevent.stop="handleContextMenu($event, service, 'service')"
            />
          </div>
        </div>

        <!-- 空状态 -->
        <div
          v-if="explorerStore.currentContent.containers.length === 0 &&
                explorerStore.currentContent.gpus.length === 0 &&
                explorerStore.currentContent.services.length === 0"
          class="empty-content"
        >
          <el-empty description="该服务器暂无资产数据">
            <el-button type="primary" size="small">添加容器</el-button>
          </el-empty>
        </div>
      </template>

      <!-- 环境/机房内容：显示子节点卡片 -->
      <template v-else-if="explorerStore.currentNode">
        <div class="folder-content">
          <div :class="['items-grid', explorerStore.viewMode]">
            <AssetCard
              v-for="child in getCurrentChildren"
              :key="child.id"
              :item="child"
              :type="child.type"
              :selected="isSelected(child.id, child.type)"
              @click="handleItemClick(child, child.type, $event)"
              @dblclick="handleItemDblClick(child, child.type)"
              @contextmenu.prevent.stop="handleContextMenu($event, child, child.type)"
            />
          </div>
        </div>
      </template>

      <!-- 根目录：欢迎界面 -->
      <template v-else>
        <div class="welcome-content">
          <div class="welcome-icon">
            <el-icon :size="64"><FolderOpened /></el-icon>
          </div>
          <h2>IT 资产管理器</h2>
          <p>请从左侧导航树选择环境、机房或服务器开始浏览</p>
          <div class="quick-stats">
            <div class="stat-item">
              <span class="stat-value">{{ totalServers }}</span>
              <span class="stat-label">服务器</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ onlineCount }}</span>
              <span class="stat-label">在线</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ offlineCount }}</span>
              <span class="stat-label">离线</span>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- 右键菜单 -->
    <ContextMenu
      v-model:visible="contextMenuVisible"
      :x="contextMenuX"
      :y="contextMenuY"
      :target-type="contextMenuType"
      :target-data="contextMenuData"
      @action="handleContextMenuAction"
    />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import {
  FolderOpened, Monitor, Box, Cpu, Setting,
  Sort, Refresh, Location
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useExplorerStore } from '@/stores/explorer'
import AssetCard from './AssetCard.vue'
import ContextMenu from './ContextMenu.vue'

const explorerStore = useExplorerStore()

// ========== 右键菜单状态 ==========
const contextMenuVisible = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const contextMenuType = ref('')
const contextMenuData = ref({})

// 获取标题图标
function getTitleIcon(type) {
  const icons = {
    environment: FolderOpened,
    datacenter: Location,
    server: Monitor,
    container: Box,
    service: Setting,
    gpu: Cpu
  }
  return icons[type] || Folder
}

// 获取服务器副标题
function getServerSubtitle(server) {
  if (!server) return ''
  const parts = []
  if (server.ip) parts.push(server.ip)
  if (server.os_type) parts.push(server.os_type)
  return parts.join(' · ')
}

// 当前节点的子节点
const getCurrentChildren = computed(() => {
  if (!explorerStore.currentNode) return []
  return explorerStore.currentNode.children || []
})

// 统计数据
const totalServers = computed(() => {
  let count = 0
  function countServers(nodes) {
    for (const node of nodes) {
      if (node.type === 'server') count++
      if (node.children) countServers(node.children)
    }
  }
  countServers(explorerStore.navigationTree)
  return count
})

const onlineCount = computed(() => {
  let count = 0
  function countOnline(nodes) {
    for (const node of nodes) {
      if (node.type === 'server' && node.status === 'online') count++
      if (node.children) countOnline(node.children)
    }
  }
  countOnline(explorerStore.navigationTree)
  return count
})

const offlineCount = computed(() => {
  let count = 0
  function countOffline(nodes) {
    for (const node of nodes) {
      if (node.type === 'server' && node.status === 'offline') count++
      if (node.children) countOffline(node.children)
    }
  }
  countOffline(explorerStore.navigationTree)
  return count
})

// 检查是否选中
function isSelected(id, type) {
  return explorerStore.selectedItems.some(
    item => item.id === id && item.type === type
  )
}

// 处理项目点击
function handleItemClick(item, type, event) {
  if (event.shiftKey) {
    // Shift+Click 范围选择
    explorerStore.selectRange({ id: item.id, type, ...item })
  } else if (event.ctrlKey || event.metaKey) {
    // Ctrl+Click 多选
    explorerStore.selectItem({ id: item.id, type, ...item }, true)
  } else {
    // 普通点击单选
    explorerStore.selectItem({ id: item.id, type, ...item }, false)
  }
}

// 处理项目双击
function handleItemDblClick(item, type) {
  if (type === 'environment' || type === 'datacenter') {
    explorerStore.navigateTo(item.id, type)
  } else if (type === 'server') {
    explorerStore.loadServerContent(item.nodeId || item.id)
  }
  // 容器、GPU、服务双击可以打开详情弹窗
}

// 点击背景清除选择
function handleBackgroundClick() {
  explorerStore.clearSelection()
}

// 排序处理
function handleSort(command) {
  explorerStore.sortBy = command
  // TODO: 实现排序逻辑
}

// 刷新处理
async function handleRefresh() {
  if (explorerStore.currentNode?.type === 'server') {
    await explorerStore.loadServerContent(explorerStore.currentNode.nodeId)
  } else {
    await explorerStore.loadNavigationTree()
  }
}

// ========== 右键菜单处理 ==========

// 显示右键菜单
function handleContextMenu(event, item, type) {
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  contextMenuType.value = type
  contextMenuData.value = item
  contextMenuVisible.value = true
}

// 空白区域右键菜单
function handleBackgroundContextMenu(event) {
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  contextMenuType.value = ''
  contextMenuData.value = {}
  contextMenuVisible.value = true
}

// 处理右键菜单操作
function handleContextMenuAction({ action, type, data }) {
  switch (action) {
    case 'view':
      console.log('查看详情:', type, data)
      // TODO: 打开详情弹窗
      break
    case 'edit':
      console.log('编辑:', type, data)
      // TODO: 打开编辑弹窗
      break
    case 'delete':
      console.log('删除:', type, data)
      // TODO: 调用删除API
      break
    case 'copyIP':
      if (data.data?.ip || data.ip) {
        navigator.clipboard.writeText(data.data?.ip || data.ip)
        ElMessage.success('IP 已复制到剪贴板')
      }
      break
    case 'copySSH':
      const ip = data.data?.ip || data.ip
      if (ip) {
        navigator.clipboard.writeText(`ssh root@${ip}`)
        ElMessage.success('SSH 命令已复制到剪贴板')
      }
      break
    case 'copyPorts':
      // 复制容器端口映射
      const ports = data.port_mappings || data.ports || ''
      if (ports) {
        navigator.clipboard.writeText(ports)
        ElMessage.success('端口映射已复制到剪贴板')
      }
      break
    case 'copyPort':
      // 复制服务端口
      const port = data.port || ''
      if (port) {
        navigator.clipboard.writeText(String(port))
        ElMessage.success('端口已复制到剪贴板')
      }
      break
    case 'copyInfo':
      // 复制GPU信息
      const gpuInfo = `${data.gpu_model || data.model || ''} (${data.gpu_uuid || data.uuid || ''})`
      navigator.clipboard.writeText(gpuInfo)
      ElMessage.success('GPU 信息已复制到剪贴板')
      break
    case 'addContainer':
    case 'addGPU':
    case 'addService':
    case 'addServer':
      console.log('添加:', action, type, data)
      // TODO: 打开添加弹窗
      break
    case 'open':
      if (type === 'environment' || type === 'datacenter') {
        explorerStore.navigateTo(data.id, type)
      }
      break
    case 'refresh':
      handleRefresh()
      break
    case 'selectAll':
      explorerStore.selectAll()
      break
    default:
      console.log('未处理的操作:', action, type, data)
  }
}
</script>

<style lang="scss" scoped>
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f5f7fa;
}

.content-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;

  .header-info {
    display: flex;
    align-items: baseline;
    gap: 12px;

    .content-title {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: #303133;

      .title-icon {
        font-size: 20px;
        color: #409EFF;
      }
    }

    .content-subtitle {
      font-size: 13px;
      color: #909399;
    }
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}

.content-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.content-section {
  margin-bottom: 24px;

  .section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    font-size: 14px;
    font-weight: 500;
    color: #606266;

    .el-icon {
      font-size: 16px;
    }
  }
}

.items-grid {
  display: grid;
  gap: 16px;

  &.grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }

  &.list {
    grid-template-columns: 1fr;
  }
}

.empty-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.welcome-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;

  .welcome-icon {
    margin-bottom: 24px;
    color: #409EFF;
  }

  h2 {
    margin: 0 0 8px;
    font-size: 24px;
    font-weight: 600;
    color: #303133;
  }

  p {
    margin: 0 0 32px;
    font-size: 14px;
    color: #909399;
  }

  .quick-stats {
    display: flex;
    gap: 48px;

    .stat-item {
      display: flex;
      flex-direction: column;
      align-items: center;

      .stat-value {
        font-size: 32px;
        font-weight: 600;
        color: #303133;
      }

      .stat-label {
        font-size: 13px;
        color: #909399;
        margin-top: 4px;
      }
    }
  }
}

.folder-content {
  min-height: 200px;
}
</style>
