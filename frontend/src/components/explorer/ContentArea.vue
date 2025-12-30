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
        <div class="content-section" v-if="sortedContainers.length > 0">
          <div class="section-header">
            <el-icon><Box /></el-icon>
            <span>容器 ({{ sortedContainers.length }})</span>
            <span class="drag-hint" v-if="authStore.isAdmin">拖拽可排序</span>
          </div>
          <div :class="['items-grid', explorerStore.viewMode]">
            <AssetCard
              v-for="(container, idx) in sortedContainers"
              :key="container.id"
              :item="container"
              type="container"
              :index="idx"
              :draggable="authStore.isAdmin"
              :selected="isSelected(container.id, 'container')"
              @click="handleItemClick(container, 'container', $event)"
              @dblclick="handleItemDblClick(container, 'container')"
              @contextmenu.prevent.stop="handleContextMenu($event, container, 'container')"
              @drop="handleDrop($event, 'container')"
            />
          </div>
        </div>

        <!-- GPU 分组 -->
        <div class="content-section" v-if="sortedGpus.length > 0">
          <div class="section-header">
            <el-icon><Cpu /></el-icon>
            <span>GPU ({{ sortedGpus.length }})</span>
            <span class="drag-hint" v-if="authStore.isAdmin">拖拽可排序</span>
          </div>
          <div :class="['items-grid', explorerStore.viewMode]">
            <AssetCard
              v-for="(gpu, idx) in sortedGpus"
              :key="gpu.id"
              :item="gpu"
              type="gpu"
              :index="idx"
              :draggable="authStore.isAdmin"
              :selected="isSelected(gpu.id, 'gpu')"
              @click="handleItemClick(gpu, 'gpu', $event)"
              @dblclick="handleItemDblClick(gpu, 'gpu')"
              @contextmenu.prevent.stop="handleContextMenu($event, gpu, 'gpu')"
              @drop="handleDrop($event, 'gpu')"
            />
          </div>
        </div>

        <!-- 服务分组 -->
        <div class="content-section" v-if="sortedServices.length > 0">
          <div class="section-header">
            <el-icon><Setting /></el-icon>
            <span>服务 ({{ sortedServices.length }})</span>
            <span class="drag-hint" v-if="authStore.isAdmin">拖拽可排序</span>
          </div>
          <div :class="['items-grid', explorerStore.viewMode]">
            <AssetCard
              v-for="(service, idx) in sortedServices"
              :key="service.id"
              :item="service"
              type="service"
              :index="idx"
              :draggable="authStore.isAdmin"
              :selected="isSelected(service.id, 'service')"
              @click="handleItemClick(service, 'service', $event)"
              @dblclick="handleItemDblClick(service, 'service')"
              @contextmenu.prevent.stop="handleContextMenu($event, service, 'service')"
              @drop="handleDrop($event, 'service')"
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

    <!-- 容器编辑弹窗 -->
    <ContainerFormDialog
      v-model="containerDialogVisible"
      :container="editingContainer"
      :server="explorerStore.currentNode?.data"
      @success="handleDialogSuccess"
    />

    <!-- 服务编辑弹窗 -->
    <ServiceFormDialog
      v-model="serviceDialogVisible"
      :service="editingService"
      :container="parentContainer"
      @success="handleDialogSuccess"
    />

    <!-- GPU编辑弹窗 -->
    <GPUFormDialog
      v-model="gpuDialogVisible"
      :gpu="editingGpu"
      :server="explorerStore.currentNode?.data"
      @success="handleDialogSuccess"
    />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import {
  FolderOpened, Monitor, Box, Cpu, Setting,
  Sort, Refresh, Location
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useExplorerStore } from '@/stores/explorer'
import { useAuthStore } from '@/stores/auth'
import { assetsApi } from '@/api/assets'
import AssetCard from './AssetCard.vue'
import ContextMenu from './ContextMenu.vue'
import ContainerFormDialog from '@/components/ContainerFormDialog.vue'
import ServiceFormDialog from '@/components/ServiceFormDialog.vue'
import GPUFormDialog from '@/components/GPUFormDialog.vue'

const explorerStore = useExplorerStore()
const authStore = useAuthStore()

// ========== 右键菜单状态 ==========
const contextMenuVisible = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const contextMenuType = ref('')
const contextMenuData = ref({})

// ========== 弹窗状态 ==========
const containerDialogVisible = ref(false)
const serviceDialogVisible = ref(false)
const gpuDialogVisible = ref(false)
const editingContainer = ref(null)
const editingService = ref(null)
const editingGpu = ref(null)
const parentContainer = ref(null)  // 添加服务时的父容器

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

