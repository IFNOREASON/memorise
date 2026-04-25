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
        <div class="w-80 flex-shrink-0 bg-white rounded-2xl shadow-soft border border-stone-100 flex flex-col overflow-hidden">
          <div class="p-4 border-b border-[#E8D5C4] flex items-center justify-between">
            <h3 class="font-bold text-[#5C4A3A] font-serif">数字人列表</h3>
            <button @click="showCreateModal = true" class="w-8 h-8 bg-[#8B6F4E] rounded-full flex items-center justify-center text-white hover:bg-[#6B5342] transition-colors">
              <Icon icon="solar:plus-bold" class="text-lg" />
            </button>
          </div>

          <div class="flex-1 overflow-y-auto p-3 space-y-2">
            <div v-for="avatar in digitalAvatars" :key="avatar.id"
              class="p-3 rounded-xl cursor-pointer transition-all hover:bg-[#E8D5C4]/30 group"
              :class="[
                selectedAvatar?.id === avatar.id ? 'bg-[#E8D5C4] border border-[#D4A574]' : 'bg-transparent border border-transparent'
              ]">
              <div class="flex items-center space-x-3">
                <div @click.stop="selectedAvatar = avatar" class="relative cursor-pointer">
                  <div class="w-12 h-12 rounded-full overflow-hidden bg-gray-200 border-2"
                       :class="[
                         selectedAvatar?.id === avatar.id ? 'border-[#8B6F4E]' : 'border-gray-200'
                       ]">
                    <img :src="avatar.avatar" class="w-full h-full object-cover" :alt="avatar.name">
                  </div>
                  <div v-if="avatar.status === 'active'" class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                  <div v-else-if="avatar.status === 'training'" class="absolute bottom-0 right-0 w-3 h-3 bg-amber-400 rounded-full border-2 border-white"></div>
                </div>
                <div @click.stop="selectedAvatar = avatar" class="flex-1 min-w-0 cursor-pointer">
                  <div class="flex items-center space-x-2">
                    <h4 class="font-semibold text-sm text-gray-800 truncate">{{ avatar.name }}</h4>
                    <span v-if="avatar.status === 'active'" class="px-2 py-0.5 bg-green-100 text-green-700 text-[10px] rounded-full">已激活</span>
                    <span v-else-if="avatar.status === 'training'" class="px-2 py-0.5 bg-amber-100 text-amber-700 text-[10px] rounded-full">训练中</span>
                    <span v-else class="px-2 py-0.5 bg-gray-100 text-gray-500 text-[10px] rounded-full">未激活</span>
                  </div>
                  <p class="text-xs text-gray-500 mt-0.5">{{ avatar.relationship }}</p>
                  <div v-if="avatar.status === 'training'" class="w-full bg-gray-100 rounded-full h-1 mt-1">
                    <div class="bg-amber-400 h-1 rounded-full transition-all" 
                         :style="{ width: avatar.trainingProgress + '%' }"></div>
                  </div>
                </div>
                <button @click.stop="confirmDeleteAvatar(avatar)" 
                        class="w-7 h-7 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 hover:bg-red-100 transition-all">
                  <Icon icon="solar:trash-bin-trash-bold" class="text-red-500 text-sm" />
                </button>
              </div>
            </div>
          </div>

          <div class="p-4 border-t border-[#E8D5C4]">
            <div class="text-center text-xs text-gray-400">
              共 {{ digitalAvatars.length }} 个数字人
            </div>
          </div>
        </div>

        <div class="flex-1 flex flex-col gap-6">
          <div class="flex-1 bg-white rounded-2xl shadow-soft border border-stone-100 overflow-hidden flex flex-col">
            <div v-if="selectedAvatar" class="flex-1 flex flex-col">
              <div class="p-4 border-b border-[#E8D5C4] flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <h3 class="font-bold text-lg text-[#5C4A3A] font-serif">{{ selectedAvatar.name }}</h3>
                  <span class="px-2 py-0.5 bg-[#E8D5C4] text-[#8B6F4E] text-xs rounded-full">{{ selectedAvatar.relationship }}</span>
                </div>
                <div class="flex items-center space-x-2">
                  <div class="flex bg-[#E8D5C4]/50 rounded-lg p-1 mr-2">
                    <button @click="displayMode = '2d'" 
                            class="px-3 py-1.5 rounded-md text-xs font-medium transition-all"
                            :class="[
                              displayMode === '2d' ? 'bg-white text-[#8B6F4E] shadow-sm' : 'text-gray-500 hover:text-gray-700'
                            ]">
                      2D
                    </button>
                    <button @click="displayMode = '3d'" 
                            class="px-3 py-1.5 rounded-md text-xs font-medium transition-all"
                            :class="[
                              displayMode === '3d' ? 'bg-white text-[#8B6F4E] shadow-sm' : 'text-gray-500 hover:text-gray-700'
                            ]">
                      3D
                    </button>
                    <button @click="displayMode = 'wireframe'" 
                            class="px-3 py-1.5 rounded-md text-xs font-medium transition-all"
                            :class="[
                              displayMode === 'wireframe' ? 'bg-white text-[#8B6F4E] shadow-sm' : 'text-gray-500 hover:text-gray-700'
                            ]">
                      线框
                    </button>
                  </div>
                  <button v-if="displayMode !== '2d'" 
                          @click="autoRotate3D = !autoRotate3D"
                          class="w-8 h-8 rounded-lg flex items-center justify-center transition-colors"
                          :class="[
                            autoRotate3D ? 'bg-[#8B6F4E] text-white' : 'bg-[#E8D5C4]/50 text-gray-600'
                          ]"
                          :title="autoRotate3D ? '停止旋转' : '开始旋转'">
                    <Icon :icon="autoRotate3D ? 'solar:pause-bold' : 'solar:play-bold'" />
                  </button>
                  <button class="px-4 py-2 bg-[#E8D5C4] text-[#8B6F4E] rounded-lg text-sm font-medium hover:bg-[#D4A574] transition-colors flex items-center space-x-1">
                    <Icon icon="solar:chat-round-dots-bold" class="text-base" />
                    <span>对话</span>
                  </button>
                  <button class="px-4 py-2 bg-[#8B6F4E] text-white rounded-lg text-sm font-medium hover:bg-[#6B5342] transition-colors flex items-center space-x-1">
                    <Icon icon="solar:phone-bold" class="text-base" />
                    <span>通话</span>
                  </button>
                </div>
              </div>

              <div class="flex-1 flex bg-gradient-to-b from-[#FAF7F2] to-[#F5E6D3] relative overflow-hidden">
                <div class="absolute inset-0 opacity-10" :style="dotPatternStyle"></div>
                
                <div v-if="displayMode === '2d'" class="flex-1 flex items-center justify-center relative z-10 p-8">
                  <div class="relative">
                    <div class="absolute inset-0 bg-[#8B6F4E]/10 rounded-full animate-pulse" 
                         :style="{ transform: 'scale(1.3)', width: avatarDisplaySize + 'px', height: avatarDisplaySize + 'px', left: -avatarDisplaySize * 0.15 + 'px', top: -avatarDisplaySize * 0.15 + 'px' }"></div>
                    
                    <div :style="{ width: avatarDisplaySize + 'px', height: avatarDisplaySize + 'px' }"
                         class="relative rounded-full overflow-hidden border-4 border-white shadow-glow transition-all duration-500"
                         :class="[
                           selectedAvatar.status === 'active' ? 'border-[#8B6F4E]' : 'border-gray-300'
                         ]">
                      <img :src="selectedAvatar.avatar" class="w-full h-full object-cover" :alt="selectedAvatar.name"
                           :class="{ 'grayscale': selectedAvatar.status === 'inactive', 'opacity-70': selectedAvatar.status === 'inactive' }">
                      
                      <div v-if="selectedAvatar.status === 'active'" class="absolute inset-0 flex items-center justify-center">
                        <div class="absolute bottom-4 left-1/2 -translate-x-1/2 flex space-x-1">
                          <div v-for="i in 4" :key="i" class="w-1.5 bg-[#8B6F4E] rounded-full animate-sound-wave"
                               :style="{ 
                                 height: 8 + Math.random() * 12 + 'px',
                                 animationDelay: (i * 0.15) + 's'
                               }"></div>
                        </div>
                      </div>
                    </div>

                    <div v-if="selectedAvatar.status === 'active'" class="absolute -bottom-2 left-1/2 -translate-x-1/2 px-3 py-1 bg-green-500 text-white text-xs rounded-full flex items-center space-x-1 shadow-md">
                      <div class="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                      <span>在线</span>
                    </div>
                    <div v-else-if="selectedAvatar.status === 'training'" class="absolute -bottom-2 left-1/2 -translate-x-1/2 px-3 py-1 bg-amber-400 text-white text-xs rounded-full flex items-center space-x-1 shadow-md">
                      <Icon icon="solar:refresh-circle-bold" class="animate-spin text-sm" />
                      <span>训练中 {{ selectedAvatar.trainingProgress }}%</span>
                    </div>
                    <div v-else class="absolute -bottom-2 left-1/2 -translate-x-1/2 px-3 py-1 bg-gray-400 text-white text-xs rounded-full shadow-md">
                      <span>离线</span>
                    </div>
                  </div>
                </div>

                <div v-else class="flex-1 relative z-10">
                  <ThreeDModelViewer 
                    :model-url="selectedAvatar.modelUrl"
                    :background-color="0xFAF7F2"
                    :auto-rotate="autoRotate3D"
                    :wireframe="displayMode === 'wireframe'"
                    full-height
                    @loaded="onModelLoaded"
                    @error="onModelError"
                  />
                  
                  <div class="absolute bottom-4 left-1/2 -translate-x-1/2 z-20">
                    <div v-if="selectedAvatar.status === 'active'" class="px-4 py-2 bg-green-500 text-white text-sm rounded-full flex items-center space-x-2 shadow-md">
                      <div class="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                      <span>在线</span>
                    </div>
                    <div v-else-if="selectedAvatar.status === 'training'" class="px-4 py-2 bg-amber-400 text-white text-sm rounded-full flex items-center space-x-2 shadow-md">
                      <Icon icon="solar:refresh-circle-bold" class="animate-spin" />
                      <span>训练中 {{ selectedAvatar.trainingProgress }}%</span>
                    </div>
                    <div v-else class="px-4 py-2 bg-gray-400 text-white text-sm rounded-full shadow-md">
                      <span>离线</span>
                    </div>
                  </div>
                </div>

                <div class="w-80 bg-white/80 backdrop-blur border-l border-[#E8D5C4] p-6 overflow-y-auto">
                  <h4 class="font-bold text-[#5C4A3A] font-serif mb-4">基本信息</h4>
                  
                  <div class="space-y-4">
                    <div>
                      <label class="text-xs text-gray-400 block mb-1">姓名</label>
                      <p class="text-sm font-medium text-gray-800">{{ selectedAvatar.name }}</p>
                    </div>
                    <div>
                      <label class="text-xs text-gray-400 block mb-1">关系</label>
                      <p class="text-sm font-medium text-gray-800">{{ selectedAvatar.relationship }}</p>
                    </div>
                    <div>
                      <label class="text-xs text-gray-400 block mb-1">生卒年份</label>
                      <p class="text-sm font-medium text-gray-800">{{ selectedAvatar.birthYear }} - {{ selectedAvatar.deathYear || '在世' }}</p>
                    </div>
                    <div>
                      <label class="text-xs text-gray-400 block mb-1">训练度</label>
                      <div class="flex items-center space-x-2">
                        <div class="flex-1 bg-gray-100 rounded-full h-2">
                          <div class="bg-[#8B6F4E] h-2 rounded-full transition-all" 
                               :style="{ width: selectedAvatar.trainingProgress + '%' }"></div>
                        </div>
                        <span class="text-sm font-medium text-gray-800">{{ selectedAvatar.trainingProgress }}%</span>
                      </div>
                    </div>
                    <div>
                      <label class="text-xs text-gray-400 block mb-1">对话次数</label>
                      <p class="text-sm font-medium text-gray-800">{{ selectedAvatar.chatCount || 0 }} 次</p>
                    </div>
                    <div>
                      <label class="text-xs text-gray-400 block mb-1">最后互动</label>
                      <p class="text-sm font-medium text-gray-800">{{ selectedAvatar.lastInteraction || '暂无' }}</p>
                    </div>
                    <div v-if="displayMode !== '2d'">
                      <label class="text-xs text-gray-400 block mb-1">3D模型</label>
                      <p class="text-sm text-gray-500">
                        {{ selectedAvatar.modelUrl ? '已加载自定义模型' : '使用默认占位模型' }}
                      </p>
                      <p class="text-xs text-gray-400 mt-1">
                        提示：可通过设置 modelUrl 加载自定义 GLB/GLTF 模型
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="flex-1 flex items-center justify-center bg-gradient-to-b from-[#FAF7F2] to-[#F5E6D3]">
              <div class="text-center">
                <div class="w-32 h-32 mx-auto mb-6 bg-[#E8D5C4] rounded-full flex items-center justify-center">
                  <Icon icon="solar:user-square-bold" class="text-5xl text-[#8B6F4E]" />
                </div>
                <h3 class="text-xl font-bold text-[#5C4A3A] font-serif mb-2">选择或创建数字人</h3>
                <p class="text-sm text-gray-500 mb-6">从左侧列表选择一个数字人，或创建新的数字生命</p>
                <button @click="showCreateModal = true" class="px-6 py-3 bg-[#8B6F4E] text-white rounded-xl font-medium hover:bg-[#6B5342] transition-colors flex items-center space-x-2 mx-auto">
                  <Icon icon="solar:plus-bold" class="text-lg" />
                  <span>创建新数字人</span>
                </button>
              </div>
            </div>
          </div>

          <div v-if="selectedAvatar" class="bg-white rounded-2xl shadow-soft border border-stone-100 overflow-hidden">
            <button @click="customizationPanelExpanded = !customizationPanelExpanded"
                    class="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
              <div class="flex items-center space-x-3">
                <Icon icon="solar:palette-bold" class="text-xl text-[#8B6F4E]" />
                <h3 class="font-bold text-lg text-[#5C4A3A] font-serif">形象定制</h3>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-sm text-gray-400">{{ customizationPanelExpanded ? '点击收起' : '点击展开' }}</span>
                <Icon :icon="customizationPanelExpanded ? 'solar:arrow-up-outline' : 'solar:arrow-down-outline'" 
                      class="text-lg text-gray-400 transition-transform" />
              </div>
            </button>

            <div v-if="customizationPanelExpanded" class="px-6 pb-6 pt-2">
              <div class="flex items-center justify-between mb-6">
                <div class="flex items-center space-x-2">
                  <button v-for="tab in customizationTabs" :key="tab.id"
                    @click="activeCustomizationTab = tab.id"
                    class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
                    :class="[
                      activeCustomizationTab === tab.id 
                        ? 'bg-[#8B6F4E] text-white' 
                        : 'bg-[#E8D5C4]/50 text-gray-600 hover:bg-[#E8D5C4]'
                    ]">
                    <Icon :icon="tab.icon" class="mr-1" />
                    {{ tab.label }}
                  </button>
                </div>
              </div>

              <div v-if="activeCustomizationTab === 'appearance'" class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div v-for="option in appearanceOptions" :key="option.id"
                  @click="selectAppearanceOption(option)"
                  class="p-4 rounded-xl border-2 cursor-pointer transition-all hover:shadow-md"
                  :class="[
                    selectedAppearance.includes(option.id) 
                      ? 'border-[#8B6F4E] bg-[#E8D5C4]/30' 
                      : 'border-gray-200 bg-white'
                  ]">
                  <div class="w-full aspect-square rounded-lg bg-gray-100 mb-3 flex items-center justify-center overflow-hidden">
                    <img v-if="option.preview" :src="option.preview" class="w-full h-full object-cover" :alt="option.label">
                    <Icon v-else :icon="option.icon" class="text-3xl text-gray-400" />
                  </div>
                  <p class="text-sm font-medium text-center text-gray-800">{{ option.label }}</p>
                </div>
              </div>

              <div v-if="activeCustomizationTab === 'voice'" class="space-y-4">
                <div v-for="voice in voiceOptions" :key="voice.id"
                  @click="selectedVoice = voice.id"
                  class="p-4 rounded-xl border-2 cursor-pointer transition-all hover:shadow-md flex items-center space-x-4"
                  :class="[
                    selectedVoice === voice.id 
                      ? 'border-[#8B6F4E] bg-[#E8D5C4]/30' 
                      : 'border-gray-200 bg-white'
                  ]">
                  <div class="w-12 h-12 rounded-full bg-[#E8D5C4] flex items-center justify-center">
                    <Icon icon="solar:volume-high-bold" class="text-xl text-[#8B6F4E]" />
                  </div>
                  <div class="flex-1">
                    <p class="font-medium text-gray-800">{{ voice.label }}</p>
                    <p class="text-sm text-gray-500">{{ voice.description }}</p>
                  </div>
                  <button @click.stop="playVoiceSample(voice.id)" class="w-10 h-10 rounded-full bg-white border border-gray-200 flex items-center justify-center hover:bg-[#E8D5C4] transition-colors">
                    <Icon icon="solar:play-circle-bold" class="text-lg text-[#8B6F4E]" />
                  </button>
                </div>
              </div>

              <div v-if="activeCustomizationTab === 'personality'" class="space-y-6">
                <div>
                  <label class="text-sm font-medium text-gray-700 block mb-3">性格特点</label>
                  <div class="flex flex-wrap gap-2">
                    <span v-for="trait in personalityTraits" :key="trait.id"
                      @click="togglePersonalityTrait(trait.id)"
                      class="px-4 py-2 rounded-full text-sm cursor-pointer transition-all"
                      :class="[
                        selectedPersonalityTraits.includes(trait.id)
                          ? 'bg-[#8B6F4E] text-white'
                          : 'bg-[#E8D5C4]/50 text-gray-600 hover:bg-[#E8D5C4]'
                      ]">
                      {{ trait.label }}
                    </span>
                  </div>
                </div>
                
                <div>
                  <label class="text-sm font-medium text-gray-700 block mb-2">语气风格</label>
                  <input type="range" min="0" max="100" v-model="toneStyle" 
                         class="w-full h-2 bg-[#E8D5C4] rounded-lg appearance-none cursor-pointer">
                  <div class="flex justify-between text-xs text-gray-400 mt-1">
                    <span>严肃正式</span>
                    <span>温和亲切</span>
                    <span>活泼开朗</span>
                  </div>
                </div>

                <div>
                  <label class="text-sm font-medium text-gray-700 block mb-2">说话语速</label>
                  <input type="range" min="0" max="100" v-model="speechSpeed" 
                         class="w-full h-2 bg-[#E8D5C4] rounded-lg appearance-none cursor-pointer">
                  <div class="flex justify-between text-xs text-gray-400 mt-1">
                    <span>缓慢</span>
                    <span>适中</span>
                    <span>快速</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showCreateModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-[#E8D5C4] flex items-center justify-between">
          <h3 class="text-xl font-bold text-[#5C4A3A] font-serif">创建新数字人</h3>
          <button @click="showCreateModal = false" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="solar:close-bold" class="text-gray-500" />
          </button>
        </div>

        <div class="p-6 space-y-4">
          <div>
            <label class="text-sm font-medium text-gray-700 block mb-2">姓名 *</label>
            <input type="text" v-model="newAvatar.name" placeholder="请输入姓名"
                   class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all">
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-2">关系 *</label>
              <select v-model="newAvatar.relationship"
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
                <button @click="newAvatar.gender = 'male'" 
                        class="flex-1 py-3 rounded-xl border-2 transition-all"
                        :class="[
                          newAvatar.gender === 'male' 
                            ? 'border-[#8B6F4E] bg-[#E8D5C4] text-[#8B6F4E]' 
                            : 'border-gray-200 text-gray-600 hover:border-[#E8D5C4]'
                        ]">
                  <Icon icon="solar:user-bold" class="mr-1" />
                  男
                </button>
                <button @click="newAvatar.gender = 'female'" 
                        class="flex-1 py-3 rounded-xl border-2 transition-all"
                        :class="[
                          newAvatar.gender === 'female' 
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
              <label class="text-sm font-medium text-gray-700 block mb-2">出生年份</label>
              <input type="text" v-model="newAvatar.birthYear" placeholder="如: 1928"
                     class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all">
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-2">逝世年份</label>
              <input type="text" v-model="newAvatar.deathYear" placeholder="如: 2018（可选）"
                     class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all">
            </div>
          </div>

          <div>
            <label class="text-sm font-medium text-gray-700 block mb-2">头像照片</label>
            <div class="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center cursor-pointer hover:border-[#8B6F4E] transition-colors">
              <Icon icon="solar:upload-square-bold" class="text-4xl text-gray-400 mb-2" />
              <p class="text-sm text-gray-500">点击或拖拽上传照片</p>
              <p class="text-xs text-gray-400 mt-1">支持 JPG、PNG 格式，建议使用清晰的面部照片</p>
            </div>
          </div>

          <div>
            <label class="text-sm font-medium text-gray-700 block mb-2">简介</label>
            <textarea v-model="newAvatar.description" rows="3" placeholder="请输入一些关于这位亲人的描述..."
                      class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent transition-all resize-none"></textarea>
          </div>
        </div>

        <div class="p-6 border-t border-[#E8D5C4] flex space-x-3">
          <button @click="showCreateModal = false" class="flex-1 py-3 border border-gray-200 rounded-xl text-gray-600 font-medium hover:bg-gray-50 transition-colors">
            取消
          </button>
          <button @click="createNewAvatar" class="flex-1 py-3 bg-[#8B6F4E] text-white rounded-xl font-medium hover:bg-[#6B5342] transition-colors">
            创建数字人
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
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import ThreeDModelViewer from './ThreeDModelViewer.vue'

