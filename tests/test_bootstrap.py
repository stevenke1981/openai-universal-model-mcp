"""Offline checks for the module bootstrap contract."""
from pathlib import Path


def test_server_module_is_launchable_without_relative_imports():
    server = Path(__file__).resolve().parents[1] / "src/openai_universal_model_mcp/server.py"
    source = server.read_text(encoding="utf-8")
    assert "from .api import" not in source
    assert "from openai_universal_model_mcp.api import" in source
    assert 'if __name__ == "__main__":' in source
    assert 'mcp.run(transport="stdio")' in source


def test_launch_examples_use_module_entrypoint():
    root = Path(__file__).resolve().parents[1]
    for file in ["scripts/run.ps1", "examples/codex-config.toml", "examples/cursor-mcp.json", "examples/claude-desktop-config.json"]:
        source = (root / file).read_text(encoding="utf-8")
        assert "openai_universal_model_mcp.server" in source
        assert "src/openai_universal_model_mcp/server.py" not in source
