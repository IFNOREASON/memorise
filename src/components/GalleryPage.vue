<template>
  <div class="min-h-screen paper-texture">
    <div class="max-w-7xl mx-auto px-6 py-8">
      <section class="mb-8">
        <div class="bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] rounded-[24px] p-8 text-white shadow-warm">
          <div class="flex flex-col md:flex-row items-center justify-between gap-6">
            <div>
              <div class="flex items-center space-x-3 mb-4">
                <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                  <Icon icon="solar:gallery-wide-bold-duotone" class="text-3xl" />
                </div>
                <div>
                  <h2 class="text-2xl font-serif font-bold">家族影集</h2>
                  <p class="text-sm text-white/70">珍藏影像，代代相传</p>
                </div>
              </div>
              <p class="text-white/80 max-w-xl">
                通过 AI 技术，将珍贵的老照片转化为动态影像，制作专属视频，让家族记忆永恒鲜活。
              </p>
            </div>
            <div class="flex items-center space-x-8">
              <div class="text-center">
                <p class="text-3xl font-bold">{{ tasks.length }}</p>
                <p class="text-sm text-white/60">影像任务</p>
              </div>
              <div class="text-center">
                <p class="text-3xl font-bold">{{ totalImages }}</p>
                <p class="text-sm text-white/60">影像素材</p>
              </div>
              <div class="text-center">
                <p class="text-3xl font-bold">{{ completedVideos }}</p>
                <p class="text-sm text-white/60">已完成视频</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="mb-8">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-[#5C4A3A] font-serif">人物影像管理</h3>
          <button 
            class="flex items-center space-x-2 px-5 py-2.5 bg-[#8B6F4E] text-white rounded-xl hover:bg-[#6B5342] transition-colors shadow-soft"
            @click="showCreateModal = true">
            <Icon icon="solar:add-circle-bold" class="text-lg" />
            <span class="font-medium">新建影像任务</span>
          </button>
        </div>

        <div class="relative">
          <button 
            class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 z-10 w-12 h-12 bg-white rounded-full shadow-soft flex items-center justify-center hover:bg-[#E8D5C4] transition-colors"
            @click="prevSlide">
            <Icon icon="solar:arrow-left-bold" class="text-[#8B6F4E] text-xl" />
          </button>

          <div class="overflow-hidden mx-8">
            <div class="flex transition-transform duration-500 ease-in-out" 
                 :style="{ transform: `translateX(-${currentSlide * 100}%)` }">
              <div v-for="(task, index) in tasks" :key="task.id"
                   class="w-full md:w-1/2 lg:w-1/3 flex-shrink-0 px-3">
                <div 
                  class="bg-white rounded-2xl p-5 shadow-soft border border-stone-100 hover-lift cursor-pointer relative"
                  @click="openMediaModal(task)">
                  <button 
                    class="absolute top-3 right-12 w-8 h-8 bg-[#E8D5C4] rounded-lg flex items-center justify-center hover:bg-[#D4A574] transition-colors z-10"
                    @click.stop="showAddMediaModal = true; addingMediaTask = task">
                    <Icon icon="solar:add-linear" class="text-[#8B6F4E] text-lg" />
                  </button>
                  <button 
                    class="absolute top-3 right-3 w-8 h-8 bg-red-50 rounded-lg flex items-center justify-center hover:bg-red-100 transition-colors z-10"
                    :class="{ 'opacity-50 cursor-not-allowed': task.mediaCount > 0 }"
                    @click.stop="handleDeleteTask(task)">
                    <Icon icon="solar:trash-bin-trash-bold" class="text-red-500 text-lg" />
                  </button>

                  <div class="flex items-start justify-between mb-4 pr-16">
                    <div class="flex items-center space-x-3">
                      <div class="w-12 h-12 rounded-xl flex items-center justify-center"
                           :class="getStatusBg(task.status)">
                        <Icon :icon="getTaskIcon(task.type)" 
                              :class="getStatusIcon(task.status)"
                              class="text-xl" />
                      </div>
                      <div>
                        <h4 class="font-bold text-gray-800">{{ task.name }}</h4>
                        <p class="text-xs text-gray-400">{{ task.personName }} · {{ task.mediaCount }} 个影像</p>
                      </div>
                    </div>
                    <span class="px-3 py-1 text-xs font-medium rounded-full"
                          :class="getStatusBadge(task.status)">
                      {{ getStatusText(task.status) }}
                    </span>
                  </div>

                  <div v-if="task.status === 'processing'" class="mb-4">
                    <div class="flex items-center justify-between text-xs text-gray-500 mb-2">
                      <span>处理进度</span>
                      <span>{{ task.progress }}%</span>
                    </div>
                    <div class="w-full bg-gray-100 rounded-full h-2">
                      <div class="h-2 rounded-full transition-all duration-500"
                           :class="task.type === 'video' ? 'bg-[#D4A574]' : 'bg-[#8B6F4E]'"
                           :style="{ width: task.progress + '%' }"></div>
                    </div>
                  </div>

                  <div v-else-if="task.status === 'completed'" class="mb-4">
                    <div class="grid grid-cols-4 gap-2">
                      <div v-for="(media, idx) in task.thumbnails" :key="idx"
                        class="aspect-square rounded-lg overflow-hidden bg-gray-100 relative">
                        <img v-if="media.type === 'image'" :src="media.url" class="w-full h-full object-cover" :alt="`缩略图${idx + 1}`">
                        <div v-else class="w-full h-full bg-gradient-to-br from-[#F5E6D3] to-[#D4A574] flex items-center justify-center">
                          <Icon icon="solar:play-bold" class="text-white text-2xl" />
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="flex items-center justify-between text-xs text-gray-400">
                    <span class="flex items-center">
                      <Icon :icon="getTypeIcon(task.type)" class="mr-1" />
                      {{ getTypeText(task.type) }}
                    </span>
                    <span>{{ task.createTime }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <button 
            class="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 z-10 w-12 h-12 bg-white rounded-full shadow-soft flex items-center justify-center hover:bg-[#E8D5C4] transition-colors"
            @click="nextSlide">
            <Icon icon="solar:arrow-right-bold" class="text-[#8B6F4E] text-xl" />
          </button>

          <div class="flex justify-center mt-6 space-x-2">
            <button 
              v-for="(_, idx) in totalSlides" :key="idx"
              class="w-2 h-2 rounded-full transition-all"
              :class="currentSlide === idx ? 'bg-[#8B6F4E] w-6' : 'bg-[#E8D5C4]'"
              @click="currentSlide = idx">
            </button>
          </div>
        </div>
      </section>

      <section class="mb-8">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-[#5C4A3A] font-serif">快速制作</h3>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white rounded-2xl p-6 shadow-soft border border-stone-100 hover-lift cursor-pointer" @click="goToImageRepair">
            <div class="w-16 h-16 bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] rounded-2xl flex items-center justify-center mb-4">
              <Icon icon="solar:image-line-duotone" class="text-[#8B6F4E] text-3xl" />
            </div>
            <h4 class="font-bold text-gray-800 mb-2">影像修复</h4>
            <p class="text-sm text-gray-500 mb-4">智能修复老照片，去除划痕、褪色，还原清晰色彩</p>
            <div class="flex items-center text-xs text-[#8B6F4E] font-medium">
              <span>开始制作</span>
              <Icon icon="material-symbols:arrow-right-alt" class="ml-1" />
            </div>
          </div>

          <div class="bg-white rounded-2xl p-6 shadow-soft border border-stone-100 hover-lift cursor-pointer">
            <div class="w-16 h-16 bg-gradient-to-br from-[#F5E6D3] to-[#D4A574] rounded-2xl flex items-center justify-center mb-4">
              <Icon icon="solar:video-circle-line-duotone" class="text-[#A67B5B] text-3xl" />
            </div>
            <h4 class="font-bold text-gray-800 mb-2">动态影像</h4>
            <p class="text-sm text-gray-500 mb-4">让静态照片动起来，眨眼、微笑，栩栩如生</p>
            <div class="flex items-center text-xs text-[#A67B5B] font-medium">
              <span>开始制作</span>
              <Icon icon="material-symbols:arrow-right-alt" class="ml-1" />
            </div>
          </div>

          <div class="bg-white rounded-2xl p-6 shadow-soft border border-stone-100 hover-lift cursor-pointer">
            <div class="w-16 h-16 bg-gradient-to-br from-[#E8D5C4] to-emerald-100 rounded-2xl flex items-center justify-center mb-4">
              <Icon icon="solar:clapperboard-line-duotone" class="text-emerald-600 text-3xl" />
            </div>
            <h4 class="font-bold text-gray-800 mb-2">回忆视频</h4>
            <p class="text-sm text-gray-500 mb-4">多张照片合成视频，添加背景音乐和特效</p>
            <div class="flex items-center text-xs text-emerald-600 font-medium">
              <span>开始制作</span>
              <Icon icon="material-symbols:arrow-right-alt" class="ml-1" />
            </div>
          </div>
        </div>
      </section>
    </div>

    <div v-if="showMediaModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/60" @click="showMediaModal = false"></div>
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b border-[#E8D5C4]">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-4">
              <div class="w-12 h-12 rounded-xl bg-[#E8D5C4] flex items-center justify-center">
                <Icon :icon="getTaskIcon(activeMediaTask?.type || 'image')" class="text-[#8B6F4E] text-2xl" />
              </div>
              <div>
                <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">{{ activeMediaTask?.name }}</h3>
                <p class="text-sm text-gray-500">
                  {{ activeMediaTask?.personName }} · 共 {{ filteredMedias.length }} 个影像
                  <span v-if="isSearching" class="text-[#8B6F4E] ml-2">（搜索结果）</span>
                </p>
              </div>
            </div>
            <button 
              class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
              @click="showMediaModal = false">
              <Icon icon="solar:close-circle-bold" class="text-xl" />
            </button>
          </div>

          <div class="flex flex-col md:flex-row gap-4">
            <div class="flex-1 relative">
              <Icon icon="solar:search-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input 
                type="text" 
                v-model="searchKeyword"
                class="w-full pl-10 pr-10 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent"
                placeholder="搜索地点、日期...">
              <button 
                v-if="searchKeyword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                @click="searchKeyword = ''">
                <Icon icon="solar:close-circle-bold" class="text-lg" />
              </button>
            </div>

            <button 
              class="flex items-center space-x-2 px-4 py-3 border border-[#E8D5C4] rounded-xl hover:bg-[#E8D5C4]/30 transition-colors"
              @click="showAdvancedSearch = !showAdvancedSearch">
              <Icon :icon="showAdvancedSearch ? 'solar:minimize-square-2-bold' : 'solar:maximize-square-2-bold'" class="text-[#8B6F4E]" />
              <span class="text-sm text-[#8B6F4E] font-medium">高级搜索</span>
            </button>

            <div class="flex items-center space-x-2 bg-[#F5E6D3] rounded-xl p-1">
              <button 
                class="px-3 py-2 rounded-lg text-sm font-medium transition-all"
                :class="displayMode === 'date' ? 'bg-white text-[#8B6F4E] shadow-sm' : 'text-gray-500 hover:text-[#8B6F4E]'"
                @click="displayMode = 'date'">
                按日期
              </button>
              <button 
                class="px-3 py-2 rounded-lg text-sm font-medium transition-all"
                :class="displayMode === 'year' ? 'bg-white text-[#8B6F4E] shadow-sm' : 'text-gray-500 hover:text-[#8B6F4E]'"
                @click="displayMode = 'year'">
                按年
              </button>
              <button 
                class="px-3 py-2 rounded-lg text-sm font-medium transition-all"
                :class="displayMode === 'month' ? 'bg-white text-[#8B6F4E] shadow-sm' : 'text-gray-500 hover:text-[#8B6F4E]'"
                @click="displayMode = 'month'">
                按月
              </button>
            </div>
          </div>

          <div v-if="showAdvancedSearch" class="mt-4 pt-4 border-t border-[#E8D5C4]">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-2">起始日期</label>
                <input 
                  type="date" 
                  v-model="searchStartDate"
                  class="w-full px-3 py-2 border border-[#E8D5C4] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent text-sm">
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-2">结束日期</label>
                <input 
                  type="date" 
                  v-model="searchEndDate"
                  class="w-full px-3 py-2 border border-[#E8D5C4] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent text-sm">
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-2">地点</label>
                <div class="relative">
                  <Icon icon="solar:point-on-map-linear" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm" />
                  <input 
                    type="text" 
                    v-model="searchLocation"
                    class="w-full pl-9 pr-3 py-2 border border-[#E8D5C4] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent text-sm"
                    placeholder="输入地点...">
                </div>
              </div>
              <div class="flex items-end space-x-2">
                <button 
                  class="flex-1 px-4 py-2 bg-[#8B6F4E] text-white rounded-lg hover:bg-[#6B5342] transition-colors text-sm font-medium"
                  @click="applyAdvancedSearch">
                  搜索
                </button>
                <button 
                  class="flex-1 px-4 py-2 border border-[#E8D5C4] text-gray-600 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
                  @click="clearAdvancedSearch">
                  重置
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-6">
          <template v-if="displayMode === 'date'">
            <div v-for="group in mediaByDate" :key="group.date" class="mb-8">
              <div class="flex items-center space-x-3 mb-4">
                <div class="w-1 h-8 bg-gradient-to-b from-[#8B6F4E] to-[#D4A574] rounded-full"></div>
                <h4 class="font-bold text-[#5C4A3A] font-serif text-lg">{{ group.date }}</h4>
                <span class="text-xs text-gray-400 bg-[#E8D5C4]/50 px-2 py-1 rounded-full">{{ group.medias.length }} 个</span>
              </div>
              
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <div v-for="media in group.medias" :key="media.id"
                     class="rounded-xl overflow-hidden bg-gray-100 relative group cursor-pointer hover:shadow-lg transition-shadow">
                  <div class="aspect-square relative">
                    <img v-if="media.type === 'image'" 
                         :src="media.url" 
                         class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110" 
                         :alt="`影像`">
                    <div v-else class="w-full h-full bg-gradient-to-br from-[#F5E6D3] to-[#D4A574] flex flex-col items-center justify-center">
                      <Icon icon="solar:play-bold" class="text-white text-4xl mb-2" />
                      <span class="text-white text-sm font-medium">{{ media.duration }}</span>
                    </div>
                    <div v-if="media.audio" class="absolute top-2 left-2 bg-[#8B6F4E] text-white px-2 py-1 rounded-lg flex items-center space-x-1 text-xs">
                      <Icon icon="solar:microphone-bold" class="text-sm" />
                      <span>有声音</span>
                    </div>
                    <div class="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
                      <div class="flex items-center space-x-2">
                        <button class="w-10 h-10 bg-white rounded-full flex items-center justify-center hover:bg-[#E8D5C4] transition-colors">
                          <Icon icon="solar:eye-bold" class="text-[#8B6F4E]" />
                        </button>
                        <button v-if="media.audio" 
                                class="w-10 h-10 bg-white rounded-full flex items-center justify-center hover:bg-[#E8D5C4] transition-colors"
                                @click.stop="playMediaAudio(media)">
                          <Icon icon="solar:play-bold" class="text-[#8B6F4E]" />
                        </button>
                        <button class="w-10 h-10 bg-white rounded-full flex items-center justify-center hover:bg-[#E8D5C4] transition-colors">
                          <Icon icon="solar:download-minimalistic-bold" class="text-[#8B6F4E]" />
                        </button>
                        <button class="w-10 h-10 bg-white rounded-full flex items-center justify-center hover:bg-red-100 transition-colors">
                          <Icon icon="solar:trash-bin-trash-bold" class="text-red-500" />
                        </button>
                      </div>
                    </div>
                  </div>
                  <div class="p-3 bg-white">
                    <div class="flex items-center justify-between text-xs text-gray-500 mb-1">
                      <div class="flex items-center space-x-2">
                        <Icon icon="solar:clock-circle-linear" class="text-xs" />
                        <span>{{ media.dateTime }}</span>
                      </div>
                      <div class="flex items-center space-x-1 text-gray-400">
                        <Icon icon="solar:point-on-map-linear" class="text-xs" />
                        <span class="truncate max-w-[100px]">{{ media.location }}</span>
                      </div>
                    </div>
                    
                    <div v-if="media.audio" class="mt-2">
                      <div v-if="expandedMediaAudio !== media.id" class="flex items-center justify-between pt-2 border-t border-[#E8D5C4]">
                        <div class="flex items-center space-x-2 flex-1 min-w-0">
                          <button 
                            class="w-7 h-7 bg-[#8B6F4E] rounded-full flex items-center justify-center flex-shrink-0 hover:bg-[#6B5342] transition-colors"
                            @click.stop="playMediaAudio(media)">
                            <Icon icon="solar:play-bold" class="text-white text-sm ml-0.5" />
                          </button>
                          <div class="min-w-0">
                            <p class="text-xs font-medium text-[#5C4A3A] truncate">{{ media.audio.name }}</p>
                            <p class="text-xs text-gray-400 truncate">
                              {{ formatTime(media.audio.duration) }} · {{ media.audio.createdAt }}
                            </p>
                          </div>
                        </div>
                        <button 
                          class="w-7 h-7 flex items-center justify-center text-gray-400 hover:text-[#8B6F4E] transition-colors"
                          @click.stop="toggleExpandMediaAudio(media)">
                          <Icon icon="solar:expand-up-down-linear" class="text-sm" />
                        </button>
                      </div>
                      
                      <div v-else class="pt-2 border-t border-[#E8D5C4]">
                        <div class="flex items-center justify-between mb-2">
                          <div class="flex items-center space-x-2">
                            <button 
                              class="w-8 h-8 bg-[#8B6F4E] rounded-full flex items-center justify-center hover:bg-[#6B5342] transition-colors"
                              @click.stop="playMediaAudio(media)">
                              <Icon 
                                :icon="playingMediaAudio === media.id ? 'solar:pause-bold' : 'solar:play-bold'" 
                                class="text-white" />
                            </button>
                            <div>
                              <p class="text-xs font-medium text-[#5C4A3A]">{{ media.audio.name }}</p>
                              <p class="text-xs text-gray-400">
                                {{ formatTime(media.audio.duration) }} · {{ media.audio.createdAt }}
                              </p>
                            </div>
                          </div>
                          <button 
                            class="w-7 h-7 flex items-center justify-center text-gray-400 hover:text-red-500 transition-colors"
                            @click.stop="toggleExpandMediaAudio(media)">
                            <Icon icon="solar:close-bold" class="text-sm" />
                          </button>
                        </div>
                        
                        <div class="flex items-center space-x-2">
                          <span class="text-xs text-gray-500 font-mono w-10 text-left">
                            {{ formatTime(currentAudioProgress) }}
                          </span>
                          <input 
                            type="range" 
                            :min="0" 
                            :max="media.audio.duration || 0" 
                            :value="currentAudioProgress"
                            class="flex-1 h-1.5 bg-[#E8D5C4] rounded-full appearance-none cursor-pointer"
                            style="accent-color: #8B6F4E"
                            @input="seekAudio($event, media)"
                            @click.stop>
                          <span class="text-xs text-gray-500 font-mono w-10 text-right">
                            {{ formatTime(media.audio.duration || 0) }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <template v-else-if="displayMode === 'year'">
            <div v-for="group in mediaByYear" :key="group.year" class="mb-8">
              <div class="flex items-center space-x-3 mb-4">
                <div class="w-1 h-8 bg-gradient-to-b from-[#8B6F4E] to-[#D4A574] rounded-full"></div>
                <h4 class="font-bold text-[#5C4A3A] font-serif text-lg">{{ group.year }}年</h4>
                <span class="text-xs text-gray-400 bg-[#E8D5C4]/50 px-2 py-1 rounded-full">{{ group.medias.length }} 个</span>
              </div>
              
              <div class="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-12 gap-2">
                <div v-for="media in group.medias" :key="media.id"
                     class="aspect-square rounded-lg overflow-hidden bg-gray-100 relative group cursor-pointer hover:shadow-md transition-shadow">
                  <img v-if="media.type === 'image'" 
                       :src="media.url" 
                       class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110" 
                       :alt="`影像`">
                  <div v-else class="w-full h-full bg-gradient-to-br from-[#F5E6D3] to-[#D4A574] flex items-center justify-center">
                    <Icon icon="solar:play-bold" class="text-white text-xl" />
                  </div>
                  <div class="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
                    <div class="flex items-center space-x-1">
                      <button class="w-7 h-7 bg-white rounded-full flex items-center justify-center hover:bg-[#E8D5C4] transition-colors">
                        <Icon icon="solar:eye-bold" class="text-[#8B6F4E] text-sm" />
                      </button>
                      <button class="w-7 h-7 bg-white rounded-full flex items-center justify-center hover:bg-red-100 transition-colors">
                        <Icon icon="solar:trash-bin-trash-bold" class="text-red-500 text-sm" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <template v-else-if="displayMode === 'month'">
            <div v-for="group in mediaByMonth" :key="group.month" class="mb-8">
              <div class="flex items-center space-x-3 mb-4">
                <div class="w-1 h-8 bg-gradient-to-b from-[#8B6F4E] to-[#D4A574] rounded-full"></div>
                <h4 class="font-bold text-[#5C4A3A] font-serif text-lg">{{ group.month }}</h4>
                <span class="text-xs text-gray-400 bg-[#E8D5C4]/50 px-2 py-1 rounded-full">{{ group.medias.length }} 个</span>
              </div>
              
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
                <div v-for="media in group.medias" :key="media.id"
                     class="rounded-lg overflow-hidden bg-gray-100 relative group cursor-pointer hover:shadow-md transition-shadow">
                  <div class="aspect-square relative">
                    <img v-if="media.type === 'image'" 
                         :src="media.url" 
                         class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110" 
                         :alt="`影像`">
                    <div v-else class="w-full h-full bg-gradient-to-br from-[#F5E6D3] to-[#D4A574] flex items-center justify-center">
                      <Icon icon="solar:play-bold" class="text-white text-2xl" />
                    </div>
                    <div class="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
                      <div class="flex items-center space-x-1">
                        <button class="w-8 h-8 bg-white rounded-full flex items-center justify-center hover:bg-[#E8D5C4] transition-colors">
                          <Icon icon="solar:eye-bold" class="text-[#8B6F4E] text-sm" />
                        </button>
                        <button class="w-8 h-8 bg-white rounded-full flex items-center justify-center hover:bg-red-100 transition-colors">
                          <Icon icon="solar:trash-bin-trash-bold" class="text-red-500 text-sm" />
                        </button>
                      </div>
                    </div>
                  </div>
                  <div class="p-2 bg-white">
                    <div class="flex flex-col">
                      <div class="flex items-center space-x-1 text-[10px] text-gray-500">
                        <Icon icon="solar:clock-circle-linear" class="text-[10px]" />
                        <span>{{ media.dateTime.slice(0, 10) }}</span>
                      </div>
                      <div class="flex items-center space-x-1 text-[10px] text-gray-400 mt-1">
                        <Icon icon="solar:point-on-map-linear" class="text-[10px]" />
                        <span class="truncate max-w-[80px]">{{ media.location }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <div v-if="filteredMedias.length === 0" class="flex flex-col items-center justify-center py-20">
            <Icon icon="solar:gallery-empty-linear" class="text-6xl text-gray-300 mb-4" />
            <p class="text-gray-500 mb-2">没有找到匹配的影像</p>
            <p class="text-gray-400 text-sm">请尝试修改搜索条件</p>
          </div>
        </div>

        <div class="flex items-center justify-end space-x-3 p-6 border-t border-[#E8D5C4]">
          <button 
            class="flex items-center space-x-2 px-5 py-2.5 border border-[#E8D5C4] text-[#8B6F4E] rounded-xl hover:bg-[#E8D5C4]/30 transition-colors"
            @click="showAddMediaModal = true">
            <Icon icon="solar:add-circle-bold" class="text-lg" />
            <span>添加影像</span>
          </button>
          <button 
            class="flex items-center space-x-2 px-5 py-2.5 bg-[#8B6F4E] text-white rounded-xl hover:bg-[#6B5342] transition-colors"
            @click="showMediaModal = false">
            <span>关闭</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="showAddMediaModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" @click="showAddMediaModal = false"></div>
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b border-[#E8D5C4] flex items-center justify-between">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">添加影像</h3>
          <button 
            class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
            @click="showAddMediaModal = false">
            <Icon icon="solar:close-circle-bold" class="text-xl" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">选择日期时间</label>
            <input 
              type="datetime-local" 
              v-model="newMediaDateTime"
              class="w-full px-4 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent">
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">拍摄地点</label>
            <div class="relative">
              <Icon icon="solar:point-on-map-linear" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input 
                type="text" 
                v-model="newMediaLocation"
                class="w-full pl-10 pr-4 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent"
                placeholder="例如：北京市海淀区老宅子">
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">上传影像</label>
            <div class="border-2 border-dashed border-[#E8D5C4] rounded-xl p-8 text-center hover:border-[#D4A574] transition-colors cursor-pointer"
                 @click="triggerMediaUpload">
              <Icon icon="solar:upload-minimalistic-bold" class="text-4xl text-gray-300 mx-auto mb-3" />
              <p class="text-sm text-gray-500">点击或拖拽上传照片/视频</p>
              <p class="text-xs text-gray-400 mt-1">支持 JPG、PNG、MP4 格式</p>
            </div>
            <input 
              type="file" 
              ref="mediaUploadInput"
              accept="image/*,video/*"
              class="hidden"
              @change="handleMediaUpload"
              multiple>
          </div>

          <div v-if="previewMedias.length > 0">
            <label class="block text-sm font-medium text-gray-700 mb-2">已选择（点击影像下方的按钮可添加录音）</label>
            <div class="space-y-4">
              <div v-for="(media, idx) in previewMedias" :key="idx"
                   class="bg-[#F5E6D3]/20 rounded-xl p-4 border border-[#E8D5C4]">
                <div class="flex gap-4">
                  <div class="w-24 h-24 flex-shrink-0 rounded-lg overflow-hidden bg-gray-100 relative">
                    <img :src="media.url" class="w-full h-full object-cover" :alt="`预览${idx + 1}`">
                    <button 
                      class="absolute top-1 right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center"
                      @click="removePreview(idx)">
                      <Icon icon="solar:close-linear" class="text-white text-xs" />
                    </button>
                  </div>
                  
                  <div class="flex-1 min-w-0">
                    <div v-if="!media.audio" class="h-full flex flex-col justify-center">
                      <p class="text-sm text-gray-500 mb-3">该影像暂无录音，您可以：</p>
                      <div class="flex flex-wrap gap-2">
                        <button 
                          v-if="!isRecording || activeRecordingMediaIndex !== idx"
                          class="flex items-center space-x-1 px-3 py-2 bg-[#8B6F4E] text-white rounded-lg hover:bg-[#6B5342] transition-colors text-sm"
                          @click="startRecording(idx)">
                          <Icon icon="solar:record-bold" class="text-sm" />
                          <span>录制声音</span>
                        </button>
                        <button 
                          v-if="activeRecordingMediaIndex === idx && isRecording && !isPaused"
                          class="flex items-center space-x-1 px-3 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors text-sm"
                          @click="pauseRecording">
                          <Icon icon="solar:pause-bold" class="text-sm" />
                          <span>暂停</span>
                        </button>
                        <button 
                          v-if="activeRecordingMediaIndex === idx && isPaused"
                          class="flex items-center space-x-1 px-3 py-2 bg-[#8B6F4E] text-white rounded-lg hover:bg-[#6B5342] transition-colors text-sm"
                          @click="resumeRecording">
                          <Icon icon="solar:play-bold" class="text-sm" />
                          <span>继续</span>
                        </button>
                        <button 
                          v-if="activeRecordingMediaIndex === idx && (isRecording || isPaused)"
                          class="flex items-center space-x-1 px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm"
                          @click="stopRecording">
                          <Icon icon="solar:stop-bold" class="text-sm" />
                          <span>停止</span>
                        </button>
                        <button 
                          v-if="!isRecording || activeRecordingMediaIndex !== idx"
                          class="flex items-center space-x-1 px-3 py-2 border border-[#E8D5C4] text-[#8B6F4E] rounded-lg hover:bg-[#E8D5C4]/30 transition-colors text-sm"
                          @click="triggerAudioUpload(idx)">
                          <Icon icon="solar:upload-minimalistic-linear" class="text-sm" />
                          <span>上传录音</span>
                        </button>
                      </div>
                      <div v-if="activeRecordingMediaIndex === idx && (isRecording || isPaused)" class="flex items-center space-x-2 mt-3">
                        <div 
                          v-if="isRecording"
                          class="w-2 h-2 bg-red-500 rounded-full animate-pulse">
                        </div>
                        <div 
                          v-if="isPaused"
                          class="w-2 h-2 bg-amber-500 rounded-full">
                        </div>
                        <span class="font-mono text-sm text-[#5C4A3A]">{{ formatTime(recordingDuration) }}</span>
                        <span class="text-xs text-gray-500">
                          {{ isPaused ? '已暂停' : '录音中...' }}
                        </span>
                      </div>
                    </div>
                    
                    <div v-else class="h-full">
                      <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-3">
                          <button 
                            class="w-8 h-8 bg-[#8B6F4E] rounded-full flex items-center justify-center hover:bg-[#6B5342] transition-colors"
                            @click="playPreviewAudio(idx)">
                            <Icon 
                              :icon="playingIndex?.mediaIndex === idx && playingIndex?.isPreview ? 'solar:pause-bold' : 'solar:play-bold'" 
                              class="text-white text-sm" />
                          </button>
                          <div>
                            <p class="text-sm font-medium text-gray-800">{{ media.audio.name }}</p>
                            <p class="text-xs text-gray-500">
                              时长: {{ formatTime(media.audio.duration) }} · {{ media.audio.createdAt }}
                            </p>
                          </div>
                        </div>
                        <div class="flex items-center space-x-2">
                          <button 
                            class="p-2 text-[#8B6F4E] hover:bg-[#E8D5C4]/30 rounded-lg transition-colors"
                            @click="startRecording(idx)"
                            :disabled="isRecording && activeRecordingMediaIndex !== idx">
                            <Icon icon="solar:refresh-bold" class="text-sm" />
                          </button>
                          <button 
                            class="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                            @click="removePreviewAudio(idx)">
                            <Icon icon="solar:trash-bin-trash-bold" class="text-sm" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <input 
            type="file" 
            ref="audioUploadInput"
            accept="audio/*"
            class="hidden"
            @change="handleAudioUpload">
        </div>

        <div class="p-6 border-t border-gray-100 flex items-center justify-end space-x-3">
          <button 
            class="px-5 py-2.5 text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
            @click="showAddMediaModal = false">
            取消
          </button>
          <button 
            class="px-5 py-2.5 bg-[#8B6F4E] text-white rounded-xl hover:bg-[#6B5342] transition-colors"
            @click="addMedia">
            添加
          </button>
        </div>
      </div>
    </div>

    <div v-if="showDeleteConfirmModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" @click="showDeleteConfirmModal = false"></div>
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
        <div class="text-center">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-red-50 flex items-center justify-center">
            <Icon icon="solar:trash-bin-trash-bold" class="text-red-500 text-3xl" />
          </div>
          <h3 class="text-lg font-bold text-gray-800 mb-2">确认删除</h3>
          <p v-if="deleteTask?.mediaCount && deleteTask.mediaCount > 0" class="text-sm text-gray-500 mb-4">
            该影像集下仍有 <span class="font-bold text-[#8B6F4E]">{{ deleteTask?.mediaCount }}</span> 个影像数据，<br>请先删除所有影像后再删除影集。
          </p>
          <p v-else class="text-sm text-gray-500 mb-4">
            确定要删除影集「<span class="font-medium">{{ deleteTask?.name }}</span>」吗？<br>此操作不可撤销。
          </p>
        </div>
        <div class="flex items-center justify-center space-x-3 mt-6">
          <button 
            class="px-5 py-2.5 text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
            @click="showDeleteConfirmModal = false">
            取消
          </button>
          <button 
            v-if="!deleteTask?.mediaCount || deleteTask.mediaCount === 0"
            class="px-5 py-2.5 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors"
            @click="confirmDeleteTask">
            确认删除
          </button>
          <button 
            v-else
            class="px-5 py-2.5 bg-gray-300 text-gray-500 rounded-xl cursor-not-allowed"
            disabled>
            无法删除
          </button>
        </div>
      </div>
    </div>

    <div v-if="showCreateModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" @click="closeCreateModal"></div>
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b border-[#E8D5C4] flex items-center justify-between">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">新建影像任务</h3>
          <button 
            class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
            @click="closeCreateModal">
            <Icon icon="solar:close-circle-bold" class="text-xl" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">任务名称</label>
            <input 
              type="text" 
              v-model="newTask.name"
              class="w-full px-4 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent"
              placeholder="例如：爷爷的青春岁月">
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">人物名称</label>
            <input 
              type="text" 
              v-model="newTask.personName"
              class="w-full px-4 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent"
              placeholder="例如：张明远">
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">制作类型</label>
            <div class="grid grid-cols-2 gap-3">
              <button 
                class="p-4 border-2 rounded-xl transition-all"
                :class="newTask.type === 'image' ? 'border-[#8B6F4E] bg-[#E8D5C4]/30' : 'border-[#E8D5C4] hover:border-[#D4A574]'"
                @click="newTask.type = 'image'">
                <Icon icon="solar:image-line-duotone" class="text-2xl mx-auto mb-2" :class="newTask.type === 'image' ? 'text-[#8B6F4E]' : 'text-gray-400'" />
                <p class="font-medium" :class="newTask.type === 'image' ? 'text-[#8B6F4E]' : 'text-gray-600'">影像制作</p>
                <p class="text-xs text-gray-400">修复 + 动态效果</p>
              </button>
              <button 
                class="p-4 border-2 rounded-xl transition-all"
                :class="newTask.type === 'video' ? 'border-[#D4A574] bg-[#F5E6D3]/50' : 'border-[#E8D5C4] hover:border-[#D4A574]'"
                @click="newTask.type = 'video'">
                <Icon icon="solar:clapperboard-line-duotone" class="text-2xl mx-auto mb-2" :class="newTask.type === 'video' ? 'text-[#D4A574]' : 'text-gray-400'" />
                <p class="font-medium" :class="newTask.type === 'video' ? 'text-[#D4A574]' : 'text-gray-600'">视频制作</p>
                <p class="text-xs text-gray-400">生成回忆视频</p>
              </button>
            </div>
          </div>
        </div>

        <div class="p-6 border-t border-gray-100 flex items-center justify-end space-x-3">
          <button 
            class="px-5 py-2.5 text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
            @click="closeCreateModal">
            取消
          </button>
          <button 
            class="px-5 py-2.5 bg-[#8B6F4E] text-white rounded-xl hover:bg-[#6B5342] transition-colors"
            @click="createTask">
            创建任务
          </button>
        </div>
      </div>
    </div>

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
          <p class="text-xs text-white/40">© 2024 memorise · 家族精神纪念馆</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'

const router = useRouter()
const currentSlide = ref(0)
const showMediaModal = ref(false)
const showAddMediaModal = ref(false)
const showCreateModal = ref(false)
const showDeleteConfirmModal = ref(false)
const showAdvancedSearch = ref(false)
const activeMediaTask = ref<Task | null>(null)
const addingMediaTask = ref<Task | null>(null)
const deleteTask = ref<Task | null>(null)
const newMediaDateTime = ref(new Date().toISOString().slice(0, 16))
const newMediaLocation = ref('')

interface PreviewMedia {
  url: string
  type: 'image' | 'video'
  audio?: RecordedAudio
}

const previewMedias = ref<PreviewMedia[]>([])
const activeRecordingMediaIndex = ref<number | null>(null)

const searchKeyword = ref('')
const searchStartDate = ref('')
const searchEndDate = ref('')
const searchLocation = ref('')
const displayMode = ref<'date' | 'year' | 'month'>('date')

const isRecording = ref(false)
const isPaused = ref(false)
const recordingDuration = ref(0)
const playingIndex = ref<{ mediaIndex: number; isPreview: boolean } | null>(null)
const playingMediaAudio = ref<string | null>(null)
const expandedMediaAudio = ref<string | null>(null)
const currentAudioProgress = ref(0)
const audioUploadInput = ref<HTMLInputElement | null>(null)
const mediaUploadInput = ref<HTMLInputElement | null>(null)

let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []
let recordingTimer: number | null = null
let audioPlayer: HTMLAudioElement | null = null
let audioProgressTimer: number | null = null

interface Media {
  id: string
  url: string
  type: 'image' | 'video'
  date: string
  dateTime: string
  location: string
  duration?: string
  year: number
  month: string
  audio?: RecordedAudio
}

interface Task {
  id: string
  name: string
  personName: string
  type: 'image' | 'video'
  status: 'processing' | 'completed' | 'draft'
  progress: number
  mediaCount: number
  createTime: string
  thumbnails: { url: string; type: 'image' | 'video' }[]
  medias: Media[]
}

interface RecordedAudio {
  name: string
  url: string
  duration: number
  blob?: Blob
  isUploaded: boolean
  createdAt: string
}

const newTask = ref({
  name: '',
  personName: '',
  type: 'image' as 'image' | 'video'
})

const tasks = ref<Task[]>([
  {
    id: '1',
    name: '爷爷的青春岁月',
    personName: '张明远',
    type: 'image',
    status: 'completed',
    progress: 100,
    mediaCount: 12,
    createTime: '2024-01-15',
    thumbnails: [
      { url: 'https://images.unsplash.com/photo-1552374196-c4e7ffc6e126?w=200&h=200&fit=crop', type: 'image' },
      { url: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=200&h=200&fit=crop', type: 'image' },
      { url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop', type: 'image' },
      { url: 'https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=200&h=200&fit=crop', type: 'image' }
    ],
    medias: [
      { id: '1-1', url: 'https://images.unsplash.com/photo-1552374196-c4e7ffc6e126?w=400&h=400&fit=crop', type: 'image', date: '1985年3月', dateTime: '1985-03-15 14:30:00', location: '北京市海淀区老宅子', year: 1985, month: '1985年3月' },
      { id: '1-2', url: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&h=400&fit=crop', type: 'image', date: '1985年3月', dateTime: '1985-03-15 15:45:00', location: '北京市海淀区老宅子', year: 1985, month: '1985年3月' },
      { id: '1-3', url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop', type: 'image', date: '1985年3月', dateTime: '1985-03-16 10:20:00', location: '北京市海淀区老宅子', year: 1985, month: '1985年3月' },
      { id: '1-4', url: 'https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=400&h=400&fit=crop', type: 'image', date: '1990年7月', dateTime: '1990-07-20 09:15:00', location: '上海市黄浦区外滩', year: 1990, month: '1990年7月' },
      { id: '1-5', url: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=400&fit=crop', type: 'image', date: '1990年7月', dateTime: '1990-07-20 11:30:00', location: '上海市黄浦区外滩', year: 1990, month: '1990年7月' },
      { id: '1-6', url: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop', type: 'image', date: '1995年10月', dateTime: '1995-10-01 16:45:00', location: '杭州市西湖区西湖', year: 1995, month: '1995年10月' },
      { id: '1-7', url: 'https://images.unsplash.com/photo-1552374196-c4e7ffc6e126?w=400&h=400&fit=crop', type: 'image', date: '1995年10月', dateTime: '1995-10-01 17:20:00', location: '杭州市西湖区西湖', year: 1995, month: '1995年10月' },
      { id: '1-8', url: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&h=400&fit=crop', type: 'image', date: '2000年2月', dateTime: '2000-02-05 13:00:00', location: '北京市朝阳区新宅子', year: 2000, month: '2000年2月' },
      { id: '1-9', url: '', type: 'video', date: '2000年2月', dateTime: '2000-02-05 14:30:00', location: '北京市朝阳区新宅子', year: 2000, month: '2000年2月', duration: '3:25' },
      { id: '1-10', url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop', type: 'image', date: '2005年5月', dateTime: '2005-05-10 09:30:00', location: '西安市雁塔区大雁塔', year: 2005, month: '2005年5月' },
      { id: '1-11', url: 'https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=400&h=400&fit=crop', type: 'image', date: '2005年5月', dateTime: '2005-05-10 10:45:00', location: '西安市雁塔区大雁塔', year: 2005, month: '2005年5月' },
      { id: '1-12', url: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=400&fit=crop', type: 'image', date: '2010年8月', dateTime: '2010-08-15 15:20:00', location: '青岛市市南区栈桥', year: 2010, month: '2010年8月' }
    ]
  },
  {
    id: '2',
    name: '奶奶的美好时光',
    personName: '李淑华',
    type: 'video',
    status: 'processing',
    progress: 68,
    mediaCount: 8,
    createTime: '2024-01-20',
    thumbnails: [],
    medias: [
      { id: '2-1', url: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop', type: 'image', date: '1970年1月', dateTime: '1970-01-15 10:30:00', location: '苏州市姑苏区老巷', year: 1970, month: '1970年1月' },
      { id: '2-2', url: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop', type: 'image', date: '1975年4月', dateTime: '1975-04-20 14:15:00', location: '南京市玄武区紫金山', year: 1975, month: '1975年4月' },
      { id: '2-3', url: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop', type: 'image', date: '1980年9月', dateTime: '1980-09-10 16:45:00', location: '扬州市广陵区瘦西湖', year: 1980, month: '1980年9月' }
    ]
  },
  {
    id: '3',
    name: '家族团圆纪念',
    personName: '家族全员',
    type: 'video',
    status: 'completed',
    progress: 100,
    mediaCount: 24,
    createTime: '2024-01-10',
    thumbnails: [
      { url: 'https://images.unsplash.com/photo-1511895426328-dc8714191300?w=200&h=200&fit=crop', type: 'image' },
      { url: 'https://images.unsplash.com/photo-1515934751635-c81c6bc9a2d8?w=200&h=200&fit=crop', type: 'image' },
      { url: '', type: 'video' },
      { url: 'https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=200&h=200&fit=crop', type: 'image' }
    ],
    medias: [
      { id: '3-1', url: 'https://images.unsplash.com/photo-1511895426328-dc8714191300?w=400&h=400&fit=crop', type: 'image', date: '2023年春节', dateTime: '2023-01-22 12:30:00', location: '北京市朝阳区新宅子', year: 2023, month: '2023年1月' },
      { id: '3-2', url: 'https://images.unsplash.com/photo-1515934751635-c81c6bc9a2d8?w=400&h=400&fit=crop', type: 'image', date: '2023年春节', dateTime: '2023-01-22 13:15:00', location: '北京市朝阳区新宅子', year: 2023, month: '2023年1月' },
      { id: '3-3', url: '', type: 'video', date: '2023年春节', dateTime: '2023-01-22 14:00:00', location: '北京市朝阳区新宅子', year: 2023, month: '2023年1月', duration: '5:30' },
      { id: '3-4', url: 'https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=400&h=400&fit=crop', type: 'image', date: '2022年中秋', dateTime: '2022-09-10 19:30:00', location: '北京市海淀区老宅子', year: 2022, month: '2022年9月' },
      { id: '3-5', url: 'https://images.unsplash.com/photo-1491013516836-7db643ee125a?w=400&h=400&fit=crop', type: 'image', date: '2022年中秋', dateTime: '2022-09-10 20:15:00', location: '北京市海淀区老宅子', year: 2022, month: '2022年9月' },
      { id: '3-6', url: 'https://images.unsplash.com/photo-1511895426328-dc8714191300?w=400&h=400&fit=crop', type: 'image', date: '2021年国庆', dateTime: '2021-10-01 10:30:00', location: '天津市和平区五大道', year: 2021, month: '2021年10月' }
    ]
  }
])

const totalSlides = computed(() => {
  if (tasks.value.length <= 1) return 1
  return Math.max(1, tasks.value.length - 2)
})

const totalImages = computed(() => {
  return tasks.value.reduce((sum, task) => sum + task.mediaCount, 0)
})

const completedVideos = computed(() => {
  return tasks.value.filter(t => t.status === 'completed').length
})

const isSearching = computed(() => {
  return searchKeyword.value !== '' || searchStartDate.value !== '' || searchEndDate.value !== '' || searchLocation.value !== ''
})

const filteredMedias = computed(() => {
  if (!activeMediaTask.value) return []
  
  let medias = [...activeMediaTask.value.medias]
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    medias = medias.filter(m => 
      m.location.toLowerCase().includes(keyword) || 
      m.dateTime.toLowerCase().includes(keyword) ||
      m.date.toLowerCase().includes(keyword)
    )
  }
  
  if (searchStartDate.value) {
    medias = medias.filter(m => m.dateTime >= searchStartDate.value)
  }
  
  if (searchEndDate.value) {
    medias = medias.filter(m => m.dateTime <= searchEndDate.value + ' 23:59:59')
  }
  
  if (searchLocation.value) {
    const locKeyword = searchLocation.value.toLowerCase()
    medias = medias.filter(m => m.location.toLowerCase().includes(locKeyword))
  }
  
  return medias
})

const mediaByDate = computed(() => {
  const groups: { date: string; medias: Media[] }[] = []
  filteredMedias.value.forEach(media => {
    const existing = groups.find(g => g.date === media.date)
    if (existing) {
      existing.medias.push(media)
    } else {
      groups.push({ date: media.date, medias: [media] })
    }
  })
  return groups
})

const mediaByYear = computed(() => {
  const groups: { year: number; medias: Media[] }[] = []
  filteredMedias.value.forEach(media => {
    const existing = groups.find(g => g.year === media.year)
    if (existing) {
      existing.medias.push(media)
    } else {
      groups.push({ year: media.year, medias: [media] })
    }
  })
  return groups.sort((a, b) => a.year - b.year)
})

const mediaByMonth = computed(() => {
  const groups: { month: string; medias: Media[] }[] = []
  filteredMedias.value.forEach(media => {
    const existing = groups.find(g => g.month === media.month)
    if (existing) {
      existing.medias.push(media)
    } else {
      groups.push({ month: media.month, medias: [media] })
    }
  })
  return groups
})

const goToImageRepair = () => {
  router.push('/gallery/repair')
}

const prevSlide = () => {
  if (currentSlide.value > 0) {
    currentSlide.value--
  } else {
    currentSlide.value = totalSlides.value - 1
  }
}

const nextSlide = () => {
  if (currentSlide.value < totalSlides.value - 1) {
    currentSlide.value++
  } else {
    currentSlide.value = 0
  }
}

const openMediaModal = (task: Task) => {
  activeMediaTask.value = task
  addingMediaTask.value = task
  showMediaModal.value = true
}

const handleDeleteTask = (task: Task) => {
  deleteTask.value = task
  showDeleteConfirmModal.value = true
}

const confirmDeleteTask = () => {
  if (!deleteTask.value) return
  const index = tasks.value.findIndex(t => t.id === deleteTask.value?.id)
  if (index > -1) {
    tasks.value.splice(index, 1)
  }
  showDeleteConfirmModal.value = false
  deleteTask.value = null
}

const triggerMediaUpload = () => {
  if (mediaUploadInput.value) {
    mediaUploadInput.value.click()
  }
}

const handleMediaUpload = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return
  
  Array.from(input.files).forEach((file) => {
    const isImage = file.type.startsWith('image/')
    const isVideo = file.type.startsWith('video/')
    
    if (!isImage && !isVideo) {
      alert(`文件 ${file.name} 不是支持的影像格式`)
      return
    }
    
    const url = URL.createObjectURL(file)
    const type = isImage ? 'image' : 'video'
    
    const newMedia: PreviewMedia = {
      url,
      type,
      audio: undefined
    }
    
    previewMedias.value.push(newMedia)
  })
  
  if (input) {
    input.value = ''
  }
}

const removePreview = (idx: number) => {
  const media = previewMedias.value[idx]
  if (media.url) {
    URL.revokeObjectURL(media.url)
  }
  if (media.audio?.blob) {
    URL.revokeObjectURL(media.audio.url)
  }
  previewMedias.value.splice(idx, 1)
  
  if (playingIndex.value?.mediaIndex === idx && playingIndex.value?.isPreview) {
    if (audioPlayer) {
      audioPlayer.pause()
      audioPlayer.currentTime = 0
    }
    playingIndex.value = null
  } else if (playingIndex.value !== null && playingIndex.value?.mediaIndex > idx) {
    playingIndex.value.mediaIndex--
  }
}

const addMedia = () => {
  previewMedias.value.forEach(media => {
    if (media.url) {
      URL.revokeObjectURL(media.url)
    }
    if (media.audio?.blob) {
      URL.revokeObjectURL(media.audio.url)
    }
  })
  showAddMediaModal.value = false
  previewMedias.value = []
}

const applyAdvancedSearch = () => {
}

const clearAdvancedSearch = () => {
  searchKeyword.value = ''
  searchStartDate.value = ''
  searchEndDate.value = ''
  searchLocation.value = ''
}

const getTaskIcon = (type: string) => {
  return type === 'video' ? 'solar:clapperboard-play-bold' : 'solar:image-bold'
}

const getTypeIcon = (type: string) => {
  return type === 'video' ? 'solar:video-linear' : 'solar:camera-linear'
}

const getTypeText = (type: string) => {
  return type === 'video' ? '视频制作' : '影像制作'
}

const getStatusBg = (status: string) => {
  switch (status) {
    case 'completed': return 'bg-emerald-50'
    case 'processing': return 'bg-[#F5E6D3]'
    default: return 'bg-gray-100'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed': return 'text-emerald-600'
    case 'processing': return 'text-[#D4A574]'
    default: return 'text-gray-400'
  }
}

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'completed': return 'bg-emerald-50 text-emerald-600'
    case 'processing': return 'bg-[#F5E6D3] text-[#D4A574]'
    default: return 'bg-gray-100 text-gray-500'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'completed': return '已完成'
    case 'processing': return '处理中'
    default: return '草稿'
  }
}

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const formatDateTime = (date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}年${month}月${day}日 ${hours}:${minutes}:${seconds}`
}

const startRecording = async (mediaIndex: number) => {
  if (activeRecordingMediaIndex.value !== null && activeRecordingMediaIndex.value !== mediaIndex) {
    alert('已有录音正在进行中，请先停止当前录音')
    return
  }
  
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const mimeTypes = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg;codecs=opus',
      'audio/mp4',
    ]
    let mimeType = ''
    for (const type of mimeTypes) {
      if (MediaRecorder.isTypeSupported(type)) {
        mimeType = type
        break
      }
    }
    if (!mimeType) {
      alert('您的浏览器不支持录音功能')
      return
    }
    mediaRecorder = new MediaRecorder(stream, { mimeType })
    audioChunks = []
    recordingDuration.value = 0
    activeRecordingMediaIndex.value = mediaIndex
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }
    
    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: mimeType })
      const audioUrl = URL.createObjectURL(audioBlob)
      const now = new Date()
      
      const newAudio: RecordedAudio = {
        name: `录音 ${mediaIndex + 1}`,
        url: audioUrl,
        duration: recordingDuration.value,
        blob: audioBlob,
        isUploaded: false,
        createdAt: formatDateTime(now)
      }
      
      if (activeRecordingMediaIndex.value !== null && previewMedias.value[activeRecordingMediaIndex.value]) {
        if (previewMedias.value[activeRecordingMediaIndex.value].audio?.blob) {
          URL.revokeObjectURL(previewMedias.value[activeRecordingMediaIndex.value].audio!.url)
        }
        previewMedias.value[activeRecordingMediaIndex.value].audio = newAudio
      }
      
      activeRecordingMediaIndex.value = null
      stream.getTracks().forEach(track => track.stop())
    }
    
    mediaRecorder.start()
    isRecording.value = true
    isPaused.value = false
    
    recordingTimer = window.setInterval(() => {
      recordingDuration.value++
    }, 1000)
    
  } catch (error) {
    console.error('录音失败:', error)
    alert('无法访问麦克风，请检查权限设置')
  }
}

const pauseRecording = () => {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.pause()
    isPaused.value = true
    if (recordingTimer) {
      clearInterval(recordingTimer)
      recordingTimer = null
    }
  }
}

const resumeRecording = () => {
  if (mediaRecorder && mediaRecorder.state === 'paused') {
    mediaRecorder.resume()
    isPaused.value = false
    recordingTimer = window.setInterval(() => {
      recordingDuration.value++
    }, 1000)
  }
}

const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
    isRecording.value = false
    isPaused.value = false
    if (recordingTimer) {
      clearInterval(recordingTimer)
      recordingTimer = null
    }
  }
}

const playPreviewAudio = (mediaIndex: number) => {
  const audio = previewMedias.value[mediaIndex]?.audio
  if (!audio) return
  
  if (playingIndex.value?.mediaIndex === mediaIndex && playingIndex.value?.isPreview) {
    if (audioPlayer) {
      audioPlayer.pause()
      audioPlayer.currentTime = 0
    }
    playingIndex.value = null
    return
  }
  
  if (audioPlayer) {
    audioPlayer.pause()
    audioPlayer.currentTime = 0
  }
  
  audioPlayer = new Audio(audio.url)
  audioPlayer.onended = () => {
    playingIndex.value = null
  }
  playingIndex.value = { mediaIndex, isPreview: true }
  audioPlayer.play()
}

const removePreviewAudio = (mediaIndex: number) => {
  const audio = previewMedias.value[mediaIndex]?.audio
  if (audio?.blob) {
    URL.revokeObjectURL(audio.url)
  }
  if (previewMedias.value[mediaIndex]) {
    previewMedias.value[mediaIndex].audio = undefined
  }
  
  if (playingIndex.value?.mediaIndex === mediaIndex && playingIndex.value?.isPreview) {
    if (audioPlayer) {
      audioPlayer.pause()
      audioPlayer.currentTime = 0
    }
    playingIndex.value = null
  }
}

const playMediaAudio = (media: Media) => {
  if (!media.audio) return
  
  if (expandedMediaAudio.value === media.id) {
    if (playingMediaAudio.value === media.id) {
      if (audioPlayer) {
        audioPlayer.pause()
      }
      playingMediaAudio.value = null
      stopAudioProgressTimer()
    } else {
      if (audioPlayer) {
        audioPlayer.play()
      }
      playingMediaAudio.value = media.id
      startAudioProgressTimer()
    }
    return
  }
  
  if (audioPlayer) {
    audioPlayer.pause()
    audioPlayer.currentTime = 0
  }
  stopAudioProgressTimer()
  
  expandedMediaAudio.value = media.id
  currentAudioProgress.value = 0
  
  audioPlayer = new Audio(media.audio.url)
  audioPlayer.onended = () => {
    playingMediaAudio.value = null
    currentAudioProgress.value = 0
    stopAudioProgressTimer()
  }
  playingMediaAudio.value = media.id
  audioPlayer.play()
  startAudioProgressTimer()
}

const toggleExpandMediaAudio = (media: Media) => {
  if (expandedMediaAudio.value === media.id) {
    expandedMediaAudio.value = null
    if (playingMediaAudio.value === media.id) {
      if (audioPlayer) {
        audioPlayer.pause()
        audioPlayer.currentTime = 0
      }
      playingMediaAudio.value = null
    }
    stopAudioProgressTimer()
    currentAudioProgress.value = 0
  } else {
    if (expandedMediaAudio.value !== null) {
      if (playingMediaAudio.value === expandedMediaAudio.value) {
        if (audioPlayer) {
          audioPlayer.pause()
          audioPlayer.currentTime = 0
        }
        playingMediaAudio.value = null
      }
      stopAudioProgressTimer()
      currentAudioProgress.value = 0
    }
    expandedMediaAudio.value = media.id
    currentAudioProgress.value = 0
  }
}

const startAudioProgressTimer = () => {
  stopAudioProgressTimer()
  audioProgressTimer = window.setInterval(() => {
    if (audioPlayer && !isNaN(audioPlayer.duration)) {
      currentAudioProgress.value = audioPlayer.currentTime
    }
  }, 100)
}

const stopAudioProgressTimer = () => {
  if (audioProgressTimer) {
    clearInterval(audioProgressTimer)
    audioProgressTimer = null
  }
}

const seekAudio = (event: Event, media: Media) => {
  const input = event.target as HTMLInputElement
  const time = parseFloat(input.value)
  if (audioPlayer && media.audio) {
    audioPlayer.currentTime = time
    currentAudioProgress.value = time
  }
}

const triggerAudioUpload = (mediaIndex: number) => {
  activeRecordingMediaIndex.value = mediaIndex
  if (audioUploadInput.value) {
    audioUploadInput.value.click()
  }
}

const handleAudioUpload = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return
  
  const file = input.files[0]
  
  if (!file.type.startsWith('audio/')) {
    alert(`文件 ${file.name} 不是音频文件`)
    if (input) input.value = ''
    return
  }
  
  const audioUrl = URL.createObjectURL(file)
  
  const tempAudio = new Audio()
  tempAudio.addEventListener('loadedmetadata', () => {
    const now = new Date()
    const newAudio: RecordedAudio = {
      name: file.name.replace(/\.[^/.]+$/, ''),
      url: audioUrl,
      duration: tempAudio.duration,
      blob: file,
      isUploaded: true,
      createdAt: formatDateTime(now)
    }
    
    if (activeRecordingMediaIndex.value !== null && previewMedias.value[activeRecordingMediaIndex.value]) {
      if (previewMedias.value[activeRecordingMediaIndex.value].audio?.blob) {
        URL.revokeObjectURL(previewMedias.value[activeRecordingMediaIndex.value].audio!.url)
      }
      previewMedias.value[activeRecordingMediaIndex.value].audio = newAudio
    }
    
    activeRecordingMediaIndex.value = null
  })
  tempAudio.src = audioUrl
  
  if (input) {
    input.value = ''
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  cleanupRecording()
}

const createTask = () => {
  if (!newTask.value.name || !newTask.value.personName) {
    return
  }
  
  const task: Task = {
    id: Date.now().toString(),
    name: newTask.value.name,
    personName: newTask.value.personName,
    type: newTask.value.type,
    status: 'draft',
    progress: 0,
    mediaCount: 0,
    createTime: new Date().toISOString().split('T')[0],
    thumbnails: [],
    medias: []
  }
  
  tasks.value.unshift(task)
  newTask.value = {
    name: '',
    personName: '',
    type: 'image'
  }
  
  closeCreateModal()
}

const cleanupRecording = () => {
  if (isRecording.value || isPaused.value) {
    stopRecording()
  }
  
  previewMedias.value.forEach(media => {
    if (media.audio?.blob) {
      URL.revokeObjectURL(media.audio.url)
    }
  })
  
  activeRecordingMediaIndex.value = null
  
  if (audioPlayer) {
    audioPlayer.pause()
    audioPlayer.currentTime = 0
    audioPlayer = null
  }
  playingIndex.value = null
}

let autoPlayInterval: number | null = null

onMounted(() => {
  autoPlayInterval = window.setInterval(() => {
    nextSlide()
  }, 5000)
})

onUnmounted(() => {
  if (autoPlayInterval) {
    clearInterval(autoPlayInterval)
  }
  cleanupRecording()
})
</script>
