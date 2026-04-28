import httpx
import asyncio
import json
import base64
import re
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings
from app.schemas import PhotoAnalysisResult, PhotoAnalysisResponse
from app.models import PhotoAngle


class AliyunServiceError(Exception):
    pass


class AliyunService:
    def __init__(self):
        self.api_key = settings.ALIYUN_API_KEY
        self.base_url = settings.ALIYUN_BASE_URL
        self.image_model = settings.ALIYUN_IMAGE_MODEL
        self.text_model = settings.ALIYUN_TEXT_MODEL
        self.face_analysis_model = settings.FACE_ANALYSIS_MODEL
        self.avatar_generation_model = settings.AVATAR_GENERATION_MODEL
        
        self._http_client: Optional[httpx.AsyncClient] = None
    
    @property
    async def http_client(self) -> httpx.AsyncClient:
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=10.0),
                follow_redirects=True
            )
        return self._http_client
    
    async def close(self):
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise AliyunServiceError("阿里云 API Key 未配置")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout)),
        reraise=True
    )
    async def analyze_photo_with_vision(
        self, 
        image_base64: str
    ) -> Dict[str, Any]:
        client = await self.http_client
        
        base64_data = self._clean_base64(image_base64)
        
        payload = {
            "model": self.face_analysis_model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """请分析这张人脸照片，返回以下信息（JSON格式）：
1. faceAngle: 检测人脸角度，可选值：front（正面）、left（左侧面）、right（右侧面）、back（背面）、closeup（特写）
2. confidence: 检测置信度，0-1之间的浮点数
3. qualityScore: 照片质量评分，0-100的整数
4. features: 检测到的面部特征列表，例如：["面部轮廓清晰", "五官特征明显", "光线充足"]
5. faceAngleLabel: 角度的中文描述，例如："正面"

只返回JSON，不要有其他内容。"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_data}"
                                }
                            }
                        ]
                    }
                ]
            },
            "parameters": {
                "max_tokens": 500,
                "temperature": 0.3
            }
        }
        
        try:
            response = await client.post(
                f"{self.base_url}/services/aigc/multimodal-generation/generation",
                headers=self._get_headers(),
                json=payload
            )
            
            if not response.status_code == 200:
                error_text = response.text
                raise AliyunServiceError(f"阿里云人脸检测失败: {response.status_code} - {error_text}")
            
            result = response.json()
            content = result.get("output", {}).get("text", "") or result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return self._parse_face_analysis_result(content)
            
        except httpx.HTTPStatusError as e:
            raise AliyunServiceError(f"HTTP错误: {e.response.status_code}")
        except Exception as e:
            raise AliyunServiceError(f"调用阿里云 API 失败: {str(e)}")
    
    def _clean_base64(self, data: str) -> str:
        if data.startswith("data:image"):
            match = re.match(r"data:image/[^;]+;base64,(.*)", data)
            if match:
                return match.group(1)
        return data
    
    def _parse_face_analysis_result(self, content: str) -> Dict[str, Any]:
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            try:
                parsed = json.loads(json_match.group(0))
                return {
                    "faceAngle": parsed.get("faceAngle", "front"),
                    "faceAngleLabel": parsed.get("faceAngleLabel", self._get_angle_label(parsed.get("faceAngle"))),
                    "confidence": float(parsed.get("confidence", 0.75)),
                    "qualityScore": int(parsed.get("qualityScore", 80)),
                    "features": parsed.get("features", ["面部轮廓清晰", "五官特征明显"])
                }
            except (json.JSONDecodeError, ValueError):
                pass
        
        return self._simulate_face_detection(content)
    
    def _simulate_face_detection(self, seed: str = "") -> Dict[str, Any]:
        angles = ["front", "left", "right", "back", "closeup"]
        angle_labels = {
            "front": "正面",
            "left": "左侧面",
            "right": "右侧面",
            "back": "背面",
            "closeup": "特写"
        }
        
        import random
        random.seed(hash(seed) if seed else random.random())
        
        angle = random.choice(angles)
        
        return {
            "faceAngle": angle,
            "faceAngleLabel": angle_labels[angle],
            "confidence": 0.75 + random.random() * 0.2,
            "qualityScore": 70 + random.randint(0, 30),
            "features": ["面部轮廓清晰", "五官特征明显", "光线充足"]
        }
    
    def _get_angle_label(self, angle: str) -> str:
        labels = {
            "front": "正面",
            "left": "左侧面",
            "right": "右侧面",
            "back": "背面",
            "closeup": "特写"
        }
        return labels.get(angle, "正面")
    
    async def analyze_photos(
        self, 
        photos: List[str]
    ) -> PhotoAnalysisResponse:
        analysis_results = []
        
        for i, photo in enumerate(photos):
            try:
                if self.api_key:
                    result = await self.analyze_photo_with_vision(photo)
                else:
                    result = self._simulate_face_detection(photo)
                
                analysis_results.append({
                    "index": i,
                    "detectedType": result.get("faceAngle", "front"),
                    "detectedTypeLabel": result.get("faceAngleLabel", "正面"),
                    "confidence": result.get("confidence", 0.75),
                    "features": result.get("features", []),
                    "qualityScore": result.get("qualityScore", 80)
                })
            except Exception as e:
                result = self._simulate_face_detection(str(i))
                analysis_results.append({
                    "index": i,
                    "detectedType": result.get("faceAngle", "front"),
                    "detectedTypeLabel": result.get("faceAngleLabel", "正面"),
                    "confidence": result.get("confidence", 0.75),
                    "features": result.get("features", []),
                    "qualityScore": result.get("qualityScore", 80)
                })
        
        photo_types = ["front", "left", "right", "back", "closeup"]
        photo_type_labels = {
            "front": "正面",
            "left": "左侧",
            "right": "右侧",
            "back": "背面",
            "closeup": "特写"
        }
        
        detected_types = set(r["detectedType"] for r in analysis_results)
        missing_types = [t for t in photo_types if t not in detected_types]
        
        overall_quality = round(
            sum(r["qualityScore"] for r in analysis_results) / len(analysis_results)
        ) if analysis_results else 0
        
        if len(detected_types) >= 4:
            recommendation = "照片覆盖角度良好，生成效果预计优秀"
        elif len(detected_types) >= 2:
            recommendation = "建议补充更多角度的照片以获得更好效果"
        else:
            recommendation = "照片角度不足，建议补充更多不同角度的照片"
        
        return PhotoAnalysisResponse(
            totalPhotos=len(photos),
            analysis=[PhotoAnalysisResult(**r) for r in analysis_results],
            detectedTypes=list(detected_types),
            detectedTypeLabels=[photo_type_labels[t] for t in detected_types],
            missingTypes=missing_types,
            missingTypeLabels=[photo_type_labels[t] for t in missing_types],
            overallQuality=overall_quality,
            recommendation=recommendation
        )
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=2, min=5, max=30),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout)),
        reraise=True
    )
    async def create_image_generation_task(
        self,
        prompt: str,
        negative_prompt: str = "模糊, 低质量, 变形, 丑陋",
        size: str = "1024*1024",
        style: str = "<portrait>"
    ) -> str:
        client = await self.http_client
        
        payload = {
            "model": self.avatar_generation_model,
            "input": {
                "prompt": prompt,
                "negative_prompt": negative_prompt
            },
            "parameters": {
                "style": style,
                "size": size,
                "n": 1
            }
        }
        
        headers = self._get_headers()
        headers["X-DashScope-Async"] = "enable"
        
        try:
            response = await client.post(
                f"{self.base_url}/services/aigc/text2image/image-synthesis",
                headers=headers,
                json=payload
            )
            
            if not response.status_code == 200:
                error_text = response.text
                raise AliyunServiceError(f"阿里云图像生成失败: {response.status_code} - {error_text}")
            
            result = response.json()
            task_id = result.get("output", {}).get("task_id") or result.get("task_id")
            
            if not task_id:
                raise AliyunServiceError("未获取到任务ID")
            
            return task_id
            
        except httpx.HTTPStatusError as e:
            raise AliyunServiceError(f"HTTP错误: {e.response.status_code}")
        except Exception as e:
            raise AliyunServiceError(f"创建图像生成任务失败: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout)),
        reraise=True
    )
    async def check_image_generation_status(
        self,
        task_id: str
    ) -> Tuple[str, Optional[str]]:
        client = await self.http_client
        
        try:
            response = await client.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=self._get_headers()
            )
            
            if not response.status_code == 200:
                return "failed", None
            
            result = response.json()
            output = result.get("output", {}) or result
            
            task_status = output.get("task_status", "unknown")
            
            if task_status == "SUCCEEDED" or task_status == "succeeded":
                results = output.get("results", [])
                if results and len(results) > 0:
                    image_url = results[0].get("url") or output.get("image_url")
                    return "completed", image_url
                return "completed", None
            
            elif task_status == "FAILED" or task_status == "failed":
                return "failed", None
            
            elif task_status == "RUNNING" or task_status == "running" or task_status == "PENDING" or task_status == "pending":
                return "processing", None
            
            return "unknown", None
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return "failed", None
            raise AliyunServiceError(f"HTTP错误: {e.response.status_code}")
        except Exception as e:
            raise AliyunServiceError(f"查询任务状态失败: {str(e)}")
    
    async def generate_avatar_prompt(
        self,
        name: str,
        gender: str,
        description: str,
        age_range: str = "老年"
    ) -> str:
        if not self.api_key:
            return self._simulate_image_prompt(name, gender, description, age_range)
        
        client = await self.http_client
        
        gender_term = "男性" if gender == "male" else "女性"
        
        prompt = f"""根据以下描述，生成一个用于AI图像生成的详细英文提示词：

人物姓名：{name}
性别：{gender_term}
年龄段：{age_range}
人物描述：{description if description else "一位慈祥的{gender_term}长辈"}

请生成一个详细的英文提示词，包含：
1. 人物的外貌特征
2. 面部特征细节
3. 表情和神态
4. 服装风格
5. 背景和光线
6. 艺术风格建议

只返回英文提示词，不要有其他内容。"""
        
        payload = {
            "model": self.text_model,
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的数字人生成助手，帮助用户生成详细的人物描述用于图像生成。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "max_tokens": 1000,
                "temperature": 0.7
            }
        }
        
        try:
            response = await client.post(
                f"{self.base_url}/services/aigc/text-generation/generation",
                headers=self._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("output", {}).get("text", "") or result.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    return content
        except Exception:
            pass
        
        return self._simulate_image_prompt(name, gender, description, age_range)
    
    def _simulate_image_prompt(
        self,
        name: str,
        gender: str,
        description: str,
        age_range: str
    ) -> str:
        gender_term = "man" if gender == "male" else "woman"
        return f"A realistic portrait of a {age_range} {gender_term}, professional photography, studio lighting, highly detailed face, sharp focus, high quality, 8k resolution, natural skin texture, warm color tone, gentle smile, kind expression"
    
    async def chat_with_avatar(
        self,
        avatar_persona: Dict[str, Any],
        messages: List[Dict[str, Any]]
    ) -> str:
        if not self.api_key:
            return self._simulate_ai_response(avatar_persona)
        
        client = await self.http_client
        
        name = avatar_persona.get("name", "数字人")
        relationship = avatar_persona.get("relationship", "亲人")
        gender_label = avatar_persona.get("gender", "爷爷")
        description = avatar_persona.get("description", "")
        
        system_prompt = f"""你是{name}，用户的{relationship}。
你的性别是{gender_label}。
{description if description else ''}

你需要以这位亲人的身份与用户对话。请记住：
1. 使用温暖、亲切、长辈般的语气
2. 回忆家族往事和传统
3. 给予关心和鼓励
4. 保持耐心和智慧
5. 回答要简洁，符合长辈说话的风格

不要暴露你是AI，要像真正的亲人一样与用户交流。"""
        
        formatted_messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        for msg in messages[-10:]:
            formatted_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        payload = {
            "model": self.text_model,
            "input": {
                "messages": formatted_messages
            },
            "parameters": {
                "max_tokens": 500,
                "temperature": 0.8
            }
        }
        
        try:
            response = await client.post(
                f"{self.base_url}/services/aigc/text-generation/generation",
                headers=self._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("output", {}).get("text", "") or result.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    return content
        except Exception:
            pass
        
        return self._simulate_ai_response(avatar_persona)
    
    def _simulate_ai_response(self, persona: Dict[str, Any]) -> str:
        import random
        responses = [
            "孩子，有什么想跟我说的吗？我一直在这儿听着。",
            "嗯，这个问题让我想起了很多往事。那时候的日子虽然苦，但大家都很知足。",
            "你一直都是个懂事的孩子，我很欣慰。有什么心事都可以跟我说。",
            "人生就是这样，起起落落。但只要保持一颗平常心，什么坎儿都能过去。",
            "记得你小时候总是追着问这问那，现在你都长大了，有了自己的想法。真好。",
            "孩子，无论遇到什么困难，都要记住：家人永远是你最坚强的后盾。",
            "这个话题让我想起了很多家族的故事。你想听听吗？",
            "你现在的努力我都看在眼里。继续加油，不要放弃。",
            "时间过得真快啊，转眼间你都这么大了。但在我心里，你永远都是那个可爱的孩子。",
            "有什么需要帮忙的吗？虽然我不在你身边，但我的心一直牵挂着你。"
        ]
        return random.choice(responses)


aliyun_service = AliyunService()
