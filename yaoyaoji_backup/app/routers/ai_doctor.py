from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
try:
    from openai import OpenAI
    import httpx
except ImportError:
    OpenAI = None
    httpx = None
import os
from datetime import datetime
from ..config import settings

router = APIRouter(prefix="/api/ai", tags=["AI医生"])

class SymptomRequest(BaseModel):
    """症状描述请求"""
    symptom_description: str

class AIResponse(BaseModel):
    """AI响应"""
    suggestion: str
    timestamp: str

class MedicineQueryRequest(BaseModel):
    """药品查询请求"""
    medicine_name: str
    
class DiseaseQueryRequest(BaseModel):
    """疾病查询请求"""
    disease_name: str

@router.post("/predict", response_model=AIResponse)
async def ai_medical_predict(request: SymptomRequest):
    """
    AI智能医疗预测
    根据用户输入的症状描述，返回专业的医学建议
    """
    if not request.symptom_description or not request.symptom_description.strip():
        raise HTTPException(status_code=400, detail="症状描述不能为空")
    
    # 检查OpenAI库是否可用
    if OpenAI is None:
        raise HTTPException(
            status_code=500,
            detail="AI服务未配置，请联系管理员安装openai库"
        )
    
    symptom_text = request.symptom_description.strip()
    print(f"📝 收到症状描述: {symptom_text}")
    
    try:
        # 初始化DeepSeek客户端（使用自定义httpx客户端以提高稳定性）
        http_client = httpx.Client(
            timeout=60.0,  # 60秒超时
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10,
                keepalive_expiry=30.0
            )
        )
        
        client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            http_client=http_client
        )
        
        # 构建专业的医疗问诊提示词
        system_prompt = """你是一位经验丰富的全科医生AI助手，名叫"药药记医生"。你的职责是：

1. 根据患者描述的症状，进行专业的初步分析
2. 给出可能的疾病原因（按可能性排序，至少3个）
3. 提供实用的自我护理建议
4. 明确告知何时需要就医
5. 如涉及用药，给出通用药品建议（OTC非处方药优先）

回答要求：
- 语言专业但易懂，避免过度专业术语
- 结构清晰，使用【】标记段落标题
- 必须强调"此建议仅供参考，不代替专业医疗诊断"
- 如症状严重或不明确，优先建议就医
- 回答长度控制在300-500字"""

        user_prompt = f"患者症状描述：{symptom_text}"
        
        print(f"🤖 正在调用DeepSeek API...")
        
        # 调用DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            stream=False
        )
        
        # 提取AI回复
        ai_suggestion = response.choices[0].message.content or "未获取到AI回复"
        print(f"✅ AI回复成功，长度: {len(ai_suggestion)}")
        
        # 关闭HTTP客户端
        http_client.close()
        
        # 返回结果
        return AIResponse(
            suggestion=ai_suggestion,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"❌ DeepSeek API调用失败: {error_type}: {error_msg}")
        
        # 如果是网络连接错误，提供更详细的错误信息
        if "Connection" in error_type or "connection" in error_msg.lower():
            print("⚠️ 网络连接错误，可能的原因：")
            print("   1. 网络不稳定或无法访问DeepSeek API")
            print("   2. 需要配置代理")
            print("   3. 防火墙阻止了连接")
        
        # 如果API调用失败，返回智能模拟建议
        print("⚠️ 使用备用模拟AI建议")
        
        # 基于关键词生成模拟建议
        mock_suggestion = generate_mock_suggestion(symptom_text)
        
        return AIResponse(
            suggestion=mock_suggestion,
            timestamp=datetime.now().isoformat()
        )

def generate_mock_suggestion(symptom_text: str) -> str:
    """生成模拟AI建议（备用方案）"""
    has_fever = any(word in symptom_text for word in ["发热", "发烧", "高烧", "体温"])
    has_cough = any(word in symptom_text for word in ["咳嗽", "咳痰"])
    has_runny_nose = any(word in symptom_text for word in ["流鼻涕", "鼻塞", "打喷嚏"])
    has_headache = any(word in symptom_text for word in ["头痛", "头疼", "头晕"])
    
    suggestion = f"""根据您描述的症状，AI初步分析如下：

【可能原因】
1. 普通感冒或流感（最可能）
2. 上呼吸道感染
3. 季节性过敏反应

【症状分析】"""
    
    if has_fever:
        suggestion += "\n- 发热症状提示可能存在感染"
    if has_cough:
        suggestion += "\n- 咳嗽可能是呼吸道受刺激的表现"
    if has_runny_nose:
        suggestion += "\n- 流鼻涕常见于感冒或过敏"
    if has_headache:
        suggestion += "\n- 头痛可能与发热或鼻塞相关"
    
    suggestion += """

【自我护理建议】
1. 多休息，保证充足睡眠（每天8小时以上）
2. 多喝温水，保持水分补充（每天2000ml以上）
3. 清淡饮食，多吃蔬菜水果
4. 保持室内通风，避免着凉
5. 可适当服用对乙酰氨基酚退烧（如体温超过38.5°C）

【用药建议】
- 退烧：对乙酰氨基酚片或布洛芬
- 止咳：复方甘草片、止咳糖浆
- 鼻塞：生理盐水鼻喷剂

【就医建议】
以下情况请立即就医：
- 体温超过39.5°C且持续不退
- 呼吸困难或胸痛
- 症状持续超过3天未好转
- 出现严重头痛、呕吐等症状

⚠️ 注意：此建议仅供参考，不代替专业医疗诊断。如症状严重或持续，请及时就医。

💡 提示：当前使用模拟AI建议（DeepSeek API暂时不可用)"""
    
    return suggestion

