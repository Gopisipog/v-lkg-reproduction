"""MCP tool registration.

Importing this package registers every tool (graph + intel) onto the
server's FastMCP instance. The server module calls ``register_all`` once
at startup so tools are available before the stdio event loop begins.
"""

from __future__ import annotations

from . import graph, intel


def register_all(mcp) -> None:
    """Register all tool modules on the given FastMCP instance."""
    graph.register(mcp)
    intel.register(mcp)


__all__ = ["register_all", "graph", "intel"]
