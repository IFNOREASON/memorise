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
          <button class="w-10 h-10 rounded-full bg-white/80 flex items-center justify-center shadow-sm hover:shadow-md transition-shadow">
            <Icon icon="solar:bell-bold" class="text-gray-600" />
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

    <main class="max-w-7xl mx-auto px-6 py-6">
      <section class="bg-white rounded-2xl shadow-soft border border-stone-100 p-6 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-bold text-[#5C4A3A] font-serif flex items-center space-x-2">
            <Icon icon="solar:home-2-bold" class="text-[#8B6F4E]" />
            <span>家族信息</span>
          </h2>
          <button @click="showFamilySettings = true" class="text-sm text-[#8B6F4E] font-medium hover:text-[#D4A574] transition-colors flex items-center space-x-1">
            <Icon icon="solar:settings-bold" class="text-lg" />
            <span>设置</span>
          </button>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-[#FAF7F2] rounded-xl p-4">
            <p class="text-xs text-gray-500 mb-1">堂号</p>
            <p class="font-bold text-[#5C4A3A]">{{ familyInfo.hallName }}</p>
          </div>
          <div class="bg-[#FAF7F2] rounded-xl p-4">
            <p class="text-xs text-gray-500 mb-1">姓氏</p>
            <p class="font-bold text-[#5C4A3A]">{{ familyInfo.surname }}氏</p>
          </div>
          <div class="bg-[#FAF7F2] rounded-xl p-4">
            <p class="text-xs text-gray-500 mb-1">始祖</p>
            <p class="font-bold text-[#5C4A3A]">{{ familyInfo.ancestor }}</p>
          </div>
          <div class="bg-[#FAF7F2] rounded-xl p-4">
            <p class="text-xs text-gray-500 mb-1">成员总数</p>
            <p class="font-bold text-[#5C4A3A]">{{ familyMembers.length }} 人</p>
          </div>
        </div>
        <div class="mt-4 pt-4 border-t border-stone-100">
          <p class="text-xs text-gray-500 mb-1">家族简介</p>
          <p class="text-sm text-gray-700 leading-relaxed">{{ familyInfo.description }}</p>
        </div>
        <div class="mt-4 pt-4 border-t border-stone-100">
          <div class="flex items-center justify-between mb-2">
            <p class="text-xs text-gray-500">字辈排行</p>
            <button @click="showFamilySettings = true" class="text-xs text-[#8B6F4E] hover:text-[#D4A574] transition-colors flex items-center space-x-1">
              <Icon icon="solar:pen-bold" class="text-sm" />
              <span>编辑</span>
            </button>
          </div>
          <div class="flex flex-wrap gap-2">
            <span v-for="(zi, index) in familyInfo.ziBei" :key="index" 
              class="px-3 py-1 bg-[#E8D5C4] text-[#8B6F4E] text-sm rounded-full font-medium">
              第{{ index + 1 }}世：{{ zi }}
            </span>
          </div>
        </div>
      </section>

      <section class="bg-white rounded-2xl shadow-soft border border-stone-100 p-6 mb-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <h2 class="text-lg font-bold text-[#5C4A3A] font-serif flex items-center space-x-2">
            <Icon icon="solar:magnifer-bold" class="text-[#8B6F4E]" />
            <span>查询检索</span>
          </h2>
          <div class="flex flex-col md:flex-row gap-3">
            <div class="relative">
              <Icon icon="solar:search-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input v-model="searchKeyword" type="text" placeholder="输入姓名搜索..." 
                class="pl-10 pr-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4] w-full md:w-64" />
            </div>
            <button @click="handleSearch" class="px-4 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all flex items-center space-x-2">
              <Icon icon="solar:search-bold" class="text-sm" />
              <span>搜索</span>
            </button>
          </div>
        </div>
      </section>

      <section class="bg-white rounded-2xl shadow-soft border border-stone-100 p-6 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-bold text-[#5C4A3A] font-serif flex items-center space-x-2">
            <Icon icon="solar:tree-bold" class="text-[#8B6F4E]" />
            <span>世系图谱</span>
          </h2>
          <div class="flex items-center space-x-2">
            <button @click="showMemberModal = true" class="px-3 py-1 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-lg text-sm font-medium shadow-warm hover:shadow-lg transition-all flex items-center space-x-1">
              <Icon icon="solar:add-circle-bold" class="text-sm" />
              <span>新增成员</span>
            </button>
            <button @click="zoomIn" class="w-8 h-8 rounded-lg bg-[#E8D5C4] flex items-center justify-center hover:bg-[#D4A574] transition-colors">
              <Icon icon="material-symbols:add" class="text-[#8B6F4E]" />
            </button>
            <span class="text-sm text-gray-500 w-16 text-center">{{ Math.round(scale * 100) }}%</span>
            <button @click="zoomOut" class="w-8 h-8 rounded-lg bg-[#E8D5C4] flex items-center justify-center hover:bg-[#D4A574] transition-colors">
              <Icon icon="material-symbols:remove" class="text-[#8B6F4E]" />
            </button>
            <button @click="resetZoom" class="px-3 py-1 rounded-lg bg-[#E8D5C4] text-[#8B6F4E] text-sm font-medium hover:bg-[#D4A574] transition-colors">
              重置
            </button>
            <button @click="toggleTreeMode" class="px-3 py-1 rounded-lg bg-white border border-[#E8D5C4] text-[#8B6F4E] text-sm font-medium hover:bg-[#E8D5C4] transition-colors">
              {{ isTreeMode ? '树形模式' : '列表模式' }}
            </button>
          </div>
        </div>
        
        <div class="relative overflow-auto bg-gradient-to-br from-[#FAF7F2] to-[#F5F1EC] rounded-xl border border-stone-100" 
          style="min-height: 500px;">
          <D3Tree 
            ref="d3TreeRef"
            :data="familyMembers"
            :selected-id="selectedMember?.id"
            :scale="scale"
            @select="selectMember"
            @context-menu="showContextMenuForNode" />
        </div>
        
        <div class="flex items-center justify-center gap-4 mt-3">
          <p class="text-xs text-gray-400">提示：右键点击节点可快速添加同级或子节点</p>
          <div class="flex items-center gap-2">
            <button @click="expandAll" class="px-3 py-1 text-xs text-[#8B6F4E] bg-[#E8D5C4] rounded-lg hover:bg-[#D4A574] transition-colors">
              展开全部
            </button>
            <button @click="collapseAll" class="px-3 py-1 text-xs text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
              折叠全部
            </button>
          </div>
        </div>
      </section>

      <section class="bg-white rounded-2xl shadow-soft border border-stone-100 p-6 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-bold text-[#5C4A3A] font-serif flex items-center space-x-2">
            <Icon icon="solar:users-group-two-bold" class="text-[#8B6F4E]" />
            <span>族人列表</span>
            <span class="text-sm font-normal text-gray-400">（{{ filteredMembers.length }}人）</span>
          </h2>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-stone-200">
                <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">姓名</th>
                <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">性别</th>
                <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">世代</th>
                <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">生卒</th>
                <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">配偶</th>
                <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">现居地</th>
                <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">状态</th>
                <th class="text-right py-3 px-4 text-xs font-medium text-gray-500 uppercase">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="member in filteredMembers" :key="member.id" 
                class="border-b border-stone-100 hover:bg-[#FAF7F2] transition-colors cursor-pointer"
                @click="selectMember(member)">
                <td class="py-3 px-4">
                  <span class="font-medium text-[#5C4A3A]">{{ member.name }}</span>
                </td>
                <td class="py-3 px-4">
                  <span class="px-2 py-1 rounded-full text-xs"
                    :class="member.gender === 'male' ? 'bg-blue-100 text-blue-700' : 'bg-pink-100 text-pink-700'">
                    {{ member.gender === 'male' ? '男' : '女' }}
                  </span>
                </td>
                <td class="py-3 px-4 text-sm text-gray-600">
                  第{{ member.generation }}世（{{ familyInfo.ziBei[member.generation - 1] || '' }}）
                </td>
                <td class="py-3 px-4 text-sm text-gray-600">
                  {{ member.birthYear || '未知' }}
                  <span v-if="member.deathYear"> - {{ member.deathYear }}</span>
                </td>
                <td class="py-3 px-4 text-sm text-gray-600">{{ member.spouse || '无' }}</td>
                <td class="py-3 px-4 text-sm text-gray-600">{{ member.residence || '未知' }}</td>
                <td class="py-3 px-4">
                  <span class="px-2 py-1 rounded-full text-xs"
                    :class="member.status === 'alive' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'">
                    {{ member.status === 'alive' ? '在世' : '已故' }}
                  </span>
                </td>
                <td class="py-3 px-4 text-right">
                  <button @click.stop="editMember(member)" class="text-[#8B6F4E] text-sm hover:text-[#D4A574] transition-colors mr-3">
                    编辑
                  </button>
                  <button @click.stop="deleteMember(member)" class="text-red-500 text-sm hover:text-red-600 transition-colors">
                    删除
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="bg-white rounded-2xl shadow-soft border border-stone-100 p-6">
        <h2 class="text-lg font-bold text-[#5C4A3A] font-serif flex items-center space-x-2 mb-4">
          <Icon icon="solar:database-bold" class="text-[#8B6F4E]" />
          <span>数据管理</span>
        </h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button class="p-4 bg-[#FAF7F2] rounded-xl hover:bg-[#E8D5C4]/50 transition-colors text-center group">
            <Icon icon="solar:import-bold" class="text-2xl text-[#8B6F4E] mx-auto mb-2 group-hover:scale-110 transition-transform" />
            <p class="text-sm font-medium text-[#5C4A3A]">导入数据</p>
            <p class="text-xs text-gray-500 mt-1">Excel/CSV</p>
          </button>
          <button class="p-4 bg-[#FAF7F2] rounded-xl hover:bg-[#E8D5C4]/50 transition-colors text-center group">
            <Icon icon="solar:export-bold" class="text-2xl text-[#8B6F4E] mx-auto mb-2 group-hover:scale-110 transition-transform" />
            <p class="text-sm font-medium text-[#5C4A3A]">导出数据</p>
            <p class="text-xs text-gray-500 mt-1">Excel/PDF</p>
          </button>
          <button class="p-4 bg-[#FAF7F2] rounded-xl hover:bg-[#E8D5C4]/50 transition-colors text-center group">
            <Icon icon="solar:history-bold" class="text-2xl text-[#8B6F4E] mx-auto mb-2 group-hover:scale-110 transition-transform" />
            <p class="text-sm font-medium text-[#5C4A3A]">操作日志</p>
            <p class="text-xs text-gray-500 mt-1">修改记录</p>
          </button>
          <button class="p-4 bg-[#FAF7F2] rounded-xl hover:bg-[#E8D5C4]/50 transition-colors text-center group">
            <Icon icon="solar:shield-check-bold" class="text-2xl text-[#8B6F4E] mx-auto mb-2 group-hover:scale-110 transition-transform" />
            <p class="text-sm font-medium text-[#5C4A3A]">备份恢复</p>
            <p class="text-xs text-gray-500 mt-1">数据安全</p>
          </button>
        </div>
      </section>
    </main>

    <div v-if="contextMenu.visible" 
      class="fixed z-[100] bg-white rounded-lg shadow-xl border border-stone-200 py-2 min-w-[160px]"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      @click.stop>
      <button @click="addSibling" class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-[#E8D5C4] flex items-center space-x-2">
        <Icon icon="solar:user-add-bold" class="text-[#8B6F4E]" />
        <span>添加同级节点</span>
      </button>
      <button @click="addChild" class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-[#E8D5C4] flex items-center space-x-2">
        <Icon icon="solar:folder-add-bold" class="text-[#8B6F4E]" />
        <span>添加子节点</span>
      </button>
      <div class="border-t border-stone-100 my-1"></div>
      <button @click="editContextMember" class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-[#E8D5C4] flex items-center space-x-2">
        <Icon icon="solar:pen-bold" class="text-[#8B6F4E]" />
        <span>编辑节点</span>
      </button>
    </div>

    <div v-if="showMemberModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-white border-b border-stone-100 px-6 py-4 flex items-center justify-between">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">
            {{ editingMember ? '编辑成员' : (modalMode === 'sibling' ? '添加同级节点' : (modalMode === 'child' ? '添加子节点' : '新增成员')) }}
          </h3>
          <button @click="closeMemberModal" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="material-symbols:close" class="text-gray-500" />
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">姓名 *</label>
            <input v-model="memberForm.name" type="text" placeholder="请输入姓名"
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">性别 *</label>
              <select v-model="memberForm.gender" 
                class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
                <option value="male">男</option>
                <option value="female">女</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">世代</label>
              <select v-model="memberForm.generation" 
                class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
                <option v-for="(zi, index) in familyInfo.ziBei" :key="index" :value="index + 1">
                  第{{ index + 1 }}世（{{ zi }}）
                </option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">出生年份</label>
              <input v-model="memberForm.birthYear" type="text" placeholder="如：1980"
                class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">去世年份</label>
              <input v-model="memberForm.deathYear" type="text" placeholder="如：2020（在世可不填）"
                class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">状态</label>
            <select v-model="memberForm.status" 
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
              <option value="alive">在世</option>
              <option value="deceased">已故</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">配偶</label>
            <input v-model="memberForm.spouse" type="text" placeholder="请输入配偶姓名"
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">父亲</label>
            <select v-model="memberForm.fatherId" 
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
              <option value="">请选择</option>
              <option v-for="m in maleMembers" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">现居地</label>
            <input v-model="memberForm.residence" type="text" placeholder="请输入现居地"
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">备注</label>
            <textarea v-model="memberForm.note" rows="3" placeholder="请输入备注信息"
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4] resize-none"></textarea>
          </div>
        </div>
        <div class="sticky bottom-0 bg-white border-t border-stone-100 px-6 py-4 flex justify-end space-x-3">
          <button @click="closeMemberModal" class="px-6 py-2 text-gray-600 bg-gray-100 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors">
            取消
          </button>
          <button @click="saveMember" class="px-6 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all">
            保存
          </button>
        </div>
      </div>
    </div>

    <div v-if="showFamilySettings" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-white border-b border-stone-100 px-6 py-4 flex items-center justify-between">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">家族设置</h3>
          <button @click="showFamilySettings = false" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="material-symbols:close" class="text-gray-500" />
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">堂号</label>
            <input v-model="familySettingsForm.hallName" type="text" placeholder="如：陇西堂"
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">姓氏</label>
            <input v-model="familySettingsForm.surname" type="text" placeholder="如：李"
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">始祖</label>
            <input v-model="familySettingsForm.ancestor" type="text" placeholder="如：李太白"
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">家族简介</label>
            <textarea v-model="familySettingsForm.description" rows="3" placeholder="请输入家族简介"
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4] resize-none"></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">字辈排行（用逗号分隔）</label>
            <input v-model="familySettingsForm.ziBeiStr" type="text" placeholder="如：元,亨,利,贞,仁,义,礼,智,信"
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
            <p class="text-xs text-gray-400 mt-1">按世代顺序输入字辈，用英文逗号分隔</p>
          </div>
        </div>
        <div class="sticky bottom-0 bg-white border-t border-stone-100 px-6 py-4 flex justify-end space-x-3">
          <button @click="showFamilySettings = false" class="px-6 py-2 text-gray-600 bg-gray-100 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors">
            取消
          </button>
          <button @click="saveFamilySettings" class="px-6 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all">
            保存
          </button>
        </div>
      </div>
    </div>

    <div v-if="selectedMember" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4" @click.self="selectedMember = null">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        <div class="bg-gradient-to-br from-[#8B6F4E] to-[#A67B5B] rounded-t-2xl p-6 text-white flex-shrink-0">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <div class="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center">
                <Icon :icon="selectedMember.gender === 'male' ? 'solar:user-bold' : 'solar:user-bold'" class="text-3xl" />
              </div>
              <div>
                <h3 class="text-xl font-bold font-serif">{{ selectedMember.name }}</h3>
                <p class="text-white/80 text-sm">第{{ selectedMember.generation }}世 · {{ familyInfo.ziBei[selectedMember.generation - 1] || '' }}字辈</p>
              </div>
            </div>
            <button @click="selectedMember = null" class="w-8 h-8 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors">
              <Icon icon="material-symbols:close" class="text-white" />
            </button>
          </div>
        </div>
        
        <div class="flex border-b border-[#E8D5C4] flex-shrink-0">
          <button 
            @click="memberDetailTab = 'info'"
            :class="[
              'flex-1 px-6 py-3 text-sm font-medium transition-colors relative',
              memberDetailTab === 'info' ? 'text-[#8B6F4E]' : 'text-gray-500 hover:text-gray-700'
            ]">
            <span class="flex items-center justify-center space-x-2">
              <Icon icon="solar:user-circle-bold" class="text-lg" />
              <span>基本信息</span>
            </span>
            <div v-if="memberDetailTab === 'info'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-[#8B6F4E]"></div>
          </button>
          <button 
            @click="memberDetailTab = 'media'"
            :class="[
              'flex-1 px-6 py-3 text-sm font-medium transition-colors relative',
              memberDetailTab === 'media' ? 'text-[#8B6F4E]' : 'text-gray-500 hover:text-gray-700'
            ]">
            <span class="flex items-center justify-center space-x-2">
              <Icon icon="solar:gallery-add-bold" class="text-lg" />
              <span>人物影像</span>
              <span v-if="(selectedMember.medias?.length || 0) > 0" 
                class="w-5 h-5 rounded-full bg-[#8B6F4E] text-white text-xs flex items-center justify-center">
                {{ selectedMember.medias?.length || 0 }}
              </span>
            </span>
            <div v-if="memberDetailTab === 'media'" class="absolute bottom-0 left-0 right-0 h-0.5 bg-[#8B6F4E]"></div>
          </button>
        </div>
        
        <div class="flex-1 overflow-y-auto">
          <div v-if="memberDetailTab === 'info'" class="p-6 space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div class="bg-[#FAF7F2] rounded-xl p-3">
                <p class="text-xs text-gray-500">性别</p>
                <p class="font-medium text-[#5C4A3A]">{{ selectedMember.gender === 'male' ? '男' : '女' }}</p>
              </div>
              <div class="bg-[#FAF7F2] rounded-xl p-3">
                <p class="text-xs text-gray-500">状态</p>
                <p class="font-medium text-[#5C4A3A]">{{ selectedMember.status === 'alive' ? '在世' : '已故' }}</p>
              </div>
            </div>
            <div class="bg-[#FAF7F2] rounded-xl p-4 space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-500">出生年份</span>
                <span class="font-medium text-[#5C4A3A]">{{ selectedMember.birthYear || '未知' }}</span>
              </div>
              <div v-if="selectedMember.deathYear" class="flex items-center justify-between">
                <span class="text-sm text-gray-500">去世年份</span>
                <span class="font-medium text-[#5C4A3A]">{{ selectedMember.deathYear }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-500">配偶</span>
                <span class="font-medium text-[#5C4A3A]">{{ selectedMember.spouse || '无' }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-500">现居地</span>
                <span class="font-medium text-[#5C4A3A]">{{ selectedMember.residence || '未知' }}</span>
              </div>
            </div>
            <div v-if="selectedMember.note" class="bg-[#FAF7F2] rounded-xl p-4">
              <p class="text-xs text-gray-500 mb-2">备注</p>
              <p class="text-sm text-gray-700">{{ selectedMember.note }}</p>
            </div>
          </div>
          
          <div v-else-if="memberDetailTab === 'media'" class="p-6">
            <div v-if="!selectedMember.medias || selectedMember.medias.length === 0" class="flex flex-col items-center justify-center py-16">
              <Icon icon="solar:gallery-empty-linear" class="text-6xl text-gray-300 mb-4" />
              <p class="text-gray-500 mb-2">暂无影像资料</p>
              <p class="text-gray-400 text-sm">该成员暂无保存的影像记录</p>
            </div>
            
            <div v-else class="grid grid-cols-2 sm:grid-cols-3 gap-4">
              <div v-for="media in selectedMember.medias" :key="media.id"
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
                  <div class="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
                    <div class="flex items-center space-x-2">
                      <button class="w-10 h-10 bg-white rounded-full flex items-center justify-center hover:bg-[#E8D5C4] transition-colors">
                        <Icon icon="solar:eye-bold" class="text-[#8B6F4E]" />
                      </button>
                      <button class="w-10 h-10 bg-white rounded-full flex items-center justify-center hover:bg-[#E8D5C4] transition-colors">
                        <Icon icon="solar:download-minimalistic-bold" class="text-[#8B6F4E]" />
                      </button>
                    </div>
                  </div>
                </div>
                <div class="p-3 bg-white">
                  <div class="space-y-1">
                    <div class="flex items-center space-x-1 text-xs text-gray-500">
                      <Icon icon="solar:clock-circle-linear" class="text-xs" />
                      <span>{{ media.dateTime }}</span>
                    </div>
                    <div class="flex items-center space-x-1 text-xs text-gray-400">
                      <Icon icon="solar:point-on-map-linear" class="text-xs" />
                      <span class="truncate">{{ media.location }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="border-t border-stone-100 px-6 py-4 flex justify-end space-x-3 flex-shrink-0">
          <button v-if="memberDetailTab === 'info'" 
            @click="editMember(selectedMember); selectedMember = null" 
            class="px-4 py-2 bg-[#E8D5C4] text-[#8B6F4E] rounded-xl text-sm font-medium hover:bg-[#D4A574] transition-colors">
            编辑信息
          </button>
          <button v-else-if="memberDetailTab === 'media'" 
            class="px-4 py-2 bg-[#E8D5C4] text-[#8B6F4E] rounded-xl text-sm font-medium hover:bg-[#D4A574] transition-colors flex items-center space-x-2">
            <Icon icon="solar:add-circle-bold" class="text-sm" />
            <span>添加影像</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, defineComponent, h, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import D3Tree from './D3Tree.vue'
import { apiService, authStore, Family, FamilyMember } from '../services/api'

const router = useRouter()

const isLoading = ref(false)

const showUserMenu = ref(false)

interface NavItem {
  id: string
  label: string
  icon: string
}

const activeNav = ref('family')

const navItems: NavItem[] = [
  { id: 'home', label: '首页', icon: 'solar:home-2-bold' },
  { id: 'family', label: '家承', icon: 'solar:tree-bold-duotone' },
  { id: 'gallery', label: '影集', icon: 'solar:gallery-wide-bold-duotone' },
  { id: 'digital', label: '生境', icon: 'solar:magic-stick-3-bold-duotone' },
  { id: 'chat', label: '语伴', icon: 'solar:chat-round-dots-bold-duotone' },
]

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const closeUserMenu = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    showUserMenu.value = false
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

const handleChangePassword = () => {
  showUserMenu.value = false
  alert('修改密码功能请在首页使用')
}

const noisePatternStyle = computed(() => ({
  backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox=%220 0 100 100%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22 opacity=%220.3%22/%3E%3C/svg%3E")`
}))

const familyInfo = reactive<{
  hallName: string
  surname: string
  ancestor: string
  description: string
  ziBei: string[]
}>({
  hallName: '陇西堂',
  surname: '李',
  ancestor: '李太白',
  description: '本族源自陇西李氏，世代耕读传家，忠厚立世。自始祖迁居以来，已历数十代，族人遍布各地，恪守祖训，传承家风。',
  ziBei: ['元', '亨', '利', '贞', '仁', '义', '礼', '智', '信']
})

interface MemberMedia {
  id: string
  url: string
  type: 'image' | 'video'
  dateTime: string
  location: string
  duration?: string
}

interface FamilyMember {
  id: string
  name: string
  gender: 'male' | 'female'
  generation: number
  birthYear?: string
  deathYear?: string
  spouse?: string
  fatherId?: string
  residence?: string
  note?: string
  status: 'alive' | 'deceased'
  medias?: MemberMedia[]
}

interface TreeNodeData extends FamilyMember {
  children: TreeNodeData[]
}

const familyMembers = ref<FamilyMember[]>([])

const searchKeyword = ref('')
const selectedMember = ref<FamilyMember | null>(null)
const memberDetailTab = ref<'info' | 'media'>('info')
const showMemberModal = ref(false)
const showFamilySettings = ref(false)
const editingMember = ref<FamilyMember | null>(null)
const collapsedBranches = ref<string[]>([])
const scale = ref(1)
const isTreeMode = ref(true)
const modalMode = ref<'normal' | 'sibling' | 'child'>('normal')
const d3TreeRef = ref<InstanceType<typeof D3Tree> | null>(null)

const contextMenu = reactive({
  visible: false,
  x: 0,
  y: 0,
  member: null as FamilyMember | null
})

const memberForm = reactive({
  id: '',
  name: '',
  gender: 'male' as const,
  generation: 1,
  birthYear: '',
  deathYear: '',
  spouse: '',
  fatherId: '',
  residence: '',
  note: '',
  status: 'alive' as const
})

const familySettingsForm = reactive({
  hallName: familyInfo.hallName,
  surname: familyInfo.surname,
  ancestor: familyInfo.ancestor,
  description: familyInfo.description,
  ziBeiStr: familyInfo.ziBei.join(',')
})

const filteredMembers = computed(() => {
  let result = familyMembers.value
  if (searchKeyword.value) {
    result = result.filter(m => m.name.includes(searchKeyword.value))
  }
  return result
})

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    const matchedMember = familyMembers.value.find(m => m.name.includes(searchKeyword.value))
    if (matchedMember) {
      selectedMember.value = matchedMember
      setTimeout(() => {
        d3TreeRef.value?.focusNode(matchedMember.id)
      }, 100)
    } else {
      alert('未找到匹配的成员')
    }
  }
}

const maleMembers = computed(() => {
  return familyMembers.value.filter(m => m.gender === 'male')
})

const treeData = computed(() => {
  const generations: FamilyMember[][] = []
  const maxGeneration = Math.max(...familyMembers.value.map(m => m.generation))
  for (let i = 1; i <= maxGeneration; i++) {
    const genMembers = familyMembers.value.filter(m => m.generation === i)
    if (genMembers.length > 0) {
      generations.push(genMembers)
    }
  }
  return generations
})

const buildTree = (members: FamilyMember[]): TreeNodeData[] => {
  const memberMap = new Map<string, TreeNodeData>()
  const roots: TreeNodeData[] = []

  members.forEach(m => {
    memberMap.set(m.id, { ...m, children: [] })
  })

  members.forEach(m => {
    const node = memberMap.get(m.id)!
    if (m.fatherId && memberMap.has(m.fatherId)) {
      const parent = memberMap.get(m.fatherId)!
      parent.children.push(node)
    } else {
      if (!roots.some(r => r.id === node.id)) {
        roots.push(node)
      }
    }
  })

  if (roots.length === 0 && members.length > 0) {
    const firstGen = Math.min(...members.map(m => m.generation))
    members.filter(m => m.generation === firstGen).forEach(m => {
      if (!roots.some(r => r.id === m.id)) {
        const node = memberMap.get(m.id)!
        roots.push(node)
      }
    })
  }

  return roots
}

const treeRoots = computed(() => buildTree(familyMembers.value))

const loadData = async () => {
  isLoading.value = true
  try {
    const response = await apiService.getFamily()
    if (response.success && response.data) {
      const { family, members } = response.data
      familyInfo.hallName = family.hallName || ''
      familyInfo.surname = family.surname
      familyInfo.ancestor = family.ancestor || ''
      familyInfo.description = family.description || ''
      familyInfo.ziBei = family.ziBei || []
      familyMembers.value = members
      familySettingsForm.hallName = family.hallName || ''
      familySettingsForm.surname = family.surname
      familySettingsForm.ancestor = family.ancestor || ''
      familySettingsForm.description = family.description || ''
      familySettingsForm.ziBeiStr = (family.ziBei || []).join(',')
    } else {
      console.error('加载家族数据失败:', response.error)
    }
  } catch (error) {
    console.error('加载家族数据失败:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadData()
  document.addEventListener('click', closeUserMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeUserMenu)
})

const zoomIn = () => {
  scale.value = Math.min(scale.value + 0.1, 2)
}

const zoomOut = () => {
  scale.value = Math.max(scale.value - 0.1, 0.5)
}

const resetZoom = () => {
  scale.value = 1
}

const toggleTreeMode = () => {
  isTreeMode.value = !isTreeMode.value
}

const selectMember = (member: FamilyMember) => {
  selectedMember.value = member
  memberDetailTab.value = 'info'
}

const toggleCollapse = (memberId: string) => {
  const index = collapsedBranches.value.indexOf(memberId)
  if (index > -1) {
    collapsedBranches.value.splice(index, 1)
  } else {
    collapsedBranches.value.push(memberId)
  }
}

const editMember = (member: FamilyMember) => {
  editingMember.value = member
  modalMode.value = 'normal'
  memberForm.id = member.id
  memberForm.name = member.name
  memberForm.gender = member.gender
  memberForm.generation = member.generation
  memberForm.birthYear = member.birthYear || ''
  memberForm.deathYear = member.deathYear || ''
  memberForm.spouse = member.spouse || ''
  memberForm.fatherId = member.fatherId || ''
  memberForm.residence = member.residence || ''
  memberForm.note = member.note || ''
  memberForm.status = member.status
  showMemberModal.value = true
}

const closeMemberModal = () => {
  showMemberModal.value = false
  editingMember.value = null
  modalMode.value = 'normal'
  contextMenu.member = null
  resetMemberForm()
}

const resetMemberForm = () => {
  memberForm.id = ''
  memberForm.name = ''
  memberForm.gender = 'male'
  memberForm.generation = 1
  memberForm.birthYear = ''
  memberForm.deathYear = ''
  memberForm.spouse = ''
  memberForm.fatherId = ''
  memberForm.residence = ''
  memberForm.note = ''
  memberForm.status = 'alive'
}

const saveMember = async () => {
  if (!memberForm.name.trim()) {
    alert('请输入姓名')
    return
  }
  try {
    if (editingMember.value) {
      const response = await apiService.updateMember(editingMember.value.id, {
        name: memberForm.name,
        gender: memberForm.gender,
        generation: memberForm.generation,
        birthYear: memberForm.birthYear || undefined,
        deathYear: memberForm.deathYear || undefined,
        spouse: memberForm.spouse || undefined,
        fatherId: memberForm.fatherId || undefined,
        residence: memberForm.residence || undefined,
        note: memberForm.note || undefined,
        status: memberForm.status
      })
      if (response.success && response.data) {
        const index = familyMembers.value.findIndex(m => m.id === editingMember.value!.id)
        if (index > -1) {
          familyMembers.value[index] = response.data
        }
      } else {
        alert(`更新失败: ${response.error || '未知错误'}`)
        return
      }
    } else {
      const response = await apiService.createMember({
        name: memberForm.name,
        gender: memberForm.gender,
        generation: memberForm.generation,
        birthYear: memberForm.birthYear || undefined,
        deathYear: memberForm.deathYear || undefined,
        spouse: memberForm.spouse || undefined,
        fatherId: memberForm.fatherId || undefined,
        residence: memberForm.residence || undefined,
        note: memberForm.note || undefined,
        status: memberForm.status
      })
      if (response.success && response.data) {
        familyMembers.value.push(response.data)
      } else {
        alert(`创建失败: ${response.error || '未知错误'}`)
        return
      }
    }
    closeMemberModal()
  } catch (error) {
    console.error('保存成员失败:', error)
    alert(`保存失败: ${error instanceof Error ? error.message : '未知错误'}`)
  }
}

const deleteMember = async (member: FamilyMember) => {
  if (confirm(`确定要删除成员「${member.name}」吗？`)) {
    try {
      const response = await apiService.deleteMember(member.id)
      if (response.success) {
        const index = familyMembers.value.findIndex(m => m.id === member.id)
        if (index > -1) {
          familyMembers.value.splice(index, 1)
        }
      } else {
        alert(`删除失败: ${response.error || '未知错误'}`)
      }
    } catch (error) {
      console.error('删除成员失败:', error)
      alert(`删除失败: ${error instanceof Error ? error.message : '未知错误'}`)
    }
  }
}

const saveFamilySettings = async () => {
  try {
    const ziBei = familySettingsForm.ziBeiStr.split(',').map(z => z.trim()).filter(z => z)
    const response = await apiService.updateFamily({
      hallName: familySettingsForm.hallName,
      surname: familySettingsForm.surname,
      ancestor: familySettingsForm.ancestor,
      description: familySettingsForm.description,
      ziBei: ziBei
    })
    if (response.success && response.data) {
      familyInfo.hallName = response.data.hallName || ''
      familyInfo.surname = response.data.surname
      familyInfo.ancestor = response.data.ancestor || ''
      familyInfo.description = response.data.description || ''
      familyInfo.ziBei = response.data.ziBei || []
      showFamilySettings.value = false
    } else {
      alert(`保存失败: ${response.error || '未知错误'}`)
    }
  } catch (error) {
    console.error('保存家族设置失败:', error)
    alert(`保存失败: ${error instanceof Error ? error.message : '未知错误'}`)
  }
}

const showContextMenuForNode = (member: FamilyMember, event: MouseEvent) => {
  contextMenu.member = member
  contextMenu.x = event.clientX
  contextMenu.y = event.clientY
  contextMenu.visible = true
}

const hideContextMenu = () => {
  contextMenu.visible = false
}

const expandAll = () => {
  d3TreeRef.value?.expandAll()
}

const collapseAll = () => {
  d3TreeRef.value?.collapseAll()
}

const addSibling = () => {
  if (!contextMenu.member) return
  
  modalMode.value = 'sibling'
  editingMember.value = null
  resetMemberForm()
  
  memberForm.generation = contextMenu.member.generation
  memberForm.fatherId = contextMenu.member.fatherId || ''
  
  contextMenu.visible = false
  showMemberModal.value = true
}

const addChild = () => {
  if (!contextMenu.member) return
  
  if (contextMenu.member.gender === 'female') {
    alert('女性成员不能作为父亲添加子节点')
    contextMenu.visible = false
    return
  }
  
  modalMode.value = 'child'
  editingMember.value = null
  resetMemberForm()
  
  memberForm.generation = contextMenu.member.generation + 1
  memberForm.fatherId = contextMenu.member.id
  
  contextMenu.visible = false
  showMemberModal.value = true
}

const editContextMember = () => {
  if (!contextMenu.member) return
  contextMenu.visible = false
  editMember(contextMenu.member)
}

const TreeNode = defineComponent({
  name: 'TreeNode',
  props: {
    node: { type: Object as () => TreeNodeData, required: true },
    level: { type: Number, default: 0 },
    collapsedBranches: { type: Array as () => string[], default: () => [] },
    selectedMember: { type: Object as () => FamilyMember | null, default: null }
  },
  emits: ['select', 'context-menu', 'toggle-collapse'],
  setup(props, { emit }) {
    const isCollapsed = computed(() => props.collapsedBranches.includes(props.node.id))
    const hasChildren = computed(() => props.node.children.length > 0)
    
    const handleClick = () => {
      emit('select', props.node)
    }
    
    const handleContextMenu = (e: MouseEvent) => {
      e.preventDefault()
      e.stopPropagation()
      emit('context-menu', props.node, e)
    }
    
    const toggleCollapse = (e: MouseEvent) => {
      e.stopPropagation()
      emit('toggle-collapse', props.node.id)
    }
    
    return () => h('div', { class: 'flex flex-col items-center' }, [
      h('div', { 
        class: 'relative cursor-pointer group mb-2',
        onClick: handleClick,
        onContextmenu: handleContextMenu
      }, [
        h('div', {
          class: [
            'bg-white rounded-xl p-4 shadow-soft border-2 transition-all hover:shadow-md min-w-[160px]',
            props.selectedMember?.id === props.node.id ? 'border-[#8B6F4E]' : 'border-stone-100'
          ]
        }, [
          h('div', { class: 'flex items-center space-x-3' }, [
            h('div', {
              class: [
                'w-10 h-10 rounded-full flex items-center justify-center',
                props.node.gender === 'male' ? 'bg-blue-100' : 'bg-pink-100'
              ]
            }, [
              h(Icon, {
                icon: 'solar:user-bold',
                class: props.node.gender === 'male' ? 'text-blue-600 text-lg' : 'text-pink-600 text-lg'
              })
            ]),
            h('div', { class: 'flex-1' }, [
              h('h4', { class: 'font-bold text-[#5C4A3A] flex items-center space-x-1 text-sm' }, [
                h('span', props.node.name),
                props.node.status === 'deceased' ? h('span', { class: 'text-xs text-gray-400' }, '（已故）') : null
              ]),
              h('p', { class: 'text-xs text-gray-500' }, [
                props.node.birthYear || '未知',
                props.node.deathYear ? ` - ${props.node.deathYear}` : ''
              ]),
              props.node.spouse ? h('p', { class: 'text-xs text-gray-500' }, `配偶：${props.node.spouse}`) : null
            ])
          ]),
          hasChildren.value ? h('div', {
            class: 'flex items-center justify-center mt-2 pt-2 border-t border-stone-100'
          }, [
            h('button', {
              onClick: toggleCollapse,
              class: 'px-2 py-1 text-xs text-gray-500 hover:bg-gray-100 rounded-lg transition-colors flex items-center space-x-1'
            }, [
              h(Icon, {
                icon: isCollapsed.value ? 'solar:add-circle-bold' : 'solar:minus-circle-bold',
                class: 'text-[#8B6F4E]'
              }),
              h('span', isCollapsed.value ? `展开 ${props.node.children.length} 个子节点` : `折叠 ${props.node.children.length} 个子节点`)
            ])
          ]) : null
        ])
      ]),
      
      hasChildren.value && !isCollapsed.value ? h('div', { class: 'relative' }, [
        h('div', { class: 'w-px h-6 bg-[#8B6F4E]/30 mx-auto' }),
        
        h('div', { class: 'flex items-start justify-center gap-4' }, [
          ...props.node.children.map((child, index) => h('div', { 
            key: child.id,
            class: 'flex flex-col items-center relative'
          }, [
            h('div', { class: 'w-6 h-px bg-[#8B6F4E]/30' }),
            h(TreeNode, {
              node: child,
              level: props.level + 1,
              collapsedBranches: props.collapsedBranches,
              selectedMember: props.selectedMember,
              onSelect: (m: FamilyMember) => emit('select', m),
              onContextMenu: (m: FamilyMember, e: MouseEvent) => emit('context-menu', m, e),
              onToggleCollapse: (id: string) => emit('toggle-collapse', id)
            })
          ]))
        ])
      ]) : null
    ])
  }
})
</script>
