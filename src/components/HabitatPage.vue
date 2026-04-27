<template>
  <div class="min-h-screen paper-texture">
    <header class="sticky top-0 z-50 glass-warm border-b border-[#E8D5C4]">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button @click="router.push('/')" class="w-12 h-12 bg-[#C84A3E] rounded-sm flex items-center justify-center shadow-md relative overflow-hidden">
            <div class="absolute inset-0 opacity-30" :style="noisePatternStyle"></div>
            <span class="text-white font-serif text-xl font-bold tracking-widest relative z-10">存</span>
          </button>
          <div>
            <h1 class="text-2xl font-bold text-[#5C4A3A] font-serif tracking-wider">生境</h1>
            <p class="text-xs text-gray-500 tracking-[0.15em] uppercase font-medium">数字生命管理</p>
          </div>
        </div>

        <nav class="hidden lg:flex items-center space-x-8">
          <button v-for="item in navItems" :key="item.id"
            class="flex items-center space-x-2 px-3 py-2 rounded-lg transition-all hover:bg-[#E8D5C4]/50"
            :class="[
              item.id === 'habitat' ? 'bg-[#E8D5C4] text-[#8B6F4E]' : 'text-gray-600'
            ]"
            @click="handleNavClick(item.id)">
            <Icon :icon="item.icon" class="text-lg" />
            <span class="font-medium text-sm">{{ item.label }}</span>
          </button>
        </nav>

        <div class="flex items-center space-x-4">
          <button class="w-10 h-10 rounded-full bg-white/80 flex items-center justify-center shadow-sm hover:shadow-md transition-shadow">
            <Icon icon="solar:bell-bold" class="text-gray-600" />
          </button>
          <div class="flex items-center space-x-3 pl-4 border-l border-[#E8D5C4]">
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] p-0.5">
              <div class="w-full h-full rounded-full bg-gray-200 overflow-hidden">
                <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face" 
                     class="w-full h-full object-cover" alt="用户头像">
              </div>
            </div>
            <div class="hidden md:block">
              <p class="text-sm font-semibold text-gray-800">张家族长</p>
              <p class="text-xs text-gray-500">管理员</p>
            </div>
          </div>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto px-6 py-8">
      <div class="flex gap-6 h-[calc(100vh-200px)]">
        <div class="w-64 flex-shrink-0 bg-white rounded-2xl shadow-soft border border-stone-100 flex flex-col overflow-hidden">
          <div class="p-4 border-b border-[#E8D5C4]">
            <h3 class="font-bold text-[#5C4A3A] font-serif">功能模块</h3>
          </div>

          <div class="flex-1 overflow-y-auto p-3 space-y-1">
            <button v-for="module in habitatModules" :key="module.id"
              @click="activeModule = module.id"
              class="w-full p-3 rounded-xl cursor-pointer transition-all hover:bg-[#E8D5C4]/30 text-left"
              :class="[
                activeModule === module.id ? 'bg-[#E8D5C4] border border-[#D4A574]' : 'bg-transparent border border-transparent'
              ]">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-lg flex items-center justify-center"
                     :class="[
                       activeModule === module.id ? 'bg-[#8B6F4E] text-white' : 'bg-[#E8D5C4]/50 text-[#8B6F4E]'
                     ]">
                  <Icon :icon="module.icon" class="text-lg" />
                </div>
                <div>
                  <h4 class="font-semibold text-sm text-gray-800">{{ module.label }}</h4>
                  <p class="text-xs text-gray-500 mt-0.5">{{ module.description }}</p>
                </div>
              </div>
            </button>
          </div>

          <div class="p-4 border-t border-[#E8D5C4]">
            <div class="text-center text-xs text-gray-400">
              更多功能开发中...
            </div>
          </div>
        </div>

        <div class="flex-1 flex flex-col gap-6 overflow-hidden">
          <div v-if="activeModule === 'ai-avatar'" class="flex-1 flex flex-col">
            <div class="flex items-center justify-between mb-6">
              <div>
                <h2 class="text-2xl font-bold text-[#5C4A3A] font-serif">AI形象管理</h2>
                <p class="text-sm text-gray-500 mt-1">创建和管理您的数字人形象，最多可创建 {{ MAX_AVATARS }} 个</p>
              </div>
              <button @click="openCreateAvatarModal" 
                      :disabled="digitalAvatars.length >= MAX_AVATARS"
                      class="px-6 py-3 bg-[#8B6F4E] text-white rounded-xl font-medium hover:bg-[#6B5342] transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed">
                <Icon icon="solar:plus-bold" class="text-lg" />
                <span>创建新形象</span>
              </button>
            </div>

            <div class="flex-1 overflow-y-auto">
              <div v-if="digitalAvatars.length === 0" class="flex-1 flex items-center justify-center bg-white rounded-2xl border border-stone-100 shadow-soft">
                <div class="text-center p-12">
                  <div class="w-24 h-24 mx-auto mb-6 bg-[#E8D5C4] rounded-full flex items-center justify-center">
                    <Icon icon="solar:user-square-bold" class="text-5xl text-[#8B6F4E]" />
                  </div>
                  <h3 class="text-xl font-bold text-[#5C4A3A] font-serif mb-2">还没有数字人形象</h3>
                  <p class="text-sm text-gray-500 mb-6">创建您的第一个数字人形象，开始数字生命之旅</p>
                  <button @click="openCreateAvatarModal" class="px-6 py-3 bg-[#8B6F4E] text-white rounded-xl font-medium hover:bg-[#6B5342] transition-colors flex items-center space-x-2 mx-auto">
                    <Icon icon="solar:plus-bold" class="text-lg" />
                    <span>创建第一个形象</span>
                  </button>
                </div>
              </div>

              <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div v-for="avatar in digitalAvatars" :key="avatar.id"
                     class="bg-white rounded-2xl shadow-soft border border-stone-100 overflow-hidden hover-lift">
                  <div class="relative">
                    <div class="aspect-[4/3] bg-gradient-to-b from-[#FAF7F2] to-[#F5E6D3] flex items-center justify-center overflow-hidden">
                      <img v-if="avatar.avatar" :src="avatar.avatar" class="w-full h-full object-cover" :alt="avatar.name">
                      <div v-else class="w-24 h-24 rounded-full bg-[#E8D5C4] flex items-center justify-center">
                        <Icon icon="solar:user-bold" class="text-4xl text-[#8B6F4E]" />
                      </div>
                    </div>
                    <div class="absolute top-3 right-3">
                      <span v-if="avatar.status === 'active'" class="px-2 py-1 bg-green-500 text-white text-xs rounded-full">已激活</span>
                      <span v-else-if="avatar.status === 'training'" class="px-2 py-1 bg-amber-400 text-white text-xs rounded-full">训练中</span>
                      <span v-else-if="avatar.status === 'generating'" class="px-2 py-1 bg-blue-500 text-white text-xs rounded-full">生成中</span>
                      <span v-else class="px-2 py-1 bg-gray-400 text-white text-xs rounded-full">未激活</span>
                    </div>
                    <div v-if="avatar.status === 'training' || avatar.status === 'generating'" class="absolute bottom-0 left-0 right-0 bg-black/50 p-3">
                      <div class="flex items-center justify-between text-white text-xs mb-1">
                        <span>{{ avatar.status === 'training' ? '训练进度' : '生成进度' }}</span>
                        <span>{{ avatar.progress }}%</span>
                      </div>
                      <div class="w-full bg-white/30 rounded-full h-1.5">
                        <div class="bg-white h-1.5 rounded-full transition-all" 
                             :style="{ width: avatar.progress + '%' }"></div>
                      </div>
                    </div>
                  </div>

                  <div class="p-4">
                    <div class="flex items-center justify-between mb-2">
                      <h4 class="font-bold text-[#5C4A3A] font-serif">{{ avatar.name }}</h4>
                      <span class="px-2 py-0.5 bg-[#E8D5C4] text-[#8B6F4E] text-xs rounded-full">{{ avatar.relationship }}</span>
                    </div>
                    <div class="flex items-center justify-between text-xs text-gray-500">
                      <span>{{ avatar.birthYear }} - {{ avatar.deathYear || '在世' }}</span>
                      <span class="flex items-center space-x-1">
                        <Icon icon="solar:chat-round-dots-bold" class="text-xs" />
                        <span>{{ avatar.chatCount || 0 }} 次对话</span>
                      </span>
                    </div>
                  </div>

                  <div class="px-4 pb-4 flex items-center space-x-2">
                    <button @click="viewAvatarDetail(avatar)" 
                            class="flex-1 py-2 bg-[#E8D5C4] text-[#8B6F4E] rounded-lg text-sm font-medium hover:bg-[#D4A574] transition-colors flex items-center justify-center space-x-1">
                      <Icon icon="solar:eye-bold" class="text-sm" />
                      <span>查看</span>
                    </button>
                    <button @click="editAvatar(avatar)" 
                            class="flex-1 py-2 border border-[#E8D5C4] text-[#8B6F4E] rounded-lg text-sm font-medium hover:bg-[#E8D5C4]/50 transition-colors flex items-center justify-center space-x-1">
                      <Icon icon="solar:pen-bold" class="text-sm" />
                      <span>编辑</span>
                    </button>
                    <button @click="confirmDeleteAvatar(avatar)" 
                            class="py-2 px-3 border border-red-200 text-red-500 rounded-lg text-sm font-medium hover:bg-red-50 transition-colors">
                      <Icon icon="solar:trash-bin-trash-bold" class="text-sm" />
                    </button>
                  </div>
                </div>

                <div v-if="digitalAvatars.length < MAX_AVATARS" 
                     @click="openCreateAvatarModal"
                     class="bg-white/50 rounded-2xl border-2 border-dashed border-[#E8D5C4] overflow-hidden hover-lift cursor-pointer flex items-center justify-center min-h-[300px]">
                  <div class="text-center p-8">
                    <div class="w-16 h-16 mx-auto mb-4 bg-[#E8D5C4] rounded-full flex items-center justify-center">
                      <Icon icon="solar:plus-bold" class="text-3xl text-[#8B6F4E]" />
                    </div>
                    <h4 class="font-bold text-[#5C4A3A] font-serif mb-2">创建新形象</h4>
                    <p class="text-sm text-gray-500">还可创建 {{ MAX_AVATARS - digitalAvatars.length }} 个</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else-if="activeModule === 'memory-upload'" class="flex-1 flex flex-col">
            <div class="flex items-center justify-between mb-6">
              <div>
                <h2 class="text-2xl font-bold text-[#5C4A3A] font-serif">记忆管理</h2>
                <p class="text-sm text-gray-500 mt-1">上传和管理与数字人关联的记忆数据</p>
              </div>
              <button @click="goToCreateMemory" 
                      class="px-6 py-3 bg-[#8B6F4E] text-white rounded-xl font-medium hover:bg-[#6B5342] transition-colors flex items-center space-x-2">
                <Icon icon="solar:plus-bold" class="text-lg" />
                <span>上传新记忆</span>
              </button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div class="bg-white rounded-2xl p-4 shadow-soft border border-stone-100">
                <div class="flex items-center space-x-3">
                  <div class="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                    <Icon icon="material-symbols:edit-note" class="text-blue-500 text-xl" />
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">文字记忆</p>
                    <p class="text-lg font-bold text-[#5C4A3A]">{{ textMemoryCount }}</p>
                  </div>
                </div>
              </div>
              <div class="bg-white rounded-2xl p-4 shadow-soft border border-stone-100">
                <div class="flex items-center space-x-3">
                  <div class="w-10 h-10 bg-purple-50 rounded-lg flex items-center justify-center">
                    <Icon icon="material-symbols:image" class="text-purple-500 text-xl" />
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">图片记忆</p>
                    <p class="text-lg font-bold text-[#5C4A3A]">{{ imageMemoryCount }}</p>
                  </div>
                </div>
              </div>
              <div class="bg-white rounded-2xl p-4 shadow-soft border border-stone-100">
                <div class="flex items-center space-x-3">
                  <div class="w-10 h-10 bg-red-50 rounded-lg flex items-center justify-center">
                    <Icon icon="material-symbols:videocam" class="text-red-500 text-xl" />
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">视频记忆</p>
                    <p class="text-lg font-bold text-[#5C4A3A]">{{ videoMemoryCount }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="mb-4">
              <label class="block text-sm font-medium text-[#5C4A3A] mb-2">筛选数字人</label>
              <select 
                v-model="memoryFilterAvatarId" 
                @change="loadMemoriesForHabitat"
                class="w-full px-4 py-3 bg-white rounded-xl border border-[#E8D5C4] text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30"
              >
                <option value="">全部数字人</option>
                <option v-for="avatar in digitalAvatars" :key="avatar.id" :value="avatar.id">
                  {{ avatar.name }} ({{ avatar.relationship }})
                </option>
              </select>
            </div>

            <div class="flex-1 overflow-y-auto">
              <div v-if="loadingMemories" class="flex-1 flex items-center justify-center">
                <div class="text-center">
                  <div class="w-12 h-12 border-4 border-[#E8D5C4] border-t-[#8B6F4E] rounded-full animate-spin mx-auto mb-4"></div>
                  <p class="text-gray-500 text-sm">加载中...</p>
                </div>
              </div>

              <div v-else-if="memoriesForHabitat.length === 0" class="flex-1 flex items-center justify-center bg-white rounded-2xl border border-stone-100 shadow-soft">
                <div class="text-center p-12">
                  <div class="w-24 h-24 mx-auto mb-6 bg-[#E8D5C4] rounded-full flex items-center justify-center">
                    <Icon icon="solar:gallery-add-bold" class="text-5xl text-[#8B6F4E]" />
                  </div>
                  <h3 class="text-xl font-bold text-[#5C4A3A] font-serif mb-2">还没有记忆数据</h3>
                  <p class="text-sm text-gray-500 mb-6">上传您的第一个记忆，让数字人更加生动</p>
                  <button @click="goToCreateMemory" class="px-6 py-3 bg-[#8B6F4E] text-white rounded-xl font-medium hover:bg-[#6B5342] transition-colors flex items-center space-x-2 mx-auto">
                    <Icon icon="solar:plus-bold" class="text-lg" />
                    <span>上传第一个记忆</span>
                  </button>
                </div>
              </div>

              <div v-else class="space-y-4">
                <div v-for="memory in memoriesForHabitat" :key="memory.id"
                     class="bg-white rounded-2xl p-4 shadow-soft border border-stone-100 hover-lift cursor-pointer"
                     @click="viewMemoryDetail(memory.id)">
                  <div class="flex items-start space-x-4">
                    <div 
                      :class="[
                        'w-16 h-16 rounded-xl flex items-center justify-center flex-shrink-0',
                        memory.type === 'text' ? 'bg-blue-50' :
                        memory.type === 'image' ? 'bg-purple-50' :
                        'bg-red-50'
                      ]"
                    >
                      <Icon 
                        :icon="getMemoryTypeIcon(memory.type)" 
                        :class="[
                          'text-2xl',
                          memory.type === 'text' ? 'text-blue-500' :
                          memory.type === 'image' ? 'text-purple-500' :
                          'text-red-500'
                        ]"
                      />
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="flex items-start justify-between">
                        <div class="flex-1">
                          <h4 class="font-bold text-gray-800 truncate">{{ memory.title }}</h4>
                          <p class="text-xs text-gray-400 mt-1">
                            {{ getAvatarNameForMemory(memory.avatarId) }} · {{ formatMemoryDate(memory.createdAt) }}
                          </p>
                        </div>
                        <div class="flex items-center space-x-1 ml-2">
                          <button 
                            @click.stop="editMemoryForHabitat(memory.id)" 
                            class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                          >
                            <Icon icon="solar:pen-bold" class="text-gray-500" />
                          </button>
                          <button 
                            @click.stop="confirmDeleteMemory(memory.id)" 
                            class="p-2 rounded-lg hover:bg-red-50 transition-colors"
                          >
                            <Icon icon="solar:trash-bin-trash-bold" class="text-red-400" />
                          </button>
                        </div>
                      </div>
                      <p v-if="memory.description" class="text-xs text-gray-500 mt-2 line-clamp-2">
                        {{ memory.description }}
                      </p>
                      <div v-if="memory.tags && memory.tags.length > 0" class="flex flex-wrap gap-1 mt-2">
                        <span 
                          v-for="(tag, index) in memory.tags.slice(0, 3)" 
                          :key="index"
                          class="px-2 py-0.5 bg-[#F5E6D3] text-[#8B6F4E] rounded text-[10px]"
                        >
                          {{ tag }}
                        </span>
                        <span v-if="memory.tags.length > 3" class="px-2 py-0.5 text-gray-400 text-[10px]">
                          +{{ memory.tags.length - 3 }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="flex-1 flex items-center justify-center bg-white rounded-2xl border border-stone-100 shadow-soft">
            <div class="text-center p-12">
              <div class="w-24 h-24 mx-auto mb-6 bg-[#E8D5C4] rounded-full flex items-center justify-center">
                <Icon :icon="getActiveModuleIcon()" class="text-5xl text-[#8B6F4E]" />
              </div>
              <h3 class="text-xl font-bold text-[#5C4A3A] font-serif mb-2">{{ getActiveModuleLabel() }}</h3>
              <p class="text-sm text-gray-500 mb-6">该功能正在开发中，敬请期待</p>
              <div class="flex items-center justify-center space-x-2 text-xs text-gray-400">
                <Icon icon="solar:clock-circle-bold" class="text-sm" />
                <span>即将上线</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showCreateAvatarModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b border-[#E8D5C4] flex items-center justify-between">
          <div>
            <h3 class="text-xl font-bold text-[#5C4A3A] font-serif">{{ editingAvatar ? '编辑数字人形象' : '创建数字人形象' }}</h3>
            <p class="text-sm text-gray-500 mt-1">步骤 {{ currentStep }} / {{ totalSteps }}</p>
          </div>
          <button @click="closeCreateAvatarModal" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="solar:close-bold" class="text-gray-500" />
          </button>
        </div>

        <div class="p-6 border-b border-[#E8D5C4]">
          <div class="flex items-center justify-between">
            <div v-for="(step, index) in createSteps" :key="step.id" class="flex items-center">
              <div class="flex items-center">
                <div class="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-all"
                     :class="[
                       currentStep > index + 1 ? 'bg-[#8B6F4E] text-white' :
                       currentStep === index + 1 ? 'bg-[#8B6F4E] text-white' :
                       'bg-gray-200 text-gray-500'
                     ]">
                  <Icon v-if="currentStep > index + 1" icon="solar:check-circle-bold" class="text-lg" />
                  <span v-else>{{ index + 1 }}</span>
                </div>
                <span class="ml-3 text-sm font-medium"
                      :class="[
                        currentStep >= index + 1 ? 'text-[#8B6F4E]' : 'text-gray-500'
                      ]">{{ step.label }}</span>
              </div>
              <div v-if="index < createSteps.length - 1" class="w-24 h-0.5 mx-4"
                   :class="[
                     currentStep > index + 1 ? 'bg-[#8B6F4E]' : 'bg-gray-200'
                   ]"></div>
            </div>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="currentStep === 1" class="space-y-6">
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-2">姓名 <span class="text-red-500">*</span></label>
              <input type="text" v-model="newAvatarForm.name" placeholder="请输入姓名"
                     class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all">
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="text-sm font-medium text-gray-700 block mb-2">关系 <span class="text-red-500">*</span></label>
                <select v-model="newAvatarForm.relationship"
                        class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all">
                  <option value="">请选择</option>
                  <option value="祖父">祖父</option>
                  <option value="祖母">祖母</option>
                  <option value="父亲">父亲</option>
                  <option value="母亲">母亲</option>
                  <option value="伯父">伯父</option>
                  <option value="叔父">叔父</option>
                  <option value="其他">其他</option>
                </select>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-700 block mb-2">性别</label>
                <div class="flex space-x-2">
                  <button @click="newAvatarForm.gender = 'male'" 
                          class="flex-1 py-3 rounded-xl border-2 transition-all"
                          :class="[
                            newAvatarForm.gender === 'male' 
                              ? 'border-[#8B6F4E] bg-[#E8D5C4] text-[#8B6F4E]' 
                              : 'border-gray-200 text-gray-600 hover:border-[#E8D5C4]'
                          ]">
                    <Icon icon="solar:user-bold" class="mr-1" />
                    男
                  </button>
                  <button @click="newAvatarForm.gender = 'female'" 
                          class="flex-1 py-3 rounded-xl border-2 transition-all"
                          :class="[
                            newAvatarForm.gender === 'female' 
                              ? 'border-[#8B6F4E] bg-[#E8D5C4] text-[#8B6F4E]' 
                              : 'border-gray-200 text-gray-600 hover:border-[#E8D5C4]'
                          ]">
                    <Icon icon="solar:user-heart-bold" class="mr-1" />
                    女
                  </button>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="text-sm font-medium text-gray-700 block mb-2">出生年份 <span class="text-red-500">*</span></label>
                <input type="text" v-model="newAvatarForm.birthYear" placeholder="如: 1928"
                       class="w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:border-transparent transition-all"
                       :class="[
                         formErrors.birthYear ? 'border-red-300 focus:ring-red-500' : 'border-gray-200 focus:ring-[#8B6F4E]'
                       ]">
                <p v-if="formErrors.birthYear" class="text-xs text-red-500 mt-1">{{ formErrors.birthYear }}</p>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-700 block mb-2">逝世年份</label>
                <input type="text" v-model="newAvatarForm.deathYear" placeholder="如: 2018（可选）"
                       class="w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:border-transparent transition-all"
                       :class="[
                         formErrors.deathYear ? 'border-red-300 focus:ring-red-500' : 'border-gray-200 focus:ring-[#8B6F4E]'
                       ]">
                <p v-if="formErrors.deathYear" class="text-xs text-red-500 mt-1">{{ formErrors.deathYear }}</p>
              </div>
            </div>

            <div>
              <label class="text-sm font-medium text-gray-700 block mb-2">简介</label>
              <textarea v-model="newAvatarForm.description" rows="3" placeholder="请输入一些关于这位亲人的描述..."
                        class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all resize-none"></textarea>
            </div>
          </div>

          <div v-if="currentStep === 2" class="space-y-6">
            <div>
              <h4 class="text-lg font-bold text-[#5C4A3A] font-serif mb-4">选择形象生成方式</h4>
              <p class="text-sm text-gray-500 mb-6">选择一种方式创建您的数字人形象，生成后可进行微调优化</p>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div @click="newAvatarForm.generationMethod = 'photo'"
                     class="p-6 rounded-2xl border-2 cursor-pointer transition-all hover:shadow-md"
                     :class="[
                       newAvatarForm.generationMethod === 'photo' 
                         ? 'border-[#8B6F4E] bg-[#E8D5C4]/30' 
                         : 'border-gray-200 bg-white hover:border-[#E8D5C4]'
                     ]">
                  <div class="w-16 h-16 rounded-full bg-[#E8D5C4] flex items-center justify-center mb-4 mx-auto">
                    <Icon icon="solar:gallery-wide-bold" class="text-3xl text-[#8B6F4E]" />
                  </div>
                  <h5 class="font-bold text-center text-[#5C4A3A] font-serif mb-2">照片生成</h5>
                  <p class="text-sm text-gray-500 text-center mb-4">上传1-5张不同角度的照片，AI将自动识别面部特征并生成形象</p>
                  <div class="flex items-center justify-center space-x-1 text-xs text-[#8B6F4E]">
                    <Icon icon="solar:stars-bold" class="text-xs" />
                    <span>推荐使用</span>
                  </div>
                </div>

                <div @click="newAvatarForm.generationMethod = 'text'"
                     class="p-6 rounded-2xl border-2 cursor-pointer transition-all hover:shadow-md"
                     :class="[
                       newAvatarForm.generationMethod === 'text' 
                         ? 'border-[#8B6F4E] bg-[#E8D5C4]/30' 
                         : 'border-gray-200 bg-white hover:border-[#E8D5C4]'
                     ]">
                  <div class="w-16 h-16 rounded-full bg-[#E8D5C4] flex items-center justify-center mb-4 mx-auto">
                    <Icon icon="solar:text-underline-bold" class="text-3xl text-[#8B6F4E]" />
                  </div>
                  <h5 class="font-bold text-center text-[#5C4A3A] font-serif mb-2">文字描述生成</h5>
                  <p class="text-sm text-gray-500 text-center mb-4">用文字描述您想要的形象特征，AI将根据描述生成</p>
                  <div class="flex items-center justify-center space-x-1 text-xs text-gray-400">
                    <Icon icon="solar:info-circle-bold" class="text-xs" />
                    <span>生成后可进行微调</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="currentStep === 3 && newAvatarForm.generationMethod === 'photo'" class="space-y-6">
            <div>
              <h4 class="text-lg font-bold text-[#5C4A3A] font-serif mb-2">上传照片</h4>
              <p class="text-sm text-gray-500 mb-4">请上传1-5张不同角度的清晰面部照片，系统将自动检测角度类型</p>
              
              <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                <div v-for="(photo, index) in newAvatarForm.uploadedPhotos" :key="index"
                     class="relative aspect-square rounded-xl overflow-hidden bg-gray-100 group">
                  <img :src="photo" class="w-full h-full object-cover" :alt="`照片 ${index + 1}`">
                  <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <button @click="removePhoto(index)" class="w-10 h-10 rounded-full bg-red-500 text-white flex items-center justify-center hover:bg-red-600 transition-colors">
                      <Icon icon="solar:close-bold" class="text-lg" />
                    </button>
                  </div>
                  <div class="absolute top-2 left-2 w-6 h-6 rounded-full bg-[#8B6F4E] text-white text-xs flex items-center justify-center font-bold">
                    {{ index + 1 }}
                  </div>
                  <div v-if="photoAnalysisResult?.analysis[index]" class="absolute bottom-2 left-2 right-2">
                    <span class="px-2 py-1 bg-white/90 text-[#8B6F4E] text-xs rounded-full font-medium backdrop-blur-sm">
                      <Icon icon="solar:face-id-bold" class="inline mr-1" />
                      {{ photoAnalysisResult.analysis[index].detectedTypeLabel }}
                      <span class="text-gray-500 ml-1">({{ Math.round(photoAnalysisResult.analysis[index].confidence * 100) }}%)</span>
                    </span>
                  </div>
                </div>

                <div v-if="newAvatarForm.uploadedPhotos.length < 5"
                     @click="triggerPhotoUpload"
                     class="aspect-square rounded-xl border-2 border-dashed border-[#E8D5C4] flex items-center justify-center cursor-pointer hover:border-[#8B6F4E] transition-colors">
                  <div class="text-center">
                    <Icon icon="solar:gallery-add-bold" class="text-3xl text-[#8B6F4E] mx-auto mb-2" />
                    <p class="text-xs text-gray-500">添加照片</p>
                    <p class="text-xs text-gray-400">({{ newAvatarForm.uploadedPhotos.length }}/5)</p>
                  </div>
                </div>
              </div>

              <input type="file" ref="photoFileInput" multiple accept="image/*" @change="handlePhotoUpload" class="hidden">

              <div v-if="isAnalyzingPhotos" class="mt-4 p-4 bg-blue-50 rounded-xl border border-blue-200">
                <div class="flex items-center space-x-3">
                  <div class="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                  <span class="text-sm text-blue-700">正在分析照片...</span>
                </div>
              </div>

              <div v-else-if="photoAnalysisError" class="mt-4 p-4 bg-red-50 rounded-xl border border-red-200">
                <div class="flex items-center space-x-3">
                  <Icon icon="solar:danger-triangle-bold" class="text-red-500 text-lg" />
                  <span class="text-sm text-red-700">{{ photoAnalysisError }}</span>
                </div>
              </div>

              <div v-else class="mt-4 p-4 bg-[#FAF7F2] rounded-xl">
                <h6 class="font-medium text-sm text-[#5C4A3A] mb-2">上传建议：</h6>
                <ul class="text-xs text-gray-500 space-y-1">
                  <li class="flex items-center space-x-2">
                    <Icon icon="solar:check-circle-bold" class="text-green-500 text-xs" />
                    <span>建议使用清晰的面部照片，光线充足</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <Icon icon="solar:check-circle-bold" class="text-green-500 text-xs" />
                    <span>上传不同角度的照片可以获得更好的3D效果</span>
                  </li>
                  <li class="flex items-center space-x-2">
                    <Icon icon="solar:check-circle-bold" class="text-green-500 text-xs" />
                    <span>支持 JPG、PNG 格式，单张不超过 10MB</span>
                  </li>
                </ul>
              </div>
            </div>

            <div v-if="photoAnalysisResult" class="space-y-4">
              <h5 class="font-medium text-[#5C4A3A] flex items-center space-x-2">
                <Icon icon="solar:chart-2-bold" class="text-lg" />
                <span>照片分析结果</span>
              </h5>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="p-4 bg-[#FAF7F2] rounded-xl">
                  <h6 class="text-sm font-medium text-gray-700 mb-3">角度覆盖情况</h6>
                  <div class="grid grid-cols-5 gap-2 mb-3">
                    <div v-for="type in ['front', 'left', 'right', 'back', 'closeup']" :key="type"
                         class="text-center">
                      <div class="w-10 h-10 mx-auto rounded-full flex items-center justify-center mb-1"
                           :class="photoAnalysisResult.detectedTypes.includes(type) 
                             ? 'bg-green-100 text-green-600' 
                             : 'bg-gray-100 text-gray-400'">
                        <Icon v-if="photoAnalysisResult.detectedTypes.includes(type)" 
                              icon="solar:check-circle-bold" class="text-lg" />
                        <Icon v-else icon="solar:minimalistic-underline-bold" class="text-lg" />
                      </div>
                      <span class="text-xs"
                            :class="photoAnalysisResult.detectedTypes.includes(type) ? 'text-green-600' : 'text-gray-400'">
                        {{ type === 'front' ? '正面' : 
                           type === 'left' ? '左侧' : 
                           type === 'right' ? '右侧' : 
                           type === 'back' ? '背面' : '特写' }}
                      </span>
                    </div>
                  </div>
                  <div v-if="photoAnalysisResult.missingTypes.length > 0" class="text-xs text-amber-600 flex items-center space-x-1">
                    <Icon icon="solar:info-circle-bold" />
                    <span>缺少角度：{{ photoAnalysisResult.missingTypeLabels.join('、') }}</span>
                  </div>
                  <div v-else class="text-xs text-green-600 flex items-center space-x-1">
                    <Icon icon="solar:check-circle-bold" />
                    <span>所有角度都已覆盖！</span>
                  </div>
                </div>

                <div class="p-4 bg-[#FAF7F2] rounded-xl">
                  <h6 class="text-sm font-medium text-gray-700 mb-3">生成质量预估</h6>
                  <div class="space-y-3">
                    <div>
                      <div class="flex items-center justify-between text-xs text-gray-500 mb-1">
                        <span>整体质量评分</span>
                        <span class="text-[#8B6F4E] font-medium">{{ photoAnalysisResult.overallQuality }}%</span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="h-2 rounded-full transition-all"
                             :class="photoAnalysisResult.overallQuality >= 80 ? 'bg-green-500' : 
                                      photoAnalysisResult.overallQuality >= 60 ? 'bg-yellow-500' : 'bg-red-500'"
                             :style="{ width: photoAnalysisResult.overallQuality + '%' }"></div>
                      </div>
                    </div>
                    <div>
                      <div class="flex items-center justify-between text-xs text-gray-500 mb-1">
                        <span>角度覆盖度</span>
                        <span class="text-[#8B6F4E] font-medium">
                          {{ photoAnalysisResult.detectedTypes.length }}/5
                        </span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="bg-[#8B6F4E] h-2 rounded-full transition-all"
                             :style="{ width: (photoAnalysisResult.detectedTypes.length / 5) * 100 + '%' }"></div>
                      </div>
                    </div>
                  </div>
                  <p class="text-xs text-gray-500 mt-3">
                    {{ photoAnalysisResult.recommendation }}
                  </p>
                </div>
              </div>

              <div class="p-4 bg-[#FAF7F2] rounded-xl">
                <h6 class="text-sm font-medium text-gray-700 mb-3">各照片详细分析</h6>
                <div class="space-y-3">
                  <div v-for="(analysis, index) in photoAnalysisResult.analysis" :key="index"
                       class="flex items-start space-x-3 p-3 bg-white rounded-lg">
                    <div class="w-12 h-12 rounded-lg overflow-hidden flex-shrink-0 bg-gray-100">
                      <img :src="newAvatarForm.uploadedPhotos[index]" class="w-full h-full object-cover" alt="">
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center space-x-2 mb-1">
                        <span class="text-sm font-medium text-gray-800">照片 {{ index + 1 }}</span>
                        <span class="px-2 py-0.5 bg-[#E8D5C4] text-[#8B6F4E] text-xs rounded-full">
                          {{ analysis.detectedTypeLabel }}
                        </span>
                        <span class="text-xs text-gray-500">
                          置信度: {{ Math.round(analysis.confidence * 100) }}%
                        </span>
                      </div>
                      <div class="flex flex-wrap gap-1">
                        <span v-for="(feature, fIndex) in analysis.features" :key="fIndex"
                              class="px-2 py-0.5 bg-green-50 text-green-600 text-xs rounded">
                          <Icon icon="solar:check-circle-bold" class="inline mr-0.5" />
                          {{ feature }}
                        </span>
                      </div>
                      <div class="text-xs text-gray-500 mt-1">
                        质量评分: {{ analysis.qualityScore }}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="currentStep === 3 && newAvatarForm.generationMethod === 'text'" class="space-y-6">
            <div>
              <h4 class="text-lg font-bold text-[#5C4A3A] font-serif mb-2">文字描述</h4>
              <p class="text-sm text-gray-500 mb-4">请详细描述您想要的形象特征，包括面部特征、发型、服装风格等</p>

              <div class="space-y-4">
                <div>
                  <label class="text-sm font-medium text-gray-700 block mb-2">整体描述</label>
                  <textarea v-model="newAvatarForm.textDescription.overall" rows="4" 
                            placeholder="例如：一位慈祥的老年男性，面带微笑，眼神温和，头发花白，穿着传统中式服装..."
                            class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all resize-none"></textarea>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="text-sm font-medium text-gray-700 block mb-2">面部特征</label>
                    <div class="flex flex-wrap gap-2">
                      <button v-for="feature in facialFeatures" :key="feature.id"
                              @click="toggleFacialFeature(feature.id)"
                              class="px-3 py-2 rounded-lg text-sm transition-all"
                              :class="[
                                newAvatarForm.textDescription.facialFeatures.includes(feature.id)
                                  ? 'bg-[#8B6F4E] text-white'
                                  : 'bg-[#E8D5C4]/50 text-gray-600 hover:bg-[#E8D5C4]'
                              ]">
                        {{ feature.label }}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label class="text-sm font-medium text-gray-700 block mb-2">发型特征</label>
                    <div class="flex flex-wrap gap-2">
                      <button v-for="hair in hairStyles" :key="hair.id"
                              @click="toggleHairStyle(hair.id)"
                              class="px-3 py-2 rounded-lg text-sm transition-all"
                              :class="[
                                newAvatarForm.textDescription.hairStyles.includes(hair.id)
                                  ? 'bg-[#8B6F4E] text-white'
                                  : 'bg-[#E8D5C4]/50 text-gray-600 hover:bg-[#E8D5C4]'
                              ]">
                        {{ hair.label }}
                      </button>
                    </div>
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="text-sm font-medium text-gray-700 block mb-2">年龄感</label>
                    <input type="range" min="0" max="100" v-model="newAvatarForm.textDescription.ageSense" 
                           class="w-full h-2 bg-[#E8D5C4] rounded-lg appearance-none cursor-pointer">
                    <div class="flex justify-between text-xs text-gray-400 mt-1">
                      <span>年轻</span>
                      <span>中年</span>
                      <span>老年</span>
                    </div>
                  </div>

                  <div>
                    <label class="text-sm font-medium text-gray-700 block mb-2">气质风格</label>
                    <select v-model="newAvatarForm.textDescription.temperament"
                            class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all">
                      <option value="gentle">温和亲切</option>
                      <option value="serious">严肃庄重</option>
                      <option value="scholarly">儒雅学者</option>
                      <option value="energetic">活力开朗</option>
                      <option value="dignified">威严庄重</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="newAvatarForm.textDescription.overall || newAvatarForm.textDescription.facialFeatures.length > 0" class="p-4 bg-[#FAF7F2] rounded-xl">
              <h6 class="font-medium text-sm text-[#5C4A3A] mb-2">描述完整性评估</h6>
              <div class="flex items-center justify-between text-xs text-gray-500 mb-2">
                <span>描述完整度</span>
                <span class="text-[#8B6F4E] font-medium">{{ calculateDescriptionCompleteness() }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-[#8B6F4E] h-2 rounded-full transition-all" 
                     :style="{ width: calculateDescriptionCompleteness() + '%' }"></div>
              </div>
              <p class="text-xs text-gray-400 mt-2">
                {{ calculateDescriptionCompleteness() >= 70 ? '描述较为完整，AI可以较好地理解您的需求' : '建议提供更详细的描述，以便AI生成更符合预期的形象' }}
              </p>
            </div>
          </div>

          <div v-if="currentStep === 4" class="space-y-6">
            <div>
              <h4 class="text-lg font-bold text-[#5C4A3A] font-serif mb-2">确认信息</h4>
              <p class="text-sm text-gray-500 mb-6">请确认以下信息无误，确认后将开始生成数字人形象</p>

              <div class="bg-[#FAF7F2] rounded-2xl p-6 space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="text-xs text-gray-400 block mb-1">姓名</label>
                    <p class="text-sm font-medium text-gray-800">{{ newAvatarForm.name || '未填写' }}</p>
                  </div>
                  <div>
                    <label class="text-xs text-gray-400 block mb-1">关系</label>
                    <p class="text-sm font-medium text-gray-800">{{ newAvatarForm.relationship || '未选择' }}</p>
                  </div>
                  <div>
                    <label class="text-xs text-gray-400 block mb-1">性别</label>
                    <p class="text-sm font-medium text-gray-800">{{ newAvatarForm.gender === 'male' ? '男' : '女' }}</p>
                  </div>
                  <div>
                    <label class="text-xs text-gray-400 block mb-1">出生年份</label>
                    <p class="text-sm font-medium text-gray-800">{{ newAvatarForm.birthYear || '未填写' }}</p>
                  </div>
                  <div v-if="newAvatarForm.deathYear">
                    <label class="text-xs text-gray-400 block mb-1">逝世年份</label>
                    <p class="text-sm font-medium text-gray-800">{{ newAvatarForm.deathYear }}</p>
                  </div>
                  <div>
                    <label class="text-xs text-gray-400 block mb-1">生成方式</label>
                    <p class="text-sm font-medium text-gray-800">
                      {{ newAvatarForm.generationMethod === 'photo' ? '照片生成' : '文字描述生成' }}
                    </p>
                  </div>
                </div>

                <div v-if="newAvatarForm.uploadedPhotos.length > 0">
                  <label class="text-xs text-gray-400 block mb-2">上传的照片</label>
                  <div class="flex space-x-2">
                    <div v-for="(photo, index) in newAvatarForm.uploadedPhotos" :key="index"
                         class="w-16 h-16 rounded-lg overflow-hidden bg-gray-100">
                      <img :src="photo" class="w-full h-full object-cover" :alt="`照片 ${index + 1}`">
                    </div>
                  </div>
                </div>

                <div v-if="newAvatarForm.description">
                  <label class="text-xs text-gray-400 block mb-1">简介</label>
                  <p class="text-sm text-gray-800">{{ newAvatarForm.description }}</p>
                </div>
              </div>

              <div class="p-4 bg-blue-50 rounded-xl border border-blue-100">
                <div class="flex items-start space-x-3">
                  <Icon icon="solar:info-circle-bold" class="text-blue-500 text-lg flex-shrink-0 mt-0.5" />
                  <div>
                    <h6 class="font-medium text-sm text-blue-800 mb-1">生成提示</h6>
                    <p class="text-xs text-blue-600">
                      确认创建后，系统将开始生成数字人形象。生成时间取决于您选择的生成方式和数据量，通常需要5-30分钟。您可以在生成过程中离开页面，系统会在后台继续处理。
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="p-6 border-t border-[#E8D5C4] flex items-center justify-between">
          <button v-if="currentStep > 1" @click="prevStep" 
                  class="px-6 py-3 border border-gray-200 text-gray-600 rounded-xl font-medium hover:bg-gray-50 transition-colors flex items-center space-x-2">
            <Icon icon="solar:arrow-left-bold" class="text-sm" />
            <span>上一步</span>
          </button>
          <div v-else></div>

          <div class="flex items-center space-x-3">
            <button @click="closeCreateAvatarModal" 
                    class="px-6 py-3 border border-gray-200 text-gray-600 rounded-xl font-medium hover:bg-gray-50 transition-colors">
              取消
            </button>
            <button v-if="currentStep < totalSteps" @click="nextStep" 
                    :disabled="!canProceedToNextStep()"
                    class="px-6 py-3 bg-[#8B6F4E] text-white rounded-xl font-medium hover:bg-[#6B5342] transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed">
              <span>下一步</span>
              <Icon icon="solar:arrow-right-bold" class="text-sm" />
            </button>
            <button v-else @click="submitCreateAvatar" 
                    class="px-6 py-3 bg-[#8B6F4E] text-white rounded-xl font-medium hover:bg-[#6B5342] transition-colors flex items-center space-x-2">
              <Icon icon="solar:check-circle-bold" class="text-sm" />
              <span>确认创建</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showEditModal && editingAvatar" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b border-[#E8D5C4] flex items-center justify-between">
          <div>
            <h3 class="text-xl font-bold text-[#5C4A3A] font-serif">编辑数字人形象</h3>
            <p class="text-sm text-gray-500 mt-1">修改以下基本信息，形象生成方式和参数不可修改</p>
          </div>
          <button @click="closeEditModal" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="solar:close-bold" class="text-gray-500" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6">
          <div class="space-y-6">
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-2">姓名 <span class="text-red-500">*</span></label>
              <input type="text" v-model="editingAvatarForm.name" placeholder="请输入姓名"
                     class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all">
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="text-sm font-medium text-gray-700 block mb-2">关系 <span class="text-red-500">*</span></label>
                <select v-model="editingAvatarForm.relationship"
                        class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all">
                  <option value="">请选择</option>
                  <option value="祖父">祖父</option>
                  <option value="祖母">祖母</option>
                  <option value="父亲">父亲</option>
                  <option value="母亲">母亲</option>
                  <option value="伯父">伯父</option>
                  <option value="叔父">叔父</option>
                  <option value="其他">其他</option>
                </select>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-700 block mb-2">性别</label>
                <div class="flex space-x-2">
                  <button @click="editingAvatarForm.gender = 'male'" 
                          class="flex-1 py-3 rounded-xl border-2 transition-all"
                          :class="[
                            editingAvatarForm.gender === 'male' 
                              ? 'border-[#8B6F4E] bg-[#E8D5C4] text-[#8B6F4E]' 
                              : 'border-gray-200 text-gray-600 hover:border-[#E8D5C4]'
                          ]">
                    <Icon icon="solar:user-bold" class="mr-1" />
                    男
                  </button>
                  <button @click="editingAvatarForm.gender = 'female'" 
                          class="flex-1 py-3 rounded-xl border-2 transition-all"
                          :class="[
                            editingAvatarForm.gender === 'female' 
                              ? 'border-[#8B6F4E] bg-[#E8D5C4] text-[#8B6F4E]' 
                              : 'border-gray-200 text-gray-600 hover:border-[#E8D5C4]'
                          ]">
                    <Icon icon="solar:user-heart-bold" class="mr-1" />
                    女
                  </button>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="text-sm font-medium text-gray-700 block mb-2">出生年份 <span class="text-red-500">*</span></label>
                <input type="text" v-model="editingAvatarForm.birthYear" placeholder="如: 1928"
                       class="w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:border-transparent transition-all"
                       :class="[
                         editingFormErrors.birthYear ? 'border-red-300 focus:ring-red-500' : 'border-gray-200 focus:ring-[#8B6F4E]'
                       ]">
                <p v-if="editingFormErrors.birthYear" class="text-xs text-red-500 mt-1">{{ editingFormErrors.birthYear }}</p>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-700 block mb-2">逝世年份</label>
                <input type="text" v-model="editingAvatarForm.deathYear" placeholder="如: 2018（可选）"
                       class="w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:border-transparent transition-all"
                       :class="[
                         editingFormErrors.deathYear ? 'border-red-300 focus:ring-red-500' : 'border-gray-200 focus:ring-[#8B6F4E]'
                       ]">
                <p v-if="editingFormErrors.deathYear" class="text-xs text-red-500 mt-1">{{ editingFormErrors.deathYear }}</p>
              </div>
            </div>

            <div>
              <label class="text-sm font-medium text-gray-700 block mb-2">简介</label>
              <textarea v-model="editingAvatarForm.description" rows="3" placeholder="请输入一些关于这位亲人的描述..."
                        class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all resize-none"></textarea>
            </div>

            <div class="p-4 bg-gray-50 rounded-xl">
              <div class="flex items-start space-x-3">
                <Icon icon="solar:info-circle-bold" class="text-gray-400 text-lg flex-shrink-0 mt-0.5" />
                <div>
                  <h6 class="font-medium text-sm text-gray-700 mb-1">关于形象生成参数</h6>
                  <p class="text-xs text-gray-500">
                    形象生成方式（照片生成、文字描述生成）以及相关参数在创建后不可修改。如需调整形象，可在创建后使用"微调形象"功能进行调整。
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="p-6 border-t border-[#E8D5C4] flex items-center justify-end space-x-3">
          <button @click="closeEditModal" 
                  class="px-6 py-3 border border-gray-200 text-gray-600 rounded-xl font-medium hover:bg-gray-50 transition-colors">
            取消
          </button>
          <button @click="saveEditAvatar" 
                  :disabled="!editingAvatarForm.name || !editingAvatarForm.relationship"
                  class="px-6 py-3 bg-[#8B6F4E] text-white rounded-xl font-medium hover:bg-[#6B5342] transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed">
            <Icon icon="solar:check-circle-bold" class="text-sm" />
            <span>保存修改</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="showDeleteModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-xl max-w-md w-full">
        <div class="p-6 text-center">
          <div class="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
            <Icon icon="solar:trash-bin-trash-bold" class="text-3xl text-red-500" />
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-2">确认删除</h3>
          <p class="text-gray-500 mb-6">
            确定要删除数字人 <span class="font-semibold text-gray-800">{{ avatarToDelete?.name }}</span> 吗？
            <br>
            <span class="text-sm">此操作不可撤销，所有相关数据将被永久删除。</span>
          </p>
          <div class="flex space-x-3">
            <button @click="showDeleteModal = false" class="flex-1 py-3 border border-gray-200 rounded-xl text-gray-600 font-medium hover:bg-gray-50 transition-colors">
              取消
            </button>
            <button @click="deleteAvatar" class="flex-1 py-3 bg-red-500 text-white rounded-xl font-medium hover:bg-red-600 transition-colors">
              确认删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showDeleteMemoryModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-xl max-w-md w-full">
        <div class="p-6 text-center">
          <div class="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
            <Icon icon="solar:trash-bin-trash-bold" class="text-3xl text-red-500" />
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-2">确认删除</h3>
          <p class="text-gray-500 mb-6">
            确定要删除这个记忆吗？
            <br>
            <span class="text-sm">此操作不可撤销。</span>
          </p>
          <div class="flex space-x-3">
            <button @click="showDeleteMemoryModal = false" class="flex-1 py-3 border border-gray-200 rounded-xl text-gray-600 font-medium hover:bg-gray-50 transition-colors">
              取消
            </button>
            <button @click="deleteMemoryForHabitat" class="flex-1 py-3 bg-red-500 text-white rounded-xl font-medium hover:bg-red-600 transition-colors">
              确认删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showDetailModal && selectedAvatar" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b border-[#E8D5C4] flex items-center justify-between">
          <h3 class="text-xl font-bold text-[#5C4A3A] font-serif">{{ selectedAvatar.name }} - 详情</h3>
          <button @click="showDetailModal = false" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="solar:close-bold" class="text-gray-500" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6">
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="lg:col-span-1">
              <div class="bg-gradient-to-b from-[#FAF7F2] to-[#F5E6D3] rounded-2xl overflow-hidden relative">
                <div class="h-64">
                  <ThreeDModelViewer 
                    :model-url="selectedAvatar.modelUrl"
                    :background-color="0xFAF7F2"
                    :auto-rotate="true"
                    full-height
                  />
                </div>
                <div class="p-4 relative z-10">
                  <div class="flex items-center justify-between mb-2">
                    <h4 class="font-bold text-xl text-[#5C4A3A] font-serif">{{ selectedAvatar.name }}</h4>
                    <span v-if="selectedAvatar.status === 'active'" class="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">已激活</span>
                    <span v-else-if="selectedAvatar.status === 'training'" class="px-2 py-0.5 bg-amber-100 text-amber-700 text-xs rounded-full">训练中</span>
                    <span v-else-if="selectedAvatar.status === 'generating'" class="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">生成中</span>
                    <span v-else class="px-2 py-0.5 bg-gray-100 text-gray-500 text-xs rounded-full">未激活</span>
                  </div>
                  <span class="inline-block px-3 py-1 bg-[#E8D5C4] text-[#8B6F4E] text-sm rounded-full mb-3">{{ selectedAvatar.relationship }}</span>
                  
                  <div class="space-y-2">
                    <div class="flex items-center justify-between">
                      <span class="text-sm text-gray-500">训练度</span>
                      <span class="text-sm font-medium text-[#8B6F4E]">{{ selectedAvatar.progress }}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-1.5">
                      <div class="bg-[#8B6F4E] h-1.5 rounded-full transition-all" 
                           :style="{ width: selectedAvatar.progress + '%' }"></div>
                    </div>
                    <div class="flex items-center justify-between mt-2">
                      <span class="text-sm text-gray-500">对话次数</span>
                      <span class="text-sm font-medium text-[#8B6F4E]">{{ selectedAvatar.chatCount || 0 }} 次</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="mt-4 space-y-2">
                <button class="w-full py-3 bg-[#8B6F4E] text-white rounded-xl font-medium hover:bg-[#6B5342] transition-colors flex items-center justify-center space-x-2">
                  <Icon icon="solar:chat-round-dots-bold" class="text-lg" />
                  <span>开始对话</span>
                </button>
                <button v-if="selectedAvatar.status === 'active'" 
                        @click="openFineTuneModal"
                        class="w-full py-3 border border-[#E8D5C4] text-[#8B6F4E] rounded-xl font-medium hover:bg-[#E8D5C4]/50 transition-colors flex items-center justify-center space-x-2">
                  <Icon icon="solar:slider-horizontal-bold" class="text-lg" />
                  <span>微调形象</span>
                </button>
                <button @click="editAvatar(selectedAvatar)" class="w-full py-3 border border-gray-200 text-gray-600 rounded-xl font-medium hover:bg-gray-50 transition-colors flex items-center justify-center space-x-2">
                  <Icon icon="solar:pen-bold" class="text-lg" />
                  <span>编辑信息</span>
                </button>
              </div>
            </div>

            <div class="lg:col-span-2 space-y-6">
              <div class="bg-[#FAF7F2] rounded-2xl p-6">
                <h5 class="font-medium text-[#5C4A3A] mb-4 flex items-center space-x-2">
                  <Icon icon="solar:info-circle-bold" class="text-lg" />
                  <span>基本信息</span>
                </h5>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="text-xs text-gray-400 block mb-1">姓名</label>
                    <p class="text-sm font-medium text-gray-800">{{ selectedAvatar.name }}</p>
                  </div>
                  <div>
                    <label class="text-xs text-gray-400 block mb-1">关系</label>
                    <p class="text-sm font-medium text-gray-800">{{ selectedAvatar.relationship }}</p>
                  </div>
                  <div>
                    <label class="text-xs text-gray-400 block mb-1">性别</label>
                    <p class="text-sm font-medium text-gray-800">{{ selectedAvatar.gender === 'male' ? '男' : '女' }}</p>
                  </div>
                  <div>
                    <label class="text-xs text-gray-400 block mb-1">出生年份</label>
                    <p class="text-sm font-medium text-gray-800">{{ selectedAvatar.birthYear || '未填写' }}</p>
                  </div>
                  <div v-if="selectedAvatar.deathYear">
                    <label class="text-xs text-gray-400 block mb-1">逝世年份</label>
                    <p class="text-sm font-medium text-gray-800">{{ selectedAvatar.deathYear }}</p>
                  </div>
                  <div>
                    <label class="text-xs text-gray-400 block mb-1">生成方式</label>
                    <p class="text-sm font-medium text-gray-800">
                      {{ selectedAvatar.generationMethod === 'photo' ? '照片生成' : '文字描述生成' }}
                    </p>
                  </div>
                </div>
              </div>

              <div v-if="selectedAvatar.description" class="bg-[#FAF7F2] rounded-2xl p-6">
                <h5 class="font-medium text-[#5C4A3A] mb-4 flex items-center space-x-2">
                  <Icon icon="solar:document-text-bold" class="text-lg" />
                  <span>简介</span>
                </h5>
                <p class="text-sm text-gray-700 leading-relaxed">{{ selectedAvatar.description }}</p>
              </div>

              <div class="bg-[#FAF7F2] rounded-2xl p-6">
                <h5 class="font-medium text-[#5C4A3A] mb-4 flex items-center space-x-2">
                  <Icon icon="solar:chart-2-bold" class="text-lg" />
                  <span>训练进度</span>
                </h5>
                <div class="space-y-4">
                  <div>
                    <div class="flex items-center justify-between mb-2">
                      <span class="text-sm text-gray-600">整体训练进度</span>
                      <span class="text-sm font-medium text-[#8B6F4E]">{{ selectedAvatar.progress }}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-3">
                      <div class="bg-[#8B6F4E] h-3 rounded-full transition-all" 
                           :style="{ width: selectedAvatar.progress + '%' }"></div>
                    </div>
                  </div>

                  <div class="grid grid-cols-3 gap-4">
                    <div class="text-center p-3 bg-white rounded-xl">
                      <div class="text-2xl font-bold text-[#8B6F4E] mb-1">98%</div>
                      <div class="text-xs text-gray-500">面部识别</div>
                    </div>
                    <div class="text-center p-3 bg-white rounded-xl">
                      <div class="text-2xl font-bold text-[#8B6F4E] mb-1">85%</div>
                      <div class="text-xs text-gray-500">声音训练</div>
                    </div>
                    <div class="text-center p-3 bg-white rounded-xl">
                      <div class="text-2xl font-bold text-[#8B6F4E] mb-1">76%</div>
                      <div class="text-xs text-gray-500">性格建模</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showFineTuneModal && selectedAvatar" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b border-[#E8D5C4] flex items-center justify-between">
          <div>
            <h3 class="text-xl font-bold text-[#5C4A3A] font-serif">微调形象</h3>
            <p class="text-sm text-gray-500 mt-1">调整 {{ selectedAvatar.name }} 的面部特征</p>
          </div>
          <button @click="closeFineTuneModal" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="solar:close-bold" class="text-gray-500" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6">
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="lg:col-span-2 space-y-6">
              <div class="space-y-4">
                <h5 class="font-medium text-[#5C4A3A] flex items-center space-x-2">
                  <Icon icon="solar:face-id-bold" class="text-lg" />
                  <span>面部轮廓</span>
                </h5>
                
                <div class="space-y-4 pl-4">
                  <div>
                    <div class="flex items-center justify-between mb-2">
                      <label class="text-sm text-gray-700">脸型宽度</label>
                      <span class="text-xs text-[#8B6F4E]">{{ fineTuneAdjustments.faceWidth }}%</span>
                    </div>
                    <input type="range" min="0" max="100" v-model="fineTuneAdjustments.faceWidth" 
                           class="w-full h-2 bg-[#E8D5C4] rounded-lg appearance-none cursor-pointer">
                    <div class="flex justify-between text-xs text-gray-400 mt-1">
                      <span>较窄</span>
                      <span>适中</span>
                      <span>较宽</span>
                    </div>
                  </div>

                  <div>
                    <div class="flex items-center justify-between mb-2">
                      <label class="text-sm text-gray-700">下颌线条</label>
                      <span class="text-xs text-[#8B6F4E]">{{ fineTuneAdjustments.jawLine }}%</span>
                    </div>
                    <input type="range" min="0" max="100" v-model="fineTuneAdjustments.jawLine" 
                           class="w-full h-2 bg-[#E8D5C4] rounded-lg appearance-none cursor-pointer">
                    <div class="flex justify-between text-xs text-gray-400 mt-1">
                      <span>圆润</span>
                      <span>适中</span>
                      <span>分明</span>
                    </div>
                  </div>

                  <div>
                    <div class="flex items-center justify-between mb-2">
                      <label class="text-sm text-gray-700">颧骨高度</label>
                      <span class="text-xs text-[#8B6F4E]">{{ fineTuneAdjustments.cheekbones }}%</span>
                    </div>
                    <input type="range" min="0" max="100" v-model="fineTuneAdjustments.cheekbones" 
                           class="w-full h-2 bg-[#E8D5C4] rounded-lg appearance-none cursor-pointer">
                    <div class="flex justify-between text-xs text-gray-400 mt-1">
                      <span>低平</span>
                      <span>适中</span>
                      <span>突出</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="space-y-4">
                <h5 class="font-medium text-[#5C4A3A] flex items-center space-x-2">
                  <Icon icon="solar:eye-bold" class="text-lg" />
                  <span>眼睛特征</span>
                </h5>
                
                <div class="space-y-4 pl-4">
                  <div>
                    <div class="flex items-center justify-between mb-2">
                      <label class="text-sm text-gray-700">眼睛大小</label>
                      <span class="text-xs text-[#8B6F4E]">{{ fineTuneAdjustments.eyeSize }}%</span>
                    </div>
                    <input type="range" min="0" max="100" v-model="fineTuneAdjustments.eyeSize" 
                           class="w-full h-2 bg-[#E8D5C4] rounded-lg appearance-none cursor-pointer">
                    <div class="flex justify-between text-xs text-gray-400 mt-1">
                      <span>较小</span>
                      <span>适中</span>
                      <span>较大</span>
                    </div>
                  </div>

                  <div>
                    <div class="flex items-center justify-between mb-2">
                      <label class="text-sm text-gray-700">眼距宽度</label>
                      <span class="text-xs text-[#8B6F4E]">{{ fineTuneAdjustments.eyeSpacing }}%</span>
                    </div>
                    <input type="range" min="0" max="100" v-model="fineTuneAdjustments.eyeSpacing" 
                           class="w-full h-2 bg-[#E8D5C4] rounded-lg appearance-none cursor-pointer">
                    <div class="flex justify-between text-xs text-gray-400 mt-1">
                      <span>较近</span>
                      <span>适中</span>
                      <span>较远</span>
                    </div>
                  </div>

                  <div>
                    <div class="flex items-center justify-between mb-2">
                      <label class="text-sm text-gray-700">双眼皮</label>
                      <span class="text-xs text-[#8B6F4E]">{{ fineTuneAdjustments.doubleEyelid }}%</span>
                    </div>
                    <input type="range" min="0" max="100" v-model="fineTuneAdjustments.doubleEyelid" 
                           class="w-full h-2 bg-[#E8D5C4] rounded-lg appearance-none cursor-pointer">
                    <div class="flex justify-between text-xs text-gray-400 mt-1">
                      <span>单眼皮</span>
                      <span>内双</span>
                      <span>双眼皮</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="space-y-4">
                <h5 class="font-medium text-[#5C4A3A] flex items-center space-x-2">
                  <Icon icon="solar:frame-bold" class="text-lg" />
                  <span>其他特征</span>
                </h5>
                
                <div class="space-y-4 pl-4">
                  <div>
                    <div class="flex items-center justify-between mb-2">
                      <label class="text-sm text-gray-700">鼻子大小</label>
                      <span class="text-xs text-[#8B6F4E]">{{ fineTuneAdjustments.noseSize }}%</span>
                    </div>
                    <input type="range" min="0" max="100" v-model="fineTuneAdjustments.noseSize" 
                           class="w-full h-2 bg-[#E8D5C4] rounded-lg appearance-none cursor-pointer">
                  </div>

                  <div>
                    <div class="flex items-center justify-between mb-2">
                      <label class="text-sm text-gray-700">嘴唇厚度</label>
                      <span class="text-xs text-[#8B6F4E]">{{ fineTuneAdjustments.lipThickness }}%</span>
                    </div>
                    <input type="range" min="0" max="100" v-model="fineTuneAdjustments.lipThickness" 
                           class="w-full h-2 bg-[#E8D5C4] rounded-lg appearance-none cursor-pointer">
                  </div>

                  <div>
                    <div class="flex items-center justify-between mb-2">
                      <label class="text-sm text-gray-700">皱纹程度</label>
                      <span class="text-xs text-[#8B6F4E]">{{ fineTuneAdjustments.wrinkles }}%</span>
                    </div>
                    <input type="range" min="0" max="100" v-model="fineTuneAdjustments.wrinkles" 
                           class="w-full h-2 bg-[#E8D5C4] rounded-lg appearance-none cursor-pointer">
                  </div>
                </div>
              </div>
            </div>

            <div class="lg:col-span-1">
              <div class="sticky top-4">
                <h5 class="font-medium text-[#5C4A3A] mb-4 text-center">预览效果</h5>
                <div class="aspect-[3/4] bg-gradient-to-b from-[#FAF7F2] to-[#F5E6D3] rounded-2xl flex items-center justify-center relative overflow-hidden">
                  <div v-if="selectedAvatar.avatar" class="absolute inset-0">
                    <img :src="selectedAvatar.avatar" class="w-full h-full object-cover opacity-80" alt="">
                  </div>
                  <div v-else class="text-center z-10">
                    <div class="w-32 h-32 mx-auto mb-4 rounded-full bg-[#E8D5C4] flex items-center justify-center">
                      <Icon icon="solar:user-square-bold" class="text-5xl text-[#8B6F4E]" />
                    </div>
                    <p class="text-sm text-gray-500">预览效果</p>
                    <p class="text-xs text-gray-400 mt-1">调整滑块后可重新生成</p>
                  </div>
                  
                  <div v-if="isFineTuning" class="absolute inset-0 bg-black/50 flex items-center justify-center">
                    <div class="text-center text-white">
                      <div class="w-10 h-10 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                      <p class="text-sm">微调中...</p>
                    </div>
                  </div>
                </div>

                <div class="mt-4 space-y-2">
                  <button @click="applyFineTune" 
                          :disabled="isFineTuning"
                          class="w-full py-3 bg-[#8B6F4E] text-white rounded-xl font-medium hover:bg-[#6B5342] transition-colors flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed">
                    <Icon icon="solar:check-circle-bold" class="text-sm" />
                    <span>应用微调</span>
                  </button>
                  <button @click="resetFineTune" 
                          class="w-full py-3 border border-[#E8D5C4] text-[#8B6F4E] rounded-xl font-medium hover:bg-[#E8D5C4]/50 transition-colors flex items-center justify-center space-x-2">
                    <Icon icon="solar:refresh-circle-bold" class="text-sm" />
                    <span>重置为默认</span>
                  </button>
                </div>

                <div v-if="selectedAvatar.fineTuneAdjustments" class="mt-4 p-4 bg-[#FAF7F2] rounded-xl">
                  <h6 class="text-sm font-medium text-[#5C4A3A] mb-2">上次微调</h6>
                  <p class="text-xs text-gray-500">已保存微调参数，可随时调整</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="p-6 border-t border-[#E8D5C4] flex items-center justify-end space-x-3">
          <button @click="closeFineTuneModal" 
                  class="px-6 py-3 border border-gray-200 text-gray-600 rounded-xl font-medium hover:bg-gray-50 transition-colors">
            取消
          </button>
          <button @click="saveAndCloseFineTune" 
                  :disabled="isFineTuning"
                  class="px-6 py-3 bg-[#8B6F4E] text-white rounded-xl font-medium hover:bg-[#6B5342] transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
            保存并关闭
          </button>
        </div>
      </div>
    </div>

    <div v-if="showConfigModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b border-[#E8D5C4] flex items-center justify-between">
          <div>
            <h3 class="text-xl font-bold text-[#5C4A3A] font-serif">API 配置</h3>
            <p class="text-sm text-gray-500 mt-1">配置 AI 模型服务的 API Key</p>
          </div>
          <button @click="closeConfigModal" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="solar:close-bold" class="text-gray-500" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-6">
          <div class="space-y-4">
            <h5 class="font-medium text-[#5C4A3A] flex items-center space-x-2">
              <Icon icon="solar:command-bold" class="text-lg" />
              <span>OpenAI 配置</span>
            </h5>
            
            <div class="space-y-4 p-4 bg-[#FAF7F2] rounded-xl">
              <div>
                <label class="text-sm font-medium text-gray-700 block mb-2">
                  API Key
                  <span class="text-gray-400 text-xs ml-1">(用于图像分析、文本生成)</span>
                </label>
                <input type="password" v-model="configForm.openai.apiKey" 
                       placeholder="sk-..."
                       class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all">
              </div>
              
              <div>
                <label class="text-sm font-medium text-gray-700 block mb-2">
                  API 地址 (可选)
                  <span class="text-gray-400 text-xs ml-1">(用于代理服务)</span>
                </label>
                <input type="text" v-model="configForm.openai.baseUrl" 
                       placeholder="https://api.openai.com/v1"
                       class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all">
              </div>

              <div>
                <label class="text-sm font-medium text-gray-700 block mb-2">
                  模型
                </label>
                <select v-model="configForm.openai.model"
                        class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all">
                  <option value="gpt-4o">GPT-4o (推荐)</option>
                  <option value="gpt-4o-mini">GPT-4o Mini</option>
                  <option value="gpt-4-turbo">GPT-4 Turbo</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                </select>
              </div>

              <div v-if="currentConfig?.openai?.apiKeyConfigured" class="flex items-center space-x-2 text-green-600 text-sm">
                <Icon icon="solar:check-circle-bold" />
                <span>OpenAI API Key 已配置</span>
              </div>
            </div>
          </div>

          <div class="space-y-4">
            <h5 class="font-medium text-[#5C4A3A] flex items-center space-x-2">
              <Icon icon="solar:cloud-bold" class="text-lg" />
              <span>阿里云百炼配置</span>
            </h5>
            
            <div class="space-y-4 p-4 bg-[#FAF7F2] rounded-xl">
              <div>
                <label class="text-sm font-medium text-gray-700 block mb-2">
                  API Key
                  <span class="text-gray-400 text-xs ml-1">(用于图像生成、图像分析)</span>
                </label>
                <input type="password" v-model="configForm.aliyun.apiKey" 
                       placeholder="sk-..."
                       class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all">
              </div>
              
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="text-sm font-medium text-gray-700 block mb-2">
                    图像生成模型
                  </label>
                  <select v-model="configForm.aliyun.imageModel"
                          class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all">
                    <option value="wanx-v1">万相 v1 (推荐)</option>
                    <option value="wanx2.1-t2i-turbo">万相 2.1 极速版</option>
                  </select>
                </div>
                <div>
                  <label class="text-sm font-medium text-gray-700 block mb-2">
                    文本模型
                  </label>
                  <select v-model="configForm.aliyun.textModel"
                          class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all">
                    <option value="qwen-plus">通义千问 Plus (推荐)</option>
                    <option value="qwen-max">通义千问 Max</option>
                    <option value="qwen-turbo">通义千问 Turbo</option>
                  </select>
                </div>
              </div>

              <div class="p-3 bg-blue-50 rounded-lg border border-blue-100">
                <h6 class="text-sm font-medium text-blue-800 mb-1">获取阿里云 API Key</h6>
                <p class="text-xs text-blue-600">
                  1. 访问 <a href="https://dashscope.console.aliyun.com" target="_blank" class="underline">阿里云百炼控制台</a><br>
                  2. 开通 DashScope 服务<br>
                  3. 在 API-Key 管理中创建新的 API Key
                </p>
              </div>

              <div v-if="currentConfig?.aliyun?.apiKeyConfigured" class="flex items-center space-x-2 text-green-600 text-sm">
                <Icon icon="solar:check-circle-bold" />
                <span>阿里云 API Key 已配置</span>
              </div>
            </div>
          </div>

          <div class="p-4 bg-amber-50 rounded-xl border border-amber-100">
            <div class="flex items-start space-x-3">
              <Icon icon="solar:info-circle-bold" class="text-amber-600 text-lg flex-shrink-0 mt-0.5" />
              <div>
                <h6 class="font-medium text-sm text-amber-800 mb-1">关于 API Key 安全</h6>
                <p class="text-xs text-amber-700">
                  API Key 仅保存在本地服务器配置文件中，不会上传到任何第三方。请妥善保管您的 API Key，不要泄露给他人。
                </p>
              </div>
            </div>
          </div>
        </div>

        <div class="p-6 border-t border-[#E8D5C4] flex items-center justify-between">
          <button @click="testConnection" 
                  :disabled="isTestingConnection"
                  class="px-6 py-3 border border-[#E8D5C4] text-[#8B6F4E] rounded-xl font-medium hover:bg-[#E8D5C4]/50 transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed">
            <Icon v-if="isTestingConnection" icon="solar:loader-bold" class="animate-spin" />
            <span>{{ isTestingConnection ? '测试中...' : '测试连接' }}</span>
          </button>
          
          <div class="flex items-center space-x-3">
            <button @click="closeConfigModal" 
                    class="px-6 py-3 border border-gray-200 text-gray-600 rounded-xl font-medium hover:bg-gray-50 transition-colors">
              取消
            </button>
            <button @click="saveConfig" 
                    :disabled="isSavingConfig"
                    class="px-6 py-3 bg-[#8B6F4E] text-white rounded-xl font-medium hover:bg-[#6B5342] transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              保存配置
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import ThreeDModelViewer from './ThreeDModelViewer.vue'
import { apiService, type PhotoAnalysisResponse, type PhotoAnalysisResult, type MemoryListItem, type MemoryType } from '../services/api'

