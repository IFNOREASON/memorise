import { getStore, persist } from './store.js';
import { generateId, now } from '../utils/helpers.js';
import { TASK_STATUS } from '../constants.js';

export function createTaskItem(itemData) {
  const store = getStore();
  const itemId = generateId('item');
  const item = {
    id: itemId,
    taskId: itemData.taskId,
    userId: itemData.userId || 'default_user',
    type: itemData.type,
    index: itemData.index || 0,
    title: itemData.title || '',
    inputData: itemData.inputData || {},
    outputData: null,
    status: TASK_STATUS.PENDING,
    error: null,
    errorCategory: null,
    retryCount: 0,
    maxRetries: itemData.maxRetries || 5,
    nextRetryAt: null,
    metadata: itemData.metadata || {},
    createdAt: now(),
    updatedAt: now(),
    startedAt: null,
    completedAt: null,
  };

  store.taskItems[itemId] = item;
  persist();
  return item;
}

export function bulkCreateTaskItems(itemsData) {
  return itemsData.map((itemData, index) =>
    createTaskItem({
      ...itemData,
      index: itemData.index ?? index,
    })
  );
}

export function getTaskItem(itemId) {
  const store = getStore();
  return store.taskItems[itemId] || null;
}

export function getTaskItems(taskId, options = {}) {
  const store = getStore();
  const { limit = 100, offset = 0, status } = options;

  let items = Object.values(store.taskItems).filter((item) => item.taskId === taskId);

  if (status) {
    items = items.filter((item) => item.status === status);
  }

  items.sort((a, b) => a.index - b.index);
  return {
    total: items.length,
    items: items.slice(offset, offset + limit),
  };
}

export function updateTaskItem(itemId, updates) {
  const store = getStore();
  const item = store.taskItems[itemId];
  if (!item) return null;

  const updated = { ...item, ...updates, updatedAt: now() };
  store.taskItems[itemId] = updated;
  persist();
  return updated;
}

export function updateTaskItemStatus(itemId, status, extra = {}) {
  const updates = { status, ...extra };

  if (status === TASK_STATUS.PROCESSING && !extra.startedAt) {
    updates.startedAt = now();
  }
  if (
    (status === TASK_STATUS.COMPLETED || status === TASK_STATUS.FAILED) &&
    !extra.completedAt
  ) {
    updates.completedAt = now();
  }

  return updateTaskItem(itemId, updates);
}

export function getPendingItemsByTask(taskId) {
  const store = getStore();
  return Object.values(store.taskItems).filter(
    (item) => item.taskId === taskId && item.status === TASK_STATUS.PENDING
  );
}

export function getFailedItemsByTask(taskId) {
  const store = getStore();
  return Object.values(store.taskItems).filter(
    (item) => item.taskId === taskId && item.status === TASK_STATUS.FAILED
  );
}

export function getRetryableItems() {
  const store = getStore();
  const nowTime = Date.now();
  return Object.values(store.taskItems).filter(
    (item) =>
      item.status === TASK_STATUS.RETRYING &&
      item.nextRetryAt &&
      new Date(item.nextRetryAt).getTime() <= nowTime
  );
}

export function deleteTaskItem(itemId) {
  const store = getStore();
  if (!store.taskItems[itemId]) return false;
  delete store.taskItems[itemId];
  persist();
  return true;
}
