<template>
  <div class="assets-page">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <!-- 筛选器 -->
        <div class="filter-tags">
          <span class="filter-label">环境:</span>
          <el-tag
            v-for="env in assetsStore.environments"
            :key="env.id"
            :type="filters.environment_id === env.id ? '' : 'info'"
            :effect="filters.environment_id === env.id ? 'dark' : 'plain'"
            :style="filters.environment_id === env.id ? { backgroundColor: env.color, borderColor: env.color } : {}"
            class="filter-tag"
            @click="toggleFilter('environment_id', env.id)"
          >
            {{ env.name }}
          </el-tag>
        </div>

        <el-divider direction="vertical" />

        <div class="filter-tags">
          <span class="filter-label">机房:</span>
          <el-tag
            v-for="dc in assetsStore.datacenters"
            :key="dc.id"
            :type="filters.datacenter_id === dc.id ? '' : 'info'"
            :effect="filters.datacenter_id === dc.id ? 'dark' : 'plain'"
            class="filter-tag"
            @click="toggleFilter('datacenter_id', dc.id)"
          >
            {{ dc.name }}
          </el-tag>
        </div>

        <el-button
          v-if="hasFilters"
          text
          type="primary"
          @click="clearFilters"
        >
          清除筛选
        </el-button>
      </div>

      <div class="toolbar-right">
        <!-- 展开层级 -->
        <el-select
          v-model="assetsStore.expandLevel"
          placeholder="展开层级"
          style="width: 120px"
          @change="loadData"
        >
          <el-option :value="1" label="仅服务器" />
          <el-option :value="2" label="展开容器" />
          <el-option :value="3" label="全部展开" />
        </el-select>

        <!-- 导入导出 -->
        <el-dropdown trigger="click" @command="handleExportCommand">
          <el-button>
            <el-icon><Download /></el-icon>
            导入/导出
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="template">下载导入模板</el-dropdown-item>
              <el-dropdown-item command="import">导入数据</el-dropdown-item>
              <el-dropdown-item divided command="export">导出数据</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- 新增按钮 -->
        <el-button type="primary" @click="showAddServerDialog" v-if="authStore.isAdmin">
          <el-icon><Plus /></el-icon>
          添加服务器
        </el-button>
      </div>
    </div>

    <!-- 资产树形表格 -->
    <div class="assets-table-wrapper">
      <el-table
        :data="assetsStore.servers"
        v-loading="assetsStore.loading"
        row-key="id"
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        :expand-row-keys="expandedKeys"
        stripe
        class="assets-table"
        @row-click="handleRowClick"
      >
        <!-- 名称列 -->
        <el-table-column label="名称" min-width="280" fixed>
          <template #default="{ row }">
            <div class="name-cell">
              <el-icon class="type-icon server"><Monitor /></el-icon>
              <span class="name">{{ row.name }}</span>
              <el-tag
                size="small"
                :style="{ backgroundColor: row.environment_color, borderColor: row.environment_color }"
                effect="dark"
                class="env-tag"
              >
                {{ row.environment_name }}
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <!-- 内网IP -->
        <el-table-column label="内网IP" width="150">
          <template #default="{ row }">
            <span class="copyable" @click.stop="copyText(row.internal_ip)">
              {{ row.internal_ip }}
              <el-icon class="copy-icon"><DocumentCopy /></el-icon>
            </span>
          </template>
        </el-table-column>

        <!-- 外网IP -->
        <el-table-column label="外网IP" width="150">
          <template #default="{ row }">
            <span v-if="row.external_ip" class="copyable" @click.stop="copyText(row.external_ip)">
              {{ row.external_ip }}
              <el-icon class="copy-icon"><DocumentCopy /></el-icon>
            </span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <!-- 配置 -->
        <el-table-column label="配置" width="160">
          <template #default="{ row }">
            <span v-if="row.cpu_cores || row.memory_gb">
              {{ row.cpu_cores || '-' }}C / {{ row.memory_gb || '-' }}G
            </span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <!-- 资源使用率 -->
        <el-table-column label="资源使用" width="200">
          <template #default="{ row }">
            <div class="usage-bars">
              <div class="usage-item">
                <span class="usage-label">CPU</span>
                <el-progress
                  :percentage="row.cpu_usage || 0"
                  :stroke-width="6"
                  :color="getUsageColor(row.cpu_usage)"
                  :show-text="false"
                />
                <span class="usage-value">{{ row.cpu_usage || 0 }}%</span>
              </div>
              <div class="usage-item">
                <span class="usage-label">MEM</span>
                <el-progress
                  :percentage="row.memory_usage || 0"
                  :stroke-width="6"
                  :color="getUsageColor(row.memory_usage)"
                  :show-text="false"
                />
                <span class="usage-value">{{ row.memory_usage || 0 }}%</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- 状态 -->
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag
              :type="getStatusType(row.status)"
              size="small"
              effect="light"
            >
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 负责人 -->
        <el-table-column prop="responsible_person" label="负责人" width="100" />

        <!-- 容器/GPU数量 -->
        <el-table-column label="容器/GPU" width="100" align="center">
          <template #default="{ row }">
            <span>{{ row.container_count }} / {{ row.gpu_count }}</span>
          </template>
        </el-table-column>

        <!-- 操作 -->
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-tooltip content="复制SSH命令">
                <el-button size="small" @click.stop="copyText(row.ssh_command)">
                  <el-icon><Connection /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="添加容器">
                <el-button size="small" @click.stop="showAddContainerDialog(row)">
                  <el-icon><Plus /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="编辑" v-if="authStore.isAdmin">
                <el-button size="small" @click.stop="showEditServerDialog(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="删除" v-if="authStore.isAdmin">
                <el-button size="small" type="danger" @click.stop="confirmDeleteServer(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 服务器详情抽屉 -->
    <ServerDrawer
      v-model="serverDrawerVisible"
      :server="selectedServer"
      @refresh="loadData"
    />

    <!-- 服务器表单弹窗 -->
    <ServerFormDialog
      v-model="serverFormVisible"
      :server="editingServer"
      @success="loadData"
    />

    <!-- 容器表单弹窗 -->
    <ContainerFormDialog
      v-model="containerFormVisible"
      :server="selectedServer"
      :container="editingContainer"
      @success="loadData"
    />

    <!-- 导入弹窗 -->
    <ImportDialog v-model="importVisible" @success="loadData" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Download, ArrowDown, Plus, Monitor, DocumentCopy,
  Connection, Edit, Delete
} from '@element-plus/icons-vue'
import { useAssetsStore } from '@/stores/assets'
import { useAuthStore } from '@/stores/auth'
import { assetsApi } from '@/api/assets'
import ServerDrawer from '@/components/ServerDrawer.vue'
import ServerFormDialog from '@/components/ServerFormDialog.vue'
import ContainerFormDialog from '@/components/ContainerFormDialog.vue'
import ImportDialog from '@/components/ImportDialog.vue'
import { importExportApi } from '@/api/admin'

