"""
硅基流动 OCR 轻量化调用模块
直接使用 requests 调用硅基流动 API，无需依赖 paddleocr 包
"""

import base64
import requests
from typing import List, Optional


class SiliconFlowOCR:
    """硅基流动 OCR 轻量化客户端"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.siliconflow.cn/v1",
        model: str = "PaddlePaddle/PaddleOCR-VL"
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _encode_image(self, image_path: str) -> str:
        """将图片编码为 base64（不压缩）"""
        from PIL import Image
        import io

        # 打开图片
        img = Image.open(image_path)
        print(f"[DEBUG] 原始图片尺寸: {img.size}, 模式: {img.mode}")

        # 只转换格式，不压缩
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 保存到内存并编码（使用 PNG 保持质量）
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        encoded = base64.b64encode(buffer.read()).decode('utf-8')
        print(f"[DEBUG] Base64 编码后大小: {len(encoded)} 字符 (~{len(encoded)//1024}KB)")

        return encoded

    def recognize(self, image_path: str) -> List[str]:
        """
        识别图片中的文字

        Args:
            image_path: 图片文件路径

        Returns:
            识别到的文字列表
        """
        # 编码图片
        image_base64 = self._encode_image(image_path)

        # 构造请求数据（使用 OpenAI 兼容格式）
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": "OCR:"  # PaddleOCR-VL 的任务标识
                        }
                    ]
                }
            ],
            "temperature": 0.0,
            "max_tokens": 15000  # 增加到 16K 以支持更多文字
        }

        # 发送请求（增加超时时间到 60 秒）
        url = f"{self.base_url}/chat/completions"

        print(f"[DEBUG] 发送请求到: {url}")
        print(f"[DEBUG] 模型: {self.model}")
        print(f"[DEBUG] 图片数据长度: {len(image_base64)} 字符")

        # 添加重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=60  # 增加到 60 秒
                )
                print(f"[DEBUG] 响应状态码: {response.status_code}")
                break  # 成功则跳出循环
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"[WARN] 请求超时，正在重试 ({attempt + 1}/{max_retries})...")
                    continue
                else:
                    raise Exception(f"API 请求超时: 已重试 {max_retries} 次")
            except requests.exceptions.RequestException as e:
                raise Exception(f"API 请求失败: {e}")

        # 检查响应
        if response.status_code != 200:
            raise Exception(
                f"API 请求失败 (状态码 {response.status_code}): {response.text}"
            )

        # 解析结果
        result = response.json()
        print(f"[DEBUG] 完整 API 响应 JSON:\n{result}\n")

        try:
            content = result['choices'][0]['message']['content']

            # 打印完整响应用于调试
            print(f"[DEBUG] API 返回内容:\n'{content}'\n")
            print(f"[DEBUG] 响应长度: {len(content)} 字符")

            # 如果内容为空或只包含空白字符
            if not content or content.strip() == "":
                print("[WARN] API 返回空内容，可能是图片太小或没有文字")
                return []

            # 按行分割
            raw_lines = [line.strip() for line in content.split('\n') if line.strip()]

            # 去重处理
            unique_lines = []
            prev_line = None

            for line in raw_lines:
                # 先检查是否与上一行完全重复
                if line == prev_line:
                    print(f"[去重] 跳过重复行: {repr(line)}")
                    continue

                # 检查行内是否有重复内容 (如 "天然成分 天然成分")
                words = line.split()
                # 去除连续重复的词
                dedup_words = []
                prev_word = None
                for word in words:
                    if word != prev_word:
                        dedup_words.append(word)
                        prev_word = word

                dedup_line = ' '.join(dedup_words)

                if dedup_line != line:
                    print(f"[去重] 行内去重: {repr(line)} -> {repr(dedup_line)}")

                unique_lines.append(dedup_line)
                prev_line = line

            print(f"[DEBUG] 原始行数: {len(raw_lines)}, 去重后: {len(unique_lines)}")
            for i, line in enumerate(unique_lines):
                print(f"[DEBUG]   行 {i+1}: {repr(line)}")

            return unique_lines
        except (KeyError, IndexError) as e:
            raise Exception(f"解析 API 响应失败: {e}, 完整响应: {result}")


# 兼容旧接口的包装类
class PaddleOCRVL:
    """兼容 PaddleOCRVL 接口的包装类"""

    def __init__(
        self,
        vl_rec_backend: Optional[str] = None,
        vl_rec_server_url: Optional[str] = None,
        vl_rec_api_model_name: Optional[str] = None,
        vl_rec_api_key: Optional[str] = None,
        **kwargs
    ):
        # 使用硅基流动 OCR
        self.ocr = SiliconFlowOCR(
            api_key=vl_rec_api_key or "",
            base_url=vl_rec_server_url or "https://api.siliconflow.cn/v1",
            model=vl_rec_api_model_name or "PaddlePaddle/PaddleOCR-VL"
        )
        print(f"[SiliconFlow OCR] 已初始化")
        print(f"  - 服务器: {vl_rec_server_url}")
        print(f"  - 模型: {vl_rec_api_model_name}")

    def predict(self, image_path: str):
        """
        预测图片内容（兼容接口）

        返回格式与原 PaddleOCRVL 兼容
        """
        text_list = self.ocr.recognize(image_path)

        # 构造兼容的结果格式
        result = [{
            'parsing_res_list': [
                type('obj', (object,), {'content': text})()
                for text in text_list
            ]
        }]

        return result