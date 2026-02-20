"""
OCR 配置文件
"""

class OCRConfig:
    """PaddleOCR 配置"""

    # 硅基流动 API 配置
    # API Key 需要在首次运行时配置
    API_KEY = ""  # 用户需要自行配置
    SERVER_URL = "https://api.siliconflow.cn/v1"
    MODEL_NAME = "PaddlePaddle/PaddleOCR-VL-1.5"
    BACKEND = "vllm-server"

    # 路径配置
    INPUT_DIR = "./images/input"
    OUTPUT_DIR = "./images/output"
