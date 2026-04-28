import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));

const CONFIG_FILE = path.join(__dirname, 'config.json');
const DATA_FILE = path.join(__dirname, 'data.json');

let config = {
  openai: {
    apiKey: '',
    baseUrl: 'https://api.openai.com/v1',
    model: 'gpt-4o'
  },
  aliyun: {
    apiKey: '',
    baseUrl: 'https://dashscope.aliyuncs.com/api/v1',
    imageModel: 'wanx-v1',
    textModel: 'qwen-plus'
  }
};

let data = {
  avatars: [],
  generationTasks: [],
  memories: [],
  voiceMaterials: [],
  voiceModels: [],
  voiceSynthesisTasks: []
};

function loadConfig() {
  if (fs.existsSync(CONFIG_FILE)) {
    try {
      const content = fs.readFileSync(CONFIG_FILE, 'utf-8');
      config = { ...config, ...JSON.parse(content) };
    } catch (error) {
      console.error('加载配置失败:', error);
    }
  }
}

function saveConfig() {
  try {
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2), 'utf-8');
  } catch (error) {
    console.error('保存配置失败:', error);
  }
}

function loadData() {
  if (fs.existsSync(DATA_FILE)) {
    try {
      const content = fs.readFileSync(DATA_FILE, 'utf-8');
      data = { ...data, ...JSON.parse(content) };
    } catch (error) {
      console.error('加载数据失败:', error);
    }
  }
}

function saveData() {
  try {
    fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf-8');
  } catch (error) {
    console.error('保存数据失败:', error);
  }
}

loadConfig();
loadData();

class AIService {
  async analyzePhotoWithAliyun(imageBase64) {
    if (!config.aliyun.apiKey) {
      throw new Error('阿里云 API Key 未配置');
    }

    try {
      const response = await fetch(`${config.aliyun.baseUrl}/services/aistudio/face-detection`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${config.aliyun.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'face-detection',
          input: {
            image_url: imageBase64.startsWith('data:') ? imageBase64 : `data:image/jpeg;base64,${imageBase64}`
          }
        })
      });

      if (!response.ok) {
        const error = await response.text();
        console.error('阿里云人脸检测失败:', error);
        return this.simulateFaceDetection(imageBase64);
      }

