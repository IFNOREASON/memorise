<template>
  <div class="min-h-screen paper-texture">
    <header class="sticky top-0 z-50 glass-warm border-b border-[#E8D5C4]">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button @click="$router.back()" class="w-10 h-10 rounded-full hover:bg-[#E8D5C4] flex items-center justify-center transition-colors">
            <Icon icon="solar:arrow-left-bold" class="text-[#8B6F4E]" />
          </button>
          <div>
            <h1 class="text-xl font-bold text-[#5C4A3A] font-serif tracking-wider">纪念日历</h1>
            <p class="text-xs text-gray-500">家族重要日期提醒</p>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <button @click="prevMonth" class="w-10 h-10 rounded-full hover:bg-[#E8D5C4] flex items-center justify-center transition-colors">
            <Icon icon="solar:arrow-left-bold" class="text-[#8B6F4E]" />
          </button>
          <button @click="goToToday" class="px-4 py-2 bg-[#E8D5C4] text-[#8B6F4E] rounded-lg text-sm font-medium hover:bg-[#D4C4B0] transition-colors">
            今天
          </button>
          <button @click="nextMonth" class="w-10 h-10 rounded-full hover:bg-[#E8D5C4] flex items-center justify-center transition-colors">
            <Icon icon="solar:arrow-right-bold" class="text-[#8B6F4E]" />
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-6">
      <div class="mb-6 text-center">
        <h2 class="text-2xl font-bold text-[#5C4A3A] font-serif">
          {{ currentYear }}年 {{ currentMonth }}月
        </h2>
      </div>

      <div v-if="upcomingAnniversaries.length > 0" class="mb-6">
        <div class="bg-gradient-to-r from-[#FAF7F2] to-[#F5EDE4] rounded-2xl shadow-soft border border-[#E8D5C4] p-6">
          <h3 class="text-lg font-bold text-[#8B6F4E] mb-4 flex items-center space-x-2">
            <Icon icon="solar:bell-bold" class="text-[#C84A3E]" />
            <span>即将到来的纪念日</span>
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="item in upcomingAnniversaries" :key="item.id" 
              class="bg-white rounded-xl p-4 shadow-sm border border-[#E8D5C4] hover:shadow-md transition-shadow cursor-pointer"
              @click="showAnniversaryDetail(item)">
              <div class="flex items-start space-x-3">
                <div class="w-12 h-12 rounded-xl flex items-center justify-center"
                  :class="anniversaryTypeBg(item.type)">
                  <Icon :icon="anniversaryTypeIcon(item.type)" class="text-xl" :class="anniversaryTypeText(item.type)" />
                </div>
                <div class="flex-1 min-w-0">
                  <p class="font-medium text-[#5C4A3A] truncate">{{ item.name }}</p>
                  <p class="text-sm text-gray-500">{{ anniversaryTypeLabel(item.type) }}</p>
                  <p class="text-xs text-[#8B6F4E] mt-1">{{ item.month }}月{{ item.day }}日</p>
                </div>
              </div>
              <div v-if="item.memberName" class="mt-2 pt-2 border-t border-gray-100">
                <p class="text-xs text-gray-400">关联成员: {{ item.memberName }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl shadow-soft border border-stone-100 overflow-hidden">
        <div class="grid grid-cols-7 bg-[#FAF7F2] border-b border-[#E8D5C4]">
          <div v-for="day in weekDays" :key="day" 
            class="py-3 text-center text-sm font-medium"
            :class="isWeekend(day) ? 'text-[#C84A3E]' : 'text-gray-600'">
            {{ day }}
          </div>
        </div>

        <div class="grid grid-cols-7">
          <template v-for="(week, weekIndex) in calendarDays" :key="weekIndex">
            <div v-for="(day, dayIndex) in week" :key="dayIndex"
              class="min-h-28 border-b border-r border-stone-100 p-1 cursor-pointer hover:bg-[#FAF7F2] transition-colors"
              :class="{ 'bg-gray-50': !day.inCurrentMonth }">
              <div class="flex items-center justify-between mb-1">
                <span class="text-sm"
                  :class="[
                    isToday(day) ? 'bg-[#8B6F4E] text-white w-6 h-6 rounded-full flex items-center justify-center' : '',
                    !day.inCurrentMonth ? 'text-gray-300' : 'text-gray-700',
                    isWeekendByIndex(dayIndex) && day.inCurrentMonth ? 'text-[#C84A3E]' : ''
                  ]">
                  {{ day.day }}
                </span>
              </div>
              <div class="space-y-1">
                <div v-for="item in day.anniversaries" :key="item.id"
                  class="text-xs p-1 rounded truncate cursor-pointer hover:opacity-80 transition-opacity"
                  :class="anniversaryTypeBg(item.type)"
                  @click.stop="showAnniversaryDetail(item)">
                  <span :class="anniversaryTypeText(item.type)">{{ item.name }}</span>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <div class="mt-6 flex items-center justify-center space-x-6">
        <div v-for="type in anniversaryTypes" :key="type.value" class="flex items-center space-x-2">
          <div class="w-3 h-3 rounded" :class="anniversaryTypeBg(type.value)"></div>
          <span class="text-sm text-gray-600">{{ type.label }}</span>
        </div>
      </div>
    </main>

    <div v-if="showDetailModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div class="border-b border-stone-100 px-6 py-4 flex items-center justify-between">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">纪念日详情</h3>
          <button @click="closeDetailModal" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="material-symbols:close" class="text-gray-500" />
          </button>
        </div>
        <div class="p-6" v-if="selectedAnniversary">
          <div class="flex items-center space-x-4 mb-6">
            <div class="w-16 h-16 rounded-2xl flex items-center justify-center"
              :class="anniversaryTypeBg(selectedAnniversary.type)">
              <Icon :icon="anniversaryTypeIcon(selectedAnniversary.type)" class="text-3xl" :class="anniversaryTypeText(selectedAnniversary.type)" />
            </div>
            <div>
              <p class="text-xl font-bold text-[#5C4A3A]">{{ selectedAnniversary.name }}</p>
              <p class="text-sm text-gray-500">{{ anniversaryTypeLabel(selectedAnniversary.type) }}</p>
              <p class="text-sm text-[#8B6F4E] mt-1">{{ selectedAnniversary.month }}月{{ selectedAnniversary.day }}日</p>
            </div>
          </div>

          <div class="space-y-3">
            <div class="flex items-center justify-between py-2 border-b border-gray-100">
              <span class="text-sm text-gray-500">日期</span>
              <span class="text-sm font-medium text-[#5C4A3A]">
                {{ selectedAnniversary.year ? selectedAnniversary.year + '年' : '' }}{{ selectedAnniversary.month }}月{{ selectedAnniversary.day }}日
              </span>
            </div>
            <div class="flex items-center justify-between py-2 border-b border-gray-100">
              <span class="text-sm text-gray-500">阴历</span>
              <span class="text-sm font-medium text-[#5C4A3A]">
                {{ selectedAnniversary.isLunar ? '是' : '否' }}
              </span>
            </div>
            <div v-if="selectedAnniversary.memberName" class="flex items-center justify-between py-2 border-b border-gray-100">
              <span class="text-sm text-gray-500">关联成员</span>
              <span class="text-sm font-medium text-[#5C4A3A]">{{ selectedAnniversary.memberName }}</span>
            </div>
            <div v-if="selectedAnniversary.description" class="py-2">
              <span class="text-sm text-gray-500 block mb-1">描述</span>
              <p class="text-sm text-[#5C4A3A]">{{ selectedAnniversary.description }}</p>
            </div>
          </div>
        </div>
        <div class="border-t border-stone-100 px-6 py-4 flex justify-end">
          <button @click="closeDetailModal" class="px-6 py-2 bg-[#8B6F4E] text-white rounded-xl text-sm font-medium hover:bg-[#A67B5B] transition-colors">
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Icon } from '@iconify/vue'
import { 
  apiService, 
  AnniversaryCalendarItem,
  AnniversaryType
} from '../services/api'

