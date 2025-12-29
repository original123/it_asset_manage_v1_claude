<template>
  <div class="assets-page">
    <!-- 批量操作工具栏 -->
    <div class="batch-toolbar" v-if="assetsStore.selectedRows.length > 0">
      <div class="toolbar-left">
        <span class="selection-count">已选 {{ assetsStore.selectedRows.length }} 项</span>
        <el-button size="small" @click="handleBatchEdit" v-if="authStore.isAdmin">批量编辑</el-button>
        <el-button size="small" type="danger" @click="handleBatchDelete" v-if="authStore.isAdmin">批量删除</el-button>
        <el-button size="small" @click="handleBatchExport">导出选中</el-button>
      </div>
      <el-button size="small" text @click="assetsStore.clearSelection">取消选择</el-button>
    </div>

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
        @selection-change="handleSelectionChange"
      >
        <!-- 复选框列 -->
        <el-table-column type="selection" width="50" :selectable="checkSelectable" />

        <!-- 名称列 -->
        <el-table-column label="名称" min-width="350" fixed>
          <template #default="{ row }">
            <!-- 资源卡片行（特殊类型） -->
            <div v-if="row._type === '_resource_card'" class="server-resource-card-inline">
              <div class="card-grid">
                <div class="resource-item">
                  <span class="label">CPU {{ row.cpu_usage }}%</span>
                  <el-progress :percentage="row.cpu_usage || 0" :stroke-width="6" :color="getUsageColor(row.cpu_usage)" />
                  <span class="spec">{{ row.cpu_cores }}核</span>
                </div>
                <div class="resource-item">
                  <span class="label">内存 {{ row.memory_usage }}%</span>
                  <el-progress :percentage="row.memory_usage || 0" :stroke-width="6" :color="getUsageColor(row.memory_usage)" />
                  <span class="spec">{{ row.memory_gb }}GB</span>
                </div>
                <div class="resource-item" v-if="row.disk_usage !== null">
                  <span class="label">磁盘 {{ row.disk_usage }}%</span>
                  <el-progress :percentage="row.disk_usage || 0" :stroke-width="6" :color="getUsageColor(row.disk_usage)" />
                  <span class="spec">{{ row.disk_gb }}GB</span>
                </div>
              </div>
              <div class="card-footer-inline">
                <span class="update-time">更新于: {{ formatUpdateTime(row.updated_at) }}</span>
                <div class="quick-actions">
                  <el-button size="small" text @click.stop="copyText(row.ssh_command)">
                    <el-icon><DocumentCopy /></el-icon> SSH
                  </el-button>
                  <el-button size="small" text @click.stop="copyText(row.internal_ip)">
                    <el-icon><Link /></el-icon> IP
                  </el-button>
                </div>
              </div>
            </div>

            <!-- 普通行 -->
            <div v-else class="name-cell">
              <!-- 服务器 -->
              <template v-if="!row._type">
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
              </template>

              <!-- 容器 -->
              <template v-else-if="row._type === 'container'">
                <el-icon class="type-icon container"><Box /></el-icon>
                <span class="name">{{ row.name }}</span>
                <el-tag size="small" type="success">容器</el-tag>
              </template>

              <!-- 服务 -->
              <template v-else-if="row._type === 'service'">
                <el-icon class="type-icon service"><Setting /></el-icon>
                <span class="name">{{ row.name }}</span>
                <el-tag size="small" type="warning">服务</el-tag>
              </template>

              <!-- GPU -->
              <template v-else-if="row._type === 'gpu'">
                <el-icon class="type-icon gpu"><Cpu /></el-icon>
                <span class="name">{{ row.model }} {{ row.memory_gb }}GB</span>
                <el-tag size="small" type="primary">GPU</el-tag>
              </template>
            </div>
          </template>
        </el-table-column>

        <!-- 内网IP -->
        <el-table-column label="内网IP" width="220">
          <template #default="{ row }">
            <!-- 资源卡片行不显示 -->
            <template v-if="row._type === '_resource_card'"></template>
            <template v-else-if="!row._type">
              <span class="copyable" @click.stop="copyText(row.internal_ip)">
                {{ row.internal_ip }}
                <el-icon class="copy-icon"><DocumentCopy /></el-icon>
              </span>
            </template>
            <template v-else-if="row._type === 'container' && row.port_mappings?.length">
              <el-tooltip v-if="row.port_mappings.length > 1" placement="top">
                <template #content>
                  <div class="port-tooltip">
                    <div v-for="(pm, idx) in row.port_mappings" :key="idx" class="port-line">
                      {{ formatPortMapping(pm) }}
                    </div>
                  </div>
                </template>
                <span class="port-info copyable" @click.stop="copyText(formatPortMapping(row.port_mappings[0]))">
                  {{ formatPortMapping(row.port_mappings[0]) }}
                  <el-tag size="small" type="info" style="margin-left: 4px">+{{ row.port_mappings.length - 1 }}</el-tag>
                </span>
              </el-tooltip>
              <span v-else class="port-info copyable" @click.stop="copyText(formatPortMapping(row.port_mappings[0]))">
                {{ formatPortMapping(row.port_mappings[0]) }}
                <el-icon class="copy-icon"><DocumentCopy /></el-icon>
              </span>
            </template>
            <template v-else-if="row._type === 'service'">
              <span class="port-info">:{{ row.port || '-' }}</span>
            </template>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <!-- 外网IP -->
        <el-table-column label="外网IP" width="150">
          <template #default="{ row }">
            <template v-if="row._type === '_resource_card'"></template>
            <template v-else-if="!row._type && row.external_ip">
              <span class="copyable" @click.stop="copyText(row.external_ip)">
                {{ row.external_ip }}
                <el-icon class="copy-icon"><DocumentCopy /></el-icon>
              </span>
            </template>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <!-- 配置 -->
        <el-table-column label="配置" width="180">
          <template #default="{ row }">
            <template v-if="row._type === '_resource_card'"></template>
            <template v-else-if="!row._type && (row.cpu_cores || row.memory_gb)">
              <span>{{ row.cpu_cores || '-' }}C / {{ row.memory_gb || '-' }}G</span>
            </template>
            <template v-else-if="row._type === 'container'">
              <span class="text-muted">{{ row.image || '-' }}</span>
            </template>
            <template v-else-if="row._type === 'gpu'">
              <span class="text-muted">{{ row.memory_gb }}GB</span>
            </template>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <!-- 资源使用率 -->
        <el-table-column label="资源使用" width="200">
          <template #default="{ row }">
            <template v-if="row._type === '_resource_card'"></template>
            <template v-else-if="!row._type">
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
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <!-- 状态 -->
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <template v-if="row._type === '_resource_card'"></template>
            <el-tag
              v-else-if="row.status"
              :type="getStatusType(row.status)"
              size="small"
              effect="light"
            >
              {{ getStatusText(row.status) }}
            </el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <!-- 负责人 -->
        <el-table-column prop="responsible_person" label="负责人" width="100">
          <template #default="{ row }">
            <template v-if="row._type === '_resource_card'"></template>
            <template v-else>{{ row.responsible_person || row.assigned_to || '-' }}</template>
          </template>
        </el-table-column>

        <!-- 容器/GPU数量 -->
        <el-table-column label="容器/GPU" width="100" align="center">
          <template #default="{ row }">
            <template v-if="row._type === '_resource_card'"></template>
            <template v-else-if="!row._type">
              <span>{{ row.container_count }} / {{ row.gpu_count }}</span>
            </template>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>

        <!-- 操作 -->
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <!-- 资源卡片不显示操作 -->
            <template v-if="row._type === '_resource_card'"></template>

            <!-- 服务器操作 -->
            <el-button-group v-else-if="!row._type">
              <el-tooltip content="复制SSH命令">
                <el-button size="small" @click.stop="copyText(row.ssh_command || `ssh ${row.ssh_user}@${row.internal_ip}`)">
                  <el-icon><Connection /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="添加容器">
                <el-button size="small" @click.stop="showAddContainerDialog(row)">
                  <el-icon><Plus /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="编辑" v-if="authStore.isAdmin">
                <el-button size="small" @click.stop="showEditDialog(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="删除" v-if="authStore.isAdmin">
                <el-button size="small" type="danger" @click.stop="confirmDelete(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </el-button-group>

            <!-- 容器操作 -->
            <el-button-group v-else-if="row._type === 'container'">
              <el-tooltip content="复制端口映射">
                <el-button size="small" @click.stop="copyPortMapping(row)">
                  <el-icon><Link /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="添加服务">
                <el-button size="small" @click.stop="showAddServiceDialog(row)">
                  <el-icon><Plus /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="编辑" v-if="authStore.isAdmin || authStore.user.username === row.responsible_person">
                <el-button size="small" @click.stop="showEditDialog(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="删除" v-if="authStore.isAdmin || authStore.user.username === row.responsible_person">
                <el-button size="small" type="danger" @click.stop="confirmDelete(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </el-button-group>

            <!-- 服务操作 -->
            <el-button-group v-else-if="row._type === 'service'">
              <el-tooltip content="复制服务URL">
                <el-button size="small" @click.stop="copyServiceURL(row)">
                  <el-icon><Link /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="编辑" v-if="authStore.isAdmin || authStore.user.username === row.responsible_person">
                <el-button size="small" @click.stop="showEditDialog(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="删除" v-if="authStore.isAdmin || authStore.user.username === row.responsible_person">
                <el-button size="small" type="danger" @click.stop="confirmDelete(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </el-button-group>

            <!-- GPU操作 -->
            <el-button-group v-else-if="row._type === 'gpu'">
              <el-tooltip content="分配GPU">
                <el-button size="small" @click.stop="showAssignGPUDialog(row)">
                  <el-icon><User /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="编辑" v-if="authStore.isAdmin">
                <el-button size="small" @click.stop="showEditDialog(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="删除" v-if="authStore.isAdmin">
                <el-button size="small" type="danger" @click.stop="confirmDelete(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </el-button-group>

            <!-- 其他类型默认操作 -->
            <el-button-group v-else>
              <el-tooltip content="编辑" v-if="authStore.isAdmin">
                <el-button size="small" @click.stop="showEditDialog(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="删除" v-if="authStore.isAdmin">
                <el-button size="small" type="danger" @click.stop="confirmDelete(row)">
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
  Connection, Edit, Delete, Box, Setting, Cpu, Link, User
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

  // 恢复展开状态
  assetsStore.loadExpandState()

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

