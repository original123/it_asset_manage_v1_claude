<template>
  <div
    class="tree-node"
    :class="{
      expanded: isExpanded,
      selected: isSelected,
      'is-server': node.type === 'server'
    }"
    :style="{ paddingLeft: level * 16 + 'px' }"
  >
    <div class="node-content" @click="handleClick" @dblclick="handleDoubleClick">
      <!-- 展开/折叠图标 -->
      <span
        v-if="hasChildren"
        class="expand-icon"
        @click.stop="toggleExpand"
      >
        <el-icon :class="{ rotated: isExpanded }"><ArrowRight /></el-icon>
      </span>
      <span v-else class="expand-placeholder" />

      <!-- 节点图标 -->
      <span class="node-icon" :class="node.type">
        <el-icon>
          <component :is="nodeIcon" />
        </el-icon>
      </span>

      <!-- 节点名称 -->
      <span class="node-name">{{ node.name }}</span>

      <!-- 状态标签 (服务器) -->
      <el-tag
        v-if="node.type === 'server' && node.status"
        :type="statusType"
        size="small"
        effect="light"
        class="status-tag"
      >
        {{ statusText }}
      </el-tag>

      <!-- 子项数量 -->
      <span v-if="node.count" class="node-count">{{ node.count }}</span>
    </div>

    <!-- 子节点 -->
    <Transition name="expand">
      <div v-if="isExpanded && hasChildren" class="node-children">
        <TreeNode
          v-for="child in node.children"
          :key="child.id"
          :node="child"
          :level="level + 1"
        />
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  ArrowRight, FolderOpened, Location, Monitor,
  Box, Setting, Cpu
} from '@element-plus/icons-vue'
import { useExplorerStore } from '@/stores/explorer'

const props = defineProps({
  node: {
    type: Object,
    required: true
  },
  level: {
    type: Number,
    default: 0
  }
})

const explorerStore = useExplorerStore()

// 是否有子节点
const hasChildren = computed(() => {
  return props.node.children && props.node.children.length > 0
})

// 是否展开
const isExpanded = computed(() => {
  return explorerStore.expandedNodes.includes(props.node.id)
})

// 是否选中 - 只有路径的最后一个节点才是选中状态
const isSelected = computed(() => {
  const path = explorerStore.currentPath
  return path.length > 0 && path[path.length - 1] === props.node.id
})

// 节点图标
const nodeIcon = computed(() => {
  const icons = {
    environment: FolderOpened,
    datacenter: Location,
    server: Monitor,
    container: Box,
    service: Setting,
    gpu: Cpu
  }
  return icons[props.node.type] || FolderOpened
})

// 状态类型
const statusType = computed(() => {
  const map = {
    online: 'success',
    offline: 'danger',
    maintenance: 'warning'
  }
  return map[props.node.status] || 'info'
})

// 状态文本
const statusText = computed(() => {
  const map = {
    online: '在线',
    offline: '离线',
    maintenance: '维护'
  }
  return map[props.node.status] || props.node.status
})

// 切换展开
function toggleExpand() {
  explorerStore.toggleNode(props.node.id)
}

// 点击节点
function handleClick() {
  explorerStore.navigateTo(props.node.id, props.node.type)
}

// 双击节点
function handleDoubleClick() {
  if (props.node.type === 'server') {
    explorerStore.loadServerContent(props.node.nodeId)
  } else if (hasChildren.value) {
    toggleExpand()
  }
}
</script>

<style lang="scss" scoped>
.tree-node {
  user-select: none;

  .node-content {
    display: flex;
    align-items: center;
    padding: 6px 12px;
    cursor: pointer;
    border-radius: 4px;
    margin: 0 8px;
    transition: background 0.2s;

    &:hover {
      background: #f5f7fa;
    }
  }

  &.selected > .node-content {
    background: #ecf5ff;
    color: #409EFF;
  }

  .expand-icon {
    width: 16px;
    height: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 4px;
    color: #909399;

    .el-icon {
      font-size: 12px;
      transition: transform 0.2s;

      &.rotated {
        transform: rotate(90deg);
      }
    }
  }

  .expand-placeholder {
    width: 16px;
    margin-right: 4px;
  }

  .node-icon {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 8px;

    .el-icon {
      font-size: 16px;
    }

    &.environment {
      color: #409EFF;
    }

    &.datacenter {
      color: #67C23A;
    }

    &.server {
      color: #909399;
    }

    &.container {
      color: #67C23A;
    }

    &.service {
      color: #E6A23C;
    }

    &.gpu {
      color: #F56C6C;
    }
  }

  .node-name {
    flex: 1;
    font-size: 13px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .status-tag {
    margin-left: 8px;
    font-size: 10px;
  }

  .node-count {
    font-size: 11px;
    color: #909399;
    background: #f0f2f5;
    padding: 2px 6px;
    border-radius: 8px;
    margin-left: 8px;
  }

  .node-children {
    overflow: hidden;
  }
}

// 展开/折叠动画
.expand-enter-active,
.expand-leave-active {
  transition: all 0.2s ease-out;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  transform: translateY(0);
}
</style>
