"""MCP server entrypoint.

Creates a FastMCP instance named ``vlkg``, registers the graph and intel
tool modules, and exposes ``main()`` so the package can be launched via
the ``vlkg-mcp`` console script. All tools read through the shared
Neo4jClient wrapper (:mod:`vlkg_mcp.db`), which transparently falls back
to the local JSON graph store when no Neo4j instance is reachable.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import __version__
from .tools import register_all


def build_server() -> FastMCP:
    mcp = FastMCP(
        "vlkg",
        instructions=(
            "Virtual-LKG knowledge graph + intelligence MCP server. "
            "Graph tools read entities/triplets via the shared datastore; "
            "intel tools run the 17 core intelligence modules."
        ),
    )
    register_all(mcp)
    return mcp


def main() -> None:
    server = build_server()
    server.run()


if __name__ == "__main__":
    main()
