<template>
  <div class="min-h-screen paper-texture">
    <header class="sticky top-0 z-50 glass-warm border-b border-[#E8D5C4]">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 bg-[#C84A3E] rounded-sm flex items-center justify-center shadow-md relative overflow-hidden">
            <div class="absolute inset-0 opacity-30" :style="noisePatternStyle"></div>
            <span class="text-white font-serif text-xl font-bold tracking-widest relative z-10">存</span>
          </div>
          <div>
            <h1 class="text-2xl font-bold text-[#5C4A3A] font-serif tracking-wider">memorise</h1>
            <p class="text-xs text-gray-500 tracking-[0.15em] uppercase font-medium">Family Memorial</p>
          </div>
        </div>

        <nav class="hidden lg:flex items-center space-x-8">
          <button v-for="item in navItems" :key="item.id"
            class="flex items-center space-x-2 px-3 py-2 rounded-lg transition-all hover:bg-[#E8D5C4]/50"
            :class="[
              activeNav === item.id ? 'bg-[#E8D5C4] text-[#8B6F4E]' : 'text-gray-600'
            ]"
            @click="handleNavClick(item.id)">
            <Icon :icon="item.icon" class="text-lg" />
            <span class="font-medium text-sm">{{ item.label }}</span>
          </button>
        </nav>

        <div class="flex items-center space-x-4">
          <button @click="goToMessages" class="relative w-10 h-10 rounded-full bg-white/80 flex items-center justify-center shadow-sm hover:shadow-md transition-shadow">
            <Icon icon="solar:bell-bold" class="text-gray-600" />
            <span v-if="unreadMessageCount > 0" class="absolute -top-1 -right-1 w-5 h-5 bg-[#C84A3E] text-white text-xs font-bold rounded-full flex items-center justify-center">
              {{ unreadMessageCount > 99 ? '99+' : unreadMessageCount }}
            </span>
          </button>
          <div class="relative flex items-center space-x-3 pl-4 border-l border-[#E8D5C4]">
            <button 
              @click="toggleUserMenu"
              class="flex items-center space-x-3 focus:outline-none"
            >
              <div class="w-10 h-10 rounded-full bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] p-0.5">
                <div class="w-full h-full rounded-full bg-gray-200 overflow-hidden">
                  <img 
                    :src="authStore.user?.avatarUrl || 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face'" 
                    class="w-full h-full object-cover" 
                    alt="用户头像"
                  >
                </div>
              </div>
              <div class="hidden md:block text-left">
                <p class="text-sm font-semibold text-gray-800">{{ authStore.user?.nickname || authStore.user?.username || '用户' }}</p>
                <p class="text-xs text-gray-500">{{ authStore.isAuthenticated ? '已登录' : '未登录' }}</p>
              </div>
              <Icon 
                icon="solar:alt-arrow-down-linear" 
                class="text-gray-400 text-sm transition-transform"
                :class="{ 'rotate-180': showUserMenu }"
              />
            </button>

            <div 
              v-if="showUserMenu"
              class="absolute right-0 top-full mt-2 w-48 bg-white rounded-xl shadow-lg border border-[#E8D5C4] py-2 z-50"
            >
              <template v-if="authStore.isAuthenticated">
                <button
                  @click="handleChangePassword"
                  class="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-[#FAF7F2] flex items-center space-x-3 transition-colors"
                >
                  <Icon icon="solar:lock-password-bold" class="text-[#8B6F4E]" />
                  <span>修改密码</span>
                </button>
                <div class="border-t border-[#E8D5C4] my-1"></div>
                <button
                  @click="handleLogout"
                  class="w-full px-4 py-3 text-left text-sm text-red-500 hover:bg-red-50 flex items-center space-x-3 transition-colors"
                >
                  <Icon icon="solar:logout-3-bold" />
                  <span>退出登录</span>
                </button>
              </template>
              <template v-else>
                <button
                  @click="handleLogin"
                  class="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-[#FAF7F2] flex items-center space-x-3 transition-colors"
                >
                  <Icon icon="solar:login-3-bold" class="text-[#8B6F4E]" />
                  <span>登录</span>
                </button>
                <button
                  @click="handleRegister"
                  class="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-[#FAF7F2] flex items-center space-x-3 transition-colors"
                >
                  <Icon icon="solar:user-add-bold" class="text-[#8B6F4E]" />
                  <span>注册</span>
                </button>
              </template>
            </div>
          </div>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto px-6 py-8">
      <section class="relative mb-10">
        <div class="absolute top-10 right-10 w-64 h-64 bg-[#E8D5C4] rounded-full blur-3xl opacity-40"></div>
        <div class="absolute bottom-0 left-0 w-48 h-48 bg-[#D4A574] rounded-full blur-2xl opacity-20"></div>
        
        <div class="relative bg-gradient-to-br from-[#8B6F4E] to-[#6B5342] rounded-[32px] p-8 lg:p-12 text-white shadow-warm overflow-hidden">
          <div class="absolute inset-0 opacity-10" :style="dotPatternStyle"></div>
          
          <div class="relative z-10 flex flex-col lg:flex-row items-center justify-between gap-8">
            <div class="flex-1">
              <div class="flex items-center space-x-3 mb-6">
                <span class="px-4 py-2 bg-white/20 backdrop-blur rounded-full text-sm font-medium border border-white/10">
                  家族精神纪念馆
                </span>
                <span class="w-3 h-3 bg-green-400 rounded-full animate-pulse"></span>
              </div>
              
              <h2 class="text-4xl lg:text-5xl font-serif font-medium leading-relaxed mb-4">
                数字生命<br>
                <span class="text-[#E8D5C4]">世代相传</span>
              </h2>
              
              <p class="text-base text-white/80 leading-relaxed mb-8 max-w-xl">
                打破时空限制，让逝去的亲人"可陪伴"、家族智慧"可传承"、思念情感"可寄托"。通过 AI 技术，让家族精神永远延续。
              </p>
              
              <div class="flex items-center space-x-12">
                <div class="text-center">
                  <p class="text-3xl font-bold">128</p>
                  <p class="text-sm text-white/60 mt-1">家族成员</p>
                </div>
                <div class="text-center">
                  <p class="text-3xl font-bold">56</p>
                  <p class="text-sm text-white/60 mt-1">珍贵影像</p>
                </div>
                <div class="text-center">
                  <p class="text-3xl font-bold">3</p>
                  <p class="text-sm text-white/60 mt-1">数字生命</p>
                </div>
              </div>
            </div>
            
            <div class="w-64 h-64 lg:w-80 lg:h-80 relative">
              <div class="absolute inset-0 bg-[#E8D5C4]/20 rounded-full animate-pulse"></div>
              <div class="absolute inset-4 bg-[#E8D5C4]/10 rounded-full animate-slow-spin"></div>
              <div class="absolute inset-8 bg-[#E8D5C4]/5 rounded-full animate-float"></div>
              <div class="absolute inset-0 flex items-center justify-center">
                <Icon icon="solar:tree-bold" class="text-white text-9xl opacity-30" />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="mb-10">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-[#5C4A3A] font-serif">五大传承模块</h3>
        </div>
        
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div v-for="module in modules" :key="module.id"
            class="group cursor-pointer"
            :class="[
              module.highlight 
                ? 'bg-gradient-to-br from-[#8B6F4E] to-[#A67B5B] shadow-glow border-2 border-white' 
                : 'bg-white shadow-soft border border-stone-100 hover-lift'
            ]"
            @click="handleModuleClick(module.id)">
            <div class="p-6 rounded-2xl text-center relative">
              <div v-if="module.highlight" class="absolute -top-2 -right-2 w-4 h-4 bg-red-500 rounded-full border-2 border-white"></div>
              
              <div class="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-3"
                   :class="[
                     module.highlight 
                       ? 'bg-white/20' 
                       : 'bg-[#E8D5C4]'
                   ]">
                <Icon :icon="module.icon" 
                      :class="[
                        module.highlight ? 'text-white' : module.color || 'text-[#8B6F4E]'
                      ]"
                      class="text-2xl" />
              </div>
              
              <span class="block font-bold text-sm"
                    :class="[
                      module.highlight ? 'text-white' : 'text-[#5C4A3A]'
                    ]">
                {{ module.label }}
              </span>
              <span class="block text-xs mt-1"
                    :class="[
                      module.highlight ? 'text-[#E8D5C4]' : 'text-gray-400'
                    ]">
                {{ module.subLabel }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <section class="mb-10">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-[#5C4A3A] font-serif">我的数字家人</h3>
          <button class="text-sm text-[#8B6F4E] font-medium flex items-center hover:underline">
            查看全部
            <Icon icon="material-symbols:chevron-right" class="ml-1" />
          </button>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="member in digitalFamily" :key="member.id"
            class="bg-white rounded-2xl p-5 shadow-soft border border-stone-100 hover-lift cursor-pointer">
            <div class="flex items-start space-x-4">
              <div class="relative">
                <div class="w-16 h-16 rounded-full p-0.5"
                     :class="[
                       member.status === 'active' 
                         ? 'bg-gradient-to-br from-[#E8D5C4] to-[#D4A574]' 
                         : 'bg-gradient-to-br from-gray-200 to-gray-300'
                     ]">
                  <div class="w-full h-full rounded-full bg-gray-200 overflow-hidden">
                    <img :src="member.avatar" class="w-full h-full object-cover" 
                         :class="{ 'grayscale': member.status === 'training' }"
                         :alt="member.name">
                  </div>
                </div>
                <div class="absolute bottom-0 right-0 w-5 h-5 rounded-full border-2 border-white flex items-center justify-center"
                     :class="[
                       member.status === 'active' ? 'bg-green-500' : 'bg-amber-400'
                     ]">
                  <Icon :icon="member.status === 'active' ? 'solar:check-bold' : 'solar:pause-bold'" 
                        class="text-white text-xs" />
                </div>
              </div>
              <div class="flex-1">
                <div class="flex items-center space-x-2">
                  <h4 class="font-bold text-gray-800">{{ member.name }}</h4>
                  <span class="px-2 py-0.5 text-[10px] rounded-full"
                        :class="[
                          member.status === 'active' 
                            ? 'bg-[#E8D5C4] text-[#8B6F4E]' 
                            : 'bg-gray-100 text-gray-500'
                        ]">
                    {{ member.status === 'active' ? '已激活' : '训练中' }}
                  </span>
                </div>
                <p class="text-xs text-gray-500 mt-1">{{ member.years }} · 训练度 {{ member.trainingProgress }}%</p>
                
                <template v-if="member.status === 'active'">
                  <div class="flex items-center mt-2 space-x-3">
                    <span class="text-xs text-gray-400 flex items-center">
                      <Icon icon="solar:chat-dots-linear" class="mr-1" style="font-size: 14px;" />
                      {{ member.chatCount }} 对话
                    </span>
                    <span class="text-xs text-gray-400 flex items-center">
                      <Icon icon="solar:clock-circle-linear" class="mr-1" style="font-size: 14px;" />
                      {{ member.lastInteraction }}
                    </span>
                  </div>
                  <button class="mt-3 w-10 h-10 rounded-full bg-[#8B6F4E] flex items-center justify-center shadow-md hover:shadow-lg transition-shadow">
                    <Icon icon="solar:phone-bold" class="text-white text-lg" />
                  </button>
                </template>
                <template v-else>
                  <div class="w-full bg-gray-100 rounded-full h-1.5 mt-3">
                    <div class="bg-amber-400 h-1.5 rounded-full transition-all" 
                         :style="{ width: member.trainingProgress + '%' }"></div>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="bg-white border-t border-[#E8D5C4] py-10">
        <div class="max-w-7xl mx-auto px-6">
          <div class="flex items-center justify-between mb-8">
            <h3 class="text-xl font-bold text-[#5C4A3A] font-serif">家族记忆轴</h3>
            <button class="text-sm text-[#8B6F4E] font-medium flex items-center hover:underline">
              查看全部记忆
              <Icon icon="material-symbols:chevron-right" class="ml-1" />
            </button>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div v-for="(memory, index) in memories" :key="memory.id"
                 class="relative pl-6 md:pl-0">
              <div class="absolute left-0 top-4 w-3 h-3 rounded-full border-2 border-white shadow-sm md:hidden"
                   :class="[
                     index === 0 ? 'bg-[#8B6F4E]' : index === 1 ? 'bg-[#D4A574]' : 'bg-emerald-500'
                   ]"></div>
              
              <div class="bg-[#FAF7F2] rounded-2xl p-5 shadow-soft border border-[#E8D5C4] hover-lift cursor-pointer">
                <div v-if="memory.image" class="mb-4">
                  <div class="photo-frame rounded-lg overflow-hidden bg-gray-100">
                    <img :src="memory.image" class="w-full h-48 object-cover" :alt="memory.title">
                  </div>
                </div>
                <div v-else class="mb-4">
                  <div class="w-12 h-12 rounded-full flex items-center justify-center mb-3"
                       :class="[
                         index === 0 ? 'bg-[#E8D5C4]' : index === 1 ? 'bg-[#F5E6D3]' : 'bg-emerald-50'
                       ]">
                    <Icon :icon="memory.icon" 
                          :class="[
                            index === 0 ? 'text-[#8B6F4E]' : index === 1 ? 'text-[#D4A574]' : 'text-emerald-600'
                          ]"
                          class="text-xl" />
                  </div>
                </div>
                
                <p class="text-xs text-gray-400 mb-2">{{ memory.date }}</p>
                <h4 class="font-bold text-gray-800 mb-2">{{ memory.title }}</h4>
                <p class="text-sm text-gray-500 line-clamp-2">{{ memory.description }}</p>
                
                <div v-if="memory.tags" class="flex items-center mt-3 space-x-2">
                  <span v-for="tag in memory.tags" :key="tag" class="text-xs text-gray-400">
                    {{ tag }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <footer class="bg-[#5C4A3A] text-white py-10">
        <div class="max-w-7xl mx-auto px-6">
          <div class="flex flex-col md:flex-row items-center justify-between">
            <div class="flex items-center space-x-4 mb-6 md:mb-0">
              <div class="w-12 h-12 bg-[#C84A3E] rounded-sm flex items-center justify-center shadow-md">
                <span class="text-white font-serif text-xl font-bold tracking-widest">存</span>
              </div>
              <div>
                <h4 class="text-xl font-bold font-serif tracking-wider">memorise</h4>
                <p class="text-xs text-white/60 tracking-[0.15em] uppercase">Family Memorial</p>
              </div>
            </div>
            
            <div class="text-center">
              <div class="inline-block border-2 border-white/40 text-white/80 px-4 py-2 mb-3 rounded-sm transform -rotate-3">
                <span class="text-sm font-serif font-bold tracking-widest">精神永存</span>
              </div>
              <p class="text-xs text-white/50 tracking-widest uppercase">Digital Life, Eternal Legacy</p>
            </div>
            
            <div class="mt-6 md:mt-0">
              <p class="text-xs text-white/40">© 2024 memorise · 家族精神纪念馆</p>
            </div>
          </div>
        </div>
      </footer>
    </div>

    <Teleport to="body">
      <div 
        v-if="showChangePasswordModal"
        class="fixed inset-0 z-[100] flex items-center justify-center"
      >
        <div 
          class="absolute inset-0 bg-black/50 backdrop-blur-sm"
          @click="closeChangePasswordModal"
        ></div>
        
        <div class="relative w-full max-w-md mx-4 bg-white rounded-2xl shadow-2xl overflow-hidden">
          <div class="bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] px-6 py-4">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-bold text-white font-serif">
                {{ changePasswordStep === 1 ? '验证身份' : '修改密码' }}
              </h3>
              <button 
                @click="closeChangePasswordModal"
                class="text-white/80 hover:text-white transition-colors"
              >
                <Icon icon="solar:close-circle-bold" class="text-xl" />
              </button>
            </div>
            <div class="flex items-center mt-3 space-x-2">
              <div 
                class="flex items-center space-x-2"
                :class="changePasswordStep >= 1 ? 'text-white' : 'text-white/50'"
              >
                <div 
                  class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                  :class="changePasswordStep >= 1 ? 'bg-white text-[#8B6F4E]' : 'bg-white/30'"
                >
                  1
                </div>
                <span class="text-sm">验证原密码</span>
              </div>
              <div class="flex-1 h-0.5 mx-2" 
                   :class="changePasswordStep >= 2 ? 'bg-white' : 'bg-white/30'"></div>
              <div 
                class="flex items-center space-x-2"
                :class="changePasswordStep >= 2 ? 'text-white' : 'text-white/50'"
              >
                <div 
                  class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                  :class="changePasswordStep >= 2 ? 'bg-white text-[#8B6F4E]' : 'bg-white/30'"
                >
                  2
                </div>
                <span class="text-sm">设置新密码</span>
              </div>
            </div>
          </div>

          <div class="p-6">
            <template v-if="changePasswordStep === 1">
              <p class="text-sm text-gray-500 mb-6">请输入您的原密码以验证身份</p>
              
              <div class="space-y-5">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">原密码</label>
                  <div class="relative">
                    <Icon icon="solar:lock-password-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg" />
                    <input
                      v-model="currentPassword"
                      :type="showCurrentPassword ? 'text' : 'password'"
                      placeholder="请输入原密码"
                      class="w-full pl-10 pr-12 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent transition-all bg-[#FAF7F2] placeholder-gray-400"
                      @keyup.enter="verifyCurrentPassword"
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
              </div>
            </template>

            <template v-else-if="changePasswordStep === 2">
              <p class="text-sm text-gray-500 mb-6">请设置您的新密码</p>
              
              <div class="space-y-5">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">新密码</label>
                  <div class="relative">
                    <Icon icon="solar:lock-password-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg" />
                    <input
                      v-model="newPassword"
                      :type="showNewPassword ? 'text' : 'password'"
                      placeholder="请输入新密码"
                      class="w-full pl-10 pr-12 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent transition-all bg-[#FAF7F2] placeholder-gray-400"
                      @keyup.enter="handleConfirmChangePassword"
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
                      v-model="confirmPassword"
                      :type="showConfirmPassword ? 'text' : 'password'"
                      placeholder="请再次输入新密码"
                      class="w-full pl-10 pr-12 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent transition-all bg-[#FAF7F2] placeholder-gray-400"
                      @keyup.enter="handleConfirmChangePassword"
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
              </div>
            </template>

            <div v-if="changePasswordError" class="mt-4 text-red-500 text-sm text-center py-2 bg-red-50 rounded-lg">
              {{ changePasswordError }}
            </div>

            <div v-if="changePasswordSuccess" class="mt-4 text-green-500 text-sm text-center py-2 bg-green-50 rounded-lg">
              {{ changePasswordSuccess }}
            </div>

            <div class="mt-6 flex space-x-3">
              <template v-if="changePasswordStep === 1">
                <button
                  @click="closeChangePasswordModal"
                  class="flex-1 py-3 border border-[#E8D5C4] text-gray-600 font-medium rounded-xl hover:bg-[#FAF7F2] transition-all"
                >
                  取消
                </button>
                <button
                  @click="verifyCurrentPassword"
                  :disabled="changePasswordLoading"
                  class="flex-1 py-3 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white font-medium rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  <Icon v-if="changePasswordLoading" icon="solar:refresh-circle-bold" class="animate-spin mr-2" />
                  {{ changePasswordLoading ? '验证中...' : '下一步' }}
                </button>
              </template>
              <template v-else-if="changePasswordStep === 2">
                <button
                  @click="goBackToStep1"
                  class="flex-1 py-3 border border-[#E8D5C4] text-gray-600 font-medium rounded-xl hover:bg-[#FAF7F2] transition-all flex items-center justify-center"
                >
                  <Icon icon="solar:arrow-left-linear" class="mr-1" />
                  上一步
                </button>
                <button
                  @click="handleConfirmChangePassword"
                  :disabled="changePasswordLoading"
                  class="flex-1 py-3 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white font-medium rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  <Icon v-if="changePasswordLoading" icon="solar:refresh-circle-bold" class="animate-spin mr-2" />
                  {{ changePasswordLoading ? '修改中...' : '确认修改' }}
                </button>
              </template>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import { authStore, apiService, type ChangePasswordRequest } from '../services/api'

const router = useRouter()

const showUserMenu = ref(false)

const showChangePasswordModal = ref(false)
const changePasswordStep = ref(1)
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const changePasswordLoading = ref(false)
const changePasswordError = ref('')
const changePasswordSuccess = ref('')
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const unreadMessageCount = ref(0)
let messagePollingInterval: number | null = null

const loadUnreadMessageCount = async () => {
  if (!authStore.isAuthenticated) {
    unreadMessageCount.value = 0
    return
  }
  try {
    const response = await apiService.getUnreadCount()
    if (response.success && response.data) {
      unreadMessageCount.value = response.data.count
    }
  } catch (error) {
    console.error('获取未读消息数失败:', error)
  }
}

const goToMessages = () => {
  router.push('/messages')
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const closeUserMenu = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    showUserMenu.value = false
  }
}

