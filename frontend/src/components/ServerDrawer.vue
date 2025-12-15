<template>
  <el-drawer
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="服务器详情"
    size="520px"
  >
    <template v-if="server">
      <div class="server-detail">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h4>基本信息</h4>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="名称">{{ server.name }}</el-descriptions-item>
            <el-descriptions-item label="机房">{{ server.datacenter_name }}</el-descriptions-item>
            <el-descriptions-item label="环境">
              <el-tag :style="{ backgroundColor: server.environment_color }" effect="dark" size="small">
                {{ server.environment_name }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="内网IP">
              <span class="copyable" @click="copyText(server.internal_ip)">
                {{ server.internal_ip }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="外网IP">
              <span v-if="server.external_ip" class="copyable" @click="copyText(server.external_ip)">
                {{ server.external_ip }}
              </span>
              <span v-else class="text-muted">-</span>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(server.status)" size="small">
                {{ getStatusText(server.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="负责人">{{ server.responsible_person || '-' }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 硬件配置 -->
        <div class="detail-section">
          <h4>硬件配置</h4>
          <div class="config-grid">
            <div class="config-item">
              <span class="label">CPU</span>
              <span class="value">{{ server.cpu_cores || '-' }} 核</span>
            </div>
            <div class="config-item">
              <span class="label">内存</span>
              <span class="value">{{ server.memory_gb || '-' }} GB</span>
            </div>
            <div class="config-item">
              <span class="label">磁盘</span>
              <span class="value">{{ server.disk_gb || '-' }} GB</span>
            </div>
            <div class="config-item">
              <span class="label">系统</span>
              <span class="value">{{ server.os_type || '-' }}</span>
            </div>
          </div>
        </div>

        <!-- SSH连接 -->
        <div class="detail-section">
          <h4>SSH连接</h4>
          <div class="ssh-command">
            <code>{{ server.ssh_command }}</code>
            <el-button size="small" @click="copyText(server.ssh_command)">
              <el-icon><DocumentCopy /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 资源使用 -->
        <div class="detail-section">
          <h4>资源使用</h4>
          <div class="usage-list">
            <div class="usage-item">
              <span class="label">CPU</span>
              <el-progress :percentage="server.cpu_usage || 0" :color="getUsageColor(server.cpu_usage)" />
            </div>
            <div class="usage-item">
              <span class="label">内存</span>
              <el-progress :percentage="server.memory_usage || 0" :color="getUsageColor(server.memory_usage)" />
            </div>
            <div class="usage-item">
              <span class="label">磁盘</span>
              <el-progress :percentage="server.disk_usage || 0" :color="getUsageColor(server.disk_usage)" />
            </div>
          </div>
        </div>

        <!-- 容器列表 -->
        <div class="detail-section">
          <div class="section-header">
            <h4>容器 ({{ server.containers?.length || 0 }})</h4>
            <el-button size="small" type="primary" plain @click="showAddContainer">
              <el-icon><Plus /></el-icon> 添加
            </el-button>
          </div>
          <div class="container-list" v-if="server.containers?.length">
            <div
              v-for="container in server.containers"
              :key="container.id"
              class="container-item"
            >
              <div class="container-header">
                <div class="container-name">
                  <el-icon><Box /></el-icon>
                  {{ container.name }}
                </div>
                <div class="container-actions">
                  <el-tag :type="getStatusType(container.status)" size="small">
                    {{ container.status }}
                  </el-tag>
                  <el-button size="small" text @click="showAddService(container)">
                    <el-icon><Plus /></el-icon>服务
                  </el-button>
                </div>
              </div>
              <!-- 服务列表 -->
              <div class="services-list" v-if="container.services?.length">
                <div
                  v-for="service in container.services"
                  :key="service.id"
                  class="service-item"
                >
                  <div class="service-info">
                    <el-icon :style="{ color: getServiceTypeColor(service.service_type) }"><Promotion /></el-icon>
                    <span class="service-name">{{ service.name }}</span>
                    <span class="service-port" v-if="service.port">:{{ service.port }}</span>
                  </div>
                  <div class="service-actions">
                    <el-tag
                      :type="service.status === 'healthy' ? 'success' : 'danger'"
                      size="small"
                    >
                      {{ service.status === 'healthy' ? '健康' : '异常' }}
                    </el-tag>
                    <el-button size="small" text type="primary" @click="showEditService(container, service)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button size="small" text type="danger" @click="confirmDeleteService(service)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
              <div v-else class="empty-services">暂无服务</div>
            </div>
          </div>
          <el-empty v-else description="暂无容器" :image-size="60" />
        </div>

        <!-- GPU列表 -->
        <div class="detail-section">
          <div class="section-header">
            <h4>GPU ({{ server.gpus?.length || 0 }})</h4>
            <el-button size="small" type="primary" plain @click="showAddGpu" v-if="isAdmin">
              <el-icon><Plus /></el-icon> 添加
            </el-button>
          </div>
          <div class="gpu-list" v-if="server.gpus?.length">
            <div v-for="gpu in server.gpus" :key="gpu.id" class="gpu-item">
              <div class="gpu-info">
                <span class="gpu-model">{{ gpu.model }}</span>
                <span class="gpu-memory">{{ gpu.memory_gb }}GB</span>
              </div>
              <div class="gpu-actions">
                <el-tag :type="gpu.status === 'free' ? 'success' : 'warning'" size="small">
                  {{ gpu.status === 'free' ? '空闲' : gpu.assigned_user_name }}
                </el-tag>
                <el-button size="small" text type="primary" @click="showAssignGpu(gpu)" v-if="isAdmin">
                  {{ gpu.status === 'free' ? '分配' : '管理' }}
                </el-button>
                <el-button size="small" text type="danger" @click="confirmDeleteGpu(gpu)" v-if="isAdmin">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无GPU" :image-size="60" />
        </div>
      </div>
    </template>

    <!-- 服务表单弹窗 -->
    <ServiceFormDialog
      v-model="serviceFormVisible"
      :container="selectedContainer"
      :service="editingService"
      @success="handleRefresh"
    />

    <!-- GPU表单弹窗 -->
    <GPUFormDialog
      v-model="gpuFormVisible"
      :server="server"
      :gpu="editingGpu"
      @success="handleRefresh"
    />

    <!-- GPU分配弹窗 -->
    <GPUAssignDialog
      v-model="gpuAssignVisible"
      :gpu="selectedGpu"
      @success="handleRefresh"
    />
  </el-drawer>
</template>

<script setup>
import { ref, computed } from 'vue'
import { DocumentCopy, Box, Plus, Edit, Delete, Promotion } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { assetsApi } from '@/api/assets'
import ServiceFormDialog from './ServiceFormDialog.vue'
import GPUFormDialog from './GPUFormDialog.vue'
import GPUAssignDialog from './GPUAssignDialog.vue'

const props = defineProps({
  modelValue: Boolean,
  server: Object
})

const emit = defineEmits(['update:modelValue', 'refresh'])

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.isAdmin)

// Service management
const serviceFormVisible = ref(false)
const selectedContainer = ref(null)
const editingService = ref(null)

// GPU management
const gpuFormVisible = ref(false)
const gpuAssignVisible = ref(false)
const editingGpu = ref(null)
const selectedGpu = ref(null)

const copyText = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制')
  } catch {
    ElMessage.error('复制失败')
  }
}

const getStatusType = (status) => {
  const map = { online: 'success', running: 'success', offline: 'danger', stopped: 'danger', healthy: 'success' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = { online: '在线', offline: '离线', maintenance: '维护中' }
  return map[status] || status
}

const getUsageColor = (value) => {
  if (value >= 80) return '#F56C6C'
  if (value >= 60) return '#E6A23C'
  return '#67C23A'
}

const getServiceTypeColor = (type) => {
  const colors = {
    web: '#409EFF',
    api: '#67C23A',
    database: '#E6A23C',
    cache: '#F56C6C',
    queue: '#909399',
    proxy: '#9C27B0',
    monitor: '#00BCD4',
    other: '#606266'
  }
  return colors[type] || colors.other
}

// Service actions
const showAddService = (container) => {
  selectedContainer.value = container
  editingService.value = null
  serviceFormVisible.value = true
}

const showEditService = (container, service) => {
  selectedContainer.value = container
  editingService.value = service
  serviceFormVisible.value = true
}

const confirmDeleteService = async (service) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除服务 "${service.name}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    await assetsApi.deleteService(service.id)
    ElMessage.success('删除成功')
    handleRefresh()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || '删除失败')
    }
  }
}

