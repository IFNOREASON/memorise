import { Router } from 'express';
import {
  getGalleryByMember,
  getGalleryByFamily,
  getGalleryPhoto,
  createGalleryPhoto,
  updateGalleryPhoto,
  deleteGalleryPhoto,
} from '../models/gallery.js';
import { GALLERY_SOURCE } from '../constants.js';

const router = Router();

function getUserId(req) {
  return req.headers['x-user-id'] || req.query.userId || 'default_user';
}

router.get('/member/:memberId', async (req, res) => {
  try {
    const { memberId } = req.params;
    const { limit = 50, offset = 0, source, isRepaired } = req.query;
    const result = getGalleryByMember(memberId, {
      limit: parseInt(limit),
      offset: parseInt(offset),
      source,
      isRepaired: isRepaired !== undefined ? isRepaired === 'true' : undefined,
    });
    res.json({
      success: true,
      data: result,
    });
  } catch (err) {
    console.error('Get gallery by member error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to get gallery',
      },
    });
  }
});

router.get('/family/:familyId', async (req, res) => {
  try {
    const { familyId } = req.params;
    const { limit = 50, offset = 0 } = req.query;
    const result = getGalleryByFamily(familyId, {
      limit: parseInt(limit),
      offset: parseInt(offset),
    });
    res.json({
      success: true,
      data: result,
    });
  } catch (err) {
    console.error('Get gallery by family error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to get gallery',
      },
    });
  }
});

router.get('/:photoId', async (req, res) => {
  try {
    const { photoId } = req.params;
    const photo = getGalleryPhoto(photoId);
    if (!photo) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Photo not found',
        },
      });
    }
    res.json({
      success: true,
      data: photo,
    });
  } catch (err) {
    console.error('Get gallery photo error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to get photo',
      },
    });
  }
});

router.post('/', async (req, res) => {
  try {
    const userId = getUserId(req);
    const photoData = { ...req.body, userId };
    const photo = createGalleryPhoto(photoData);
    res.status(201).json({
      success: true,
      data: photo,
    });
  } catch (err) {
    console.error('Create gallery photo error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to create photo',
      },
    });
  }
});

router.put('/:photoId', async (req, res) => {
  try {
    const { photoId } = req.params;
    const photo = updateGalleryPhoto(photoId, req.body);
    if (!photo) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Photo not found',
        },
      });
    }
    res.json({
      success: true,
      data: photo,
    });
  } catch (err) {
    console.error('Update gallery photo error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to update photo',
      },
    });
  }
});

router.delete('/:photoId', async (req, res) => {
  try {
    const { photoId } = req.params;
    const deleted = deleteGalleryPhoto(photoId);
    if (!deleted) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'NOT_FOUND',
          message: 'Photo not found',
        },
      });
    }
    res.json({
      success: true,
      data: { deleted: true },
    });
  } catch (err) {
    console.error('Delete gallery photo error:', err);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: err.message || 'Failed to delete photo',
      },
    });
  }
});

export default router;