const handleChangePassword = () => {
  showUserMenu.value = false
  openChangePasswordModal()
}

const openChangePasswordModal = () => {
  showChangePasswordModal.value = true
  changePasswordStep.value = 1
  currentPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
  changePasswordError.value = ''
  changePasswordSuccess.value = ''
  changePasswordLoading.value = false
  showCurrentPassword.value = false
  showNewPassword.value = false
  showConfirmPassword.value = false
}

const closeChangePasswordModal = () => {
  showChangePasswordModal.value = false
  changePasswordStep.value = 1
  currentPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
  changePasswordError.value = ''
  changePasswordSuccess.value = ''
  changePasswordLoading.value = false
}

const verifyCurrentPassword = async () => {
  if (!currentPassword.value) {
    changePasswordError.value = '请输入原密码'
    return
  }

  changePasswordLoading.value = true
  changePasswordError.value = ''

  try {
    const result = await apiService.verifyPassword(currentPassword.value)
    if (result.success) {
      changePasswordStep.value = 2
      changePasswordError.value = ''
    } else {
      changePasswordError.value = result.error || '密码错误'
    }
  } catch (e) {
    changePasswordError.value = '验证密码时发生错误，请稍后重试'
  } finally {
    changePasswordLoading.value = false
  }
}

const handleConfirmChangePassword = async () => {
  if (!newPassword.value || !confirmPassword.value) {
    changePasswordError.value = '请填写所有密码字段'
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    changePasswordError.value = '两次输入的新密码不一致'
    return
  }

  if (newPassword.value.length < 6) {
    changePasswordError.value = '新密码长度至少为6位'
    return
  }

  changePasswordLoading.value = true
  changePasswordError.value = ''

  try {
    const request: ChangePasswordRequest = {
      currentPassword: currentPassword.value,
      newPassword: newPassword.value,
      confirmPassword: confirmPassword.value
    }

    const result = await apiService.changePassword(request)
    if (result.success) {
      changePasswordSuccess.value = '密码修改成功，请重新登录'
      changePasswordError.value = ''
      
      setTimeout(() => {
        authStore.clearAuth()
        closeChangePasswordModal()
        router.push('/login')
      }, 2000)
    } else {
      changePasswordError.value = result.error || '密码修改失败'
    }
  } catch (e) {
    changePasswordError.value = '修改密码时发生错误，请稍后重试'
  } finally {
    changePasswordLoading.value = false
  }
}

