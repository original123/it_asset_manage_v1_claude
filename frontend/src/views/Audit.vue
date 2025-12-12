<template>
  <div class="audit-page">
    <div class="page-header">
      <h2 class="page-title">审计日志</h2>
      <el-button @click="handleExport">
        <el-icon><Download /></el-icon>
        导出日志
      </el-button>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-bar">
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        @change="loadData"
      />

      <el-select v-model="filters.action" placeholder="操作类型" clearable @change="loadData">
        <el-option label="创建" value="create" />
        <el-option label="更新" value="update" />
        <el-option label="删除" value="delete" />
      </el-select>

      <el-select v-model="filters.resource_type" placeholder="资源类型" clearable @change="loadData">
        <el-option label="服务器" value="server" />
        <el-option label="容器" value="container" />
        <el-option label="服务" value="service" />
        <el-option label="GPU" value="gpu" />
        <el-option label="机房" value="datacenter" />
        <el-option label="用户" value="user" />
      </el-select>

      <el-input
        v-model="filters.keyword"
        placeholder="搜索资源名称/用户名"
        clearable
        style="width: 200px"
        @keyup.enter="loadData"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- 日志表格 -->
    <div class="log-table-wrapper">
      <el-table :data="logs" v-loading="loading" stripe>
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column prop="username" label="操作用户" width="120" />

        <el-table-column label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action)" size="small">
              {{ getActionText(row.action) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="资源类型" width="100">
          <template #default="{ row }">
            {{ getResourceTypeText(row.resource_type) }}
          </template>
        </el-table-column>

        <el-table-column prop="resource_name" label="资源名称" min-width="150" />

        <el-table-column prop="ip_address" label="IP地址" width="140" />

        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="showDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @change="loadData"
        />
      </div>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="日志详情" width="600px">
      <el-descriptions :column="2" border v-if="selectedLog">
        <el-descriptions-item label="时间">{{ formatTime(selectedLog.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="用户">{{ selectedLog.username }}</el-descriptions-item>
        <el-descriptions-item label="操作">{{ getActionText(selectedLog.action) }}</el-descriptions-item>
        <el-descriptions-item label="资源类型">{{ getResourceTypeText(selectedLog.resource_type) }}</el-descriptions-item>
        <el-descriptions-item label="资源名称" :span="2">{{ selectedLog.resource_name }}</el-descriptions-item>
        <el-descriptions-item label="IP地址">{{ selectedLog.ip_address }}</el-descriptions-item>
        <el-descriptions-item label="资源ID">{{ selectedLog.resource_id }}</el-descriptions-item>
      </el-descriptions>

      <div v-if="selectedLog?.changes" class="changes-section">
        <h4>变更内容</h4>
        <pre class="changes-content">{{ JSON.stringify(selectedLog.changes, null, 2) }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { Download, Search } from '@element-plus/icons-vue'
import { auditApi } from '@/api/admin'

const loading = ref(false)
const logs = ref([])
const detailVisible = ref(false)
const selectedLog = ref(null)

const dateRange = ref([])
const filters = reactive({
  action: '',
  resource_type: '',
  keyword: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

onMounted(() => {
  loadData()
})

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...filters
    }

    if (dateRange.value?.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const res = await auditApi.getLogs(params)
    if (res.code === 0) {
      logs.value = res.data
      Object.assign(pagination, res.pagination)
    }
  } finally {
    loading.value = false
  }
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

const getActionType = (action) => {
  const map = { create: 'success', update: 'warning', delete: 'danger' }
  return map[action] || 'info'
}

const getActionText = (action) => {
  const map = { create: '创建', update: '更新', delete: '删除' }
  return map[action] || action
}

const getResourceTypeText = (type) => {
  const map = {
    server: '服务器',
    container: '容器',
    service: '服务',
    gpu: 'GPU',
    datacenter: '机房',
    user: '用户'
  }
  return map[type] || type
}

const showDetail = async (log) => {
  try {
    const res = await auditApi.getLogDetail(log.id)
    if (res.code === 0) {
      selectedLog.value = res.data
      detailVisible.value = true
    }
  } catch (e) {
    console.error(e)
  }
}

const handleExport = () => {
  const params = new URLSearchParams()
  if (dateRange.value?.length === 2) {
    params.append('start_date', dateRange.value[0])
    params.append('end_date', dateRange.value[1])
  }
  if (filters.action) params.append('action', filters.action)
  if (filters.resource_type) params.append('resource_type', filters.resource_type)

  window.open(`/api/audit-logs/export?${params.toString()}`)
}
</script>

<style lang="scss" scoped>
.audit-page {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .page-title {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
      margin: 0;
    }
  }

  .filter-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    padding: 16px 20px;
    background: #fff;
    border-radius: 12px;
  }

  .log-table-wrapper {
    background: #fff;
    border-radius: 12px;
    padding: 16px;

    .pagination-wrapper {
      margin-top: 16px;
      display: flex;
      justify-content: flex-end;
    }
  }

  .changes-section {
    margin-top: 20px;

    h4 {
      margin: 0 0 12px;
      font-size: 14px;
      color: #606266;
    }

    .changes-content {
      background: #f5f7fa;
      padding: 12px;
      border-radius: 8px;
      font-size: 12px;
      overflow: auto;
      max-height: 300px;
    }
  }
}
</style>
