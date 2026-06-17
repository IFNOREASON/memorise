import { delay } from '../utils/helpers.js';

const MOCK_RATE_LIMIT_CHANCE = 0.08;
const MOCK_TIMEOUT_CHANCE = 0.05;

export const GENERATION_TYPE = {
  SCENE: 'scene',
  PORTRAIT: 'portrait',
  ANIMATION: 'animation',
  DIGITAL_HUMAN: 'digital_human',
  FINE_TUNE: 'fine_tune',
};

export const SCENE_STYLES = {
  REALISTIC: 'realistic',
  OIL_PAINTING: 'oil_painting',
  WATERCOLOR: 'watercolor',
  ANIME: 'anime',
  VINTAGE: 'vintage',
  INK: 'ink',
};

export async function generateScene(prompt, options = {}) {
  const {
    style = SCENE_STYLES.REALISTIC,
    width = 1024,
    height = 1024,
    numImages = 1,
    referenceImages = [],
    characterDescription = '',
  } = options;

  const processingTime = 2000 + Math.random() * 3000;
  await delay(processingTime);

  if (Math.random() < MOCK_RATE_LIMIT_CHANCE) {
    const error = new Error('Rate limit exceeded for generation API');
    error.code = 'RATE_LIMIT_EXCEEDED';
    error.status = 429;
    throw error;
  }

  if (Math.random() < MOCK_TIMEOUT_CHANCE) {
    const error = new Error('Generation service timeout');
    error.code = 'REQUEST_TIMEOUT';
    error.status = 504;
    throw error;
  }

  const images = [];
  for (let i = 0; i < numImages; i++) {
    images.push({
      id: `gen_${Date.now()}_${i}`,
      url: `https://api.mock-ai-generation.com/output/scene_${style}_${Date.now()}_${i}.jpg`,
      thumbnailUrl: `https://api.mock-ai-generation.com/output/scene_${style}_${Date.now()}_${i}_thumb.jpg`,
      width,
      height,
      seed: Math.floor(Math.random() * 1000000),
      prompt,
      style,
    });
  }

  return {
    images,
    prompt,
    style,
    settings: {
      width,
      height,
      numImages,
      referenceImages: referenceImages.length,
      characterDescription,
    },
    processingTime: Math.round(processingTime),
    generatedAt: new Date().toISOString(),
  };
}

export async function generatePortrait(referenceImage, options = {}) {
  const {
    style = SCENE_STYLES.REALISTIC,
    expression = 'neutral',
    age = null,
    clothing = '',
    background = '',
  } = options;

  const processingTime = 2500 + Math.random() * 2000;
  await delay(processingTime);

  return {
    originalImage: referenceImage,
    generatedUrl: `https://api.mock-ai-generation.com/output/portrait_${style}_${Date.now()}.jpg`,
    thumbnailUrl: `https://api.mock-ai-generation.com/output/portrait_${style}_${Date.now()}_thumb.jpg`,
    style,
    settings: {
      expression,
      age,
      clothing,
      background,
    },
    quality: Math.floor(Math.random() * 15) + 85,
    generatedAt: new Date().toISOString(),
  };
}

export async function generateAnimation(referenceImages, options = {}) {
  const {
    duration = 3,
    motion = 'subtle',
    fps = 24,
  } = options;

  const processingTime = 5000 + Math.random() * 5000;
  await delay(processingTime);

  return {
    videoUrl: `https://api.mock-ai-generation.com/output/animation_${Date.now()}.mp4`,
    thumbnailUrl: `https://api.mock-ai-generation.com/output/animation_${Date.now()}_thumb.jpg`,
    duration,
    motion,
    fps,
    referenceImages: referenceImages.length,
    generatedAt: new Date().toISOString(),
  };
}

export async function createDigitalHuman(referenceImages, options = {}) {
  const {
    name = '',
    gender = 'unknown',
    ageRange = '',
    description = '',
  } = options;

  const processingTime = 8000 + Math.random() * 7000;
  await delay(processingTime);

  return {
    digitalHumanId: `dh_${Date.now()}`,
    name,
    gender,
    ageRange,
    description,
    avatarUrl: `https://api.mock-ai-generation.com/output/digital_human_${Date.now()}.jpg`,
    status: 'training',
    trainingProgress: 0,
    referenceImages: referenceImages.length,
    createdAt: new Date().toISOString(),
  };
}

export async function fineTuneModel(digitalHumanId, trainingData, options = {}) {
  const {
    epochs = 100,
    learningRate = 0.0001,
    priority = 'standard',
  } = options;

  const processingTime = 10000 + Math.random() * 10000;
  await delay(processingTime);

  return {
    digitalHumanId,
    fineTuneJobId: `ft_${Date.now()}`,
    status: 'completed',
    epochs,
    finalLoss: 0.023 + Math.random() * 0.05,
    accuracy: 0.92 + Math.random() * 0.07,
    trainingSamples: trainingData.length,
    completedAt: new Date().toISOString(),
  };
}

export async function getGenerationStatus(jobId) {
  return {
    jobId,
    status: 'completed',
    progress: 100,
    result: null,
  };
}

export default {
  generateScene,
  generatePortrait,
  generateAnimation,
  createDigitalHuman,
  fineTuneModel,
  getGenerationStatus,
  GENERATION_TYPE,
  SCENE_STYLES,
};
