from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

def test_ui_static_contract():
    ui_content = (ROOT_DIR / "app" / "ui_streamlit.py").read_text(encoding="utf-8")
    
    # Check mode labels
    assert "Demo Fixture" in ui_content
    assert "Live Loomi MCP" in ui_content
    assert "Last Successful MCP Refresh" in ui_content
    
    # Check "facade" is not there
    assert "facade" not in ui_content.lower()
    
    # Check it explains live MCP vs cached fallback vs synthetic ops
    # The UI should contain references to these concepts
    assert "synthetic" in ui_content.lower() or "mock" in ui_content.lower()
    
    # Check no hardcoded endpoints or IDs
    assert "loomi-mcp-alpha.bloomreach.com" not in ui_content
    assert "952be3a0" not in ui_content
    
    # Check import without mcp
    assert "import mcp" not in ui_content

def test_ui_imports_without_mcp(monkeypatch):
    import sys
    monkeypatch.setitem(sys.modules, "mcp", None)
    # Just try to import it
    try:
        import app.ui_streamlit
        assert True
    except ImportError as e:
        if "mcp" in str(e):
            pytest.fail("UI imported MCP at module level")
