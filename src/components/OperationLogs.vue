<template>
  <div class="min-h-screen paper-texture">
    <header class="sticky top-0 z-50 glass-warm border-b border-[#E8D5C4]">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button @click="$router.back()" class="w-10 h-10 rounded-full hover:bg-[#E8D5C4] flex items-center justify-center transition-colors">
            <Icon icon="solar:arrow-left-bold" class="text-[#8B6F4E]" />
          </button>
          <div>
            <h1 class="text-xl font-bold text-[#5C4A3A] font-serif tracking-wider">操作日志</h1>
            <p class="text-xs text-gray-500">操作追踪 · 变更记录</p>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-6">
      <div class="bg-white rounded-2xl shadow-soft border border-stone-100 p-6 mb-6">
        <div class="flex flex-wrap items-center gap-4">
          <div class="relative flex-1 min-w-[200px] max-w-md">
            <Icon icon="solar:search-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input v-model="searchKeyword" type="text" placeholder="搜索操作描述..." 
              class="pl-10 pr-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4] w-full" />
          </div>
          <select v-model="operationFilter" class="px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
            <option value="">全部操作</option>
            <option value="create">创建</option>
            <option value="update">更新</option>
            <option value="delete">删除</option>
            <option value="invite">邀请</option>
            <option value="approve">批准</option>
            <option value="reject">拒绝</option>
            <option value="role_change">角色变更</option>
            <option value="login">登录</option>
            <option value="logout">登出</option>
          </select>
          <select v-model="targetTypeFilter" class="px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
            <option value="">全部目标</option>
            <option value="family">家族</option>
            <option value="family_member">成员</option>
            <option value="user">用户</option>
            <option value="invitation">邀请</option>
            <option value="approval">审核</option>
            <option value="role">角色</option>
          </select>
          <select v-model="userIdFilter" class="px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
            <option value="">全部用户</option>
            <option value="me">我自己</option>
          </select>
          <button @click="loadLogs" class="px-4 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all flex items-center space-x-2">
            <Icon icon="solar:refresh-bold" class="text-sm" />
            <span>刷新</span>
          </button>
        </div>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-xl shadow-soft border border-stone-100 p-4">
          <div class="flex items-center justify-between mb-2">
            <p class="text-xs text-gray-500">今日操作</p>
            <div class="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center">
              <Icon icon="solar:calendar-today-bold" class="text-blue-600" />
            </div>
          </div>
          <p class="text-2xl font-bold text-[#5C4A3A]">{{ todayCount }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-soft border border-stone-100 p-4">
          <div class="flex items-center justify-between mb-2">
            <p class="text-xs text-gray-500">创建操作</p>
            <div class="w-8 h-8 rounded-lg bg-green-100 flex items-center justify-center">
              <Icon icon="solar:add-circle-bold" class="text-green-600" />
            </div>
          </div>
          <p class="text-2xl font-bold text-[#5C4A3A]">{{ createCount }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-soft border border-stone-100 p-4">
          <div class="flex items-center justify-between mb-2">
            <p class="text-xs text-gray-500">更新操作</p>
            <div class="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center">
              <Icon icon="solar:pen-bold" class="text-purple-600" />
            </div>
          </div>
          <p class="text-2xl font-bold text-[#5C4A3A]">{{ updateCount }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-soft border border-stone-100 p-4">
          <div class="flex items-center justify-between mb-2">
            <p class="text-xs text-gray-500">删除操作</p>
            <div class="w-8 h-8 rounded-lg bg-red-100 flex items-center justify-center">
              <Icon icon="solar:trash-bin-trash-bold" class="text-red-600" />
            </div>
          </div>
          <p class="text-2xl font-bold text-[#5C4A3A]">{{ deleteCount }}</p>
        </div>
      </div>

      <div class="bg-white rounded-2xl shadow-soft border border-stone-100 overflow-hidden">
        <div class="divide-y divide-stone-100">
          <div v-for="log in filteredLogs" :key="log.id" 
            class="p-4 hover:bg-[#FAF7F2] transition-colors cursor-pointer"
            @click="showLogDetail(log)">
            <div class="flex items-start space-x-4">
              <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                :class="operationIconClass(log.operation)">
                <Icon :icon="operationIcon(log.operation)" class="text-xl" :class="operationColorClass(log.operation)" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between mb-1">
                  <div class="flex items-center space-x-2">
                    <span class="px-2 py-0.5 rounded text-xs font-medium"
                      :class="operationClass(log.operation)">
                      {{ operationLabel(log.operation) }}
                    </span>
                    <span v-if="log.targetType" class="px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
                      {{ targetTypeLabel(log.targetType) }}
                    </span>
                  </div>
                  <span class="text-xs text-gray-400">
                    {{ formatDate(log.createdAt) }}
                  </span>
                </div>
                <p class="text-sm text-[#5C4A3A] mb-1">
                  {{ log.description || getDefaultDescription(log) }}
                </p>
                <div class="flex items-center space-x-4 text-xs text-gray-500">
                  <span v-if="log.user" class="flex items-center space-x-1">
                    <Icon icon="solar:user-bold" class="text-xs" />
                    <span>{{ log.user.nickname || log.user.username }}</span>
                  </span>
                  <span v-if="log.ipAddress" class="flex items-center space-x-1">
                    <Icon icon="solar:global-bold" class="text-xs" />
                    <span>{{ log.ipAddress }}</span>
                  </span>
                  <span v-if="log.beforeData && Object.keys(log.beforeData).length > 0" 
                    class="flex items-center space-x-1 text-orange-500">
                    <Icon icon="solar:documents-bold" class="text-xs" />
                    <span>有数据变更</span>
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="filteredLogs.length === 0" class="p-12 text-center">
            <Icon icon="solar:inbox-empty-bold" class="text-5xl text-gray-300 mx-auto mb-4" />
            <p class="text-gray-500 mb-2">暂无操作日志</p>
            <p class="text-gray-400 text-sm">当前筛选条件下没有找到操作记录</p>
          </div>
        </div>

        <div v-if="total > logs.length" class="p-4 border-t border-stone-100 text-center">
          <button @click="loadMore" class="px-6 py-2 text-[#8B6F4E] hover:bg-[#E8D5C4] rounded-lg text-sm font-medium transition-colors">
            加载更多
          </button>
        </div>
      </div>
    </main>

    <div v-if="showDetailModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        <div class="border-b border-stone-100 px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-lg flex items-center justify-center"
              :class="operationIconClass(selectedLog?.operation || '')">
              <Icon :icon="operationIcon(selectedLog?.operation || '')" class="text-xl" 
                :class="operationColorClass(selectedLog?.operation || '')" />
            </div>
            <div>
              <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">操作详情</h3>
              <p class="text-xs text-gray-500">
                {{ operationLabel(selectedLog?.operation || '') }}
              </p>
            </div>
          </div>
          <button @click="closeDetailModal" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="material-symbols:close" class="text-gray-500" />
          </button>
        </div>
        
        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="selectedLog" class="space-y-6">
            <div class="grid grid-cols-2 gap-4">
              <div class="p-4 bg-[#FAF7F2] rounded-xl">
                <p class="text-xs text-gray-500 mb-1">操作时间</p>
                <p class="font-medium text-[#5C4A3A]">
                  {{ formatDateTime(selectedLog.createdAt) }}
                </p>
              </div>
              <div class="p-4 bg-[#FAF7F2] rounded-xl">
                <p class="text-xs text-gray-500 mb-1">目标类型</p>
                <p class="font-medium text-[#5C4A3A]">
                  {{ targetTypeLabel(selectedLog.targetType || '') }}
                </p>
              </div>
            </div>

            <div class="p-4 bg-[#FAF7F2] rounded-xl">
              <p class="text-xs text-gray-500 mb-2">操作人</p>
              <div v-if="selectedLog.user" class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] flex items-center justify-center">
                  <span class="text-white font-medium">
                    {{ selectedLog.user.nickname?.charAt(0) || selectedLog.user.username?.charAt(0) || '?' }}
                  </span>
                </div>
                <div>
                  <p class="font-medium text-[#5C4A3A]">
                    {{ selectedLog.user.nickname || selectedLog.user.username }}
                  </p>
                  <p class="text-sm text-gray-500">{{ selectedLog.user.username }}</p>
                </div>
              </div>
              <p v-else class="text-gray-400">未知用户</p>
            </div>

            <div v-if="selectedLog.description" class="p-4 bg-[#FAF7F2] rounded-xl">
              <p class="text-xs text-gray-500 mb-2">操作描述</p>
              <p class="text-sm text-[#5C4A3A]">{{ selectedLog.description }}</p>
            </div>

            <div v-if="selectedLog.ipAddress || selectedLog.userAgent" class="p-4 bg-[#FAF7F2] rounded-xl">
              <p class="text-xs text-gray-500 mb-2">请求信息</p>
              <div class="space-y-2 text-sm">
                <div v-if="selectedLog.ipAddress" class="flex items-start space-x-2">
                  <span class="text-gray-400 w-16 flex-shrink-0">IP地址:</span>
                  <span class="text-[#5C4A3A]">{{ selectedLog.ipAddress }}</span>
                </div>
                <div v-if="selectedLog.userAgent" class="flex items-start space-x-2">
                  <span class="text-gray-400 w-16 flex-shrink-0">浏览器:</span>
                  <span class="text-[#5C4A3A] break-all">{{ selectedLog.userAgent }}</span>
                </div>
              </div>
            </div>

            <div v-if="(selectedLog.beforeData && Object.keys(selectedLog.beforeData).length > 0) || 
                        (selectedLog.afterData && Object.keys(selectedLog.afterData).length > 0)">
              <p class="text-sm font-medium text-[#5C4A3A] mb-3">数据变更详情</p>
              
              <div v-if="selectedLog.beforeData && Object.keys(selectedLog.beforeData).length > 0" class="mb-4">
                <p class="text-xs text-gray-500 mb-2">修改前:</p>
                <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <pre class="text-sm text-gray-600 whitespace-pre-wrap">{{ formatJson(selectedLog.beforeData) }}</pre>
                </div>
              </div>

              <div v-if="selectedLog.afterData && Object.keys(selectedLog.afterData).length > 0">
                <p class="text-xs text-gray-500 mb-2">修改后:</p>
                <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                  <pre class="text-sm text-green-700 whitespace-pre-wrap">{{ formatJson(selectedLog.afterData) }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="border-t border-stone-100 px-6 py-4 flex justify-end flex-shrink-0">
          <button @click="closeDetailModal" class="px-6 py-2 text-gray-600 bg-gray-100 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors">
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import { apiService, OperationLog, authStore } from '../services/api'

const router = useRouter()

const isLoading = ref(false)
const logs = ref<OperationLog[]>([])
const total = ref(0)
const offset = ref(0)
const limit = ref(50)

const searchKeyword = ref('')
const operationFilter = ref('')
const targetTypeFilter = ref('')
const userIdFilter = ref('')

const showDetailModal = ref(false)
const selectedLog = ref<OperationLog | null>(null)

const todayCount = computed(() => {
  const today = new Date().toDateString()
  return logs.value.filter(log => new Date(log.createdAt).toDateString() === today).length
})

const createCount = computed(() => {
  return logs.value.filter(log => log.operation === 'create').length
})

const updateCount = computed(() => {
  return logs.value.filter(log => log.operation === 'update').length
})

const deleteCount = computed(() => {
  return logs.value.filter(log => log.operation === 'delete').length
})

const filteredLogs = computed(() => {
  let result = [...logs.value]
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(log => {
      const desc = (log.description || '').toLowerCase()
      return desc.includes(keyword)
    })
  }
  
  if (operationFilter.value) {
    result = result.filter(log => log.operation === operationFilter.value)
  }
  
  if (targetTypeFilter.value) {
    result = result.filter(log => log.targetType === targetTypeFilter.value)
  }
  
  if (userIdFilter.value === 'me') {
    result = result.filter(log => log.userId === authStore.user?.id)
  }
  
  return result
})

const operationLabel = (operation: string) => {
  const labels: Record<string, string> = {
    create: '创建',
    update: '更新',
    delete: '删除',
    invite: '邀请',
    approve: '批准',
    reject: '拒绝',
    role_change: '角色变更',
    login: '登录',
    logout: '登出',
  }
  return labels[operation] || operation
}

const operationClass = (operation: string) => {
  const classes: Record<string, string> = {
    create: 'bg-green-100 text-green-700',
    update: 'bg-blue-100 text-blue-700',
    delete: 'bg-red-100 text-red-700',
    invite: 'bg-purple-100 text-purple-700',
    approve: 'bg-emerald-100 text-emerald-700',
    reject: 'bg-red-100 text-red-700',
    role_change: 'bg-orange-100 text-orange-700',
    login: 'bg-blue-100 text-blue-700',
    logout: 'bg-gray-100 text-gray-700',
  }
  return classes[operation] || 'bg-gray-100 text-gray-700'
}

const operationIcon = (operation: string) => {
  const icons: Record<string, string> = {
    create: 'solar:add-circle-bold',
    update: 'solar:pen-bold',
    delete: 'solar:trash-bin-trash-bold',
    invite: 'solar:letter-bold',
    approve: 'solar:check-circle-bold',
    reject: 'solar:close-circle-bold',
    role_change: 'solar:user-star-bold',
    login: 'solar:login-3-bold',
    logout: 'solar:logout-3-bold',
  }
  return icons[operation] || 'solar:document-bold'
}

const operationIconClass = (operation: string) => {
  const classes: Record<string, string> = {
    create: 'bg-green-100',
    update: 'bg-blue-100',
    delete: 'bg-red-100',
    invite: 'bg-purple-100',
    approve: 'bg-emerald-100',
    reject: 'bg-red-100',
    role_change: 'bg-orange-100',
    login: 'bg-blue-100',
    logout: 'bg-gray-100',
  }
  return classes[operation] || 'bg-gray-100'
}

const operationColorClass = (operation: string) => {
  const classes: Record<string, string> = {
    create: 'text-green-600',
    update: 'text-blue-600',
    delete: 'text-red-600',
    invite: 'text-purple-600',
    approve: 'text-emerald-600',
    reject: 'text-red-600',
    role_change: 'text-orange-600',
    login: 'text-blue-600',
    logout: 'text-gray-600',
  }
  return classes[operation] || 'text-gray-600'
}

const targetTypeLabel = (targetType: string) => {
  const labels: Record<string, string> = {
    family: '家族',
    family_member: '成员',
    user: '用户',
    invitation: '邀请',
    approval: '审核',
    role: '角色',
  }
  return labels[targetType] || targetType || '未知'
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`
  
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

const formatJson = (data: Record<string, unknown>) => {
  return JSON.stringify(data, null, 2)
}

const getDefaultDescription = (log: OperationLog) => {
  const op = operationLabel(log.operation)
  const target = targetTypeLabel(log.targetType || '')
  return `${op}${target}操作`
}

const loadLogs = async () => {
  isLoading.value = true
  try {
    const options: {
      operation?: string
      targetType?: string
      userId?: string
      limit?: number
      offset?: number
    } = {
      limit: limit.value,
      offset: 0,
    }
    
    if (operationFilter.value) options.operation = operationFilter.value
    if (targetTypeFilter.value) options.targetType = targetTypeFilter.value
    
    const response = await apiService.getOperationLogs(options)
    
    if (response.success && response.data) {
      logs.value = response.data.logs
      total.value = response.data.total
      offset.value = response.data.logs.length
    }
  } catch (error) {
    console.error('加载日志失败:', error)
  } finally {
    isLoading.value = false
  }
}

const loadMore = async () => {
  isLoading.value = true
  try {
    const options: {
      operation?: string
      targetType?: string
      userId?: string
      limit?: number
      offset?: number
    } = {
      limit: limit.value,
      offset: offset.value,
    }
    
    if (operationFilter.value) options.operation = operationFilter.value
    if (targetTypeFilter.value) options.targetType = targetTypeFilter.value
    
    const response = await apiService.getOperationLogs(options)
    
    if (response.success && response.data) {
      logs.value = [...logs.value, ...response.data.logs]
      offset.value = logs.value.length
    }
  } catch (error) {
    console.error('加载更多日志失败:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadLogs()
})

const showLogDetail = (log: OperationLog) => {
  selectedLog.value = log
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedLog.value = null
}
</script>