// 监听展开层级变化
watch(() => assetsStore.expandLevel, () => {
  loadData()
  assetsStore.saveExpandState() // 保存展开层级到localStorage
})

const loadData = async () => {
  await assetsStore.loadServersTree()

  // 根据展开层级自动展开行
  if (assetsStore.expandLevel >= 2) {
    const keys = []
    // 展开所有服务器
    assetsStore.servers.forEach(server => {
      keys.push(server.id)

      // 如果是第三层级，也展开所有容器
      if (assetsStore.expandLevel >= 3 && server.children) {
        server.children.forEach(child => {
          if (child._type === 'container') {
            keys.push(child.id)
          }
        })
      }
    })
    expandedKeys.value = keys
  } else {
    expandedKeys.value = []
  }
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
  // 只有服务器行才打开详情抽屉
  if (!row._type) {
    selectedServer.value = row
    serverDrawerVisible.value = true
  }
}

const formatPortMapping = (pm) => {
  if (!pm) return '-'
  return `容器:${pm.container_port}→内:${pm.internal_port}→外:${pm.external_port || '-'}`
}

const copyText = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制')
  } catch {
    ElMessage.error('复制失败')
  }
}

// 复制容器端口映射
const copyPortMapping = async (container) => {
  if (!container.port_mappings || container.port_mappings.length === 0) {
    ElMessage.warning('该容器没有端口映射')
    return
  }
  const text = container.port_mappings.map(pm =>
    formatPortMapping(pm)
  ).join('\n')
  await copyText(text)
}