const currentDate = ref(new Date())
const currentYear = computed(() => currentDate.value.getFullYear())
const currentMonth = computed(() => currentDate.value.getMonth() + 1)

const weekDays = ['日', '一', '二', '三', '四', '五', '六']
const anniversaryTypes = [
  { value: 'birthday' as AnniversaryType, label: '生日' },
  { value: 'deathday' as AnniversaryType, label: '忌日' },
  { value: 'weddingday' as AnniversaryType, label: '结婚日' },
  { value: 'sacrificialday' as AnniversaryType, label: '祭祀日' }
]

const calendarAnniversaries = ref<AnniversaryCalendarItem[]>([])
const upcomingAnniversaries = ref<AnniversaryCalendarItem[]>([])

const showDetailModal = ref(false)
const selectedAnniversary = ref<AnniversaryCalendarItem | null>(null)

interface CalendarDay {
  day: number
  inCurrentMonth: boolean
  anniversaries: AnniversaryCalendarItem[]
}

const calendarDays = computed<CalendarDay[][]>(() => {
  const year = currentYear.value
  const month = currentMonth.value - 1
  
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const prevLastDay = new Date(year, month, 0)
  
  const firstDayOfWeek = firstDay.getDay()
  const lastDate = lastDay.getDate()
  const prevLastDate = prevLastDay.getDate()
  
  const weeks: CalendarDay[][] = []
  let currentWeek: CalendarDay[] = []
  
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    currentWeek.push({
      day: prevLastDate - i,
      inCurrentMonth: false,
      anniversaries: []
    })
  }
  
  for (let i = 1; i <= lastDate; i++) {
    const dayAnniversaries = calendarAnniversaries.value.filter(
      item => item.month === currentMonth.value && item.day === i
    )
    
    currentWeek.push({
      day: i,
      inCurrentMonth: true,
      anniversaries: dayAnniversaries
    })
    
    if (currentWeek.length === 7) {
      weeks.push(currentWeek)
      currentWeek = []
    }
  }
  
  if (currentWeek.length > 0) {
    const remaining = 7 - currentWeek.length
    for (let i = 1; i <= remaining; i++) {
      currentWeek.push({
        day: i,
        inCurrentMonth: false,
        anniversaries: []
      })
    }
    weeks.push(currentWeek)
  }
  
  return weeks
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

const isWeekend = (day: string): boolean => {
  return day === '日' || day === '六'
}

const isWeekendByIndex = (index: number): boolean => {
  return index === 0 || index === 6
}

const isToday = (day: CalendarDay): boolean => {
  if (!day.inCurrentMonth) return false
  const today = new Date()
  return today.getFullYear() === currentYear.value &&
         today.getMonth() + 1 === currentMonth.value &&
         today.getDate() === day.day
}

const prevMonth = () => {
  currentDate.value = new Date(currentYear.value, currentMonth.value - 2, 1)
}

const nextMonth = () => {
  currentDate.value = new Date(currentYear.value, currentMonth.value, 1)
}

const goToToday = () => {
  currentDate.value = new Date()
}

const loadCalendarData = async () => {
  try {
    const [calendarResp, upcomingResp] = await Promise.all([
      apiService.getAnniversariesCalendar(currentYear.value, currentMonth.value),
      apiService.getUpcomingAnniversaries(7)
    ])
    
    if (calendarResp.success && calendarResp.data) {
      calendarAnniversaries.value = calendarResp.data.items
    }
    
    if (upcomingResp.success && upcomingResp.data) {
      upcomingAnniversaries.value = upcomingResp.data
    }
  } catch (error) {
    console.error('加载日历数据失败:', error)
  }
}

const showAnniversaryDetail = (item: AnniversaryCalendarItem) => {
  selectedAnniversary.value = item
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedAnniversary.value = null
}

onMounted(() => {
  loadCalendarData()
})

watch([currentYear, currentMonth], () => {
  loadCalendarData()
})
</script>