      const result = await response.json();
      return this.parseFaceDetectionResult(result);
    } catch (error) {
      console.error('调用阿里云 API 失败:', error);
      return this.simulateFaceDetection(imageBase64);
    }
  }

  async analyzePhotoWithOpenAI(imageBase64) {
    if (!config.openai.apiKey) {
      throw new Error('OpenAI API Key 未配置');
    }

    try {
      const base64Data = imageBase64.replace(/^data:image\/\w+;base64,/, '');

      const response = await fetch(`${config.openai.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${config.openai.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: config.openai.model || 'gpt-4o',
          messages: [
            {
              role: 'user',
              content: [
                {
                  type: 'text',
                  text: `请分析这张人脸照片，返回以下信息（JSON格式）：
1. faceAngle: 检测人脸角度，可选值：front（正面）、left（左侧面）、right（右侧面）、back（背面）、closeup（特写）
2. confidence: 检测置信度，0-1之间的浮点数
3. qualityScore: 照片质量评分，0-100的整数
4. features: 检测到的面部特征列表，例如：["面部轮廓清晰", "五官特征明显", "光线充足"]
5. faceAngleLabel: 角度的中文描述，例如："正面"

只返回JSON，不要有其他内容。`
                },
                {
                  type: 'image_url',
                  image_url: {
                    url: `data:image/jpeg;base64,${base64Data}`
                  }
                }
              ]
            }
          ],
          max_tokens: 500
        })
      });

      if (!response.ok) {
        const error = await response.text();
        console.error('OpenAI API 失败:', error);
        return this.simulateFaceDetection(imageBase64);
      }

      const result = await response.json();
      const content = result.choices[0]?.message?.content || '';

      try {
        const jsonMatch = content.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const parsed = JSON.parse(jsonMatch[0]);
          return {
            faceAngle: parsed.faceAngle || 'front',
            faceAngleLabel: parsed.faceAngleLabel || this.getAngleLabel(parsed.faceAngle),
            confidence: parsed.confidence || 0.85,
            qualityScore: parsed.qualityScore || 80,
            features: parsed.features || ['面部轮廓清晰', '五官特征明显']
          };
        }
      } catch (e) {
        console.error('解析 OpenAI 响应失败:', e);
      }

      return this.simulateFaceDetection(imageBase64);
    } catch (error) {
      console.error('调用 OpenAI API 失败:', error);
      return this.simulateFaceDetection(imageBase64);
    }
  }

  simulateFaceDetection(imageBase64) {
    const angles = ['front', 'left', 'right', 'back', 'closeup'];
    const angleLabels = {
      front: '正面',
      left: '左侧面',
      right: '右侧面',
      back: '背面',
      closeup: '特写'
    };

    const hash = this.simpleHash(imageBase64.substring(0, 100));
    const angleIndex = hash % angles.length;
    const angle = angles[angleIndex];

    return {
      faceAngle: angle,
      faceAngleLabel: angleLabels[angle],
      confidence: 0.75 + Math.random() * 0.2,
      qualityScore: 70 + Math.floor(Math.random() * 30),
      features: ['面部轮廓清晰', '五官特征明显', '光线充足']
    };
  }

  simpleHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return Math.abs(hash);
  }

  getAngleLabel(angle) {
    const labels = {
      front: '正面',
      left: '左侧面',
      right: '右侧面',
      back: '背面',
      closeup: '特写'
    };
    return labels[angle] || '正面';
  }

  async generateImageWithAliyun(prompt, negativePrompt = '') {
    if (!config.aliyun.apiKey) {
      throw new Error('阿里云 API Key 未配置');
    }

    try {
      const response = await fetch(`${config.aliyun.baseUrl}/services/aigc/text2image/image-synthesis`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${config.aliyun.apiKey}`,
          'Content-Type': 'application/json',
          'X-DashScope-Async': 'enable'
        },
        body: JSON.stringify({
          model: config.aliyun.imageModel || 'wanx-v1',
          input: {
            prompt: prompt,
            negative_prompt: negativePrompt || '模糊, 低质量, 变形, 丑陋'
          },
          parameters: {
            style: '<portrait>',
            size: '1024*1024',
            n: 1
          }
        })
      });

      if (!response.ok) {
        const error = await response.text();
        console.error('阿里云图像生成失败:', error);
        return null;
      }

      const result = await response.json();
      return {
        taskId: result.output?.task_id || result.task_id,
        status: 'pending'
      };
    } catch (error) {
      console.error('调用阿里云图像生成 API 失败:', error);
      return null;
    }
  }

  async checkAliyunImageTask(taskId) {
    if (!config.aliyun.apiKey) {
      throw new Error('阿里云 API Key 未配置');
    }

    try {
      const response = await fetch(`${config.aliyun.baseUrl}/tasks/${taskId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${config.aliyun.apiKey}`
        }
      });

      if (!response.ok) {
        return { status: 'failed' };
      }

      const result = await response.json();
      return {
        status: result.output?.task_status || result.task_status,
        imageUrl: result.output?.results?.[0]?.url || result.output?.image_url
      };
    } catch (error) {
      console.error('查询阿里云任务状态失败:', error);
      return { status: 'failed' };
    }
  }

  async generateTextWithOpenAI(prompt) {
    if (!config.openai.apiKey) {
      throw new Error('OpenAI API Key 未配置');
    }

    try {
      const response = await fetch(`${config.openai.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${config.openai.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: config.openai.model || 'gpt-4o',
          messages: [
            {
              role: 'system',
              content: '你是一个专业的数字人生成助手，帮助用户生成详细的人物描述用于图像生成。'
            },
            {
              role: 'user',
              content: prompt
            }
          ],
          max_tokens: 1000
        })
      });

      if (!response.ok) {
        const error = await response.text();
        console.error('OpenAI 文本生成失败:', error);
        return null;
      }

      const result = await response.json();
      return result.choices[0]?.message?.content || null;
    } catch (error) {
      console.error('调用 OpenAI 文本生成 API 失败:', error);
      return null;
    }
  }

  async generateImagePromptFromDescription(description, gender, ageRange) {
    const prompt = `根据以下描述，生成一个用于AI图像生成的详细英文提示词：

人物描述：${description}
性别：${gender === 'male' ? '男性' : '女性'}
年龄段：${ageRange}

请生成一个详细的英文提示词，包含：
1. 人物的外貌特征
2. 面部特征细节
3. 表情和神态
4. 服装风格
5. 背景和光线
6. 艺术风格建议

只返回英文提示词，不要有其他内容。`;

    const result = await this.generateTextWithOpenAI(prompt);
    if (result) {
      return result;
    }

    return this.simulateImagePrompt(description, gender, ageRange);
  }

  simulateImagePrompt(description, gender, ageRange) {
    const genderTerm = gender === 'male' ? 'man' : 'woman';
    return `A realistic portrait of a ${ageRange} ${genderTerm}, ${description}, professional photography, studio lighting, highly detailed face, sharp focus, high quality, 8k resolution, natural skin texture, warm color tone`;
  }

  async fineTuneAvatar(avatarId, adjustments) {
    const avatar = data.avatars.find(a => a.id === avatarId);
    if (!avatar) {
      throw new Error('数字人不存在');
    }

    avatar.fineTuneAdjustments = adjustments;
    avatar.status = 'fine-tuning';
    avatar.progress = 0;
    saveData();

    setTimeout(() => {
      const foundAvatar = data.avatars.find(a => a.id === avatarId);
      if (foundAvatar) {
        foundAvatar.status = 'active';
        foundAvatar.progress = 100;
        foundAvatar.fineTunedAt = new Date().toISOString();
        saveData();
      }
    }, 5000);

    return {
      success: true,
      avatarId,
      status: 'fine-tuning'
    };
  }
}

const aiService = new AIService();

class VoiceService {
  createVoiceMaterial(avatarId, name, type, format, duration, size, audioData) {
    const materialId = `voice_material_${Date.now()}`;
    const now = new Date().toISOString();

    const newMaterial = {
      id: materialId,
      avatarId,
      name,
      type: type || 'upload',
      format: format || 'wav',
      duration: duration || 0,
      size: size || 0,
      audioData: audioData || null,
      status: 'raw',
      transcription: '',
      qualityScore: 0,
      preprocessInfo: null,
      createdAt: now,
      updatedAt: now
    };

    data.voiceMaterials.push(newMaterial);
    saveData();

    return newMaterial;
  }

  getVoiceMaterials(avatarId) {
    if (avatarId) {
      return data.voiceMaterials.filter(m => m.avatarId === avatarId);
    }
    return data.voiceMaterials;
  }

  getVoiceMaterial(materialId) {
    return data.voiceMaterials.find(m => m.id === materialId);
  }

  updateVoiceMaterial(materialId, updates) {
    const material = data.voiceMaterials.find(m => m.id === materialId);
    if (!material) {
      return null;
    }

    if (updates.name !== undefined) material.name = updates.name;
    if (updates.status !== undefined) material.status = updates.status;
    if (updates.transcription !== undefined) material.transcription = updates.transcription;
    if (updates.qualityScore !== undefined) material.qualityScore = updates.qualityScore;
    if (updates.preprocessInfo !== undefined) material.preprocessInfo = updates.preprocessInfo;

    material.updatedAt = new Date().toISOString();
    saveData();

    return material;
  }

  deleteVoiceMaterial(materialId) {
    const index = data.voiceMaterials.findIndex(m => m.id === materialId);
    if (index === -1) {
      return false;
    }

    data.voiceMaterials.splice(index, 1);
    saveData();
    return true;
  }

  preprocessAudio(materialId) {
    const material = this.getVoiceMaterial(materialId);
    if (!material) {
      return null;
    }

    material.status = 'preprocessing';
    material.updatedAt = new Date().toISOString();
    saveData();

    setTimeout(() => {
      const foundMaterial = data.voiceMaterials.find(m => m.id === materialId);
      if (foundMaterial) {
        foundMaterial.status = 'preprocessed';
        foundMaterial.qualityScore = 70 + Math.floor(Math.random() * 30);
        foundMaterial.preprocessInfo = {
          noiseReduction: 'applied',
          volumeNormalized: true,
          silenceRemoved: true,
          formatConverted: 'wav',
          processedAt: new Date().toISOString()
        };
        foundMaterial.updatedAt = new Date().toISOString();
        saveData();
      }
    }, 3000);

    return material;
  }

  batchPreprocess(materialIds) {
    const results = [];
    for (const materialId of materialIds) {
      const result = this.preprocessAudio(materialId);
      results.push({
        materialId,
        success: !!result,
        status: result ? result.status : 'failed'
      });
    }
    return results;
  }

  createVoiceModel(avatarId, name, materialIds, config) {
    const modelId = `voice_model_${Date.now()}`;
    const now = new Date().toISOString();

    const newModel = {
      id: modelId,
      avatarId,
      name,
      status: 'training',
      progress: 0,
      trainingConfig: config || {
        epochs: 100,
        batchSize: 16,
        learningRate: 0.0001
      },
      materialIds: materialIds || [],
      modelPath: null,
      sampleAudioPath: null,
      qualityMetrics: null,
      createdAt: now,
      updatedAt: now
    };

    data.voiceModels.push(newModel);
    saveData();

    this.simulateTraining(modelId);

    return newModel;
  }

  simulateTraining(modelId) {
    let progress = 0;

    const interval = setInterval(() => {
      progress += 5;

      const model = data.voiceModels.find(m => m.id === modelId);
      if (!model) {
        clearInterval(interval);
        return;
      }

      model.progress = Math.min(progress, 100);

      if (progress >= 100) {
        model.status = 'ready';
        model.qualityMetrics = {
          mos: 3.8 + Math.random() * 0.8,
          similarity: 75 + Math.floor(Math.random() * 20),
          naturalness: 70 + Math.floor(Math.random() * 25)
        };
        model.updatedAt = new Date().toISOString();

        const avatar = data.avatars.find(a => a.id === model.avatarId);
        if (avatar) {
          avatar.voiceModelId = modelId;
          avatar.voiceEnabled = true;
        }

        clearInterval(interval);
      }

      saveData();
    }, 1000);
  }

  getVoiceModels(avatarId) {
    if (avatarId) {
      return data.voiceModels.filter(m => m.avatarId === avatarId);
    }
    return data.voiceModels;
  }

  getVoiceModel(modelId) {
    return data.voiceModels.find(m => m.id === modelId);
  }

  deleteVoiceModel(modelId) {
    const index = data.voiceModels.findIndex(m => m.id === modelId);
    if (index === -1) {
      return false;
    }

    const model = data.voiceModels[index];

    const avatar = data.avatars.find(a => a.id === model.avatarId);
    if (avatar && avatar.voiceModelId === modelId) {
      avatar.voiceModelId = null;
      avatar.voiceEnabled = false;
    }

    data.voiceModels.splice(index, 1);
    saveData();
    return true;
  }

  synthesizeVoice(modelId, text, options) {
    const model = this.getVoiceModel(modelId);
    if (!model || model.status !== 'ready') {
      return null;
    }

    const taskId = `voice_synth_${Date.now()}`;
    const now = new Date().toISOString();

    const newTask = {
      id: taskId,
      modelId,
      avatarId: model.avatarId,
      text,
      options: options || {
        speed: 1.0,
        pitch: 1.0,
        emotion: 'neutral'
      },
      status: 'synthesizing',
      progress: 0,
      audioPath: null,
      duration: 0,
      createdAt: now,
      updatedAt: now
    };

    data.voiceSynthesisTasks.push(newTask);
    saveData();

    this.simulateSynthesis(taskId);

    return newTask;
  }

  simulateSynthesis(taskId) {
    let progress = 0;

    const interval = setInterval(() => {
      progress += 20;

      const task = data.voiceSynthesisTasks.find(t => t.id === taskId);
      if (!task) {
        clearInterval(interval);
        return;
      }

      task.progress = Math.min(progress, 100);

      if (progress >= 100) {
        task.status = 'completed';
        task.duration = Math.floor(task.text.length * 0.2);
        task.audioPath = `/api/voice/synthesis/${taskId}/audio`;
        task.updatedAt = new Date().toISOString();
        clearInterval(interval);
      }

      saveData();
    }, 500);
  }

  getSynthesisTask(taskId) {
    return data.voiceSynthesisTasks.find(t => t.id === taskId);
  }

  bindVoiceModelToAvatar(avatarId, modelId) {
    const avatar = data.avatars.find(a => a.id === avatarId);
    const model = data.voiceModels.find(m => m.id === modelId);

    if (!avatar || !model) {
      return null;
    }

    if (model.avatarId !== avatarId) {
      return null;
    }

    avatar.voiceModelId = modelId;
    avatar.voiceEnabled = true;
    avatar.voiceBoundAt = new Date().toISOString();
    saveData();

    return avatar;
  }

  unbindVoiceModelFromAvatar(avatarId) {
    const avatar = data.avatars.find(a => a.id === avatarId);
    if (!avatar) {
      return null;
    }

    avatar.voiceModelId = null;
    avatar.voiceEnabled = false;
    avatar.voiceBoundAt = null;
    saveData();

    return avatar;
  }
}

const voiceService = new VoiceService();

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Memorise backend is running' });
});

app.get('/api/config', (req, res) => {
  res.json({
    success: true,
    data: {
      openai: {
        apiKeyConfigured: !!config.openai.apiKey,
        baseUrl: config.openai.baseUrl,
        model: config.openai.model
      },
      aliyun: {
        apiKeyConfigured: !!config.aliyun.apiKey,
        baseUrl: config.aliyun.baseUrl,
        imageModel: config.aliyun.imageModel,
        textModel: config.aliyun.textModel
      }
    }
  });
});

app.put('/api/config', (req, res) => {
  try {
    const { openai, aliyun } = req.body;

    if (openai) {
      if (openai.apiKey !== undefined) config.openai.apiKey = openai.apiKey;
      if (openai.baseUrl) config.openai.baseUrl = openai.baseUrl;
      if (openai.model) config.openai.model = openai.model;
    }

    if (aliyun) {
      if (aliyun.apiKey !== undefined) config.aliyun.apiKey = aliyun.apiKey;
      if (aliyun.baseUrl) config.aliyun.baseUrl = aliyun.baseUrl;
      if (aliyun.imageModel) config.aliyun.imageModel = aliyun.imageModel;
      if (aliyun.textModel) config.aliyun.textModel = aliyun.textModel;
    }

    saveConfig();

    res.json({
      success: true,
      message: '配置已保存'
    });
  } catch (error) {
    console.error('保存配置失败:', error);
    res.status(500).json({
      success: false,
      error: '保存配置失败'
    });
  }
});

app.post('/api/photos/analyze', async (req, res) => {
  try {
    const { photos } = req.body;

    if (!photos || !Array.isArray(photos) || photos.length === 0) {
      return res.status(400).json({
        success: false,
        error: '请提供至少一张照片'
      });
    }

    const analysisResults = [];

    for (let i = 0; i < photos.length; i++) {
      const photo = photos[i];
      let result;

      if (config.openai.apiKey) {
        result = await aiService.analyzePhotoWithOpenAI(photo);
      } else if (config.aliyun.apiKey) {
        result = await aiService.analyzePhotoWithAliyun(photo);
      } else {
        result = aiService.simulateFaceDetection(photo);
      }

      analysisResults.push({
        index: i,
        detectedType: result.faceAngle,
        detectedTypeLabel: result.faceAngleLabel,
        confidence: result.confidence,
        features: result.features,
        qualityScore: result.qualityScore
      });
    }

    const photoTypes = ['front', 'left', 'right', 'back', 'closeup'];
    const photoTypeLabels = {
      front: '正面',
      left: '左侧面',
      right: '右侧面',
      back: '背面',
      closeup: '特写'
    };

    const detectedTypes = new Set(analysisResults.map(r => r.detectedType));
    const missingTypes = photoTypes.filter(t => !detectedTypes.has(t));

    res.json({
      success: true,
      data: {
        totalPhotos: photos.length,
        analysis: analysisResults,
        detectedTypes: Array.from(detectedTypes),
        detectedTypeLabels: Array.from(detectedTypes).map(t => photoTypeLabels[t]),
        missingTypes: missingTypes,
        missingTypeLabels: missingTypes.map(t => photoTypeLabels[t]),
        overallQuality: Math.round(analysisResults.reduce((sum, r) => sum + r.qualityScore, 0) / analysisResults.length),
        recommendation: detectedTypes.size >= 4
          ? '照片覆盖角度良好，生成效果预计优秀'
          : detectedTypes.size >= 2
            ? '建议补充更多角度的照片以获得更好效果'
            : '照片角度不足，建议补充更多不同角度的照片'
      }
    });
  } catch (error) {
    console.error('照片分析错误:', error);
    res.status(500).json({
      success: false,
      error: '照片分析失败，请重试'
    });
  }
});

app.post('/api/avatars/generate', async (req, res) => {
  try {
    const {
      name,
      relationship,
      gender,
      birthYear,
      deathYear,
      description,
      generationMethod,
      photos,
      textDescription
    } = req.body;

    if (!name || !relationship || !generationMethod) {
      return res.status(400).json({
        success: false,
        error: '缺少必要参数'
      });
    }

    const avatarId = `avatar_${Date.now()}`;
    const taskId = `task_${Date.now()}`;

    const newAvatar = {
      id: avatarId,
      name,
      relationship,
      gender,
      birthYear,
      deathYear: deathYear || undefined,
      description: description || '',
      generationMethod,
      photos: photos || [],
      textDescription: textDescription || undefined,
      status: 'generating',
      progress: 0,
      createdAt: new Date().toISOString(),
      taskId
    };

    data.avatars.push(newAvatar);
    saveData();

    simulateAvatarGeneration(avatarId, generationMethod);

    res.json({
      success: true,
      data: {
        taskId,
        avatarId,
        status: 'generating',
        message: '数字人生成任务已创建'
      }
    });
  } catch (error) {
    console.error('创建生成任务错误:', error);
    res.status(500).json({
      success: false,
      error: '创建生成任务失败，请重试'
    });
  }
});

function simulateAvatarGeneration(avatarId, generationMethod) {
  let progress = 0;

  const interval = setInterval(() => {
    progress += 10;

    const avatar = data.avatars.find(a => a.id === avatarId);
    if (!avatar) {
      clearInterval(interval);
      return;
    }

    avatar.progress = Math.min(progress, 100);

    if (progress >= 100) {
      avatar.status = 'active';
      avatar.avatar = `https://images.unsplash.com/photo-1507003211169?w=400&h=400&fit=crop&crop=face`;
      avatar.modelUrl = '/models/girl_speedsculpt.glb';
      clearInterval(interval);
    }

    saveData();
  }, 1000);
}

