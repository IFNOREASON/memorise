<template>
  <div class="min-h-screen paper-texture flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center mb-4">
          <div class="w-16 h-16 bg-[#C84A3E] rounded-sm flex items-center justify-center shadow-md relative overflow-hidden">
            <span class="text-white font-serif text-2xl font-bold tracking-widest relative z-10">存</span>
          </div>
        </div>
        <h1 class="text-3xl font-bold text-[#5C4A3A] font-serif tracking-wider">memorise</h1>
        <p class="text-sm text-gray-500 tracking-[0.15em] uppercase font-medium mt-1">Family Memorial</p>
      </div>

      <div class="bg-white rounded-2xl shadow-soft border border-stone-100 p-8">
        <h2 class="text-xl font-bold text-[#5C4A3A] font-serif mb-6 text-center">修改密码</h2>

        <form @submit.prevent="handleChangePassword" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">原密码</label>
            <div class="relative">
              <Icon icon="solar:lock-password-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg" />
              <input
                v-model="form.currentPassword"
                :type="showCurrentPassword ? 'text' : 'password'"
                placeholder="请输入原密码"
                class="w-full pl-10 pr-12 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent transition-all bg-[#FAF7F2] placeholder-gray-400"
                required
              />
              <button
                type="button"
                @click="showCurrentPassword = !showCurrentPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <Icon :icon="showCurrentPassword ? 'solar:eye-bold' : 'solar:eye-closed-bold'" class="text-lg" />
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">新密码</label>
            <div class="relative">
              <Icon icon="solar:lock-password-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg" />
              <input
                v-model="form.newPassword"
                :type="showNewPassword ? 'text' : 'password'"
                placeholder="请输入新密码"
                class="w-full pl-10 pr-12 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent transition-all bg-[#FAF7F2] placeholder-gray-400"
                required
              />
              <button
                type="button"
                @click="showNewPassword = !showNewPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <Icon :icon="showNewPassword ? 'solar:eye-bold' : 'solar:eye-closed-bold'" class="text-lg" />
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">确认新密码</label>
            <div class="relative">
              <Icon icon="solar:lock-password-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg" />
              <input
                v-model="form.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="请再次输入新密码"
                class="w-full pl-10 pr-12 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent transition-all bg-[#FAF7F2] placeholder-gray-400"
                required
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <Icon :icon="showConfirmPassword ? 'solar:eye-bold' : 'solar:eye-closed-bold'" class="text-lg" />
              </button>
            </div>
          </div>

          <div v-if="error" class="text-red-500 text-sm text-center py-2 bg-red-50 rounded-lg">
            {{ error }}
          </div>

          <div v-if="success" class="text-green-500 text-sm text-center py-2 bg-green-50 rounded-lg">
            {{ success }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white font-medium rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <Icon v-if="loading" icon="solar:refresh-circle-bold" class="animate-spin mr-2" />
            {{ loading ? '修改中...' : '确认修改' }}
          </button>
        </form>

        <div class="mt-6 text-center">
          <router-link to="/" class="text-sm text-gray-400 hover:text-gray-600 flex items-center justify-center">
            <Icon icon="solar:arrow-left-linear" class="mr-1" />
            返回首页
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import { apiService, authStore, type ChangePasswordRequest } from '../services/api'

const router = useRouter()

const form = ref<ChangePasswordRequest>({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const error = ref('')
const success = ref('')

const handleChangePassword = async () => {
  if (!form.value.currentPassword || !form.value.newPassword || !form.value.confirmPassword) {
    error.value = '请填写所有密码字段'
    return
  }

  if (form.value.newPassword !== form.value.confirmPassword) {
    error.value = '两次输入的新密码不一致'
    return
  }

  if (form.value.newPassword.length < 6) {
    error.value = '新密码长度至少为6位'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    const result = await apiService.changePassword(form.value)
    if (result.success) {
      success.value = '密码修改成功，正在跳转到登录页面...'
      authStore.clearAuth()
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    } else {
      error.value = result.error || '密码修改失败'
    }
  } catch (e) {
    error.value = '修改密码时发生错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>
