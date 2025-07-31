# src/image_analyzer.py
import os
import base64
from openai import OpenAI

# 支持的图像格式
SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png')


def encode_image_to_base64(image_path):
    """将本地图片编码为 base64 字符串"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def is_image_file(file_path):
    """判断是否是支持的图像文件"""
    return os.path.isfile(file_path) and file_path.lower().endswith(SUPPORTED_FORMATS)


def analyze_image(image_path):
    """分析图像并返回识别结果"""
    try:
        if not is_image_file(image_path):
            return "错误：请提供一个有效的图像文件（jpg/png）"

        # 将图片转为 base64
        base64_image = encode_image_to_base64(image_path)

        # 初始化客户端
        client = OpenAI(
            base_url="https://ark.cn-beijing.volces.com/api/v3",  # 去掉多余空格
            api_key=os.environ.get("ARK_API_KEY"),
        )

        response = client.chat.completions.create(
            model="doubao-1.5-vision-lite-250315",  # doubao-1.5-vision-lite-250315，doubao-seed-1-6-flash-250715（有点垃圾）
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                # 使用你测试成功的URL格式
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                "返回被方框框起来的单词和短语，逗号分隔"
                                # "这篇文章中有一些英文单词或短语被方框框住了。请你按照以下要求处理这些被框起来的内容："
                                # "要求："
                                # "1.列出所有被方框框起来的英文单词或短语。"
                                # "2.筛选符合以下标准的短语："
                                # "核心特征：该短语由 2 个及以上单词组成，但其整体语义无法通过组成单词的字面意思直接组合推导，属于固定搭配、习语、成语或具有特殊引申义的表达（即 “语义不可拆分”）。"
                                # "排除标准：若短语的语义可由组成单词的字面意思简单叠加得出（如 “generally speaking”=“generally（一般地）+ speaking（说）”→“一般来说”），无特殊引申义，则排除此类短语。"
                                # "3.对于不符合上述标准的短语，返回其中一个词义比较重要的单词。"
                                # "返回要求：以逗号分隔的形式返回，"
                                # "返回示例：apple, banana, cat,take on"
                            )
                        },
                    ],
                }
            ],
        )

        result = response.choices[0].message.content.strip()
        return result

    except Exception as e:
        return f"分析失败：{str(e)}"


def save_result_to_file(result, filename="word.txt"):
    """将结果保存到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(result)
        return True
    except Exception as e:
        print(f"保存文件失败：{str(e)}")
        return False