const router = useRouter()

const MAX_AVATARS = 5

interface DigitalAvatar {
  id: string
  name: string
  relationship: string
  gender: 'male' | 'female'
  avatar?: string
  modelUrl?: string
  status: 'active' | 'training' | 'generating' | 'inactive' | 'fine-tuning'
  progress: number
  birthYear?: string
  deathYear?: string
  chatCount?: number
  lastInteraction?: string
  generationMethod?: 'photo' | 'text' | 'manual'
  description?: string
  fineTuneAdjustments?: FineTuneAdjustments
}

interface HabitatModule {
  id: string
  label: string
  description: string
  icon: string
}

interface CreateStep {
  id: string
  label: string
}

interface FacialFeature {
  id: string
  label: string
}

interface HairStyle {
  id: string
  label: string
}

const digitalAvatars = ref<DigitalAvatar[]>([])
const isLoadingAvatars = ref(false)

const loadAvatars = async () => {
  isLoadingAvatars.value = true
  try {
    const response = await apiService.getAvatars()
    if (response.success && response.data && response.data.avatars) {
      digitalAvatars.value = response.data.avatars.map((avatar: any) => ({
        id: avatar.id,
        name: avatar.name,
        relationship: avatar.relationship,
        gender: avatar.gender as 'male' | 'female',
        avatar: avatar.avatar,
        modelUrl: avatar.modelUrl,
        status: avatar.status as DigitalAvatar['status'],
        progress: avatar.progress || 0,
        birthYear: avatar.birthYear,
        deathYear: avatar.deathYear,
        chatCount: avatar.chatCount || 0,
        lastInteraction: avatar.lastInteraction,
        generationMethod: avatar.generationMethod as 'photo' | 'text' | 'manual',
        description: avatar.description,
        fineTuneAdjustments: avatar.fineTuneAdjustments
      }))
    }
  } catch (error) {
    console.error('加载数字人列表失败:', error)
  } finally {
    isLoadingAvatars.value = false
  }
}

