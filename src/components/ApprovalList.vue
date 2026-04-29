<template>
  <div class="min-h-screen paper-texture">
    <header class="sticky top-0 z-50 glass-warm border-b border-[#E8D5C4]">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button @click="$router.back()" class="w-10 h-10 rounded-full hover:bg-[#E8D5C4] flex items-center justify-center transition-colors">
            <Icon icon="solar:arrow-left-bold" class="text-[#8B6F4E]" />
          </button>
          <div>
            <h1 class="text-xl font-bold text-[#5C4A3A] font-serif tracking-wider">审核中心</h1>
            <p class="text-xs text-gray-500">修改审批 · 变更记录</p>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-6">
      <div v-if="pendingApprovals.length > 0" class="bg-white rounded-2xl shadow-soft border border-stone-100 p-6 mb-6">
        <h3 class="text-lg font-bold text-[#5C4A3A] font-serif flex items-center space-x-2 mb-4">
          <Icon icon="solar:notification-bold" class="text-[#C84A3E]" />
          <span>待处理审核（{{ pendingApprovals.length }}）</span>
          <span class="text-sm font-normal text-gray-400">需要您审批的变更申请</span>
        </h3>
        <div class="space-y-4">
          <div v-for="approval in pendingApprovals" :key="approval.id" 
            class="p-5 bg-gradient-to-br from-[#FAF7F2] to-[#F5F1EC] rounded-xl border border-[#E8D5C4]">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-3 mb-2">
                  <span class="px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-700">
                    {{ operationLabel(approval.operation) }}
                  </span>
                  <span class="px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700">
                    {{ targetTypeLabel(approval.targetType) }}
                  </span>
                </div>
                <div class="flex items-center space-x-3 mb-3">
                  <div class="w-8 h-8 rounded-full bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] flex items-center justify-center">
                    <span class="text-white text-sm font-medium">
                      {{ approval.requester?.nickname?.charAt(0) || approval.requester?.username?.charAt(0) || '?' }}
                    </span>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-[#5C4A3A]">
                      {{ approval.requester?.nickname || approval.requester?.username || '未知用户' }}
                    </p>
                    <p class="text-xs text-gray-500">
                      申请时间: {{ formatDate(approval.createdAt) }}
                    </p>
                  </div>
                </div>
                <div v-if="approval.comment" class="mb-3 p-3 bg-white/60 rounded-lg">
                  <p class="text-sm text-gray-600">
                    <span class="text-gray-400">申请说明: </span>{{ approval.comment }}
                  </p>
                </div>
                <div class="p-3 bg-white/80 rounded-lg">
                  <p class="text-xs text-gray-400 mb-2">变更内容预览:</p>
                  <div class="text-sm text-gray-600 space-y-1">
                    <template v-for="(value, key) in approval.modifiedData" :key="key">
                      <div class="flex items-start space-x-2">
                        <span class="text-gray-400 w-20 flex-shrink-0">{{ fieldLabel(key) }}:</span>
                        <span class="text-[#5C4A3A]">{{ formatValue(value) }}</span>
                      </div>
                    </template>
                  </div>
                </div>
              </div>
            </div>
            <div class="flex items-center justify-end space-x-3 mt-4 pt-4 border-t border-[#E8D5C4]">
              <button @click="showDetail(approval)" class="text-[#8B6F4E] text-sm hover:text-[#D4A574] transition-colors">
                查看详情
              </button>
              <button @click="rejectApproval(approval)" class="px-4 py-2 text-gray-600 bg-gray-100 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors">
                拒绝
              </button>
              <button @click="approveApproval(approval)" class="px-4 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-lg text-sm font-medium shadow-warm hover:shadow-lg transition-all">
                批准
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl shadow-soft border border-stone-100 p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif flex items-center space-x-2">
            <Icon icon="solar:history-bold" class="text-[#8B6F4E]" />
            <span>审核历史</span>
          </h3>
          <div class="flex items-center space-x-3">
            <select v-model="approvalStatusFilter" class="px-3 py-1.5 bg-[#FAF7F2] border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
              <option value="">全部状态</option>
              <option value="approved">已批准</option>
              <option value="rejected">已拒绝</option>
              <option value="pending">待处理</option>
            </select>
            <select v-model="approvalTypeFilter" class="px-3 py-1.5 bg-[#FAF7F2] border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
              <option value="">全部类型</option>
              <option value="create">创建</option>
              <option value="update">更新</option>
              <option value="delete">删除</option>
            </select>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-stone-200">
                <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">申请人</th>
                <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">操作类型</th>
                <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">目标类型</th>
                <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">状态</th>
                <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">审批人</th>
                <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">申请时间</th>
                <th class="text-right py-3 px-4 text-xs font-medium text-gray-500 uppercase">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="approval in filteredApprovals" :key="approval.id" 
                class="border-b border-stone-100 hover:bg-[#FAF7F2] transition-colors">
                <td class="py-4 px-4">
                  <div class="flex items-center space-x-3">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] flex items-center justify-center">
                      <span class="text-white text-sm font-medium">
                        {{ approval.requester?.nickname?.charAt(0) || approval.requester?.username?.charAt(0) || '?' }}
                      </span>
                    </div>
                    <div>
                      <p class="text-sm font-medium text-[#5C4A3A]">
                        {{ approval.requester?.nickname || approval.requester?.username }}
                      </p>
                    </div>
                  </div>
                </td>
                <td class="py-4 px-4">
                  <span class="px-2 py-1 rounded text-xs font-medium"
                    :class="operationClass(approval.operation)">
                    {{ operationLabel(approval.operation) }}
                  </span>
                </td>
                <td class="py-4 px-4">
                  <span class="text-sm text-gray-600">
                    {{ targetTypeLabel(approval.targetType) }}
                  </span>
                </td>
                <td class="py-4 px-4">
                  <span class="px-2 py-1 rounded-full text-xs font-medium"
                    :class="approvalStatusClass(approval.status)">
                    {{ approvalStatusLabel(approval.status) }}
                  </span>
                </td>
                <td class="py-4 px-4">
                  <template v-if="approval.approver">
                    <span class="text-sm text-gray-600">
                      {{ approval.approver.nickname || approval.approver.username }}
                    </span>
                  </template>
                  <template v-else>
                    <span class="text-sm text-gray-400">-</span>
                  </template>
                </td>
                <td class="py-4 px-4 text-sm text-gray-500">
                  {{ formatDate(approval.createdAt) }}
                </td>
                <td class="py-4 px-4 text-right">
                  <button @click="showDetail(approval)" class="text-[#8B6F4E] text-sm hover:text-[#D4A574] transition-colors">
                    详情
                  </button>
                </td>
              </tr>
              <tr v-if="filteredApprovals.length === 0">
                <td colspan="7" class="py-8 text-center text-gray-400">
                  暂无审核记录
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="showMyApprovals && myApprovals.length > 0" class="bg-white rounded-2xl shadow-soft border border-stone-100 p-6 mt-6">
        <h3 class="text-lg font-bold text-[#5C4A3A] font-serif flex items-center space-x-2 mb-4">
          <Icon icon="solar:document-bold" class="text-[#8B6F4E]" />
          <span>我的申请</span>
        </h3>
        <div class="space-y-3">
          <div v-for="approval in myApprovals" :key="approval.id" 
            class="flex items-center justify-between p-4 border border-stone-100 rounded-xl hover:border-[#E8D5C4] transition-colors">
            <div class="flex items-center space-x-4">
              <div class="w-10 h-10 rounded-lg flex items-center justify-center"
                :class="{
                  'bg-green-100': approval.status === 'approved',
                  'bg-red-100': approval.status === 'rejected',
                  'bg-yellow-100': approval.status === 'pending'
                }">
                <Icon v-if="approval.status === 'approved'" icon="solar:check-circle-bold" class="text-green-600 text-xl" />
                <Icon v-else-if="approval.status === 'rejected'" icon="solar:close-circle-bold" class="text-red-600 text-xl" />
                <Icon v-else icon="solar:clock-circle-bold" class="text-yellow-600 text-xl" />
              </div>
              <div>
                <p class="font-medium text-[#5C4A3A]">
                  {{ operationLabel(approval.operation) }} - {{ targetTypeLabel(approval.targetType) }}
                </p>
                <p class="text-xs text-gray-500">
                  申请时间: {{ formatDate(approval.createdAt) }}
                </p>
              </div>
            </div>
            <div class="flex items-center space-x-3">
              <span class="px-2 py-1 rounded-full text-xs font-medium"
                :class="approvalStatusClass(approval.status)">
                {{ approvalStatusLabel(approval.status) }}
              </span>
              <button @click="showDetail(approval)" class="text-[#8B6F4E] text-sm hover:text-[#D4A574] transition-colors">
                查看
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <div v-if="showDetailModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        <div class="border-b border-stone-100 px-6 py-4 flex items-center justify-between flex-shrink-0">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">审核详情</h3>
          <button @click="closeDetailModal" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="material-symbols:close" class="text-gray-500" />
          </button>
        </div>
        
        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="selectedApproval" class="space-y-6">
            <div class="grid grid-cols-2 gap-4">
              <div class="p-4 bg-[#FAF7F2] rounded-xl">
                <p class="text-xs text-gray-500 mb-1">操作类型</p>
                <span class="px-2 py-1 rounded text-xs font-medium"
                  :class="operationClass(selectedApproval.operation)">
                  {{ operationLabel(selectedApproval.operation) }}
                </span>
              </div>
              <div class="p-4 bg-[#FAF7F2] rounded-xl">
                <p class="text-xs text-gray-500 mb-1">目标类型</p>
                <p class="font-medium text-[#5C4A3A]">
                  {{ targetTypeLabel(selectedApproval.targetType) }}
                </p>
              </div>
              <div class="p-4 bg-[#FAF7F2] rounded-xl">
                <p class="text-xs text-gray-500 mb-1">申请状态</p>
                <span class="px-2 py-1 rounded-full text-xs font-medium"
                  :class="approvalStatusClass(selectedApproval.status)">
                  {{ approvalStatusLabel(selectedApproval.status) }}
                </span>
              </div>
              <div class="p-4 bg-[#FAF7F2] rounded-xl">
                <p class="text-xs text-gray-500 mb-1">申请时间</p>
                <p class="font-medium text-[#5C4A3A]">
                  {{ formatDate(selectedApproval.createdAt) }}
                </p>
              </div>
            </div>

            <div class="p-4 bg-[#FAF7F2] rounded-xl">
              <p class="text-xs text-gray-500 mb-2">申请人</p>
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] flex items-center justify-center">
                  <span class="text-white font-medium">
                    {{ selectedApproval.requester?.nickname?.charAt(0) || selectedApproval.requester?.username?.charAt(0) || '?' }}
                  </span>
                </div>
                <div>
                  <p class="font-medium text-[#5C4A3A]">
                    {{ selectedApproval.requester?.nickname || selectedApproval.requester?.username }}
                  </p>
                  <p class="text-sm text-gray-500">{{ selectedApproval.requester?.username }}</p>
                </div>
              </div>
            </div>

            <div v-if="selectedApproval.comment" class="p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
              <p class="text-xs text-yellow-700 mb-1">申请说明</p>
              <p class="text-sm text-yellow-800">{{ selectedApproval.comment }}</p>
            </div>

            <div class="p-4 bg-[#FAF7F2] rounded-xl">
              <p class="text-xs text-gray-500 mb-3">变更数据</p>
              <div class="space-y-3">
                <div v-if="selectedApproval.originalData && Object.keys(selectedApproval.originalData).length > 0">
                  <p class="text-sm text-gray-500 mb-2">修改前:</p>
                  <div class="bg-white p-3 rounded-lg space-y-1">
                    <template v-for="(value, key) in selectedApproval.originalData" :key="key">
                      <div class="flex items-start space-x-2 text-sm">
                        <span class="text-gray-400 w-24 flex-shrink-0">{{ fieldLabel(key) }}:</span>
                        <span class="text-gray-600 line-through">{{ formatValue(value) }}</span>
                      </div>
                    </template>
                  </div>
                </div>
                <div>
                  <p class="text-sm text-gray-500 mb-2">修改后:</p>
                  <div class="bg-green-50 p-3 rounded-lg space-y-1">
                    <template v-for="(value, key) in selectedApproval.modifiedData" :key="key">
                      <div class="flex items-start space-x-2 text-sm">
                        <span class="text-gray-400 w-24 flex-shrink-0">{{ fieldLabel(key) }}:</span>
                        <span class="text-green-700 font-medium">{{ formatValue(value) }}</span>
                      </div>
                    </template>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="selectedApproval.status !== 'pending'" class="p-4 border rounded-xl"
              :class="selectedApproval.status === 'approved' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'">
              <p class="text-xs text-gray-500 mb-2">
                {{ selectedApproval.status === 'approved' ? '批准信息' : '拒绝信息' }}
              </p>
              <div class="flex items-center space-x-3 mb-2">
                <div class="w-8 h-8 rounded-full bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] flex items-center justify-center">
                  <span class="text-white text-sm font-medium">
                    {{ selectedApproval.approver?.nickname?.charAt(0) || selectedApproval.approver?.username?.charAt(0) || '?' }}
                  </span>
                </div>
                <div>
                  <p class="text-sm font-medium"
                    :class="selectedApproval.status === 'approved' ? 'text-green-700' : 'text-red-700'">
                    {{ selectedApproval.approver?.nickname || selectedApproval.approver?.username }}
                  </p>
                  <p class="text-xs text-gray-500">
                    {{ selectedApproval.status === 'approved' ? formatDate(selectedApproval.approvedAt!) : formatDate(selectedApproval.rejectedAt!) }}
                  </p>
                </div>
              </div>
              <p v-if="selectedApproval.rejectionReason" class="text-sm text-red-600">
                拒绝原因: {{ selectedApproval.rejectionReason }}
              </p>
            </div>
          </div>
        </div>

        <div v-if="selectedApproval && selectedApproval.status === 'pending'" 
          class="border-t border-stone-100 px-6 py-4 flex justify-end space-x-3 flex-shrink-0">
          <button @click="closeDetailModal" class="px-6 py-2 text-gray-600 bg-gray-100 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors">
            关闭
          </button>
          <button @click="rejectApproval(selectedApproval)" class="px-6 py-2 text-red-600 bg-red-50 rounded-xl text-sm font-medium hover:bg-red-100 transition-colors">
            拒绝
          </button>
          <button @click="approveApproval(selectedApproval)" class="px-6 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all">
            批准
          </button>
        </div>
      </div>
    </div>

    <div v-if="showRejectModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div class="border-b border-stone-100 px-6 py-4 flex items-center justify-between">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">拒绝审核</h3>
          <button @click="closeRejectModal" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="material-symbols:close" class="text-gray-500" />
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">拒绝原因（可选）</label>
            <textarea v-model="rejectReason" rows="4" placeholder="请输入拒绝原因"
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4] resize-none"></textarea>
          </div>
        </div>
        <div class="border-t border-stone-100 px-6 py-4 flex justify-end space-x-3">
          <button @click="closeRejectModal" class="px-6 py-2 text-gray-600 bg-gray-100 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors">
            取消
          </button>
          <button @click="confirmReject" class="px-6 py-2 bg-red-500 text-white rounded-xl text-sm font-medium hover:bg-red-600 transition-colors">
            确认拒绝
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
import { apiService, Approval } from '../services/api'

