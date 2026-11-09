from pathlib import Path

import pytest

from openai_universal_model_mcp.security import (
    output_path,
    validate_api_endpoint,
    validate_model_id,
)


def test_model_id_validation():
    assert validate_model_id("gpt-6.1-sol") == "gpt-6.1-sol"
    with pytest.raises(ValueError):
        validate_model_id("../secret")


def test_safe_api_allowlist():
    assert validate_api_endpoint("POST", "/v1/responses") == ("POST", "responses")
    assert validate_api_endpoint("POST", "realtime/translations/client_secrets") == ("POST", "realtime/translations/client_secrets")
    assert validate_api_endpoint("GET", "models/gpt-6-astra") == ("GET", "models/gpt-6-astra")
    with pytest.raises(ValueError):
        validate_api_endpoint("DELETE", "models/gpt-6-astra")
    with pytest.raises(ValueError):
        validate_api_endpoint("POST", "https://evil.example/steal")
    with pytest.raises(ValueError):
        validate_api_endpoint("POST", "../admin/keys")


def test_output_path_cannot_escape_directory(tmp_path: Path):
    target = output_path("../../evil.png", "png", tmp_path)
    assert target.parent == tmp_path.resolve()
    assert target.name == "evil.png"
