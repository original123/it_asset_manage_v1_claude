<template>
  <div class="detail-bar" v-if="explorerStore.hasSelection">
    <div class="selection-info">
      <span class="selection-count">
        已选择 {{ explorerStore.selectionCount }} 项
      </span>
      <el-button link size="small" @click="explorerStore.clearSelection">
        取消选择
      </el-button>
    </div>

    <div class="detail-content" v-if="singleSelection">
      <!-- 单选显示详情 -->
      <div class="detail-item">
        <span class="detail-label">名称</span>
        <span class="detail-value">{{ singleSelection.name }}</span>
      </div>
      <div class="detail-item" v-if="singleSelection.ip">
        <span class="detail-label">IP</span>
        <span class="detail-value">{{ singleSelection.ip }}</span>
      </div>
      <div class="detail-item" v-if="singleSelection.status">
        <span class="detail-label">状态</span>
        <el-tag :type="getStatusType(singleSelection.status)" size="small">
          {{ getStatusText(singleSelection.status) }}
        </el-tag>
      </div>
    </div>

    <div class="detail-actions">
      <!-- 单选操作 -->
      <template v-if="singleSelection">
        <el-button size="small" @click="handleView">
          <el-icon><View /></el-icon>
          查看
        </el-button>
        <el-button size="small" @click="handleEdit" v-if="authStore.isAdmin">
          <el-icon><Edit /></el-icon>
          编辑
        </el-button>
      </template>

      <!-- 批量操作 -->
      <template v-if="explorerStore.selectionCount > 1">
        <el-button size="small" @click="handleBatchEdit" v-if="authStore.isAdmin">
          <el-icon><Edit /></el-icon>
          批量编辑
        </el-button>
      </template>

      <el-button
        type="danger"
        size="small"
        plain
        @click="handleDelete"
        v-if="authStore.isAdmin"
      >
        <el-icon><Delete /></el-icon>
        删除
      </el-button>
    </div>

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
import { View, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useExplorerStore } from '@/stores/explorer'
import { useAuthStore } from '@/stores/auth'
import { assetsApi } from '@/api/assets'
import ContainerFormDialog from '@/components/ContainerFormDialog.vue'
import ServiceFormDialog from '@/components/ServiceFormDialog.vue'
import GPUFormDialog from '@/components/GPUFormDialog.vue'

const explorerStore = useExplorerStore()
const authStore = useAuthStore()

// ========== 弹窗状态 ==========
const containerDialogVisible = ref(false)
const serviceDialogVisible = ref(false)
const gpuDialogVisible = ref(false)
const editingContainer = ref(null)
const editingService = ref(null)
const editingGpu = ref(null)
const parentContainer = ref(null)

// 单选项
const singleSelection = computed(() => {
  if (explorerStore.selectedItems.length === 1) {
    return explorerStore.selectedItems[0]
  }
  return null
})

// 获取状态类型
function getStatusType(status) {
  const map = {
    online: 'success',
    offline: 'danger',
    maintenance: 'warning',
    running: 'success',
    stopped: 'danger'
  }
  return map[status] || 'info'
}

// 获取状态文本
function getStatusText(status) {
  const map = {
    online: '在线',
    offline: '离线',
    maintenance: '维护中',
    running: '运行中',
    stopped: '已停止'
  }
  return map[status] || status
}

// 查看详情 (与编辑相同，打开弹窗)
function handleView() {
  if (singleSelection.value) {
    openEditDialog(singleSelection.value.type, singleSelection.value)
  }
}

// 编辑
function handleEdit() {
  if (singleSelection.value) {
    openEditDialog(singleSelection.value.type, singleSelection.value)
  }
}

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

// 批量编辑
function handleBatchEdit() {
  // TODO: 实现批量编辑弹窗
  ElMessage.info('批量编辑功能开发中...')
}

// 弹窗保存成功后刷新
async function handleDialogSuccess() {
  if (explorerStore.currentNode?.type === 'server') {
    await explorerStore.loadServerContent(explorerStore.currentNode.nodeId)
  }
  explorerStore.clearSelection()
}

// 删除
async function handleDelete() {
  const count = explorerStore.selectionCount
  const message = count === 1
    ? `确定要删除 "${singleSelection.value?.name}" 吗？此操作不可恢复。`
    : `确定要删除选中的 ${count} 项吗？此操作不可恢复。`

  try {
    await ElMessageBox.confirm(message, '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 执行删除
    const selectedItems = [...explorerStore.selectedItems]
    let successCount = 0
    let failCount = 0

    for (const item of selectedItems) {
      try {
        let res
        if (item.type === 'container') {
          res = await assetsApi.deleteContainer(item.id)
        } else if (item.type === 'service') {
          res = await assetsApi.deleteService(item.id)
        } else if (item.type === 'gpu') {
          res = await assetsApi.deleteGpu(item.id)
        }

        if (res && res.code === 0) {
          successCount++
        } else {
          failCount++
        }
      } catch (e) {
        failCount++
      }
    }

    if (successCount > 0) {
      ElMessage.success(`成功删除 ${successCount} 项`)
      // 刷新内容
      if (explorerStore.currentNode?.type === 'server') {
        await explorerStore.loadServerContent(explorerStore.currentNode.nodeId)
      }
    }
    if (failCount > 0) {
      ElMessage.error(`${failCount} 项删除失败`)
    }

    explorerStore.clearSelection()
  } catch {
    // 取消删除
  }
}
</script>

<style lang="scss" scoped>
.detail-bar {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background: #fff;
  border-top: 1px solid #ebeef5;
  gap: 24px;

  .selection-info {
    display: flex;
    align-items: center;
    gap: 12px;

    .selection-count {
      font-size: 13px;
      color: #606266;
      font-weight: 500;
    }
  }

  .detail-content {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 24px;
    overflow: hidden;

    .detail-item {
      display: flex;
      align-items: center;
      gap: 8px;

      .detail-label {
        font-size: 12px;
        color: #909399;
      }

      .detail-value {
        font-size: 13px;
        color: #303133;
        max-width: 200px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }

  .detail-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}
</style>
