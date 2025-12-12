import request from '@/utils/request'

export const auditApi = {
  getLogs(params) {
    return request.get('/audit-logs', { params })
  },

  getLogDetail(id) {
    return request.get(`/audit-logs/${id}`)
  },

  exportLogs(params) {
    return request.get('/audit-logs/export', {
      params,
      responseType: 'blob'
    })
  }
}

export const usersApi = {
  getUsers(params) {
    return request.get('/users', { params })
  },

  createUser(data) {
    return request.post('/users', data)
  },

  updateUser(id, data) {
    return request.put(`/users/${id}`, data)
  },

  deleteUser(id) {
    return request.delete(`/users/${id}`)
  }
}

export const importExportApi = {
  downloadTemplate() {
    return request.get('/import-export/template', {
      responseType: 'blob'
    })
  },

  importData(file, overwrite = false) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('overwrite', overwrite)
    return request.post('/import-export/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  exportData(type = 'all') {
    return request.get('/import-export/export', {
      params: { type },
      responseType: 'blob'
    })
  }
}