const goBackToStep1 = () => {
  changePasswordStep.value = 1
  newPassword.value = ''
  confirmPassword.value = ''
  changePasswordError.value = ''
  changePasswordSuccess.value = ''
}

const handleLogout = () => {
  showUserMenu.value = false
  authStore.clearAuth()
  router.push('/login')
}

const handleLogin = () => {
  showUserMenu.value = false
  router.push('/login')
}

const handleRegister = () => {
  showUserMenu.value = false
  router.push('/register')
}

onMounted(() => {
  document.addEventListener('click', closeUserMenu)
  loadUnreadMessageCount()
  messagePollingInterval = window.setInterval(() => {
    loadUnreadMessageCount()
  }, 60000)
})

onUnmounted(() => {
  document.removeEventListener('click', closeUserMenu)
  if (messagePollingInterval) {
    window.clearInterval(messagePollingInterval)
    messagePollingInterval = null
  }
})

const handleModuleClick = (moduleId: string) => {
  if (moduleId === 'family') {
    router.push('/zupu')
  } else if (moduleId === 'gallery') {
    router.push('/gallery')
  } else if (moduleId === 'digital') {
    router.push('/habitat')
  } else if (moduleId === 'chat') {
    router.push('/chat')
  }
}

const handleNavClick = (navId: string) => {
  activeNav.value = navId
  if (navId === 'home') {
    router.push('/')
  } else if (navId === 'family') {
    router.push('/zupu')
  } else if (navId === 'gallery') {
    router.push('/gallery')
  } else if (navId === 'digital') {
    router.push('/habitat')
  } else if (navId === 'chat') {
    router.push('/chat')
  }
}