const habitatModules: HabitatModule[] = [
  {
    id: 'ai-avatar',
    label: 'AI形象管理',
    description: '创建和管理数字人形象',
    icon: 'solar:user-square-bold'
  },
  {
    id: 'voice-training',
    label: '声音训练',
    description: '训练数字人声音',
    icon: 'solar:volume-high-bold'
  },
  {
    id: 'memory-upload',
    label: '记忆上传',
    description: '上传和管理记忆数据',
    icon: 'solar:gallery-add-bold'
  },
  {
    id: 'personality-setting',
    label: '性格设定',
    description: '调整数字人性格',
    icon: 'solar:heart-bold'
  }
]

const activeModule = ref('ai-avatar')
const selectedAvatar = ref<DigitalAvatar | null>(null)

const showCreateAvatarModal = ref(false)
const showDeleteModal = ref(false)
const showDetailModal = ref(false)
const editingAvatar = ref<DigitalAvatar | null>(null)
const avatarToDelete = ref<DigitalAvatar | null>(null)

const createSteps: CreateStep[] = [
  { id: 'basic-info', label: '基本信息' },
  { id: 'generation-method', label: '生成方式' },
  { id: 'specific-settings', label: '详细设置' },
  { id: 'confirmation', label: '确认创建' }
]

const currentStep = ref(1)
const totalSteps = computed(() => createSteps.length)

