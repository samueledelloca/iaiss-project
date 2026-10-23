"""The MCP server builds and exposes every tool (Paper2Agent validation)."""
from __future__ import annotations
import asyncio, inspect, sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "model"))
from c9n2a import paths, tools as T

pytestmark = pytest.mark.skipif(
    not (paths.DATASETS / "fig2_fluorospot_responses.csv").exists(),
    reason="datasets not built")

def _await(x):
    return asyncio.run(x) if inspect.iscoroutine(x) else x

def test_server_registers_all_tools():
    from model.mcp_server import build_server
    mcp = build_server()
    listed = _await(mcp.list_tools())
    assert {t.name for t in listed} == set(T.TOOLS)

def test_server_call_tool_roundtrip():
    from model.mcp_server import build_server
    mcp = build_server()
    res = _await(mcp.call_tool("list_datasets", {}))
    assert res.content
