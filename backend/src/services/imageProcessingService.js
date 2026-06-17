import { delay } from '../utils/helpers.js';

const MOCK_RATE_LIMIT_CHANCE = 0.1;
const MOCK_TIMEOUT_CHANCE = 0.05;
const MOCK_INVALID_FORMAT_CHANCE = 0.03;
const MOCK_PROCESSING_TIME_MS = 1500;

export const REPAIR_MODES = {
  BASIC: 'basic',
  ENHANCE: 'enhance',
  COLORIZE: 'colorize',
  FULL: 'full',
};

export async function repairImage(imageUrl, options = {}) {
  const {
    mode = REPAIR_MODES.FULL,
    enableScratchRemoval = true,
    enableColorize = true,
    enableFaceEnhance = true,
    targetResolution = '1080p',
  } = options;

  await delay(MOCK_PROCESSING_TIME_MS + Math.random() * 1000);

  if (Math.random() < MOCK_RATE_LIMIT_CHANCE) {
    const error = new Error('Rate limit exceeded, please try again later');
    error.code = 'RATE_LIMIT_EXCEEDED';
    error.status = 429;
    throw error;
  }

  if (Math.random() < MOCK_TIMEOUT_CHANCE) {
    const error = new Error('Request timeout');
    error.code = 'REQUEST_TIMEOUT';
    error.status = 504;
    throw error;
  }

  if (Math.random() < MOCK_INVALID_FORMAT_CHANCE) {
    const error = new Error('Invalid image format');
    error.code = 'INVALID_IMAGE_FORMAT';
    error.status = 400;
    throw error;
  }

  const repairedUrl = generateMockRepairedUrl(imageUrl, mode);

  return {
    originalUrl: imageUrl,
    repairedUrl,
    thumbnailUrl: repairedUrl + '&thumb=true',
    mode,
    settings: {
      enableScratchRemoval,
      enableColorize,
      enableFaceEnhance,
      targetResolution,
    },
    stats: {
      scratchesRemoved: Math.floor(Math.random() * 50) + 10,
      facesEnhanced: Math.floor(Math.random() * 5) + 1,
      colorConfidence: Math.floor(Math.random() * 20) + 80,
      resolution: targetResolution,
    },
    processedAt: new Date().toISOString(),
  };
}

export async function batchRepairImages(images, options = {}) {
  const results = [];
  const errors = [];

  for (let i = 0; i < images.length; i++) {
    try {
      const result = await repairImage(images[i].url, options);
      results.push({
        index: i,
        original: images[i],
        result,
        success: true,
      });
    } catch (error) {
      errors.push({
        index: i,
        original: images[i],
        error: {
          message: error.message,
          code: error.code,
          status: error.status,
        },
        success: false,
      });
    }
  }

  return { results, errors, total: images.length };
}

function generateMockRepairedUrl(originalUrl, mode) {
  const baseUrl = 'https://api.mock-alibaba-vision.com/repair';
  const timestamp = Date.now();
  const modeSuffix = mode === REPAIR_MODES.COLORIZE
    ? '_colorized'
    : mode === REPAIR_MODES.ENHANCE
    ? '_enhanced'
    : '_repaired';
  return `${baseUrl}/output/${encodeURIComponent(originalUrl)}${modeSuffix}_${timestamp}.jpg`;
}

export async function enhanceFace(imageUrl, options = {}) {
  await delay(800 + Math.random() * 500);

  return {
    originalUrl: imageUrl,
    enhancedUrl: imageUrl + '&enhanced=face',
    facesDetected: Math.floor(Math.random() * 5) + 1,
    settings: options,
  };
}

export async function colorizeImage(imageUrl, options = {}) {
  await delay(1000 + Math.random() * 800);

  return {
    originalUrl: imageUrl,
    colorizedUrl: imageUrl + '&colorized=true',
    colorConfidence: Math.floor(Math.random() * 20) + 80,
    settings: options,
  };
}

export default {
  repairImage,
  batchRepairImages,
  enhanceFace,
  colorizeImage,
  REPAIR_MODES,
};