const photoFileInput = ref<HTMLInputElement | null>(null)

const isAnalyzingPhotos = ref(false)
const photoAnalysisResult = ref<PhotoAnalysisResponse | null>(null)
const photoAnalysisError = ref<string>('')
const photoAnalysisDebounceTimer = ref<number | null>(null)
const needsReanalysis = ref(false)
const lastAnalyzedPhotosCount = ref(0)

const generationTrackingInterval = ref<number | null>(null)
const pendingAvatarId = ref<string>('')
const pendingTaskId = ref<string>('')

interface NewAvatarForm {
  name: string
  relationship: string
  gender: 'male' | 'female'
  birthYear: string
  deathYear: string
  description: string
  generationMethod: 'photo' | 'text' | 'manual'
  uploadedPhotos: string[]
  textDescription: {
    overall: string
    facialFeatures: string[]
    hairStyles: string[]
    ageSense: number
    temperament: string
  }
  manualAdjust: {
    faceWidth: number
    jawLine: number
    cheekbones: number
    eyeSize: number
    eyeSpacing: number
    doubleEyelid: number
    noseSize: number
    lipThickness: number
    wrinkles: number
  }
}

const defaultNewAvatarForm: NewAvatarForm = {
  name: '',
  relationship: '',
  gender: 'male',
  birthYear: '',
  deathYear: '',
  description: '',
  generationMethod: 'photo',
  uploadedPhotos: [],
  textDescription: {
    overall: '',
    facialFeatures: [],
    hairStyles: [],
    ageSense: 50,
    temperament: 'gentle'
  },
  manualAdjust: {
    faceWidth: 50,
    jawLine: 50,
    cheekbones: 50,
    eyeSize: 50,
    eyeSpacing: 50,
    doubleEyelid: 50,
    noseSize: 50,
    lipThickness: 50,
    wrinkles: 50
  }
}

