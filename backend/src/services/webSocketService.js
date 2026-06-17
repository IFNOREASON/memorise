import { WebSocketServer } from 'ws';
import { WEBSOCKET_CONFIG } from '../constants.js';

let wss = null;
const userConnections = new Map();

export function initWebSocket(server) {
  if (wss) return wss;

  wss = new WebSocketServer({ server, path: '/ws' });

  wss.on('connection', (ws, req) => {
    const userId = getUserIdFromRequest(req);
    ws.userId = userId;
    ws.isAlive = true;

    if (!userConnections.has(userId)) {
      userConnections.set(userId, new Set());
    }
    userConnections.get(userId).add(ws);

    ws.on('pong', () => {
      ws.isAlive = true;
    });

    ws.on('message', (data) => {
      try {
        const message = JSON.parse(data.toString());
        handleClientMessage(ws, message);
      } catch (err) {
        console.error('WebSocket message parse error:', err);
      }
    });

    ws.on('close', () => {
      const conns = userConnections.get(userId);
      if (conns) {
        conns.delete(ws);
        if (conns.size === 0) {
          userConnections.delete(userId);
        }
      }
    });

    ws.send(JSON.stringify({
      type: 'connected',
      timestamp: new Date().toISOString(),
    }));
  });

  const heartbeatInterval = setInterval(() => {
    wss.clients.forEach((ws) => {
      if (ws.isAlive === false) {
        ws.terminate();
        return;
      }
      ws.isAlive = false;
      try {
        ws.ping();
      } catch (e) {
        ws.terminate();
      }
    });
  }, WEBSOCKET_CONFIG.HEARTBEAT_INTERVAL_MS);

  wss.on('close', () => {
    clearInterval(heartbeatInterval);
  });

  console.log('WebSocket server initialized on /ws');
  return wss;
}

function getUserIdFromRequest(req) {
  const url = new URL(req.url, 'http://localhost');
  const userId = url.searchParams.get('userId') || 'default_user';
  return userId;
}

function handleClientMessage(ws, message) {
  switch (message.type) {
    case 'ping':
      ws.send(JSON.stringify({ type: 'pong', timestamp: new Date().toISOString() }));
      break;
    case 'subscribe':
      handleSubscribe(ws, message);
      break;
    default:
      break;
  }
}

function handleSubscribe(ws, message) {
  if (message.channels) {
    ws.subscribedChannels = message.channels;
  }
  ws.send(JSON.stringify({
    type: 'subscribed',
    channels: message.channels || [],
    timestamp: new Date().toISOString(),
  }));
}

export function sendToUser(userId, payload) {
  const conns = userConnections.get(userId);
  if (!conns || conns.size === 0) return false;

  const message = JSON.stringify({
    ...payload,
    timestamp: new Date().toISOString(),
  });

  let sentCount = 0;
  conns.forEach((ws) => {
    if (ws.readyState === 1) {
      try {
        ws.send(message);
        sentCount++;
      } catch (e) {
        console.error('WebSocket send error:', e);
      }
    }
  });

  return sentCount > 0;
}

export function broadcastTaskUpdate(userId, task) {
  return sendToUser(userId, {
    type: 'task_update',
    data: task,
  });
}

export function broadcastTaskItemUpdate(userId, item) {
  return sendToUser(userId, {
    type: 'task_item_update',
    data: item,
  });
}

export function broadcastTaskProgress(userId, taskId, progress) {
  return sendToUser(userId, {
    type: 'task_progress',
    data: {
      taskId,
      progress,
    },
  });
}

export function getConnectedUserCount() {
  return userConnections.size;
}

export function getUserConnectionCount(userId) {
  const conns = userConnections.get(userId);
  return conns ? conns.size : 0;
}

export function getWss() {
  return wss;
}

export default {
  initWebSocket,
  sendToUser,
  broadcastTaskUpdate,
  broadcastTaskItemUpdate,
  broadcastTaskProgress,
  getConnectedUserCount,
  getUserConnectionCount,
  getWss,
};