// 复制服务URL
const copyServiceURL = async (service) => {
  // 构建服务URL (需要从父容器和服务器获取IP和端口信息)
  const url = `http://${service.container_ip || 'localhost'}:${service.port || '8080'}`
  await copyText(url)
}

// 显示添加服务对话框
const showAddServiceDialog = (container) => {
  ElMessage.info('添加服务功能开发中')
  // TODO: 实现添加服务对话框
}

// 显示GPU分配对话框
const showAssignGPUDialog = (gpu) => {
  ElMessage.info('GPU分配功能开发中')
  // TODO: 实现GPU分配对话框
}

// 统一的编辑方法
const showEditDialog = (row) => {
  if (!row._type) {
    // 服务器
    showEditServerDialog(row)
  } else {
    ElMessage.info(`编辑${row._type}功能开发中`)
    // TODO: 根据类型显示对应的编辑对话框
  }
}

// 统一的删除确认方法
const confirmDelete = (row) => {
  if (!row._type) {
    // 服务器
    confirmDeleteServer(row)
  } else {
    const typeNames = {
      container: '容器',
      service: '服务',
      gpu: 'GPU'
    }
    const typeName = typeNames[row._type] || '资产'

    ElMessageBox.confirm(
      `确定要删除${typeName} "${row.name}" 吗?`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    ).then(() => {
      ElMessage.info(`删除${typeName}功能开发中`)
      // TODO: 实现对应类型的删除API调用
    })
  }
}

const getUsageColor = (value) => {
  if (value >= 80) return '#F56C6C'
  if (value >= 60) return '#E6A23C'
  return '#67C23A'
}

const getStatusType = (status) => {
  const map = {
    // 服务器状态
    online: 'success',
    offline: 'danger',
    maintenance: 'warning',
    // 容器状态
    running: 'success',
    stopped: 'danger',
    error: 'danger',
    // 服务状态
    healthy: 'success',
    unhealthy: 'danger',
    // GPU状态
    available: 'success',
    in_use: 'warning',
    unavailable: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    // 服务器状态
    online: '在线',
    offline: '离线',
    maintenance: '维护中',
    // 容器状态
    running: '运行',
    stopped: '停止',
    error: '错误',
    // 服务状态
    healthy: '健康',
    unhealthy: '异常',
    // GPU状态
    available: '空闲',
    in_use: '使用中',
    unavailable: '不可用',
    free: '空闲'  // 额外添加
  }
  return map[status] || status
}

