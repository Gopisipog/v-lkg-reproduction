"""Shared pytest fixtures for the vlkg_mcp test-suite.

The server is exercised through the FastMCP in-process API
(``list_tools`` / ``call_tool``) so the suite needs no external MCP client
or live Neo4j instance. Graph tools fall back to the JSON-backed
``LocalGraphStore``; intel tools instantiate the real ``src.core`` engines
(lazily built by :func:`vlkg_mcp.tools.intel._get_engine`).
"""

from __future__ import annotations

import pytest

from vlkg_mcp.tools import register_all


@pytest.fixture()
def server() -> "FastMCP":
    """Return a configured FastMCP instance with every tool registered.

    A fresh instance is created per test so tool sets do not leak across
    tests (especially for the regressive RED demo).
    """
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("vlkg")
    register_all(mcp)
    return mcp


@pytest.fixture()
async def tool_names(server) -> set[str]:
    """Public names of every tool registered on the server."""
    tools = await server.list_tools()
    return {tool.name for tool in tools}
