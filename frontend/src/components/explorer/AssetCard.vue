<template>
  <div
    class="asset-card"
    :class="[
      type,
      { selected, 'list-mode': isListMode, 'drag-over': isDragOver, 'dragging': isDragging }
    ]"
    :draggable="draggable"
    @click="$emit('click', $event)"
    @dblclick="$emit('dblclick', $event)"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
    @dragover.prevent="handleDragOver"
    @dragleave="handleDragLeave"
    @drop="handleDrop"
  >
    <!-- 网格模式 -->
    <template v-if="!isListMode">
      <div class="card-icon">
        <el-icon :size="32">
          <component :is="cardIcon" />
        </el-icon>
      </div>
      <div class="card-content">
        <div class="card-name">{{ item.name }}</div>
        <div class="card-info">
          <span v-if="statusText" class="status-dot" :class="statusClass" />
          <span class="info-text">{{ cardSubtitle }}</span>
        </div>
        <!-- 容器专属：显示使用人和用途 -->
        <template v-if="type === 'container'">
          <div class="card-extra" v-if="item.assigned_user_name">
            <el-icon :size="12"><User /></el-icon>
            <span>{{ item.assigned_user_name }}</span>
          </div>
          <div class="card-extra purpose" v-if="item.purpose">
            <el-icon :size="12"><Document /></el-icon>
            <span>{{ item.purpose }}</span>
          </div>
        </template>
      </div>
      <el-tag
        v-if="item.status && type === 'server'"
        :type="statusTagType"
        size="small"
        class="card-status"
      >
        {{ statusText }}
      </el-tag>
    </template>

    <!-- 列表模式 -->
    <template v-else>
      <div class="list-icon">
        <el-icon :size="20">
          <component :is="cardIcon" />
        </el-icon>
      </div>
      <div class="list-name">{{ item.name }}</div>
      <div class="list-info">{{ cardSubtitle }}</div>
      <!-- 容器专属：列表模式显示使用人 -->
      <div class="list-user" v-if="type === 'container' && item.assigned_user_name">
        <el-icon :size="12"><User /></el-icon>
        {{ item.assigned_user_name }}
      </div>
      <!-- 容器专属：列表模式显示用途 -->
      <div class="list-purpose" v-if="type === 'container' && item.purpose">
        {{ item.purpose }}
      </div>
      <el-tag
        v-if="item.status"
        :type="statusTagType"
        size="small"
        class="list-status"
      >
        {{ statusText }}
      </el-tag>
      <div class="list-count" v-if="childCount > 0">
        {{ childCount }}
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import {
  FolderOpened, Location, Monitor, Box, Setting, Cpu, User, Document
} from '@element-plus/icons-vue'
import { useExplorerStore } from '@/stores/explorer'

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  type: {
    type: String,
    required: true
  },
  selected: {
    type: Boolean,
    default: false
  },
  draggable: {
    type: Boolean,
    default: false
  },
  index: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['click', 'dblclick', 'dragstart', 'dragend', 'drop'])

const explorerStore = useExplorerStore()

// 拖拽状态
const isDragging = ref(false)
const isDragOver = ref(false)

// 是否列表模式
const isListMode = computed(() => explorerStore.viewMode === 'list')

// 卡片图标
const cardIcon = computed(() => {
  const icons = {
    environment: FolderOpened,
    datacenter: Location,
    server: Monitor,
    container: Box,
    service: Setting,
    gpu: Cpu
  }
  return icons[props.type] || Folder
})

// 状态文本
const statusText = computed(() => {
  if (!props.item.status) return ''
  const map = {
    online: '在线',
    offline: '离线',
    maintenance: '维护',
    running: '运行中',
    stopped: '已停止',
    idle: '空闲',
    busy: '繁忙'
  }
  return map[props.item.status] || props.item.status
})

// 状态标签类型
const statusTagType = computed(() => {
  const map = {
    online: 'success',
    offline: 'danger',
    maintenance: 'warning',
    running: 'success',
    stopped: 'danger',
    idle: 'success',
    busy: 'warning'
  }
  return map[props.item.status] || 'info'
})

// 状态点样式类
const statusClass = computed(() => {
  const map = {
    online: 'online',
    offline: 'offline',
    maintenance: 'warning',
    running: 'online',
    stopped: 'offline',
    idle: 'online',
    busy: 'warning'
  }
  return map[props.item.status] || ''
})

// 卡片副标题
const cardSubtitle = computed(() => {
  switch (props.type) {
    case 'environment':
      return `${props.item.count || 0} 个服务器`
    case 'datacenter':
      return props.item.count ? `${props.item.count} 个服务器` : ''
    case 'server':
      return props.item.data?.ip || props.item.ip || ''
    case 'container':
      return props.item.container_name || props.item.image || ''
    case 'gpu':
      return props.item.model || props.item.gpu_model || ''
    case 'service':
      return props.item.container_name || props.item.port || ''
    default:
      return ''
  }
})