app.post('/api/avatars/:id/fine-tune', async (req, res) => {
  try {
    const { id } = req.params;
    const { adjustments } = req.body;

    if (!adjustments) {
      return res.status(400).json({
        success: false,
        error: '缺少微调参数'
      });
    }

    const result = await aiService.fineTuneAvatar(id, adjustments);

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('微调数字人失败:', error);
    res.status(500).json({
      success: false,
      error: error.message || '微调失败'
    });
  }
});

app.get('/api/avatars/:id/status', (req, res) => {
  try {
    const { id } = req.params;
    const avatar = data.avatars.find(a => a.id === id);

    if (!avatar) {
      return res.status(404).json({
        success: false,
        error: '数字人不存在'
      });
    }

    res.json({
      success: true,
      data: {
        avatarId: avatar.id,
        status: avatar.status,
        progress: avatar.progress,
        generationMethod: avatar.generationMethod,
        fineTuneAdjustments: avatar.fineTuneAdjustments,
        estimatedTimeRemaining: avatar.status === 'generating' || avatar.status === 'fine-tuning'
          ? Math.max(0, Math.round((100 - avatar.progress) * 0.5))
          : 0
      }
    });
  } catch (error) {
    console.error('查询状态错误:', error);
    res.status(500).json({
      success: false,
      error: '查询状态失败，请重试'
    });
  }
});

