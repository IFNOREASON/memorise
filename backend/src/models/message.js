import { getStore, persist } from './store.js';
import { generateId, now } from '../utils/helpers.js';

export function createMessage(messageData) {
  const store = getStore();
  const messageId = generateId('msg');
  const message = {
    id: messageId,
    userId: messageData.userId || 'default_user',
    type: messageData.type || 'info',
    title: messageData.title || '',
    content: messageData.content || '',
    category: messageData.category || 'system',
    taskId: messageData.taskId || null,
    itemId: messageData.itemId || null,
    actionUrl: messageData.actionUrl || null,
    actionText: messageData.actionText || null,
    metadata: messageData.metadata || {},
    isRead: false,
    createdAt: now(),
    readAt: null,
  };

  store.messages[messageId] = message;
  persist();
  return message;
}

export function getMessage(messageId) {
  const store = getStore();
  return store.messages[messageId] || null;
}

export function getMessagesByUser(userId, options = {}) {
  const store = getStore();
  const { limit = 50, offset = 0, isRead, type, category } = options;

  let messages = Object.values(store.messages).filter((m) => m.userId === userId);

  if (isRead !== undefined) {
    messages = messages.filter((m) => m.isRead === isRead);
  }
  if (type) {
    messages = messages.filter((m) => m.type === type);
  }
  if (category) {
    messages = messages.filter((m) => m.category === category);
  }

  messages.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  return {
    total: messages.length,
    items: messages.slice(offset, offset + limit),
  };
}

export function markMessageRead(messageId) {
  const store = getStore();
  const message = store.messages[messageId];
  if (!message) return null;

  const updated = { ...message, isRead: true, readAt: now() };
  store.messages[messageId] = updated;
  persist();
  return updated;
}

export function markAllMessagesRead(userId) {
  const store = getStore();
  const messages = Object.values(store.messages).filter(
    (m) => m.userId === userId && !m.isRead
  );
  const nowTime = now();
  messages.forEach((m) => {
    store.messages[m.id] = { ...m, isRead: true, readAt: nowTime };
  });
  persist();
  return messages.length;
}

export function countUnreadMessages(userId) {
  const store = getStore();
  return Object.values(store.messages).filter((m) => m.userId === userId && !m.isRead).length;
}

export function deleteMessage(messageId) {
  const store = getStore();
  if (!store.messages[messageId]) return false;
  delete store.messages[messageId];
  persist();
  return true;
}
