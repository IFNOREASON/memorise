<template>
  <div class="min-h-screen paper-texture">
    <header class="sticky top-0 z-50 glass-warm border-b border-[#E8D5C4]">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button @click="$router.back()" class="w-10 h-10 rounded-full hover:bg-[#E8D5C4] flex items-center justify-center transition-colors">
            <Icon icon="solar:arrow-left-bold" class="text-[#8B6F4E]" />
          </button>
          <div>
            <h1 class="text-xl font-bold text-[#5C4A3A] font-serif tracking-wider">纪念日管理</h1>
            <p class="text-xs text-gray-500">管理家族重要日期</p>
          </div>
        </div>
        <button @click="showCreateModal = true" class="px-4 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all flex items-center space-x-2">
          <Icon icon="solar:add-circle-bold" class="text-sm" />
          <span>添加纪念日</span>
        </button>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-6">
      <div class="flex border-b border-[#E8D5C4] mb-6">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-6 py-3 text-sm font-medium transition-colors relative',
            activeTab === tab.id ? 'text-[#8B6F4E]' : 'text-gray-500 hover:text-gray-700'
          ]">
          <span class="flex items-center space-x-2">
            <Icon :icon="tab.icon" class="text-lg" />
            <span>{{ tab.label }}</span>
          </span>
          <div v-if="activeTab === tab.id" class="absolute bottom-0 left-0 right-0 h-0.5 bg-[#8B6F4E]"></div>
        </button>
      </div>

      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center space-x-4">
          <select v-model="filterType" class="px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
            <option value="">全部类型</option>
            <option value="birthday">生日</option>
            <option value="deathday">忌日</option>
            <option value="weddingday">结婚日</option>
            <option value="sacrificialday">祭祀日</option>
          </select>
          <div class="relative">
            <Icon icon="solar:search-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input v-model="searchKeyword" type="text" placeholder="搜索纪念日名称..." 
              class="pl-10 pr-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4] w-64" />
          </div>
        </div>
        <select v-model="filterActive" class="px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
          <option value="">全部状态</option>
          <option :value="true">启用</option>
          <option :value="false">停用</option>
        </select>
      </div>

      <div v-if="filteredAnniversaries.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="anniversary in filteredAnniversaries" :key="anniversary.id" 
          class="bg-white rounded-2xl shadow-soft border border-stone-100 p-5 hover:shadow-md transition-shadow">
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-start space-x-3">
              <div class="w-12 h-12 rounded-xl flex items-center justify-center"
                :class="anniversaryTypeBg(anniversary.type)">
                <Icon :icon="anniversaryTypeIcon(anniversary.type)" class="text-xl" :class="anniversaryTypeText(anniversary.type)" />
              </div>
              <div>
                <p class="font-bold text-[#5C4A3A]">{{ anniversary.name }}</p>
                <p class="text-sm text-gray-500">{{ anniversaryTypeLabel(anniversary.type) }}</p>
              </div>
            </div>
            <div class="flex items-center space-x-1">
              <button @click="editAnniversary(anniversary)" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
                <Icon icon="solar:pen-bold" class="text-gray-500 text-sm" />
              </button>
              <button @click="deleteAnniversary(anniversary)" class="w-8 h-8 rounded-full hover:bg-red-50 flex items-center justify-center transition-colors">
                <Icon icon="solar:trash-bin-trash-bold" class="text-red-500 text-sm" />
              </button>
            </div>
          </div>

          <div class="space-y-2 text-sm">
            <div class="flex items-center justify-between">
              <span class="text-gray-500">日期</span>
              <span class="font-medium text-[#5C4A3A]">
                {{ anniversary.year ? anniversary.year + '年' : '' }}{{ anniversary.month }}月{{ anniversary.day }}日
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-500">重复</span>
              <span class="font-medium text-[#5C4A3A]">{{ repeatTypeLabel(anniversary.repeatType) }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-500">阴历</span>
              <span class="font-medium text-[#5C4A3A]">{{ anniversary.isLunar ? '是' : '否' }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-500">状态</span>
              <span class="px-2 py-0.5 rounded-full text-xs font-medium"
                :class="anniversary.isActive ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'">
                {{ anniversary.isActive ? '启用' : '停用' }}
              </span>
            </div>
          </div>

          <div v-if="anniversary.description" class="mt-4 pt-4 border-t border-gray-100">
            <p class="text-sm text-gray-500 line-clamp-2">{{ anniversary.description }}</p>
          </div>
        </div>
      </div>

      <div v-else class="bg-white rounded-2xl shadow-soft border border-stone-100 p-12 text-center">
        <Icon icon="solar:calendar-bold" class="text-6xl text-gray-300 mx-auto mb-4" />
        <p class="text-gray-500 mb-2">暂无纪念日数据</p>
        <p class="text-gray-400 text-sm mb-4">点击上方按钮添加第一个纪念日</p>
        <button @click="showCreateModal = true" class="px-4 py-2 bg-[#8B6F4E] text-white rounded-xl text-sm font-medium hover:bg-[#A67B5B] transition-colors">
          添加纪念日
        </button>
      </div>
    </main>

    <div v-if="showCreateModal || showEditModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="border-b border-stone-100 px-6 py-4 flex items-center justify-between sticky top-0 bg-white">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">
            {{ showEditModal ? '编辑纪念日' : '添加纪念日' }}
          </h3>
          <button @click="closeModal" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="material-symbols:close" class="text-gray-500" />
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">纪念日名称 *</label>
            <input v-model="form.name" type="text" placeholder="例如：爷爷生日"
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">纪念日类型 *</label>
            <div class="grid grid-cols-4 gap-2">
              <div v-for="type in anniversaryTypes" :key="type.value"
                @click="form.type = type.value"
                class="flex items-center justify-center space-x-2 p-3 rounded-xl cursor-pointer transition-all border-2"
                :class="[
                  form.type === type.value ? 'border-[#8B6F4E] bg-[#E8D5C4]' : 'border-transparent bg-[#FAF7F2] hover:border-[#E8D5C4]'
                ]">
                <Icon :icon="anniversaryTypeIcon(type.value)" class="text-sm"
                  :class="form.type === type.value ? anniversaryTypeText(type.value) : 'text-gray-500'" />
                <span class="text-sm" :class="form.type === type.value ? 'text-[#8B6F4E] font-medium' : 'text-gray-600'">
                  {{ type.label }}
                </span>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">日期 *</label>
              <input v-model="form.date" type="text" placeholder="YYYY-MM-DD 或 MM-DD"
                class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
              <p class="text-xs text-gray-400 mt-1">格式：1990-05-15 或 05-15</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">重复类型</label>
              <select v-model="form.repeatType" class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
                <option value="yearly">每年</option>
                <option value="monthly">每月</option>
                <option value="once">一次</option>
              </select>
            </div>
          </div>

          <div class="flex items-center space-x-6">
            <label class="flex items-center space-x-2 cursor-pointer">
              <input v-model="form.isLunar" type="checkbox" class="w-4 h-4 rounded text-[#8B6F4E] focus:ring-[#8B6F4E]" />
              <span class="text-sm text-gray-700">阴历日期</span>
            </label>
            <label class="flex items-center space-x-2 cursor-pointer">
              <input v-model="form.isActive" type="checkbox" class="w-4 h-4 rounded text-[#8B6F4E] focus:ring-[#8B6F4E]" />
              <span class="text-sm text-gray-700">启用提醒</span>
            </label>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">描述</label>
            <textarea v-model="form.description" rows="3" placeholder="添加备注信息（可选）"
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4] resize-none"></textarea>
          </div>
        </div>
        <div class="border-t border-stone-100 px-6 py-4 flex justify-end space-x-3 sticky bottom-0 bg-white">
          <button @click="closeModal" class="px-6 py-2 text-gray-600 bg-gray-100 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors">
            取消
          </button>
          <button @click="saveAnniversary" class="px-6 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all">
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { 
  apiService, 
  Anniversary,
  AnniversaryType,
  RepeatType,
  CreateAnniversaryRequest,
  UpdateAnniversaryRequest
} from '../services/api'