const newAvatarForm = ref<NewAvatarForm>({ ...defaultNewAvatarForm })

const formErrors = ref<{
  birthYear: string
  deathYear: string
}>({
  birthYear: '',
  deathYear: ''
})

const editingAvatarForm = ref<{
  name: string
  relationship: string
  gender: 'male' | 'female'
  birthYear: string
  deathYear: string
  description: string
}>({
  name: '',
  relationship: '',
  gender: 'male',
  birthYear: '',
  deathYear: '',
  description: ''
})

const editingFormErrors = ref<{
  birthYear: string
  deathYear: string
}>({
  birthYear: '',
  deathYear: ''
})

const showEditModal = ref(false)

const validateYear = (year: string, isRequired: boolean = false): string => {
  if (!year) {
    return isRequired ? '请输入年份' : ''
  }
  
  const yearNum = parseInt(year, 10)
  const currentYear = new Date().getFullYear()
  
  if (isNaN(yearNum) || year.length !== 4) {
    return '请输入有效的4位年份'
  }
  
  if (yearNum < 1900 || yearNum > currentYear) {
    return `年份范围应为1900-${currentYear}`
  }
  
  return ''
}

const validateYears = (isEdit: boolean = false) => {
  const errors = isEdit ? editingFormErrors : formErrors
  const form = isEdit ? editingAvatarForm : newAvatarForm
  
  errors.value.birthYear = validateYear(form.value.birthYear, true)
  
  if (form.value.deathYear) {
    errors.value.deathYear = validateYear(form.value.deathYear)
    
    if (!errors.value.deathYear && form.value.birthYear && !errors.value.birthYear) {
      const birthYear = parseInt(form.value.birthYear, 10)
      const deathYear = parseInt(form.value.deathYear, 10)
      if (deathYear < birthYear) {
        errors.value.deathYear = '逝世年份不能早于出生年份'
      }
    }
  } else {
    errors.value.deathYear = ''
  }
  
  return !errors.value.birthYear && !errors.value.deathYear
}

