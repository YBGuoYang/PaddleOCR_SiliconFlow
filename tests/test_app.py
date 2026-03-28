from screenshot_ocr.app import OCRService
from screenshot_ocr.config import AppConfig


class FakePipeline:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def predict(self, image_path):
        return [
            {
                "parsing_res_list": [
                    type("Item", (object,), {"content": "line-1"})(),
                    type("Item", (object,), {"content": "line-2"})(),
                ]
            }
        ]


def test_ocr_service_initializes_with_config_api_key():
    config = AppConfig(api_key="sk-test")
    service = OCRService(
        config,
        server_url="https://example.com",
        model_name="demo-model",
        backend="demo-backend",
        pipeline_factory=FakePipeline,
    )

    service.initialize()

    assert service.pipeline is not None
    assert service.pipeline.kwargs["vl_rec_api_key"] == "sk-test"


def test_ocr_service_recognize_file_extracts_text():
    service = OCRService(
        AppConfig(api_key="sk-test"),
        server_url="https://example.com",
        model_name="demo-model",
        backend="demo-backend",
        pipeline_factory=FakePipeline,
    )

    assert service.recognize_file("demo.png") == ["line-1", "line-2"]