const activeTab = ref<'all' | 'active' | 'inactive'>('all')
const filterType = ref('')
const filterActive = ref<boolean | undefined>(undefined)
const searchKeyword = ref('')

const anniversaries = ref<Anniversary[]>([])

const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingAnniversary = ref<Anniversary | null>(null)

const tabs = computed(() => [
  { id: 'all', label: '全部', icon: 'solar:calendar-bold' },
  { id: 'active', label: '启用', icon: 'solar:check-circle-bold' },
  { id: 'inactive', label: '停用', icon: 'solar:close-circle-bold' }
])

const anniversaryTypes = [
  { value: 'birthday' as AnniversaryType, label: '生日' },
  { value: 'deathday' as AnniversaryType, label: '忌日' },
  { value: 'weddingday' as AnniversaryType, label: '结婚日' },
  { value: 'sacrificialday' as AnniversaryType, label: '祭祀日' }
]

const form = reactive<{
  name: string
  type: AnniversaryType
  date: string
  repeatType: RepeatType
  isLunar: boolean
  isActive: boolean
  description: string
}>({
  name: '',
  type: 'birthday',
  date: '',
  repeatType: 'yearly',
  isLunar: false,
  isActive: true,
  description: ''
})

const filteredAnniversaries = computed(() => {
  let result = anniversaries.value

  if (activeTab.value === 'active') {
    result = result.filter(a => a.isActive)
  } else if (activeTab.value === 'inactive') {
    result = result.filter(a => !a.isActive)
  }

  if (filterType.value) {
    result = result.filter(a => a.type === filterType.value)
  }

  if (filterActive.value !== undefined) {
    result = result.filter(a => a.isActive === filterActive.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(a => 
      a.name.toLowerCase().includes(keyword) ||
      (a.description && a.description.toLowerCase().includes(keyword))
    )
  }

  return result
})

const anniversaryTypeIcon = (type: AnniversaryType): string => {
  const icons: Record<AnniversaryType, string> = {
    birthday: 'solar:cake-birthday-bold',
    deathday: 'solar:cloud-moon-bold',
    weddingday: 'solar:heart-bold',
    sacrificialday: 'solar:stars-bold'
  }
  return icons[type] || 'solar:calendar-bold'
}

const anniversaryTypeLabel = (type: AnniversaryType): string => {
  const labels: Record<AnniversaryType, string> = {
    birthday: '生日',
    deathday: '忌日',
    weddingday: '结婚日',
    sacrificialday: '祭祀日'
  }
  return labels[type] || type
}

const anniversaryTypeBg = (type: AnniversaryType): string => {
  const bgs: Record<AnniversaryType, string> = {
    birthday: 'bg-pink-100',
    deathday: 'bg-gray-100',
    weddingday: 'bg-red-100',
    sacrificialday: 'bg-amber-100'
  }
  return bgs[type] || 'bg-gray-100'
}

const anniversaryTypeText = (type: AnniversaryType): string => {
  const texts: Record<AnniversaryType, string> = {
    birthday: 'text-pink-600',
    deathday: 'text-gray-600',
    weddingday: 'text-red-600',
    sacrificialday: 'text-amber-600'
  }
  return texts[type] || 'text-gray-600'
}

const repeatTypeLabel = (type: RepeatType): string => {
  const labels: Record<RepeatType, string> = {
    yearly: '每年',
    monthly: '每月',
    once: '一次'
  }
  return labels[type] || type
}

const loadAnniversaries = async () => {
  try {
    const response = await apiService.getAnniversaries()
    if (response.success && response.data) {
      anniversaries.value = response.data.anniversaries
    }
  } catch (error) {
    console.error('加载纪念日失败:', error)
  }
}

const resetForm = () => {
  form.name = ''
  form.type = 'birthday'
  form.date = ''
  form.repeatType = 'yearly'
  form.isLunar = false
  form.isActive = true
  form.description = ''
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  editingAnniversary.value = null
  resetForm()
}

const editAnniversary = (anniversary: Anniversary) => {
  editingAnniversary.value = anniversary
  form.name = anniversary.name
  form.type = anniversary.type
  form.date = anniversary.date
  form.repeatType = anniversary.repeatType
  form.isLunar = anniversary.isLunar
  form.isActive = anniversary.isActive
  form.description = anniversary.description || ''
  showEditModal.value = true
}

const deleteAnniversary = async (anniversary: Anniversary) => {
  if (confirm(`确定要删除纪念日「${anniversary.name}」吗？`)) {
    try {
      const response = await apiService.deleteAnniversary(anniversary.id)
      if (response.success) {
        const index = anniversaries.value.findIndex(a => a.id === anniversary.id)
        if (index > -1) {
          anniversaries.value.splice(index, 1)
        }
      } else {
        alert(`删除失败: ${response.error || '未知错误'}`)
      }
    } catch (error) {
      console.error('删除纪念日失败:', error)
      alert('删除失败')
    }
  }
}

const saveAnniversary = async () => {
  if (!form.name.trim()) {
    alert('请输入纪念日名称')
    return
  }
  if (!form.date.trim()) {
    alert('请输入日期')
    return
  }

  try {
    if (showEditModal.value && editingAnniversary.value) {
      const request: UpdateAnniversaryRequest = {
        name: form.name,
        type: form.type,
        date: form.date,
        repeatType: form.repeatType,
        isLunar: form.isLunar,
        isActive: form.isActive,
        description: form.description || undefined
      }

      const response = await apiService.updateAnniversary(editingAnniversary.value.id, request)
      if (response.success && response.data) {
        const index = anniversaries.value.findIndex(a => a.id === editingAnniversary.value!.id)
        if (index > -1) {
          anniversaries.value[index] = response.data
        }
        closeModal()
      } else {
        alert(`更新失败: ${response.error || '未知错误'}`)
      }
    } else {
      const request: CreateAnniversaryRequest = {
        name: form.name,
        type: form.type,
        date: form.date,
        repeatType: form.repeatType,
        isLunar: form.isLunar
      }

      const response = await apiService.createAnniversary(request)
      if (response.success && response.data) {
        anniversaries.value.unshift(response.data)
        closeModal()
      } else {
        alert(`创建失败: ${response.error || '未知错误'}`)
      }
    }
  } catch (error) {
    console.error('保存纪念日失败:', error)
    alert('保存失败')
  }
}

onMounted(() => {
  loadAnniversaries()
})
</script>