@router.post("/query-medicine", response_model=AIResponse)
async def ai_query_medicine(request: MedicineQueryRequest):
    """
    AI 药品查询助手
    提供药品的详细信息、用法用量、注意事项等
    """
    if not request.medicine_name or not request.medicine_name.strip():
        raise HTTPException(status_code=400, detail="药品名称不能为空")
    
    if OpenAI is None:
        raise HTTPException(status_code=500, detail="AI服务未配置")
    
    medicine_name = request.medicine_name.strip()
    print(f"💊 收到药品查询: {medicine_name}")
    
    try:
        client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            timeout=30.0
        )
        
        system_prompt = """你是一位专业的药学专家AI助手。你的职责是提供准确、全面的药品信息，包括：

1. 药品的通用名和商品名
2. 主要成分和作用机制
3. 适应症（用于治疗什么疾病）
4. 用法用量（常规剂量）
5. 注意事项和禁忌症
6. 常见副作用
7. **药物相互作用和用药禁忌**：详细说明哪些药物不能与其同时服用，包括具体的药物名称和原因。如果没有已知的药物相互作用，请明确说明“暂无已知的药物相互作用禁忌”或“但仍需遵医嘱”。

回答要求：
- 信息准确、专业但易懂
- 使用【】标记段落标题
- 强调用药安全和遵医嘱
- 对于药物相互作用，必须给出明确的结论，不可模棱两可
- 控制在500字以内"""
        
        user_prompt = f"请提供关于药品『{medicine_name}』的详细信息"
        
        print(f"🤖 正在调用DeepSeek API查询药品...")
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # 更低的温度以获得更准确的信息
            max_tokens=1200,
            stream=False
        )
        
        ai_response = response.choices[0].message.content or "未获取到AI回复"
        print(f"✅ 药品查询成功")
        
        return AIResponse(
            suggestion=ai_response,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"❌ 药品查询失败: {error_type}: {error_msg}")
        
        # 如果是网络连接错误，提供更详细的错误信息
        if "Connection" in error_type or "connection" in error_msg.lower():
            print("⚠️ 网络连接错误，可能的原因：")
            print("   1. 网络不稳定或无法访问DeepSeek API")
            print("   2. 需要配置代理")
            print("   3. 防火墙阻止了连接")
        
        # 返回简化的回复
        return AIResponse(
            suggestion=f"抱歉，暂时无法查询药品『{medicine_name}』的详细信息。\n\n原因：{error_type}\n建议：请检查网络连接或稍后重试，也可咨询医师、药师。",
            timestamp=datetime.now().isoformat()
        )

@router.post("/query-disease", response_model=AIResponse)
async def ai_query_disease(request: DiseaseQueryRequest):
    """
    AI 疾病查询助手
    提供疾病的详细信息、症状、治疗方案等
    """
    if not request.disease_name or not request.disease_name.strip():
        raise HTTPException(status_code=400, detail="疾病名称不能为空")
    
    if OpenAI is None:
        raise HTTPException(status_code=500, detail="AI服务未配置")
    
    disease_name = request.disease_name.strip()
    print(f"🏥 收到疾病查询: {disease_name}")
    
    try:
        client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            timeout=30.0
        )
        
        system_prompt = """你是一位专业的医学专家AI助手。你的职责是提供准确、全面的疾病信息，包括：

1. 疾病的医学定义和分类
2. 常见症状和体征
3. 可能的病因和发病机制
4. 诊断方法
5. 治疗方案（包括药物治疗和非药物治疗）
6. **常用药物及其用药禁忌**：列出常用治疗药物，并说明哪些药物之间不能同时使用。如果没有特殊禁忌，请说明“常规用药无明显禁忌，但应遵医嘱”。
7. 预防措施
8. 预后和注意事项

回答要求：
- 信息准确、专业但易懂
- 使用【】标记段落标题
- 强调及时就医的重要性
- 对于用药禁忌，必须给出明确的结论
- 控制在600字以内"""
        
        user_prompt = f"请提供关于疾病『{disease_name}』的详细信息"
        
        print(f"🤖 正在调用DeepSeek API查询疾病...")
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1500,
            stream=False
        )
        
        ai_response = response.choices[0].message.content or "未获取到AI回复"
        print(f"✅ 疾病查询成功")
        
        return AIResponse(
            suggestion=ai_response,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"❌ 疾病查询失败: {error_type}: {error_msg}")
        
        # 如果是网络连接错误，提供更详细的错误信息
        if "Connection" in error_type or "connection" in error_msg.lower():
            print("⚠️ 网络连接错误，可能的原因：")
            print("   1. 网络不稳定或无法访问DeepSeek API")
            print("   2. 需要配置代理")
            print("   3. 防火墙阻止了连接")
        
        return AIResponse(
            suggestion=f"抱歉，暂时无法查询疾病『{disease_name}』的详细信息。\n\n原因：{error_type}\n建议：请检查网络连接或稍后重试，也可咨询专业医师。",
            timestamp=datetime.now().isoformat()
        )
