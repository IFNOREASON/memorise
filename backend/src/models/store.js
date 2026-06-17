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

function loadStore() {
  ensureDataDir();
  if (!fs.existsSync(DATA_FILE)) {
    return {
      tasks: {},
      taskItems: {},
      taskLogs: {},
      galleries: {},
      familyMemories: {},
      messages: {},
      pushRules: {},
      logs: [],
    };
  }
  try {
    const content = fs.readFileSync(DATA_FILE, 'utf-8');
    return JSON.parse(content);
  } catch {
    return {
      tasks: {},
      taskItems: {},
      taskLogs: {},
      galleries: {},
      familyMemories: {},
      messages: {},
      pushRules: {},
      logs: [],
    };
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
  store = {
    tasks: {},
    taskItems: {},
    taskLogs: {},
    galleries: {},
    familyMemories: {},
    messages: {},
    pushRules: {},
    logs: [],
  };
  persist();
}

export default {
  getStore,
  persist,
  resetStore,
};
