<template>
  <div class="overview-page">
    <h2 class="page-title">机房总览</h2>

    <div class="datacenter-grid" v-loading="loading">
      <div
        v-for="dc in datacenters"
        :key="dc.id"
        class="datacenter-card"
        @click="goToAssets(dc.id)"
      >
        <div class="card-header">
          <div class="dc-icon">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <div class="dc-info">
            <h3 class="dc-name">{{ dc.name }}</h3>
            <p class="dc-location">{{ dc.location || '未设置位置' }}</p>
          </div>
        </div>

        <div class="card-stats">
          <div class="stat-item">
            <span class="stat-value">{{ dc.server_count }}</span>
            <span class="stat-label">服务器</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ dc.container_count }}</span>
            <span class="stat-label">容器</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ dc.service_count }}</span>
            <span class="stat-label">服务</span>
          </div>
          <div class="stat-item highlight">
            <span class="stat-value">{{ dc.gpu_server_count }}</span>
            <span class="stat-label">GPU机</span>
          </div>
        </div>

        <div class="card-footer">
          <div class="status-summary">
            <span class="status online">
              <span class="dot"></span>
              {{ dc.status_stats?.online || 0 }} 在线
            </span>
            <span class="status offline">
              <span class="dot"></span>
              {{ dc.status_stats?.offline || 0 }} 离线
            </span>
          </div>
          <el-button text type="primary" class="view-btn">
            查看详情 →
          </el-button>
        </div>
      </div>

      <!-- 添加机房卡片 -->
      <div class="datacenter-card add-card" @click="showAddDialog" v-if="authStore.isAdmin">
        <el-icon class="add-icon"><Plus /></el-icon>
        <span>添加机房</span>
      </div>
    </div>

    <!-- 添加/编辑机房弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingDc ? '编辑机房' : '添加机房'"
      width="480px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="机房名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入机房名称" />
        </el-form-item>
        <el-form-item label="位置" prop="location">
          <el-input v-model="form.location" placeholder="请输入机房位置" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="机房描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { OfficeBuilding, Plus } from '@element-plus/icons-vue'
import { assetsApi } from '@/api/assets'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const datacenters = ref([])
const dialogVisible = ref(false)
const submitting = ref(false)
const editingDc = ref(null)
const formRef = ref(null)

const form = reactive({
  name: '',
  location: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入机房名称', trigger: 'blur' }]
}

onMounted(() => {
  loadData()
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await assetsApi.getDatacentersOverview()
    if (res.code === 0) {
      datacenters.value = res.data
    }
  } finally {
    loading.value = false
  }
}

const goToAssets = (dcId) => {
  router.push({ path: '/assets', query: { datacenter_id: dcId } })
}

const showAddDialog = () => {
  editingDc.value = null
  Object.assign(form, { name: '', location: '', description: '' })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (editingDc.value) {
        await assetsApi.updateDatacenter(editingDc.value.id, form)
        ElMessage.success('更新成功')
      } else {
        await assetsApi.createDatacenter(form)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadData()
    } catch (e) {
      ElMessage.error(e.message || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}
</script>

<style lang="scss" scoped>
.overview-page {
  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 24px;
  }
}

.datacenter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.datacenter-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  }

  &.add-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 220px;
    border: 2px dashed #dcdfe6;
    background: #fafafa;

    .add-icon {
      font-size: 48px;
      color: #c0c4cc;
      margin-bottom: 12px;
    }

    span {
      color: #909399;
      font-size: 14px;
    }

    &:hover {
      border-color: #409EFF;
      background: #ecf5ff;

      .add-icon, span {
        color: #409EFF;
      }
    }
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;

    .dc-icon {
      width: 48px;
      height: 48px;
      background: linear-gradient(135deg, #409EFF, #66b1ff);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 24px;
    }

    .dc-info {
      .dc-name {
        font-size: 18px;
        font-weight: 600;
        color: #303133;
        margin: 0 0 4px;
      }

      .dc-location {
        font-size: 13px;
        color: #909399;
        margin: 0;
      }
    }
  }

  .card-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    padding: 16px 0;
    border-top: 1px solid #f0f0f0;
    border-bottom: 1px solid #f0f0f0;

    .stat-item {
      text-align: center;

      .stat-value {
        display: block;
        font-size: 24px;
        font-weight: 600;
        color: #303133;
      }

      .stat-label {
        font-size: 12px;
        color: #909399;
      }

      &.highlight .stat-value {
        color: #409EFF;
      }
    }
  }

  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 16px;

    .status-summary {
      display: flex;
      gap: 16px;

      .status {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        color: #606266;

        .dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }

        &.online .dot { background: #67C23A; }
        &.offline .dot { background: #F56C6C; }
      }
    }

    .view-btn {
      padding: 0;
    }
  }
}
</style>
