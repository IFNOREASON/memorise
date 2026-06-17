import { TASK_STATUS, TASK_QUEUE_CONFIG, ERROR_CATEGORY } from '../constants.js';
import { calculateRetryDelay, categorizeError } from '../utils/helpers.js';
import {
  updateTaskItemStatus,
  updateTaskItem,
  getTaskItem,
  getRetryableItems,
} from '../models/taskItem.js';
import { updateTask, getTask, updateTaskProgress } from '../models/task.js';
import { createTaskLog } from '../models/taskLog.js';
import { getStore } from '../models/store.js';
import { broadcastTaskUpdate, broadcastTaskItemUpdate } from './webSocketService.js';

const processingItems = new Set();
const userProcessingCount = new Map();
const taskHandlers = new Map();
let isRunning = false;
let queueLoopTimer = null;
let retryLoopTimer = null;
let onTaskCompleteCallback = null;

export function registerTaskHandler(taskType, handler) {
  taskHandlers.set(taskType, handler);
  console.log(`Registered task handler for type: ${taskType}`);
}

export function unregisterTaskHandler(taskType) {
  taskHandlers.delete(taskType);
}

export function getTaskHandler(taskType) {
  return taskHandlers.get(taskType) || null;
}

export function startQueue() {
  if (isRunning) return;
  isRunning = true;

  queueLoopTimer = setInterval(processQueue, 500);
  retryLoopTimer = setInterval(processRetries, 1000);

  console.log('Task queue started');
}

export function stopQueue() {
  isRunning = false;
  if (queueLoopTimer) {
    clearInterval(queueLoopTimer);
    queueLoopTimer = null;
  }
  if (retryLoopTimer) {
    clearInterval(retryLoopTimer);
    retryLoopTimer = null;
  }
  console.log('Task queue stopped');
}

async function processQueue() {
  if (!isRunning) return;

  const pendingItems = getPendingItemsForProcessing();

  for (const item of pendingItems) {
    if (!canProcessItem(item)) continue;
    processItem(item);
  }
}

function getPendingItemsForProcessing() {
  const store = getStore();

  return Object.values(store.taskItems)
    .filter((item) => item.status === TASK_STATUS.PENDING)
    .sort((a, b) => {
      const taskA = store.tasks[a.taskId];
      const taskB = store.tasks[b.taskId];
      const priorityA = taskA?.priority || 0;
      const priorityB = taskB?.priority || 0;
      if (priorityB !== priorityA) return priorityB - priorityA;
      return new Date(a.createdAt) - new Date(b.createdAt);
    });
}

function canProcessItem(item) {
  if (processingItems.has(item.id)) return false;

  const userCount = userProcessingCount.get(item.userId) || 0;
  if (userCount >= TASK_QUEUE_CONFIG.MAX_CONCURRENT_PER_USER) return false;

  const task = getTask(item.taskId);
  if (!task) return false;
  if (task.status === TASK_STATUS.CANCELLED) return false;

  return true;
}

async function processItem(item) {
  processingItems.add(item.id);

  const currentUserCount = userProcessingCount.get(item.userId) || 0;
  userProcessingCount.set(item.userId, currentUserCount + 1);

  try {
    await executeItem(item);
  } catch (err) {
    console.error('Unexpected error processing item:', item.id, err);
  } finally {
    processingItems.delete(item.id);
    const count = userProcessingCount.get(item.userId) || 0;
    userProcessingCount.set(item.userId, Math.max(0, count - 1));
  }
}

async function executeItem(item) {
  const handler = taskHandlers.get(item.type);
  if (!handler) {
    markItemFailed(item, `No handler registered for type: ${item.type}`, ERROR_CATEGORY.NON_RETRYABLE);
    return;
  }

  const task = getTask(item.taskId);
  if (!task || task.status === TASK_STATUS.CANCELLED) {
    return;
  }

  if (task.status === TASK_STATUS.PENDING || task.status === TASK_STATUS.RETRYING) {
    const updatedTask = updateTask(item.taskId, {
      status: TASK_STATUS.PROCESSING,
      startedAt: new Date().toISOString(),
    });
    broadcastTaskUpdate(item.userId, updatedTask);
    createTaskLog({
      taskId: item.taskId,
      itemId: item.id,
      userId: item.userId,
      level: 'info',
      action: 'task_started',
      message: '任务开始处理',
    });
  }

  updateTaskItemStatus(item.id, TASK_STATUS.PROCESSING, {
    startedAt: new Date().toISOString(),
  });

  const currentItem = getTaskItem(item.id);
  broadcastTaskItemUpdate(item.userId, currentItem);

  createTaskLog({
    taskId: item.taskId,
    itemId: item.id,
    userId: item.userId,
    level: 'info',
    action: 'item_started',
    message: `开始处理子任务 ${item.index + 1}`,
  });

  try {
    const result = await handler({
      item: currentItem,
      task,
      input: item.inputData,
    });

    await handleItemSuccess(item, result);
  } catch (error) {
    await handleItemError(item, error);
  }
}