watch(() => newAvatarForm.value.birthYear, () => {
  if (newAvatarForm.value.birthYear) {
    formErrors.value.birthYear = validateYear(newAvatarForm.value.birthYear, true)
    if (newAvatarForm.value.deathYear && !formErrors.value.birthYear) {
      const birthYear = parseInt(newAvatarForm.value.birthYear, 10)
      const deathYear = parseInt(newAvatarForm.value.deathYear, 10)
      if (deathYear < birthYear) {
        formErrors.value.deathYear = '逝世年份不能早于出生年份'
      }
    }
  }
})

watch(() => newAvatarForm.value.deathYear, () => {
  if (newAvatarForm.value.deathYear) {
    formErrors.value.deathYear = validateYear(newAvatarForm.value.deathYear)
    if (!formErrors.value.deathYear && newAvatarForm.value.birthYear && !formErrors.value.birthYear) {
      const birthYear = parseInt(newAvatarForm.value.birthYear, 10)
      const deathYear = parseInt(newAvatarForm.value.deathYear, 10)
      if (deathYear < birthYear) {
        formErrors.value.deathYear = '逝世年份不能早于出生年份'
      }
    }
  } else {
    formErrors.value.deathYear = ''
  }
})

watch(() => editingAvatarForm.value.birthYear, () => {
  if (editingAvatarForm.value.birthYear) {
    editingFormErrors.value.birthYear = validateYear(editingAvatarForm.value.birthYear, true)
    if (editingAvatarForm.value.deathYear && !editingFormErrors.value.birthYear) {
      const birthYear = parseInt(editingAvatarForm.value.birthYear, 10)
      const deathYear = parseInt(editingAvatarForm.value.deathYear, 10)
      if (deathYear < birthYear) {
        editingFormErrors.value.deathYear = '逝世年份不能早于出生年份'
      }
    }
  }
})