app.get('/api/avatars/:id', (req, res) => {
  try {
    const { id } = req.params;
    const avatar = data.avatars.find(a => a.id === id);

    if (!avatar) {
      return res.status(404).json({
        success: false,
        error: '数字人不存在'
      });
    }

    res.json({
      success: true,
      data: {
        id: avatar.id,
        name: avatar.name,
        relationship: avatar.relationship,
        gender: avatar.gender,
        birthYear: avatar.birthYear,
        deathYear: avatar.deathYear,
        description: avatar.description,
        generationMethod: avatar.generationMethod,
        status: avatar.status,
        progress: avatar.progress,
        avatar: avatar.avatar,
        modelUrl: avatar.modelUrl,
        createdAt: avatar.createdAt,
        fineTuneAdjustments: avatar.fineTuneAdjustments,
        fineTunedAt: avatar.fineTunedAt,
        voiceModelId: avatar.voiceModelId,
        voiceEnabled: avatar.voiceEnabled,
        voiceBoundAt: avatar.voiceBoundAt
      }
    });
  } catch (error) {
    console.error('获取数字人信息错误:', error);
    res.status(500).json({
      success: false,
      error: '获取数字人信息失败，请重试'
    });
  }
});

app.get('/api/avatars', (req, res) => {
  try {
    const avatarList = data.avatars.map(avatar => ({
      id: avatar.id,
      name: avatar.name,
      relationship: avatar.relationship,
      gender: avatar.gender,
      birthYear: avatar.birthYear,
      deathYear: avatar.deathYear,
      description: avatar.description,
      generationMethod: avatar.generationMethod,
      status: avatar.status,
      progress: avatar.progress,
      avatar: avatar.avatar,
      createdAt: avatar.createdAt,
      voiceModelId: avatar.voiceModelId,
      voiceEnabled: avatar.voiceEnabled
    }));

    res.json({
      success: true,
      data: {
        total: avatarList.length,
        avatars: avatarList
      }
    });
  } catch (error) {
    console.error('获取数字人列表错误:', error);
    res.status(500).json({
      success: false,
      error: '获取数字人列表失败，请重试'
    });
  }
});

