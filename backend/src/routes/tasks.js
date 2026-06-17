import { Router } from 'express';
import taskService from '../services/taskService.js';

const router = Router();

function getUserId(req) {
  return req.headers['x-user-id'] || req.query.userId || 'default_user';
}

router.post('/repair', async (req, res) => {
  try {
    const userId = getUserId(req);
    const result = await taskService.submitImageRepairTask(userId, req.body);
    res.status(201).json({
      success: true,
      data: result,
    });
  } catch (err) {
    console.error('Submit repair task error:', err);
    const status = err.status || 500;
    res.status(status).json({
      success: false,
      error: {
        code: err.code || 'INTERNAL_ERROR',
        message: err.message || 'Failed to submit repair task',
      },
    });
  }
});

router.post('/generate', async (req, res) => {
  try {
    const userId = getUserId(req);
    const result = await taskService.submitGenerationTask(userId, req.body);
    res.status(201).json({
      success: true,
      data: result,
    });
  } catch (err) {
    console.error('Submit generation task error:', err);
    const status = err.status || 500;
    res.status(status).json({
      success: false,
      error: {
        code: err.code || 'INTERNAL_ERROR',
        message: err.message || 'Failed to submit generation task',
      },
    });
  }
});

router.get('/', async (req, res) => {
  try {
    const userId = getUserId(req);
    const { limit = 20, offset = 0, status, type } = req.query;
    const result = taskService.listUserTasks(userId, {
      limit: parseInt(limit),
      offset: parseInt(offset),
      status,
      type,
    });
    res.json({
      success: true,
      data: result,
    });
  } catch (err) {
    console.error('List tasks error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to list tasks',
      },
    });
  }
});

router.get('/:taskId', async (req, res) => {
  try {
    const { taskId } = req.params;
    const task = taskService.getTaskWithDetails(taskId);
    if (!task) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Task not found',
        },
      });
    }
    res.json({
      success: true,
      data: task,
    });
  } catch (err) {
    console.error('Get task error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to get task',
      },
    });
  }
});

router.post('/:taskId/cancel', async (req, res) => {
  try {
    const { taskId } = req.params;
    const task = taskService.cancelTask(taskId);
    if (!task) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Task not found',
        },
      });
    }
    res.json({
      success: true,
      data: task,
    });
  } catch (err) {
    console.error('Cancel task error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to cancel task',
      },
    });
  }
});

router.post('/:taskId/retry', async (req, res) => {
  try {
    const { taskId } = req.params;
    const task = taskService.retryTask(taskId);
    if (!task) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Task not found',
        },
      });
    }
    res.json({
      success: true,
      data: task,
    });
  } catch (err) {
    console.error('Retry task error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to retry task',
      },
    });
  }
});

router.get('/:taskId/items', async (req, res) => {
  try {
    const { taskId } = req.params;
    const { limit = 50, offset = 0, status } = req.query;
    const result = taskService.getTaskItemsList(taskId, {
      limit: parseInt(limit),
      offset: parseInt(offset),
      status,
    });
    res.json({
      success: true,
      data: result,
    });
  } catch (err) {
    console.error('Get task items error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to get task items',
      },
    });
  }
});

router.get('/:taskId/logs', async (req, res) => {
  try {
    const { taskId } = req.params;
    const { limit = 100, offset = 0, level } = req.query;
    const result = taskService.getTaskLogsList(taskId, {
      limit: parseInt(limit),
      offset: parseInt(offset),
      level,
    });
    res.json({
      success: true,
      data: result,
    });
  } catch (err) {
    console.error('Get task logs error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to get task logs',
      },
    });
  }
});

router.get('/items/:itemId', async (req, res) => {
  try {
    const { itemId } = req.params;
    const item = taskService.getTaskItemDetails(itemId);
    if (!item) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Task item not found',
        },
      });
    }
    res.json({
      success: true,
      data: item,
    });
  } catch (err) {
    console.error('Get task item error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to get task item',
      },
    });
  }
});

router.get('/queue/stats', async (req, res) => {
  try {
    const stats = taskService.getQueueStats();
    res.json({
      success: true,
      data: stats,
    });
  } catch (err) {
    console.error('Get queue stats error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to get queue stats',
      },
    });
  }
});

export default router;
