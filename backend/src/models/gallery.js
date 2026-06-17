import { getStore, persist } from './store.js';
import { generateId, now } from '../utils/helpers.js';
import { GALLERY_SOURCE } from '../constants.js';

export function createGalleryPhoto(photoData) {
  const store = getStore();
  const photoId = generateId('photo');
  const photo = {
    id: photoId,
    userId: photoData.userId || 'default_user',
    familyId: photoData.familyId || null,
    memberId: photoData.memberId || null,
    title: photoData.title || '',
    description: photoData.description || '',
    imageUrl: photoData.imageUrl,
    thumbnailUrl: photoData.thumbnailUrl || photoData.imageUrl,
    source: photoData.source || GALLERY_SOURCE.UPLOAD,
    sourceTaskId: photoData.sourceTaskId || null,
    sourceItemId: photoData.sourceItemId || null,
    originalPhotoId: photoData.originalPhotoId || null,
    repairedPhotoId: photoData.repairedPhotoId || null,
    isRepaired: photoData.isRepaired || false,
    isAIGenerated: photoData.isAIGenerated || false,
    tags: photoData.tags || [],
    metadata: photoData.metadata || {},
    createdAt: now(),
    updatedAt: now(),
  };

  store.galleries[photoId] = photo;
  persist();
  return photo;
}

export function getGalleryPhoto(photoId) {
  const store = getStore();
  return store.galleries[photoId] || null;
}

export function getGalleryByMember(memberId, options = {}) {
  const store = getStore();
  const { limit = 50, offset = 0, source, isRepaired } = options;

  let photos = Object.values(store.galleries).filter((p) => p.memberId === memberId);

  if (source) {
    photos = photos.filter((p) => p.source === source);
  }
  if (isRepaired !== undefined) {
    photos = photos.filter((p) => p.isRepaired === isRepaired);
  }

  photos.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  return {
    total: photos.length,
    items: photos.slice(offset, offset + limit),
  };
}

export function getGalleryByFamily(familyId, options = {}) {
  const store = getStore();
  const { limit = 50, offset = 0 } = options;

  let photos = Object.values(store.galleries).filter((p) => p.familyId === familyId);
  photos.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  return {
    total: photos.length,
    items: photos.slice(offset, offset + limit),
  };
}

export function updateGalleryPhoto(photoId, updates) {
  const store = getStore();
  const photo = store.galleries[photoId];
  if (!photo) return null;

  const updated = { ...photo, ...updates, updatedAt: now() };
  store.galleries[photoId] = updated;
  persist();
  return updated;
}

export function linkRepairedPhoto(originalPhotoId, repairedPhotoId) {
  updateGalleryPhoto(originalPhotoId, { repairedPhotoId });
  updateGalleryPhoto(repairedPhotoId, { originalPhotoId, isRepaired: true });
}

export function deleteGalleryPhoto(photoId) {
  const store = getStore();
  if (!store.galleries[photoId]) return false;
  delete store.galleries[photoId];
  persist();
  return true;
}
