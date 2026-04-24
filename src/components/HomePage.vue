<template>
  <div class="flex justify-center items-center min-h-screen bg-gray-200 p-4">
    <div class="w-[393px] h-[852px] paper-texture overflow-hidden relative shadow-2xl rounded-[50px] border-[12px] border-gray-900">
      
      <div class="h-12 flex justify-between items-center px-8 pt-3 pb-1">
        <span class="text-sm font-semibold text-gray-800">09:41</span>
        <div class="flex items-center space-x-1.5">
          <Icon icon="material-symbols:signal-cellular-4-bar" class="text-gray-800" style="font-size: 16px;" />
          <Icon icon="material-symbols:wifi" class="text-gray-800" style="font-size: 16px;" />
          <Icon icon="material-symbols:battery-full" class="text-gray-800" style="font-size: 16px;" />
        </div>
      </div>

      <div class="h-[calc(100%-90px)] overflow-y-auto no-scrollbar pb-20">
        
        <header class="px-6 py-4 flex items-center justify-between sticky top-0 z-50 glass-warm">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-[#C84A3E] rounded-sm flex items-center justify-center shadow-md relative overflow-hidden">
              <div class="absolute inset-0 opacity-30" :style="noisePatternStyle"></div>
              <span class="text-white font-serif text-lg font-bold tracking-widest relative z-10">存</span>
            </div>
            <div>
              <h1 class="text-xl font-bold text-[#5C4A3A] font-serif tracking-wider">memorise</h1>
              <p class="text-[9px] text-gray-500 tracking-[0.15em] uppercase font-medium">Family Memorial</p>
            </div>
          </div>
          <button class="w-9 h-9 rounded-full bg-white/80 flex items-center justify-center shadow-sm hover:shadow-md transition-shadow">
            <Icon icon="material-symbols:menu" class="text-gray-600 text-lg" />
          </button>
        </header>

        <section class="px-6 mt-2 relative">
          <div class="absolute top-10 right-0 w-32 h-32 bg-[#E8D5C4] rounded-full blur-3xl opacity-40"></div>
          <div class="absolute bottom-0 left-0 w-24 h-24 bg-[#D4A574] rounded-full blur-2xl opacity-20"></div>
          
          <div class="relative bg-gradient-to-br from-[#8B6F4E] to-[#6B5342] rounded-[32px] p-6 text-white shadow-warm overflow-hidden">
            <div class="absolute inset-0 opacity-10" :style="dotPatternStyle"></div>
            
            <div class="relative z-10">
              <div class="flex items-center space-x-2 mb-4">
                <span class="px-3 py-1 bg-white/20 backdrop-blur rounded-full text-[10px] font-medium border border-white/10">
                  家族精神纪念馆
                </span>
                <span class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
              </div>
              
              <h2 class="text-2xl font-serif font-medium leading-relaxed mb-3">
                数字生命<br>
                <span class="text-[#E8D5C4]">世代相传</span>
              </h2>
              
              <p class="text-xs text-white/80 leading-relaxed mb-6 max-w-[280px]">
                打破时空限制，让逝去的亲人"可陪伴"、家族智慧"可传承"、思念情感"可寄托"
              </p>
              
              <div class="flex items-center space-x-6 border-t border-white/20 pt-4">
                <div>
                  <p class="text-lg font-bold">128</p>
                  <p class="text-[10px] text-white/60">家族成员</p>
                </div>
                <div>
                  <p class="text-lg font-bold">56</p>
                  <p class="text-[10px] text-white/60">珍贵影像</p>
                </div>
                <div>
                  <p class="text-lg font-bold">3</p>
                  <p class="text-[10px] text-white/60">数字生命</p>
                </div>
              </div>
            </div>
            
            <div class="absolute -right-4 -bottom-4 w-32 h-32 opacity-20">
              <Icon icon="solar:tree-bold" class="text-white text-8xl" />
            </div>
          </div>
        </section>

        <section class="px-6 mt-8">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-base font-bold text-[#5C4A3A] font-serif">五大传承模块</h3>
            <span class="text-xs text-gray-400">滑动查看</span>
          </div>
          
          <div class="grid grid-cols-5 gap-2">
            <div class="flex flex-col items-center group cursor-pointer">
              <div class="w-12 h-12 bg-white rounded-2xl flex items-center justify-center mb-2 shadow-soft border border-[#E8D5C4] group-active:scale-90 transition-all relative">
                <div class="absolute inset-0 bg-[#E8D5C4] rounded-2xl opacity-0 group-hover:opacity-20 transition-opacity"></div>
                <Icon icon="solar:tree-bold-duotone" class="text-[#8B6F4E] text-xl" />
              </div>
              <span class="text-xs font-semibold text-[#5C4A3A]">家承</span>
              <span class="text-[8px] text-gray-400 mt-0.5">族谱</span>
            </div>

            <div class="flex flex-col items-center group cursor-pointer">
              <div class="w-12 h-12 bg-white rounded-2xl flex items-center justify-center mb-2 shadow-soft border border-orange-100 group-active:scale-90 transition-all">
                <Icon icon="solar:gallery-wide-bold-duotone" class="text-orange-600 text-xl" />
              </div>
              <span class="text-xs font-semibold text-[#5C4A3A]">影集</span>
              <span class="text-[8px] text-gray-400 mt-0.5">影像</span>
            </div>

            <div class="flex flex-col items-center group cursor-pointer">
              <div class="w-14 h-14 bg-gradient-to-br from-[#8B6F4E] to-[#A67B5B] rounded-2xl flex items-center justify-center mb-2 shadow-glow border-2 border-white group-active:scale-90 transition-all relative -mt-1">
                <Icon icon="solar:magic-stick-3-bold-duotone" class="text-white text-2xl" />
                <div class="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border-2 border-white"></div>
              </div>
              <span class="text-xs font-bold text-[#8B6F4E]">生境</span>
              <span class="text-[8px] text-[#D4A574] font-medium">数字生命</span>
            </div>

            <div class="flex flex-col items-center group cursor-pointer">
              <div class="w-12 h-12 bg-white rounded-2xl flex items-center justify-center mb-2 shadow-soft border border-emerald-100 group-active:scale-90 transition-all">
                <Icon icon="solar:chat-round-dots-bold-duotone" class="text-emerald-600 text-xl" />
              </div>
              <span class="text-xs font-semibold text-[#5C4A3A]">语伴</span>
              <span class="text-[8px] text-gray-400 mt-0.5">AI对话</span>
            </div>

            <div class="flex flex-col items-center group cursor-pointer">
              <div class="w-12 h-12 bg-white rounded-2xl flex items-center justify-center mb-2 shadow-soft border border-blue-100 group-active:scale-90 transition-all">
                <Icon icon="solar:heart-lock-bold-duotone" class="text-blue-500 text-xl" />
              </div>
              <span class="text-xs font-semibold text-[#5C4A3A]">念境</span>
              <span class="text-[8px] text-gray-400 mt-0.5">3D空间</span>
            </div>
          </div>
        </section>

        <section class="px-6 mt-8">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-base font-bold text-[#5C4A3A] font-serif">我的数字家人</h3>
            <button class="text-xs text-[#8B6F4E] font-medium flex items-center">
              查看全部
              <Icon icon="material-symbols:chevron-right" class="ml-1" style="font-size: 16px;" />
            </button>
          </div>
          
          <div class="space-y-3">
            <div class="bg-white rounded-2xl p-4 shadow-soft border border-stone-100 hover-lift cursor-pointer flex items-center space-x-4">
              <div class="relative">
                <div class="w-16 h-16 rounded-full bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] p-0.5">
                  <div class="w-full h-full rounded-full bg-gray-200 overflow-hidden">
                    <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face" class="w-full h-full object-cover" alt="祖父">
                  </div>
                </div>
                <div class="absolute bottom-0 right-0 w-5 h-5 bg-green-500 rounded-full border-2 border-white flex items-center justify-center">
                  <Icon icon="solar:check-bold" class="text-white text-xs" />
                </div>
              </div>
              <div class="flex-1">
                <div class="flex items-center space-x-2">
                  <h4 class="font-bold text-gray-800">祖父 · 张明远</h4>
                  <span class="px-2 py-0.5 bg-[#E8D5C4] text-[#8B6F4E] text-[10px] rounded-full">已激活</span>
                </div>
                <p class="text-xs text-gray-500 mt-1">1928-2018 · 训练度 98%</p>
                <div class="flex items-center mt-2 space-x-3">
                  <span class="text-[10px] text-gray-400 flex items-center">
                    <Icon icon="solar:chat-dots-linear" class="mr-1" style="font-size: 12px;" />
                    2.3k 对话
                  </span>
                  <span class="text-[10px] text-gray-400 flex items-center">
                    <Icon icon="solar:clock-circle-linear" class="mr-1" style="font-size: 12px;" />
                    3天前互动
                  </span>
                </div>
              </div>
              <button class="w-10 h-10 rounded-full bg-[#8B6F4E] flex items-center justify-center shadow-md hover:shadow-lg transition-shadow">
                <Icon icon="solar:phone-bold" class="text-white text-xl" />
              </button>
            </div>

            <div class="bg-white rounded-2xl p-4 shadow-soft border border-stone-100 hover-lift cursor-pointer flex items-center space-x-4 opacity-80">
              <div class="relative">
                <div class="w-16 h-16 rounded-full bg-gradient-to-br from-gray-200 to-gray-300 p-0.5">
                  <div class="w-full h-full rounded-full bg-gray-200 overflow-hidden">
                    <img src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&h=200&fit=crop&crop=face" class="w-full h-full object-cover grayscale" alt="祖母">
                  </div>
                </div>
                <div class="absolute bottom-0 right-0 w-5 h-5 bg-amber-400 rounded-full border-2 border-white flex items-center justify-center">
                  <Icon icon="solar:pause-bold" class="text-white text-xs" />
                </div>
              </div>
              <div class="flex-1">
                <div class="flex items-center space-x-2">
                  <h4 class="font-bold text-gray-800">祖母 · 李淑华</h4>
                  <span class="px-2 py-0.5 bg-gray-100 text-gray-500 text-[10px] rounded-full">训练中</span>
                </div>
                <p class="text-xs text-gray-500 mt-1">1932-2020 · 训练度 76%</p>
                <div class="w-full bg-gray-100 rounded-full h-1.5 mt-2">
                  <div class="bg-amber-400 h-1.5 rounded-full" style="width: 76%"></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="px-6 mt-8">
          <h3 class="text-base font-bold text-[#5C4A3A] font-serif mb-4">家族记忆轴</h3>
          
          <div class="relative pl-6 space-y-6">
            <div class="absolute left-[11px] top-2 bottom-2 w-px timeline-line"></div>
            
            <div class="relative">
              <div class="absolute left-[-17px] top-1 w-3 h-3 bg-[#8B6F4E] rounded-full border-2 border-white shadow-sm"></div>
              <div class="bg-white rounded-xl p-3 shadow-soft border border-stone-100">
                <div class="flex items-start space-x-3">
                  <div class="photo-frame w-20 h-20 rounded-lg overflow-hidden flex-shrink-0 bg-gray-100">
                    <img src="https://images.unsplash.com/photo-1511895426328-dc8714191300?w=300&h=300&fit=crop" class="w-full h-full object-cover" alt="全家福">
                  </div>
                  <div>
                    <p class="text-xs text-gray-400 mb-1">1985年春</p>
                    <h4 class="text-sm font-bold text-gray-800">四世同堂全家福</h4>
                    <p class="text-xs text-gray-500 mt-1 line-clamp-2">爷爷六十大寿，全家二十三口人在老宅院子里的合影...</p>
                    <div class="flex items-center mt-2 space-x-2">
                      <span class="text-[10px] text-gray-400">12张影像</span>
                      <span class="w-1 h-1 bg-gray-300 rounded-full"></span>
                      <span class="text-[10px] text-gray-400">3个故事</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="relative">
              <div class="absolute left-[-17px] top-1 w-3 h-3 bg-[#D4A574] rounded-full border-2 border-white shadow-sm"></div>
              <div class="bg-white rounded-xl p-3 shadow-soft border border-stone-100">
                <div class="flex items-start space-x-3">
                  <div class="w-10 h-10 rounded-full bg-[#E8D5C4] flex items-center justify-center flex-shrink-0">
                    <Icon icon="solar:pen-new-square-bold" class="text-[#8B6F4E]" />
                  </div>
                  <div>
                    <p class="text-xs text-gray-400 mb-1">昨天</p>
                    <h4 class="text-sm font-bold text-gray-800">给爷爷写了一封信</h4>
                    <p class="text-xs text-gray-500 mt-1">通过时光信箱功能，倾诉近期的工作感悟...</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="relative">
              <div class="absolute left-[-17px] top-1 w-3 h-3 bg-emerald-500 rounded-full border-2 border-white shadow-sm"></div>
              <div class="bg-white rounded-xl p-3 shadow-soft border border-stone-100">
                <div class="flex items-start space-x-3">
                  <div class="w-10 h-10 rounded-full bg-emerald-50 flex items-center justify-center flex-shrink-0">
                    <Icon icon="solar:chat-round-dots-bold" class="text-emerald-600" />
                  </div>
                  <div>
                    <p class="text-xs text-gray-400 mb-1">2小时前</p>
                    <h4 class="text-sm font-bold text-gray-800">与祖父数字人对话</h4>
                    <p class="text-xs text-gray-500 mt-1">讨论了关于家族传承的话题，获得了宝贵建议...</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="px-6 mt-8 mb-8">
          <div class="grid grid-cols-2 gap-3">
            <button class="bg-white rounded-2xl p-4 shadow-soft border border-stone-100 flex flex-col items-center space-y-2 hover-lift">
              <div class="w-12 h-12 bg-[#E8D5C4] rounded-full flex items-center justify-center">
                <Icon icon="solar:upload-minimalistic-bold" class="text-[#8B6F4E] text-2xl" />
              </div>
              <span class="text-sm font-medium text-gray-700">上传老照片</span>
              <span class="text-[10px] text-gray-400">修复 & 上色</span>
            </button>
            
            <button class="bg-white rounded-2xl p-4 shadow-soft border border-stone-100 flex flex-col items-center space-y-2 hover-lift">
              <div class="w-12 h-12 bg-[#F5E6D3] rounded-full flex items-center justify-center">
                <Icon icon="solar:video-frame-play-horizontal-bold" class="text-[#D4A574] text-2xl" />
              </div>
              <span class="text-sm font-medium text-gray-700">生成影像</span>
              <span class="text-[10px] text-gray-400">动态回忆</span>
            </button>
          </div>
        </section>

        <div class="px-6 mb-8 text-center">
          <div class="inline-block seal-stamp px-3 py-1.5 mb-3">
            <span class="text-xs font-serif font-bold tracking-widest">精神永存</span>
          </div>
          <p class="text-xs text-gray-400 tracking-widest uppercase">Digital Life, Eternal Legacy</p>
        </div>
      </div>

      <nav class="absolute bottom-0 w-full h-[84px] bg-white/95 backdrop-blur-xl border-t border-stone-100 px-2 flex justify-between items-start pt-2 safe-area-inset-bottom z-50">
        <div class="flex flex-col items-center flex-1 py-2 cursor-pointer">
          <div class="w-10 h-10 rounded-full bg-[#8B6F4E]/10 flex items-center justify-center">
            <Icon icon="solar:home-2-bold" class="text-xl text-[#8B6F4E]" />
          </div>
          <span class="text-[10px] mt-1 font-bold text-[#8B6F4E]">首页</span>
        </div>
        
        <div class="flex flex-col items-center flex-1 py-2 cursor-pointer opacity-60 hover:opacity-100 transition-opacity">
          <div class="w-10 h-10 rounded-full flex items-center justify-center">
            <Icon icon="solar:tree-bold-duotone" class="text-xl text-gray-400" />
          </div>
          <span class="text-[10px] mt-1 text-gray-400">家承</span>
        </div>
        
        <div class="flex flex-col items-center flex-1 -mt-5 relative">
          <div class="w-16 h-16 bg-gradient-to-br from-[#8B6F4E] to-[#A67B5B] rounded-full border-4 border-[#FAF7F2] shadow-warm flex items-center justify-center cursor-pointer active:scale-90 transition-transform animate-pulse-glow">
            <Icon icon="solar:magic-stick-3-bold-duotone" class="text-white text-3xl" />
          </div>
          <span class="text-[10px] mt-1 text-[#8B6F4E] font-bold">创建</span>
        </div>
        
        <div class="flex flex-col items-center flex-1 py-2 cursor-pointer opacity-60 hover:opacity-100 transition-opacity">
          <div class="w-10 h-10 rounded-full flex items-center justify-center">
            <Icon icon="solar:chat-round-dots-bold-duotone" class="text-xl text-gray-400" />
          </div>
          <span class="text-[10px] mt-1 text-gray-400">语伴</span>
        </div>
        
        <div class="flex flex-col items-center flex-1 py-2 cursor-pointer opacity-60 hover:opacity-100 transition-opacity">
          <div class="w-10 h-10 rounded-full flex items-center justify-center">
            <Icon icon="solar:user-bold" class="text-xl text-gray-400" />
          </div>
          <span class="text-[10px] mt-1 text-gray-400">我的</span>
        </div>
      </nav>

      <div class="absolute bottom-2 left-1/2 -translate-x-1/2 w-32 h-1 bg-gray-900/20 rounded-full z-50"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Icon } from '@iconify/vue'

const noisePatternStyle = computed(() => ({
  backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox=%220 0 100 100%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22 opacity=%220.3%22/%3E%3C/svg%3E")`
}))

const dotPatternStyle = computed(() => ({
  backgroundImage: `url("data:image/svg+xml,%3Csvg width=%2260%22 height=%2260%22 viewBox=%220 0 60 60%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cg fill=%22none%22 fill-rule=%22evenodd%22%3E%3Cg fill=%22%23ffffff%22 fill-opacity=%220.4%22%3E%3Cpath d=%22M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
}))
</script>
