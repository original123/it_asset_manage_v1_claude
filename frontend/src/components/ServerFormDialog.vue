<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="server ? '编辑服务器' : '添加服务器'"
    width="600px"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="服务器名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入服务器名称" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="状态" prop="status">
            <el-select v-model="form.status" style="width: 100%">
              <el-option label="在线" value="online" />
              <el-option label="离线" value="offline" />
              <el-option label="维护中" value="maintenance" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="机房" prop="datacenter_id">
            <el-select v-model="form.datacenter_id" placeholder="选择机房" style="width: 100%">
              <el-option
                v-for="dc in datacenters"
                :key="dc.id"
                :label="dc.name"
                :value="dc.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="环境" prop="environment_id">
            <el-select v-model="form.environment_id" placeholder="选择环境" style="width: 100%">
              <el-option
                v-for="env in environments"
                :key="env.id"
                :label="env.name"
                :value="env.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="内网IP" prop="internal_ip">
            <el-input v-model="form.internal_ip" placeholder="192.168.1.100" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="外网IP">
            <el-input v-model="form.external_ip" placeholder="可选" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">硬件配置</el-divider>

      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="CPU核数">
            <el-input-number v-model="form.cpu_cores" :min="1" :max="256" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="内存(GB)">
            <el-input-number v-model="form.memory_gb" :min="1" :max="2048" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="磁盘(GB)">
            <el-input-number v-model="form.disk_gb" :min="1" :max="102400" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="操作系统">
        <el-input v-model="form.os_type" placeholder="CentOS 7.9" />
      </el-form-item>

      <el-divider content-position="left">SSH配置</el-divider>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="SSH端口">
            <el-input-number v-model="form.ssh_port" :min="1" :max="65535" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="SSH用户">
            <el-input v-model="form.ssh_user" placeholder="root" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="负责人">
        <el-input v-model="form.responsible_person" placeholder="负责人姓名" />
      </el-form-item>

      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="2" placeholder="服务器描述" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="loading">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { assetsApi } from '@/api/assets'

const props = defineProps({
  modelValue: Boolean,
  server: Object
})

const emit = defineEmits(['update:modelValue', 'success'])

const formRef = ref(null)
const loading = ref(false)
const datacenters = ref([])
const environments = ref([])

const form = reactive({
  name: '',
  datacenter_id: null,
  environment_id: null,
  internal_ip: '',
  external_ip: '',
  cpu_cores: null,
  memory_gb: null,
  disk_gb: null,
  os_type: '',
  ssh_port: 22,
  ssh_user: 'root',
  responsible_person: '',
  description: '',
  status: 'online'
})

const rules = {
  name: [{ required: true, message: '请输入服务器名称', trigger: 'blur' }],
  datacenter_id: [{ required: true, message: '请选择机房', trigger: 'change' }],
  environment_id: [{ required: true, message: '请选择环境', trigger: 'change' }],
  internal_ip: [{ required: true, message: '请输入内网IP', trigger: 'blur' }]
}

onMounted(async () => {
  const [dcRes, envRes] = await Promise.all([
    assetsApi.getDatacenters(),
    assetsApi.getEnvironments()
  ])
  if (dcRes.code === 0) datacenters.value = dcRes.data
  if (envRes.code === 0) environments.value = envRes.data
})

watch(() => props.modelValue, (val) => {
  if (val && props.server) {
    Object.assign(form, props.server)
  } else if (val) {
    Object.assign(form, {
      name: '', datacenter_id: null, environment_id: null,
      internal_ip: '', external_ip: '', cpu_cores: null,
      memory_gb: null, disk_gb: null, os_type: '',
      ssh_port: 22, ssh_user: 'root', responsible_person: '',
      description: '', status: 'online'
    })
  }
})

const handleSubmit = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      if (props.server) {
        await assetsApi.updateServer(props.server.id, form)
        ElMessage.success('更新成功')
      } else {
        await assetsApi.createServer(form)
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
