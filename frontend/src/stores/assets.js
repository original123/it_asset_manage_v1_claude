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
  const expandedRowKeys = ref([]) // 手动展开的行ID列表

  // LocalStorage key
  const STORAGE_KEY = 'it_asset_expand_state'

  // 保存展开状态到localStorage
  function saveExpandState() {
    try {
      const state = {
        expandLevel: expandLevel.value,
        expandedRowKeys: expandedRowKeys.value
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    } catch (e) {
      console.warn('保存展开状态失败:', e)
    }
  }

  // 从localStorage恢复展开状态
  function loadExpandState() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const state = JSON.parse(saved)
        if (state.expandLevel) {
          expandLevel.value = state.expandLevel
        }
        if (state.expandedRowKeys) {
          expandedRowKeys.value = state.expandedRowKeys
        }
      }
    } catch (e) {
      console.warn('恢复展开状态失败:', e)
    }
  }

  // 添加/移除手动展开的行
  function toggleExpandedRow(rowKey) {
    const index = expandedRowKeys.value.indexOf(rowKey)
    if (index > -1) {
      expandedRowKeys.value.splice(index, 1)
    } else {
      expandedRowKeys.value.push(rowKey)
    }
    saveExpandState()
  }

  // 设置展开层级并保存
  function setExpandLevel(level) {
    expandLevel.value = level
    saveExpandState()
  }

  // 配置数据
  const datacenters = ref([])
  const environments = ref([])

  // 当前选中
  const selectedServer = ref(null)
  const selectedContainer = ref(null)

  // 批量选择状态
  const selectedRows = ref([])
  const selectedIds = ref(new Set())

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

  // 批量选择操作
  function setSelection(rows) {
    selectedRows.value = rows
    selectedIds.value = new Set(rows.map(r => r.id))
  }

  function clearSelection() {
    selectedRows.value = []
    selectedIds.value = new Set()
  }

  function toggleSelection(row) {
    const index = selectedRows.value.findIndex(r => r.id === row.id)
    if (index > -1) {
      selectedRows.value.splice(index, 1)
      selectedIds.value.delete(row.id)
    } else {
      selectedRows.value.push(row)
      selectedIds.value.add(row.id)
    }
  }

  return {
    filters,
    servers,
    loading,
    expandLevel,
    expandedRowKeys,
    datacenters,
    environments,
    selectedServer,
    selectedContainer,
    selectedRows,
    selectedIds,
    drawerVisible,
    drawerType,
    loadServersTree,
    loadDatacenters,
    loadEnvironments,
    setFilter,
    clearFilters,
    openDrawer,
    closeDrawer,
    setSelection,
    clearSelection,
    toggleSelection,
    saveExpandState,
    loadExpandState,
    toggleExpandedRow,
    setExpandLevel
  }
})
