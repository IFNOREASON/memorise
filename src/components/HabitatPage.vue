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
              <p class="text-sm text-gray-500 mb-6">选择一种方式创建您的数字人形象，也可以后续进行微调</p>

              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                  <div class="h-5"></div>
                </div>

                <div @click="newAvatarForm.generationMethod = 'manual'"
                     class="p-6 rounded-2xl border-2 cursor-pointer transition-all hover:shadow-md"
                     :class="[
                       newAvatarForm.generationMethod === 'manual' 
                         ? 'border-[#8B6F4E] bg-[#E8D5C4]/30' 
                         : 'border-gray-200 bg-white hover:border-[#E8D5C4]'
                     ]">
                  <div class="w-16 h-16 rounded-full bg-[#E8D5C4] flex items-center justify-center mb-4 mx-auto">
                    <Icon icon="solar:slider-horizontal-bold" class="text-3xl text-[#8B6F4E]" />
                  </div>
                  <h5 class="font-bold text-center text-[#5C4A3A] font-serif mb-2">手动微调</h5>
                  <p class="text-sm text-gray-500 text-center mb-4">从基础模板开始，通过滑块精确调整各项面部特征</p>
                  <div class="h-5"></div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="currentStep === 3 && newAvatarForm.generationMethod === 'photo'" class="space-y-6">
            <div>
              <h4 class="text-lg font-bold text-[#5C4A3A] font-serif mb-2">上传照片</h4>
              <p class="text-sm text-gray-500 mb-4">请上传1-5张不同角度的清晰面部照片，建议包含正面、侧面、45度角等</p>
              
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

              <div class="mt-4 p-4 bg-[#FAF7F2] rounded-xl">
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

            <div v-if="newAvatarForm.uploadedPhotos.length > 0" class="space-y-4">
              <h5 class="font-medium text-[#5C4A3A]">照片分析预览</h5>
              <div class="grid grid-cols-2 gap-4">
                <div class="p-4 bg-[#FAF7F2] rounded-xl">
                  <h6 class="text-sm font-medium text-gray-700 mb-2">检测到的特征</h6>
                  <div class="flex flex-wrap gap-2">
                    <span class="px-3 py-1 bg-[#E8D5C4] text-[#8B6F4E] text-xs rounded-full">面部轮廓清晰</span>
                    <span class="px-3 py-1 bg-[#E8D5C4] text-[#8B6F4E] text-xs rounded-full">五官特征明显</span>
                    <span class="px-3 py-1 bg-[#E8D5C4] text-[#8B6F4E] text-xs rounded-full">肤色正常</span>
                  </div>
                </div>
                <div class="p-4 bg-[#FAF7F2] rounded-xl">
                  <h6 class="text-sm font-medium text-gray-700 mb-2">生成质量预估</h6>
                  <div class="flex items-center space-x-3">
                    <div class="flex-1">
                      <div class="flex items-center justify-between text-xs text-gray-500 mb-1">
                        <span>生成准确度</span>
                        <span class="text-[#8B6F4E] font-medium">
                          {{ newAvatarForm.uploadedPhotos.length >= 3 ? '高' : newAvatarForm.uploadedPhotos.length >= 2 ? '中' : '低' }}
                        </span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="bg-[#8B6F4E] h-2 rounded-full transition-all" 
                             :style="{ width: (newAvatarForm.uploadedPhotos.length * 20) + '%' }"></div>
                      </div>
                    </div>
                  </div>
                  <p class="text-xs text-gray-400 mt-2">
                    {{ newAvatarForm.uploadedPhotos.length >= 3 ? '照片数量充足，生成效果预计很好' : newAvatarForm.uploadedPhotos.length >= 2 ? '建议再上传1张照片以获得更好效果' : '建议上传更多照片以提高生成质量' }}
                  </p>
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

          <div v-if="currentStep === 3 && newAvatarForm.generationMethod === 'manual'" class="space-y-6">
            <div>
              <h4 class="text-lg font-bold text-[#5C4A3A] font-serif mb-2">手动微调</h4>
              <p class="text-sm text-gray-500 mb-4">通过滑块精确调整各项面部特征，打造专属形象</p>

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
                          <span class="text-xs text-[#8B6F4E]">{{ newAvatarForm.manualAdjust.faceWidth }}%</span>
                        </div>
                        <input type="range" min="0" max="100" v-model="newAvatarForm.manualAdjust.faceWidth" 
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
                          <span class="text-xs text-[#8B6F4E]">{{ newAvatarForm.manualAdjust.jawLine }}%</span>
                        </div>
                        <input type="range" min="0" max="100" v-model="newAvatarForm.manualAdjust.jawLine" 
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
                          <span class="text-xs text-[#8B6F4E]">{{ newAvatarForm.manualAdjust.cheekbones }}%</span>
                        </div>
                        <input type="range" min="0" max="100" v-model="newAvatarForm.manualAdjust.cheekbones" 
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
                          <span class="text-xs text-[#8B6F4E]">{{ newAvatarForm.manualAdjust.eyeSize }}%</span>
                        </div>
                        <input type="range" min="0" max="100" v-model="newAvatarForm.manualAdjust.eyeSize" 
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
                          <span class="text-xs text-[#8B6F4E]">{{ newAvatarForm.manualAdjust.eyeSpacing }}%</span>
                        </div>
                        <input type="range" min="0" max="100" v-model="newAvatarForm.manualAdjust.eyeSpacing" 
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
                          <span class="text-xs text-[#8B6F4E]">{{ newAvatarForm.manualAdjust.doubleEyelid }}%</span>
                        </div>
                        <input type="range" min="0" max="100" v-model="newAvatarForm.manualAdjust.doubleEyelid" 
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
                          <span class="text-xs text-[#8B6F4E]">{{ newAvatarForm.manualAdjust.noseSize }}%</span>
                        </div>
                        <input type="range" min="0" max="100" v-model="newAvatarForm.manualAdjust.noseSize" 
                               class="w-full h-2 bg-[#E8D5C4] rounded-lg appearance-none cursor-pointer">
                      </div>

                      <div>
                        <div class="flex items-center justify-between mb-2">
                          <label class="text-sm text-gray-700">嘴唇厚度</label>
                          <span class="text-xs text-[#8B6F4E]">{{ newAvatarForm.manualAdjust.lipThickness }}%</span>
                        </div>
                        <input type="range" min="0" max="100" v-model="newAvatarForm.manualAdjust.lipThickness" 
                               class="w-full h-2 bg-[#E8D5C4] rounded-lg appearance-none cursor-pointer">
                      </div>

                      <div>
                        <div class="flex items-center justify-between mb-2">
                          <label class="text-sm text-gray-700">皱纹程度</label>
                          <span class="text-xs text-[#8B6F4E]">{{ newAvatarForm.manualAdjust.wrinkles }}%</span>
                        </div>
                        <input type="range" min="0" max="100" v-model="newAvatarForm.manualAdjust.wrinkles" 
                               class="w-full h-2 bg-[#E8D5C4] rounded-lg appearance-none cursor-pointer">
                      </div>
                    </div>
                  </div>
                </div>

                <div class="lg:col-span-1">
                  <div class="sticky top-4">
                    <h5 class="font-medium text-[#5C4A3A] mb-4 text-center">实时预览</h5>
                    <div class="aspect-[3/4] bg-gradient-to-b from-[#FAF7F2] to-[#F5E6D3] rounded-2xl flex items-center justify-center relative overflow-hidden">
                      <div class="absolute inset-0 opacity-10" :style="dotPatternStyle"></div>
                      <div class="text-center z-10">
                        <div class="w-32 h-32 mx-auto mb-4 rounded-full bg-[#E8D5C4] flex items-center justify-center">
                          <Icon icon="solar:user-square-bold" class="text-5xl text-[#8B6F4E]" />
                        </div>
                        <p class="text-sm text-gray-500">预览效果</p>
                        <p class="text-xs text-gray-400 mt-1">调整滑块查看变化</p>
                      </div>
                    </div>

                    <div class="mt-4 space-y-2">
                      <button class="w-full py-2 bg-[#E8D5C4] text-[#8B6F4E] rounded-lg text-sm font-medium hover:bg-[#D4A574] transition-colors flex items-center justify-center space-x-1">
                        <Icon icon="solar:refresh-circle-bold" class="text-sm" />
                        <span>重置为默认</span>
                      </button>
                      <button class="w-full py-2 border border-[#E8D5C4] text-[#8B6F4E] rounded-lg text-sm font-medium hover:bg-[#E8D5C4]/50 transition-colors flex items-center justify-center space-x-1">
                        <Icon icon="solar:save-2-bold" class="text-sm" />
                        <span>保存为预设</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
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
                      {{ newAvatarForm.generationMethod === 'photo' ? '照片生成' : 
                         newAvatarForm.generationMethod === 'text' ? '文字描述生成' : '手动微调' }}
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
                    形象生成方式（照片生成、文字描述生成、手动微调）以及相关参数在创建后不可修改。如需调整形象，请重新创建新的数字人形象。
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
                <button @click="editAvatar(selectedAvatar)" class="w-full py-3 border border-[#E8D5C4] text-[#8B6F4E] rounded-xl font-medium hover:bg-[#E8D5C4]/50 transition-colors flex items-center justify-center space-x-2">
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
                      {{ selectedAvatar.generationMethod === 'photo' ? '照片生成' : 
                         selectedAvatar.generationMethod === 'text' ? '文字描述生成' : '手动微调' }}
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
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import ThreeDModelViewer from './ThreeDModelViewer.vue'