watch(() => editingAvatarForm.value.deathYear, () => {
  if (editingAvatarForm.value.deathYear) {
    editingFormErrors.value.deathYear = validateYear(editingAvatarForm.value.deathYear)
    if (!editingFormErrors.value.deathYear && editingAvatarForm.value.birthYear && !editingFormErrors.value.birthYear) {
      const birthYear = parseInt(editingAvatarForm.value.birthYear, 10)
      const deathYear = parseInt(editingAvatarForm.value.deathYear, 10)
      if (deathYear < birthYear) {
        editingFormErrors.value.deathYear = '逝世年份不能早于出生年份'
      }
    }
  } else {
    editingFormErrors.value.deathYear = ''
  }
})

const facialFeatures: FacialFeature[] = [
  { id: 'round-face', label: '圆脸' },
  { id: 'square-face', label: '方脸' },
  { id: 'oval-face', label: '鹅蛋脸' },
  { id: 'big-eyes', label: '大眼睛' },
  { id: 'small-eyes', label: '小眼睛' },
  { id: 'high-bridge', label: '高鼻梁' },
  { id: 'thick-eyebrows', label: '浓眉' },
  { id: 'thin-eyebrows', label: '淡眉' }
]

const hairStyles: HairStyle[] = [
  { id: 'short-hair', label: '短发' },
  { id: 'long-hair', label: '长发' },
  { id: 'white-hair', label: '白发' },
  { id: 'black-hair', label: '黑发' },
  { id: 'curly-hair', label: '卷发' },
  { id: 'straight-hair', label: '直发' }
]

const navItems = [
  { id: 'home', label: '首页', icon: 'solar:home-2-bold' },
  { id: 'family', label: '家承', icon: 'solar:tree-bold-duotone' },
  { id: 'gallery', label: '影集', icon: 'solar:gallery-wide-bold-duotone' },
  { id: 'habitat', label: '生境', icon: 'solar:magic-stick-3-bold-duotone' },
  { id: 'chat', label: '语伴', icon: 'solar:chat-round-dots-bold-duotone' }
]

const handleNavClick = (navId: string) => {
  if (navId === 'home') {
    router.push('/')
  } else if (navId === 'family') {
    router.push('/zupu')
  } else if (navId === 'gallery') {
    router.push('/gallery')
  }
}

const getActiveModuleIcon = () => {
  const module = habitatModules.find(m => m.id === activeModule.value)
  return module?.icon || 'solar:info-circle-bold'
}

const getActiveModuleLabel = () => {
  const module = habitatModules.find(m => m.id === activeModule.value)
  return module?.label || '功能模块'
}

const openCreateAvatarModal = () => {
  if (digitalAvatars.value.length >= MAX_AVATARS) {
    return
  }
  newAvatarForm.value = { ...defaultNewAvatarForm }
  currentStep.value = 1
  editingAvatar.value = null
  showCreateAvatarModal.value = true
}

const closeCreateAvatarModal = () => {
  showCreateAvatarModal.value = false
  newAvatarForm.value = { ...defaultNewAvatarForm }
  currentStep.value = 1
  editingAvatar.value = null
}

const canProceedToNextStep = () => {
  switch (currentStep.value) {
    case 1:
      return newAvatarForm.value.name && newAvatarForm.value.relationship
    case 2:
      return !!newAvatarForm.value.generationMethod
    case 3:
      if (newAvatarForm.value.generationMethod === 'photo') {
        return newAvatarForm.value.uploadedPhotos.length >= 1
      }
      return true
    default:
      return true
  }
}

const nextStep = () => {
  if (currentStep.value < totalSteps.value && canProceedToNextStep()) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const triggerPhotoUpload = () => {
  photoFileInput.value?.click()
}

const handlePhotoUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files || files.length === 0) return

  const remainingSlots = 5 - newAvatarForm.value.uploadedPhotos.length
  const filesToProcess = Array.from(files).slice(0, remainingSlots)
  
  target.value = ''

  if (filesToProcess.length === 0) return

  let processedCount = 0
  const totalToProcess = filesToProcess.length

  filesToProcess.forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const result = e.target?.result as string
      if (result && newAvatarForm.value.uploadedPhotos.length < 5) {
        newAvatarForm.value.uploadedPhotos.push(result)
      }
      
      processedCount++
      if (processedCount >= totalToProcess) {
        analyzePhotos()
      }
    }
    reader.readAsDataURL(file)
  })
}

const performPhotoAnalysis = async () => {
  if (isAnalyzingPhotos.value) {
    needsReanalysis.value = true
    return
  }

  isAnalyzingPhotos.value = true
  needsReanalysis.value = false
  lastAnalyzedPhotosCount.value = newAvatarForm.value.uploadedPhotos.length
  photoAnalysisError.value = ''

  try {
    const response = await apiService.analyzePhotos(newAvatarForm.value.uploadedPhotos)
    
    if (response.success && response.data) {
      photoAnalysisResult.value = response.data
    } else {
      photoAnalysisError.value = response.error || '照片分析失败'
    }
  } catch (error) {
    photoAnalysisError.value = error instanceof Error ? error.message : '照片分析失败'
  } finally {
    isAnalyzingPhotos.value = false

    if (needsReanalysis.value || 
        newAvatarForm.value.uploadedPhotos.length !== lastAnalyzedPhotosCount.value) {
      performPhotoAnalysis()
    }
  }
}

const analyzePhotos = () => {
  if (newAvatarForm.value.uploadedPhotos.length === 0) {
    photoAnalysisResult.value = null
    photoAnalysisError.value = ''
    needsReanalysis.value = false
    if (photoAnalysisDebounceTimer.value) {
      clearTimeout(photoAnalysisDebounceTimer.value)
      photoAnalysisDebounceTimer.value = null
    }
    return
  }

  if (photoAnalysisDebounceTimer.value) {
    clearTimeout(photoAnalysisDebounceTimer.value)
  }

  photoAnalysisDebounceTimer.value = window.setTimeout(() => {
    performPhotoAnalysis()
  }, 300)
}

const removePhoto = (index: number) => {
  newAvatarForm.value.uploadedPhotos.splice(index, 1)
  analyzePhotos()
}

const toggleFacialFeature = (featureId: string) => {
  const index = newAvatarForm.value.textDescription.facialFeatures.indexOf(featureId)
  if (index > -1) {
    newAvatarForm.value.textDescription.facialFeatures.splice(index, 1)
  } else {
    newAvatarForm.value.textDescription.facialFeatures.push(featureId)
  }
}

const toggleHairStyle = (hairId: string) => {
  const index = newAvatarForm.value.textDescription.hairStyles.indexOf(hairId)
  if (index > -1) {
    newAvatarForm.value.textDescription.hairStyles.splice(index, 1)
  } else {
    newAvatarForm.value.textDescription.hairStyles.push(hairId)
  }
}

const calculateDescriptionCompleteness = () => {
  let score = 0
  const total = 5

  if (newAvatarForm.value.textDescription.overall.length > 20) score++
  if (newAvatarForm.value.textDescription.facialFeatures.length > 0) score++
  if (newAvatarForm.value.textDescription.hairStyles.length > 0) score++
  if (newAvatarForm.value.textDescription.ageSense !== 50) score++
  if (newAvatarForm.value.textDescription.temperament) score++

  return Math.round((score / total) * 100)
}

const submitCreateAvatar = async () => {
  const request = {
    name: newAvatarForm.value.name,
    relationship: newAvatarForm.value.relationship,
    gender: newAvatarForm.value.gender,
    birthYear: newAvatarForm.value.birthYear,
    deathYear: newAvatarForm.value.deathYear || undefined,
    description: newAvatarForm.value.description,
    generationMethod: newAvatarForm.value.generationMethod,
    photos: newAvatarForm.value.uploadedPhotos.length > 0 ? newAvatarForm.value.uploadedPhotos : [],
    textDescription: newAvatarForm.value.generationMethod === 'text' ? {
      overall: newAvatarForm.value.textDescription.overall,
      facialFeatures: newAvatarForm.value.textDescription.facialFeatures,
      hairStyles: newAvatarForm.value.textDescription.hairStyles,
      ageSense: newAvatarForm.value.textDescription.ageSense,
      temperament: newAvatarForm.value.textDescription.temperament
    } : undefined
  }

  try {
    const response = await apiService.generateAvatar(request)
    
    if (response.success && response.data) {
      const { taskId, avatarId } = response.data
      
      const newDigitalAvatar: DigitalAvatar = {
        id: avatarId,
        name: newAvatarForm.value.name,
        relationship: newAvatarForm.value.relationship,
        gender: newAvatarForm.value.gender,
        avatar: newAvatarForm.value.uploadedPhotos[0] || undefined,
        status: 'generating',
        progress: 0,
        birthYear: newAvatarForm.value.birthYear,
        deathYear: newAvatarForm.value.deathYear || undefined,
        chatCount: 0,
        generationMethod: newAvatarForm.value.generationMethod,
        description: newAvatarForm.value.description
      }

      digitalAvatars.value.push(newDigitalAvatar)
      closeCreateAvatarModal()

      pendingAvatarId.value = avatarId
      pendingTaskId.value = taskId
      startGenerationTracking(avatarId, taskId)
    } else {
      console.error('创建数字人失败:', response.error)
      alert('创建数字人失败: ' + (response.error || '未知错误'))
    }
  } catch (error) {
    console.error('创建数字人失败:', error)
    alert('创建数字人失败: ' + (error instanceof Error ? error.message : '未知错误'))
  }
}

