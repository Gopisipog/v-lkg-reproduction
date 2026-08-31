"""MCP server entrypoint.

Creates a FastMCP instance named ``vlkg``, registers the graph and intel
tool modules, and exposes ``main()`` so the package can be launched via
the ``vlkg-mcp`` console script. All tools read through the shared
Neo4jClient wrapper (:mod:`vlkg_mcp.db`), which transparently falls back
to the local JSON graph store when no Neo4j instance is reachable.
"""

from __future__ import annotations

import sys
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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

    # Inject CORSMiddleware to handle CORS preflight OPTIONS requests (fixes 405 errors)
    orig_sse_app = mcp.sse_app
    def custom_sse_app(*args, **kwargs):
        app = orig_sse_app(*args, **kwargs)
        from starlette.middleware.cors import CORSMiddleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        return app
    mcp.sse_app = custom_sse_app

    return mcp


def main() -> None:
    import os
    server = build_server()
    port_env = os.environ.get("PORT")
    if port_env:
        port = int(port_env)
        server.settings.host = "0.0.0.0"
        server.settings.port = port
        server.settings.transport_security.enable_dns_rebinding_protection = False
        print(f"Starting MCP server in SSE mode on port {port}...")
        server.run(transport="sse")
    else:
        server.run()


if __name__ == "__main__":
    main()
