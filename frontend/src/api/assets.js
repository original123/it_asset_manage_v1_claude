import request from '@/utils/request'

export const assetsApi = {
  // 服务器
  getServers(params) {
    return request.get('/servers', { params })
  },

  getServersTree(params) {
    return request.get('/servers/tree', { params })
  },

  getServer(id) {
    return request.get(`/servers/${id}`)
  },

  createServer(data) {
    return request.post('/servers', data)
  },

  updateServer(id, data) {
    return request.put(`/servers/${id}`, data)
  },

  deleteServer(id) {
    return request.delete(`/servers/${id}`)
  },

  // 容器
  getContainers(params) {
    return request.get('/containers', { params })
  },

  getContainer(id) {
    return request.get(`/containers/${id}`)
  },

  createContainer(data) {
    return request.post('/containers', data)
  },

  updateContainer(id, data) {
    return request.put(`/containers/${id}`, data)
  },

  deleteContainer(id) {
    return request.delete(`/containers/${id}`)
  },

  updateContainerSortOrder(items) {
    return request.post('/containers/update-sort-order', { items })
  },

  // 服务
  getServices(params) {
    return request.get('/services', { params })
  },

  createService(data) {
    return request.post('/services', data)
  },

  updateService(id, data) {
    return request.put(`/services/${id}`, data)
  },

  deleteService(id) {
    return request.delete(`/services/${id}`)
  },

  updateServiceSortOrder(items) {
    return request.post('/services/update-sort-order', { items })
  },

  // GPU
  getGpus(params) {
    return request.get('/gpus', { params })
  },

  createGpu(data) {
    return request.post('/gpus', data)
  },

  updateGpu(id, data) {
    return request.put(`/gpus/${id}`, data)
  },

  assignGpu(id, userId) {
    return request.post(`/gpus/${id}/assign`, { user_id: userId })
  },

  releaseGpu(id) {
    return request.post(`/gpus/${id}/release`)
  },

  deleteGpu(id) {
    return request.delete(`/gpus/${id}`)
  },

  updateGpuSortOrder(items) {
    return request.post('/gpus/update-sort-order', { items })
  },

  // 机房
  getDatacenters(params) {
    return request.get('/datacenters', { params })
  },

  getDatacentersOverview() {
    return request.get('/datacenters/overview')
  },

  createDatacenter(data) {
    return request.post('/datacenters', data)
  },

  updateDatacenter(id, data) {
    return request.put(`/datacenters/${id}`, data)
  },

  deleteDatacenter(id) {
    return request.delete(`/datacenters/${id}`)
  },

  // 环境
  getEnvironments() {
    return request.get('/environments')
  },

  // 搜索
  search(keyword) {
    return request.get('/search', { params: { keyword } })
  },

  quickSearch(keyword) {
    return request.get('/search/quick', { params: { keyword } })
  },

  // 用户选项
  getUserOptions() {
    return request.get('/users/options')
  }
}
