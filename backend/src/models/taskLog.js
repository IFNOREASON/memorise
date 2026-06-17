import { getStore, persist } from './store.js';
import { generateId, now } from '../utils/helpers.js';

export function createTaskLog(logData) {
  const store = getStore();
  const logId = generateId('log');
  const log = {
    id: logId,
    taskId: logData.taskId || null,
    itemId: logData.itemId || null,
    userId: logData.userId || 'default_user',
    level: logData.level || 'info',
    action: logData.action || '',
    message: logData.message || '',
    details: logData.details || {},
    timestamp: now(),
  };

  store.taskLogs[logId] = log;
  store.logs.push(log);
  if (store.logs.length > 10000) {
    store.logs = store.logs.slice(-5000);
  }
  persist();
  return log;
}

export function getTaskLogs(taskId, options = {}) {
  const store = getStore();
  const { limit = 100, offset = 0, level } = options;

  let logs = Object.values(store.taskLogs).filter((log) => log.taskId === taskId);

  if (level) {
    logs = logs.filter((log) => log.level === level);
  }

  logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  return {
    total: logs.length,
    items: logs.slice(offset, offset + limit),
  };
}

export function getRecentLogs(userId, limit = 50) {
  const store = getStore();
  let logs = store.logs;
  if (userId) {
    logs = logs.filter((log) => log.userId === userId);
  }
  return logs.slice(-limit).reverse();
}
