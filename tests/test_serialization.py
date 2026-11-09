from openai_universal_model_mcp.security import parse_json_object_or_array


def test_parse_json_array():
    value = parse_json_object_or_array('[{"role":"user","content":"hi"}]', "payload")
    assert isinstance(value, list)
    assert value[0]["role"] == "user"


def test_parse_json_invalid():
    try:
        parse_json_object_or_array("{broken", "payload")
    except ValueError as exc:
        assert "valid JSON" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
