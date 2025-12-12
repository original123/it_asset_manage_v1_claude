import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { assetsApi } from '@/api/assets'

export const useAssetsStore = defineStore('assets', () => {
  // 筛选状态
  const filters = ref({
    datacenter_id: null,
    environment_id: null,
    status: null,
    keyword: ''
  })

  // 数据
  const servers = ref([])
  const loading = ref(false)
  const expandLevel = ref(1) // 1=服务器, 2=容器, 3=服务

  // 配置数据
  const datacenters = ref([])
  const environments = ref([])

  // 当前选中
  const selectedServer = ref(null)
  const selectedContainer = ref(null)

  // 抽屉状态
  const drawerVisible = ref(false)
  const drawerType = ref('') // server, container, service, gpu

  async function loadServersTree() {
    loading.value = true
    try {
      const res = await assetsApi.getServersTree({
        datacenter_id: filters.value.datacenter_id,
        environment_id: filters.value.environment_id,
        expand_level: expandLevel.value
      })
      if (res.code === 0) {
        servers.value = res.data
      }
    } finally {
      loading.value = false
    }
  }

  async function loadDatacenters() {
    const res = await assetsApi.getDatacenters()
    if (res.code === 0) {
      datacenters.value = res.data
    }
  }

  async function loadEnvironments() {
    const res = await assetsApi.getEnvironments()
    if (res.code === 0) {
      environments.value = res.data
    }
  }

  function setFilter(key, value) {
    filters.value[key] = value
  }

  function clearFilters() {
    filters.value = {
      datacenter_id: null,
      environment_id: null,
      status: null,
      keyword: ''
    }
  }

  function openDrawer(type, data) {
    drawerType.value = type
    if (type === 'server') {
      selectedServer.value = data
    } else if (type === 'container') {
      selectedContainer.value = data
    }
    drawerVisible.value = true
  }

  function closeDrawer() {
    drawerVisible.value = false
    drawerType.value = ''
  }

  return {
    filters,
    servers,
    loading,
    expandLevel,
    datacenters,
    environments,
    selectedServer,
    selectedContainer,
    drawerVisible,
    drawerType,
    loadServersTree,
    loadDatacenters,
    loadEnvironments,
    setFilter,
    clearFilters,
    openDrawer,
    closeDrawer
  }
})