const router = useRouter()

const isLoading = ref(false)
const approvals = ref<Approval[]>([])
const myApprovals = ref<Approval[]>([])
const approvalStatusFilter = ref('')
const approvalTypeFilter = ref('')
const showMyApprovals = ref(true)

const showDetailModal = ref(false)
const showRejectModal = ref(false)
const selectedApproval = ref<Approval | null>(null)
const rejectReason = ref('')

const pendingApprovals = computed(() => {
  return approvals.value.filter(a => a.status === 'pending')
})

const filteredApprovals = computed(() => {
  let result = approvals.value.filter(a => a.status !== 'pending')
  
  if (approvalStatusFilter.value) {
    result = result.filter(a => a.status === approvalStatusFilter.value)
  }
  
  if (approvalTypeFilter.value) {
    result = result.filter(a => a.operation === approvalTypeFilter.value)
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
    role_change: 'bg-orange-100 text-orange-700',
  }
  return classes[operation] || 'bg-gray-100 text-gray-700'
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
  return labels[targetType] || targetType
}

const approvalStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    pending: '待处理',
    approved: '已批准',
    rejected: '已拒绝',
  }
  return labels[status] || status
}

const approvalStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-700',
    approved: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700',
  }
  return classes[status] || 'bg-gray-100 text-gray-600'
}