// 按 sort_order 排序的容器列表
const sortedContainers = computed(() => {
  return [...explorerStore.currentContent.containers].sort((a, b) => {
    return (a.sort_order || 0) - (b.sort_order || 0)
  })
})

// 按 sort_order 排序的 GPU 列表
const sortedGpus = computed(() => {
  return [...explorerStore.currentContent.gpus].sort((a, b) => {
    return (a.sort_order || 0) - (b.sort_order || 0)
  })
})

// 按 sort_order 排序的服务列表
const sortedServices = computed(() => {
  return [...explorerStore.currentContent.services].sort((a, b) => {
    return (a.sort_order || 0) - (b.sort_order || 0)
  })
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
    case 'edit':
      openEditDialog(type, data)
      break
    case 'delete':
      handleDelete(type, data)
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
      editingContainer.value = null
      containerDialogVisible.value = true
      break
    case 'addGPU':
      editingGpu.value = null
      gpuDialogVisible.value = true
      break
    case 'addService':
      // 找到父容器
      parentContainer.value = data
      editingService.value = null
      serviceDialogVisible.value = true
      break
    case 'addServer':
      // 这个由 AssetExplorer 处理
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

// ========== 编辑弹窗操作 ==========

// 打开编辑弹窗
function openEditDialog(type, data) {
  if (type === 'container') {
    editingContainer.value = data
    containerDialogVisible.value = true
  } else if (type === 'service') {
    // 找到服务所属的容器
    const containerName = data.container_name
    const container = explorerStore.currentContent.containers.find(c => c.name === containerName)
    parentContainer.value = container || null
    editingService.value = data
    serviceDialogVisible.value = true
  } else if (type === 'gpu') {
    editingGpu.value = data
    gpuDialogVisible.value = true
  }
}

// 删除操作
async function handleDelete(type, data) {
  const typeNames = {
    container: '容器',
    service: '服务',
    gpu: 'GPU'
  }
  const typeName = typeNames[type] || type

  try {
    await ElMessageBox.confirm(
      `确定要删除${typeName} "${data.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    let res
    if (type === 'container') {
      res = await assetsApi.deleteContainer(data.id)
    } else if (type === 'service') {
      res = await assetsApi.deleteService(data.id)
    } else if (type === 'gpu') {
      res = await assetsApi.deleteGpu(data.id)
    }

    if (res && res.code === 0) {
      ElMessage.success(`${typeName}删除成功`)
      // 刷新内容
      if (explorerStore.currentNode?.type === 'server') {
        await explorerStore.loadServerContent(explorerStore.currentNode.nodeId)
      }
    } else {
      ElMessage.error(res?.message || '删除失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      console.error('删除失败:', e)
      ElMessage.error('删除失败')
    }
  }
}

// 弹窗保存成功后刷新
async function handleDialogSuccess() {
  if (explorerStore.currentNode?.type === 'server') {
    await explorerStore.loadServerContent(explorerStore.currentNode.nodeId)
  }
}

// ========== 拖拽排序处理 ==========

async function handleDrop({ from, to }, type) {
  if (from.index === to.index) return

  // 获取对应类型的列表
  let items = []
  let apiMethod = null

  if (type === 'container') {
    items = [...sortedContainers.value]
    apiMethod = assetsApi.updateContainerSortOrder
  } else if (type === 'gpu') {
    items = [...sortedGpus.value]
    apiMethod = assetsApi.updateGpuSortOrder
  } else if (type === 'service') {
    items = [...sortedServices.value]
    apiMethod = assetsApi.updateServiceSortOrder
  }

  if (!apiMethod || items.length === 0) return

  // 从旧位置移除并插入新位置
  const [movedItem] = items.splice(from.index, 1)
  items.splice(to.index, 0, movedItem)

  // 更新排序顺序
  const sortItems = items.map((item, idx) => ({
    id: item.id,
    sort_order: idx
  }))

  try {
    const res = await apiMethod(sortItems)
    if (res && res.code === 0) {
      ElMessage.success('排序已保存')
      // 刷新内容
      if (explorerStore.currentNode?.type === 'server') {
        await explorerStore.loadServerContent(explorerStore.currentNode.nodeId)
      }
    } else {
      ElMessage.error(res?.message || '排序保存失败')
    }
  } catch (e) {
    console.error('排序保存失败:', e)
    ElMessage.error('排序保存失败')
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

    .drag-hint {
      margin-left: auto;
      font-size: 12px;
      font-weight: normal;
      color: #909399;
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
