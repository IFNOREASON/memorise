import { ref, onUnmounted, onMounted } from 'vue';
import type { Task, TaskItem, WebSocketMessage } from '../types/task';
import { taskApi } from '../api';

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || (
  typeof window !== 'undefined'
    ? `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`
    : 'ws://localhost:3000/ws'
);
const POLLING_INTERVAL_MS = 3000;
const MAX_POLLING_INTERVAL_MS = 15000;
const POLLING_BACKOFF_MULTIPLIER = 1.5;
const RECONNECT_DELAY_MS = 2000;
const MAX_RECONNECT_DELAY_MS = 30000;

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'polling';

export function useTaskWebSocket(userId: string = 'default_user') {
  const connectionStatus = ref<ConnectionStatus>('disconnected');
  const lastMessage = ref<WebSocketMessage | null>(null);
  const tasks = ref<Map<string, Task>>(new Map());
  const taskItems = ref<Map<string, TaskItem>>(new Map());

  let ws: WebSocket | null = null;
  let reconnectAttempts = 0;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  let pollingTimer: ReturnType<typeof setInterval> | null = null;
  let pollingInterval = POLLING_INTERVAL_MS;
  let isManualClose = false;

  function connect() {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    isManualClose = false;
    connectionStatus.value = 'connecting';

    try {
      const wsUrl = `${WS_BASE_URL}?userId=${encodeURIComponent(userId)}`;
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('[WebSocket] Connected');
        connectionStatus.value = 'connected';
        reconnectAttempts = 0;
        stopPolling();
        pollingInterval = POLLING_INTERVAL_MS;
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          handleMessage(message);
        } catch (err) {
          console.error('[WebSocket] Failed to parse message:', err);
        }
      };

      ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
      };

      ws.onclose = (event) => {
        console.log('[WebSocket] Closed:', event.code, event.reason);
        connectionStatus.value = 'disconnected';

        if (!isManualClose) {
          scheduleReconnect();
        }
      };
    } catch (err) {
      console.error('[WebSocket] Failed to connect:', err);
      startPolling();
    }
  }

  function disconnect() {
    isManualClose = true;
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
    stopPolling();
    if (ws) {
      ws.close();
      ws = null;
    }
    connectionStatus.value = 'disconnected';
  }

  function scheduleReconnect() {
    if (reconnectTimer) return;

    const delay = Math.min(
      RECONNECT_DELAY_MS * Math.pow(2, reconnectAttempts),
      MAX_RECONNECT_DELAY_MS
    );
    reconnectAttempts++;

    console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${reconnectAttempts})`);

    if (reconnectAttempts >= 3) {
      console.log('[WebSocket] Too many reconnect attempts, falling back to polling');
      startPolling();
      return;
    }

    reconnectTimer = setTimeout(() => {
      reconnectTimer = null;
      connect();
    }, delay);
  }

  function handleMessage(message: WebSocketMessage) {
    lastMessage.value = message;

    switch (message.type) {
      case 'task_update':
        if (message.data) {
          tasks.value.set(message.data.id, message.data as Task);
        }
        break;
      case 'task_item_update':
        if (message.data) {
          taskItems.value.set(message.data.id, message.data as TaskItem);
        }
        break;
      case 'task_progress':
        break;
      case 'connected':
        break;
      case 'pong':
        break;
    }
  }

  function startPolling() {
    if (pollingTimer) return;

    connectionStatus.value = 'polling';
    console.log('[Polling] Started with interval:', pollingInterval);

    pollingTimer = setInterval(() => {
      pollTasks();
    }, pollingInterval);

    pollTasks();
  }

  function stopPolling() {
    if (pollingTimer) {
      clearInterval(pollingTimer);
      pollingTimer = null;
    }
  }

  async function pollTasks() {
    try {
      const response = await taskApi.list({ limit: 20, offset: 0 });
      if (response.success && response.data) {
        response.data.items.forEach((task) => {
          tasks.value.set(task.id, task);
        });
      }

      if (pollingInterval < MAX_POLLING_INTERVAL_MS) {
        pollingInterval = Math.min(
          pollingInterval * POLLING_BACKOFF_MULTIPLIER,
          MAX_POLLING_INTERVAL_MS
        );
        if (pollingTimer) {
          clearInterval(pollingTimer);
          pollingTimer = setInterval(() => pollTasks(), pollingInterval);
        }
      }
    } catch (err) {
      console.error('[Polling] Error:', err);
    }
  }

  async function pollTaskDetail(taskId: string) {
    try {
      const response = await taskApi.get(taskId);
      if (response.success && response.data) {
        tasks.value.set(response.data.id, response.data);
        if (response.data.items) {
          response.data.items.forEach((item) => {
            taskItems.value.set(item.id, item);
          });
        }
      }
    } catch (err) {
      console.error('[Polling] Error fetching task detail:', err);
    }
  }

  function sendMessage(type: string, data?: any) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type, data }));
      return true;
    }
    return false;
  }

  function subscribe(channels: string[]) {
    sendMessage('subscribe', { channels });
  }

  function getTask(taskId: string): Task | undefined {
    return tasks.value.get(taskId);
  }

  function getTaskItemsByTask(taskId: string): TaskItem[] {
    return Array.from(taskItems.value.values()).filter((item) => item.taskId === taskId);
  }

  function setTask(task: Task) {
    tasks.value.set(task.id, task);
  }

  function setTaskItem(item: TaskItem) {
    taskItems.value.set(item.id, item);
  }

  onMounted(() => {
    connect();
  });

  onUnmounted(() => {
    disconnect();
  });

  return {
    connectionStatus,
    lastMessage,
    tasks,
    taskItems,
    connect,
    disconnect,
    sendMessage,
    subscribe,
    getTask,
    getTaskItemsByTask,
    setTask,
    setTaskItem,
    pollTaskDetail,
    pollTasks,
  };
}

export default useTaskWebSocket;