const fieldLabel = (field: string) => {
  const labels: Record<string, string> = {
    name: '姓名',
    gender: '性别',
    generation: '世代',
    birthYear: '出生年份',
    deathYear: '去世年份',
    spouse: '配偶',
    fatherId: '父亲',
    residence: '现居地',
    note: '备注',
    status: '状态',
    hallName: '堂号',
    surname: '姓氏',
    ancestor: '始祖',
    description: '简介',
    ziBei: '字辈',
    role: '角色',
    email: '邮箱',
    username: '用户名',
    nickname: '昵称',
  }
  return labels[field] || field
}

const formatValue = (value: unknown) => {
  if (value === null || value === undefined) {
    return '-'
  }
  if (typeof value === 'boolean') {
    return value ? '是' : '否'
  }
  if (typeof value === 'object') {
    return JSON.stringify(value)
  }
  return String(value)
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const loadData = async () => {
  isLoading.value = true
  try {
    const [pendingResp, historyResp, myResp] = await Promise.all([
      apiService.getPendingApprovals(),
      apiService.getApprovals(),
      apiService.getMyApprovals(),
    ])
    
    if (pendingResp.success && pendingResp.data) {
      approvals.value = [...pendingResp.data.approvals]
    }
    
    if (historyResp.success && historyResp.data) {
      approvals.value = [...approvals.value, ...historyResp.data.approvals]
    }
    
    if (myResp.success && myResp.data) {
      myApprovals.value = myResp.data.approvals
    }
  } catch (error) {
    console.error('加载审核数据失败:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadData()
})

const showDetail = (approval: Approval) => {
  selectedApproval.value = approval
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedApproval.value = null
}

const approveApproval = async (approval: Approval) => {
  if (confirm('确定要批准此申请吗？')) {
    try {
      const response = await apiService.approveApproval(approval.id)
      if (response.success && response.data) {
        const index = approvals.value.findIndex(a => a.id === approval.id)
        if (index > -1) {
          approvals.value[index] = response.data
        }
        closeDetailModal()
        alert('已批准')
      } else {
        alert(`操作失败: ${response.error || '未知错误'}`)
      }
    } catch (error) {
      console.error('批准失败:', error)
      alert('操作失败')
    }
  }
}

const rejectApproval = (approval: Approval) => {
  selectedApproval.value = approval
  rejectReason.value = ''
  showRejectModal.value = true
  showDetailModal.value = false
}

const closeRejectModal = () => {
  showRejectModal.value = false
  selectedApproval.value = null
  rejectReason.value = ''
}

const confirmReject = async () => {
  if (!selectedApproval.value) return
  
  try {
    const response = await apiService.rejectApproval(
      selectedApproval.value.id,
      rejectReason.value || undefined
    )
    
    if (response.success && response.data) {
      const index = approvals.value.findIndex(a => a.id === selectedApproval.value!.id)
      if (index > -1) {
        approvals.value[index] = response.data
      }
      closeRejectModal()
      alert('已拒绝')
    } else {
      alert(`操作失败: ${response.error || '未知错误'}`)
    }
  } catch (error) {
    console.error('拒绝失败:', error)
    alert('操作失败')
  }
}
</script>
