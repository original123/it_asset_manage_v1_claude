<template>
  <div class="breadcrumb-nav">
    <div class="breadcrumb-items">
      <!-- 首页 -->
      <span class="breadcrumb-item home" @click="navigateHome">
        <el-icon><HomeFilled /></el-icon>
      </span>

      <!-- 筛选模式 -->
      <template v-if="explorerStore.isFilterMode">
        <span class="breadcrumb-separator">
          <el-icon><ArrowRight /></el-icon>
        </span>
        <span class="breadcrumb-item filter current">
          <el-icon class="item-icon"><Filter /></el-icon>
          <span class="item-name">{{ filterTitle }}</span>
          <el-tag size="small" type="info">{{ explorerStore.filteredServers.length }}</el-tag>
        </span>
      </template>

      <!-- 正常路径项 -->
      <template v-else>
        <template v-for="(item, index) in explorerStore.breadcrumbPath" :key="item.id">
          <span class="breadcrumb-separator">
            <el-icon><ArrowRight /></el-icon>
          </span>
          <span
            class="breadcrumb-item"
            :class="{ current: index === explorerStore.breadcrumbPath.length - 1 }"
            @click="navigateTo(item, index)"
          >
            <el-icon class="item-icon">
              <component :is="getIcon(item.type)" />
            </el-icon>
            <span class="item-name">{{ item.name }}</span>
          </span>
        </template>

        <!-- 当前服务器信息 -->
        <template v-if="explorerStore.currentNode?.type === 'server'">
          <span class="breadcrumb-separator">
            <el-icon><ArrowRight /></el-icon>
          </span>
          <span class="breadcrumb-item current">
            <el-icon class="item-icon"><Monitor /></el-icon>
            <span class="item-name">{{ explorerStore.currentNode.name }}</span>
          </span>
        </template>
      </template>
    </div>

    <!-- 返回/清除筛选按钮 -->
    <el-button
      v-if="explorerStore.isFilterMode"
      link
      size="small"
      @click="clearFilter"
    >
      <el-icon><Close /></el-icon>
      清除筛选
    </el-button>
    <el-button
      v-else-if="canGoBack"
      link
      size="small"
      @click="navigateBack"
    >
      <el-icon><Back /></el-icon>
      返回
    </el-button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  HomeFilled, ArrowRight, Back,
  FolderOpened, Location, Monitor, Box, Setting, Cpu,
  Filter, Close
} from '@element-plus/icons-vue'
import { useExplorerStore } from '@/stores/explorer'

const explorerStore = useExplorerStore()

const canGoBack = computed(() => {
  return explorerStore.breadcrumbPath.length > 0 || explorerStore.currentNode
})

// 筛选模式标题
const filterTitle = computed(() => {
  const mode = explorerStore.filterMode
  if (mode === 'offline') return '离线服务器'
  if (mode === 'highLoad') return '高负载服务器'
  return '筛选结果'
})

function getIcon(type) {
  const icons = {
    environment: FolderOpened,
    datacenter: Location,
    server: Monitor,
    container: Box,
    service: Setting,
    gpu: Cpu
  }
  return icons[type] || FolderOpened
}

function navigateHome() {
  explorerStore.clearFilter()
  explorerStore.navigateHome()
}

function navigateTo(item, index) {
  // 点击面包屑项，截断路径到该位置
  explorerStore.currentPath = explorerStore.currentPath.slice(0, index + 1)
  explorerStore.navigateTo(item.id, item.type)
}

function navigateBack() {
  explorerStore.navigateBack()
}

function clearFilter() {
  explorerStore.clearFilter()
}
</script>

<style lang="scss" scoped>
.breadcrumb-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  min-height: 40px;
}

.breadcrumb-items {
  display: flex;
  align-items: center;
  gap: 4px;
  overflow: hidden;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s;

  &:hover:not(.current) {
    background: #f5f7fa;
    color: #409EFF;
  }

  &.home {
    padding: 4px 6px;

    .el-icon {
      font-size: 16px;
    }
  }

  &.current {
    color: #303133;
    font-weight: 500;
    cursor: default;
  }

  &.filter {
    background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
    border: 1px solid #b3d8ff;

    .item-icon {
      color: #409EFF;
    }

    .el-tag {
      margin-left: 4px;
    }
  }

  .item-icon {
    font-size: 14px;
  }

  .item-name {
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.breadcrumb-separator {
  color: #c0c4cc;
  display: flex;
  align-items: center;

  .el-icon {
    font-size: 12px;
  }
}
</style>
