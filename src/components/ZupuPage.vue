<template>
  <div class="min-h-screen paper-texture">

    <div v-if="showFamilySidebar && hasFamily && userFamilies.length > 0" 
      class="fixed left-0 top-0 h-full w-72 bg-white shadow-2xl z-50 overflow-y-auto"
      style="margin-top: 80px;">
      <div class="p-4 border-b border-[#E8D5C4]">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-bold text-[#5C4A3A]">我的族谱</h3>
          <button @click="showFamilySidebar = false" class="text-gray-400 hover:text-gray-600">
            <Icon icon="solar:close-linear" class="text-lg" />
          </button>
        </div>
        
        <div class="flex gap-2">
          <button 
            v-if="!hasOwnedFamily"
            @click="showCreateFamilyModal = true; showFamilySidebar = false"
            class="flex-1 px-3 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-lg text-sm font-medium hover:shadow-lg transition-all flex items-center justify-center space-x-1"
          >
            <Icon icon="solar:add-circle-bold" class="text-sm" />
            <span>创建族谱</span>
          </button>
          <button 
            @click="showJoinFamilyModal = true; showFamilySidebar = false"
            class="flex-1 px-3 py-2 bg-white border border-[#E8D5C4] text-[#8B6F4E] rounded-lg text-sm font-medium hover:bg-[#FAF7F2] transition-all flex items-center justify-center space-x-1"
          >
            <Icon icon="solar:link-bold" class="text-sm" />
            <span>加入族谱</span>
          </button>
        </div>
      </div>
      
      <div class="p-3">
        <template v-if="ownedFamily">
          <div class="mb-3">
            <p class="text-xs text-gray-400 mb-2 px-2">我创建的</p>
            <button 
              @click="switchFamily(ownedFamily.family.id)"
              class="w-full p-3 rounded-xl transition-all flex items-center space-x-3"
              :class="[
                currentFamilyId === ownedFamily.family.id 
                  ? 'bg-gradient-to-r from-[#8B6F4E]/10 to-[#A67B5B]/10 border-2 border-[#8B6F4E]' 
                  : 'bg-[#FAF7F2] hover:bg-[#E8D5C4]/50 border-2 border-transparent'
              ]"
            >
              <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-[#C84A3E] to-[#E86B5F] flex items-center justify-center shadow-md flex-shrink-0">
                <span class="text-white font-bold text-sm">{{ ownedFamily.family.surname }}</span>
              </div>
              <div class="flex-1 min-w-0 text-left">
                <p class="text-sm font-semibold text-[#5C4A3A] truncate">
                  {{ ownedFamily.family.surname }}氏
                </p>
                <p v-if="ownedFamily.family.hallName" class="text-xs text-gray-400 truncate">
                  {{ ownedFamily.family.hallName }}
                </p>
                <div class="flex items-center space-x-2 mt-1">
                  <span class="px-1.5 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700">
                    族长
                  </span>
                  <span class="text-xs text-gray-400">
                    {{ ownedFamily.memberCount }} 人
                  </span>
                </div>
              </div>
              <Icon 
                v-if="currentFamilyId === ownedFamily.family.id" 
                icon="solar:check-circle-bold" 
                class="text-[#8B6F4E] flex-shrink-0" 
              />
            </button>
          </div>
        </template>
        
        <div v-if="userFamilies.filter(f => !f.isHead).length > 0">
          <p class="text-xs text-gray-400 mb-2 px-2">我参与的</p>
          <div class="space-y-2">
            <button 
              v-for="familyItem in userFamilies.filter(f => !f.isHead)" 
              :key="familyItem.family.id"
              @click="switchFamily(familyItem.family.id)"
              class="w-full p-3 rounded-xl transition-all flex items-center space-x-3"
              :class="[
                currentFamilyId === familyItem.family.id 
                  ? 'bg-gradient-to-r from-[#8B6F4E]/10 to-[#A67B5B]/10 border-2 border-[#8B6F4E]' 
                  : 'bg-[#FAF7F2] hover:bg-[#E8D5C4]/50 border-2 border-transparent'
              ]"
            >
              <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-[#8B6F4E] to-[#A67B5B] flex items-center justify-center shadow-md flex-shrink-0">
                <span class="text-white font-bold text-sm">{{ familyItem.family.surname }}</span>
              </div>
              <div class="flex-1 min-w-0 text-left">
                <p class="text-sm font-semibold text-[#5C4A3A] truncate">
                  {{ familyItem.family.surname }}氏
                </p>
                <p v-if="familyItem.family.hallName" class="text-xs text-gray-400 truncate">
                  {{ familyItem.family.hallName }}
                </p>
                <div class="flex items-center space-x-2 mt-1">
                  <span class="px-1.5 py-0.5 rounded text-xs font-medium" :class="roleClass(familyItem.role)">
                    {{ roleLabel(familyItem.role) }}
                  </span>
                  <span class="text-xs text-gray-400">
                    {{ familyItem.memberCount }} 人
                  </span>
                </div>
              </div>
              <Icon 
                v-if="currentFamilyId === familyItem.family.id" 
                icon="solar:check-circle-bold" 
                class="text-[#8B6F4E] flex-shrink-0" 
              />
            </button>
          </div>
        </div>
        
        <div v-if="!hasOwnedFamily && userFamilies.filter(f => !f.isHead).length === 0" class="text-center py-8">
          <Icon icon="solar:folder-opened-bold" class="text-4xl text-gray-300 mx-auto mb-2" />
          <p class="text-sm text-gray-400">暂无其他族谱</p>
        </div>
      </div>
    </div>

    <div v-if="showFamilySidebar" 
      @click="showFamilySidebar = false"
      class="fixed inset-0 bg-black/30 z-40 lg:hidden">
    </div>

    <main class="max-w-7xl mx-auto px-6 py-6">
      <template v-if="isLoading || hasFamily === null">
        <div class="flex flex-col items-center justify-center py-20">
          <Icon icon="solar:refresh-circle-bold" class="text-5xl text-[#8B6F4E] animate-spin mb-4" />
          <p class="text-gray-500">加载中...</p>
        </div>
      </template>

      <template v-else-if="!hasFamily">
        <div class="flex flex-col items-center justify-center py-16">
          <div class="w-32 h-32 bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] rounded-full flex items-center justify-center mb-8 shadow-lg">
            <Icon icon="solar:tree-bold-duotone" class="text-6xl text-[#8B6F4E]" />
          </div>
          <h2 class="text-3xl font-bold text-[#5C4A3A] font-serif mb-4">开始您的家族传承</h2>
          <p class="text-gray-500 mb-10 text-center max-w-lg text-lg">
            创建您的家族族谱，记录家族历史，传承家风家训。<br />
            或通过族长分享的链接加入已有的家族族谱。
          </p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl w-full">
            <div 
              @click="showCreateFamilyModal = true"
              class="bg-white rounded-2xl shadow-soft border border-stone-100 p-8 cursor-pointer hover:shadow-lg transition-all hover:border-[#E8D5C4] group"
            >
              <div class="w-16 h-16 bg-gradient-to-br from-[#8B6F4E] to-[#A67B5B] rounded-xl flex items-center justify-center mb-6 shadow-md group-hover:scale-110 transition-transform">
                <Icon icon="solar:add-circle-bold" class="text-3xl text-white" />
              </div>
              <h3 class="text-xl font-bold text-[#5C4A3A] font-serif mb-2">创建新族谱</h3>
              <p class="text-sm text-gray-500 mb-4">
                作为族长创建您的家族族谱，设定姓氏、堂号、始祖等信息。
              </p>
              <div class="flex items-center text-[#8B6F4E] font-medium text-sm">
                <span>开始创建</span>
                <Icon icon="solar:arrow-right-linear" class="ml-1 group-hover:translate-x-1 transition-transform" />
              </div>
              <div class="mt-4 pt-4 border-t border-stone-100">
                <p class="text-xs text-gray-400">
                  <Icon icon="solar:info-circle-linear" class="inline mr-1" />
                  每位用户只能创建一个族谱
                </p>
              </div>
            </div>
            
            <div 
              @click="showJoinFamilyModal = true"
              class="bg-white rounded-2xl shadow-soft border border-stone-100 p-8 cursor-pointer hover:shadow-lg transition-all hover:border-[#E8D5C4] group"
            >
              <div class="w-16 h-16 bg-gradient-to-br from-[#D4A574] to-[#8B6F4E] rounded-xl flex items-center justify-center mb-6 shadow-md group-hover:scale-110 transition-transform">
                <Icon icon="solar:link-bold" class="text-3xl text-white" />
              </div>
              <h3 class="text-xl font-bold text-[#5C4A3A] font-serif mb-2">加入已有族谱</h3>
              <p class="text-sm text-gray-500 mb-4">
                通过族长分享的链接代码，加入已有的家族族谱作为共建者。
              </p>
              <div class="flex items-center text-[#8B6F4E] font-medium text-sm">
                <span>输入链接代码</span>
                <Icon icon="solar:arrow-right-linear" class="ml-1 group-hover:translate-x-1 transition-transform" />
              </div>
              <div class="mt-4 pt-4 border-t border-stone-100">
                <p class="text-xs text-gray-400">
                  <Icon icon="solar:info-circle-linear" class="inline mr-1" />
                  可同时参与多个族谱的共建
                </p>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template v-else>
      <section class="bg-white rounded-2xl shadow-soft border border-stone-100 p-6 mb-6">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
          <div class="flex flex-wrap items-center gap-3">
            <button v-if="hasFamily && userFamilies.length > 0" 
              @click="showFamilySidebar = !showFamilySidebar"
              class="flex items-center space-x-2 px-4 py-2 bg-white/80 rounded-lg border border-[#E8D5C4] hover:bg-[#FAF7F2] transition-all">
              <Icon icon="solar:tree-bold-duotone" class="text-[#8B6F4E]" />
              <span class="text-sm font-medium text-[#5C4A3A] max-w-[150px] truncate">
                {{ currentFamily?.family.surname || familyInfo.surname }}氏
                <span v-if="currentFamily?.family.hallName" class="text-gray-400">· {{ currentFamily.family.hallName }}</span>
              </span>
              <Icon icon="solar:alt-arrow-down-linear" class="text-gray-400 text-sm transition-transform" :class="{ 'rotate-180': showFamilySidebar }" />
              <span v-if="userFamilies.length > 1" class="px-1.5 py-0.5 bg-[#E8D5C4] text-[#8B6F4E] text-xs rounded-full font-medium">
                {{ userFamilies.length }}
              </span>
            </button>
            
            <div v-if="(canManageMembers || canViewApprovals || canViewLogs)" class="relative">
              <button 
                @click="toggleManageMenu"
                class="flex items-center space-x-2 px-4 py-2 rounded-lg border border-[#E8D5C4] hover:bg-[#E8D5C4]/50 transition-all">
                <Icon icon="solar:settings-bold" class="text-[#8B6F4E]" />
                <span class="font-medium text-sm text-gray-600">管理功能</span>
                <Icon icon="solar:alt-arrow-down-linear" class="text-gray-400 text-sm transition-transform" :class="{ 'rotate-180': showManageMenu }" />
                <span v-if="pendingApprovalsCount > 0" class="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-[#C84A3E] text-white text-xs flex items-center justify-center">
                  {{ pendingApprovalsCount }}
                </span>
              </button>
              
              <div v-if="showManageMenu" 
                class="absolute left-0 top-full mt-2 w-48 bg-white rounded-xl shadow-lg border border-[#E8D5C4] py-2 z-50">
                <button
                  @click="navigateToMemberManagement"
                  v-if="canManageMembers"
                  class="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-[#FAF7F2] flex items-center space-x-3 transition-colors">
                  <Icon icon="solar:users-group-two-bold" class="text-[#8B6F4E]" />
                  <span>成员管理</span>
                </button>
                <button
                  @click="navigateToApprovals"
                  v-if="canViewApprovals"
                  class="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-[#FAF7F2] flex items-center space-x-3 transition-colors">
                  <Icon icon="solar:document-bold" class="text-[#8B6F4E]" />
                  <span>审核中心</span>
                  <span v-if="pendingApprovalsCount > 0" class="ml-auto w-5 h-5 rounded-full bg-[#C84A3E] text-white text-xs flex items-center justify-center">
                    {{ pendingApprovalsCount }}
                  </span>
                </button>
                <button
                  @click="navigateToLogs"
                  v-if="canViewLogs"
                  class="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-[#FAF7F2] flex items-center space-x-3 transition-colors">
                  <Icon icon="solar:history-bold" class="text-[#8B6F4E]" />
                  <span>操作日志</span>
                </button>
              </div>
            </div>
          </div>
          
          <div class="flex items-center gap-3">
            <button 
              v-if="isHead && hasFamily" 
              @click="showCollaborationModal = true; loadCollaborationLinks()"
              class="px-4 py-2 bg-gradient-to-r from-[#C84A3E] to-[#E86B5F] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all flex items-center space-x-2"
            >
              <Icon icon="solar:share-bold" class="text-sm" />
              <span>邀请共建</span>
            </button>
            <button @click="showFamilySettings = true" class="px-4 py-2 bg-white border border-[#E8D5C4] text-[#8B6F4E] rounded-xl text-sm font-medium hover:bg-[#FAF7F2] transition-colors flex items-center space-x-2">
              <Icon icon="solar:settings-bold" class="text-lg" />
              <span>设置</span>
            </button>
          </div>
        </div>
        
        <div class="flex items-center justify-between mb-4 pt-4 border-t border-stone-100">
          <h2 class="text-lg font-bold text-[#5C4A3A] font-serif flex items-center space-x-2">
            <Icon icon="solar:home-2-bold" class="text-[#8B6F4E]" />
            <span>家族信息</span>
          </h2>
          <template v-if="myRole">
            <span class="px-2 py-0.5 rounded text-xs font-medium" :class="roleClass(myRole)">
              您的角色: {{ roleLabel(myRole) }}
            </span>
          </template>
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
            <button v-if="canEdit" @click="showMemberModal = true" class="px-3 py-1 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-lg text-sm font-medium shadow-warm hover:shadow-lg transition-all flex items-center space-x-1">
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
                  <template v-if="canEdit">
                    <button @click.stop="editMember(member)" class="text-[#8B6F4E] text-sm hover:text-[#D4A574] transition-colors mr-3">
                      编辑
                    </button>
                  </template>
                  <template v-if="canDelete">
                    <button @click.stop="deleteMember(member)" class="text-red-500 text-sm hover:text-red-600 transition-colors">
                      删除
                    </button>
                  </template>
                  <template v-else-if="!canEdit">
                    <span class="text-gray-400 text-xs">只读</span>
                  </template>
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
        <div class="grid grid-cols-2 gap-4">
          <button @click="showImportModal = true" class="p-4 bg-[#FAF7F2] rounded-xl hover:bg-[#E8D5C4]/50 transition-colors text-center group">
            <Icon icon="solar:import-bold" class="text-2xl text-[#8B6F4E] mx-auto mb-2 group-hover:scale-110 transition-transform" />
            <p class="text-sm font-medium text-[#5C4A3A]">导入数据</p>
            <p class="text-xs text-gray-500 mt-1">Excel/CSV</p>
          </button>
          <button @click="showExportModal = true" class="p-4 bg-[#FAF7F2] rounded-xl hover:bg-[#E8D5C4]/50 transition-colors text-center group">
            <Icon icon="solar:export-bold" class="text-2xl text-[#8B6F4E] mx-auto mb-2 group-hover:scale-110 transition-transform" />
            <p class="text-sm font-medium text-[#5C4A3A]">导出数据</p>
            <p class="text-xs text-gray-500 mt-1">Excel/CSV</p>
          </button>
        </div>
      </section>

      <section class="mb-8 px-6" v-if="hasFamily">
        <div class="max-w-7xl mx-auto">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-xl font-bold text-[#5C4A3A] font-serif">家族记忆管理</h3>
            <button 
              class="flex items-center space-x-2 px-5 py-2.5 bg-[#8B6F4E] text-white rounded-xl hover:bg-[#6B5342] transition-colors shadow-soft"
              @click="showFamilyMemoryModal = true">
              <Icon icon="solar:add-circle-bold" class="text-lg" />
              <span class="font-medium">添加记忆</span>
            </button>
          </div>

          <div class="relative pl-8">
            <div class="absolute left-[11px] top-2 bottom-2 w-px bg-[#E8D5C4]"></div>
            
            <div v-if="familyMemories.length === 0" class="text-center py-12 text-gray-500">
              <Icon icon="solar:bookmark-bold" class="text-4xl mb-3 mx-auto text-[#E8D5C4]" />
              <p>暂无家族记忆，点击上方按钮添加</p>
            </div>

            <div v-else class="space-y-6">
              <div v-for="memory in familyMemories" :key="memory.id" class="relative">
                <div class="absolute left-[-29px] top-2 w-4 h-4 rounded-full border-2 border-white shadow-sm z-10"
                     :class="getMemoryTypeColor(memory.type)"></div>
                
                <div class="bg-white rounded-xl shadow-soft border border-stone-100 hover-lift cursor-pointer"
                     @click="openFamilyMemoryDetail(memory)">
                  <div class="p-4">
                    <div class="flex items-start justify-between mb-2">
                      <div class="flex-1">
                        <div class="flex items-center space-x-2 mb-1">
                          <span class="px-2 py-0.5 rounded-full text-xs font-medium"
                                :class="getMemoryTypeBadge(memory.type)">
                            {{ getMemoryTypeLabel(memory.type) }}
                          </span>
                          <span v-if="memory.eventDate" class="text-xs text-gray-400">
                            {{ formatEventDate(memory.eventDate) }}
                          </span>
                        </div>
                        <h4 class="font-bold text-[#5C4A3A] mb-1">{{ memory.title }}</h4>
                        <p v-if="memory.description" class="text-sm text-gray-500 line-clamp-2 mb-2">
                          {{ memory.description }}
                        </p>
                        <div class="flex items-center space-x-3 text-xs text-gray-400">
                          <span v-if="memory.location" class="flex items-center">
                            <Icon icon="solar:point-on-map-linear" class="mr-1 w-3 h-3" />
                            {{ memory.location }}
                          </span>
                        </div>
                      </div>
                      
                      <div class="flex items-center space-x-1 ml-4">
                        <button 
                          class="p-2 text-gray-400 hover:text-[#8B6F4E] hover:bg-[#E8D5C4]/30 rounded-lg transition-colors"
                          @click.stop="editFamilyMemory(memory)">
                          <Icon icon="solar:pen-bold" class="w-4 h-4" />
                        </button>
                        <button 
                          class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                          @click.stop="confirmDeleteFamilyMemory(memory)">
                          <Icon icon="solar:trash-bin-trash-bold" class="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    
                    <div v-if="memory.mediaUrl" class="mt-3">
                      <img 
                        :src="getFullMediaUrl(memory.mediaUrl)" 
                        :alt="memory.title"
                        class="w-full max-h-64 object-contain rounded-lg bg-gray-50" />
                    </div>
                    
                    <div v-if="memory.tags && memory.tags.length > 0" class="mt-3 flex flex-wrap gap-1">
                      <span 
                        v-for="tag in memory.tags" 
                        :key="tag"
                        class="px-2 py-0.5 bg-[#E8D5C4]/30 text-[#8B6F4E] rounded-full text-xs">
                        {{ tag }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      </template>
    </main>

    <div v-if="showFamilyMemoryModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/60" @click="closeFamilyMemoryModal"></div>
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b border-[#E8D5C4] flex items-center justify-between">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">
            {{ editingFamilyMemory ? '编辑家族记忆' : '添加家族记忆' }}
          </h3>
          <button 
            class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
            @click="closeFamilyMemoryModal">
            <Icon icon="solar:close-circle-bold" class="text-xl" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">记忆标题 *</label>
            <input 
              type="text" 
              v-model="newFamilyMemory.title"
              class="w-full px-4 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent"
              placeholder="输入记忆标题">
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">记忆类型</label>
            <div class="grid grid-cols-3 gap-3">
              <button 
                v-for="type in ['text', 'image', 'video']" 
                :key="type"
                class="p-3 border-2 rounded-xl transition-all"
                :class="newFamilyMemory.type === type ? 'border-[#8B6F4E] bg-[#E8D5C4]/30' : 'border-[#E8D5C4] hover:border-[#D4A574]'"
                @click="newFamilyMemory.type = type">
                <Icon :icon="getMemoryTypeIcon(type)" class="text-xl mx-auto mb-1" :class="newFamilyMemory.type === type ? 'text-[#8B6F4E]' : 'text-gray-400'" />
                <p class="text-sm font-medium" :class="newFamilyMemory.type === type ? 'text-[#8B6F4E]' : 'text-gray-600'">
                  {{ getMemoryTypeLabel(type) }}
                </p>
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">事件日期</label>
            <input 
              type="date" 
              v-model="newFamilyMemory.eventDate"
              class="w-full px-4 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent">
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">发生地点</label>
            <div class="relative">
              <Icon icon="solar:point-on-map-linear" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input 
                type="text" 
                v-model="newFamilyMemory.location"
                class="w-full pl-10 pr-4 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent"
                placeholder="例如：北京市海淀区老宅">
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">详细描述</label>
            <textarea 
              v-model="newFamilyMemory.description"
              rows="4"
              class="w-full px-4 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent resize-none"
              placeholder="详细描述这个家族记忆..."></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">上传照片/视频</label>
            <div class="border-2 border-dashed border-[#E8D5C4] rounded-xl p-8 text-center hover:border-[#D4A574] transition-colors cursor-pointer"
                 @click="triggerFamilyMemoryMediaUpload">
              <Icon icon="solar:upload-minimalistic-bold" class="text-4xl text-gray-300 mx-auto mb-3" />
              <p class="text-sm text-gray-500">点击或拖拽上传照片/视频</p>
              <p class="text-xs text-gray-400 mt-1">支持 JPG、PNG、MP4 格式</p>
            </div>
            <input 
              type="file" 
              ref="familyMemoryMediaInput"
              accept="image/*,video/*"
              class="hidden"
              @change="handleFamilyMemoryMediaUpload">
            
            <div v-if="newFamilyMemory.previewUrl" class="mt-3">
              <img 
                :src="newFamilyMemory.previewUrl" 
                alt="预览"
                class="w-full max-h-64 object-contain rounded-lg bg-gray-50" />
              <button 
                class="mt-2 text-sm text-red-500 hover:text-red-600"
                @click="removeFamilyMemoryMedia">
                移除媒体
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">标签（用逗号分隔）</label>
            <input 
              type="text" 
              v-model="newFamilyMemory.tagsStr"
              class="w-full px-4 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent"
              placeholder="例如：春节, 团圆, 老照片">
          </div>
        </div>

        <div class="p-6 border-t border-gray-100 flex items-center justify-end space-x-3">
          <button 
            class="px-5 py-2.5 text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
            @click="closeFamilyMemoryModal">
            取消
          </button>
          <button 
            class="px-5 py-2.5 bg-[#8B6F4E] text-white rounded-xl hover:bg-[#6B5342] transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            :disabled="!newFamilyMemory.title || isFamilyMemoryLoading"
            @click="saveFamilyMemory">
            {{ isFamilyMemoryLoading ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showFamilyMemoryDetailModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/60" @click="showFamilyMemoryDetailModal = false"></div>
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b border-[#E8D5C4] flex items-center justify-between">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">{{ selectedFamilyMemory?.title }}</h3>
          <button 
            class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
            @click="showFamilyMemoryDetailModal = false">
            <Icon icon="solar:close-circle-bold" class="text-xl" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6">
          <div class="flex items-center space-x-3 mb-4">
            <span class="px-3 py-1 rounded-full text-sm font-medium"
                  :class="getMemoryTypeBadge(selectedFamilyMemory?.type || 'text')">
              {{ getMemoryTypeLabel(selectedFamilyMemory?.type || 'text') }}
            </span>
            <span v-if="selectedFamilyMemory?.eventDate" class="text-sm text-gray-400">
              {{ formatEventDate(selectedFamilyMemory?.eventDate || '') }}
            </span>
            <span v-if="selectedFamilyMemory?.location" class="flex items-center text-sm text-gray-400">
              <Icon icon="solar:point-on-map-linear" class="mr-1 w-4 h-4" />
              {{ selectedFamilyMemory?.location }}
            </span>
          </div>

          <div v-if="selectedFamilyMemory?.mediaUrl" class="mb-6">
            <img 
              :src="getFullMediaUrl(selectedFamilyMemory?.mediaUrl || '')" 
              :alt="selectedFamilyMemory?.title"
              class="w-full max-h-96 object-contain rounded-xl bg-gray-50" />
          </div>

          <div v-if="selectedFamilyMemory?.description" class="mb-6">
            <h4 class="font-medium text-gray-700 mb-2">记忆描述</h4>
            <p class="text-gray-600 whitespace-pre-wrap">{{ selectedFamilyMemory?.description }}</p>
          </div>

          <div v-if="selectedFamilyMemory?.tags && selectedFamilyMemory?.tags.length > 0" class="mb-6">
            <h4 class="font-medium text-gray-700 mb-2">标签</h4>
            <div class="flex flex-wrap gap-2">
              <span 
                v-for="tag in selectedFamilyMemory?.tags" 
                :key="tag"
                class="px-3 py-1 bg-[#E8D5C4]/30 text-[#8B6F4E] rounded-full text-sm">
                {{ tag }}
              </span>
            </div>
          </div>

          <div class="text-xs text-gray-400 pt-4 border-t border-gray-100">
            创建时间：{{ selectedFamilyMemory?.createdAt ? new Date(selectedFamilyMemory.createdAt).toLocaleString('zh-CN') : '' }}
          </div>
        </div>
      </div>
    </div>

    <div v-if="showDeleteFamilyMemoryConfirm" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" @click="showDeleteFamilyMemoryConfirm = false"></div>
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
        <div class="text-center">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-red-50 flex items-center justify-center">
            <Icon icon="solar:trash-bin-trash-bold" class="text-red-500 text-3xl" />
          </div>
          <h3 class="text-lg font-bold text-gray-800 mb-2">确认删除</h3>
          <p class="text-sm text-gray-500 mb-6">
            确定要删除记忆「<span class="font-medium">{{ deletingFamilyMemory?.title }}</span>」吗？<br>此操作不可撤销。
          </p>
        </div>
        <div class="flex items-center justify-center space-x-3">
          <button 
            class="px-5 py-2.5 text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
            @click="showDeleteFamilyMemoryConfirm = false">
            取消
          </button>
          <button 
            class="px-5 py-2.5 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors"
            @click="deleteFamilyMemory">
            确认删除
          </button>
        </div>
      </div>
    </div>

    <div v-if="showCreateFamilyModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="bg-white rounded-2xl shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-stone-100">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-bold text-[#5C4A3A] flex items-center space-x-2">
              <Icon icon="solar:add-circle-bold" class="text-[#8B6F4E]" />
              <span>新建族谱</span>
            </h3>
            <button @click="showCreateFamilyModal = false" class="text-gray-400 hover:text-gray-600">
              <Icon icon="solar:close-circle-bold" class="text-2xl" />
            </button>
          </div>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">姓氏 <span class="text-red-500">*</span></label>
            <input v-model="createFamilyForm.surname" type="text" placeholder="例如：李" 
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">堂号</label>
            <input v-model="createFamilyForm.hallName" type="text" placeholder="例如：陇西堂" 
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">始祖</label>
            <input v-model="createFamilyForm.ancestor" type="text" placeholder="例如：李太白" 
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">家族简介</label>
            <textarea v-model="createFamilyForm.description" placeholder="请输入家族简介..." rows="3"
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4] resize-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">字辈排行</label>
            <input v-model="createFamilyForm.ziBeiStr" type="text" placeholder="用逗号分隔，例如：元,亨,利,贞" 
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
            <p class="text-xs text-gray-500 mt-1">多个字辈用逗号或空格分隔</p>
          </div>
        </div>
        <div class="p-6 border-t border-stone-100 flex justify-end space-x-3">
          <button @click="showCreateFamilyModal = false" 
            class="px-4 py-2 text-gray-600 bg-stone-100 rounded-xl text-sm font-medium hover:bg-stone-200 transition-colors">
            取消
          </button>
          <button @click="handleCreateFamily" :disabled="isCreatingFamily"
            class="px-4 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2">
            <Icon v-if="isCreatingFamily" icon="solar:refresh-circle-bold" class="text-sm animate-spin" />
            <span>{{ isCreatingFamily ? '创建中...' : '创建族谱' }}</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="showJoinFamilyModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="bg-white rounded-2xl shadow-xl max-w-md w-full mx-4">
        <div class="p-6 border-b border-stone-100">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-bold text-[#5C4A3A] flex items-center space-x-2">
              <Icon icon="solar:link-bold" class="text-[#8B6F4E]" />
              <span>导入已有族谱</span>
            </h3>
            <button @click="showJoinFamilyModal = false" class="text-gray-400 hover:text-gray-600">
              <Icon icon="solar:close-circle-bold" class="text-2xl" />
            </button>
          </div>
        </div>
        <div class="p-6">
          <p class="text-sm text-gray-500 mb-4">
            请输入族长分享的链接代码，加入已有的家族族谱。
          </p>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">链接代码 <span class="text-red-500">*</span></label>
            <input v-model="joinLinkCode" type="text" placeholder="例如：ABC123XYZ789" 
              class="w-full px-4 py-3 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4] text-center font-mono text-lg tracking-wider" />
          </div>
        </div>
        <div class="p-6 border-t border-stone-100 flex justify-end space-x-3">
          <button @click="showJoinFamilyModal = false" 
            class="px-4 py-2 text-gray-600 bg-stone-100 rounded-xl text-sm font-medium hover:bg-stone-200 transition-colors">
            取消
          </button>
          <button @click="handleJoinFamily" :disabled="isJoiningFamily"
            class="px-4 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2">
            <Icon v-if="isJoiningFamily" icon="solar:refresh-circle-bold" class="text-sm animate-spin" />
            <span>{{ isJoiningFamily ? '加入中...' : '加入族谱' }}</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="showCollaborationModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="bg-white rounded-2xl shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-stone-100">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-bold text-[#5C4A3A] flex items-center space-x-2">
              <Icon icon="solar:share-bold" class="text-[#8B6F4E]" />
              <span>邀请共建</span>
            </h3>
            <button @click="showCollaborationModal = false" class="text-gray-400 hover:text-gray-600">
              <Icon icon="solar:close-circle-bold" class="text-2xl" />
            </button>
          </div>
        </div>
        <div class="p-6">
          <div class="bg-[#FAF7F2] rounded-xl p-4 mb-6">
            <h4 class="text-sm font-bold text-[#5C4A3A] mb-3">创建新的分享链接</h4>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <label class="block text-xs text-gray-500 mb-1">权限设置</label>
                <select v-model="newLinkForm.role" 
                  class="w-full px-3 py-2 bg-white border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
                  <option value="viewer">仅浏览</option>
                  <option value="editor">可编辑</option>
                  <option value="admin">管理员</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">使用次数</label>
                <input v-model.number="newLinkForm.maxUses" type="number" min="1" max="100"
                  class="w-full px-3 py-2 bg-white border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">有效天数</label>
                <select v-model.number="newLinkForm.expiresInDays"
                  class="w-full px-3 py-2 bg-white border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
                  <option :value="7">7天</option>
                  <option :value="30">30天</option>
                  <option :value="90">90天</option>
                  <option :value="0">永久有效</option>
                </select>
              </div>
            </div>
            <button @click="handleCreateLink" :disabled="isCreatingLink"
              class="px-4 py-2 bg-gradient-to-r from-[#C84A3E] to-[#E86B5F] text-white rounded-lg text-sm font-medium hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2">
              <Icon v-if="isCreatingLink" icon="solar:refresh-circle-bold" class="text-sm animate-spin" />
              <span>{{ isCreatingLink ? '创建中...' : '生成链接' }}</span>
            </button>
          </div>

          <div>
            <h4 class="text-sm font-bold text-[#5C4A3A] mb-3">已有链接</h4>
            <div v-if="loadingCollaborationLinks" class="text-center py-8 text-gray-400">
              <Icon icon="solar:refresh-circle-bold" class="text-3xl animate-spin mx-auto mb-2" />
              <p class="text-sm">加载中...</p>
            </div>
            <div v-else-if="collaborationLinks.length === 0" class="text-center py-8 text-gray-400">
              <Icon icon="solar:link-bold" class="text-3xl mx-auto mb-2" />
              <p class="text-sm">暂无分享链接</p>
            </div>
            <div v-else class="space-y-3">
              <div v-for="link in collaborationLinks" :key="link.id" 
                class="bg-white border border-stone-200 rounded-xl p-4 hover:shadow-md transition-shadow">
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="flex items-center space-x-2 mb-2">
                      <span class="px-2 py-0.5 rounded text-xs font-medium" :class="linkStatusClass(link.status)">
                        {{ linkStatusLabel(link.status) }}
                      </span>
                      <span class="px-2 py-0.5 rounded text-xs font-medium" :class="roleClass(link.role)">
                        {{ roleLabel(link.role) }}
                      </span>
                      <span v-if="!link.isVisible" class="px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-500">
                        已隐藏
                      </span>
                    </div>
                    <div class="font-mono text-sm text-[#5C4A3A] mb-1">
                      {{ link.linkCode }}
                    </div>
                    <div class="text-xs text-gray-400 space-x-3">
                      <span>已使用: {{ link.usedCount }}/{{ link.maxUses }}</span>
                      <span v-if="link.expiresAt">过期时间: {{ new Date(link.expiresAt).toLocaleDateString() }}</span>
                      <span>创建时间: {{ new Date(link.createdAt).toLocaleDateString() }}</span>
                    </div>
                  </div>
                  <div class="flex items-center space-x-2 ml-4">
                    <button v-if="link.status === 'active'" 
                      @click="handleCopyLink(link.linkCode)"
                      class="p-2 text-gray-500 hover:text-[#8B6F4E] hover:bg-[#E8D5C4]/30 rounded-lg transition-colors"
                      :title="copyingLinkId === link.linkCode ? '已复制' : '复制链接'">
                      <Icon :icon="copyingLinkId === link.linkCode ? 'solar:check-circle-bold' : 'solar:copy-bold'" class="text-lg" />
                    </button>
                    <div class="relative group">
                      <button class="p-2 text-gray-500 hover:text-[#8B6F4E] hover:bg-[#E8D5C4]/30 rounded-lg transition-colors"
                        title="设置权限">
                        <Icon icon="solar:key-bold" class="text-lg" />
                      </button>
                      <div class="absolute right-0 top-full mt-1 bg-white rounded-lg shadow-lg border border-stone-200 py-1 min-w-[120px] opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                        <button @click="handleUpdateLinkRole(link.id, 'viewer')"
                          :class="link.role === 'viewer' ? 'bg-[#E8D5C4]' : ''"
                          class="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-[#FAF7F2]">
                          仅浏览
                        </button>
                        <button @click="handleUpdateLinkRole(link.id, 'editor')"
                          :class="link.role === 'editor' ? 'bg-[#E8D5C4]' : ''"
                          class="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-[#FAF7F2]">
                          可编辑
                        </button>
                        <button @click="handleUpdateLinkRole(link.id, 'admin')"
                          :class="link.role === 'admin' ? 'bg-[#E8D5C4]' : ''"
                          class="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-[#FAF7F2]">
                          管理员
                        </button>
                      </div>
                    </div>
                    <button v-if="link.status === 'active'"
                      @click="handleToggleLinkVisibility(link.id, !link.isVisible)"
                      class="p-2 text-gray-500 hover:text-[#8B6F4E] hover:bg-[#E8D5C4]/30 rounded-lg transition-colors"
                      :title="link.isVisible ? '隐藏链接' : '显示链接'">
                      <Icon :icon="link.isVisible ? 'solar:eye-bold' : 'solar:eye-closed-bold'" class="text-lg" />
                    </button>
                    <button v-if="link.status === 'active'"
                      @click="handleResetLink(link.id)"
                      class="p-2 text-gray-500 hover:text-[#C84A3E] hover:bg-red-50 rounded-lg transition-colors"
                      title="重置链接（生成新代码）">
                      <Icon icon="solar:refresh-bold" class="text-lg" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="p-6 border-t border-stone-100 flex justify-end">
          <button @click="showCollaborationModal = false" 
            class="px-4 py-2 text-gray-600 bg-stone-100 rounded-xl text-sm font-medium hover:bg-stone-200 transition-colors">
            关闭
          </button>
        </div>
      </div>
    </div>

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

    <div v-if="showImportModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4" @click.self="showImportModal = false">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="bg-gradient-to-br from-[#8B6F4E] to-[#A67B5B] rounded-t-2xl p-6 text-white">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-bold font-serif">导入族谱数据</h3>
            <button @click="closeImportModal" class="w-8 h-8 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors">
              <Icon icon="material-symbols:close" class="text-white" />
            </button>
          </div>
        </div>
        <div class="p-6">
          <div class="mb-6">
            <p class="text-sm text-gray-600 mb-4">支持 Excel (.xlsx) 和 CSV 格式的文件导入。导入后数据将自动生成族谱树并保存到数据库。</p>
            <div class="border-2 border-dashed border-[#E8D5C4] rounded-xl p-8 text-center bg-[#FAF7F2] hover:bg-[#E8D5C4]/30 transition-colors cursor-pointer" @click="triggerFileInput">
              <input ref="fileInputRef" type="file" accept=".xlsx,.xls,.csv" class="hidden" @change="handleFileSelect" />
              <Icon icon="solar:upload-bold" class="text-4xl text-[#8B6F4E] mx-auto mb-3" />
              <p class="text-sm font-medium text-[#5C4A3A]">点击选择文件或拖拽文件到此处</p>
              <p class="text-xs text-gray-500 mt-1">支持 .xlsx, .xls, .csv 格式</p>
            </div>
            <div v-if="selectedFile" class="mt-4 p-4 bg-blue-50 rounded-xl">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-2">
                  <Icon icon="solar:file-text-bold" class="text-blue-600" />
                  <span class="text-sm font-medium text-blue-800">{{ selectedFile.name }}</span>
                </div>
                <button @click="clearSelectedFile" class="text-gray-400 hover:text-red-500">
                  <Icon icon="solar:close-circle-bold" class="text-lg" />
                </button>
              </div>
            </div>
          </div>
          
          <div v-if="importPreview.length > 0" class="mb-6">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-bold text-[#5C4A3A]">数据预览（前5条）</h4>
              <div class="flex items-center space-x-3 text-xs">
                <span class="px-2 py-1 bg-blue-100 text-blue-700 rounded">共 {{ importPreview.length }} 条</span>
                <span class="px-2 py-1 bg-green-100 text-green-700 rounded">新增 {{ importNewCount }} 条</span>
                <span v-if="importDuplicateCount > 0" class="px-2 py-1 bg-yellow-100 text-yellow-700 rounded">重复 {{ importDuplicateCount }} 条</span>
              </div>
            </div>
            
            <div v-if="importDuplicateCount > 0" class="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
              <div class="flex items-start space-x-2">
                <Icon icon="solar:warning-circle-bold" class="text-yellow-500 mt-0.5 flex-shrink-0" />
                <div>
                  <p class="text-sm font-medium text-yellow-800">检测到 {{ importDuplicateCount }} 条重复数据</p>
                  <p class="text-xs text-yellow-600 mt-1">以下成员已存在，导入时将自动跳过：</p>
                  <div class="flex flex-wrap gap-2 mt-2">
                    <span v-for="name in importDuplicateNames.slice(0, 5)" :key="name" class="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-xs">
                      {{ name }}
                    </span>
                    <span v-if="importDuplicateNames.length > 5" class="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-xs">
                      等{{ importDuplicateNames.length }}人
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="overflow-x-auto border border-stone-200 rounded-xl">
              <table class="w-full text-sm">
                <thead class="bg-[#FAF7F2]">
                  <tr>
                    <th class="px-3 py-2 text-left text-gray-600">姓名</th>
                    <th class="px-3 py-2 text-left text-gray-600">性别</th>
                    <th class="px-3 py-2 text-left text-gray-600">世代</th>
                    <th class="px-3 py-2 text-left text-gray-600">父亲</th>
                    <th class="px-3 py-2 text-left text-gray-600">状态</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in importPreview.slice(0, 5)" :key="index" class="border-t border-stone-100">
                    <td class="px-3 py-2">{{ item.name }}</td>
                    <td class="px-3 py-2">{{ item.gender === 'male' ? '男' : '女' }}</td>
                    <td class="px-3 py-2">{{ item.generation }}</td>
                    <td class="px-3 py-2">{{ item.fatherName || '-' }}</td>
                    <td class="px-3 py-2">{{ item.status === 'alive' ? '在世' : '已故' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <div v-if="importError" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
            <div class="flex items-center space-x-2">
              <Icon icon="solar:danger-circle-bold" class="text-red-500" />
              <p class="text-sm text-red-700">{{ importError }}</p>
            </div>
          </div>
          
          <div class="flex justify-end space-x-3">
            <button @click="closeImportModal" class="px-6 py-2 text-gray-600 bg-gray-100 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors">
              取消
            </button>
            <button @click="handleImport" :disabled="!selectedFile || importing" class="px-6 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2">
              <Icon v-if="importing" icon="solar:refresh-circle-bold" class="animate-spin" />
              <span>{{ importing ? '导入中...' : '确认导入' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showExportModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4" @click.self="showExportModal = false">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div class="bg-gradient-to-br from-[#8B6F4E] to-[#A67B5B] rounded-t-2xl p-6 text-white">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-bold font-serif">导出族谱数据</h3>
            <button @click="showExportModal = false" class="w-8 h-8 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors">
              <Icon icon="material-symbols:close" class="text-white" />
            </button>
          </div>
        </div>
        <div class="p-6">
          <p class="text-sm text-gray-600 mb-6">选择导出格式，将导出当前家族的所有成员数据。</p>
          
          <div class="space-y-3 mb-6">
            <label class="flex items-center p-4 border border-stone-200 rounded-xl cursor-pointer hover:bg-[#FAF7F2] transition-colors" :class="{ 'border-[#8B6F4E] bg-[#E8D5C4]/20': exportFormat === 'xlsx' }">
              <input type="radio" v-model="exportFormat" value="xlsx" class="hidden" />
              <div class="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center mr-4">
                <Icon icon="solar:file-sheet-bold" class="text-green-600 text-xl" />
              </div>
              <div>
                <p class="font-medium text-[#5C4A3A]">Excel 格式 (.xlsx)</p>
                <p class="text-xs text-gray-500">适合在 Excel 中编辑和查看</p>
              </div>
              <div v-if="exportFormat === 'xlsx'" class="ml-auto">
                <Icon icon="solar:check-circle-bold" class="text-[#8B6F4E]" />
              </div>
            </label>
            
            <label class="flex items-center p-4 border border-stone-200 rounded-xl cursor-pointer hover:bg-[#FAF7F2] transition-colors" :class="{ 'border-[#8B6F4E] bg-[#E8D5C4]/20': exportFormat === 'csv' }">
              <input type="radio" v-model="exportFormat" value="csv" class="hidden" />
              <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center mr-4">
                <Icon icon="solar:file-text-bold" class="text-blue-600 text-xl" />
              </div>
              <div>
                <p class="font-medium text-[#5C4A3A]">CSV 格式 (.csv)</p>
                <p class="text-xs text-gray-500">通用文本格式，兼容性好</p>
              </div>
              <div v-if="exportFormat === 'csv'" class="ml-auto">
                <Icon icon="solar:check-circle-bold" class="text-[#8B6F4E]" />
              </div>
            </label>
          </div>
          
          <div class="flex justify-end space-x-3">
            <button @click="showExportModal = false" class="px-6 py-2 text-gray-600 bg-gray-100 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors">
              取消
            </button>
            <button @click="handleExport" :disabled="exporting" class="px-6 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2">
              <Icon v-if="exporting" icon="solar:refresh-circle-bold" class="animate-spin" />
              <span>{{ exporting ? '导出中...' : '导出' }}</span>
            </button>
          </div>
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
import { ref, computed, reactive, defineComponent, h, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import D3Tree from './D3Tree.vue'
import { apiService, Family, FamilyMember, FamilyRole, CollaborationLink, UserFamilyListItem } from '../services/api'

const router = useRouter()

const isLoading = ref(false)

const showManageMenu = ref(false)

interface FamilyMemoryItem {
  id: string
  familyId: string
  title: string
  type: 'text' | 'image' | 'video'
  description?: string
  content?: string
  eventDate?: string
  location?: string
  mediaUrl?: string
  mediaType?: string
  tags?: string[]
  createdAt: string
  updatedAt: string
}

const familyMemories = ref<FamilyMemoryItem[]>([])
const showFamilyMemoryModal = ref(false)
const showFamilyMemoryDetailModal = ref(false)
const showDeleteFamilyMemoryConfirm = ref(false)
const editingFamilyMemory = ref<FamilyMemoryItem | null>(null)
const selectedFamilyMemory = ref<FamilyMemoryItem | null>(null)
const deletingFamilyMemory = ref<FamilyMemoryItem | null>(null)
const isFamilyMemoryLoading = ref(false)
const familyMemoryMediaInput = ref<HTMLInputElement | null>(null)

const newFamilyMemory = reactive({
  title: '',
  type: 'text' as 'text' | 'image' | 'video',
  description: '',
  eventDate: '',
  location: '',
  tagsStr: '',
  mediaFile: null as File | null,
  previewUrl: ''
})

const getMemoryTypeIcon = (type: string) => {
  const icons: Record<string, string> = {
    text: 'solar:note-book-bold',
    image: 'solar:gallery-wide-bold',
    video: 'solar:video-camera-bold'
  }
  return icons[type] || icons.text
}

const getMemoryTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    text: '文字记忆',
    image: '照片记忆',
    video: '视频记忆'
  }
  return labels[type] || '文字记忆'
}

const getMemoryTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    text: 'bg-[#8B6F4E]',
    image: 'bg-[#D4A574]',
    video: 'bg-emerald-500'
  }
  return colors[type] || colors.text
}

const getMemoryTypeBadge = (type: string) => {
  const badges: Record<string, string> = {
    text: 'bg-[#8B6F4E]/10 text-[#8B6F4E]',
    image: 'bg-[#D4A574]/10 text-[#D4A574]',
    video: 'bg-emerald-500/10 text-emerald-600'
  }
  return badges[type] || badges.text
}

const formatEventDate = (dateStr: string) => {
  if (!dateStr) return ''
  try {
    return new Date(dateStr).toLocaleDateString('zh-CN')
  } catch {
    return dateStr
  }
}

const getFullMediaUrl = (url: string) => {
  if (!url) return ''
  if (url.startsWith('http') || url.startsWith('data:')) {
    return url
  }
  return `http://localhost:8000${url}`
}

const loadFamilyMemories = async () => {
  if (!hasFamily.value) return
  isFamilyMemoryLoading.value = true
  try {
    const response = await apiService.getFamilyMemories()
    if (response.success && response.data) {
      familyMemories.value = response.data.memories.sort((a, b) => {
        const dateA = a.eventDate || a.createdAt
        const dateB = b.eventDate || b.createdAt
        return new Date(dateB).getTime() - new Date(dateA).getTime()
      })
    }
  } catch (error) {
    console.error('加载家族记忆失败:', error)
  } finally {
    isFamilyMemoryLoading.value = false
  }
}

const triggerFamilyMemoryMediaUpload = () => {
  if (familyMemoryMediaInput.value) {
    familyMemoryMediaInput.value.click()
  }
}

const handleFamilyMemoryMediaUpload = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return
  
  const file = input.files[0]
  newFamilyMemory.mediaFile = file
  
  const reader = new FileReader()
  reader.onload = (e) => {
    newFamilyMemory.previewUrl = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

const removeFamilyMemoryMedia = () => {
  newFamilyMemory.mediaFile = null
  newFamilyMemory.previewUrl = ''
  if (familyMemoryMediaInput.value) {
    familyMemoryMediaInput.value.value = ''
  }
}

const closeFamilyMemoryModal = () => {
  showFamilyMemoryModal.value = false
  editingFamilyMemory.value = null
  resetNewFamilyMemory()
}

const resetNewFamilyMemory = () => {
  newFamilyMemory.title = ''
  newFamilyMemory.type = 'text'
  newFamilyMemory.description = ''
  newFamilyMemory.eventDate = ''
  newFamilyMemory.location = ''
  newFamilyMemory.tagsStr = ''
  newFamilyMemory.mediaFile = null
  newFamilyMemory.previewUrl = ''
}

const saveFamilyMemory = async () => {
  if (!newFamilyMemory.title) return
  
  isFamilyMemoryLoading.value = true
  try {
    const tags = newFamilyMemory.tagsStr
      ? newFamilyMemory.tagsStr.split(/[,，]/).map(t => t.trim()).filter(t => t)
      : undefined
    
    if (editingFamilyMemory.value) {
      const response = await apiService.updateFamilyMemory(editingFamilyMemory.value.id, {
        title: newFamilyMemory.title,
        type: newFamilyMemory.type,
        description: newFamilyMemory.description,
        eventDate: newFamilyMemory.eventDate,
        location: newFamilyMemory.location,
        tags
      })
      
      if (response.success && response.data) {
        const index = familyMemories.value.findIndex(m => m.id === editingFamilyMemory.value?.id)
        if (index > -1) {
          familyMemories.value[index] = response.data
        }
      }
    } else {
      if (newFamilyMemory.mediaFile) {
        const formData = new FormData()
        formData.append('title', newFamilyMemory.title)
        formData.append('type', newFamilyMemory.type)
        if (newFamilyMemory.description) {
          formData.append('description', newFamilyMemory.description)
        }
        if (newFamilyMemory.eventDate) {
          formData.append('eventDate', newFamilyMemory.eventDate)
        }
        if (newFamilyMemory.location) {
          formData.append('location', newFamilyMemory.location)
        }
        if (tags) {
          formData.append('tags', tags.join(','))
        }
        formData.append('file', newFamilyMemory.mediaFile)
        
        const response = await apiService.uploadFamilyMemoryWithMedia(formData)
        if (response.success && response.data) {
          familyMemories.value.unshift(response.data)
        }
      } else {
        const response = await apiService.createFamilyMemory({
          title: newFamilyMemory.title,
          type: newFamilyMemory.type,
          description: newFamilyMemory.description,
          eventDate: newFamilyMemory.eventDate,
          location: newFamilyMemory.location,
          tags
        })
        
        if (response.success && response.data) {
          familyMemories.value.unshift(response.data)
        }
      }
    }
    
    familyMemories.value.sort((a, b) => {
      const dateA = a.eventDate || a.createdAt
      const dateB = b.eventDate || b.createdAt
      return new Date(dateB).getTime() - new Date(dateA).getTime()
    })
    
    closeFamilyMemoryModal()
  } catch (error) {
    console.error('保存家族记忆失败:', error)
  } finally {
    isFamilyMemoryLoading.value = false
  }
}

const editFamilyMemory = (memory: FamilyMemoryItem) => {
  editingFamilyMemory.value = memory
  newFamilyMemory.title = memory.title
  newFamilyMemory.type = memory.type
  newFamilyMemory.description = memory.description || ''
  newFamilyMemory.eventDate = memory.eventDate || ''
  newFamilyMemory.location = memory.location || ''
  newFamilyMemory.tagsStr = memory.tags?.join(', ') || ''
  newFamilyMemory.mediaFile = null
  newFamilyMemory.previewUrl = memory.mediaUrl ? getFullMediaUrl(memory.mediaUrl) : ''
  showFamilyMemoryModal.value = true
}

const openFamilyMemoryDetail = (memory: FamilyMemoryItem) => {
  selectedFamilyMemory.value = memory
  showFamilyMemoryDetailModal.value = true
}

const confirmDeleteFamilyMemory = (memory: FamilyMemoryItem) => {
  deletingFamilyMemory.value = memory
  showDeleteFamilyMemoryConfirm.value = true
}

const deleteFamilyMemory = async () => {
  if (!deletingFamilyMemory.value) return
  
  isFamilyMemoryLoading.value = true
  try {
    const response = await apiService.deleteFamilyMemory(deletingFamilyMemory.value.id)
    if (response.success) {
      const index = familyMemories.value.findIndex(m => m.id === deletingFamilyMemory.value?.id)
      if (index > -1) {
        familyMemories.value.splice(index, 1)
      }
      showDeleteFamilyMemoryConfirm.value = false
      deletingFamilyMemory.value = null
    }
  } catch (error) {
    console.error('删除家族记忆失败:', error)
  } finally {
    isFamilyMemoryLoading.value = false
  }
}

const hasFamily = ref<boolean | null>(null)
const showCreateFamilyModal = ref(false)
const showJoinFamilyModal = ref(false)
const showCollaborationModal = ref(false)
const collaborationLinks = ref<CollaborationLink[]>([])
const loadingCollaborationLinks = ref(false)

const userFamilies = ref<UserFamilyListItem[]>([])
const currentFamilyId = ref<string | null>(null)
const showFamilySidebar = ref(false)

const currentFamily = computed<UserFamilyListItem | null>(() => {
  if (!currentFamilyId.value) return null
  return userFamilies.value.find(f => f.family.id === currentFamilyId.value) || null
})

const hasOwnedFamily = computed(() => {
  return userFamilies.value.some(f => f.isHead)
})

const ownedFamily = computed<UserFamilyListItem | null>(() => {
  return userFamilies.value.find(f => f.isHead) || null
})

const createFamilyForm = reactive({
  hallName: '',
  surname: '',
  ancestor: '',
  description: '',
  ziBeiStr: ''
})

const joinLinkCode = ref('')

const newLinkForm = reactive({
  role: 'viewer' as FamilyRole,
  maxUses: 1,
  expiresInDays: 30
})

const isCreatingFamily = ref(false)
const isJoiningFamily = ref(false)
const isCreatingLink = ref(false)
const copyingLinkId = ref<string | null>(null)

let permissionPollTimer: number | null = null
const POLL_INTERVAL = 30000

const refreshPermissions = async () => {
  try {
    const statusResp = await apiService.getMyFamilyStatus()
    
    if (statusResp.success && statusResp.data) {
      const oldHasFamily = hasFamily.value
      const oldRole = myRole.value
      
      hasFamily.value = statusResp.data.hasFamily
      userFamilies.value = statusResp.data.families || []
      
      if (statusResp.data.hasFamily && userFamilies.value.length > 0) {
        const storedFamilyId = apiService.getCurrentFamilyId()
        let targetFamily: UserFamilyListItem | null = null
        
        if (storedFamilyId) {
          targetFamily = userFamilies.value.find(f => f.family.id === storedFamilyId) || null
        }
        
        if (!targetFamily) {
          if (statusResp.data.ownedFamily) {
            targetFamily = statusResp.data.ownedFamily
          } else {
            targetFamily = userFamilies.value[0]
          }
        }
        
        if (targetFamily) {
          if (!currentFamilyId.value || currentFamilyId.value !== targetFamily.family.id) {
            currentFamilyId.value = targetFamily.family.id
            apiService.setCurrentFamilyId(targetFamily.family.id)
            myRole.value = targetFamily.role
            
            familyInfo.hallName = targetFamily.family.hallName || ''
            familyInfo.surname = targetFamily.family.surname
            familyInfo.ancestor = targetFamily.family.ancestor || ''
            familyInfo.description = targetFamily.family.description || ''
            familyInfo.ziBei = targetFamily.family.ziBei || []
            
            if (!oldHasFamily && statusResp.data.hasFamily) {
              await loadData()
            }
          } else if (targetFamily.role !== oldRole) {
            myRole.value = targetFamily.role
            alert(`您的权限已变更为：${roleLabel(targetFamily.role)}`)
          }
        }
      } else {
        currentFamilyId.value = null
        apiService.setCurrentFamilyId(null)
        myRole.value = null
      }
    }
  } catch (error) {
    console.error('刷新权限失败:', error)
  }
}

const isHead = computed(() => myRole.value === 'head')

const linkStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    active: '有效',
    expired: '已过期',
    used: '已使用',
    disabled: '已禁用'
  }
  return labels[status] || status
}

const linkStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    active: 'bg-green-100 text-green-700',
    expired: 'bg-yellow-100 text-yellow-700',
    used: 'bg-blue-100 text-blue-700',
    disabled: 'bg-gray-100 text-gray-500'
  }
  return classes[status] || 'bg-gray-100 text-gray-500'
}

const generateShareLink = (linkCode: string) => {
  return `${window.location.origin}/collaboration/join/${linkCode}`
}

const handleCreateFamily = async () => {
  if (!createFamilyForm.surname.trim()) {
    alert('请输入姓氏')
    return
  }
  
  isCreatingFamily.value = true
  try {
    const ziBei = createFamilyForm.ziBeiStr
      .split(/[,，\s]+/)
      .filter(s => s.trim())
    
    const response = await apiService.createFamily({
      hallName: createFamilyForm.hallName.trim() || undefined,
      surname: createFamilyForm.surname.trim(),
      ancestor: createFamilyForm.ancestor.trim() || undefined,
      description: createFamilyForm.description.trim() || undefined,
      ziBei: ziBei.length > 0 ? ziBei : undefined
    })
    
    if (response.success && response.data) {
      myRole.value = response.data.role
      hasFamily.value = true
      showCreateFamilyModal.value = false
      await loadData()
    } else {
      alert(`创建失败: ${response.error || '未知错误'}`)
    }
  } catch (error) {
    console.error('创建家族失败:', error)
    alert('创建失败，请稍后重试')
  } finally {
    isCreatingFamily.value = false
  }
}

const handleJoinFamily = async () => {
  if (!joinLinkCode.value.trim()) {
    alert('请输入链接代码')
    return
  }
  
  isJoiningFamily.value = true
  try {
    const response = await apiService.joinByLink(joinLinkCode.value.trim().toUpperCase())
    
    if (response.success && response.data) {
      myRole.value = response.data.role
      hasFamily.value = true
      showJoinFamilyModal.value = false
      joinLinkCode.value = ''
      await loadData()
    } else {
      alert(`加入失败: ${response.error || '未知错误'}`)
    }
  } catch (error) {
    console.error('加入家族失败:', error)
    alert('加入失败，请检查链接代码是否正确')
  } finally {
    isJoiningFamily.value = false
  }
}

const loadCollaborationLinks = async () => {
  loadingCollaborationLinks.value = true
  try {
    const response = await apiService.getCollaborationLinks()
    if (response.success && response.data) {
      collaborationLinks.value = response.data.links
    }
  } catch (error) {
    console.error('加载链接列表失败:', error)
  } finally {
    loadingCollaborationLinks.value = false
  }
}

const handleCreateLink = async () => {
  if (newLinkForm.maxUses < 1) {
    alert('使用次数至少为1次')
    return
  }
  
  isCreatingLink.value = true
  try {
    const response = await apiService.createCollaborationLink({
      role: newLinkForm.role,
      maxUses: newLinkForm.maxUses,
      expiresInDays: newLinkForm.expiresInDays > 0 ? newLinkForm.expiresInDays : undefined
    })
    
    if (response.success && response.data) {
      collaborationLinks.value.unshift(response.data)
      newLinkForm.role = 'viewer'
      newLinkForm.maxUses = 1
      newLinkForm.expiresInDays = 30
    } else {
      alert(`创建失败: ${response.error || '未知错误'}`)
    }
  } catch (error) {
    console.error('创建链接失败:', error)
    alert('创建失败，请稍后重试')
  } finally {
    isCreatingLink.value = false
  }
}

const handleUpdateLinkRole = async (linkId: string, newRole: FamilyRole) => {
  try {
    const response = await apiService.updateCollaborationLink(linkId, { role: newRole })
    if (response.success && response.data) {
      const index = collaborationLinks.value.findIndex(l => l.id === linkId)
      if (index > -1) {
        collaborationLinks.value[index] = response.data
      }
    }
  } catch (error) {
    console.error('更新链接失败:', error)
    alert('更新失败')
  }
}

const handleToggleLinkVisibility = async (linkId: string, isVisible: boolean) => {
  try {
    const response = await apiService.updateCollaborationLink(linkId, { isVisible })
    if (response.success && response.data) {
      const index = collaborationLinks.value.findIndex(l => l.id === linkId)
      if (index > -1) {
        collaborationLinks.value[index] = response.data
      }
    }
  } catch (error) {
    console.error('更新链接可见性失败:', error)
    alert('更新失败')
  }
}

const handleResetLink = async (linkId: string) => {
  if (!confirm('重置链接将生成新的链接代码，旧链接将失效。确定要重置吗？')) {
    return
  }
  
  try {
    const response = await apiService.resetCollaborationLink(linkId)
    if (response.success && response.data) {
      const index = collaborationLinks.value.findIndex(l => l.id === linkId)
      if (index > -1) {
        collaborationLinks.value[index] = response.data
      }
    }
  } catch (error) {
    console.error('重置链接失败:', error)
    alert('重置失败')
  }
}

const handleCopyLink = async (linkCode: string) => {
  const shareLink = generateShareLink(linkCode)
  try {
    await navigator.clipboard.writeText(shareLink)
    copyingLinkId.value = linkCode
    setTimeout(() => {
      copyingLinkId.value = null
    }, 2000)
  } catch (error) {
    alert(`复制失败，请手动复制: ${shareLink}`)
  }
}

const pendingApprovalsCount = ref(0)
const myPendingInvitationsCount = ref(0)

const myRole = ref<FamilyRole | null>(null)

const canEdit = computed(() => {
  if (!myRole.value) return false
  const roles: FamilyRole[] = ['head', 'admin', 'editor']
  return roles.includes(myRole.value)
})

const canDelete = computed(() => {
  if (!myRole.value) return false
  const roles: FamilyRole[] = ['head', 'admin', 'editor']
  return roles.includes(myRole.value)
})

const canManageMembers = computed(() => {
  if (!myRole.value) return false
  const roles: FamilyRole[] = ['head', 'admin']
  return roles.includes(myRole.value)
})

const canViewApprovals = computed(() => {
  if (!myRole.value) return false
  const roles: FamilyRole[] = ['head', 'admin', 'editor']
  return roles.includes(myRole.value)
})

const canViewLogs = computed(() => {
  if (!myRole.value) return false
  const roles: FamilyRole[] = ['head', 'admin', 'editor']
  return roles.includes(myRole.value)
})

const roleLabel = (role: FamilyRole) => {
  const labels: Record<FamilyRole, string> = {
    head: '族长',
    admin: '管理员',
    editor: '编辑',
    viewer: '浏览',
  }
  return labels[role]
}

const roleClass = (role: FamilyRole) => {
  const classes: Record<FamilyRole, string> = {
    head: 'bg-red-100 text-red-700',
    admin: 'bg-purple-100 text-purple-700',
    editor: 'bg-blue-100 text-blue-700',
    viewer: 'bg-gray-100 text-gray-600',
  }
  return classes[role]
}

const toggleManageMenu = () => {
  showManageMenu.value = !showManageMenu.value
}

const closeManageMenu = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    showManageMenu.value = false
  }
}

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

const showImportModal = ref(false)
const showExportModal = ref(false)
const selectedFile = ref<File | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const importing = ref(false)
const exporting = ref(false)
const importError = ref('')
const importPreview = ref<any[]>([])
const importDuplicateNames = ref<string[]>([])
const importDuplicateCount = ref(0)
const importNewCount = ref(0)
const exportFormat = ref('xlsx')

interface ImportMemberData {
  name: string
  gender: 'male' | 'female'
  generation: number
  birthYear?: string
  deathYear?: string
  spouse?: string
  fatherName?: string
  residence?: string
  note?: string
  status: 'alive' | 'deceased'
}

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const clearSelectedFile = () => {
  selectedFile.value = null
  importPreview.value = []
  importError.value = ''
  importDuplicateNames.value = []
  importDuplicateCount.value = 0
  importNewCount.value = 0
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

const closeImportModal = () => {
  showImportModal.value = false
  clearSelectedFile()
}

const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const validExtensions = ['.xlsx', '.xls', '.csv']
  const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'))
  
  if (!validExtensions.includes(fileExtension)) {
    importError.value = '不支持的文件格式，请上传 .xlsx, .xls 或 .csv 文件'
    return
  }

  selectedFile.value = file
  importError.value = ''
  
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiService.previewImport(formData)
    if (response.success && response.data) {
      importPreview.value = response.data.preview
      importDuplicateNames.value = response.data.duplicate_names || []
      importDuplicateCount.value = response.data.duplicate_count || 0
      importNewCount.value = response.data.new_count || response.data.preview.length
    } else {
      importError.value = response.error || '文件解析失败'
    }
  } catch (error) {
    console.error('文件预览失败:', error)
    importError.value = '文件解析失败，请检查文件格式'
  }
}

const handleImport = async () => {
  if (!selectedFile.value) return

  importing.value = true
  importError.value = ''
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    const response = await apiService.importData(formData)
    if (response.success && response.data) {
      const { imported_count, skipped_count, skipped_names, members } = response.data
      
      let message = `导入成功！\n新增：${imported_count} 条`
      if (skipped_count > 0) {
        message += `\n跳过重复：${skipped_count} 条`
        if (skipped_names && skipped_names.length > 0) {
          message += `\n\n跳过的成员：${skipped_names.slice(0, 5).join('、')}`
          if (skipped_names.length > 5) {
            message += ` 等${skipped_names.length}人`
          }
        }
      }
      
      alert(message)
      familyMembers.value = members
      closeImportModal()
    } else {
      importError.value = response.error || '导入失败'
    }
  } catch (error) {
    console.error('导入失败:', error)
    importError.value = '导入失败，请稍后重试'
  } finally {
    importing.value = false
  }
}

const handleExport = async () => {
  exporting.value = true
  
  try {
    const blob = await apiService.exportData(exportFormat.value)
    
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `族谱数据_${familyInfo.surname}氏_${new Date().toISOString().slice(0, 10)}.${exportFormat.value}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    
    showExportModal.value = false
    alert('导出成功！')
  } catch (error) {
    console.error('导出失败:', error)
    alert('导出失败，请稍后重试')
  } finally {
    exporting.value = false
  }
}

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
    const statusResp = await apiService.getMyFamilyStatus()
    
    if (statusResp.success && statusResp.data) {
      hasFamily.value = statusResp.data.hasFamily
      userFamilies.value = statusResp.data.families || []
      
      if (!statusResp.data.hasFamily || userFamilies.value.length === 0) {
        isLoading.value = false
        return
      }
      
      let targetFamily: UserFamilyListItem | null = null
      const storedFamilyId = apiService.getCurrentFamilyId()
      
      if (storedFamilyId) {
        targetFamily = userFamilies.value.find(f => f.family.id === storedFamilyId) || null
      }
      
      if (!targetFamily) {
        if (statusResp.data.ownedFamily) {
          targetFamily = statusResp.data.ownedFamily
        } else {
          targetFamily = userFamilies.value[0]
        }
      }
      
      if (targetFamily) {
        currentFamilyId.value = targetFamily.family.id
        apiService.setCurrentFamilyId(targetFamily.family.id)
        myRole.value = targetFamily.role
        
        familyInfo.hallName = targetFamily.family.hallName || ''
        familyInfo.surname = targetFamily.family.surname
        familyInfo.ancestor = targetFamily.family.ancestor || ''
        familyInfo.description = targetFamily.family.description || ''
        familyInfo.ziBei = targetFamily.family.ziBei || []
        familySettingsForm.hallName = targetFamily.family.hallName || ''
        familySettingsForm.surname = targetFamily.family.surname
        familySettingsForm.ancestor = targetFamily.family.ancestor || ''
        familySettingsForm.description = targetFamily.family.description || ''
        familySettingsForm.ziBeiStr = (targetFamily.family.ziBei || []).join(',')
      }
      
      const [familyResp, approvalsResp, invitationsResp] = await Promise.all([
        apiService.getFamily(),
        apiService.getPendingApprovals(),
        apiService.getMyInvitations('pending'),
      ])

      if (familyResp.success && familyResp.data) {
        const { family, members } = familyResp.data
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
        console.error('加载家族数据失败:', familyResp.error)
      }

      if (approvalsResp.success && approvalsResp.data) {
        pendingApprovalsCount.value = approvalsResp.data.approvals.length
      }

      if (invitationsResp.success && invitationsResp.data) {
        myPendingInvitationsCount.value = invitationsResp.data.invitations.length
      }
      
      await loadFamilyMemories()
    } else {
      console.error('获取家族状态失败:', statusResp.error)
      if (statusResp.error && statusResp.error.includes('404')) {
        hasFamily.value = false
      } else if (statusResp.error && statusResp.error.includes('401')) {
        alert('请先登录')
        router.push('/login')
        return
      } else {
        hasFamily.value = false
      }
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    hasFamily.value = false
  } finally {
    isLoading.value = false
  }
}

const switchFamily = async (familyId: string) => {
  const targetFamily = userFamilies.value.find(f => f.family.id === familyId)
  if (!targetFamily) return
  
  currentFamilyId.value = familyId
  apiService.setCurrentFamilyId(familyId)
  myRole.value = targetFamily.role
  
  familyInfo.hallName = targetFamily.family.hallName || ''
  familyInfo.surname = targetFamily.family.surname
  familyInfo.ancestor = targetFamily.family.ancestor || ''
  familyInfo.description = targetFamily.family.description || ''
  familyInfo.ziBei = targetFamily.family.ziBei || []
  familySettingsForm.hallName = targetFamily.family.hallName || ''
  familySettingsForm.surname = targetFamily.family.surname
  familySettingsForm.ancestor = targetFamily.family.ancestor || ''
  familySettingsForm.description = targetFamily.family.description || ''
  familySettingsForm.ziBeiStr = (targetFamily.family.ziBei || []).join(',')
  
  showFamilySidebar.value = false
  
  isLoading.value = true
  try {
    const familyResp = await apiService.getFamily()
    if (familyResp.success && familyResp.data) {
      const { family, members } = familyResp.data
      familyInfo.hallName = family.hallName || ''
      familyInfo.surname = family.surname
      familyInfo.ancestor = family.ancestor || ''
      familyInfo.description = family.description || ''
      familyInfo.ziBei = family.ziBei || []
      familyMembers.value = members
    }
  } catch (error) {
    console.error('加载家族数据失败:', error)
  } finally {
    isLoading.value = false
  }
}

const navigateToMemberManagement = () => {
  showManageMenu.value = false
  router.push('/family/members')
}

const navigateToApprovals = () => {
  showManageMenu.value = false
  router.push('/family/approvals')
}

const navigateToLogs = () => {
  showManageMenu.value = false
  router.push('/family/logs')
}

onMounted(() => {
  loadData()
  document.addEventListener('click', closeManageMenu)
  
  permissionPollTimer = window.setInterval(refreshPermissions, POLL_INTERVAL)
})

onUnmounted(() => {
  document.removeEventListener('click', closeManageMenu)
  
  if (permissionPollTimer !== null) {
    window.clearInterval(permissionPollTimer)
    permissionPollTimer = null
  }
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
