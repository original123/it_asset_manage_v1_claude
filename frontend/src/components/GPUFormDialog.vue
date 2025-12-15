<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="gpu ? '编辑GPU' : '添加GPU'"
    width="500px"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="GPU型号" prop="model">
        <el-input v-model="form.model" placeholder="如: NVIDIA RTX 4090" />
      </el-form-item>

      <el-form-item label="所属服务器">
        <el-input :value="server?.name" disabled />
      </el-form-item>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="显存(GB)" prop="memory_gb">
            <el-input-number v-model="form.memory_gb" :min="1" :max="1024" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="索引">
            <el-input-number v-model="form.index" :min="0" :max="15" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="状态">
        <el-select v-model="form.status" style="width: 100%">
          <el-option label="空闲" value="free" />
          <el-option label="使用中" value="in_use" />
          <el-option label="错误" value="error" />
        </el-select>
      </el-form-item>

      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="2" placeholder="GPU描述" />
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
  server: Object,
  gpu: Object
})

const emit = defineEmits(['update:modelValue', 'success'])

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  model: '',
  memory_gb: 24,
  index: 0,
  status: 'free',
  description: ''
})

const rules = {
  model: [{ required: true, message: '请输入GPU型号', trigger: 'blur' }],
  memory_gb: [{ required: true, message: '请输入显存大小', trigger: 'blur' }]
}

watch(() => props.modelValue, (val) => {
  if (val && props.gpu) {
    Object.assign(form, { ...props.gpu })
  } else if (val) {
    Object.assign(form, {
      model: '',
      memory_gb: 24,
      index: 0,
      status: 'free',
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
        server_id: props.server.id
      }

      if (props.gpu) {
        await assetsApi.updateGpu(props.gpu.id, data)
        ElMessage.success('更新成功')
      } else {
        await assetsApi.createGpu(data)
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