const getAvailableGpuCount = (server) => {
  if (!server.children) return 0
  const gpus = server.children.filter(c => c._type === 'gpu')
  return gpus.filter(g => g.is_available || g.status === 'available' || g.status === 'free').length
}

const formatUpdateTime = (time) => {
  if (!time) return '未知'
  const now = new Date()
  const updated = new Date(time)
  const diff = Math.floor((now - updated) / 1000 / 60) // 分钟

  if (diff < 1) return '刚刚'
  if (diff < 60) return `${diff}分钟前`
  if (diff < 1440) return `${Math.floor(diff / 60)}小时前`
  return `${Math.floor(diff / 1440)}天前`
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

// 批量操作处理函数
const handleSelectionChange = (rows) => {
  assetsStore.setSelection(rows)
}

const checkSelectable = (row) => {
  // 资源卡片行不可选
  return row._type !== '_resource_card'
}

const handleBatchDelete = async () => {
  const count = assetsStore.selectedRows.length
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${count} 项资产吗？相关的容器、服务和GPU数据也会被删除。`,
      '批量删除确认',
      { type: 'warning' }
    )

    // TODO: 调用批量删除API
    for (const row of assetsStore.selectedRows) {
      if (!row._type) {
        // 服务器
        await assetsApi.deleteServer(row.id)
      }
    }

    ElMessage.success(`已删除 ${count} 项`)
    assetsStore.clearSelection()
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || '删除失败')
    }
  }
}

const handleBatchEdit = () => {
  ElMessage.info('批量编辑功能开发中...')
}

const handleBatchExport = () => {
  const ids = Array.from(assetsStore.selectedIds)
  downloadFile(`/api/import-export/export?ids=${ids.join(',')}`, 'selected_assets.xlsx')
}
</script>

<style lang="scss" scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono&display=swap');

.assets-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

// 批量操作工具栏
.batch-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: linear-gradient(135deg, #ecf5ff 0%, #e1f0ff 100%);
  border-radius: 12px;
  margin-bottom: 12px;
  border: 1px solid #b3d8ff;
  animation: slideDown 0.3s ease;

  .toolbar-left {
    display: flex;
    align-items: center;
    gap: 12px;

    .selection-count {
      font-size: 14px;
      font-weight: 500;
      color: #409EFF;
    }
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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

  // 树形符号样式 (├─ └─ │)
  :deep(.el-table__row--level-1) {
    .el-table__indent {
      position: relative;

      &::before {
        content: '├─';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        color: #d9d9d9;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        line-height: 1;
        pointer-events: none;
      }
    }

    // 最后一个子节点使用 └─
    &:last-child .el-table__indent::before {
      content: '└─';
    }
  }

  // 第三层（服务）：添加嵌套树形符号
  :deep(.el-table__row--level-2) {
    .el-table__indent {
      position: relative;

      &::before {
        content: '│  └─';
        position: absolute;
        left: -16px;
        top: 50%;
        transform: translateY(-50%);
        color: #d9d9d9;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        line-height: 1;
        pointer-events: none;
        white-space: pre;
      }
    }

    // 如果是父容器的最后一个服务,不显示竖线
    &:last-child .el-table__indent::before {
      content: '   └─';
    }
  }

  .name-cell {
    display: flex;
    align-items: center;
    gap: 8px;

    .type-icon {
      font-size: 18px;

      &.server { color: #409EFF; }
      &.container { color: #67C23A; }
      &.service { color: #E6A23C; }
      &.gpu { color: #F56C6C; }
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

  .port-info {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
  }

  .port-tooltip {
    .port-line {
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      line-height: 1.8;
      white-space: nowrap;
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

  // 资源卡片内联样式（作为树形子行）
  .server-resource-card-inline {
    background: linear-gradient(135deg, #f5f7fa 0%, #fafbfc 100%);
    border-radius: 8px;
    padding: 16px 20px;
    margin: -8px -12px;
    border: 1px solid #e4e7ed;

    .card-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-bottom: 12px;
    }

    .resource-item {
      .label {
        display: block;
        font-size: 12px;
        font-weight: 500;
        color: #606266;
        margin-bottom: 6px;
        font-family: 'JetBrains Mono', monospace;
      }

      .spec {
        display: block;
        margin-top: 4px;
        font-size: 11px;
        color: #909399;
      }
    }

    .card-footer-inline {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 12px;
      border-top: 1px solid #e4e7ed;

      .update-time {
        font-size: 11px;
        color: #909399;
      }

      .quick-actions {
        display: flex;
        gap: 8px;
      }
    }
  }
}
</style>
