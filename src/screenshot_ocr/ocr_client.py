"""OCR client helpers and legacy compatibility wrapper."""

from __future__ import annotations

import base64
import io
from typing import Any

import requests
from PIL import Image

from .logging_utils import log_debug, log_warn


def extract_text_from_prediction(results: list[dict[str, Any]]) -> list[str]:
    """Extract normalized text lines from compatibility prediction results."""
    text_list: list[str] = []
    for result in results:
        parsing_res = result.get("parsing_res_list", [])
        for item in parsing_res:
            content = getattr(item, "content", "")
            if content:
                text_list.append(content)
    return text_list


def _deduplicate_lines(raw_lines: list[str]) -> list[str]:
    unique_lines: list[str] = []
    prev_line: str | None = None
    for line in raw_lines:
        if line == prev_line:
            log_debug(f"去重: 跳过重复行 {line!r}")
            continue

        dedup_words: list[str] = []
        prev_word: str | None = None
        for word in line.split():
            if word != prev_word:
                dedup_words.append(word)
                prev_word = word
        dedup_line = " ".join(dedup_words)

        if dedup_line != line:
            log_debug(f"去重: 行内去重 {line!r} -> {dedup_line!r}")

        unique_lines.append(dedup_line)
        prev_line = line
    return unique_lines


class SiliconFlowOCR:
    """Lightweight SiliconFlow OCR client using the OpenAI-compatible endpoint."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.siliconflow.cn/v1",
        model: str = "PaddlePaddle/PaddleOCR-VL",
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _encode_image(self, image_path: str) -> str:
        image = Image.open(image_path)
        log_debug(f"原始图片尺寸: {image.size}, 模式: {image.mode}")

        if image.mode != "RGB":
            image = image.convert("RGB")

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        log_debug(f"Base64 编码后大小: {len(encoded)} 字符 (~{len(encoded)//1024}KB)")
        return encoded

    def _build_payload(self, image_base64: str) -> dict[str, Any]:
        return {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}",
                            },
                        },
                        {"type": "text", "text": "OCR:"},
                    ],
                }
            ],
            "temperature": 0.0,
            "max_tokens": 15000,
        }

    def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        log_debug(f"发送请求到: {url}")
        log_debug(f"模型: {self.model}")

        max_retries = 3
        response = None
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, headers=self.headers, timeout=60)
                log_debug(f"响应状态码: {response.status_code}")
                break
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    log_warn(f"请求超时，正在重试 ({attempt + 1}/{max_retries})...")
                    continue
                raise Exception(f"API 请求超时: 已重试 {max_retries} 次")
            except requests.exceptions.RequestException as exc:
                raise Exception(f"API 请求失败: {exc}")

        if response is None:
            raise Exception("API 请求失败: 未收到响应")
        if response.status_code != 200:
            raise Exception(f"API 请求失败 (状态码 {response.status_code}): {response.text}")
        return response.json()

    def _parse_response(self, result: dict[str, Any]) -> list[str]:
        try:
            content = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise Exception(f"解析 API 响应失败: {exc}, 完整响应: {result}")

        log_debug(f"API 返回内容:\n{content!r}\n")
        if not content or content.strip() == "":
            log_warn("API 返回空内容，可能是图片太小或没有文字")
            return []

        raw_lines = [line.strip() for line in content.split("\n") if line.strip()]
        unique_lines = _deduplicate_lines(raw_lines)
        log_debug(f"原始行数: {len(raw_lines)}, 去重后: {len(unique_lines)}")
        for index, line in enumerate(unique_lines, start=1):
            log_debug(f"  行 {index}: {line!r}")
        return unique_lines

    def recognize(self, image_path: str) -> list[str]:
        image_base64 = self._encode_image(image_path)
        payload = self._build_payload(image_base64)
        result = self._request(payload)
        log_debug(f"完整 API 响应 JSON:\n{result}\n")
        return self._parse_response(result)


class PaddleOCRVL:
    """Compatibility wrapper used by the current UI scripts."""

    def __init__(
        self,
        vl_rec_backend: str | None = None,
        vl_rec_server_url: str | None = None,
        vl_rec_api_model_name: str | None = None,
        vl_rec_api_key: str | None = None,
        **_: Any,
    ):
        self.ocr = SiliconFlowOCR(
            api_key=vl_rec_api_key or "",
            base_url=vl_rec_server_url or "https://api.siliconflow.cn/v1",
            model=vl_rec_api_model_name or "PaddlePaddle/PaddleOCR-VL",
        )
        log_debug("[SiliconFlow OCR] 已初始化")
        log_debug(f"  - 服务器: {vl_rec_server_url}")
        log_debug(f"  - 模型: {vl_rec_api_model_name}")

    def predict(self, image_path: str) -> list[dict[str, Any]]:
        text_list = self.ocr.recognize(image_path)
        return [
            {
                "parsing_res_list": [
                    type("PredictionItem", (object,), {"content": text})()
                    for text in text_list
                ]
            }
        ]
