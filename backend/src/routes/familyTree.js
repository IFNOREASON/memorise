import { Router } from 'express';
import {
  createFamilyMember,
  getFamilyMember,
  getFamilyMembers,
  getAllFamilyMembers,
  updateFamilyMember,
  deleteFamilyMember,
} from '../models/familyMember.js';
import {
  createFamilyRelationship,
  getFamilyRelationship,
  getRelationshipsByFamily,
  getRelationshipsByMember,
  updateFamilyRelationship,
  deleteFamilyRelationship,
  getFamilyTreeData,
} from '../models/familyRelationship.js';

const router = Router();

function getUserId(req) {
  return req.headers['x-user-id'] || req.query.userId || 'default_user';
}

router.get('/family/:familyId/tree', async (req, res) => {
  try {
    const { familyId } = req.params;
    const treeData = getFamilyTreeData(familyId);
    res.json({
      success: true,
      data: treeData,
    });
  } catch (err) {
    console.error('Get family tree error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to get family tree',
      },
    });
  }
});

router.get('/family/:familyId/members', async (req, res) => {
  try {
    const { familyId } = req.params;
    const { limit = 50, offset = 0, generation } = req.query;
    const result = getFamilyMembers(familyId, {
      limit: parseInt(limit),
      offset: parseInt(offset),
      generation: generation !== undefined ? parseInt(generation) : undefined,
    });
    res.json({
      success: true,
      data: result,
    });
  } catch (err) {
    console.error('Get family members error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to get family members',
      },
    });
  }
});

router.get('/family/:familyId/relationships', async (req, res) => {
  try {
    const { familyId } = req.params;
    const { type, memberId } = req.query;
    const relationships = getRelationshipsByFamily(familyId, { type, memberId });
    res.json({
      success: true,
      data: relationships,
    });
  } catch (err) {
    console.error('Get family relationships error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to get relationships',
      },
    });
  }
});

router.get('/members/:memberId', async (req, res) => {
  try {
    const { memberId } = req.params;
    const member = getFamilyMember(memberId);
    if (!member) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Family member not found',
        },
      });
    }
    res.json({
      success: true,
      data: member,
    });
  } catch (err) {
    console.error('Get family member error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to get family member',
      },
    });
  }
});

router.get('/members/:memberId/relationships', async (req, res) => {
  try {
    const { memberId } = req.params;
    const relationships = getRelationshipsByMember(memberId);
    res.json({
      success: true,
      data: relationships,
    });
  } catch (err) {
    console.error('Get member relationships error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to get member relationships',
      },
    });
  }
});

router.post('/members', async (req, res) => {
  try {
    const userId = getUserId(req);
    const memberData = { ...req.body, userId };
    const member = createFamilyMember(memberData);
    res.status(201).json({
      success: true,
      data: member,
    });
  } catch (err) {
    console.error('Create family member error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to create family member',
      },
    });
  }
});

router.put('/members/:memberId', async (req, res) => {
  try {
    const { memberId } = req.params;
    const member = updateFamilyMember(memberId, req.body);
    if (!member) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Family member not found',
        },
      });
    }
    res.json({
      success: true,
      data: member,
    });
  } catch (err) {
    console.error('Update family member error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to update family member',
      },
    });
  }
});

router.delete('/members/:memberId', async (req, res) => {
  try {
    const { memberId } = req.params;
    const deleted = deleteFamilyMember(memberId);
    if (!deleted) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Family member not found',
        },
      });
    }
    res.json({
      success: true,
      data: { deleted: true },
    });
  } catch (err) {
    console.error('Delete family member error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to delete family member',
      },
    });
  }
});

router.get('/relationships/:relId', async (req, res) => {
  try {
    const { relId } = req.params;
    const relationship = getFamilyRelationship(relId);
    if (!relationship) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Relationship not found',
        },
      });
    }
    res.json({
      success: true,
      data: relationship,
    });
  } catch (err) {
    console.error('Get relationship error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to get relationship',
      },
    });
  }
});

router.post('/relationships', async (req, res) => {
  try {
    const relationshipData = req.body;
    const relationship = createFamilyRelationship(relationshipData);
    res.status(201).json({
      success: true,
      data: relationship,
    });
  } catch (err) {
    console.error('Create relationship error:', err);
    const isValidation = err.message.includes('Validation failed') || err.message.includes('Circular reference') || err.message.includes('already exists');
    res.status(isValidation ? 400 : 500).json({
      success: false,
      error: {
        code: isValidation ? 'VALIDATION_ERROR' : 'INTERNAL_ERROR',
        message: err.message,
      },
    });
  }
});

router.put('/relationships/:relId', async (req, res) => {
  try {
    const { relId } = req.params;
    const relationship = updateFamilyRelationship(relId, req.body);
    if (!relationship) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Relationship not found',
        },
      });
    }
    res.json({
      success: true,
      data: relationship,
    });
  } catch (err) {
    console.error('Update relationship error:', err);
    const isValidation = err.message.includes('Validation failed') || err.message.includes('Circular reference') || err.message.includes('already exists');
    res.status(isValidation ? 400 : 500).json({
      success: false,
      error: {
        code: isValidation ? 'VALIDATION_ERROR' : 'INTERNAL_ERROR',
        message: err.message,
      },
    });
  }
});

router.delete('/relationships/:relId', async (req, res) => {
  try {
    const { relId } = req.params;
    const deleted = deleteFamilyRelationship(relId);
    if (!deleted) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Relationship not found',
        },
      });
    }
    res.json({
      success: true,
      data: { deleted: true },
    });
  } catch (err) {
    console.error('Delete relationship error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to delete relationship',
      },
    });
  }
});

export default router;