async function handleItemSuccess(item, result) {
  const updatedItem = updateTaskItemStatus(item.id, TASK_STATUS.COMPLETED, {
    outputData: result,
    error: null,
    errorCategory: null,
  });

  broadcastTaskItemUpdate(item.userId, updatedItem);

  const updatedTask = updateTaskProgress(item.taskId);
  broadcastTaskUpdate(item.userId, updatedTask);

  createTaskLog({
    taskId: item.taskId,
    itemId: item.id,
    userId: item.userId,
    level: 'info',
    action: 'item_completed',
    message: `子任务 ${item.index + 1} 处理完成`,
  });

  await checkTaskCompletion(item.taskId);
}

async function handleItemError(item, error) {
  const errorCategory = categorizeError(error);
  const errorMessage = error.message || 'Unknown error';
  const errorCode = error.code || 'UNKNOWN_ERROR';

  createTaskLog({
    taskId: item.taskId,
    itemId: item.id,
    userId: item.userId,
    level: 'error',
    action: 'item_error',
    message: `子任务 ${item.index + 1} 处理失败: ${errorMessage}`,
    details: {
      errorCode,
      errorMessage,
      errorCategory,
      retryCount: item.retryCount,
    },
  });

  if (errorCategory === ERROR_CATEGORY.RETRYABLE && item.retryCount < item.maxRetries) {
    await scheduleRetry(item, error, errorCode);
  } else {
    markItemFailed(item, errorMessage, errorCategory, errorCode);
  }
}

async function scheduleRetry(item, error, errorCode) {
  const newRetryCount = item.retryCount + 1;
  const delayMs = calculateRetryDelay(newRetryCount, TASK_QUEUE_CONFIG);
  const nextRetryAt = new Date(Date.now() + delayMs).toISOString();

  updateTaskItemStatus(item.id, TASK_STATUS.RETRYING, {
    retryCount: newRetryCount,
    nextRetryAt,
    error: {
      message: error.message || 'Unknown error',
      code: errorCode,
    },
    errorCategory: ERROR_CATEGORY.RETRYABLE,
  });

  const currentItem = getTaskItem(item.id);
  broadcastTaskItemUpdate(item.userId, currentItem);

  const task = getTask(item.taskId);
  if (task && task.status !== TASK_STATUS.RETRYING) {
    const updatedTask = updateTask(item.taskId, { status: TASK_STATUS.RETRYING });
    broadcastTaskUpdate(item.userId, updatedTask);
  }

  createTaskLog({
    taskId: item.taskId,
    itemId: item.id,
    userId: item.userId,
    level: 'warn',
    action: 'item_retry_scheduled',
    message: `子任务 ${item.index + 1} 第 ${newRetryCount} 次重试，将在 ${Math.round(delayMs / 1000)} 秒后执行`,
    details: {
      retryCount: newRetryCount,
      maxRetries: item.maxRetries,
      delayMs,
      errorCode,
    },
  });
}

function markItemFailed(item, errorMessage, errorCategory, errorCode = 'UNKNOWN_ERROR') {
  const updatedItem = updateTaskItemStatus(item.id, TASK_STATUS.FAILED, {
    error: {
      message: errorMessage,
      code: errorCode,
    },
    errorCategory,
  });

  broadcastTaskItemUpdate(item.userId, updatedItem);

  const updatedTask = updateTaskProgress(item.taskId);
  broadcastTaskUpdate(item.userId, updatedTask);

  createTaskLog({
    taskId: item.taskId,
    itemId: item.id,
    userId: item.userId,
    level: 'error',
    action: 'item_failed',
    message: `子任务 ${item.index + 1} 处理失败，已达到最大重试次数或为不可重试错误`,
    details: {
      errorMessage,
      errorCode,
      errorCategory,
      retryCount: item.retryCount,
    },
  });

  checkTaskCompletion(item.taskId);
}

async function processRetries() {
  if (!isRunning) return;

  const retryableItems = getRetryableItems();

  for (const item of retryableItems) {
    if (processingItems.has(item.id)) continue;

    const task = getTask(item.taskId);
    if (!task || task.status === TASK_STATUS.CANCELLED) continue;

    updateTaskItem(item.id, {
      status: TASK_STATUS.PENDING,
      nextRetryAt: null,
    });

    createTaskLog({
      taskId: item.taskId,
      itemId: item.id,
      userId: item.userId,
      level: 'info',
      action: 'item_retry_starting',
      message: `子任务 ${item.index + 1} 开始第 ${item.retryCount} 次重试`,
    });
  }
}

