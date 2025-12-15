<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="service ? '编辑服务' : '添加服务'"
    width="550px"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="服务名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入服务名称" />
      </el-form-item>

      <el-form-item label="所属容器">
        <el-input :value="container?.name" disabled />
      </el-form-item>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="服务类型">
            <el-select v-model="form.service_type" placeholder="选择类型" style="width: 100%">
              <el-option label="Web服务" value="web" />
              <el-option label="API服务" value="api" />
              <el-option label="数据库" value="database" />
              <el-option label="缓存服务" value="cache" />
              <el-option label="消息队列" value="queue" />
              <el-option label="代理服务" value="proxy" />
              <el-option label="监控服务" value="monitor" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="端口">
            <el-input-number v-model="form.port" :min="1" :max="65535" style="width: 100%" placeholder="服务端口" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="版本">
            <el-input v-model="form.version" placeholder="如: v1.0.0" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="状态">
            <el-select v-model="form.status" style="width: 100%">
              <el-option label="健康" value="healthy" />
              <el-option label="异常" value="unhealthy" />
              <el-option label="已停止" value="stopped" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="健康检查URL">
        <el-input v-model="form.health_check_url" placeholder="如: http://localhost:8080/health" />
      </el-form-item>

      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="2" placeholder="服务描述" />
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
import { assetsApi } from '@/api/assets'

const props = defineProps({
  modelValue: Boolean,
  container: Object,
  service: Object
})

const emit = defineEmits(['update:modelValue', 'success'])

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  name: '',
  service_type: 'web',
  port: null,
  version: '',
  status: 'healthy',
  health_check_url: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入服务名称', trigger: 'blur' }]
}

watch(() => props.modelValue, (val) => {
  if (val && props.service) {
    Object.assign(form, { ...props.service })
  } else if (val) {
    Object.assign(form, {
      name: '',
      service_type: 'web',
      port: null,
      version: '',
      status: 'healthy',
      health_check_url: '',
      description: ''
    })
  }
})

const handleSubmit = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const data = {
        ...form,
        container_id: props.container.id
      }

      if (props.service) {
        await assetsApi.updateService(props.service.id, data)
        ElMessage.success('更新成功')
      } else {
        await assetsApi.createService(data)
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
