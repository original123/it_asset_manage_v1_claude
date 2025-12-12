import request from '@/utils/request'

export const authApi = {
  login(username, password) {
    return request.post('/auth/login', { username, password })
  },

  logout() {
    return request.post('/auth/logout')
  },

  getMe() {
    return request.get('/auth/me')
  },

  changePassword(oldPassword, newPassword) {
    return request.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword
    })
  }
}
