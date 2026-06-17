import { Router } from 'express';
import {
  getFamilyMemories,
  getFamilyMemory,
  createFamilyMemory,
  updateFamilyMemory,
  deleteFamilyMemory,
} from '../models/familyMemory.js';

const router = Router();

function getUserId(req) {
  return req.headers['x-user-id'] || req.query.userId || 'default_user';
}

router.get('/family/:familyId', async (req, res) => {
  try {
    const { familyId } = req.params;
    const { limit = 50, offset = 0, type, memberId } = req.query;
    const result = getFamilyMemories(familyId, {
      limit: parseInt(limit),
      offset: parseInt(offset),
      type,
      memberId,
    });
    res.json({
      success: true,
      data: result,
    });
  } catch (err) {
    console.error('Get family memories error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to get family memories',
      },
    });
  }
});

router.get('/:memoryId', async (req, res) => {
  try {
    const { memoryId } = req.params;
    const memory = getFamilyMemory(memoryId);
    if (!memory) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Family memory not found',
        },
      });
    }
    res.json({
      success: true,
      data: memory,
    });
  } catch (err) {
    console.error('Get family memory error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to get family memory',
      },
    });
  }
});

router.post('/', async (req, res) => {
  try {
    const userId = getUserId(req);
    const memoryData = { ...req.body, userId };
    const memory = createFamilyMemory(memoryData);
    res.status(201).json({
      success: true,
      data: memory,
    });
  } catch (err) {
    console.error('Create family memory error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to create family memory',
      },
    });
  }
});

router.put('/:memoryId', async (req, res) => {
  try {
    const { memoryId } = req.params;
    const memory = updateFamilyMemory(memoryId, req.body);
    if (!memory) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Family memory not found',
        },
      });
    }
    res.json({
      success: true,
      data: memory,
    });
  } catch (err) {
    console.error('Update family memory error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to update family memory',
      },
    });
  }
});

router.delete('/:memoryId', async (req, res) => {
  try {
    const { memoryId } = req.params;
    const deleted = deleteFamilyMemory(memoryId);
    if (!deleted) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Family memory not found',
        },
      });
    }
    res.json({
      success: true,
      data: { deleted: true },
    });
  } catch (err) {
    console.error('Delete family memory error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to delete family memory',
      },
    });
  }
});

export default router;