interface NavItem {
  id: string
  label: string
  icon: string
}

interface Module {
  id: string
  label: string
  subLabel: string
  icon: string
  highlight: boolean
  color?: string
}

interface DigitalFamilyMember {
  id: string
  name: string
  years: string
  trainingProgress: number
  status: 'active' | 'training'
  avatar: string
  chatCount: string
  lastInteraction: string
}

interface Memory {
  id: string
  date: string
  title: string
  description: string
  image?: string
  icon?: string
  tags?: string[]
}

const activeNav = ref('home')

const navItems: NavItem[] = [
  { id: 'home', label: '首页', icon: 'solar:home-2-bold' },
  { id: 'family', label: '家承', icon: 'solar:tree-bold-duotone' },
  { id: 'gallery', label: '影集', icon: 'solar:gallery-wide-bold-duotone' },
  { id: 'digital', label: '生境', icon: 'solar:magic-stick-3-bold-duotone' },
  { id: 'chat', label: '语伴', icon: 'solar:chat-round-dots-bold-duotone' },
]

const modules: Module[] = [
  { id: 'family', label: '家承', subLabel: '族谱', icon: 'solar:tree-bold-duotone', highlight: false },
  { id: 'gallery', label: '影集', subLabel: '影像', icon: 'solar:gallery-wide-bold-duotone', highlight: false, color: 'text-orange-600' },
  { id: 'digital', label: '生境', subLabel: '数字生命', icon: 'solar:magic-stick-3-bold-duotone', highlight: true },
  { id: 'chat', label: '语伴', subLabel: 'AI对话', icon: 'solar:chat-round-dots-bold-duotone', highlight: false, color: 'text-emerald-600' },
  { id: 'space', label: '念境', subLabel: '3D空间', icon: 'solar:heart-lock-bold-duotone', highlight: false, color: 'text-blue-500' },
]

