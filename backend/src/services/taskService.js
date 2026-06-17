import { TASK_TYPE, TASK_STATUS, TASK_QUEUE_CONFIG, GALLERY_SOURCE } from '../constants.js';
import { createTask, getTask, getTasksByUser } from '../models/task.js';
import { bulkCreateTaskItems, getTaskItems, getTaskItem } from '../models/taskItem.js';
import { createTaskLog, getTaskLogs } from '../models/taskLog.js';
import { getStore } from '../models/store.js';
import { createGalleryPhoto, linkRepairedPhoto } from '../models/gallery.js';
import { createRepairMemory } from '../models/familyMemory.js';
import { createMessage } from '../models/message.js';
import taskQueue from './taskQueue.js';
import { repairImage } from './imageProcessingService.js';
import { generateScene } from './generationService.js';

export async function submitImageRepairTask(userId, payload) {
  const {
    images,
    familyId = null,
    memberId = null,
    title = '',
    description = '',
    repairOptions = {},
    autoAddToGallery = true,
    autoCreateMemory = true,
    maxRetries = TASK_QUEUE_CONFIG.MAX_RETRY_ATTEMPTS,
    priority = 0,
  } = payload;

  if (!images || images.length === 0) {
    const err = new Error('No images provided for repair');
    err.code = 'BAD_REQUEST';
    err.status = 400;
    throw err;
  }

  const pendingCount = countPendingTasksForUser(userId);
  if (pendingCount + images.length > TASK_QUEUE_CONFIG.MAX_QUEUE_SIZE_PER_USER) {
    const err = new Error(`Queue limit exceeded. Maximum ${TASK_QUEUE_CONFIG.MAX_QUEUE_SIZE_PER_USER} items per user.`);
    err.code = 'QUEUE_FULL';
    err.status = 429;
    throw err;
  }

  const task = createTask({
    userId,
    familyId,
    memberId,
    type: TASK_TYPE.IMAGE_REPAIR,
    title: title || `老照片修复 (${images.length}张)`,
    description,
    totalItems: images.length,
    priority,
    metadata: {
      repairOptions,
      autoAddToGallery,
      autoCreateMemory,
    },
  });

  const itemsData = images.map((img, index) => ({
    taskId: task.id,
    userId,
    type: TASK_TYPE.IMAGE_REPAIR,
    index,
    title: img.title || `照片 ${index + 1}`,
    inputData: {
      imageUrl: img.url,
      originalPhotoId: img.photoId || null,
      title: img.title || '',
      description: img.description || '',
      repairOptions,
    },
    metadata: {
      familyId,
      memberId,
      autoAddToGallery,
    },
    maxRetries,
  }));

  const items = bulkCreateTaskItems(itemsData);

  createTaskLog({
    taskId: task.id,
    userId,
    level: 'info',
    action: 'task_submitted',
    message: `任务已提交，共 ${images.length} 张照片待修复`,
    details: {
      imageCount: images.length,
      familyId,
      memberId,
    },
  });

  items.forEach((item) => taskQueue.addToQueue(item));

  return {
    task,
    itemCount: items.length,
  };
}

