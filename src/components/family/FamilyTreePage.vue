<template>
  <div class="min-h-screen paper-texture">
    <header class="sticky top-0 z-50 glass-warm border-b border-[#E8D5C4]">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button @click="$emit('back')" class="w-10 h-10 rounded-full bg-white/80 flex items-center justify-center shadow-sm hover:shadow-md transition-shadow">
            <Icon icon="material-symbols:arrow-back" class="text-gray-600 text-lg" />
          </button>
          <div>
            <h1 class="text-2xl font-bold text-[#5C4A3A] font-serif tracking-wider">家族谱系</h1>
            <p class="text-xs text-gray-500 tracking-[0.15em] uppercase font-medium">Family Tree</p>
          </div>
        </div>

        <div class="flex items-center space-x-3">
          <button @click="showAddMemberModal = true"
            class="px-4 py-2 bg-[#8B6F4E] text-white rounded-xl text-sm font-medium shadow-md hover:shadow-lg transition-shadow flex items-center space-x-2">
            <Icon icon="material-symbols:person-add" class="text-lg" />
            <span>添加成员</span>
          </button>
          <button @click="showAddRelModal = true"
            class="px-4 py-2 bg-white text-[#8B6F4E] border border-[#E8D5C4] rounded-xl text-sm font-medium shadow-soft hover:shadow-md transition-shadow flex items-center space-x-2">
            <Icon icon="material-symbols:link" class="text-lg" />
            <span>添加关系</span>
          </button>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto px-6 py-8">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="text-center">
          <Icon icon="solar:tree-bold-duotone" class="text-6xl text-[#E8D5C4] animate-pulse mb-4" />
          <p class="text-gray-500">加载家族树中...</p>
        </div>
      </div>

      <div v-else-if="treeMembers.length === 0" class="flex items-center justify-center py-20">
        <div class="text-center max-w-md">
          <Icon icon="solar:tree-bold-duotone" class="text-8xl text-[#E8D5C4] mb-6" />
          <h3 class="text-xl font-bold text-[#5C4A3A] font-serif mb-3">尚无家族成员</h3>
          <p class="text-gray-500 mb-6">开始添加家族成员，构建你的家族谱系树</p>
          <button @click="showAddMemberModal = true"
            class="px-6 py-3 bg-[#8B6F4E] text-white rounded-xl font-medium shadow-md hover:shadow-lg transition-shadow">
            添加第一位成员
          </button>
        </div>
      </div>

      <div v-else class="flex gap-6">
        <div class="flex-1 min-w-0">
          <div class="bg-white rounded-2xl shadow-soft border border-stone-100 p-6 overflow-x-auto">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">谱系图</h3>
              <div class="flex items-center space-x-4 text-xs text-gray-400">
                <span class="flex items-center"><span class="w-3 h-3 rounded-full bg-[#8B6F4E] mr-1.5"></span>父辈</span>
                <span class="flex items-center"><span class="w-3 h-3 rounded-full bg-[#D4A574] mr-1.5"></span>同辈</span>
                <span class="flex items-center"><span class="w-3 h-3 rounded-full bg-rose-400 mr-1.5"></span>配偶</span>
              </div>
            </div>

            <div class="tree-container">
              <div v-for="rootId in treeData?.rootMembers" :key="rootId" class="generation-group">
                <TreeNode
                  :member-id="rootId"
                  :member-map="memberMap"
                  :children-map="treeData?.childrenOf || {}"
                  :spouse-map="treeData?.spouseOf || {}"
                  :sibling-map="treeData?.siblingOf || {}"
                  :selected-id="selectedMemberId"
                  @select="selectMember"
                />
              </div>

              <div v-if="orphanMembers.length > 0" class="mt-8 pt-6 border-t border-dashed border-[#E8D5C4]">
                <p class="text-xs text-gray-400 mb-3 font-medium">未关联成员</p>
                <div class="flex flex-wrap gap-3">
                  <div v-for="member in orphanMembers" :key="member.id"
                    @click="selectMember(member.id)"
                    class="flex items-center space-x-2 px-3 py-2 bg-[#FAF7F2] rounded-xl border border-[#E8D5C4] cursor-pointer hover:shadow-soft transition-shadow"
                    :class="{ 'ring-2 ring-[#8B6F4E]': selectedMemberId === member.id }">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] flex items-center justify-center text-white text-xs font-bold overflow-hidden">
                      <img v-if="member.avatar" :src="member.avatar" class="w-full h-full object-cover" :alt="member.name" />
                      <span v-else>{{ member.name.charAt(0) }}</span>
                    </div>
                    <span class="text-sm font-medium text-[#5C4A3A]">{{ member.name }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="selectedMember" class="w-96 flex-shrink-0">
          <div class="bg-white rounded-2xl shadow-soft border border-stone-100 overflow-hidden sticky top-24">
            <div class="relative bg-gradient-to-br from-[#8B6F4E] to-[#6B5342] p-6 text-white">
              <button @click="selectedMemberId = null"
                class="absolute top-3 right-3 w-8 h-8 rounded-full bg-white/20 flex items-center justify-center hover:bg-white/30 transition-colors">
                <Icon icon="material-symbols:close" class="text-white text-sm" />
              </button>
              <div class="flex items-center space-x-4">
                <div class="w-20 h-20 rounded-full bg-white/20 p-0.5 flex-shrink-0">
                  <div class="w-full h-full rounded-full bg-white/10 overflow-hidden">
                    <img v-if="selectedMember.avatar" :src="selectedMember.avatar" class="w-full h-full object-cover" :alt="selectedMember.name" />
                    <div v-else class="w-full h-full flex items-center justify-center text-2xl font-serif font-bold">
                      {{ selectedMember.name.charAt(0) }}
                    </div>
                  </div>
                </div>
                <div>
                  <h3 class="text-xl font-bold font-serif">{{ selectedMember.name }}</h3>
                  <p class="text-sm text-white/70 mt-1">
                    {{ formatLifeYears(selectedMember) }}
                  </p>
                  <p v-if="selectedMember.gender" class="text-xs text-white/50 mt-1">
                    {{ selectedMember.gender === 'male' ? '男' : selectedMember.gender === 'female' ? '女' : '' }}
                  </p>
                </div>
              </div>
            </div>

            <div class="p-6">
              <div v-if="selectedMember.bio" class="mb-6">
                <h4 class="text-sm font-bold text-[#5C4A3A] mb-2">生平简介</h4>
                <p class="text-sm text-gray-600 leading-relaxed">{{ selectedMember.bio }}</p>
              </div>

              <div class="mb-6">
                <h4 class="text-sm font-bold text-[#5C4A3A] mb-3">家族关系</h4>
                <div v-if="memberRelationships.length === 0" class="text-sm text-gray-400">暂无关系记录</div>
                <div v-else class="space-y-2">
                  <div v-for="rel in memberRelationships" :key="rel.id"
                    class="flex items-center justify-between px-3 py-2 bg-[#FAF7F2] rounded-lg">
                    <div class="flex items-center space-x-2">
                      <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                        :class="relationshipBadgeClass(rel)">
                        {{ relationshipLabel(rel) }}
                      </span>
                      <span class="text-sm text-[#5C4A3A]">{{ getRelatedMemberName(rel) }}</span>
                    </div>
                    <button @click="deleteRelationship(rel.id)"
                      class="text-gray-300 hover:text-red-400 transition-colors">
                      <Icon icon="material-symbols:close" class="text-sm" />
                    </button>
                  </div>
                </div>
              </div>

              <div class="mb-6">
                <h4 class="text-sm font-bold text-[#5C4A3A] mb-3">关联记忆</h4>
                <div v-if="memberMemories.length === 0" class="text-sm text-gray-400">暂无记忆记录</div>
                <div v-else class="space-y-2">
                  <div v-for="memory in memberMemories" :key="memory.id"
                    class="px-3 py-2 bg-[#FAF7F2] rounded-lg cursor-pointer hover:shadow-soft transition-shadow">
                    <p class="text-sm font-medium text-[#5C4A3A]">{{ memory.title }}</p>
                    <p class="text-xs text-gray-400 mt-0.5">{{ memory.date || formatDate(memory.createdAt) }}</p>
                  </div>
                </div>
              </div>

              <div class="mb-6">
                <h4 class="text-sm font-bold text-[#5C4A3A] mb-3">关联照片</h4>
                <div v-if="memberPhotos.length === 0" class="text-sm text-gray-400">暂无照片</div>
                <div v-else class="grid grid-cols-3 gap-2">
                  <div v-for="photo in memberPhotos.slice(0, 6)" :key="photo.id"
                    class="aspect-square rounded-lg overflow-hidden bg-gray-100">
                    <img :src="photo.thumbnailUrl || photo.imageUrl" class="w-full h-full object-cover" :alt="photo.title" />
                  </div>
                </div>
              </div>

              <div class="flex items-center space-x-2 pt-4 border-t border-[#E8D5C4]">
                <button @click="editMember"
                  class="flex-1 px-4 py-2 bg-[#8B6F4E] text-white rounded-xl text-sm font-medium shadow-sm hover:shadow-md transition-shadow">
                  编辑信息
                </button>
                <button @click="confirmDeleteMember"
                  class="px-4 py-2 bg-white text-red-500 border border-red-200 rounded-xl text-sm font-medium hover:bg-red-50 transition-colors">
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <teleport to="body">
      <div v-if="showAddMemberModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="showAddMemberModal = false">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
          <div class="px-6 py-4 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white flex items-center justify-between">
            <h3 class="font-bold font-serif">添加家族成员</h3>
            <button @click="showAddMemberModal = false" class="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
              <Icon icon="material-symbols:close" class="text-white text-sm" />
            </button>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-[#5C4A3A] mb-1">姓名 *</label>
              <input v-model="newMember.name" type="text" placeholder="请输入姓名"
                class="w-full px-4 py-2 border border-[#E8D5C4] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30" />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-[#5C4A3A] mb-1">出生日期</label>
                <input v-model="newMember.birthDate" type="date"
                  class="w-full px-4 py-2 border border-[#E8D5C4] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30" />
              </div>
              <div>
                <label class="block text-sm font-medium text-[#5C4A3A] mb-1">逝世日期</label>
                <input v-model="newMember.deathDate" type="date"
                  class="w-full px-4 py-2 border border-[#E8D5C4] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30" />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-[#5C4A3A] mb-1">性别</label>
                <select v-model="newMember.gender"
                  class="w-full px-4 py-2 border border-[#E8D5C4] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30">
                  <option value="">请选择</option>
                  <option value="male">男</option>
                  <option value="female">女</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-[#5C4A3A] mb-1">世代</label>
                <input v-model.number="newMember.generation" type="number" placeholder="如: 1, 2, 3"
                  class="w-full px-4 py-2 border border-[#E8D5C4] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30" />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#5C4A3A] mb-1">头像URL</label>
              <input v-model="newMember.avatar" type="text" placeholder="头像图片地址"
                class="w-full px-4 py-2 border border-[#E8D5C4] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30" />
            </div>
            <div>
              <label class="block text-sm font-medium text-[#5C4A3A] mb-1">生平简介</label>
              <textarea v-model="newMember.bio" rows="3" placeholder="简单介绍这位家族成员..."
                class="w-full px-4 py-2 border border-[#E8D5C4] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30 resize-none"></textarea>
            </div>
            <div v-if="formError" class="px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
              {{ formError }}
            </div>
            <div class="flex items-center space-x-3 pt-2">
              <button @click="showAddMemberModal = false"
                class="flex-1 px-4 py-2 bg-white border border-[#E8D5C4] text-[#5C4A3A] rounded-xl text-sm font-medium hover:bg-[#FAF7F2] transition-colors">
                取消
              </button>
              <button @click="handleAddMember"
                class="flex-1 px-4 py-2 bg-[#8B6F4E] text-white rounded-xl text-sm font-medium shadow-md hover:shadow-lg transition-shadow">
                确认添加
              </button>
            </div>
          </div>
        </div>
      </div>
    </teleport>

    <teleport to="body">
      <div v-if="showAddRelModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="showAddRelModal = false">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
          <div class="px-6 py-4 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white flex items-center justify-between">
            <h3 class="font-bold font-serif">添加关系</h3>
            <button @click="showAddRelModal = false" class="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
              <Icon icon="material-symbols:close" class="text-white text-sm" />
            </button>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-[#5C4A3A] mb-1">成员A *</label>
              <select v-model="newRel.fromMemberId"
                class="w-full px-4 py-2 border border-[#E8D5C4] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30">
                <option value="">请选择</option>
                <option v-for="m in treeMembers" :key="m.id" :value="m.id">{{ m.name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#5C4A3A] mb-1">关系类型 *</label>
              <select v-model="newRel.type"
                class="w-full px-4 py-2 border border-[#E8D5C4] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30">
                <option value="">请选择</option>
                <option value="parent_child">父子/母子 (A是B的父/母辈)</option>
                <option value="sibling">兄弟姐妹</option>
                <option value="spouse">配偶</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#5C4A3A] mb-1">成员B *</label>
              <select v-model="newRel.toMemberId"
                class="w-full px-4 py-2 border border-[#E8D5C4] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30">
                <option value="">请选择</option>
                <option v-for="m in treeMembers" :key="m.id" :value="m.id">{{ m.name }}</option>
              </select>
            </div>
            <div v-if="relFormError" class="px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
              {{ relFormError }}
            </div>
            <div class="flex items-center space-x-3 pt-2">
              <button @click="showAddRelModal = false"
                class="flex-1 px-4 py-2 bg-white border border-[#E8D5C4] text-[#5C4A3A] rounded-xl text-sm font-medium hover:bg-[#FAF7F2] transition-colors">
                取消
              </button>
              <button @click="handleAddRelationship"
                class="flex-1 px-4 py-2 bg-[#8B6F4E] text-white rounded-xl text-sm font-medium shadow-md hover:shadow-lg transition-shadow">
                确认添加
              </button>
            </div>
          </div>
        </div>
      </div>
    </teleport>

    <teleport to="body">
      <div v-if="showEditModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="showEditModal = false">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
          <div class="px-6 py-4 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white flex items-center justify-between">
            <h3 class="font-bold font-serif">编辑成员信息</h3>
            <button @click="showEditModal = false" class="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
              <Icon icon="material-symbols:close" class="text-white text-sm" />
            </button>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-[#5C4A3A] mb-1">姓名 *</label>
              <input v-model="editForm.name" type="text"
                class="w-full px-4 py-2 border border-[#E8D5C4] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30" />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-[#5C4A3A] mb-1">出生日期</label>
                <input v-model="editForm.birthDate" type="date"
                  class="w-full px-4 py-2 border border-[#E8D5C4] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30" />
              </div>
              <div>
                <label class="block text-sm font-medium text-[#5C4A3A] mb-1">逝世日期</label>
                <input v-model="editForm.deathDate" type="date"
                  class="w-full px-4 py-2 border border-[#E8D5C4] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30" />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-[#5C4A3A] mb-1">性别</label>
                <select v-model="editForm.gender"
                  class="w-full px-4 py-2 border border-[#E8D5C4] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30">
                  <option value="">请选择</option>
                  <option value="male">男</option>
                  <option value="female">女</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-[#5C4A3A] mb-1">世代</label>
                <input v-model.number="editForm.generation" type="number"
                  class="w-full px-4 py-2 border border-[#E8D5C4] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30" />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#5C4A3A] mb-1">头像URL</label>
              <input v-model="editForm.avatar" type="text"
                class="w-full px-4 py-2 border border-[#E8D5C4] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30" />
            </div>
            <div>
              <label class="block text-sm font-medium text-[#5C4A3A] mb-1">生平简介</label>
              <textarea v-model="editForm.bio" rows="3"
                class="w-full px-4 py-2 border border-[#E8D5C4] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30 resize-none"></textarea>
            </div>
            <div v-if="formError" class="px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
              {{ formError }}
            </div>
            <div class="flex items-center space-x-3 pt-2">
              <button @click="showEditModal = false"
                class="flex-1 px-4 py-2 bg-white border border-[#E8D5C4] text-[#5C4A3A] rounded-xl text-sm font-medium hover:bg-[#FAF7F2] transition-colors">
                取消
              </button>
              <button @click="handleEditMember"
                class="flex-1 px-4 py-2 bg-[#8B6F4E] text-white rounded-xl text-sm font-medium shadow-md hover:shadow-lg transition-shadow">
                保存修改
              </button>
            </div>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Icon } from '@iconify/vue'
import { familyTreeApi, familyMemoryApi, galleryApi } from '../../api'
import type { FamilyMember, FamilyRelationship, FamilyTreeData } from '../../types/task'

defineEmits(['back'])

const FAMILY_ID = 'default_family'
const loading = ref(true)
const treeData = ref<FamilyTreeData | null>(null)
const selectedMemberId = ref<string | null>(null)
const memberMemories = ref<any[]>([])
const memberPhotos = ref<any[]>([])
const memberRelationships = ref<FamilyRelationship[]>([])
const formError = ref('')
const relFormError = ref('')

const showAddMemberModal = ref(false)
const showAddRelModal = ref(false)
const showEditModal = ref(false)

const newMember = ref({
  name: '',
  birthDate: '',
  deathDate: '',
  gender: '',
  generation: null as number | null,
  avatar: '',
  bio: '',
})

const newRel = ref({
  fromMemberId: '',
  toMemberId: '',
  type: '',
})

const editForm = ref({
  name: '',
  birthDate: '',
  deathDate: '',
  gender: '',
  generation: null as number | null,
  avatar: '',
  bio: '',
})

const treeMembers = computed(() => treeData.value?.members || [])
const memberMap = computed(() => {
  const map: Record<string, FamilyMember> = {}
  treeMembers.value.forEach((m) => { map[m.id] = m })
  return map
})

const selectedMember = computed(() => {
  if (!selectedMemberId.value) return null
  return memberMap.value[selectedMemberId.value] || null
})

const orphanMembers = computed(() => {
  if (!treeData.value) return []
  const relatedIds = new Set<string>()
  treeData.value.relationships.forEach((rel) => {
    relatedIds.add(rel.fromMemberId)
    relatedIds.add(rel.toMemberId)
  })
  return treeMembers.value.filter((m) => !relatedIds.has(m.id))
})

function selectMember(memberId: string) {
  selectedMemberId.value = memberId
}

watch(selectedMemberId, async (newId) => {
  if (!newId) {
    memberRelationships.value = []
    memberMemories.value = []
    memberPhotos.value = []
    return
  }
  try {
    const [relRes, memRes, photoRes] = await Promise.all([
      familyTreeApi.getMemberRelationships(newId),
      familyMemoryApi.getByFamily(FAMILY_ID, { memberId: newId, limit: 10 }),
      galleryApi.getByMember(newId, { limit: 6 }),
    ])
    if (relRes.success) memberRelationships.value = relRes.data
    if (memRes.success) memberMemories.value = memRes.data.items
    if (photoRes.success) memberPhotos.value = photoRes.data.items
  } catch (err) {
    console.error('Load member details error:', err)
  }
})

function formatLifeYears(member: FamilyMember): string {
  if (!member.birthDate && !member.deathDate) return ''
  const birth = member.birthDate ? new Date(member.birthDate).getFullYear() : '?'
  const death = member.deathDate ? new Date(member.deathDate).getFullYear() : ''
  if (death) return `${birth} - ${death}`
  return `${birth} - 今`
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function relationshipLabel(rel: FamilyRelationship): string {
  const isSelectedFrom = rel.fromMemberId === selectedMemberId.value
  if (rel.type === 'parent_child') {
    return isSelectedFrom ? '子女' : '父/母'
  }
  if (rel.type === 'sibling') return '兄弟姐妹'
  if (rel.type === 'spouse') return '配偶'
  return rel.type
}

function relationshipBadgeClass(rel: FamilyRelationship): string {
  if (rel.type === 'parent_child') return 'bg-[#8B6F4E]/10 text-[#8B6F4E]'
  if (rel.type === 'sibling') return 'bg-[#D4A574]/20 text-[#D4A574]'
  if (rel.type === 'spouse') return 'bg-rose-100 text-rose-500'
  return 'bg-gray-100 text-gray-500'
}

function getRelatedMemberName(rel: FamilyRelationship): string {
  const isSelectedFrom = rel.fromMemberId === selectedMemberId.value
  const relatedId = isSelectedFrom ? rel.toMemberId : rel.fromMemberId
  return memberMap.value[relatedId]?.name || '未知成员'
}

async function loadTree() {
  loading.value = true
  try {
    const response = await familyTreeApi.getTree(FAMILY_ID)
    if (response.success) {
      treeData.value = response.data
    }
  } catch (err) {
    console.error('Load family tree error:', err)
  } finally {
    loading.value = false
  }
}

async function handleAddMember() {
  formError.value = ''
  if (!newMember.value.name.trim()) {
    formError.value = '请输入姓名'
    return
  }
  try {
    const response = await familyTreeApi.createMember({
      ...newMember.value,
      familyId: FAMILY_ID,
    })
    if (response.success) {
      showAddMemberModal.value = false
      newMember.value = { name: '', birthDate: '', deathDate: '', gender: '', generation: null, avatar: '', bio: '' }
      await loadTree()
    }
  } catch (err: any) {
    formError.value = err.message || '添加失败'
  }
}

async function handleAddRelationship() {
  relFormError.value = ''
  if (!newRel.value.fromMemberId || !newRel.value.toMemberId || !newRel.value.type) {
    relFormError.value = '请填写完整的关系信息'
    return
  }
  if (newRel.value.fromMemberId === newRel.value.toMemberId) {
    relFormError.value = '不能与自己建立关系'
    return
  }
  try {
    const response = await familyTreeApi.createRelationship({
      fromMemberId: newRel.value.fromMemberId,
      toMemberId: newRel.value.toMemberId,
      type: newRel.value.type as any,
      familyId: FAMILY_ID,
    })
    if (response.success) {
      showAddRelModal.value = false
      newRel.value = { fromMemberId: '', toMemberId: '', type: '' }
      await loadTree()
    }
  } catch (err: any) {
    const response = err?.response?.data || err
    relFormError.value = response?.error?.message || response?.message || '添加关系失败'
  }
}

function editMember() {
  if (!selectedMember.value) return
  editForm.value = {
    name: selectedMember.value.name,
    birthDate: selectedMember.value.birthDate || '',
    deathDate: selectedMember.value.deathDate || '',
    gender: selectedMember.value.gender || '',
    generation: selectedMember.value.generation,
    avatar: selectedMember.value.avatar || '',
    bio: selectedMember.value.bio || '',
  }
  showEditModal.value = true
}

async function handleEditMember() {
  formError.value = ''
  if (!editForm.value.name.trim()) {
    formError.value = '请输入姓名'
    return
  }
  if (!selectedMemberId.value) return
  try {
    const response = await familyTreeApi.updateMember(selectedMemberId.value, {
      ...editForm.value,
      birthDate: editForm.value.birthDate || null,
      deathDate: editForm.value.deathDate || null,
      gender: editForm.value.gender || null,
      generation: editForm.value.generation,
      avatar: editForm.value.avatar || '',
      bio: editForm.value.bio || '',
    })
    if (response.success) {
      showEditModal.value = false
      await loadTree()
    }
  } catch (err: any) {
    formError.value = err.message || '编辑失败'
  }
}

async function deleteRelationship(relId: string) {
  try {
    await familyTreeApi.deleteRelationship(relId)
    await loadTree()
    if (selectedMemberId.value) {
      const relRes = await familyTreeApi.getMemberRelationships(selectedMemberId.value)
      if (relRes.success) memberRelationships.value = relRes.data
    }
  } catch (err) {
    console.error('Delete relationship error:', err)
  }
}

async function confirmDeleteMember() {
  if (!selectedMemberId.value) return
  if (!confirm('确定删除此成员？该成员的所有关系也将被删除。')) return
  try {
    await familyTreeApi.deleteMember(selectedMemberId.value)
    selectedMemberId.value = null
    await loadTree()
  } catch (err) {
    console.error('Delete member error:', err)
  }
}

onMounted(() => {
  loadTree()
})
</script>

<script lang="ts">
import { defineComponent, h, PropType } from 'vue'
import { Icon } from '@iconify/vue'
import type { FamilyMember } from '../../types/task'

const TreeNode = defineComponent({
  name: 'TreeNode',
  props: {
    memberId: { type: String, required: true },
    memberMap: { type: Object as PropType<Record<string, FamilyMember>>, required: true },
    childrenMap: { type: Object as PropType<Record<string, string[]>>, default: () => ({}) },
    spouseMap: { type: Object as PropType<Record<string, string[]>>, default: () => ({}) },
    siblingMap: { type: Object as PropType<Record<string, string[]>>, default: () => ({}) },
    selectedId: { type: String, default: null },
    depth: { type: Number, default: 0 },
  },
  emits: ['select'],
  setup(props, { emit }) {
    return () => {
      const member = props.memberMap[props.memberId]
      if (!member) return null

      const children = props.childrenMap[props.memberId] || []
      const spouses = props.spouseMap[props.memberId] || []

      const isSelected = props.selectedId === props.memberId

      return h('div', { class: 'tree-node' }, [
        h('div', { class: 'node-content flex items-start' }, [
          h('div', { class: 'node-unit flex flex-col items-center' }, [
            h('div', {
              class: [
                'member-card flex items-center space-x-3 px-4 py-3 rounded-xl cursor-pointer transition-all',
                isSelected
                  ? 'bg-[#8B6F4E] text-white shadow-glow'
                  : 'bg-white border border-stone-100 shadow-soft hover:shadow-md hover-lift',
              ],
              onClick: () => emit('select', props.memberId),
            }, [
              h('div', {
                class: [
                  'w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center overflow-hidden',
                  isSelected ? 'bg-white/20' : 'bg-gradient-to-br from-[#E8D5C4] to-[#D4A574]',
                ],
              }, [
                member.avatar
                  ? h('img', { src: member.avatar, class: 'w-full h-full object-cover', alt: member.name })
                  : h('span', {
                      class: ['text-sm font-bold', isSelected ? 'text-white' : 'text-white'],
                    }, member.name.charAt(0)),
              ]),
              h('div', {}, [
                h('p', {
                  class: ['text-sm font-bold', isSelected ? 'text-white' : 'text-[#5C4A3A]'],
                }, member.name),
                h('p', {
                  class: ['text-xs', isSelected ? 'text-white/70' : 'text-gray-400'],
                }, formatLife(member)),
              ]),
            ]),

            spouses.length > 0
              ? h('div', { class: 'flex items-center mt-2 space-x-1' },
                  spouses.map((spouseId: string) => {
                    const spouse = props.memberMap[spouseId]
                    if (!spouse) return null
                    const isSpouseSelected = props.selectedId === spouseId
                    return h('div', {
                      class: [
                        'flex items-center space-x-2 px-3 py-1.5 rounded-lg cursor-pointer text-xs transition-all',
                        isSpouseSelected
                          ? 'bg-rose-400 text-white'
                          : 'bg-rose-50 border border-rose-200 text-rose-500 hover:bg-rose-100',
                      ],
                      onClick: () => emit('select', spouseId),
                    }, [
                      h('span', { class: 'text-[10px]' }, '♡'),
                      h('span', { class: 'font-medium' }, spouse.name),
                    ])
                  })
                )
              : null,
          ]),

          children.length > 0
            ? h('div', { class: 'ml-8 pl-6 border-l-2 border-[#E8D5C4] relative' }, [
                h('div', {
                  class: 'absolute left-0 top-4 w-6 h-px bg-[#E8D5C4]',
                  style: { transform: 'translateX(-1.5rem)' },
                }),
                h('div', { class: 'space-y-4 mt-2' },
                  children.map((childId: string) =>
                    h(TreeNode as any, {
                      key: childId,
                      memberId: childId,
                      memberMap: props.memberMap,
                      childrenMap: props.childrenMap,
                      spouseMap: props.spouseMap,
                      siblingMap: props.siblingMap,
                      selectedId: props.selectedId,
                      depth: props.depth + 1,
                      onSelect: (id: string) => emit('select', id),
                    })
                  )
                ),
              ])
            : null,
        ]),
      ])
    }
  },
})

function formatLife(member: FamilyMember): string {
  if (!member.birthDate && !member.deathDate) return ''
  const birth = member.birthDate ? new Date(member.birthDate).getFullYear() : '?'
  const death = member.deathDate ? new Date(member.deathDate).getFullYear() : ''
  if (death) return `${birth}-${death}`
  return `${birth}-今`
}

export { TreeNode }
export default {}
</script>

<style scoped>
.tree-container {
  min-width: fit-content;
}

.tree-node {
  position: relative;
}

.generation-group + .generation-group {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px dashed #E8D5C4;
}
</style>
