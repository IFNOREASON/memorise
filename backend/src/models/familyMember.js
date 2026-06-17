import { getStore, persist } from './store.js';
import { generateId, now } from '../utils/helpers.js';

export function createFamilyMember(memberData) {
  const store = getStore();
  const memberId = generateId('member');
  const member = {
    id: memberId,
    userId: memberData.userId || 'default_user',
    familyId: memberData.familyId || null,
    name: memberData.name || '',
    birthDate: memberData.birthDate || null,
    deathDate: memberData.deathDate || null,
    avatar: memberData.avatar || '',
    bio: memberData.bio || '',
    gender: memberData.gender || null,
    generation: memberData.generation || null,
    metadata: memberData.metadata || {},
    createdAt: now(),
    updatedAt: now(),
  };

  store.familyMembers[memberId] = member;
  persist();
  return member;
}

export function getFamilyMember(memberId) {
  const store = getStore();
  return store.familyMembers[memberId] || null;
}

export function getFamilyMembers(familyId, options = {}) {
  const store = getStore();
  const { limit = 50, offset = 0, generation } = options;

  let members = Object.values(store.familyMembers).filter((m) => m.familyId === familyId);

  if (generation !== undefined && generation !== null) {
    members = members.filter((m) => m.generation === generation);
  }

  members.sort((a, b) => {
    if (a.generation !== null && b.generation !== null) {
      if (a.generation !== b.generation) return a.generation - b.generation;
    }
    if (a.birthDate && b.birthDate) {
      return new Date(a.birthDate) - new Date(b.birthDate);
    }
    return new Date(a.createdAt) - new Date(b.createdAt);
  });

  return {
    total: members.length,
    items: members.slice(offset, offset + limit),
  };
}

export function getAllFamilyMembers(familyId) {
  const store = getStore();
  return Object.values(store.familyMembers).filter((m) => m.familyId === familyId);
}

export function updateFamilyMember(memberId, updates) {
  const store = getStore();
  const member = store.familyMembers[memberId];
  if (!member) return null;

  const { id, userId, createdAt, ...updatableFields } = updates;
  const updated = { ...member, ...updatableFields, updatedAt: now() };
  store.familyMembers[memberId] = updated;
  persist();
  return updated;
}

export function deleteFamilyMember(memberId) {
  const store = getStore();
  if (!store.familyMembers[memberId]) return false;

  Object.keys(store.familyRelationships).forEach((relId) => {
    const rel = store.familyRelationships[relId];
    if (rel.fromMemberId === memberId || rel.toMemberId === memberId) {
      delete store.familyRelationships[relId];
    }
  });

  delete store.familyMembers[memberId];
  persist();
  return true;
}
