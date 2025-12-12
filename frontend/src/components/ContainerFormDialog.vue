<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="container ? '编辑容器' : '添加容器'"
    width="650px"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="容器名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入容器名称" />
      </el-form-item>

      <el-form-item label="所属服务器">
        <el-input :value="server?.name" disabled />
      </el-form-item>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="镜像">
            <el-input v-model="form.image" placeholder="nginx:latest" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="状态">
            <el-select v-model="form.status" style="width: 100%">
              <el-option label="运行中" value="running" />
              <el-option label="已停止" value="stopped" />
              <el-option label="错误" value="error" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="CPU限制">
            <el-input-number v-model="form.cpu_limit" :min="0.1" :max="64" :precision="1" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="内存限制(MB)">
            <el-input-number v-model="form.memory_limit_mb" :min="64" :max="131072" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 端口映射 -->
      <el-divider content-position="left">端口映射</el-divider>

      <div class="port-mappings">
        <div v-for="(pm, index) in form.port_mappings" :key="index" class="port-mapping-item">
          <el-row :gutter="8" align="middle">
            <el-col :span="4">
              <el-input v-model.number="pm.container_port" placeholder="容器端口" size="small">
                <template #prepend>容器</template>
              </el-input>
            </el-col>
            <el-col :span="1" class="arrow">→</el-col>
            <el-col :span="6">
              <el-input v-model.number="pm.internal_port" placeholder="内网端口" size="small">
                <template #prepend>内网</template>
              </el-input>
            </el-col>
            <el-col :span="1" class="arrow">→</el-col>
            <el-col :span="6">
              <el-input v-model.number="pm.external_port" placeholder="外网端口(可选)" size="small">
                <template #prepend>外网</template>
              </el-input>
            </el-col>
            <el-col :span="3">
              <el-select v-model="pm.protocol" size="small">
                <el-option label="TCP" value="tcp" />
                <el-option label="UDP" value="udp" />
              </el-select>
            </el-col>
            <el-col :span="2">
              <el-button type="danger" size="small" @click="removePortMapping(index)" :icon="Delete" circle />
            </el-col>
          </el-row>
          <el-input v-model="pm.description" placeholder="用途说明" size="small" style="margin-top: 8px" />
        </div>

        <el-button type="primary" plain size="small" @click="addPortMapping" :icon="Plus">
          添加端口映射
        </el-button>
      </div>

      <el-form-item label="描述" style="margin-top: 16px">
        <el-input v-model="form.description" type="textarea" :rows="2" placeholder="容器描述" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="loading">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { assetsApi } from '@/api/assets'

const props = defineProps({
  modelValue: Boolean,
  server: Object,
  container: Object
})

const emit = defineEmits(['update:modelValue', 'success'])

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  name: '',
  image: '',
  status: 'running',
  cpu_limit: null,
  memory_limit_mb: null,
  description: '',
  port_mappings: []
})

const rules = {
  name: [{ required: true, message: '请输入容器名称', trigger: 'blur' }]
}

watch(() => props.modelValue, (val) => {
  if (val && props.container) {
    Object.assign(form, {
      ...props.container,
      port_mappings: props.container.port_mappings?.map(pm => ({ ...pm })) || []
    })
  } else if (val) {
    Object.assign(form, {
      name: '', image: '', status: 'running',
      cpu_limit: null, memory_limit_mb: null,
      description: '', port_mappings: []
    })
  }
})

const addPortMapping = () => {
  form.port_mappings.push({
    container_port: null,
    internal_port: null,
    external_port: null,
    protocol: 'tcp',
    description: ''
  })
}

const removePortMapping = (index) => {
  form.port_mappings.splice(index, 1)
}

const handleSubmit = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const data = {
        ...form,
        server_id: props.server.id,
        port_mappings: form.port_mappings.filter(pm => pm.container_port && pm.internal_port)
      }

      if (props.container) {
        await assetsApi.updateContainer(props.container.id, data)
        ElMessage.success('更新成功')
      } else {
        await assetsApi.createContainer(data)
        ElMessage.success('创建成功')
      }
      emit('update:modelValue', false)
      emit('success')
    } catch (e) {
      ElMessage.error(e.message || '操作失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style lang="scss" scoped>
.port-mappings {
  .port-mapping-item {
    padding: 12px;
    background: #f5f7fa;
    border-radius: 8px;
    margin-bottom: 12px;
  }

  .arrow {
    text-align: center;
    color: #909399;
    font-size: 16px;
  }
}
</style>
