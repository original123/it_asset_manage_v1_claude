import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { assetsApi } from '@/api/assets'

export const useExplorerStore = defineStore('explorer', () => {
  // ========== 导航状态 ==========
  // 当前路径：['env-prod', 'dc-shanghai', 'server-001']
  const currentPath = ref([])
  // 展开的节点ID列表
  const expandedNodes = ref([])
  // 分组方式：environment-first | datacenter-first | type | flat
  const groupingMode = ref('environment-first')

  // ========== 选择状态 ==========
  // 选中项的ID和类型 { id, type }
  const selectedItems = ref([])
  // 最后选中的项
  const lastSelected = ref(null)

  // ========== 视图状态 ==========
  // 视图模式：grid | list
  const viewMode = ref('grid')
  // 排序字段
  const sortBy = ref('name')
  // 排序方向
  const sortOrder = ref('asc')

  // ========== 数据 ==========
  // 导航树数据
  const navigationTree = ref([])
  // 当前内容区数据
  const currentContent = ref({
    containers: [],
    gpus: [],
    services: []
  })
  // 当前选中的节点信息
  const currentNode = ref(null)
  // 加载状态
  const loading = ref(false)
  const treeLoading = ref(false)

  // ========== 快捷访问 ==========
  const quickAccess = ref({
    offlineServers: [],
    highLoadServers: [],
    recentAccess: []
  })

  // ========== 用户偏好 ==========
  const preferences = ref({
    panelWidth: 260,
    showDetailBar: true
  })

  // ========== 配置数据 ==========
  const datacenters = ref([])
  const environments = ref([])

  // LocalStorage keys
  const STORAGE_KEY_PREFS = 'explorer_preferences'
  const STORAGE_KEY_STATE = 'explorer_state'

  // ========== 计算属性 ==========

  // 面包屑路径
  const breadcrumbPath = computed(() => {
    const result = []
    let current = navigationTree.value

    for (const nodeId of currentPath.value) {
      const node = findNodeById(current, nodeId)
      if (node) {
        result.push({
          id: node.id,
          name: node.name,
          type: node.type,
          icon: getNodeIcon(node.type)
        })
        current = node.children || []
      }
    }
    return result
  })

  // 是否有选中项
  const hasSelection = computed(() => selectedItems.value.length > 0)

  // 选中项数量
  const selectionCount = computed(() => selectedItems.value.length)

  // 当前内容统计
  const contentStats = computed(() => {
    return {
      containers: currentContent.value.containers?.length || 0,
      gpus: currentContent.value.gpus?.length || 0,
      services: currentContent.value.services?.length || 0
    }
  })

  // ========== 方法 ==========

  // 辅助函数：根据ID查找节点
  function findNodeById(nodes, id) {
    for (const node of nodes) {
      if (node.id === id) return node
      if (node.children) {
        const found = findNodeById(node.children, id)
        if (found) return found
      }
    }
    return null
  }

  // 辅助函数：获取节点图标
  function getNodeIcon(type) {
    const icons = {
      environment: 'Folder',
      datacenter: 'Location',
      server: 'Monitor',
      container: 'Box',
      service: 'Setting',
      gpu: 'Cpu'
    }
    return icons[type] || 'Document'
  }

  // 加载导航树数据
  async function loadNavigationTree() {
    treeLoading.value = true
    try {
      // 加载环境和机房配置
      const [envRes, dcRes] = await Promise.all([
        assetsApi.getEnvironments(),
        assetsApi.getDatacenters()
      ])

      if (envRes.code === 0) environments.value = envRes.data
      console.log('Loaded environments:', environments.value)
      if (dcRes.code === 0) datacenters.value = dcRes.data
      console.log('Loaded datacenters:', datacenters.value)

      // 加载服务器树
      const serversRes = await assetsApi.getServersTree({ expand_level: 3 })
      console.log('Loaded servers tree raw:', serversRes.data)

      if (serversRes.code === 0) {
        // 根据分组方式构建导航树
        navigationTree.value = buildNavigationTree(serversRes.data)
        console.log('Built navigation tree:', navigationTree.value)
      } else {
        console.error('Failed to load servers tree:', serversRes)
      }
    } catch (error) {
      console.error('Error in loadNavigationTree:', error)
    } finally {
      treeLoading.value = false
    }
  }

  // 构建导航树
  function buildNavigationTree(servers) {
    if (!servers) {
      console.warn('buildNavigationTree called with no servers.')
      return []
    }
    if (groupingMode.value === 'flat') {
      // 扁平列表：直接显示所有服务器
      return servers.map(s => ({
        id: `server-${s.id}`,
        nodeId: s.id,
        name: s.name,
        type: 'server',
        status: s.status,
        data: s,
        children: []
      }))
    }

    if (groupingMode.value === 'environment-first') {
      // 按环境 → 机房 → 服务器分组
      return buildEnvFirstTree(servers)
    }

    if (groupingMode.value === 'datacenter-first') {
      // 按机房 → 环境 → 服务器分组
      return buildDcFirstTree(servers)
    }

    // 默认返回扁平列表
    return servers.map(s => ({
      id: `server-${s.id}`,
      nodeId: s.id,
      name: s.name,
      type: 'server',
      status: s.status,
      data: s,
      children: []
    }))
  }

  // 按环境优先构建树
  function buildEnvFirstTree(servers) {
    const envMap = new Map()

    for (const env of environments.value) {
      envMap.set(env.id, {
        id: `env-${env.id}`,
        nodeId: env.id,
        name: env.name,
        type: 'environment',
        color: env.color,
        children: new Map() // 机房Map
      })
    }

    // 按环境和机房分组服务器
    for (const server of servers) {
      const envId = server.environment_id
      const dcId = server.datacenter_id

      if (!envMap.has(envId)) continue

      const envNode = envMap.get(envId)

      if (!envNode.children.has(dcId)) {
        const dc = datacenters.value.find(d => d.id === dcId)
        envNode.children.set(dcId, {
          id: `dc-${dcId}`,
          nodeId: dcId,
          name: dc?.name || '未知机房',
          type: 'datacenter',
          children: []
        })
      }

      envNode.children.get(dcId).children.push({
        id: `server-${server.id}`,
        nodeId: server.id,
        name: server.name,
        type: 'server',
        status: server.status,
        data: server,
        children: []
      })
    }

    // 转换为数组并计算数量
    return Array.from(envMap.values())
      .map(env => ({
        ...env,
        children: Array.from(env.children.values()),
        count: Array.from(env.children.values()).reduce(
          (sum, dc) => sum + dc.children.length, 0
        )
      }))
      .filter(env => env.count > 0)
  }

  // 按机房优先构建树
  function buildDcFirstTree(servers) {
    const dcMap = new Map()

    for (const dc of datacenters.value) {
      dcMap.set(dc.id, {
        id: `dc-${dc.id}`,
        nodeId: dc.id,
        name: dc.name,
        type: 'datacenter',
        children: new Map() // 环境Map
      })
    }

    // 按机房和环境分组服务器
    for (const server of servers) {
      const dcId = server.datacenter_id
      const envId = server.environment_id

      if (!dcMap.has(dcId)) continue

      const dcNode = dcMap.get(dcId)

      if (!dcNode.children.has(envId)) {
        const env = environments.value.find(e => e.id === envId)
        dcNode.children.set(envId, {
          id: `env-${envId}`,
          nodeId: envId,
          name: env?.name || '未知环境',
          type: 'environment',
          color: env?.color,
          children: []
        })
      }

      dcNode.children.get(envId).children.push({
        id: `server-${server.id}`,
        nodeId: server.id,
        name: server.name,
        type: 'server',
        status: server.status,
        data: server,
        children: []
      })
    }

    // 转换为数组并计算数量
    return Array.from(dcMap.values())
      .map(dc => ({
        ...dc,
        children: Array.from(dc.children.values()),
        count: Array.from(dc.children.values()).reduce(
          (sum, env) => sum + env.children.length, 0
        )
      }))
      .filter(dc => dc.count > 0)
  }

  // 导航到指定节点
  async function navigateTo(nodeId, nodeType) {
    // 更新当前路径
    if (nodeType === 'environment' || nodeType === 'datacenter') {
      // 根据节点类型确定路径深度
      const nodeIndex = currentPath.value.indexOf(nodeId)
      if (nodeIndex >= 0) {
        // 回退到已存在的节点
        currentPath.value = currentPath.value.slice(0, nodeIndex + 1)
      } else {
        // 添加新节点
        currentPath.value.push(nodeId)
      }
      currentNode.value = findNodeById(navigationTree.value, nodeId)
      // 加载该层级下的内容
      await loadContentForPath()
    } else if (nodeType === 'server') {
      // 导航到服务器详情
      const serverId = nodeId.replace('server-', '')
      await loadServerContent(parseInt(serverId))
    }
  }

  // 根据当前路径加载内容
  async function loadContentForPath() {
    if (currentPath.value.length === 0) {
      // 根目录，显示所有环境/机房
      currentContent.value = { containers: [], gpus: [], services: [] }
      return
    }

    loading.value = true
    try {
      // 获取当前节点
      let current = navigationTree.value
      for (const nodeId of currentPath.value) {
        const node = findNodeById(current, nodeId)
        if (node) {
          currentNode.value = node
          current = node.children || []
        }
      }
    } finally {
      loading.value = false
    }
  }

  // 加载服务器内容（容器、GPU等）
  async function loadServerContent(serverId) {
    loading.value = true
    try {
      const res = await assetsApi.getServersTree({ expand_level: 3 })
      if (res.code === 0) {
        const server = res.data.find(s => s.id === serverId)
        if (server) {
          currentNode.value = {
            id: `server-${server.id}`,
            nodeId: server.id,
            name: server.name,
            type: 'server',
            data: server
          }

          // 分离容器和GPU
          const containers = []
          const gpus = []
          const services = []

          if (server.children) {
            for (const child of server.children) {
              if (child._type === 'container') {
                containers.push(child)
                // 收集服务
                if (child.children) {
                  for (const service of child.children) {
                    if (service._type === 'service') {
                      services.push({ ...service, container_name: child.name })
                    }
                  }
                }
              } else if (child._type === 'gpu') {
                gpus.push(child)
              }
            }
          }

          currentContent.value = { containers, gpus, services }
        } else {
          console.warn('Server not found for ID:', serverId)
        }
      } else {
        console.error('Failed to load server content:', res)
      }
    } catch (error) {
      console.error('Error in loadServerContent:', error)
    } finally {
      loading.value = false
    }
  }

  // 展开/折叠节点
  function toggleNode(nodeId) {
    const index = expandedNodes.value.indexOf(nodeId)
    if (index >= 0) {
      expandedNodes.value.splice(index, 1)
    } else {
      expandedNodes.value.push(nodeId)
    }
    saveState()
  }

  // 选中项
  function selectItem(item, multiSelect = false) {
    if (multiSelect) {
      // Ctrl+Click 多选
      const index = selectedItems.value.findIndex(
        i => i.id === item.id && i.type === item.type
      )
      if (index >= 0) {
        selectedItems.value.splice(index, 1)
      } else {
        selectedItems.value.push({ id: item.id, type: item.type, data: item })
      }
    } else {
      // 单选
      selectedItems.value = [{ id: item.id, type: item.type, data: item }]
    }
    lastSelected.value = item
  }

  // 清除选择
  function clearSelection() {
    selectedItems.value = []
    lastSelected.value = null
  }

  // 全选当前内容
  function selectAll() {
    selectedItems.value = []

    for (const container of currentContent.value.containers) {
      selectedItems.value.push({ id: container.id, type: 'container', data: container })
    }
    for (const gpu of currentContent.value.gpus) {
      selectedItems.value.push({ id: gpu.id, type: 'gpu', data: gpu })
    }
    for (const service of currentContent.value.services) {
      selectedItems.value.push({ id: service.id, type: 'service', data: service })
    }
  }

  // 获取当前所有可选项列表（用于键盘导航）
  function getAllSelectableItems() {
    const items = []

    // 如果在服务器内容页面
    if (currentNode.value?.type === 'server') {
      for (const container of currentContent.value.containers) {
        items.push({ id: container.id, type: 'container', data: container })
      }
      for (const gpu of currentContent.value.gpus) {
        items.push({ id: gpu.id, type: 'gpu', data: gpu })
      }
      for (const service of currentContent.value.services) {
        items.push({ id: service.id, type: 'service', data: service })
      }
    } else if (currentNode.value) {
      // 如果在环境/机房节点，返回子节点
      for (const child of currentNode.value.children || []) {
        items.push({ id: child.id, type: child.type, data: child })
      }
    }

    return items
  }

  // 键盘导航：选择下一个/上一个项目
  function selectNext() {
    const items = getAllSelectableItems()
    if (items.length === 0) return

    if (selectedItems.value.length === 0) {
      // 没有选中项，选择第一个
      selectItem({ ...items[0].data, id: items[0].id, type: items[0].type })
      return
    }

    // 找到当前选中项的索引
    const currentSelected = selectedItems.value[selectedItems.value.length - 1]
    const currentIndex = items.findIndex(
      i => i.id === currentSelected.id && i.type === currentSelected.type
    )

    if (currentIndex < items.length - 1) {
      const nextItem = items[currentIndex + 1]
      selectItem({ ...nextItem.data, id: nextItem.id, type: nextItem.type })
    }
  }

  function selectPrevious() {
    const items = getAllSelectableItems()
    if (items.length === 0) return

    if (selectedItems.value.length === 0) {
      // 没有选中项，选择最后一个
      const lastItem = items[items.length - 1]
      selectItem({ ...lastItem.data, id: lastItem.id, type: lastItem.type })
      return
    }

    // 找到当前选中项的索引
    const currentSelected = selectedItems.value[selectedItems.value.length - 1]
    const currentIndex = items.findIndex(
      i => i.id === currentSelected.id && i.type === currentSelected.type
    )

    if (currentIndex > 0) {
      const prevItem = items[currentIndex - 1]
      selectItem({ ...prevItem.data, id: prevItem.id, type: prevItem.type })
    }
  }

  // 打开当前选中的项目
  async function openSelected() {
    if (selectedItems.value.length !== 1) return

    const selected = selectedItems.value[0]
    if (selected.type === 'environment' || selected.type === 'datacenter') {
      await navigateTo(selected.id, selected.type)
    } else if (selected.type === 'server') {
      const serverId = selected.id.toString().replace('server-', '')
      await loadServerContent(parseInt(serverId))
    }
  }

  // Shift+Click 范围选择
  function selectRange(item) {
    const items = getAllSelectableItems()
    if (items.length === 0) return

    if (!lastSelected.value) {
      // 没有上一个选中项，执行普通选择
      selectItem(item)
      return
    }

    // 找到上一个选中项的索引
    const lastIndex = items.findIndex(
      i => i.id === lastSelected.value.id && i.type === lastSelected.value.type
    )
    // 找到当前点击项的索引
    const currentIndex = items.findIndex(
      i => i.id === item.id && i.type === item.type
    )

    if (lastIndex === -1 || currentIndex === -1) {
      selectItem(item)
      return
    }

    // 计算范围
    const start = Math.min(lastIndex, currentIndex)
    const end = Math.max(lastIndex, currentIndex)

    // 选择范围内的所有项
    selectedItems.value = []
    for (let i = start; i <= end; i++) {
      selectedItems.value.push({
        id: items[i].id,
        type: items[i].type,
        data: items[i].data
      })
    }
  }

  // 切换视图模式
  function setViewMode(mode) {
    viewMode.value = mode
    savePreferences()
  }

  // 切换分组方式
  async function setGroupingMode(mode) {
    groupingMode.value = mode
    savePreferences()
    await loadNavigationTree()
  }

  // 返回上一级
  function navigateBack() {
    if (currentPath.value.length > 0) {
      currentPath.value.pop()
      loadContentForPath()
    }
  }

  // 返回根目录
  function navigateHome() {
    currentPath.value = []
    currentNode.value = null
    currentContent.value = { containers: [], gpus: [], services: [] }
  }

  // 保存用户偏好
  function savePreferences() {
    try {
      const prefs = {
        viewMode: viewMode.value,
        groupingMode: groupingMode.value,
        panelWidth: preferences.value.panelWidth,
        showDetailBar: preferences.value.showDetailBar
      }
      localStorage.setItem(STORAGE_KEY_PREFS, JSON.stringify(prefs))
    } catch (e) {
      console.warn('保存偏好失败:', e)
    }
  }

  // 加载用户偏好
  function loadPreferences() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_PREFS)
      if (saved) {
        const prefs = JSON.parse(saved)
        if (prefs.viewMode) viewMode.value = prefs.viewMode
        if (prefs.groupingMode) groupingMode.value = prefs.groupingMode
        if (prefs.panelWidth) preferences.value.panelWidth = prefs.panelWidth
        if (prefs.showDetailBar !== undefined) preferences.value.showDetailBar = prefs.showDetailBar
      }
    } catch (e) {
      console.warn('加载偏好失败:', e)
    }
  }

  // 保存状态
  function saveState() {
    try {
      const state = {
        currentPath: currentPath.value,
        expandedNodes: expandedNodes.value
      }
      localStorage.setItem(STORAGE_KEY_STATE, JSON.stringify(state))
    } catch (e) {
      console.warn('保存状态失败:', e)
    }
  }

  // 加载状态
  function loadState() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_STATE)
      if (saved) {
        const state = JSON.parse(saved)
        if (state.currentPath) currentPath.value = state.currentPath
        if (state.expandedNodes) expandedNodes.value = state.expandedNodes
      }
    } catch (e) {
      console.warn('加载状态失败:', e)
    }
  }

  // 设置面板宽度
  function setPanelWidth(width) {
    preferences.value.panelWidth = Math.min(400, Math.max(200, width))
    savePreferences()
  }

  // 加载快捷访问数据
  async function loadQuickAccess() {
    try {
      console.log('Loading quick access data...')
      const res = await assetsApi.getServersTree({ expand_level: 1 })
      console.log('Quick access servers raw:', res.data)
      if (res.code === 0) {
        const servers = res.data

        // 离线服务器
        quickAccess.value.offlineServers = servers
          .filter(s => s.status === 'offline')
          .slice(0, 5)
        console.log('Offline servers:', quickAccess.value.offlineServers)

        // 高负载服务器 (CPU或内存 > 80%)
        quickAccess.value.highLoadServers = servers
          .filter(s => (s.cpu_usage > 80 || s.memory_usage > 80))
          .slice(0, 5)
        console.log('High load servers:', quickAccess.value.highLoadServers)
      }
    } catch (e) {
      console.warn('加载快捷访问失败:', e)
    }
  }

  return {
    // 状态
    currentPath,
    expandedNodes,
    groupingMode,
    selectedItems,
    lastSelected,
    viewMode,
    sortBy,
    sortOrder,
    navigationTree,
    currentContent,
    currentNode,
    loading,
    treeLoading,
    quickAccess,
    preferences,
    datacenters,
    environments,

    // 计算属性
    breadcrumbPath,
    hasSelection,
    selectionCount,
    contentStats,

    // 方法
    loadNavigationTree,
    navigateTo,
    loadServerContent,
    toggleNode,
    selectItem,
    clearSelection,
    selectAll,
    selectNext,
    selectPrevious,
    openSelected,
    selectRange,
    getAllSelectableItems,
    setViewMode,
    setGroupingMode,
    navigateBack,
    navigateHome,
    savePreferences,
    loadPreferences,
    saveState,
    loadState,
    setPanelWidth,
    loadQuickAccess,
    findNodeById,
    getNodeIcon
  }
})
