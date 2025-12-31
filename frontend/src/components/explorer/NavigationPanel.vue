<template>
  <div class="navigation-panel-inner">
    <!-- 资产导航树 -->
    <div class="nav-section">
      <div class="section-header">
        <span class="section-title">
          <el-icon><OfficeBuilding /></el-icon>
          资产导航
        </span>
        <el-button link size="small" @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>

      <div class="tree-container" v-loading="explorerStore.treeLoading">
        <div
          v-for="node in explorerStore.navigationTree"
          :key="node.id"
          class="tree-node-wrapper"
        >
          <TreeNode :node="node" :level="0" />
        </div>

        <div v-if="explorerStore.navigationTree.length === 0 && !explorerStore.treeLoading" class="empty-tree">
          <el-empty description="暂无资产数据" :image-size="60" />
        </div>
      </div>
    </div>

    <!-- 快捷访问 -->
    <div class="nav-section">
      <div class="section-header collapsible" @click="toggleQuickAccess">
        <span class="section-title">
          <el-icon><Promotion /></el-icon>
          快捷访问
        </span>
        <el-icon class="collapse-icon" :class="{ expanded: quickAccessExpanded }">
          <ArrowRight />
        </el-icon>
      </div>

      <div v-show="quickAccessExpanded" class="quick-access-list">
        <!-- 离线服务器 -->
        <div
          class="quick-access-item"
          @click="filterByStatus('offline')"
        >
          <span class="item-icon offline">
            <el-icon><CircleClose /></el-icon>
          </span>
          <span class="item-name">离线服务器</span>
          <span class="item-count">{{ explorerStore.quickAccess.offlineServers.length }}</span>
        </div>

        <!-- 高负载 -->
        <div
          class="quick-access-item"
          @click="filterByHighLoad"
        >
          <span class="item-icon warning">
            <el-icon><Warning /></el-icon>
          </span>
          <span class="item-name">高负载</span>
          <span class="item-count">{{ explorerStore.quickAccess.highLoadServers.length }}</span>
        </div>

        <!-- 最近访问 -->
        <div class="recent-access-header">
          <el-icon><Clock /></el-icon>
          <span>最近访问</span>
        </div>
        <div
          v-for="item in explorerStore.quickAccess.recentAccess"
          :key="item.id"
          class="quick-access-item sub-item"
          @click="navigateToRecent(item)"
        >
          <el-icon><Monitor /></el-icon>
          <span class="item-name">{{ item.name }}</span>
        </div>
        <div v-if="explorerStore.quickAccess.recentAccess.length === 0" class="no-recent">
          暂无最近访问
        </div>
      </div>
    </div>

    <!-- 导航设置 -->
    <div class="nav-section nav-settings">
      <div class="section-header collapsible" @click="toggleSettings">
        <span class="section-title">
          <el-icon><Setting /></el-icon>
          导航设置
        </span>
        <el-icon class="collapse-icon" :class="{ expanded: settingsExpanded }">
          <ArrowRight />
        </el-icon>
      </div>

      <div v-show="settingsExpanded" class="settings-content">
        <div class="setting-label">分组方式</div>
        <el-radio-group
          v-model="groupingMode"
          size="small"
          @change="handleGroupingChange"
        >
          <el-radio label="environment-first">环境 → 机房</el-radio>
          <el-radio label="datacenter-first">机房 → 环境</el-radio>
          <el-radio label="flat">扁平列表</el-radio>
        </el-radio-group>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  OfficeBuilding, Refresh, Promotion, ArrowRight,
  CircleClose, Warning, Clock, Monitor, Setting
} from '@element-plus/icons-vue'
import { useExplorerStore } from '@/stores/explorer'
import TreeNode from './TreeNode.vue'

const explorerStore = useExplorerStore()

// 折叠状态
const quickAccessExpanded = ref(true)
const settingsExpanded = ref(false)

// 分组方式
const groupingMode = computed({
  get: () => explorerStore.groupingMode,
  set: (val) => explorerStore.setGroupingMode(val)
})

function toggleQuickAccess() {
  quickAccessExpanded.value = !quickAccessExpanded.value
}

function toggleSettings() {
  settingsExpanded.value = !settingsExpanded.value
}

function handleRefresh() {
  // loadNavigationTree 内部会同时更新快捷访问数据
  explorerStore.loadNavigationTree()
}

function handleGroupingChange(mode) {
  explorerStore.setGroupingMode(mode)
}

function filterByStatus(status) {
  if (status === 'offline') {
    explorerStore.filterByOffline()
  }
}

function filterByHighLoad() {
  explorerStore.filterByHighLoad()
}

function navigateToRecent(item) {
  explorerStore.navigateTo(`server-${item.id}`, 'server')
}
</script>

<style lang="scss" scoped>
.navigation-panel-inner {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.nav-section {
  border-bottom: 1px solid #ebeef5;

  &:first-child {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: #fafafa;

    &.collapsible {
      cursor: pointer;

      &:hover {
        background: #f0f2f5;
      }
    }

    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      font-weight: 500;
      color: #606266;

      .el-icon {
        font-size: 16px;
      }
    }

    .collapse-icon {
      transition: transform 0.2s;
      color: #909399;

      &.expanded {
        transform: rotate(90deg);
      }
    }
  }
}

.tree-container {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.empty-tree {
  padding: 20px;
}

// 快捷访问
.quick-access-list {
  padding: 8px 0;
}

.quick-access-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: #f5f7fa;
  }

  &.sub-item {
    padding-left: 32px;

    .el-icon {
      font-size: 14px;
      color: #909399;
      margin-right: 8px;
    }
  }

  .item-icon {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 8px;

    .el-icon {
      font-size: 12px;
      color: #fff;
    }

    &.offline {
      background: #F56C6C;
    }

    &.warning {
      background: #E6A23C;
    }
  }

  .item-name {
    flex: 1;
    font-size: 13px;
    color: #606266;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .item-count {
    font-size: 12px;
    color: #909399;
    background: #f0f2f5;
    padding: 2px 8px;
    border-radius: 10px;
  }
}

.recent-access-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px 4px;
  font-size: 12px;
  color: #909399;

  .el-icon {
    font-size: 14px;
  }
}

.no-recent {
  padding: 8px 32px;
  font-size: 12px;
  color: #c0c4cc;
}

// 导航设置
.nav-settings {
  border-bottom: none;
}

.settings-content {
  padding: 12px 16px;

  .setting-label {
    font-size: 12px;
    color: #909399;
    margin-bottom: 8px;
  }

  .el-radio-group {
    display: flex;
    flex-direction: column;
    gap: 8px;

    :deep(.el-radio) {
      margin-right: 0;

      .el-radio__label {
        font-size: 13px;
      }
    }
  }
}
</style>
