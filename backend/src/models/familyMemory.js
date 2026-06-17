import { getStore, persist } from './store.js';
import { generateId, now } from '../utils/helpers.js';

export function createFamilyMemory(memoryData) {
  const store = getStore();
  const memoryId = generateId('memory');
  const memory = {
    id: memoryId,
    userId: memoryData.userId || 'default_user',
    familyId: memoryData.familyId || null,
    memberId: memoryData.memberId || null,
    title: memoryData.title || '',
    description: memoryData.description || '',
    content: memoryData.content || '',
    date: memoryData.date || null,
    location: memoryData.location || '',
    type: memoryData.type || 'photo',
    photoIds: memoryData.photoIds || [],
    beforeAfterPairs: memoryData.beforeAfterPairs || [],
    sourceTaskId: memoryData.sourceTaskId || null,
    tags: memoryData.tags || [],
    metadata: memoryData.metadata || {},
    isPublished: memoryData.isPublished !== false,
    createdAt: now(),
    updatedAt: now(),
  };

  store.familyMemories[memoryId] = memory;
  persist();
  return memory;
}

export function getFamilyMemory(memoryId) {
  const store = getStore();
  return store.familyMemories[memoryId] || null;
}

export function getFamilyMemories(familyId, options = {}) {
  const store = getStore();
  const { limit = 50, offset = 0, type, memberId } = options;

  let memories = Object.values(store.familyMemories).filter((m) => m.familyId === familyId);

  if (type) {
    memories = memories.filter((m) => m.type === type);
  }
  if (memberId) {
    memories = memories.filter((m) => m.memberId === memberId);
  }

  memories.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  return {
    total: memories.length,
    items: memories.slice(offset, offset + limit),
  };
}

export function updateFamilyMemory(memoryId, updates) {
  const store = getStore();
  const memory = store.familyMemories[memoryId];
  if (!memory) return null;

  const updated = { ...memory, ...updates, updatedAt: now() };
  store.familyMemories[memoryId] = updated;
  persist();
  return updated;
}

export function deleteFamilyMemory(memoryId) {
  const store = getStore();
  if (!store.familyMemories[memoryId]) return false;
  delete store.familyMemories[memoryId];
  persist();
  return true;
}

export function createRepairMemory(task, beforeAfterPairs) {
  return createFamilyMemory({
    userId: task.userId,
    familyId: task.familyId,
    memberId: task.memberId,
    title: `老照片修复 - ${task.title || '批量修复'}`,
    description: `通过AI技术修复的老照片合集，共 ${beforeAfterPairs.length} 张`,
    type: 'repair',
    sourceTaskId: task.id,
    beforeAfterPairs,
    photoIds: beforeAfterPairs.flatMap((pair) => [pair.beforeId, pair.afterId]),
    tags: ['老照片修复', 'AI修复'],
  });
}