const router = useRouter()

interface DigitalAvatar {
  id: string
  name: string
  relationship: string
  avatar: string
  modelUrl?: string
  status: 'active' | 'training' | 'inactive'
  trainingProgress: number
  birthYear: string
  deathYear?: string
  chatCount?: number
  lastInteraction?: string
}

interface NavItem {
  id: string
  label: string
  icon: string
}

interface CustomizationTab {
  id: string
  label: string
  icon: string
}

interface AppearanceOption {
  id: string
  label: string
  icon: string
  preview?: string
}

interface VoiceOption {
  id: string
  label: string
  description: string
}

interface PersonalityTrait {
  id: string
  label: string
}

const digitalAvatars = ref<DigitalAvatar[]>([
  {
    id: '1',
    name: '祖父 · 张明远',
    relationship: '祖父',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face',
    modelUrl: '/models/girl_speedsculpt.glb',
    status: 'active',
    trainingProgress: 98,
    birthYear: '1928',
    deathYear: '2018',
    chatCount: 2345,
    lastInteraction: '3天前'
  },
  {
    id: '2',
    name: '祖母 · 李淑华',
    relationship: '祖母',
    avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=face',
    modelUrl: undefined,
    status: 'training',
    trainingProgress: 76,
    birthYear: '1932',
    deathYear: '2020',
    chatCount: 0
  },
  {
    id: '3',
    name: '父亲 · 张建国',
    relationship: '父亲',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face',
    modelUrl: undefined,
    status: 'inactive',
    trainingProgress: 0,
    birthYear: '1958',
    chatCount: 0
  }
])

