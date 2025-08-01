# src/LLMAPI.py
import os
from openai import OpenAI
import json
import logging

# 配置日志记录（可选，但推荐）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化Ark客户端
# 假设 API Key 已通过环境变量 ARK_API_KEY 设置
# 注意：原始 URL 末尾有空格，已修正
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
ARK_API_KEY = os.environ.get("ARK_API_KEY")

if not ARK_API_KEY:
    raise ValueError("环境变量 ARK_API_KEY 未设置。请先设置您的 API Key。")

client = OpenAI(
    base_url=ARK_BASE_URL,
    api_key=ARK_API_KEY,
)

def call_doubao_model(model_name, prompt_text):
    """
    调用豆包大模型 API。

    Args:
        model_name (str): 要调用的方舟推理接入点 ID (例如: "doubao-seed-1-6-flash-250615")。
        prompt_text (str): 发送给模型的文本提示词。

    Returns:
        str or None: 返回模型的主要文本回复内容。如果调用失败，则返回 None。
                     注意：此函数返回的是原始文本，可能需要调用方进一步处理（如解析 JSON）。
    """
    try:
        logger.info(f"🤖 正在调用豆包模型 '{model_name}'...")
        logger.debug(f"📝 发送的提示词: {prompt_text}")

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        # 注意：原始 image_url 末尾有空格，已修正
                        # 如果需要发送图片，可以在这里添加 image_url 部分
                        # {
                        #     "type": "image_url",
                        #     "image_url": {
                        #         "url": "https://your-image-url.com/image.jpg"
                        #     },
                        # },
                        {"type": "text", "text": prompt_text},
                    ],
                }
            ],
            # 可以根据需要添加其他参数，例如 temperature, max_tokens 等
        )

        # 提取主要的回复文本
        reply_content = response.choices[0].message.content
        logger.info("✅ 豆包模型调用成功。")
        logger.debug(f"🤖 模型回复: {reply_content}")
        return reply_content

    except Exception as e:
        logger.error(f"❌ 调用豆包模型 '{model_name}' 时出错: {e}")
        return None

# # --- 示例用法 (如果直接运行此脚本) ---
# if __name__ == "__main__":
#     # 请确保环境变量 ARK_API_KEY 已设置
#     model_to_use = "doubao-seed-1-6-flash-250615" # 替换为你的实际模型ID
#     test_prompt = "你好，请介绍一下你自己。"
#
#     result = call_doubao_model(model_to_use, test_prompt)
#     if result:
#         print("模型回复:")
#         print(result)
#     else:
#         print("调用模型失败。")