const digitalFamily: DigitalFamilyMember[] = [
  {
    id: '1',
    name: '祖父 · 张明远',
    years: '1928-2018',
    trainingProgress: 98,
    status: 'active',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face',
    chatCount: '2.3k',
    lastInteraction: '3天前互动'
  },
  {
    id: '2',
    name: '祖母 · 李淑华',
    years: '1932-2020',
    trainingProgress: 76,
    status: 'training',
    avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&h=200&fit=crop&crop=face',
    chatCount: '0',
    lastInteraction: ''
  }
]

const memories: Memory[] = [
  {
    id: '1',
    date: '1985年春',
    title: '四世同堂全家福',
    description: '爷爷六十大寿，全家二十三口人在老宅院子里的合影，这是家族最珍贵的记忆之一。',
    image: 'https://images.unsplash.com/photo-1511895426328-dc8714191300?w=400&h=300&fit=crop',
    tags: ['12张影像', '3个故事']
  },
  {
    id: '2',
    date: '昨天',
    title: '给爷爷写了一封信',
    description: '通过时光信箱功能，倾诉近期的工作感悟，希望爷爷能在天之灵看到我的成长。',
    icon: 'solar:pen-new-square-bold'
  },
  {
    id: '3',
    date: '2小时前',
    title: '与祖父数字人对话',
    description: '讨论了关于家族传承的话题，获得了宝贵建议，仿佛爷爷就在身边一样。',
    icon: 'solar:chat-round-dots-bold'
  }
]

const noisePatternStyle = computed(() => ({
  backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox=%220 0 100 100%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22 opacity=%220.3%22/%3E%3C/svg%3E")`
}))

const dotPatternStyle = computed(() => ({
  backgroundImage: `url("data:image/svg+xml,%3Csvg width=%2260%22 height=%2260%22 viewBox=%220 0 60 60%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cg fill=%22none%22 fill-rule=%22evenodd%22%3E%3Cg fill=%22%23ffffff%22 fill-opacity=%220.4%22%3E%3Cpath d=%22M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
}))
</script>
