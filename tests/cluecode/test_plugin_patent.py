import json
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import load_json_result


def test_patent_detection_basic(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("US Patent 8,123,456 B2 and patent pending.")

    result_file = tmp_path / "result.json"

    run_scan_click(
        ["--patent", "--json", str(result_file), str(test_file)]
    )

    result = load_json_result(result_file)

    detections = result["files"][0].get("patent_detections", [])

    assert len(detections) == 2

    values = [d["patent_reference"] for d in detections]

    assert "US Patent 8,123,456 B2" in values
    assert "patent pending" in values

    for d in detections:
        assert "type" in d
        assert "start_line" in d
        assert "end_line" in d


def test_patent_detection_none(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("This file has no patent reference.")

    result_file = tmp_path / "result.json"

    run_scan_click(
        ["--patent", "--json", str(result_file), str(test_file)]
    )

    result = load_json_result(result_file)

    detections = result["files"][0].get("patent_detections", [])

    assert detections == []


def test_patent_international_formats(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text(
        "EP1234567B1\nWO 2019/123456\nUS20190012345A1"
    )

    result_file = tmp_path / "result.json"

    run_scan_click(
        ["--patent", "--json", str(result_file), str(test_file)]
    )

    result = load_json_result(result_file)

    detections = result["files"][0].get("patent_detections", [])

    values = [d["patent_reference"] for d in detections]

    assert any("EP1234567B1" in v for v in values)
    assert any("WO 2019/123456" in v for v in values)
    assert any("US20190012345A1" in v for v in values)


def test_patent_no_false_positive(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("This is unpatented technology.")

    result_file = tmp_path / "result.json"

    run_scan_click(
        ["--patent", "--json", str(result_file), str(test_file)]
    )

    result = load_json_result(result_file)

    detections = result["files"][0].get("patent_detections", [])

    assert detections == []


def test_patent_threshold(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text(
        "US Patent 1\nUS Patent 2\nUS Patent 3"
    )

    result_file = tmp_path / "result.json"

    run_scan_click(
        ["--patent", "--max-patent", "1", "--json", str(result_file), str(test_file)]
    )

    result = load_json_result(result_file)

    detections = result["files"][0].get("patent_detections", [])

    assert len(detections) == 1
    assert detections[0]["patent_reference"] == "US Patent 1"
    