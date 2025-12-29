<template>
  <div class="status-bar">
    <div class="status-left">
      <!-- 当前位置信息 -->
      <span class="status-item" v-if="explorerStore.currentNode">
        <el-icon><Location /></el-icon>
        {{ locationText }}
      </span>

      <!-- 内容统计 -->
      <span class="status-item" v-if="explorerStore.currentNode?.type === 'server'">
        <el-icon><Box /></el-icon>
        {{ explorerStore.contentStats.containers }} 容器
      </span>
      <span class="status-item" v-if="explorerStore.currentNode?.type === 'server'">
        <el-icon><Cpu /></el-icon>
        {{ explorerStore.contentStats.gpus }} GPU
      </span>
      <span class="status-item" v-if="explorerStore.currentNode?.type === 'server'">
        <el-icon><Setting /></el-icon>
        {{ explorerStore.contentStats.services }} 服务
      </span>
    </div>

    <div class="status-center">
      <!-- 加载状态 -->
      <transition name="fade">
        <span v-if="explorerStore.loading" class="loading-indicator">
          <el-icon class="is-loading"><Loading /></el-icon>
          加载中...
        </span>
      </transition>
    </div>

    <div class="status-right">
      <!-- 视图模式 -->
      <span class="status-item view-mode">
        <el-icon v-if="explorerStore.viewMode === 'grid'"><Grid /></el-icon>
        <el-icon v-else><List /></el-icon>
        {{ explorerStore.viewMode === 'grid' ? '网格视图' : '列表视图' }}
      </span>

      <!-- 分组方式 -->
      <span class="status-item grouping-mode">
        <el-icon><Setting /></el-icon>
        {{ groupingModeText }}
      </span>

      <!-- 快捷键提示 -->
      <el-tooltip content="Ctrl+K 搜索 | Backspace 返回 | F5 刷新" placement="top">
        <span class="status-item keyboard-hint">
          <el-icon><InfoFilled /></el-icon>
        </span>
      </el-tooltip>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Location, Box, Cpu, Setting, Loading,
  Grid, List, InfoFilled
} from '@element-plus/icons-vue'
import { useExplorerStore } from '@/stores/explorer'

const explorerStore = useExplorerStore()

// 当前位置文本
const locationText = computed(() => {
  if (!explorerStore.currentNode) return ''

  const typeNames = {
    environment: '环境',
    datacenter: '机房',
    server: '服务器'
  }

  const typeName = typeNames[explorerStore.currentNode.type] || ''
  return `${typeName}: ${explorerStore.currentNode.name}`
})

// 分组方式文本
const groupingModeText = computed(() => {
  const modes = {
    'environment-first': '环境优先',
    'datacenter-first': '机房优先',
    'flat': '扁平列表'
  }
  return modes[explorerStore.groupingMode] || ''
})
</script>

<style lang="scss" scoped>
.status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 20px;
  background: #fff;
  border-top: 1px solid #e4e7ed;
  font-size: 12px;
  color: #909399;
  min-height: 28px;
}

.status-left,
.status-center,
.status-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 4px;

  .el-icon {
    font-size: 14px;
  }
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #409EFF;

  .el-icon {
    font-size: 14px;
  }
}

.keyboard-hint {
  cursor: help;
  opacity: 0.7;

  &:hover {
    opacity: 1;
  }
}

// 过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