// 子节点数量
const childCount = computed(() => {
  return props.item.children?.length || props.item.count || 0
})

// ========== 拖拽处理 ==========

function handleDragStart(e) {
  if (!props.draggable) return
  isDragging.value = true
  e.dataTransfer.effectAllowed = 'move'
  e.dataTransfer.setData('application/json', JSON.stringify({
    id: props.item.id,
    type: props.type,
    index: props.index
  }))
  emit('dragstart', { item: props.item, type: props.type, index: props.index })
}

function handleDragEnd() {
  isDragging.value = false
  isDragOver.value = false
  emit('dragend')
}

function handleDragOver(e) {
  if (!props.draggable) return
  isDragOver.value = true
}

function handleDragLeave() {
  isDragOver.value = false
}

function handleDrop(e) {
  if (!props.draggable) return
  isDragOver.value = false
  try {
    const data = JSON.parse(e.dataTransfer.getData('application/json'))
    if (data.type === props.type && data.id !== props.item.id) {
      emit('drop', {
        from: data,
        to: { id: props.item.id, type: props.type, index: props.index }
      })
    }
  } catch (err) {
    console.error('拖拽数据解析失败:', err)
  }
}
</script>

<style lang="scss" scoped>
.asset-card {
  display: flex;
  flex-direction: column;
  padding: 16px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;

  &:hover {
    border-color: #409EFF;
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
    transform: translateY(-2px);
  }

  &:active {
    transform: translateY(0);
    box-shadow: 0 2px 6px rgba(64, 158, 255, 0.1);
  }

  &.selected {
    border-color: #409EFF;
    background: #ecf5ff;
    box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
  }

  // 拖拽状态
  &.dragging {
    opacity: 0.5;
    border-style: dashed;
  }

  &.drag-over {
    border-color: #67C23A;
    border-style: dashed;
    background: #f0f9eb;
  }

  // 不同类型的图标颜色
  .card-icon {
    margin-bottom: 12px;

    .el-icon {
      color: #909399;
    }
  }

  &.environment .card-icon .el-icon {
    color: #409EFF;
  }

  &.datacenter .card-icon .el-icon {
    color: #67C23A;
  }

  &.server .card-icon .el-icon {
    color: #909399;
  }

  &.container .card-icon .el-icon {
    color: #67C23A;
  }

  &.gpu .card-icon .el-icon {
    color: #F56C6C;
  }

  &.service .card-icon .el-icon {
    color: #E6A23C;
  }

  .card-content {
    flex: 1;

    .card-name {
      font-size: 14px;
      font-weight: 500;
      color: #303133;
      margin-bottom: 4px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .card-info {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: #909399;

      .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #c0c4cc;

        &.online {
          background: #67C23A;
        }

        &.offline {
          background: #F56C6C;
        }

        &.warning {
          background: #E6A23C;
        }
      }

      .info-text {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    .card-extra {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 12px;
      color: #606266;
      margin-top: 4px;

      .el-icon {
        color: #909399;
      }

      span {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      &.purpose {
        color: #909399;
      }
    }
  }

  .card-status {
    position: absolute;
    top: 8px;
    right: 8px;
  }

  // 列表模式样式
  &.list-mode {
    flex-direction: row;
    align-items: center;
    padding: 12px 16px;

    .list-icon {
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 12px;
      background: #f5f7fa;
      border-radius: 6px;

      .el-icon {
        color: inherit;
      }
    }

    &.environment .list-icon {
      color: #409EFF;
      background: #ecf5ff;
    }

    &.datacenter .list-icon {
      color: #67C23A;
      background: #f0f9eb;
    }

    &.server .list-icon {
      color: #909399;
      background: #f5f7fa;
    }

    &.container .list-icon {
      color: #67C23A;
      background: #f0f9eb;
    }

    &.gpu .list-icon {
      color: #F56C6C;
      background: #fef0f0;
    }

    &.service .list-icon {
      color: #E6A23C;
      background: #fdf6ec;
    }

    .list-name {
      flex: 1;
      font-size: 14px;
      font-weight: 500;
      color: #303133;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .list-info {
      width: 120px;
      font-size: 13px;
      color: #909399;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      margin-right: 12px;
    }

    .list-user {
      display: flex;
      align-items: center;
      gap: 4px;
      width: 80px;
      font-size: 12px;
      color: #606266;
      margin-right: 12px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;

      .el-icon {
        color: #909399;
        flex-shrink: 0;
      }
    }

    .list-purpose {
      width: 150px;
      font-size: 12px;
      color: #909399;
      margin-right: 12px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .list-status {
      margin-right: 12px;
    }

    .list-count {
      font-size: 12px;
      color: #909399;
      background: #f0f2f5;
      padding: 2px 8px;
      border-radius: 10px;
    }
  }
}
</style>
