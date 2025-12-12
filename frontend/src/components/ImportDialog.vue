<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="导入数据"
    width="500px"
  >
    <el-upload
      ref="uploadRef"
      drag
      :auto-upload="false"
      :limit="1"
      accept=".xlsx,.xls"
      :on-change="handleFileChange"
      :on-exceed="handleExceed"
    >
      <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
      <div class="el-upload__text">
        拖拽文件到此处，或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          只能上传 xlsx/xls 文件，请先
          <el-link type="primary" @click="downloadTemplate">下载导入模板</el-link>
        </div>
      </template>
    </el-upload>

    <el-checkbox v-model="overwrite" style="margin-top: 16px">
      覆盖已存在的数据
    </el-checkbox>

    <div v-if="result" class="import-result">
      <el-alert
        :title="result.success ? '导入完成' : '导入失败'"
        :type="result.success ? 'success' : 'error'"
        show-icon
      >
        <template #default>
          <p v-if="result.servers">
            服务器: 创建 {{ result.servers.created }} 条, 更新 {{ result.servers.updated }} 条
            <span v-if="result.servers.errors?.length">, 错误 {{ result.servers.errors.length }} 条</span>
          </p>
          <p v-if="result.containers">
            容器: 创建 {{ result.containers.created }} 条, 更新 {{ result.containers.updated }} 条
            <span v-if="result.containers.errors?.length">, 错误 {{ result.containers.errors.length }} 条</span>
          </p>
        </template>
      </el-alert>
    </div>

    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">关闭</el-button>
      <el-button type="primary" @click="handleImport" :loading="loading" :disabled="!file">
        开始导入
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { importExportApi } from '@/api/admin'

defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue', 'success'])

const uploadRef = ref(null)
const file = ref(null)
const loading = ref(false)
const overwrite = ref(false)
const result = ref(null)

const handleFileChange = (uploadFile) => {
  file.value = uploadFile.raw
  result.value = null
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const downloadTemplate = () => {
  window.open('/api/import-export/template')
}

const handleImport = async () => {
  if (!file.value) return

  loading.value = true
  result.value = null

  try {
    const res = await importExportApi.importData(file.value, overwrite.value)
    if (res.code === 0) {
      result.value = { success: true, ...res.data }
      emit('success')
    }
  } catch (e) {
    result.value = { success: false, message: e.message }
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.import-result {
  margin-top: 16px;
  p { margin: 4px 0; font-size: 13px; }
}
</style>