export async function submitGenerationTask(userId, payload) {
  const {
    type = 'scene',
    prompt,
    familyId = null,
    memberId = null,
    title = '',
    description = '',
    generationOptions = {},
    numImages = 1,
    autoAddToGallery = true,
    maxRetries = TASK_QUEUE_CONFIG.MAX_RETRY_ATTEMPTS,
    priority = 0,
  } = payload;

  if (!prompt) {
    const err = new Error('Prompt is required for generation');
    err.code = 'BAD_REQUEST';
    err.status = 400;
    throw err;
  }

  const task = createTask({
    userId,
    familyId,
    memberId,
    type: TASK_TYPE.AI_GENERATION,
    title: title || `AI生成 - ${type}`,
    description,
    totalItems: numImages,
    priority,
    metadata: {
      generationType: type,
      prompt,
      generationOptions,
      autoAddToGallery,
    },
  });

  const itemsData = [];
  for (let i = 0; i < numImages; i++) {
    itemsData.push({
      taskId: task.id,
      userId,
      type: TASK_TYPE.AI_GENERATION,
      index: i,
      title: `${title || '生成图'} ${i + 1}`,
      inputData: {
        prompt,
        type,
        generationOptions,
      },
      metadata: {
        familyId,
        memberId,
        autoAddToGallery,
      },
      maxRetries,
    });
  }

  const items = bulkCreateTaskItems(itemsData);

  createTaskLog({
    taskId: task.id,
    userId,
    level: 'info',
    action: 'task_submitted',
    message: `AI生成任务已提交，共 ${numImages} 张`,
    details: {
      numImages,
      type,
      familyId,
      memberId,
    },
  });

  items.forEach((item) => taskQueue.addToQueue(item));

  return {
    task,
    itemCount: items.length,
  };
}

async function imageRepairHandler({ item, task, input }) {
  const { imageUrl, repairOptions = {} } = input;
  const result = await repairImage(imageUrl, repairOptions);

  const { autoAddToGallery, familyId, memberId } = item.metadata || {};

  if (autoAddToGallery) {
    try {
      const repairedPhoto = createGalleryPhoto({
        userId: item.userId,
        familyId: familyId || null,
        memberId: memberId || null,
        title: item.title + ' (已修复)',
        description: 'AI修复后的老照片',
        imageUrl: result.repairedUrl,
        thumbnailUrl: result.thumbnailUrl,
        source: GALLERY_SOURCE.REPAIR,
        sourceTaskId: item.taskId,
        sourceItemId: item.id,
        originalPhotoId: input.originalPhotoId || null,
        isRepaired: true,
        tags: ['修复', '老照片'],
        metadata: {
          repairStats: result.stats,
          repairMode: result.mode,
        },
      });

      if (input.originalPhotoId) {
        linkRepairedPhoto(input.originalPhotoId, repairedPhoto.id);
      }

      result.galleryPhotoId = repairedPhoto.id;
    } catch (err) {
      console.error('Failed to add to gallery:', err);
    }
  }

  return result;
}

async function generationHandler({ item, task, input }) {
  const { prompt, generationOptions = {} } = input;
  const result = await generateScene(prompt, {
    ...generationOptions,
    numImages: 1,
  });

  const { autoAddToGallery, familyId, memberId } = item.metadata || {};

  if (autoAddToGallery && result.images && result.images.length > 0) {
    try {
      const generatedPhoto = createGalleryPhoto({
        userId: item.userId,
        familyId: familyId || null,
        memberId: memberId || null,
        title: item.title,
        description: 'AI生成的影像',
        imageUrl: result.images[0].url,
        thumbnailUrl: result.images[0].thumbnailUrl,
        source: GALLERY_SOURCE.AI_GENERATION,
        sourceTaskId: item.taskId,
        sourceItemId: item.id,
        isAIGenerated: true,
        tags: ['AI生成', generationOptions.style || 'realistic'],
        metadata: {
          prompt,
          seed: result.images[0].seed,
          style: generationOptions.style,
        },
      });

      result.galleryPhotoId = generatedPhoto.id;
    } catch (err) {
      console.error('Failed to add generated image to gallery:', err);
    }
  }

  return result;
}

async function handleTaskComplete(task, items) {
  if (task.type === TASK_TYPE.IMAGE_REPAIR && task.metadata?.autoCreateMemory) {
    try {
      await createRepairMemoryFromTask(task, items);
    } catch (err) {
      console.error('Failed to create repair memory:', err);
    }
  }

  try {
    await sendTaskCompletionMessage(task, items);
  } catch (err) {
    console.error('Failed to send completion message:', err);
  }
}