const route = useRoute()
const assetsStore = useAssetsStore()
const authStore = useAuthStore()

const filters = computed(() => assetsStore.filters)
const hasFilters = computed(() => {
  return filters.value.environment_id || filters.value.datacenter_id || filters.value.keyword
})

const expandedKeys = ref([])
const serverDrawerVisible = ref(false)
const serverFormVisible = ref(false)
const containerFormVisible = ref(false)
const importVisible = ref(false)
const selectedServer = ref(null)
const editingServer = ref(null)
const editingContainer = ref(null)

onMounted(async () => {
  // 等待 token 就绪（解决登录跳转后的时序问题）
  let retries = 0
  while (!localStorage.getItem('token') && retries < 10) {
    await new Promise(resolve => setTimeout(resolve, 50))
    retries++
  }

  await Promise.all([
    assetsStore.loadDatacenters(),
    assetsStore.loadEnvironments()
  ])
  loadData()

  // 处理URL参数
  if (route.query.keyword) {
    assetsStore.setFilter('keyword', route.query.keyword)
  }
})

watch(() => route.query.keyword, (val) => {
  if (val) {
    assetsStore.setFilter('keyword', val)
    loadData()
  }
})

const loadData = () => {
  assetsStore.loadServersTree()
}

const toggleFilter = (key, value) => {
  if (filters.value[key] === value) {
    assetsStore.setFilter(key, null)
  } else {
    assetsStore.setFilter(key, value)
  }
  loadData()
}

