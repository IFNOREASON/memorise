import { getStore, persist } from './store.js';
import { generateId, now } from '../utils/helpers.js';
import { RELATIONSHIP_TYPE } from '../constants.js';

function hasCircularReference(fromMemberId, toMemberId, type) {
  if (type === RELATIONSHIP_TYPE.SPOUSE) {
    return false;
  }

  if (type === RELATIONSHIP_TYPE.PARENT_CHILD) {
    return wouldCreateCycle(fromMemberId, toMemberId);
  }

  if (type === RELATIONSHIP_TYPE.SIBLING) {
    return false;
  }

  return false;
}

function wouldCreateCycle(parentId, childId) {
  if (parentId === childId) return true;

  const store = getStore();
  const visited = new Set();
  const stack = [parentId];

  while (stack.length > 0) {
    const current = stack.pop();
    if (current === childId) return true;
    if (visited.has(current)) continue;
    visited.add(current);

    Object.values(store.familyRelationships).forEach((rel) => {
      if (rel.type === RELATIONSHIP_TYPE.PARENT_CHILD && rel.toMemberId === current) {
        stack.push(rel.fromMemberId);
      }
    });
  }

  return false;
}

function validateRelationshipData(fromMemberId, toMemberId, type) {
  const errors = [];

  if (!fromMemberId || !toMemberId) {
    errors.push('fromMemberId and toMemberId are required');
  }

  if (fromMemberId === toMemberId) {
    errors.push('A member cannot have a relationship with themselves');
  }

  if (!Object.values(RELATIONSHIP_TYPE).includes(type)) {
    errors.push(`Invalid relationship type. Must be one of: ${Object.values(RELATIONSHIP_TYPE).join(', ')}`);
  }

  const store = getStore();
  if (fromMemberId && !store.familyMembers[fromMemberId]) {
    errors.push(`Member ${fromMemberId} does not exist`);
  }
  if (toMemberId && !store.familyMembers[toMemberId]) {
    errors.push(`Member ${toMemberId} does not exist`);
  }

  if (type === RELATIONSHIP_TYPE.SPOUSE) {
    Object.values(store.familyRelationships).forEach((rel) => {
      if (rel.type === RELATIONSHIP_TYPE.SPOUSE) {
        if (
          (rel.fromMemberId === fromMemberId && rel.toMemberId !== toMemberId) ||
          (rel.fromMemberId === toMemberId && rel.toMemberId !== fromMemberId)
        ) {
          if (rel.toMemberId !== toMemberId && rel.toMemberId !== fromMemberId) {
            errors.push('A member can only have one spouse');
          }
        }
      }
    });
  }

  return errors;
}

function relationshipExists(fromMemberId, toMemberId, type, excludeId = null) {
  const store = getStore();
  return Object.values(store.familyRelationships).some((rel) => {
    if (excludeId && rel.id === excludeId) return false;

    if (type === RELATIONSHIP_TYPE.SIBLING || type === RELATIONSHIP_TYPE.SPOUSE) {
      return (
        rel.type === type &&
        ((rel.fromMemberId === fromMemberId && rel.toMemberId === toMemberId) ||
          (rel.fromMemberId === toMemberId && rel.toMemberId === fromMemberId))
      );
    }

    return rel.type === type && rel.fromMemberId === fromMemberId && rel.toMemberId === toMemberId;
  });
}

export function createFamilyRelationship(relationshipData) {
  const store = getStore();
  const { fromMemberId, toMemberId, type } = relationshipData;

  const validationErrors = validateRelationshipData(fromMemberId, toMemberId, type);
  if (validationErrors.length > 0) {
    throw new Error(`Validation failed: ${validationErrors.join('; ')}`);
  }

  if (hasCircularReference(fromMemberId, toMemberId, type)) {
    throw new Error('Circular reference detected: this relationship would create a cycle in the family tree');
  }

  if (relationshipExists(fromMemberId, toMemberId, type)) {
    throw new Error('This relationship already exists');
  }

  const relId = generateId('rel');
  const relationship = {
    id: relId,
    fromMemberId,
    toMemberId,
    type,
    familyId: relationshipData.familyId || null,
    metadata: relationshipData.metadata || {},
    createdAt: now(),
    updatedAt: now(),
  };

  store.familyRelationships[relId] = relationship;
  persist();
  return relationship;
}