const router = useRouter()

const MAX_AVATARS = 5

interface DigitalAvatar {
  id: string
  name: string
  relationship: string
  gender: 'male' | 'female'
  avatar?: string
  modelUrl?: string
  status: 'active' | 'training' | 'generating' | 'inactive'
  progress: number
  birthYear?: string
  deathYear?: string
  chatCount?: number
  lastInteraction?: string
  generationMethod?: 'photo' | 'text' | 'manual'
  description?: string
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

const digitalAvatars = ref<DigitalAvatar[]>([
  {
    id: '1',
    name: '祖父 · 张明远',
    relationship: '祖父',
    gender: 'male',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face',
    modelUrl: '/models/girl_speedsculpt.glb',
    status: 'active',
    progress: 98,
    birthYear: '1928',
    deathYear: '2018',
    chatCount: 2345,
    lastInteraction: '3天前',
    generationMethod: 'photo',
    description: '一位慈祥的祖父，一生勤劳善良，热爱家庭，对子孙后代充满关爱。'
  },
  {
    id: '2',
    name: '祖母 · 李淑华',
    relationship: '祖母',
    gender: 'female',
    avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=face',
    modelUrl: undefined,
    status: 'training',
    progress: 76,
    birthYear: '1932',
    deathYear: '2020',
    chatCount: 0,
    generationMethod: 'text'
  }
])

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
  if (!files) return

