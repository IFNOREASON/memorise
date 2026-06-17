import { Router } from 'express';
import {
  getMessagesByUser,
  getMessage,
  markMessageRead,
  markAllMessagesRead,
  countUnreadMessages,
  deleteMessage,
} from '../models/message.js';

const router = Router();

function getUserId(req) {
  return req.headers['x-user-id'] || req.query.userId || 'default_user';
}

router.get('/', async (req, res) => {
  try {
    const userId = getUserId(req);
    const { limit = 20, offset = 0, isRead, type, category } = req.query;
    const result = getMessagesByUser(userId, {
      limit: parseInt(limit),
      offset: parseInt(offset),
      isRead: isRead !== undefined ? isRead === 'true' : undefined,
      type,
      category,
    });
    res.json({
      success: true,
      data: result,
    });
  } catch (err) {
    console.error('List messages error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to list messages',
      },
    });
  }
});

router.get('/unread/count', async (req, res) => {
  try {
    const userId = getUserId(req);
    const count = countUnreadMessages(userId);
    res.json({
      success: true,
      data: { count },
    });
  } catch (err) {
    console.error('Count unread messages error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to count unread messages',
      },
    });
  }
});

router.get('/:messageId', async (req, res) => {
  try {
    const { messageId } = req.params;
    const message = getMessage(messageId);
    if (!message) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Message not found',
        },
      });
    }
    res.json({
      success: true,
      data: message,
    });
  } catch (err) {
    console.error('Get message error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to get message',
      },
    });
  }
});

router.post('/:messageId/read', async (req, res) => {
  try {
    const { messageId } = req.params;
    const message = markMessageRead(messageId);
    if (!message) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Message not found',
        },
      });
    }
    res.json({
      success: true,
      data: message,
    });
  } catch (err) {
    console.error('Mark message read error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to mark message as read',
      },
    });
  }
});

router.post('/read/all', async (req, res) => {
  try {
    const userId = getUserId(req);
    const count = markAllMessagesRead(userId);
    res.json({
      success: true,
      data: { markedCount: count },
    });
  } catch (err) {
    console.error('Mark all messages read error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to mark all messages as read',
      },
    });
  }
});

router.delete('/:messageId', async (req, res) => {
  try {
    const { messageId } = req.params;
    const deleted = deleteMessage(messageId);
    if (!deleted) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Message not found',
        },
      });
    }
    res.json({
      success: true,
      data: { deleted: true },
    });
  } catch (err) {
    console.error('Delete message error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to delete message',
      },
    });
  }
});

export default router;