export function getFamilyRelationship(relId) {
  const store = getStore();
  return store.familyRelationships[relId] || null;
}

export function getRelationshipsByFamily(familyId, options = {}) {
  const store = getStore();
  const { type, memberId } = options;

  let relationships = Object.values(store.familyRelationships).filter(
    (r) => r.familyId === familyId
  );

  if (type) {
    relationships = relationships.filter((r) => r.type === type);
  }

  if (memberId) {
    relationships = relationships.filter(
      (r) => r.fromMemberId === memberId || r.toMemberId === memberId
    );
  }

  relationships.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
  return relationships;
}

export function getRelationshipsByMember(memberId) {
  const store = getStore();
  return Object.values(store.familyRelationships).filter(
    (r) => r.fromMemberId === memberId || r.toMemberId === memberId
  );
}

export function updateFamilyRelationship(relId, updates) {
  const store = getStore();
  const relationship = store.familyRelationships[relId];
  if (!relationship) return null;

  const { id, createdAt, ...updatableFields } = updates;
  const newFrom = updatableFields.fromMemberId || relationship.fromMemberId;
  const newTo = updatableFields.toMemberId || relationship.toMemberId;
  const newType = updatableFields.type || relationship.type;

  if (newFrom !== relationship.fromMemberId || newTo !== relationship.toMemberId || newType !== relationship.type) {
    const validationErrors = validateRelationshipData(newFrom, newTo, newType);
    if (validationErrors.length > 0) {
      throw new Error(`Validation failed: ${validationErrors.join('; ')}`);
    }

    if (hasCircularReference(newFrom, newTo, newType)) {
      throw new Error('Circular reference detected: this relationship would create a cycle in the family tree');
    }

    if (relationshipExists(newFrom, newTo, newType, relId)) {
      throw new Error('This relationship already exists');
    }
  }

  const updated = { ...relationship, ...updatableFields, updatedAt: now() };
  store.familyRelationships[relId] = updated;
  persist();
  return updated;
}

export function deleteFamilyRelationship(relId) {
  const store = getStore();
  if (!store.familyRelationships[relId]) return false;
  delete store.familyRelationships[relId];
  persist();
  return true;
}

export function getFamilyTreeData(familyId) {
  const store = getStore();
  const members = Object.values(store.familyMembers).filter((m) => m.familyId === familyId);
  const relationships = Object.values(store.familyRelationships).filter(
    (r) => r.familyId === familyId
  );

  const childrenOf = {};
  const spouseOf = {};
  const siblingOf = {};

  relationships.forEach((rel) => {
    if (rel.type === RELATIONSHIP_TYPE.PARENT_CHILD) {
      if (!childrenOf[rel.fromMemberId]) childrenOf[rel.fromMemberId] = [];
      childrenOf[rel.fromMemberId].push(rel.toMemberId);
    } else if (rel.type === RELATIONSHIP_TYPE.SPOUSE) {
      if (!spouseOf[rel.fromMemberId]) spouseOf[rel.fromMemberId] = [];
      spouseOf[rel.fromMemberId].push(rel.toMemberId);
      if (!spouseOf[rel.toMemberId]) spouseOf[rel.toMemberId] = [];
      spouseOf[rel.toMemberId].push(rel.fromMemberId);
    } else if (rel.type === RELATIONSHIP_TYPE.SIBLING) {
      if (!siblingOf[rel.fromMemberId]) siblingOf[rel.fromMemberId] = [];
      siblingOf[rel.fromMemberId].push(rel.toMemberId);
      if (!siblingOf[rel.toMemberId]) siblingOf[rel.toMemberId] = [];
      siblingOf[rel.toMemberId].push(rel.fromMemberId);
    }
  });

  const childSet = new Set();
  Object.values(childrenOf).forEach((children) => {
    children.forEach((c) => childSet.add(c));
  });

  const rootMembers = members.filter((m) => !childSet.has(m.id));

  return {
    members,
    relationships,
    rootMembers: rootMembers.map((m) => m.id),
    childrenOf,
    spouseOf,
    siblingOf,
  };
}
