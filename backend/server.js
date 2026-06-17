import express from 'express';
import cors from 'cors';
import { createServer } from 'http';
import { initWebSocket } from './src/services/webSocketService.js';
import { initTaskServices } from './src/services/taskService.js';
import tasksRouter from './src/routes/tasks.js';
import messagesRouter from './src/routes/messages.js';
import galleryRouter from './src/routes/gallery.js';
import familyMemoriesRouter from './src/routes/familyMemories.js';
import familyTreeRouter from './src/routes/familyTree.js';

const app = express();
const server = createServer(app);
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json({ limit: '50mb' }));

app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Memorise backend is running' });
});

app.get('/api/test', (req, res) => {
  res.json({ message: 'Hello from Memorise API!' });
});

app.use('/api/tasks', tasksRouter);
app.use('/api/messages', messagesRouter);
app.use('/api/gallery', galleryRouter);
app.use('/api/family-memories', familyMemoriesRouter);
app.use('/api/family-tree', familyTreeRouter);

app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({
    success: false,
    error: {
      code: 'INTERNAL_ERROR',
      message: 'Internal server error',
    },
  });
});

app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: {
      code: 'NOT_FOUND',
      message: 'Endpoint not found',
    },
  });
});

initWebSocket(server);

initTaskServices();

server.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
  console.log(`WebSocket available at ws://localhost:${PORT}/ws`);
});