async function checkTaskCompletion(taskId) {
  const task = getTask(taskId);
  if (!task) return;

  const store = getStore();
  const items = Object.values(store.taskItems).filter((item) => item.taskId === taskId);

  if (items.length === 0) return;

  const allCompleted = items.every(
    (item) => item.status === TASK_STATUS.COMPLETED || item.status === TASK_STATUS.FAILED
  );

  if (!allCompleted) return;

  const allSuccess = items.every((item) => item.status === TASK_STATUS.COMPLETED);
  const allFailed = items.every((item) => item.status === TASK_STATUS.FAILED);
  const successCount = items.filter((item) => item.status === TASK_STATUS.COMPLETED).length;
  const failedCount = items.filter((item) => item.status === TASK_STATUS.FAILED).length;

  let finalStatus;
  if (allSuccess) {
    finalStatus = TASK_STATUS.COMPLETED;
  } else if (allFailed) {
    finalStatus = TASK_STATUS.FAILED;
  } else {
    finalStatus = TASK_STATUS.COMPLETED;
  }

  const updatedTask = updateTask(taskId, {
    status: finalStatus,
    completedAt: new Date().toISOString(),
    completedItems: successCount,
    failedItems: failedCount,
    progress: 100,
    result: {
      total: items.length,
      success: successCount,
      failed: failedCount,
    },
  });

  broadcastTaskUpdate(task.userId, updatedTask);

  createTaskLog({
    taskId,
    userId: task.userId,
    level: allSuccess ? 'info' : allFailed ? 'error' : 'warn',
    action: 'task_completed',
    message: `任务完成: ${successCount} 成功, ${failedCount} 失败, 共 ${items.length} 项`,
    details: {
      total: items.length,
      success: successCount,
      failed: failedCount,
    },
  });

  if (typeof onTaskCompleteCallback === 'function') {
    try {
      await onTaskCompleteCallback(updatedTask, items);
    } catch (err) {
      console.error('Error in task complete callback:', err);
    }
  }
}

export function setOnTaskCompleteCallback(callback) {
  onTaskCompleteCallback = callback;
}

export function getQueueStats() {
  return {
    processingItems: processingItems.size,
    userProcessingCounts: Object.fromEntries(userProcessingCount),
    isRunning,
    registeredHandlers: Array.from(taskHandlers.keys()),
  };
}

export function addToQueue(item) {
  updateTaskItemStatus(item.id, TASK_STATUS.PENDING);
}

export function cancelTask(taskId) {
  const task = getTask(taskId);
  if (!task) return null;

  const store = getStore();
  const items = Object.values(store.taskItems).filter((item) => item.taskId === taskId);

  items.forEach((item) => {
    if (item.status === TASK_STATUS.PENDING || item.status === TASK_STATUS.RETRYING) {
      updateTaskItemStatus(item.id, TASK_STATUS.CANCELLED);
    }
  });

  const updatedTask = updateTask(taskId, {
    status: TASK_STATUS.CANCELLED,
    cancelledAt: new Date().toISOString(),
  });

  broadcastTaskUpdate(task.userId, updatedTask);

  createTaskLog({
    taskId,
    userId: task.userId,
    level: 'info',
    action: 'task_cancelled',
    message: '任务已取消',
  });

  return updatedTask;
}

export function retryTask(taskId) {
  const task = getTask(taskId);
  if (!task) return null;

  const store = getStore();
  const failedItems = Object.values(store.taskItems).filter(
    (item) => item.taskId === taskId && item.status === TASK_STATUS.FAILED
  );

  if (failedItems.length === 0) return task;

  failedItems.forEach((item) => {
    updateTaskItem(item.id, {
      status: TASK_STATUS.PENDING,
      retryCount: 0,
      error: null,
      errorCategory: null,
      nextRetryAt: null,
      completedAt: null,
    });
  });

  const updatedTask = updateTask(taskId, {
    status: TASK_STATUS.PENDING,
    completedAt: null,
    error: null,
  });

  broadcastTaskUpdate(task.userId, updatedTask);

  createTaskLog({
    taskId,
    userId: task.userId,
    level: 'info',
    action: 'task_retried',
    message: `重新提交任务，${failedItems.length} 个失败项将重新处理`,
    details: {
      retryItemCount: failedItems.length,
    },
  });

  return updatedTask;
}

export default {
  registerTaskHandler,
  unregisterTaskHandler,
  getTaskHandler,
  startQueue,
  stopQueue,
  getQueueStats,
  addToQueue,
  cancelTask,
  retryTask,
  setOnTaskCompleteCallback,
};