const clearFilters = () => {
  assetsStore.clearFilters()
  loadData()
}

const handleRowClick = (row) => {
  selectedServer.value = row
  serverDrawerVisible.value = true
}

const copyText = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制')
  } catch {
    ElMessage.error('复制失败')
  }
}

const getUsageColor = (value) => {
  if (value >= 80) return '#F56C6C'
  if (value >= 60) return '#E6A23C'
  return '#67C23A'
}

const getStatusType = (status) => {
  const map = {
    online: 'success',
    offline: 'danger',
    maintenance: 'warning'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    online: '在线',
    offline: '离线',
    maintenance: '维护中'
  }
  return map[status] || status
}

const showAddServerDialog = () => {
  editingServer.value = null
  serverFormVisible.value = true
}

const showEditServerDialog = (server) => {
  editingServer.value = server
  serverFormVisible.value = true
}

const showAddContainerDialog = (server) => {
  selectedServer.value = server
  editingContainer.value = null
  containerFormVisible.value = true
}

const confirmDeleteServer = async (server) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除服务器 "${server.name}" 吗？相关的容器、服务和GPU数据也会被删除。`,
      '确认删除',
      { type: 'warning' }
    )
    await assetsApi.deleteServer(server.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || '删除失败')
    }
  }
}

const handleExportCommand = async (command) => {
  switch (command) {
    case 'template':
      downloadFile('/api/import-export/template', 'import_template.xlsx')
      break
    case 'import':
      importVisible.value = true
      break
    case 'export':
      downloadFile('/api/import-export/export?type=all', 'export_data.xlsx')
      break
  }
}

const downloadFile = (url, filename) => {
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
}
</script>

<style lang="scss" scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono&display=swap');

.assets-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

// 工具栏
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #fff;
  border-radius: 12px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;

  .filter-label {
    font-size: 13px;
    color: #606266;
    margin-right: 4px;
  }

  .filter-tags {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .filter-tag {
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      transform: scale(1.05);
    }
  }
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

// 资产表格
.assets-table-wrapper {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.assets-table {
  font-family: 'Inter', sans-serif;

  .name-cell {
    display: flex;
    align-items: center;
    gap: 8px;

    .type-icon {
      font-size: 18px;

      &.server { color: #409EFF; }
      &.container { color: #67C23A; }
      &.service { color: #E6A23C; }
    }

    .name {
      font-weight: 500;
      color: #303133;
    }

    .env-tag {
      font-size: 10px;
    }
  }

  .copyable {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    cursor: pointer;
    transition: color 0.2s;

    .copy-icon {
      opacity: 0;
      font-size: 12px;
      transition: opacity 0.2s;
    }

    &:hover {
      color: #409EFF;

      .copy-icon {
        opacity: 1;
      }
    }
  }

  .text-muted {
    color: #c0c4cc;
  }

  .usage-bars {
    display: flex;
    flex-direction: column;
    gap: 4px;

    .usage-item {
      display: flex;
      align-items: center;
      gap: 8px;

      .usage-label {
        width: 28px;
        font-size: 10px;
        color: #909399;
        font-family: 'JetBrains Mono', monospace;
      }

      .el-progress {
        flex: 1;
      }

      .usage-value {
        width: 36px;
        font-size: 11px;
        color: #606266;
        text-align: right;
        font-family: 'JetBrains Mono', monospace;
      }
    }
  }
}
</style>
