import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, '../../data');
const DATA_FILE = path.join(DATA_DIR, 'store.json');

function ensureDataDir() {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

const DEFAULT_STORE = {
  tasks: {},
  taskItems: {},
  taskLogs: {},
  galleries: {},
  familyMemories: {},
  familyMembers: {},
  familyRelationships: {},
  messages: {},
  pushRules: {},
  logs: [],
};

function migrateStore(loaded) {
  const store = { ...loaded };
  for (const key of Object.keys(DEFAULT_STORE)) {
    if (store[key] === undefined || store[key] === null) {
      store[key] = DEFAULT_STORE[key];
    }
  }
  return store;
}

function loadStore() {
  ensureDataDir();
  if (!fs.existsSync(DATA_FILE)) {
    return { ...DEFAULT_STORE };
  }
  try {
    const content = fs.readFileSync(DATA_FILE, 'utf-8');
    return migrateStore(JSON.parse(content));
  } catch {
    return { ...DEFAULT_STORE };
  }
}

function saveStore(store) {
  ensureDataDir();
  fs.writeFileSync(DATA_FILE, JSON.stringify(store, null, 2), 'utf-8');
}

let store = loadStore();

export function getStore() {
  return store;
}

export function persist() {
  saveStore(store);
}

export function resetStore() {
  store = { ...DEFAULT_STORE };
  persist();
}

export default {
  getStore,
  persist,
  resetStore,
};