app.delete('/api/avatars/:id', (req, res) => {
  try {
    const { id } = req.params;
    const index = data.avatars.findIndex(a => a.id === id);

    if (index === -1) {
      return res.status(404).json({
        success: false,
        error: '数字人不存在'
      });
    }

    data.avatars.splice(index, 1);

    const relatedMemories = data.memories.filter(m => m.avatarId === id);
    if (relatedMemories.length > 0) {
      data.memories = data.memories.filter(m => m.avatarId !== id);
    }

    saveData();

    res.json({
      success: true,
      message: '数字人已删除，关联记忆也已删除'
    });
  } catch (error) {
    console.error('删除数字人错误:', error);
    res.status(500).json({
      success: false,
      error: '删除数字人失败，请重试'
    });
  }
});

app.put('/api/avatars/:id', (req, res) => {
  try {
    const { id } = req.params;
    const { name, relationship, gender, birthYear, deathYear, description } = req.body;
    const avatar = data.avatars.find(a => a.id === id);

    if (!avatar) {
      return res.status(404).json({
        success: false,
        error: '数字人不存在'
      });
    }

    if (name) avatar.name = name;
    if (relationship) avatar.relationship = relationship;
    if (gender) avatar.gender = gender;
    if (birthYear !== undefined) avatar.birthYear = birthYear;
    if (deathYear !== undefined) avatar.deathYear = deathYear;
    if (description !== undefined) avatar.description = description;

    saveData();

    res.json({
      success: true,
      data: {
        id: avatar.id,
        name: avatar.name,
        relationship: avatar.relationship,
        gender: avatar.gender,
        birthYear: avatar.birthYear,
        deathYear: avatar.deathYear,
        description: avatar.description,
        status: avatar.status,
        progress: avatar.progress
      }
    });
  } catch (error) {
    console.error('更新数字人错误:', error);
    res.status(500).json({
      success: false,
      error: '更新数字人失败，请重试'
    });
  }
});

app.get('/api/memories', (req, res) => {
  try {
    const { avatarId, type, tag } = req.query;

    let filteredMemories = [...data.memories];

    if (avatarId) {
      filteredMemories = filteredMemories.filter(m => m.avatarId === avatarId);
    }

    if (type) {
      filteredMemories = filteredMemories.filter(m => m.type === type);
    }

    if (tag) {
      filteredMemories = filteredMemories.filter(m => m.tags && m.tags.includes(tag));
    }

    const memoryList = filteredMemories.map(memory => ({
      id: memory.id,
      avatarId: memory.avatarId,
      title: memory.title,
      type: memory.type,
      description: memory.description,
      tags: memory.tags,
      createdAt: memory.createdAt,
      updatedAt: memory.updatedAt
    }));

    res.json({
      success: true,
      data: {
        total: memoryList.length,
        memories: memoryList
      }
    });
  } catch (error) {
    console.error('获取记忆列表错误:', error);
    res.status(500).json({
      success: false,
      error: '获取记忆列表失败，请重试'
    });
  }
});

app.get('/api/memories/:id', (req, res) => {
  try {
    const { id } = req.params;
    const memory = data.memories.find(m => m.id === id);

    if (!memory) {
      return res.status(404).json({
        success: false,
        error: '记忆不存在'
      });
    }

    res.json({
      success: true,
      data: {
        id: memory.id,
        avatarId: memory.avatarId,
        title: memory.title,
        type: memory.type,
        content: memory.content,
        description: memory.description,
        tags: memory.tags,
        metadata: memory.metadata,
        createdAt: memory.createdAt,
        updatedAt: memory.updatedAt
      }
    });
  } catch (error) {
    console.error('获取记忆详情错误:', error);
    res.status(500).json({
      success: false,
      error: '获取记忆详情失败，请重试'
    });
  }
});

app.post('/api/memories', (req, res) => {
  try {
    const {
      avatarId,
      title,
      type,
      content,
      description,
      tags,
      metadata
    } = req.body;

    if (!avatarId || !title || !type || !content) {
      return res.status(400).json({
        success: false,
        error: '缺少必要参数'
      });
    }

    const validTypes = ['text', 'image', 'video'];
    if (!validTypes.includes(type)) {
      return res.status(400).json({
        success: false,
        error: '不支持的记忆类型，仅支持 text、image、video'
      });
    }

    const avatar = data.avatars.find(a => a.id === avatarId);
    if (!avatar) {
      return res.status(404).json({
        success: false,
        error: '关联的数字人不存在'
      });
    }

    const memoryId = `memory_${Date.now()}`;
    const now = new Date().toISOString();

    const newMemory = {
      id: memoryId,
      avatarId,
      title,
      type,
      content,
      description: description || '',
      tags: tags || [],
      metadata: metadata || {},
      createdAt: now,
      updatedAt: now
    };

    data.memories.push(newMemory);
    saveData();

    res.json({
      success: true,
      data: {
        id: newMemory.id,
        avatarId: newMemory.avatarId,
        title: newMemory.title,
        type: newMemory.type,
        createdAt: newMemory.createdAt,
        message: '记忆创建成功'
      }
    });
  } catch (error) {
    console.error('创建记忆错误:', error);
    res.status(500).json({
      success: false,
      error: '创建记忆失败，请重试'
    });
  }
});

