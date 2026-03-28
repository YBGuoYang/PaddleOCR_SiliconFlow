"""Application-level OCR workflow helpers."""

from __future__ import annotations

from typing import Callable

from .config import AppConfig
from .logging_utils import log_info, log_ok
from .ocr_client import PaddleOCRVL, extract_text_from_prediction


class OCRService:
    """Thin service around OCR client initialization and prediction."""

    def __init__(
        self,
        config: AppConfig,
        *,
        server_url: str,
        model_name: str,
        backend: str,
        pipeline_factory: Callable[..., PaddleOCRVL] = PaddleOCRVL,
    ):
        self.config = config
        self.server_url = server_url
        self.model_name = model_name
        self.backend = backend
        self.pipeline_factory = pipeline_factory
        self.pipeline: PaddleOCRVL | None = None

    def initialize(self) -> None:
        log_info("正在初始化 PaddleOCR...")
        self.pipeline = self.pipeline_factory(
            vl_rec_backend=self.backend,
            vl_rec_server_url=self.server_url,
            vl_rec_api_model_name=self.model_name,
            vl_rec_api_key=self.config.api_key,
        )
        log_ok("OCR 初始化完成")

    def update_api_key(self, api_key: str) -> None:
        self.config.api_key = api_key.strip()
        self.initialize()

    def recognize_file(self, image_path: str) -> list[str]:
        if self.pipeline is None:
            self.initialize()
        assert self.pipeline is not None
        results = self.pipeline.predict(image_path)
        return extract_text_from_prediction(results)
