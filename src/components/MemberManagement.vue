<template>
  <div class="min-h-screen paper-texture">
    <header class="sticky top-0 z-50 glass-warm border-b border-[#E8D5C4]">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button @click="$router.back()" class="w-10 h-10 rounded-full hover:bg-[#E8D5C4] flex items-center justify-center transition-colors">
            <Icon icon="solar:arrow-left-bold" class="text-[#8B6F4E]" />
          </button>
          <div>
            <h1 class="text-xl font-bold text-[#5C4A3A] font-serif tracking-wider">家族管理</h1>
            <p class="text-xs text-gray-500">成员邀请 · 权限管理</p>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-6">
      <div class="flex border-b border-[#E8D5C4] mb-6">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-6 py-3 text-sm font-medium transition-colors relative',
            activeTab === tab.id ? 'text-[#8B6F4E]' : 'text-gray-500 hover:text-gray-700'
          ]">
          <span class="flex items-center space-x-2">
            <Icon :icon="tab.icon" class="text-lg" />
            <span>{{ tab.label }}</span>
            <span v-if="tab.badge" class="w-5 h-5 rounded-full bg-[#C84A3E] text-white text-xs flex items-center justify-center">
              {{ tab.badge }}
            </span>
          </span>
          <div v-if="activeTab === tab.id" class="absolute bottom-0 left-0 right-0 h-0.5 bg-[#8B6F4E]"></div>
        </button>
      </div>

      <div v-if="activeTab === 'members'" class="bg-white rounded-2xl shadow-soft border border-stone-100 p-6">
        <div class="flex items-center justify-between mb-6">
          <div class="relative flex-1 max-w-md">
            <Icon icon="solar:search-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input v-model="memberSearch" type="text" placeholder="搜索成员（姓名/邮箱）..." 
              class="pl-10 pr-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4] w-full" />
          </div>
          <div class="flex items-center space-x-3">
            <select v-model="memberRoleFilter" class="px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
              <option value="">全部角色</option>
              <option value="head">族长</option>
              <option value="admin">管理员</option>
              <option value="editor">编辑</option>
              <option value="viewer">浏览</option>
            </select>
            <button v-if="canInvite" @click="showInviteModal = true" class="px-4 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all flex items-center space-x-2">
              <Icon icon="solar:user-add-bold" class="text-sm" />
              <span>邀请成员</span>
            </button>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-stone-200">
                <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">成员</th>
                <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">邮箱</th>
                <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">角色</th>
                <th class="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">加入时间</th>
                <th class="text-right py-3 px-4 text-xs font-medium text-gray-500 uppercase">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="fu in filteredFamilyUsers" :key="fu.id" 
                class="border-b border-stone-100 hover:bg-[#FAF7F2] transition-colors">
                <td class="py-4 px-4">
                  <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-full bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] flex items-center justify-center">
                      <span class="text-white font-medium">{{ fu.user?.nickname?.charAt(0) || fu.user?.username?.charAt(0) || '?' }}</span>
                    </div>
                    <div>
                      <p class="font-medium text-[#5C4A3A]">{{ fu.user?.nickname || fu.user?.username || '未知' }}</p>
                      <p v-if="fu.role === 'head'" class="text-xs text-[#C84A3E]">族长</p>
                    </div>
                  </div>
                </td>
                <td class="py-4 px-4 text-sm text-gray-600">
                  {{ fu.user?.username || '-' }}
                </td>
                <td class="py-4 px-4">
                  <span class="px-3 py-1 rounded-full text-xs font-medium"
                    :class="roleClass(fu.role)">
                    {{ roleLabel(fu.role) }}
                  </span>
                </td>
                <td class="py-4 px-4 text-sm text-gray-500">
                  {{ formatDate(fu.createdAt) }}
                </td>
                <td class="py-4 px-4 text-right">
                  <div class="flex items-center justify-end space-x-2">
                    <button v-if="canManageRole(fu.role)" 
                      @click="startChangeRole(fu)"
                      class="text-[#8B6F4E] text-sm hover:text-[#D4A574] transition-colors">
                      调整角色
                    </button>
                    <button v-if="canRemove(fu.role)" 
                      @click="removeMember(fu)"
                      class="text-red-500 text-sm hover:text-red-600 transition-colors">
                      移除
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredFamilyUsers.length === 0">
                <td colspan="5" class="py-8 text-center text-gray-400">
                  暂无成员数据
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="activeTab === 'invitations'" class="space-y-6">
        <div v-if="pendingInvitations.length > 0" class="bg-white rounded-2xl shadow-soft border border-stone-100 p-6">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif flex items-center space-x-2 mb-4">
            <Icon icon="solar:clock-circle-bold" class="text-[#C84A3E]" />
            <span>待处理邀请（{{ pendingInvitations.length }}）</span>
          </h3>
          <div class="space-y-3">
            <div v-for="inv in pendingInvitations" :key="inv.id" 
              class="flex items-center justify-between p-4 bg-[#FAF7F2] rounded-xl">
              <div class="flex items-center space-x-4">
                <div class="w-12 h-12 rounded-full bg-yellow-100 flex items-center justify-center">
                  <Icon icon="solar:letter-bold" class="text-yellow-600 text-xl" />
                </div>
                <div>
                  <p class="font-medium text-[#5C4A3A]">{{ inv.inviteeEmail }}</p>
                  <p class="text-xs text-gray-500">
                    邀请人: {{ inv.inviter?.nickname || inv.inviter?.username }} · 
                    角色: {{ roleLabel(inv.role) }}
                  </p>
                  <p v-if="inv.message" class="text-xs text-gray-400 mt-1">
                    留言: {{ inv.message }}
                  </p>
                </div>
              </div>
              <div class="flex items-center space-x-3">
                <span class="text-xs text-gray-400">
                  {{ formatDate(inv.createdAt) }}
                </span>
                <button @click="resendInvitation(inv)" class="text-[#8B6F4E] text-sm hover:text-[#D4A574] transition-colors">
                  重发
                </button>
                <button @click="cancelInvitation(inv)" class="text-red-500 text-sm hover:text-red-600 transition-colors">
                  取消
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl shadow-soft border border-stone-100 p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold text-[#5C4A3A] font-serif flex items-center space-x-2">
              <Icon icon="solar:history-bold" class="text-[#8B6F4E]" />
              <span>历史邀请</span>
            </h3>
            <select v-model="invitationStatusFilter" class="px-3 py-1.5 bg-[#FAF7F2] border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
              <option value="">全部</option>
              <option value="accepted">已接受</option>
              <option value="rejected">已拒绝</option>
              <option value="expired">已过期</option>
            </select>
          </div>
          <div class="space-y-3">
            <div v-for="inv in filteredHistoryInvitations" :key="inv.id" 
              class="flex items-center justify-between p-4 border border-stone-100 rounded-xl">
              <div class="flex items-center space-x-4">
                <div class="w-10 h-10 rounded-full flex items-center justify-center"
                  :class="{
                    'bg-green-100': inv.status === 'accepted',
                    'bg-red-100': inv.status === 'rejected',
                    'bg-gray-100': inv.status === 'expired'
                  }">
                  <Icon v-if="inv.status === 'accepted'" icon="solar:check-circle-bold" class="text-green-600" />
                  <Icon v-else-if="inv.status === 'rejected'" icon="solar:close-circle-bold" class="text-red-600" />
                  <Icon v-else icon="solar:clock-circle-outline" class="text-gray-500" />
                </div>
                <div>
                  <p class="font-medium text-[#5C4A3A]">{{ inv.inviteeEmail }}</p>
                  <p class="text-xs text-gray-500">
                    角色: {{ roleLabel(inv.role) }}
                  </p>
                </div>
              </div>
              <div class="flex items-center space-x-3">
                <span class="px-2 py-1 rounded-full text-xs"
                  :class="{
                    'bg-green-100 text-green-700': inv.status === 'accepted',
                    'bg-red-100 text-red-700': inv.status === 'rejected',
                    'bg-gray-100 text-gray-600': inv.status === 'expired'
                  }">
                  {{ invitationStatusLabel(inv.status) }}
                </span>
                <span class="text-xs text-gray-400">
                  {{ formatDate(inv.createdAt) }}
                </span>
              </div>
            </div>
            <div v-if="filteredHistoryInvitations.length === 0" class="py-8 text-center text-gray-400">
              暂无历史邀请记录
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'my-invitations'" class="space-y-6">
        <div v-if="myPendingInvitations.length > 0" class="bg-white rounded-2xl shadow-soft border border-stone-100 p-6">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif flex items-center space-x-2 mb-4">
            <Icon icon="solar:bell-bold" class="text-[#C84A3E]" />
            <span>收到的邀请（{{ myPendingInvitations.length }}）</span>
          </h3>
          <div class="space-y-4">
            <div v-for="inv in myPendingInvitations" :key="inv.id" 
              class="p-6 bg-gradient-to-br from-[#FAF7F2] to-[#F5F1EC] rounded-xl border border-[#E8D5C4]">
              <div class="flex items-start justify-between">
                <div class="flex items-start space-x-4">
                  <div class="w-14 h-14 rounded-full bg-gradient-to-br from-[#8B6F4E] to-[#A67B5B] flex items-center justify-center shadow-md">
                    <span class="text-white text-xl font-serif font-bold">
                      {{ inv.family?.surname?.charAt(0) || '?' }}
                    </span>
                  </div>
                  <div class="flex-1">
                    <p class="font-bold text-[#5C4A3A] text-lg">
                      {{ inv.family?.surname }}氏家族
                      <span v-if="inv.family?.hallName" class="text-sm font-normal text-gray-500">
                        （{{ inv.family?.hallName }}）
                      </span>
                    </p>
                    <p class="text-sm text-gray-500 mt-1">
                      邀请人: <span class="text-[#5C4A3A] font-medium">{{ inv.inviter?.nickname || inv.inviter?.username }}</span>
                    </p>
                    <p class="text-sm text-gray-500">
                      邀请角色: <span class="font-medium">{{ roleLabel(inv.role) }}</span>
                    </p>
                    <p v-if="inv.message" class="text-sm text-gray-600 mt-3 p-3 bg-white/60 rounded-lg">
                      <span class="text-gray-400">留言: </span>{{ inv.message }}
                    </p>
                    <p class="text-xs text-gray-400 mt-2">
                      邀请时间: {{ formatDate(inv.createdAt) }} · 
                      有效期至: {{ formatDate(inv.expiresAt) }}
                    </p>
                  </div>
                </div>
              </div>
              <div class="flex items-center justify-end space-x-3 mt-4 pt-4 border-t border-[#E8D5C4]">
                <button @click="showRejectModal(inv)" class="px-6 py-2 text-gray-600 bg-gray-100 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors">
                  拒绝
                </button>
                <button @click="acceptMyInvitation(inv)" class="px-6 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all">
                  接受邀请
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="bg-white rounded-2xl shadow-soft border border-stone-100 p-12 text-center">
          <Icon icon="solar:inbox-empty-bold" class="text-6xl text-gray-300 mx-auto mb-4" />
          <p class="text-gray-500 mb-2">暂无收到的邀请</p>
          <p class="text-gray-400 text-sm">当有人邀请您加入家族时，邀请将显示在这里</p>
        </div>
      </div>
    </main>

    <div v-if="showInviteModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div class="border-b border-stone-100 px-6 py-4 flex items-center justify-between">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">邀请成员加入</h3>
          <button @click="closeInviteModal" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="material-symbols:close" class="text-gray-500" />
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">邀请邮箱 *</label>
            <input v-model="inviteForm.inviteeEmail" type="email" placeholder="请输入被邀请人邮箱"
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">分配角色 *</label>
            <select v-model="inviteForm.role" 
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4]">
              <option v-for="role in availableRoles" :key="role.value" :value="role.value">
                {{ role.label }}
              </option>
            </select>
            <p class="text-xs text-gray-400 mt-1">
              权限等级: 族长 > 管理员 > 编辑 > 浏览
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">邀请留言</label>
            <textarea v-model="inviteForm.message" rows="3" placeholder="给被邀请人的留言（可选）"
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4] resize-none"></textarea>
          </div>
        </div>
        <div class="border-t border-stone-100 px-6 py-4 flex justify-end space-x-3">
          <button @click="closeInviteModal" class="px-6 py-2 text-gray-600 bg-gray-100 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors">
            取消
          </button>
          <button @click="sendInvitation" class="px-6 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all">
            发送邀请
          </button>
        </div>
      </div>
    </div>

    <div v-if="showRoleModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div class="border-b border-stone-100 px-6 py-4 flex items-center justify-between">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">调整角色</h3>
          <button @click="closeRoleModal" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="material-symbols:close" class="text-gray-500" />
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div v-if="selectedFamilyUser" class="flex items-center space-x-3 p-3 bg-[#FAF7F2] rounded-xl">
            <div class="w-12 h-12 rounded-full bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] flex items-center justify-center">
              <span class="text-white font-medium">
                {{ selectedFamilyUser.user?.nickname?.charAt(0) || selectedFamilyUser.user?.username?.charAt(0) || '?' }}
              </span>
            </div>
            <div>
              <p class="font-medium text-[#5C4A3A]">
                {{ selectedFamilyUser.user?.nickname || selectedFamilyUser.user?.username }}
              </p>
              <p class="text-xs text-gray-500">当前角色: {{ roleLabel(selectedFamilyUser.role) }}</p>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">选择新角色</label>
            <div class="space-y-2">
              <div v-for="role in availableRoles" :key="role.value" 
                @click="roleForm.newRole = role.value"
                class="flex items-center space-x-3 p-3 rounded-xl cursor-pointer transition-colors"
                :class="roleForm.newRole === role.value ? 'bg-[#E8D5C4] border-2 border-[#8B6F4E]' : 'bg-[#FAF7F2] border-2 border-transparent'">
                <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center"
                  :class="roleForm.newRole === role.value ? 'border-[#8B6F4E] bg-[#8B6F4E]' : 'border-gray-300'">
                  <Icon v-if="roleForm.newRole === role.value" icon="solar:check-bold" class="text-white text-xs" />
                </div>
                <div class="flex-1">
                  <p class="font-medium text-[#5C4A3A]">{{ role.label }}</p>
                  <p class="text-xs text-gray-500">{{ role.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="border-t border-stone-100 px-6 py-4 flex justify-end space-x-3">
          <button @click="closeRoleModal" class="px-6 py-2 text-gray-600 bg-gray-100 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors">
            取消
          </button>
          <button @click="saveRoleChange" class="px-6 py-2 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white rounded-xl text-sm font-medium shadow-warm hover:shadow-lg transition-all">
            确认调整
          </button>
        </div>
      </div>
    </div>

    <div v-if="showRejectReasonModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div class="border-b border-stone-100 px-6 py-4 flex items-center justify-between">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">拒绝邀请</h3>
          <button @click="closeRejectModal" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="material-symbols:close" class="text-gray-500" />
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div v-if="selectedInvitation" class="p-3 bg-[#FAF7F2] rounded-xl">
            <p class="font-medium text-[#5C4A3A]">
              拒绝 {{ selectedInvitation.family?.surname }}氏家族的邀请
            </p>
            <p class="text-xs text-gray-500 mt-1">
              邀请人: {{ selectedInvitation.inviter?.nickname || selectedInvitation.inviter?.username }}
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">拒绝原因（可选）</label>
            <textarea v-model="rejectReason" rows="3" placeholder="请输入拒绝原因（可选）"
              class="w-full px-4 py-2 bg-[#FAF7F2] border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E8D5C4] resize-none"></textarea>
          </div>
        </div>
        <div class="border-t border-stone-100 px-6 py-4 flex justify-end space-x-3">
          <button @click="closeRejectModal" class="px-6 py-2 text-gray-600 bg-gray-100 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors">
            取消
          </button>
          <button @click="rejectMyInvitation" class="px-6 py-2 bg-red-500 text-white rounded-xl text-sm font-medium hover:bg-red-600 transition-colors">
            确认拒绝
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import { 
  apiService, 
  authStore, 
  FamilyUser, 
  Invitation, 
  FamilyRole,
  Family
} from '../services/api'

const router = useRouter()

const isLoading = ref(false)
const activeTab = ref<'members' | 'invitations' | 'my-invitations'>('members')
const memberSearch = ref('')
const memberRoleFilter = ref('')
const invitationStatusFilter = ref('')

const familyUsers = ref<FamilyUser[]>([])
const invitations = ref<Invitation[]>([])
const myInvitations = ref<Invitation[]>([])
const myFamilyInfo = ref<{ role: FamilyRole } | null>(null)

const showInviteModal = ref(false)
const showRoleModal = ref(false)
const showRejectReasonModal = ref(false)
const selectedFamilyUser = ref<FamilyUser | null>(null)
const selectedInvitation = ref<Invitation | null>(null)
const rejectReason = ref('')

const tabs = computed(() => [
  { id: 'members', label: '成员列表', icon: 'solar:users-group-two-bold', badge: null },
  { id: 'invitations', label: '发出的邀请', icon: 'solar:outgoing-call-bold', badge: pendingInvitations.value.length || null },
  { id: 'my-invitations', label: '收到的邀请', icon: 'solar:inbox-bold', badge: myPendingInvitations.value.length || null },
])

const inviteForm = reactive({
  inviteeEmail: '',
  role: 'viewer' as FamilyRole,
  message: '',
})

const roleForm = reactive({
  newRole: 'viewer' as FamilyRole,
})

const roleDefinitions = [
  { value: 'head' as FamilyRole, label: '族长', description: '最高权限，可管理所有成员和数据' },
  { value: 'admin' as FamilyRole, label: '管理员', description: '可邀请成员、管理角色、审核修改' },
  { value: 'editor' as FamilyRole, label: '编辑', description: '可编辑族谱数据，但修改需要审核' },
  { value: 'viewer' as FamilyRole, label: '浏览', description: '仅可查看族谱数据' },
]

const availableRoles = computed(() => {
  const myRole = myFamilyInfo.value?.role
  if (!myRole) return []
  
  const roleOrder: FamilyRole[] = ['head', 'admin', 'editor', 'viewer']
  const myIndex = roleOrder.indexOf(myRole)
  
  return roleDefinitions.filter((_, index) => index > myIndex)
})

const canInvite = computed(() => {
  const role = myFamilyInfo.value?.role
  return role === 'head' || role === 'admin'
})

const filteredFamilyUsers = computed(() => {
  let result = familyUsers.value
  
  if (memberSearch.value) {
    const keyword = memberSearch.value.toLowerCase()
    result = result.filter(fu => {
      const nickname = fu.user?.nickname?.toLowerCase() || ''
      const username = fu.user?.username?.toLowerCase() || ''
      return nickname.includes(keyword) || username.includes(keyword)
    })
  }
  
  if (memberRoleFilter.value) {
    result = result.filter(fu => fu.role === memberRoleFilter.value)
  }
  
  return result
})

const pendingInvitations = computed(() => {
  return invitations.value.filter(inv => inv.status === 'pending')
})

const historyInvitations = computed(() => {
  return invitations.value.filter(inv => inv.status !== 'pending')
})

const filteredHistoryInvitations = computed(() => {
  if (!invitationStatusFilter.value) {
    return historyInvitations.value
  }
  return historyInvitations.value.filter(inv => inv.status === invitationStatusFilter.value)
})

const myPendingInvitations = computed(() => {
  return myInvitations.value.filter(inv => inv.status === 'pending')
})

const canManageRole = (targetRole: FamilyRole) => {
  const myRole = myFamilyInfo.value?.role
  if (!myRole) return false
  
  const roleOrder: FamilyRole[] = ['head', 'admin', 'editor', 'viewer']
  const myIndex = roleOrder.indexOf(myRole)
  const targetIndex = roleOrder.indexOf(targetRole)
  
  return myIndex < targetIndex
}

const canRemove = (targetRole: FamilyRole) => {
  const myRole = myFamilyInfo.value?.role
  if (!myRole) return false
  
  const roleOrder: FamilyRole[] = ['head', 'admin', 'editor', 'viewer']
  const myIndex = roleOrder.indexOf(myRole)
  const targetIndex = roleOrder.indexOf(targetRole)
  
  return myIndex < targetIndex && targetRole !== 'head'
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

const roleLabel = (role: FamilyRole) => {
  const labels: Record<FamilyRole, string> = {
    head: '族长',
    admin: '管理员',
    editor: '编辑',
    viewer: '浏览',
  }
  return labels[role]
}

const invitationStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    pending: '待处理',
    accepted: '已接受',
    rejected: '已拒绝',
    expired: '已过期',
  }
  return labels[status] || status
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const loadData = async () => {
  isLoading.value = true
  try {
    const [familyInfoResp, usersResp, invitationsResp, myInvitationsResp] = await Promise.all([
      apiService.getMyFamilyInfo(),
      apiService.getFamilyUsers(),
      apiService.getInvitations(),
      apiService.getMyInvitations(),
    ])
    
    if (familyInfoResp.success && familyInfoResp.data) {
      myFamilyInfo.value = { role: familyInfoResp.data.role }
    }
    
    if (usersResp.success && usersResp.data) {
      familyUsers.value = usersResp.data.familyUsers
    }
    
    if (invitationsResp.success && invitationsResp.data) {
      invitations.value = invitationsResp.data.invitations
    }
    
    if (myInvitationsResp.success && myInvitationsResp.data) {
      myInvitations.value = myInvitationsResp.data.invitations
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadData()
})

const closeInviteModal = () => {
  showInviteModal.value = false
  inviteForm.inviteeEmail = ''
  inviteForm.role = 'viewer'
  inviteForm.message = ''
}

const sendInvitation = async () => {
  if (!inviteForm.inviteeEmail.trim()) {
    alert('请输入邀请邮箱')
    return
  }
  
  try {
    const response = await apiService.createInvitation({
      inviteeEmail: inviteForm.inviteeEmail,
      role: inviteForm.role,
      message: inviteForm.message || undefined,
    })
    
    if (response.success && response.data) {
      invitations.value.unshift(response.data)
      closeInviteModal()
      alert('邀请已发送')
    } else {
      alert(`发送失败: ${response.error || '未知错误'}`)
    }
  } catch (error) {
    console.error('发送邀请失败:', error)
    alert('发送邀请失败')
  }
}

const resendInvitation = (inv: Invitation) => {
  alert(`重发邀请功能: ${inv.inviteeEmail}`)
}

const cancelInvitation = async (inv: Invitation) => {
  if (confirm(`确定要取消对 ${inv.inviteeEmail} 的邀请吗？`)) {
    const index = invitations.value.findIndex(i => i.id === inv.id)
    if (index > -1) {
      invitations.value.splice(index, 1)
    }
  }
}

const startChangeRole = (fu: FamilyUser) => {
  selectedFamilyUser.value = fu
  roleForm.newRole = fu.role
  showRoleModal.value = true
}

const closeRoleModal = () => {
  showRoleModal.value = false
  selectedFamilyUser.value = null
}

const saveRoleChange = async () => {
  if (!selectedFamilyUser.value) return
  
  try {
    const response = await apiService.changeUserRole({
      userId: selectedFamilyUser.value.userId,
      newRole: roleForm.newRole,
    })
    
    if (response.success && response.data) {
      const index = familyUsers.value.findIndex(fu => fu.id === selectedFamilyUser.value!.id)
      if (index > -1) {
        familyUsers.value[index] = response.data
      }
      closeRoleModal()
      alert('角色已调整')
    } else {
      alert(`调整失败: ${response.error || '未知错误'}`)
    }
  } catch (error) {
    console.error('调整角色失败:', error)
    alert('调整角色失败')
  }
}

const removeMember = async (fu: FamilyUser) => {
  const name = fu.user?.nickname || fu.user?.username || '该成员'
  if (confirm(`确定要移除 ${name} 吗？`)) {
    const index = familyUsers.value.findIndex(f => f.id === fu.id)
    if (index > -1) {
      familyUsers.value.splice(index, 1)
    }
  }
}

const showRejectModal = (inv: Invitation) => {
  selectedInvitation.value = inv
  rejectReason.value = ''
  showRejectReasonModal.value = true
}

const closeRejectModal = () => {
  showRejectReasonModal.value = false
  selectedInvitation.value = null
  rejectReason.value = ''
}

const acceptMyInvitation = async (inv: Invitation) => {
  if (confirm(`确定要接受 ${inv.family?.surname}氏家族的邀请吗？`)) {
    try {
      const response = await apiService.acceptInvitation(inv.id)
      if (response.success) {
        const index = myInvitations.value.findIndex(i => i.id === inv.id)
        if (index > -1) {
          myInvitations.value.splice(index, 1)
        }
        alert('已接受邀请，请刷新页面')
      } else {
        alert(`接受邀请失败: ${response.error || '未知错误'}`)
      }
    } catch (error) {
      console.error('接受邀请失败:', error)
      alert('接受邀请失败')
    }
  }
}

const rejectMyInvitation = async () => {
  if (!selectedInvitation.value) return
  
  try {
    const response = await apiService.rejectInvitation(
      selectedInvitation.value.id,
      rejectReason.value || undefined
    )
    
    if (response.success) {
      const index = myInvitations.value.findIndex(i => i.id === selectedInvitation.value!.id)
      if (index > -1) {
        myInvitations.value.splice(index, 1)
      }
      closeRejectModal()
      alert('已拒绝邀请')
    } else {
      alert(`拒绝邀请失败: ${response.error || '未知错误'}`)
    }
  } catch (error) {
    console.error('拒绝邀请失败:', error)
    alert('拒绝邀请失败')
  }
}
</script>
