import streamlit as st
import requests
import base64
from typing import Dict
import io
from PIL import Image
import os
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 从Streamlit Secrets获取凭证
account_id = st.secrets.get("CLOUDFLARE_ACCOUNT_ID", "")
api_token = st.secrets.get("CLOUDFLARE_API_TOKEN", "")

class MultiModelGenerator:
    def __init__(self, account_id: str, api_token: str):
        self.account_id = account_id
        self.api_token = api_token
        
        # 定义所有支持的AI模型
        self.models = [
            {
                "id": "@cf/stabilityai/stable-diffusion-xl-base-1.0",
                "name": "SDXL Base",
                "description": "最高质量的SDXL基础版本",
                "steps": None
            },
            {
                "id": "@cf/bytedance/stable-diffusion-xl-lightning",
                "name": "SDXL Lightning",
                "description": "字节优化的快速SDXL版本",
                "steps": None
            },
            {
                "id": "@cf/lykon/dreamshaper-8-lcm",
                "name": "Dreamshaper",
                "description": "快速的Dreamshaper模型",
                "steps": 8
            },
            {
                "id": "@cf/black-forest-labs/flux-1-schnell",
                "name": "Flux Schnell",
                "description": "轻量快速生成模型",
                "steps": 8
            }
        ]
        
        # 定义支持的图像尺寸
        self.sizes = [
            {"id": "1024x1024", "name": "1:1 方形 (1024x1024)"},
            {"id": "1024x576", "name": "16:9 横向 (1024x576)"},
            {"id": "576x1024", "name": "9:16 纵向 (576x1024)"}
        ]
        
        # 定义主题模板
        self.themes = [
            "a beautiful girl",
            "a handsome man", 
            "a future city",
            "a fantasy landscape", 
            "a cyberpunk scene", 
            "an ancient castle"
        ]

    async def generate_image_async(self, session, model: Dict, prompt: str, size: str) -> tuple:
        """异步生成图像"""
        width, height = map(int, size.split('x'))
        url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{model['id']}"
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "prompt": prompt,
            "width": width,
            "height": height
        }
        
        # 添加steps参数（如果模型需要）
        if model['steps']:
            params["steps"] = model['steps']
        
        try:
            async with session.post(url, headers=headers, json=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API错误: {error_text}")
                
                content_type = response.headers.get('content-type', '')
                
                if 'application/json' in content_type:
                    result = await response.json()
                    if model['id'] == "@cf/black-forest-labs/flux-1-schnell":
                        if 'result' in result and isinstance(result['result'], dict) and 'image' in result['result']:
                            image_data = base64.b64decode(result['result']['image'])
                        else:
                            raise Exception("Flux模型返回了意外的JSON格式")
                    else:
                        if 'error' in result:
                            raise Exception(f"API错误: {result['error']}")
                        image_data = await response.read()
                else:
                    image_data = await response.read()
                
                image = Image.open(io.BytesIO(image_data))
                return model['id'], image
                
        except Exception as e:
            return model['id'], e

    def generate_prompt_with_llm(self, theme: str) -> str:
        """使用LLM生成详细的图像提示词"""
        system_prompt = """You are an expert at writing Stable Diffusion prompts. Create detailed, artistic prompts for image generation.

Important rules for the prompts:
1. Be VERY detailed and descriptive
2. Include ALL of these aspects:
   - Main subject details
   - Lighting and atmosphere
   - Color palette or mood
   - Camera angle or perspective
   - Artistic style or medium
   - Technical quality terms

Format your prompt like this:
[main subject details], [lighting], [atmosphere], [colors/mood], [camera/perspective], [artistic style], [technical quality]

Examples:
Theme: a beautiful girl
"ethereal young woman with flowing auburn hair and delicate features, soft golden hour sunlight streaming through gossamer curtains, dreamy atmospheric mood, warm pastel color palette, medium close-up shot with shallow depth of field, fashion photography style, cinematic composition, 8k resolution, masterpiece quality, highly detailed"

Theme: a cyberpunk city
"massive cyberpunk metropolis with towering crystalline skyscrapers, neon signs reflecting in rain-slicked streets, volumetric fog catching holographic advertisements, moody night atmosphere with electric blue and purple hues, dramatic low angle view looking up, blade runner style, ray traced lighting, cinematic composition, 8k resolution, masterpiece quality, photorealistic details"
"""

        user_prompt = f"""Create a highly detailed Stable Diffusion prompt for: {theme}
Include specific details about subject, lighting, atmosphere, colors, camera view, and artistic style."""
        
        try:
            url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/@cf/deepseek-ai/deepseek-r1-distill-qwen-32b"
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            prompt = result['result']['response'].strip()
            prompt = prompt.replace('PROMPT:', '').replace('think', '')
            prompt = prompt.replace('<', '').replace('>', '')
            prompt = prompt.split('\n')[0].strip()
            
            if not any(term in prompt.lower() for term in ['8k', 'masterpiece', 'highly detailed']):
                prompt = f"{prompt}, 8k, masterpiece, highly detailed"
            
            return prompt
            
        except Exception as e:
            st.error(f"生成提示词失败: {e}")
            return f"{theme}, cinematic lighting, highly detailed, 8k"

async def main():
    st.set_page_config(
        page_title="AI图像生成器 V2",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎨 AI图像生成器 V2")
    st.markdown("### 使用多个Cloudflare AI模型同时生成图像，对比不同模型的效果")
    
    if not account_id or not api_token:
        st.error("请设置Cloudflare凭证！")
        st.stop()
    
    # 初始化生成器
    generator = MultiModelGenerator(account_id=account_id, api_token=api_token)
    
    # 侧边栏设置
    with st.sidebar:
        st.header("🛠️ 设置")
        
        # 选择图像尺寸
        selected_size = st.selectbox(
            "📐 选择图像尺寸",
            options=generator.sizes,
            format_func=lambda x: x['name']
        )
        
        # 选择是否使用AI生成提示词
        use_ai_prompt = st.checkbox("🤖 使用AI生成提示词", value=True)
        
        if use_ai_prompt:
            selected_theme = st.selectbox(
                "🎯 选择主题",
                options=generator.themes,
                help="选择一个主题，AI将为您生成详细的图像提示词"
            )
            
            if st.button("🎲 生成提示词", use_container_width=True):
                with st.spinner("🤖 AI正在创作提示词..."):
                    prompt = generator.generate_prompt_with_llm(selected_theme)
                    st.session_state.generated_prompt = prompt
                    st.success("✨ 提示词生成完成！")
            
            prompt = st.text_area(
                "✏️ AI生成的提示词 (可以修改)",
                value=st.session_state.get('generated_prompt', ''),
                height=150,
                help="这是AI根据选择的主题生成的详细提示词，您可以直接使用或进行修改"
            )
        else:
            prompt = st.text_area(
                "✏️ 输入提示词",
                height=150,
                help="描述您想要生成的图像，可以非常详细"
            )
        
        generate_button = st.button("🎨 同时生成所有图像", type="primary", use_container_width=True)

    # 主要内容区域
    if generate_button and prompt:
        # 创建2x2网格
        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)
        
        grid = [
            row1_col1, row1_col2,
            row2_col1, row2_col2
        ]
        
        # 创建进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 为每个模型创建占位符
        placeholders = {}
        for i, model in enumerate(generator.models):
            with grid[i]:
                st.subheader(f"📸 {model['name']}")
                st.markdown(f"*{model['description']}*")
                placeholders[model['id']] = st.empty()
        
        # 异步生成所有图像
        async with aiohttp.ClientSession() as session:
            tasks = []
            for model in generator.models:
                task = generator.generate_image_async(session, model, prompt, selected_size['id'])
                tasks.append(task)
            
            # 等待所有任务完成
            total_models = len(generator.models)
            completed = 0
            
            for coro in asyncio.as_completed(tasks):
                model_id, result = await coro
                completed += 1
                progress = completed / total_models
                progress_bar.progress(progress)
                status_text.text(f"已完成 {completed}/{total_models} 个模型")
                
                # 获取对应的模型信息
                model = next(m for m in generator.models if m['id'] == model_id)
                
                # 显示结果
                if isinstance(result, Exception):
                    placeholders[model_id].error(f"❌ {model['name']} 生成失败: {str(result)}")
                else:
                    placeholders[model_id].image(
                        result,
                        caption=f"由 {model['name']} 生成",
                        use_column_width=True
                    )
                    
                    # 提供下载按钮
                    buf = io.BytesIO()
                    result.save(buf, format="PNG")
                    with grid[generator.models.index(model)]:
                        st.download_button(
                            label=f"⬇️ 下载 {model['name']} 生成的图像",
                            data=buf.getvalue(),
                            file_name=f"generated_image_{model['name']}.png",
                            mime="image/png",
                            use_container_width=True
                        )
        
        # 完成后清除进度条和状态文本
        progress_bar.empty()
        status_text.empty()
        st.success("🎉 所有图像生成完成！")
    else:
        st.info("👈 请在左侧设置提示词并点击生成按钮开始创建图像")

if __name__ == "__main__":
    asyncio.run(main()) 