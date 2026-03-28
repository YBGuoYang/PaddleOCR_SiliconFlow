from screenshot_ocr.ocr_client import extract_text_from_prediction


def test_extract_text_from_prediction_collects_content():
    prediction = [
        {
            "parsing_res_list": [
                type("Item", (object,), {"content": "第一行"})(),
                type("Item", (object,), {"content": ""})(),
                type("Item", (object,), {"content": "第二行"})(),
            ]
        }
    ]

    assert extract_text_from_prediction(prediction) == ["第一行", "第二行"]