// Container action
const showAddContainer = () => {
  emit('update:modelValue', false)
  emit('refresh', { action: 'addContainer', server: props.server })
}

// GPU actions
const showAddGpu = () => {
  editingGpu.value = null
  gpuFormVisible.value = true
}

const showAssignGpu = (gpu) => {
  selectedGpu.value = gpu
  gpuAssignVisible.value = true
}

const confirmDeleteGpu = async (gpu) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除GPU "${gpu.model}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    await assetsApi.deleteGpu(gpu.id)
    ElMessage.success('删除成功')
    handleRefresh()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || '删除失败')
    }
  }
}

const handleRefresh = () => {
  emit('refresh')
}
</script>

<style lang="scss" scoped>
.server-detail {
  .detail-section {
    margin-bottom: 24px;

    h4 {
      font-size: 14px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid #ebeef5;
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid #ebeef5;

      h4 {
        margin: 0;
        padding: 0;
        border: none;
      }
    }
  }

  .copyable {
    cursor: pointer;
    color: #409EFF;
    &:hover { text-decoration: underline; }
  }

  .text-muted { color: #c0c4cc; }

  .config-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;

    .config-item {
      background: #f5f7fa;
      padding: 12px;
      border-radius: 8px;

      .label {
        display: block;
        font-size: 12px;
        color: #909399;
        margin-bottom: 4px;
      }

      .value {
        font-size: 14px;
        font-weight: 500;
        color: #303133;
      }
    }
  }

  .ssh-command {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #1a1f2e;
    padding: 12px;
    border-radius: 8px;

    code {
      flex: 1;
      color: #67C23A;
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      word-break: break-all;
    }
  }

  .usage-list {
    .usage-item {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;

      .label {
        width: 40px;
        font-size: 12px;
        color: #909399;
      }

      .el-progress { flex: 1; }
    }
  }

  .container-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .container-item {
    background: #f5f7fa;
    border-radius: 8px;
    padding: 12px;

    .container-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }

    .container-name {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      font-weight: 500;
    }

    .container-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }

  .services-list {
    margin-top: 8px;
    padding-left: 24px;
    border-left: 2px solid #e4e7ed;
  }

  .service-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px dashed #ebeef5;

    &:last-child {
      border-bottom: none;
    }

    .service-info {
      display: flex;
      align-items: center;
      gap: 6px;

      .service-name {
        font-size: 13px;
      }

      .service-port {
        font-size: 12px;
        color: #909399;
        font-family: 'JetBrains Mono', monospace;
      }
    }

    .service-actions {
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }

  .empty-services {
    font-size: 12px;
    color: #909399;
    padding: 8px 0 0 24px;
  }

  .gpu-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .gpu-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 8px;

    .gpu-info {
      .gpu-model {
        font-size: 13px;
        font-weight: 500;
      }
      .gpu-memory {
        font-size: 12px;
        color: #909399;
        margin-left: 8px;
      }
    }

    .gpu-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
}
</style>