app.put('/api/memories/:id', (req, res) => {
  try {
    const { id } = req.params;
    const {
      title,
      type,
      content,
      description,
      tags,
      metadata
    } = req.body;

    const memory = data.memories.find(m => m.id === id);

    if (!memory) {
      return res.status(404).json({
        success: false,
        error: '记忆不存在'
      });
    }

    if (title) memory.title = title;
    if (type) {
      const validTypes = ['text', 'image', 'video'];
      if (!validTypes.includes(type)) {
        return res.status(400).json({
          success: false,
          error: '不支持的记忆类型，仅支持 text、image、video'
        });
      }
      memory.type = type;
    }
    if (content) memory.content = content;
    if (description !== undefined) memory.description = description;
    if (tags !== undefined) memory.tags = tags;
    if (metadata !== undefined) memory.metadata = metadata;

    memory.updatedAt = new Date().toISOString();
    saveData();

    res.json({
      success: true,
      data: {
        id: memory.id,
        title: memory.title,
        type: memory.type,
        updatedAt: memory.updatedAt,
        message: '记忆更新成功'
      }
    });
  } catch (error) {
    console.error('更新记忆错误:', error);
    res.status(500).json({
      success: false,
      error: '更新记忆失败，请重试'
    });
  }
});

app.delete('/api/memories/:id', (req, res) => {
  try {
    const { id } = req.params;
    const index = data.memories.findIndex(m => m.id === id);

    if (index === -1) {
      return res.status(404).json({
        success: false,
        error: '记忆不存在'
      });
    }

    data.memories.splice(index, 1);
    saveData();

    res.json({
      success: true,
      message: '记忆已删除'
    });
  } catch (error) {
    console.error('删除记忆错误:', error);
    res.status(500).json({
      success: false,
      error: '删除记忆失败，请重试'
    });
  }
});

app.get('/api/avatars/:avatarId/memories', (req, res) => {
  try {
    const { avatarId } = req.params;
    const { type, tag } = req.query;

    const avatar = data.avatars.find(a => a.id === avatarId);
    if (!avatar) {
      return res.status(404).json({
        success: false,
        error: '数字人不存在'
      });
    }

    let memories = data.memories.filter(m => m.avatarId === avatarId);

    if (type) {
      memories = memories.filter(m => m.type === type);
    }

    if (tag) {
      memories = memories.filter(m => m.tags && m.tags.includes(tag));
    }

    const memoryList = memories.map(memory => ({
      id: memory.id,
      avatarId: memory.avatarId,
      title: memory.title,
      type: memory.type,
      description: memory.description,
      tags: memory.tags,
      createdAt: memory.createdAt,
      updatedAt: memory.updatedAt
    }));

    res.json({
      success: true,
      data: {
        avatarId,
        avatarName: avatar.name,
        total: memoryList.length,
        memories: memoryList
      }
    });
  } catch (error) {
    console.error('获取数字人记忆错误:', error);
    res.status(500).json({
      success: false,
      error: '获取数字人记忆失败，请重试'
    });
  }
});

app.post('/api/memories/batch', (req, res) => {
  try {
    const { memories } = req.body;

    if (!memories || !Array.isArray(memories) || memories.length === 0) {
      return res.status(400).json({
        success: false,
        error: '请提供至少一个记忆'
      });
    }

    const results = [];
    const errors = [];

    for (let i = 0; i < memories.length; i++) {
      const memoryData = memories[i];

      try {
        if (!memoryData.avatarId || !memoryData.title || !memoryData.type || !memoryData.content) {
          throw new Error('缺少必要参数');
        }

        const validTypes = ['text', 'image', 'video'];
        if (!validTypes.includes(memoryData.type)) {
          throw new Error('不支持的记忆类型');
        }

        const avatar = data.avatars.find(a => a.id === memoryData.avatarId);
        if (!avatar) {
          throw new Error('关联的数字人不存在');
        }

        const memoryId = `memory_${Date.now()}_${i}`;
        const now = new Date().toISOString();

        const newMemory = {
          id: memoryId,
          avatarId: memoryData.avatarId,
          title: memoryData.title,
          type: memoryData.type,
          content: memoryData.content,
          description: memoryData.description || '',
          tags: memoryData.tags || [],
          metadata: memoryData.metadata || {},
          createdAt: now,
          updatedAt: now
        };

        data.memories.push(newMemory);
        results.push({
          index: i,
          success: true,
          id: newMemory.id,
          title: newMemory.title
        });
      } catch (error) {
        errors.push({
          index: i,
          success: false,
          error: error.message
        });
      }
    }

    if (results.length > 0) {
      saveData();
    }

    res.json({
      success: true,
      data: {
        total: memories.length,
        successCount: results.length,
        errorCount: errors.length,
        results,
        errors
      }
    });
  } catch (error) {
    console.error('批量创建记忆错误:', error);
    res.status(500).json({
      success: false,
      error: '批量创建记忆失败，请重试'
    });
  }
});

app.get('/api/voice/materials', (req, res) => {
  try {
    const { avatarId } = req.query;
    const materials = voiceService.getVoiceMaterials(avatarId);

    const materialList = materials.map(m => ({
      id: m.id,
      avatarId: m.avatarId,
      name: m.name,
      type: m.type,
      format: m.format,
      duration: m.duration,
      size: m.size,
      status: m.status,
      qualityScore: m.qualityScore,
      transcription: m.transcription,
      preprocessInfo: m.preprocessInfo,
      createdAt: m.createdAt,
      updatedAt: m.updatedAt
    }));

    res.json({
      success: true,
      data: {
        total: materialList.length,
        materials: materialList
      }
    });
  } catch (error) {
    console.error('获取声音素材列表错误:', error);
    res.status(500).json({
      success: false,
      error: '获取声音素材列表失败，请重试'
    });
  }
});

