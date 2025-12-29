<template>
  <div
    class="asset-card"
    :class="[
      type,
      { selected, 'list-mode': isListMode }
    ]"
    @click="$emit('click', $event)"
    @dblclick="$emit('dblclick', $event)"
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
import { computed, inject } from 'vue'
import {
  FolderOpened, Location, Monitor, Box, Setting, Cpu
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
  }
})

defineEmits(['click', 'dblclick'])

const explorerStore = useExplorerStore()

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
  transition: all 0.2s;

  &:hover {
    border-color: #c0c4cc;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }

  &.selected {
    border-color: #409EFF;
    background: #ecf5ff;
    box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
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
      width: 150px;
      font-size: 13px;
      color: #909399;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      margin-right: 12px;
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