  const remainingSlots = 5 - newAvatarForm.value.uploadedPhotos.length
  const filesToProcess = Array.from(files).slice(0, remainingSlots)

  filesToProcess.forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const result = e.target?.result as string
      if (result && newAvatarForm.value.uploadedPhotos.length < 5) {
        newAvatarForm.value.uploadedPhotos.push(result)
      }
    }
    reader.readAsDataURL(file)
  })
}

const removePhoto = (index: number) => {
  newAvatarForm.value.uploadedPhotos.splice(index, 1)
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

const submitCreateAvatar = () => {
  const avatarImages = [
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face',
    'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=face',
    'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face'
  ]

  const newId = String(Date.now())
  const newDigitalAvatar: DigitalAvatar = {
    id: newId,
    name: newAvatarForm.value.name,
    relationship: newAvatarForm.value.relationship,
    gender: newAvatarForm.value.gender,
    avatar: newAvatarForm.value.uploadedPhotos[0] || avatarImages[Math.floor(Math.random() * avatarImages.length)],
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

  simulateGeneration(newId)
}

const simulateGeneration = (avatarId: string) => {
  const avatar = digitalAvatars.value.find(a => a.id === avatarId)
  if (!avatar) return

  const interval = setInterval(() => {
    if (avatar.progress < 100) {
      avatar.progress += Math.random() * 10
      if (avatar.progress > 100) avatar.progress = 100
    } else {
      avatar.status = 'inactive'
      clearInterval(interval)
    }
  }, 1000)
}

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

const noisePatternStyle = computed(() => ({
  backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox=%220 0 100 100%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22 opacity=%220.3%22/%3E%3C/svg%3E")`
}))

const dotPatternStyle = computed(() => ({
  backgroundImage: `url("data:image/svg+xml,%3Csvg width=%2260%22 height=%2260%22 viewBox=%220 0 60 60%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cg fill=%22none%22 fill-rule=%22evenodd%22%3E%3Cg fill=%22%23ffffff%22 fill-opacity=%220.4%22%3E%3Cpath d=%22M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
}))
</script>