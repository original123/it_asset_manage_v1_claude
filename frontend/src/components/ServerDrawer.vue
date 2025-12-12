<template>
  <el-drawer
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="服务器详情"
    size="480px"
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
        <div class="detail-section" v-if="server.containers?.length">
          <h4>容器 ({{ server.containers.length }})</h4>
          <div class="container-list">
            <div
              v-for="container in server.containers"
              :key="container.id"
              class="container-item"
            >
              <div class="container-name">
                <el-icon><Box /></el-icon>
                {{ container.name }}
              </div>
              <el-tag :type="getStatusType(container.status)" size="small">
                {{ container.status }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- GPU列表 -->
        <div class="detail-section" v-if="server.gpus?.length">
          <h4>GPU ({{ server.gpus.length }})</h4>
          <div class="gpu-list">
            <div v-for="gpu in server.gpus" :key="gpu.id" class="gpu-item">
              <div class="gpu-info">
                <span class="gpu-model">{{ gpu.model }}</span>
                <span class="gpu-memory">{{ gpu.memory_gb }}GB</span>
              </div>
              <el-tag :type="gpu.status === 'free' ? 'success' : 'warning'" size="small">
                {{ gpu.status === 'free' ? '空闲' : gpu.assigned_user_name }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </template>
  </el-drawer>
</template>

<script setup>
import { DocumentCopy, Box } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

defineProps({
  modelValue: Boolean,
  server: Object
})

defineEmits(['update:modelValue', 'refresh'])

const copyText = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制')
  } catch {
    ElMessage.error('复制失败')
  }
}

const getStatusType = (status) => {
  const map = { online: 'success', running: 'success', offline: 'danger', stopped: 'danger' }
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

  .container-list, .gpu-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .container-item, .gpu-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 12px;
    background: #f5f7fa;
    border-radius: 8px;
  }

  .container-name {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
  }

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
}
</style>
