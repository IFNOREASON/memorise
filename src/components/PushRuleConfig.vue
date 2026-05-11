<template>
  <div class="min-h-screen paper-texture">
    <header class="sticky top-0 z-50 glass-warm border-b border-[#E8D5C4]">
      <div class="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button @click="$router.back()" class="w-10 h-10 rounded-full hover:bg-[#E8D5C4] flex items-center justify-center transition-colors">
            <Icon icon="solar:arrow-left-bold" class="text-[#8B6F4E]" />
          </button>
          <div>
            <h1 class="text-xl font-bold text-[#5C4A3A] font-serif tracking-wider">推送规则配置</h1>
            <p class="text-xs text-gray-500">设置纪念日提醒推送方式</p>
          </div>
        </div>
        <button @click="showCreateModal = true" class="px-4 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all flex items-center space-x-2">
          <Icon icon="solar:add-circle-bold" class="text-sm" />
          <span>添加规则</span>
        </button>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-6 py-6">
      <div class="bg-gradient-to-r from-[#FAF7F2] to-[#F5EDE4] rounded-2xl shadow-soft border border-[#E8D5C4] p-6 mb-6">
        <h3 class="text-lg font-bold text-[#8B6F4E] mb-3 flex items-center space-x-2">
          <Icon icon="solar:info-circle-bold" class="text-[#8B6F4E]" />
          <span>关于推送规则</span>
        </h3>
        <ul class="text-sm text-gray-600 space-y-2">
          <li class="flex items-start space-x-2">
            <Icon icon="solar:check-circle-bold" class="text-green-500 mt-0.5 flex-shrink-0" />
            <span>可以为不同类型的纪念日设置不同的提醒规则</span>
          </li>
          <li class="flex items-start space-x-2">
            <Icon icon="solar:check-circle-bold" class="text-green-500 mt-0.5 flex-shrink-0" />
            <span>设置提前提醒天数，让您有足够的时间准备</span>
          </li>
          <li class="flex items-start space-x-2">
            <Icon icon="solar:check-circle-bold" class="text-green-500 mt-0.5 flex-shrink-0" />
            <span>不设置纪念日类型的规则将适用于所有类型</span>
          </li>
        </ul>
      </div>

      <div v-if="pushRules.length > 0" class="space-y-4">
        <div v-for="rule in pushRules" :key="rule.id" 
          class="bg-white rounded-2xl shadow-soft border border-stone-100 p-5">
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 rounded-xl bg-[#E8D5C4] flex items-center justify-center">
                <Icon icon="solar:bell-ring-bold" class="text-[#8B6F4E]" />
              </div>
              <div>
                <p class="font-medium text-[#5C4A3A]">
                  {{ rule.anniversaryType ? anniversaryTypeLabel(rule.anniversaryType) : '所有纪念日' }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ rule.isEnabled ? '已启用' : '已停用' }}
                </p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button @click="toggleRuleStatus(rule)" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
                <Icon :icon="rule.isEnabled ? 'solar:eye-bold' : 'solar:eye-closed-bold'" 
                  :class="rule.isEnabled ? 'text-green-500' : 'text-gray-400'" class="text-sm" />
              </button>
              <button @click="editRule(rule)" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
                <Icon icon="solar:pen-bold" class="text-gray-500 text-sm" />
              </button>
              <button @click="deleteRule(rule)" class="w-8 h-8 rounded-full hover:bg-red-50 flex items-center justify-center transition-colors">
                <Icon icon="solar:trash-bin-trash-bold" class="text-red-500 text-sm" />
              </button>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-4">
            <div class="bg-[#FAF7F2] rounded-xl p-3">
              <p class="text-xs text-gray-500 mb-1">推送渠道</p>
              <div class="flex items-center space-x-1">
                <template v-for="channel in rule.pushChannels" :key="channel">
                  <span class="px-2 py-0.5 bg-white rounded text-xs text-[#8B6F4E] border border-[#E8D5C4]">
                    {{ channelLabel(channel) }}
                  </span>
                </template>
              </div>
            </div>
            <div class="bg-[#FAF7F2] rounded-xl p-3">
              <p class="text-xs text-gray-500 mb-1">提前提醒</p>
              <p class="text-sm font-medium text-[#5C4A3A]">
                {{ rule.advanceDays === 0 ? '当天' : rule.advanceDays + '天前' }}
              </p>
            </div>
            <div class="bg-[#FAF7F2] rounded-xl p-3">
              <p class="text-xs text-gray-500 mb-1">推送时间</p>
              <p class="text-sm font-medium text-[#5C4A3A]">{{ rule.pushTime }}</p>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="bg-white rounded-2xl shadow-soft border border-stone-100 p-12 text-center">
        <Icon icon="solar:settings-bold" class="text-6xl text-gray-300 mx-auto mb-4" />
        <p class="text-gray-500 mb-2">暂无推送规则</p>
        <p class="text-gray-400 text-sm mb-4">添加规则以启用纪念日提醒</p>
        <button @click="showCreateModal = true" class="px-4 py-2 bg-[#8B6F4E] text-white rounded-xl text-sm font-medium hover:bg-[#A67B5B] transition-colors">
          添加推送规则
        </button>
      </div>
    </main>

    <div v-if="showCreateModal || showEditModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div class="border-b border-stone-100 px-6 py-4 flex items-center justify-between">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">
            {{ showEditModal ? '编辑规则' : '添加规则' }}
          </h3>
          <button @click="closeModal" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="material-symbols:close" class="text-gray-500" />
          </button>
        </div>
        <div class="p-6 space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">适用纪念日类型</label>
            <select v-model="form.anniversaryType" class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
              <option :value="undefined">所有纪念日类型</option>
              <option v-for="type in anniversaryTypes" :key="type.value" :value="type.value">
                {{ type.label }}
              </option>
            </select>
            <p class="text-xs text-gray-400 mt-1">选择"所有纪念日类型"将适用于所有未单独设置规则的纪念日</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">推送渠道</label>
            <div class="space-y-2">
              <label v-for="channel in channels" :key="channel.value" 
                class="flex items-center space-x-3 p-3 bg-[#FAF7F2] rounded-xl cursor-pointer hover:bg-[#F5EDE4] transition-colors">
                <input type="checkbox" v-model="form.pushChannels" :value="channel.value"
                  class="w-4 h-4 rounded text-[#8B6F4E] focus:ring-[#8B6F4E]" />
                <div>
                  <p class="text-sm font-medium text-[#5C4A3A]">{{ channel.label }}</p>
                  <p class="text-xs text-gray-500">{{ channel.description }}</p>
                </div>
              </label>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">提前提醒天数</label>
              <select v-model="form.advanceDays" class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
                <option :value="0">当天提醒</option>
                <option :value="1">提前1天</option>
                <option :value="3">提前3天</option>
                <option :value="7">提前7天</option>
                <option :value="14">提前14天</option>
                <option :value="30">提前30天</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">推送时间</label>
              <input v-model="form.pushTime" type="time" 
                class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
            </div>
          </div>

          <div class="flex items-center space-x-2">
            <input v-model="form.isEnabled" type="checkbox" 
              class="w-4 h-4 rounded text-[#8B6F4E] focus:ring-[#8B6F4E]" />
            <span class="text-sm text-gray-700">启用此规则</span>
          </div>
        </div>
        <div class="border-t border-stone-100 px-6 py-4 flex justify-end space-x-3">
          <button @click="closeModal" class="px-6 py-2 text-gray-600 bg-gray-100 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors">
            取消
          </button>
          <button @click="saveRule" class="px-6 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all">
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { 
  apiService, 
  PushRule,
  AnniversaryType,
  PushChannel,
  CreatePushRuleRequest,
  UpdatePushRuleRequest
} from '../services/api'

const pushRules = ref<PushRule[]>([])

const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingRule = ref<PushRule | null>(null)

const anniversaryTypes = [
  { value: 'birthday' as AnniversaryType, label: '生日' },
  { value: 'deathday' as AnniversaryType, label: '忌日' },
  { value: 'weddingday' as AnniversaryType, label: '结婚日' },
  { value: 'sacrificialday' as AnniversaryType, label: '祭祀日' }
]

const channels = [
  { value: 'in_app' as PushChannel, label: '应用内消息', description: '在应用消息中心接收提醒' },
  { value: 'email' as PushChannel, label: '邮件推送', description: '发送到您的注册邮箱' },
  { value: 'sms' as PushChannel, label: '短信推送', description: '发送短信提醒（需配置短信服务）' }
]

const form = reactive<{
  anniversaryType: AnniversaryType | undefined
  pushChannels: PushChannel[]
  advanceDays: number
  pushTime: string
  isEnabled: boolean
}>({
  anniversaryType: undefined,
  pushChannels: ['in_app'],
  advanceDays: 0,
  pushTime: '09:00',
  isEnabled: true
})

const anniversaryTypeLabel = (type: AnniversaryType): string => {
  const labels: Record<AnniversaryType, string> = {
    birthday: '生日',
    deathday: '忌日',
    weddingday: '结婚日',
    sacrificialday: '祭祀日'
  }
  return labels[type] || type
}

const channelLabel = (channel: PushChannel): string => {
  const labels: Record<PushChannel, string> = {
    in_app: '应用内',
    email: '邮件',
    sms: '短信'
  }
  return labels[channel] || channel
}

const loadPushRules = async () => {
  try {
    const response = await apiService.getPushRules()
    if (response.success && response.data) {
      pushRules.value = response.data.rules
    }
  } catch (error) {
    console.error('加载推送规则失败:', error)
  }
}

const resetForm = () => {
  form.anniversaryType = undefined
  form.pushChannels = ['in_app']
  form.advanceDays = 0
  form.pushTime = '09:00'
  form.isEnabled = true
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  editingRule.value = null
  resetForm()
}

const editRule = (rule: PushRule) => {
  editingRule.value = rule
  form.anniversaryType = rule.anniversaryType || undefined
  form.pushChannels = [...rule.pushChannels]
  form.advanceDays = rule.advanceDays
  form.pushTime = rule.pushTime
  form.isEnabled = rule.isEnabled
  showEditModal.value = true
}

const deleteRule = async (rule: PushRule) => {
  const typeLabel = rule.anniversaryType ? anniversaryTypeLabel(rule.anniversaryType) : '所有纪念日'
  if (confirm(`确定要删除「${typeLabel}」的推送规则吗？`)) {
    try {
      const response = await apiService.deletePushRule(rule.id)
      if (response.success) {
        const index = pushRules.value.findIndex(r => r.id === rule.id)
        if (index > -1) {
          pushRules.value.splice(index, 1)
        }
      } else {
        alert(`删除失败: ${response.error || '未知错误'}`)
      }
    } catch (error) {
      console.error('删除推送规则失败:', error)
      alert('删除失败')
    }
  }
}

const toggleRuleStatus = async (rule: PushRule) => {
  try {
    const request: UpdatePushRuleRequest = {
      isEnabled: !rule.isEnabled
    }
    const response = await apiService.updatePushRule(rule.id, request)
    if (response.success && response.data) {
      const index = pushRules.value.findIndex(r => r.id === rule.id)
      if (index > -1) {
        pushRules.value[index].isEnabled = !rule.isEnabled
      }
    }
  } catch (error) {
    console.error('更新规则状态失败:', error)
  }
}

const saveRule = async () => {
  if (form.pushChannels.length === 0) {
    alert('请至少选择一个推送渠道')
    return
  }

  try {
    if (showEditModal.value && editingRule.value) {
      const request: UpdatePushRuleRequest = {
        anniversaryType: form.anniversaryType,
        pushChannels: form.pushChannels,
        advanceDays: form.advanceDays,
        pushTime: form.pushTime,
        isEnabled: form.isEnabled
      }

      const response = await apiService.updatePushRule(editingRule.value.id, request)
      if (response.success && response.data) {
        const index = pushRules.value.findIndex(r => r.id === editingRule.value!.id)
        if (index > -1) {
          pushRules.value[index] = response.data
        }
        closeModal()
      } else {
        alert(`更新失败: ${response.error || '未知错误'}`)
      }
    } else {
      const request: CreatePushRuleRequest = {
        anniversaryType: form.anniversaryType,
        pushChannels: form.pushChannels,
        advanceDays: form.advanceDays,
        pushTime: form.pushTime
      }

      const response = await apiService.createPushRule(request)
      if (response.success && response.data) {
        pushRules.value.unshift(response.data)
        closeModal()
      } else {
        alert(`创建失败: ${response.error || '未知错误'}`)
      }
    }
  } catch (error) {
    console.error('保存推送规则失败:', error)
    alert('保存失败')
  }
}

onMounted(() => {
  loadPushRules()
})
</script>
