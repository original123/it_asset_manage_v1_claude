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
        <span class="detail-value">{{ singleSelection.data?.name || singleSelection.name }}</span>
      </div>
      <div class="detail-item" v-if="singleSelection.data?.ip">
        <span class="detail-label">IP</span>
        <span class="detail-value">{{ singleSelection.data.ip }}</span>
      </div>
      <div class="detail-item" v-if="singleSelection.data?.status">
        <span class="detail-label">状态</span>
        <el-tag :type="getStatusType(singleSelection.data.status)" size="small">
          {{ getStatusText(singleSelection.data.status) }}
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
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { View, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useExplorerStore } from '@/stores/explorer'
import { useAuthStore } from '@/stores/auth'

const explorerStore = useExplorerStore()
const authStore = useAuthStore()

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

// 查看详情
function handleView() {
  // TODO: 打开详情弹窗
  console.log('查看详情:', singleSelection.value)
}

// 编辑
function handleEdit() {
  // TODO: 打开编辑弹窗
  console.log('编辑:', singleSelection.value)
}

// 批量编辑
function handleBatchEdit() {
  // TODO: 打开批量编辑弹窗
  console.log('批量编辑:', explorerStore.selectedItems)
}

// 删除
async function handleDelete() {
  const count = explorerStore.selectionCount
  const message = count === 1
    ? `确定要删除 "${singleSelection.value?.data?.name || singleSelection.value?.name}" 吗?`
    : `确定要删除选中的 ${count} 项吗?`

  try {
    await ElMessageBox.confirm(message, '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // TODO: 调用删除API
    ElMessage.success('删除成功')
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