const selectedAvatar = ref<DigitalAvatar | null>(null)
const displayMode = ref<'2d' | '3d' | 'wireframe'>('3d')
const autoRotate3D = ref(true)
const customizationPanelExpanded = ref(false)

const navItems: NavItem[] = [
  { id: 'home', label: '首页', icon: 'solar:home-2-bold' },
  { id: 'family', label: '家承', icon: 'solar:tree-bold-duotone' },
  { id: 'gallery', label: '影集', icon: 'solar:gallery-wide-bold-duotone' },
  { id: 'habitat', label: '生境', icon: 'solar:magic-stick-3-bold-duotone' },
  { id: 'chat', label: '语伴', icon: 'solar:chat-round-dots-bold-duotone' },
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

const customizationTabs: CustomizationTab[] = [
  { id: 'appearance', label: '外观', icon: 'solar:user-square-bold' },
  { id: 'voice', label: '声音', icon: 'solar:volume-high-bold' },
  { id: 'personality', label: '性格', icon: 'solar:heart-bold' },
]

const activeCustomizationTab = ref('appearance')

const appearanceOptions: AppearanceOption[] = [
  { id: 'formal', label: '正装风格', icon: 'solar:user-bold', preview: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face' },
  { id: 'casual', label: '休闲风格', icon: 'solar:user-bold', preview: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&h=200&fit=crop&crop=face' },
  { id: 'traditional', label: '传统服饰', icon: 'solar:user-heart-bold', preview: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&crop=face' },
  { id: 'modern', label: '现代风格', icon: 'solar:user-bold', preview: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face' },
]

const selectedAppearance = ref<string[]>(['formal'])

const selectAppearanceOption = (option: AppearanceOption) => {
  const index = selectedAppearance.value.indexOf(option.id)
  if (index > -1) {
    selectedAppearance.value.splice(index, 1)
  } else {
    selectedAppearance.value = [option.id]
  }
}

const voiceOptions: VoiceOption[] = [
  { id: 'deep', label: '深沉男声', description: '低音频，稳重威严' },
  { id: 'warm', label: '温暖男声', description: '中音域，亲切和蔼' },
  { id: 'soft', label: '柔和女声', description: '温柔细腻，娓娓道来' },
  { id: 'bright', label: '明亮女声', description: '清脆悦耳，活力四射' },
]

const selectedVoice = ref('warm')

const playVoiceSample = (voiceId: string) => {
  console.log('Playing voice sample:', voiceId)
}

const personalityTraits: PersonalityTrait[] = [
  { id: 'kind', label: '善良' },
  { id: 'strict', label: '严格' },
  { id: 'humorous', label: '幽默' },
  { id: 'serious', label: '严肃' },
  { id: 'patient', label: '耐心' },
  { id: 'decisive', label: '果断' },
  { id: 'gentle', label: '温和' },
  { id: 'wise', label: '睿智' },
]

const selectedPersonalityTraits = ref<string[]>(['kind', 'wise', 'gentle'])

const togglePersonalityTrait = (traitId: string) => {
  const index = selectedPersonalityTraits.value.indexOf(traitId)
  if (index > -1) {
    selectedPersonalityTraits.value.splice(index, 1)
  } else {
    selectedPersonalityTraits.value.push(traitId)
  }
}

const toneStyle = ref(50)
const speechSpeed = ref(50)

const avatarDisplaySize = computed(() => {
  return 280
})

const showCreateModal = ref(false)
const showDeleteModal = ref(false)
const avatarToDelete = ref<DigitalAvatar | null>(null)

const newAvatar = ref({
  name: '',
  relationship: '',
  gender: 'male' as 'male' | 'female',
  birthYear: '',
  deathYear: '',
  description: ''
})

const confirmDeleteAvatar = (avatar: DigitalAvatar) => {
  avatarToDelete.value = avatar
  showDeleteModal.value = true
}

const onModelLoaded = () => {
  console.log('3D模型加载成功')
}

const onModelError = (error: string) => {
  console.warn('3D模型加载失败:', error)
}

const deleteAvatar = () => {
  if (!avatarToDelete.value) return
  
  const index = digitalAvatars.value.findIndex(a => a.id === avatarToDelete.value!.id)
  if (index > -1) {
    digitalAvatars.value.splice(index, 1)
    
    if (selectedAvatar.value?.id === avatarToDelete.value!.id) {
      selectedAvatar.value = null
    }
  }
  
  showDeleteModal.value = false
  avatarToDelete.value = null
}

const createNewAvatar = () => {
  if (!newAvatar.value.name || !newAvatar.value.relationship) {
    alert('请填写必填项')
    return
  }

  const avatarImages = [
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face',
    'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=face',
    'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face',
  ]

  const newId = String(digitalAvatars.value.length + 1)
  const newDigitalAvatar: DigitalAvatar = {
    id: newId,
    name: newAvatar.value.name,
    relationship: newAvatar.value.relationship,
    avatar: avatarImages[parseInt(newId) % avatarImages.length],
    status: 'inactive',
    trainingProgress: 0,
    birthYear: newAvatar.value.birthYear,
    deathYear: newAvatar.value.deathYear || undefined,
    chatCount: 0
  }

  digitalAvatars.value.push(newDigitalAvatar)
  selectedAvatar.value = newDigitalAvatar
  showCreateModal.value = false

  newAvatar.value = {
    name: '',
    relationship: '',
    gender: 'male',
    birthYear: '',
    deathYear: '',
    description: ''
  }
}

const noisePatternStyle = computed(() => ({
  backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox=%220 0 100 100%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22 opacity=%220.3%22/%3E%3C/svg%3E")`
}))

const dotPatternStyle = computed(() => ({
  backgroundImage: `url("data:image/svg+xml,%3Csvg width=%2260%22 height=%2260%22 viewBox=%220 0 60 60%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cg fill=%22none%22 fill-rule=%22evenodd%22%3E%3Cg fill=%22%23ffffff%22 fill-opacity=%220.4%22%3E%3Cpath d=%22M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
}))
</script>
