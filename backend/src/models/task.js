import { getStore, persist } from './store.js';
import { generateId, now } from '../utils/helpers.js';
import { TASK_STATUS } from '../constants.js';

export function createTask(taskData) {
  const store = getStore();
  const taskId = generateId('task');
  const task = {
    id: taskId,
    userId: taskData.userId || 'default_user',
    familyId: taskData.familyId || null,
    memberId: taskData.memberId || null,
    type: taskData.type,
    title: taskData.title || '',
    description: taskData.description || '',
    status: TASK_STATUS.PENDING,
    totalItems: taskData.totalItems || 0,
    completedItems: 0,
    failedItems: 0,
    progress: 0,
    priority: taskData.priority || 0,
    metadata: taskData.metadata || {},
    result: null,
    error: null,
    createdAt: now(),
    updatedAt: now(),
    startedAt: null,
    completedAt: null,
    cancelledAt: null,
  };

  store.tasks[taskId] = task;
  persist();
  return task;
}

export function getTask(taskId) {
  const store = getStore();
  return store.tasks[taskId] || null;
}

export function getTasksByUser(userId, options = {}) {
  const store = getStore();
  const { limit = 50, offset = 0, status, type } = options;

  let tasks = Object.values(store.tasks).filter((t) => t.userId === userId);

  if (status) {
    tasks = tasks.filter((t) => t.status === status);
  }
  if (type) {
    tasks = tasks.filter((t) => t.type === type);
  }

  tasks.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  return {
    total: tasks.length,
    items: tasks.slice(offset, offset + limit),
  };
}

export function updateTask(taskId, updates) {
  const store = getStore();
  const task = store.tasks[taskId];
  if (!task) return null;

  const updated = { ...task, ...updates, updatedAt: now() };
  store.tasks[taskId] = updated;
  persist();
  return updated;
}

export function updateTaskProgress(taskId) {
  const store = getStore();
  const task = store.tasks[taskId];
  if (!task) return null;

  const items = Object.values(store.taskItems).filter((item) => item.taskId === taskId);
  const completed = items.filter((item) => item.status === TASK_STATUS.COMPLETED).length;
  const failed = items.filter((item) => item.status === TASK_STATUS.FAILED).length;
  const total = items.length || task.totalItems || 0;
  const progress = total > 0 ? Math.round(((completed + failed) / total) * 100) : 0;

  const updated = {
    ...task,
    completedItems: completed,
    failedItems: failed,
    totalItems: total,
    progress,
    updatedAt: now(),
  };

  store.tasks[taskId] = updated;
  persist();
  return updated;
}

export function deleteTask(taskId) {
  const store = getStore();
  if (!store.tasks[taskId]) return false;
  delete store.tasks[taskId];

  const items = Object.values(store.taskItems).filter((item) => item.taskId === taskId);
  items.forEach((item) => delete store.taskItems[item.id]);

  persist();
  return true;
}

export function countTasksByStatus(userId, status) {
  const store = getStore();
  return Object.values(store.tasks).filter((t) => t.userId === userId && t.status === status).length;
}

export function countPendingTasks(userId) {
  const store = getStore();
  return Object.values(store.tasks).filter(
    (t) => t.userId === userId && (t.status === TASK_STATUS.PENDING || t.status === TASK_STATUS.PROCESSING || t.status === TASK_STATUS.RETRYING)
  ).length;
}
