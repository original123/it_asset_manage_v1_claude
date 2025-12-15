<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="分配GPU"
    width="450px"
  >
    <div class="gpu-info" v-if="gpu">
      <el-descriptions :column="1" border size="small">
        <el-descriptions-item label="GPU型号">{{ gpu.model }}</el-descriptions-item>
        <el-descriptions-item label="显存">{{ gpu.memory_gb }} GB</el-descriptions-item>
        <el-descriptions-item label="当前状态">
          <el-tag :type="gpu.status === 'free' ? 'success' : 'warning'" size="small">
            {{ gpu.status === 'free' ? '空闲' : gpu.assigned_user_name || '使用中' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <el-form ref="formRef" :model="form" label-width="80px" style="margin-top: 20px">
      <el-form-item label="分配给" prop="user_id">
        <el-select
          v-model="form.user_id"
          placeholder="选择用户"
          style="width: 100%"
          filterable
        >
          <el-option
            v-for="user in userOptions"
            :key="user.id"
            :label="user.display_name"
            :value="user.id"
          >
            <span>{{ user.display_name }}</span>
            <span style="color: #909399; margin-left: 8px">@{{ user.username }}</span>
          </el-option>
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button
        v-if="gpu?.status !== 'free'"
        type="warning"
        @click="handleRelease"
        :loading="loading"
      >
        释放GPU
      </el-button>
      <el-button type="primary" @click="handleAssign" :loading="loading" :disabled="!form.user_id">
        分配
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { assetsApi } from '@/api/assets'

const props = defineProps({
  modelValue: Boolean,
  gpu: Object
})

const emit = defineEmits(['update:modelValue', 'success'])

const loading = ref(false)
const userOptions = ref([])

const form = reactive({
  user_id: null
})

onMounted(async () => {
  const res = await assetsApi.getUserOptions()
  if (res.code === 0) {
    userOptions.value = res.data
  }
})

watch(() => props.modelValue, (val) => {
  if (val) {
    form.user_id = props.gpu?.assigned_to || null
  }
})

const handleAssign = async () => {
  if (!form.user_id) return

  loading.value = true
  try {
    await assetsApi.assignGpu(props.gpu.id, form.user_id)
    ElMessage.success('分配成功')
    emit('update:modelValue', false)
    emit('success')
  } catch (e) {
    ElMessage.error(e.message || '分配失败')
  } finally {
    loading.value = false
  }
}

const handleRelease = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要释放此GPU吗？当前使用者: ${props.gpu.assigned_user_name}`,
      '确认释放',
      { type: 'warning' }
    )

    loading.value = true
    await assetsApi.releaseGpu(props.gpu.id)
    ElMessage.success('释放成功')
    emit('update:modelValue', false)
    emit('success')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || '释放失败')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.gpu-info {
  margin-bottom: 16px;
}
</style>