app.post('/api/voice/materials', (req, res) => {
  try {
    const {
      avatarId,
      name,
      type,
      format,
      duration,
      size,
      audioData
    } = req.body;

    if (!avatarId || !name) {
      return res.status(400).json({
        success: false,
        error: '缺少必要参数：avatarId 和 name'
      });
    }

    const avatar = data.avatars.find(a => a.id === avatarId);
    if (!avatar) {
      return res.status(404).json({
        success: false,
        error: '关联的数字人不存在'
      });
    }

    const material = voiceService.createVoiceMaterial(
      avatarId,
      name,
      type,
      format,
      duration,
      size,
      audioData
    );

    res.json({
      success: true,
      data: {
        id: material.id,
        avatarId: material.avatarId,
        name: material.name,
        status: material.status,
        createdAt: material.createdAt,
        message: '声音素材创建成功'
      }
    });
  } catch (error) {
    console.error('创建声音素材错误:', error);
    res.status(500).json({
      success: false,
      error: '创建声音素材失败，请重试'
    });
  }
});

app.get('/api/voice/materials/:id', (req, res) => {
  try {
    const { id } = req.params;
    const material = voiceService.getVoiceMaterial(id);

    if (!material) {
      return res.status(404).json({
        success: false,
        error: '声音素材不存在'
      });
    }

    res.json({
      success: true,
      data: {
        id: material.id,
        avatarId: material.avatarId,
        name: material.name,
        type: material.type,
        format: material.format,
        duration: material.duration,
        size: material.size,
        status: material.status,
        qualityScore: material.qualityScore,
        transcription: material.transcription,
        preprocessInfo: material.preprocessInfo,
        createdAt: material.createdAt,
        updatedAt: material.updatedAt
      }
    });
  } catch (error) {
    console.error('获取声音素材错误:', error);
    res.status(500).json({
      success: false,
      error: '获取声音素材失败，请重试'
    });
  }
});

app.put('/api/voice/materials/:id', (req, res) => {
  try {
    const { id } = req.params;
    const { name, transcription } = req.body;

    const material = voiceService.updateVoiceMaterial(id, {
      name,
      transcription
    });

    if (!material) {
      return res.status(404).json({
        success: false,
        error: '声音素材不存在'
      });
    }

    res.json({
      success: true,
      data: {
        id: material.id,
        name: material.name,
        updatedAt: material.updatedAt,
        message: '声音素材更新成功'
      }
    });
  } catch (error) {
    console.error('更新声音素材错误:', error);
    res.status(500).json({
      success: false,
      error: '更新声音素材失败，请重试'
    });
  }
});

app.delete('/api/voice/materials/:id', (req, res) => {
  try {
    const { id } = req.params;
    const success = voiceService.deleteVoiceMaterial(id);

    if (!success) {
      return res.status(404).json({
        success: false,
        error: '声音素材不存在'
      });
    }

    res.json({
      success: true,
      message: '声音素材已删除'
    });
  } catch (error) {
    console.error('删除声音素材错误:', error);
    res.status(500).json({
      success: false,
      error: '删除声音素材失败，请重试'
    });
  }
});

app.post('/api/voice/materials/:id/preprocess', (req, res) => {
  try {
    const { id } = req.params;
    const material = voiceService.preprocessAudio(id);

    if (!material) {
      return res.status(404).json({
        success: false,
        error: '声音素材不存在'
      });
    }

    res.json({
      success: true,
      data: {
        materialId: material.id,
        status: material.status,
        message: '音频预处理任务已开始'
      }
    });
  } catch (error) {
    console.error('音频预处理错误:', error);
    res.status(500).json({
      success: false,
      error: '音频预处理失败，请重试'
    });
  }
});

app.post('/api/voice/materials/batch-preprocess', (req, res) => {
  try {
    const { materialIds } = req.body;

    if (!materialIds || !Array.isArray(materialIds) || materialIds.length === 0) {
      return res.status(400).json({
        success: false,
        error: '请提供至少一个素材ID'
      });
    }

    const results = voiceService.batchPreprocess(materialIds);

    res.json({
      success: true,
      data: {
        total: materialIds.length,
        results,
        message: '批量预处理任务已开始'
      }
    });
  } catch (error) {
    console.error('批量预处理错误:', error);
    res.status(500).json({
      success: false,
      error: '批量预处理失败，请重试'
    });
  }
});

app.get('/api/voice/models', (req, res) => {
  try {
    const { avatarId } = req.query;
    const models = voiceService.getVoiceModels(avatarId);

    const modelList = models.map(m => ({
      id: m.id,
      avatarId: m.avatarId,
      name: m.name,
      status: m.status,
      progress: m.progress,
      materialIds: m.materialIds,
      qualityMetrics: m.qualityMetrics,
      trainingConfig: m.trainingConfig,
      createdAt: m.createdAt,
      updatedAt: m.updatedAt
    }));

    res.json({
      success: true,
      data: {
        total: modelList.length,
        models: modelList
      }
    });
  } catch (error) {
    console.error('获取声音模型列表错误:', error);
    res.status(500).json({
      success: false,
      error: '获取声音模型列表失败，请重试'
    });
  }
});

app.post('/api/voice/models', (req, res) => {
  try {
    const {
      avatarId,
      name,
      materialIds,
      config
    } = req.body;

    if (!avatarId || !name) {
      return res.status(400).json({
        success: false,
        error: '缺少必要参数：avatarId 和 name'
      });
    }

    const avatar = data.avatars.find(a => a.id === avatarId);
    if (!avatar) {
      return res.status(404).json({
        success: false,
        error: '关联的数字人不存在'
      });
    }

    if (!materialIds || !Array.isArray(materialIds) || materialIds.length === 0) {
      return res.status(400).json({
        success: false,
        error: '请提供至少一个声音素材'
      });
    }

    const validMaterials = materialIds.filter(id => {
      const m = voiceService.getVoiceMaterial(id);
      return m && m.avatarId === avatarId && m.status === 'preprocessed';
    });

    if (validMaterials.length === 0) {
      return res.status(400).json({
        success: false,
        error: '没有有效的预处理后素材，请先预处理素材'
      });
    }

    const model = voiceService.createVoiceModel(avatarId, name, validMaterials, config);

    res.json({
      success: true,
      data: {
        modelId: model.id,
        avatarId: model.avatarId,
        name: model.name,
        status: model.status,
        progress: model.progress,
        materialCount: validMaterials.length,
        message: '声线训练任务已开始'
      }
    });
  } catch (error) {
    console.error('创建声音模型错误:', error);
    res.status(500).json({
      success: false,
      error: '创建声音模型失败，请重试'
    });
  }
});

