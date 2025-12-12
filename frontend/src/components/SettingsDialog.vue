<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="系统设置"
    width="700px"
  >
    <el-tabs v-model="activeTab">
      <!-- 机房管理 -->
      <el-tab-pane label="机房管理" name="datacenters">
        <div class="setting-section">
          <div class="section-header">
            <span>机房列表</span>
            <el-button type="primary" size="small" @click="showDcDialog()">添加机房</el-button>
          </div>
          <el-table :data="datacenters" size="small">
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="location" label="位置" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button text type="primary" size="small" @click="showDcDialog(row)">编辑</el-button>
                <el-button text type="danger" size="small" @click="deleteDc(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 用户管理 -->
      <el-tab-pane label="用户管理" name="users">
        <div class="setting-section">
          <div class="section-header">
            <span>用户列表</span>
            <el-button type="primary" size="small" @click="showUserDialog()">添加用户</el-button>
          </div>
          <el-table :data="users" size="small">
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="display_name" label="显示名" />
            <el-table-column label="角色" width="100">
              <template #default="{ row }">
                <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small">
                  {{ row.role === 'admin' ? '管理员' : '用户' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button text type="primary" size="small" @click="showUserDialog(row)">编辑</el-button>
                <el-button text type="danger" size="small" @click="deleteUser(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 机房表单弹窗 -->
    <el-dialog v-model="dcDialogVisible" :title="editingDc ? '编辑机房' : '添加机房'" width="400px" append-to-body>
      <el-form :model="dcForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="dcForm.name" />
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="dcForm.location" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dcDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveDc">确定</el-button>
      </template>
    </el-dialog>

    <!-- 用户表单弹窗 -->
    <el-dialog v-model="userDialogVisible" :title="editingUser ? '编辑用户' : '添加用户'" width="400px" append-to-body>
      <el-form :model="userForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="userForm.username" :disabled="!!editingUser" />
        </el-form-item>
        <el-form-item label="显示名">
          <el-input v-model="userForm.display_name" />
        </el-form-item>
        <el-form-item label="密码" v-if="!editingUser">
          <el-input v-model="userForm.password" type="password" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="userForm.role" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="userForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser">确定</el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { assetsApi } from '@/api/assets'
import { usersApi } from '@/api/admin'

const props = defineProps({ modelValue: Boolean })

const activeTab = ref('datacenters')
const datacenters = ref([])
const users = ref([])

const dcDialogVisible = ref(false)
const editingDc = ref(null)
const dcForm = reactive({ name: '', location: '' })

const userDialogVisible = ref(false)
const editingUser = ref(null)
const userForm = reactive({ username: '', display_name: '', password: '', role: 'user', is_active: true })

watch(() => props.modelValue, (val) => {
  if (val) {
    loadDatacenters()
    loadUsers()
  }
})

const loadDatacenters = async () => {
  const res = await assetsApi.getDatacenters()
  if (res.code === 0) datacenters.value = res.data
}

const loadUsers = async () => {
  const res = await usersApi.getUsers({ page_size: 100 })
  if (res.code === 0) users.value = res.data
}

const showDcDialog = (dc = null) => {
  editingDc.value = dc
  Object.assign(dcForm, dc || { name: '', location: '' })
  dcDialogVisible.value = true
}

const saveDc = async () => {
  try {
    if (editingDc.value) {
      await assetsApi.updateDatacenter(editingDc.value.id, dcForm)
    } else {
      await assetsApi.createDatacenter(dcForm)
    }
    ElMessage.success('保存成功')
    dcDialogVisible.value = false
    loadDatacenters()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

const deleteDc = async (dc) => {
  await ElMessageBox.confirm(`确定删除机房 "${dc.name}"?`)
  await assetsApi.deleteDatacenter(dc.id)
  ElMessage.success('删除成功')
  loadDatacenters()
}

const showUserDialog = (user = null) => {
  editingUser.value = user
  Object.assign(userForm, user || { username: '', display_name: '', password: '', role: 'user', is_active: true })
  userDialogVisible.value = true
}

const saveUser = async () => {
  try {
    if (editingUser.value) {
      await usersApi.updateUser(editingUser.value.id, userForm)
    } else {
      await usersApi.createUser(userForm)
    }
    ElMessage.success('保存成功')
    userDialogVisible.value = false
    loadUsers()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

const deleteUser = async (user) => {
  await ElMessageBox.confirm(`确定删除用户 "${user.username}"?`)
  await usersApi.deleteUser(user.id)
  ElMessage.success('删除成功')
  loadUsers()
}
</script>

<style lang="scss" scoped>
.setting-section {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    font-weight: 500;
  }
}
</style>
