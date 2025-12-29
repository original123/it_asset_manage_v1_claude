<template>
  <Teleport to="body">
    <transition name="context-menu">
      <div
        v-if="visible"
        ref="menuRef"
        class="context-menu"
        :style="menuStyle"
        @click.stop
        @contextmenu.prevent
      >
        <div class="menu-content">
          <!-- 服务器菜单 -->
          <template v-if="targetType === 'server'">
            <div class="menu-item" @click="handleAction('view')">
              <el-icon><View /></el-icon>
              <span>查看详情</span>
            </div>
            <div class="menu-item" @click="handleAction('edit')" v-if="authStore.isAdmin">
              <el-icon><Edit /></el-icon>
              <span>编辑</span>
            </div>
            <div class="menu-divider" />
            <div class="menu-item" @click="handleAction('copyIP')">
              <el-icon><CopyDocument /></el-icon>
              <span>复制 IP</span>
            </div>
            <div class="menu-item" @click="handleAction('copySSH')">
              <el-icon><Connection /></el-icon>
              <span>复制 SSH 命令</span>
            </div>
            <div class="menu-divider" v-if="authStore.isAdmin" />
            <div class="menu-item" @click="handleAction('addContainer')" v-if="authStore.isAdmin">
              <el-icon><Plus /></el-icon>
              <span>添加容器</span>
            </div>
            <div class="menu-item" @click="handleAction('addGPU')" v-if="authStore.isAdmin">
              <el-icon><Cpu /></el-icon>
              <span>添加 GPU</span>
            </div>
            <div class="menu-divider" v-if="authStore.isAdmin" />
            <div class="menu-item danger" @click="handleAction('delete')" v-if="authStore.isAdmin">
              <el-icon><Delete /></el-icon>
              <span>删除</span>
            </div>
          </template>

          <!-- 容器菜单 -->
          <template v-else-if="targetType === 'container'">
            <div class="menu-item" @click="handleAction('view')">
              <el-icon><View /></el-icon>
              <span>查看详情</span>
            </div>
            <div class="menu-item" @click="handleAction('edit')" v-if="authStore.isAdmin">
              <el-icon><Edit /></el-icon>
              <span>编辑</span>
            </div>
            <div class="menu-divider" />
            <div class="menu-item" @click="handleAction('copyPorts')">
              <el-icon><CopyDocument /></el-icon>
              <span>复制端口映射</span>
            </div>
            <div class="menu-divider" v-if="authStore.isAdmin" />
            <div class="menu-item" @click="handleAction('addService')" v-if="authStore.isAdmin">
              <el-icon><Plus /></el-icon>
              <span>添加服务</span>
            </div>
            <div class="menu-divider" v-if="authStore.isAdmin" />
            <div class="menu-item danger" @click="handleAction('delete')" v-if="authStore.isAdmin">
              <el-icon><Delete /></el-icon>
              <span>删除</span>
            </div>
          </template>

          <!-- GPU 菜单 -->
          <template v-else-if="targetType === 'gpu'">
            <div class="menu-item" @click="handleAction('view')">
              <el-icon><View /></el-icon>
              <span>查看详情</span>
            </div>
            <div class="menu-item" @click="handleAction('edit')" v-if="authStore.isAdmin">
              <el-icon><Edit /></el-icon>
              <span>编辑</span>
            </div>
            <div class="menu-divider" />
            <div class="menu-item" @click="handleAction('copyInfo')">
              <el-icon><CopyDocument /></el-icon>
              <span>复制 GPU 信息</span>
            </div>
            <div class="menu-divider" v-if="authStore.isAdmin" />
            <div class="menu-item danger" @click="handleAction('delete')" v-if="authStore.isAdmin">
              <el-icon><Delete /></el-icon>
              <span>删除</span>
            </div>
          </template>

          <!-- 服务菜单 -->
          <template v-else-if="targetType === 'service'">
            <div class="menu-item" @click="handleAction('view')">
              <el-icon><View /></el-icon>
              <span>查看详情</span>
            </div>
            <div class="menu-item" @click="handleAction('edit')" v-if="authStore.isAdmin">
              <el-icon><Edit /></el-icon>
              <span>编辑</span>
            </div>
            <div class="menu-divider" />
            <div class="menu-item" @click="handleAction('copyPort')">
              <el-icon><CopyDocument /></el-icon>
              <span>复制端口</span>
            </div>
            <div class="menu-divider" v-if="authStore.isAdmin" />
            <div class="menu-item danger" @click="handleAction('delete')" v-if="authStore.isAdmin">
              <el-icon><Delete /></el-icon>
              <span>删除</span>
            </div>
          </template>

          <!-- 环境/机房菜单 -->
          <template v-else-if="targetType === 'environment' || targetType === 'datacenter'">
            <div class="menu-item" @click="handleAction('open')">
              <el-icon><FolderOpened /></el-icon>
              <span>打开</span>
            </div>
            <div class="menu-item" @click="handleAction('expandAll')">
              <el-icon><Expand /></el-icon>
              <span>展开全部</span>
            </div>
            <div class="menu-item" @click="handleAction('collapseAll')">
              <el-icon><Fold /></el-icon>
              <span>折叠全部</span>
            </div>
          </template>

          <!-- 空白区域菜单 -->
          <template v-else>
            <div class="menu-item" @click="handleAction('refresh')">
              <el-icon><Refresh /></el-icon>
              <span>刷新</span>
            </div>
            <div class="menu-item" @click="handleAction('selectAll')">
              <el-icon><Select /></el-icon>
              <span>全选</span>
              <span class="shortcut">Ctrl+A</span>
            </div>
            <div class="menu-divider" v-if="authStore.isAdmin" />
            <div class="menu-item" @click="handleAction('addServer')" v-if="authStore.isAdmin">
              <el-icon><Plus /></el-icon>
              <span>添加服务器</span>
            </div>
          </template>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import {
  View, Edit, Delete, CopyDocument, Connection, Plus,
  Cpu, Refresh, FolderOpened, Expand, Fold, Select
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  x: {
    type: Number,
    default: 0
  },
  y: {
    type: Number,
    default: 0
  },
  targetType: {
    type: String,
    default: '' // server, container, gpu, service, environment, datacenter, ''
  },
  targetData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:visible', 'action'])

const authStore = useAuthStore()
const menuRef = ref(null)

// 计算菜单位置，确保不超出视口
const menuStyle = computed(() => {
  let x = props.x
  let y = props.y

  // 菜单尺寸估算
  const menuWidth = 180
  const menuHeight = 300

  // 检查右边界
  if (x + menuWidth > window.innerWidth) {
    x = window.innerWidth - menuWidth - 10
  }

  // 检查下边界
  if (y + menuHeight > window.innerHeight) {
    y = window.innerHeight - menuHeight - 10
  }

  return {
    left: `${x}px`,
    top: `${y}px`
  }
})

// 处理菜单操作
function handleAction(action) {
  emit('action', {
    action,
    type: props.targetType,
    data: props.targetData
  })
  closeMenu()
}

// 关闭菜单
function closeMenu() {
  emit('update:visible', false)
}

// 点击外部关闭
function handleClickOutside(e) {
  if (menuRef.value && !menuRef.value.contains(e.target)) {
    closeMenu()
  }
}

// ESC 关闭
function handleKeydown(e) {
  if (e.key === 'Escape') {
    closeMenu()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style lang="scss" scoped>
.context-menu {
  position: fixed;
  z-index: 9999;
  min-width: 160px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  overflow: hidden;

  .menu-content {
    padding: 6px 0;
  }

  .menu-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 16px;
    font-size: 13px;
    color: #303133;
    cursor: pointer;
    transition: background 0.15s;

    &:hover {
      background: #f5f7fa;
    }

    .el-icon {
      font-size: 15px;
      color: #606266;
    }

    .shortcut {
      margin-left: auto;
      font-size: 11px;
      color: #909399;
    }

    &.danger {
      color: #F56C6C;

      .el-icon {
        color: #F56C6C;
      }

      &:hover {
        background: #fef0f0;
      }
    }
  }

  .menu-divider {
    height: 1px;
    margin: 6px 12px;
    background: #ebeef5;
  }
}

// 动画
.context-menu-enter-active,
.context-menu-leave-active {
  transition: all 0.15s ease;
}

.context-menu-enter-from,
.context-menu-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