const startGenerationTracking = (avatarId: string, taskId: string) => {
  if (generationTrackingInterval.value) {
    clearInterval(generationTrackingInterval.value)
  }

  generationTrackingInterval.value = window.setInterval(async () => {
    const avatar = digitalAvatars.value.find(a => a.id === avatarId)
    if (!avatar) {
      stopGenerationTracking()
      return
    }

    try {
      const response = await apiService.getAvatarStatus(avatarId)
      
      if (response.success && response.data) {
        avatar.progress = response.data.progress
        avatar.status = response.data.status as DigitalAvatar['status']

        if (response.data.status === 'active') {
          const avatarDetail = await apiService.getAvatar(avatarId)
          if (avatarDetail.success && avatarDetail.data) {
            avatar.avatar = avatarDetail.data.avatar
            avatar.modelUrl = avatarDetail.data.modelUrl
          }
          stopGenerationTracking()
        }
      }
    } catch (error) {
      console.error('跟踪生成进度失败:', error)
    }
  }, 2000)
}

const stopGenerationTracking = () => {
  if (generationTrackingInterval.value) {
    clearInterval(generationTrackingInterval.value)
    generationTrackingInterval.value = null
  }
  pendingAvatarId.value = ''
  pendingTaskId.value = ''
}

onMounted(() => {
  loadAvatars()
  loadMemoriesForHabitat()
})

onUnmounted(() => {
  stopGenerationTracking()
  if (photoAnalysisDebounceTimer.value) {
    clearTimeout(photoAnalysisDebounceTimer.value)
    photoAnalysisDebounceTimer.value = null
  }
})

const viewAvatarDetail = (avatar: DigitalAvatar) => {
  selectedAvatar.value = avatar
  showDetailModal.value = true
}

const editAvatar = (avatar: DigitalAvatar) => {
  editingAvatar.value = avatar
  editingAvatarForm.value = {
    name: avatar.name,
    relationship: avatar.relationship,
    gender: avatar.gender,
    birthYear: avatar.birthYear || '',
    deathYear: avatar.deathYear || '',
    description: avatar.description || ''
  }
  editingFormErrors.value = {
    birthYear: '',
    deathYear: ''
  }
  showDetailModal.value = false
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editingAvatar.value = null
  editingFormErrors.value = {
    birthYear: '',
    deathYear: ''
  }
}

const saveEditAvatar = () => {
  if (!editingAvatar.value) return
  
  if (!editingAvatarForm.value.name || !editingAvatarForm.value.relationship) {
    return
  }
  
  if (!validateYears(true)) {
    return
  }

  const index = digitalAvatars.value.findIndex(a => a.id === editingAvatar.value!.id)
  if (index > -1) {
    digitalAvatars.value[index] = {
      ...digitalAvatars.value[index],
      name: editingAvatarForm.value.name,
      relationship: editingAvatarForm.value.relationship,
      gender: editingAvatarForm.value.gender,
      birthYear: editingAvatarForm.value.birthYear,
      deathYear: editingAvatarForm.value.deathYear || undefined,
      description: editingAvatarForm.value.description
    }
    
    if (selectedAvatar.value?.id === editingAvatar.value!.id) {
      selectedAvatar.value = { ...digitalAvatars.value[index] }
    }
  }

  closeEditModal()
}

const confirmDeleteAvatar = (avatar: DigitalAvatar) => {
  avatarToDelete.value = avatar
  showDeleteModal.value = true
}

const deleteAvatar = () => {
  if (!avatarToDelete.value) return

  const index = digitalAvatars.value.findIndex(a => a.id === avatarToDelete.value!.id)
  if (index > -1) {
    digitalAvatars.value.splice(index, 1)
  }

  showDeleteModal.value = false
  avatarToDelete.value = null
}

const showFineTuneModal = ref(false)
const isFineTuning = ref(false)

interface FineTuneAdjustments {
  faceWidth: number
  jawLine: number
  cheekbones: number
  eyeSize: number
  eyeSpacing: number
  doubleEyelid: number
  noseSize: number
  lipThickness: number
  wrinkles: number
}

const defaultFineTuneAdjustments: FineTuneAdjustments = {
  faceWidth: 50,
  jawLine: 50,
  cheekbones: 50,
  eyeSize: 50,
  eyeSpacing: 50,
  doubleEyelid: 50,
  noseSize: 50,
  lipThickness: 50,
  wrinkles: 50
}

const fineTuneAdjustments = ref<FineTuneAdjustments>({ ...defaultFineTuneAdjustments })

const openFineTuneModal = () => {
  if (!selectedAvatar.value) return
  
  if (selectedAvatar.value.fineTuneAdjustments) {
    fineTuneAdjustments.value = { ...selectedAvatar.value.fineTuneAdjustments }
  } else {
    fineTuneAdjustments.value = { ...defaultFineTuneAdjustments }
  }
  
  showFineTuneModal.value = true
}

const closeFineTuneModal = () => {
  showFineTuneModal.value = false
  isFineTuning.value = false
}

const resetFineTune = () => {
  fineTuneAdjustments.value = { ...defaultFineTuneAdjustments }
}

const applyFineTune = async () => {
  if (!selectedAvatar.value) return
  
  isFineTuning.value = true
  
  try {
    const response = await apiService.fineTuneAvatar(selectedAvatar.value.id, {
      faceWidth: fineTuneAdjustments.value.faceWidth,
      jawLine: fineTuneAdjustments.value.jawLine,
      cheekbones: fineTuneAdjustments.value.cheekbones,
      eyeSize: fineTuneAdjustments.value.eyeSize,
      eyeSpacing: fineTuneAdjustments.value.eyeSpacing,
      doubleEyelid: fineTuneAdjustments.value.doubleEyelid,
      noseSize: fineTuneAdjustments.value.noseSize,
      lipThickness: fineTuneAdjustments.value.lipThickness,
      wrinkles: fineTuneAdjustments.value.wrinkles
    })
    
    if (response.success) {
      if (selectedAvatar.value) {
        selectedAvatar.value.fineTuneAdjustments = { ...fineTuneAdjustments.value }
        selectedAvatar.value.status = 'fine-tuning'
        
        const index = digitalAvatars.value.findIndex(a => a.id === selectedAvatar.value!.id)
        if (index > -1) {
          digitalAvatars.value[index] = { ...selectedAvatar.value }
        }
      }
      
      alert('微调已应用，正在重新生成形象...')
    } else {
      alert('微调失败: ' + (response.error || '未知错误'))
    }
  } catch (error) {
    console.error('应用微调失败:', error)
    alert('微调失败: ' + (error instanceof Error ? error.message : '未知错误'))
  } finally {
    isFineTuning.value = false
  }
}

const saveAndCloseFineTune = async () => {
  await applyFineTune()
  closeFineTuneModal()
}

const showConfigModal = ref(false)
const isSavingConfig = ref(false)
const isTestingConnection = ref(false)

interface ConfigForm {
  openai: {
    apiKey: string
    baseUrl: string
    model: string
  }
  aliyun: {
    apiKey: string
    imageModel: string
    textModel: string
  }
}

const defaultConfigForm: ConfigForm = {
  openai: {
    apiKey: '',
    baseUrl: 'https://api.openai.com/v1',
    model: 'gpt-4o'
  },
  aliyun: {
    apiKey: '',
    imageModel: 'wanx-v1',
    textModel: 'qwen-plus'
  }
}

const configForm = ref<ConfigForm>({ ...defaultConfigForm })
const currentConfig = ref<any>(null)

const openConfigModal = async () => {
  configForm.value = { ...defaultConfigForm }
  currentConfig.value = null
  
  try {
    const response = await apiService.getConfig()
    if (response.success && response.data) {
      currentConfig.value = response.data
      
      configForm.value.openai.baseUrl = response.data.openai.baseUrl || defaultConfigForm.openai.baseUrl
      configForm.value.openai.model = response.data.openai.model || defaultConfigForm.openai.model
      
      configForm.value.aliyun.imageModel = response.data.aliyun.imageModel || defaultConfigForm.aliyun.imageModel
      configForm.value.aliyun.textModel = response.data.aliyun.textModel || defaultConfigForm.aliyun.textModel
    }
  } catch (error) {
    console.error('获取配置失败:', error)
  }
  
  showConfigModal.value = true
}

const closeConfigModal = () => {
  showConfigModal.value = false
  isSavingConfig.value = false
  isTestingConnection.value = false
}

const saveConfig = async () => {
  isSavingConfig.value = true
  
  try {
    const response = await apiService.updateConfig({
      openai: {
        apiKey: configForm.value.openai.apiKey || undefined,
        baseUrl: configForm.value.openai.baseUrl,
        model: configForm.value.openai.model
      },
      aliyun: {
        apiKey: configForm.value.aliyun.apiKey || undefined,
        imageModel: configForm.value.aliyun.imageModel,
        textModel: configForm.value.aliyun.textModel
      }
    })
    
    if (response.success) {
      alert('配置已保存')
      closeConfigModal()
    } else {
      alert('保存配置失败: ' + (response.error || '未知错误'))
    }
  } catch (error) {
    console.error('保存配置失败:', error)
    alert('保存配置失败: ' + (error instanceof Error ? error.message : '未知错误'))
  } finally {
    isSavingConfig.value = false
  }
}

const testConnection = async () => {
  isTestingConnection.value = true
  
  try {
    const response = await apiService.checkHealth()
    
    if (response.success) {
      alert('连接成功！后端服务运行正常。')
    } else {
      alert('连接失败: ' + (response.error || '未知错误'))
    }
  } catch (error) {
    console.error('测试连接失败:', error)
    alert('连接失败: ' + (error instanceof Error ? error.message : '未知错误'))
  } finally {
    isTestingConnection.value = false
  }
}

const noisePatternStyle = computed(() => ({
  backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox=%220 0 100 100%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22 opacity=%220.3%22/%3E%3C/svg%3E")`
}))

const dotPatternStyle = computed(() => ({
  backgroundImage: `url("data:image/svg+xml,%3Csvg width=%2260%22 height=%2260%22 viewBox=%220 0 60 60%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cg fill=%22none%22 fill-rule=%22evenodd%22%3E%3Cg fill=%22%23ffffff%22 fill-opacity=%220.4%22%3E%3Cpath d=%22M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
}))

const memoriesForHabitat = ref<MemoryListItem[]>([])
const loadingMemories = ref(false)
const memoryFilterAvatarId = ref('')
const memoryToDelete = ref<string | null>(null)
const showDeleteMemoryModal = ref(false)

const textMemoryCount = computed(() => 
  memoriesForHabitat.value.filter(m => m.type === 'text').length
)

const imageMemoryCount = computed(() => 
  memoriesForHabitat.value.filter(m => m.type === 'image').length
)

const videoMemoryCount = computed(() => 
  memoriesForHabitat.value.filter(m => m.type === 'video').length
)

const loadMemoriesForHabitat = async () => {
  loadingMemories.value = true
  try {
    const options: { avatarId?: string; type?: MemoryType } = {}
    
    if (memoryFilterAvatarId.value) {
      options.avatarId = memoryFilterAvatarId.value
    }

    const response = await apiService.getMemories(options)
    if (response.success && response.data) {
      memoriesForHabitat.value = response.data.memories
    } else {
      memoriesForHabitat.value = []
    }
  } catch (error) {
    console.error('加载记忆列表失败:', error)
    memoriesForHabitat.value = []
  } finally {
    loadingMemories.value = false
  }
}

const goToCreateMemory = () => {
  router.push('/memory/create')
}

const getMemoryTypeIcon = (type: MemoryType) => {
  const icons = {
    text: 'material-symbols:edit-note',
    image: 'material-symbols:image',
    video: 'material-symbols:videocam'
  }
  return icons[type] || icons.text
}

const getAvatarNameForMemory = (avatarId: string) => {
  const avatar = digitalAvatars.value.find(a => a.id === avatarId)
  return avatar ? avatar.name : '未知数字人'
}

const formatMemoryDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const viewMemoryDetail = (memoryId: string) => {
  router.push(`/memory/edit/${memoryId}`)
}

const editMemoryForHabitat = (memoryId: string) => {
  router.push(`/memory/edit/${memoryId}`)
}

const confirmDeleteMemory = (memoryId: string) => {
  memoryToDelete.value = memoryId
  showDeleteMemoryModal.value = true
}

const deleteMemoryForHabitat = async () => {
  if (!memoryToDelete.value) return
  
  try {
    const response = await apiService.deleteMemory(memoryToDelete.value)
    if (response.success) {
      const index = memoriesForHabitat.value.findIndex(m => m.id === memoryToDelete.value)
      if (index > -1) {
        memoriesForHabitat.value.splice(index, 1)
      }
      showDeleteMemoryModal.value = false
      memoryToDelete.value = null
    } else {
      alert('删除记忆失败: ' + (response.error || '未知错误'))
    }
  } catch (error) {
    console.error('删除记忆失败:', error)
    alert('删除记忆失败: ' + (error instanceof Error ? error.message : '未知错误'))
  }
}
</script>