async function createRepairMemoryFromTask(task, items) {
  const completedItems = items.filter((item) => item.status === TASK_STATUS.COMPLETED);

  if (completedItems.length === 0) return null;

  const beforeAfterPairs = completedItems.map((item) => ({
    beforeUrl: item.inputData?.imageUrl,
    afterUrl: item.outputData?.repairedUrl,
    beforeId: item.inputData?.originalPhotoId,
    afterId: item.outputData?.galleryPhotoId,
    title: item.title,
    stats: item.outputData?.stats,
  }));

  const memory = createRepairMemory(task, beforeAfterPairs);
  return memory;
}

async function sendTaskCompletionMessage(task, items) {
  const successCount = items.filter((item) => item.status === TASK_STATUS.COMPLETED).length;
  const failedCount = items.filter((item) => item.status === TASK_STATUS.FAILED).length;
  const totalCount = items.length;

  let messageType = 'success';
  let title = '';
  let content = '';

  const taskTypeName = task.type === TASK_TYPE.IMAGE_REPAIR ? '照片修复' : 'AI生成';

  if (failedCount === 0) {
    messageType = 'success';
    title = '任务全部完成';
    content = `您的 ${totalCount} 张${taskTypeName}任务已全部完成`;
  } else if (successCount === 0) {
    messageType = 'error';
    title = '任务全部失败';
    content = `您的 ${totalCount} 张${taskTypeName}任务全部失败，点击查看详情`;
  } else {
    messageType = 'warning';
    title = '任务部分完成';
    content = `您的 ${totalCount} 张${taskTypeName}任务中，${successCount} 张成功，${failedCount} 张失败，点击查看详情`;
  }

  const message = createMessage({
    userId: task.userId,
    type: messageType,
    category: 'task',
    title,
    content,
    taskId: task.id,
    actionUrl: `/tasks/${task.id}`,
    actionText: '查看详情',
    metadata: {
      taskType: task.type,
      totalItems: totalCount,
      successItems: successCount,
      failedItems: failedCount,
    },
  });

  return message;
}

export function getTaskWithDetails(taskId) {
  const task = getTask(taskId);
  if (!task) return null;

  const { items } = getTaskItems(taskId, { limit: 100 });

  return {
    ...task,
    items,
  };
}

export function listUserTasks(userId, options = {}) {
  return getTasksByUser(userId, options);
}

export function cancelTask(taskId) {
  return taskQueue.cancelTask(taskId);
}

export function retryTask(taskId) {
  return taskQueue.retryTask(taskId);
}

export function getTaskItemsList(taskId, options = {}) {
  return getTaskItems(taskId, options);
}

export function getTaskItemDetails(itemId) {
  return getTaskItem(itemId);
}

export function getTaskLogsList(taskId, options = {}) {
  return getTaskLogs(taskId, options);
}

function countPendingTasksForUser(userId) {
  const store = getStore();
  return Object.values(store.taskItems).filter(
    (item) =>
      item.userId === userId &&
      (item.status === TASK_STATUS.PENDING ||
        item.status === TASK_STATUS.PROCESSING ||
        item.status === TASK_STATUS.RETRYING)
  ).length;
}

export function getQueueStats() {
  return taskQueue.getQueueStats();
}

export function initTaskServices() {
  taskQueue.registerTaskHandler(TASK_TYPE.IMAGE_REPAIR, imageRepairHandler);
  taskQueue.registerTaskHandler(TASK_TYPE.AI_GENERATION, generationHandler);
  taskQueue.setOnTaskCompleteCallback(handleTaskComplete);
  taskQueue.startQueue();
  console.log('Task services initialized');
}

export default {
  submitImageRepairTask,
  submitGenerationTask,
  getTaskWithDetails,
  listUserTasks,
  cancelTask,
  retryTask,
  getTaskItemsList,
  getTaskItemDetails,
  getTaskLogsList,
  getQueueStats,
  initTaskServices,
};