app.get('/api/voice/models/:id', (req, res) => {
  try {
    const { id } = req.params;
    const model = voiceService.getVoiceModel(id);

    if (!model) {
      return res.status(404).json({
        success: false,
        error: '声音模型不存在'
      });
    }

    res.json({
      success: true,
      data: {
        id: model.id,
        avatarId: model.avatarId,
        name: model.name,
        status: model.status,
        progress: model.progress,
        materialIds: model.materialIds,
        qualityMetrics: model.qualityMetrics,
        trainingConfig: model.trainingConfig,
        modelPath: model.modelPath,
        sampleAudioPath: model.sampleAudioPath,
        createdAt: model.createdAt,
        updatedAt: model.updatedAt
      }
    });
  } catch (error) {
    console.error('获取声音模型错误:', error);
    res.status(500).json({
      success: false,
      error: '获取声音模型失败，请重试'
    });
  }
});

app.get('/api/voice/models/:id/status', (req, res) => {
  try {
    const { id } = req.params;
    const model = voiceService.getVoiceModel(id);

    if (!model) {
      return res.status(404).json({
        success: false,
        error: '声音模型不存在'
      });
    }

    res.json({
      success: true,
      data: {
        modelId: model.id,
        status: model.status,
        progress: model.progress,
        qualityMetrics: model.qualityMetrics,
        estimatedTimeRemaining: model.status === 'training'
          ? Math.max(0, Math.round((100 - model.progress) * 0.5))
          : 0
      }
    });
  } catch (error) {
    console.error('获取训练状态错误:', error);
    res.status(500).json({
      success: false,
      error: '获取训练状态失败，请重试'
    });
  }
});

app.delete('/api/voice/models/:id', (req, res) => {
  try {
    const { id } = req.params;
    const success = voiceService.deleteVoiceModel(id);

    if (!success) {
      return res.status(404).json({
        success: false,
        error: '声音模型不存在'
      });
    }

    res.json({
      success: true,
      message: '声音模型已删除'
    });
  } catch (error) {
    console.error('删除声音模型错误:', error);
    res.status(500).json({
      success: false,
      error: '删除声音模型失败，请重试'
    });
  }
});

app.post('/api/voice/synthesize', (req, res) => {
  try {
    const {
      modelId,
      avatarId,
      text,
      options
    } = req.body;

    if (!text) {
      return res.status(400).json({
        success: false,
        error: '请提供要合成的文本'
      });
    }

    let targetModelId = modelId;

    if (!targetModelId && avatarId) {
      const avatar = data.avatars.find(a => a.id === avatarId);
      if (avatar && avatar.voiceModelId) {
        targetModelId = avatar.voiceModelId;
      }
    }

    if (!targetModelId) {
      return res.status(400).json({
        success: false,
        error: '请提供 modelId 或 avatarId（需要已绑定声音模型）'
      });
    }

    const task = voiceService.synthesizeVoice(targetModelId, text, options);

    if (!task) {
      return res.status(400).json({
        success: false,
        error: '声音模型不存在或未准备好'
      });
    }

    res.json({
      success: true,
      data: {
        taskId: task.id,
        modelId: task.modelId,
        avatarId: task.avatarId,
        text: task.text,
        status: task.status,
        progress: task.progress,
        message: '语音合成任务已开始'
      }
    });
  } catch (error) {
    console.error('语音合成错误:', error);
    res.status(500).json({
      success: false,
      error: '语音合成失败，请重试'
    });
  }
});

app.get('/api/voice/synthesis/:id', (req, res) => {
  try {
    const { id } = req.params;
    const task = voiceService.getSynthesisTask(id);

    if (!task) {
      return res.status(404).json({
        success: false,
        error: '合成任务不存在'
      });
    }

    res.json({
      success: true,
      data: {
        taskId: task.id,
        modelId: task.modelId,
        avatarId: task.avatarId,
        text: task.text,
        options: task.options,
        status: task.status,
        progress: task.progress,
        audioPath: task.audioPath,
        duration: task.duration,
        createdAt: task.createdAt,
        updatedAt: task.updatedAt
      }
    });
  } catch (error) {
    console.error('获取合成任务错误:', error);
    res.status(500).json({
      success: false,
      error: '获取合成任务失败，请重试'
    });
  }
});

app.put('/api/avatars/:id/voice-model', (req, res) => {
  try {
    const { id } = req.params;
    const { modelId } = req.body;

    if (!modelId) {
      return res.status(400).json({
        success: false,
        error: '请提供 modelId'
      });
    }

    const avatar = voiceService.bindVoiceModelToAvatar(id, modelId);

    if (!avatar) {
      return res.status(404).json({
        success: false,
        error: '数字人或声音模型不存在，或模型不属于该数字人'
      });
    }

    res.json({
      success: true,
      data: {
        avatarId: avatar.id,
        voiceModelId: avatar.voiceModelId,
        voiceEnabled: avatar.voiceEnabled,
        voiceBoundAt: avatar.voiceBoundAt,
        message: '声音模型已绑定到数字人'
      }
    });
  } catch (error) {
    console.error('绑定声音模型错误:', error);
    res.status(500).json({
      success: false,
      error: '绑定声音模型失败，请重试'
    });
  }
});

app.delete('/api/avatars/:id/voice-model', (req, res) => {
  try {
    const { id } = req.params;

    const avatar = voiceService.unbindVoiceModelFromAvatar(id);

    if (!avatar) {
      return res.status(404).json({
        success: false,
        error: '数字人不存在'
      });
    }

    res.json({
      success: true,
      data: {
        avatarId: avatar.id,
        voiceModelId: avatar.voiceModelId,
        voiceEnabled: avatar.voiceEnabled,
        message: '声音模型已解绑'
      }
    });
  } catch (error) {
    console.error('解绑声音模型错误:', error);
    res.status(500).json({
      success: false,
      error: '解绑声音模型失败，请重试'
    });
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
  console.log(`数据文件: ${DATA_FILE}`);
  console.log(`配置文件: ${CONFIG_FILE}`);
});
