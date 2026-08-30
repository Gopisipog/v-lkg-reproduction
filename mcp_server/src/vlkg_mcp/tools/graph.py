"""Graph intelligence MCP tools.

Thin wrappers around the shared database access layer (``vlkg_mcp.db``)
that expose the color-coded knowledge graph to MCP clients. Every tool
returns JSON-serializable data and clamps output size via pagination or
limits so large local graphs stay usable over stdio MCP.
"""

from __future__ import annotations

from typing import Any, Optional

from mcp.server.fastmcp import Context

from .. import db

import json

# Hard bound on how many records any list-like tool returns at once.
DEFAULT_LIMIT = 200


def _clamp(
    rows: list[dict[str, Any]],
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Apply offset/limit to a list of dict rows (JSON-safe slice)."""
    limit = max(1, limit)
    offset = max(0, offset)
    return rows[offset : offset + limit]


def register(mcp) -> None:
    """Register every graph tool on the given FastMCP instance."""

    @mcp.tool(
        name="graph_stats",
        title="Graph statistics",
        description=(
            "Return aggregate statistics for the knowledge graph: node count, "
            "relationship count, and average degree. Backs the 'Graph' "
            "analytics overview."
        ),
    )
    def graph_stats() -> dict[str, Any]:
        stats = db.get_stats()
        return {
            "node_count": stats.get("node_count", 0),
            "relationship_count": stats.get("relationship_count", stats.get("rel_count", 0)),
            "average_degree": stats.get("average_degree", stats.get("avg_degree", 0.0)),
            "rel_count": stats.get("rel_count", stats.get("relationship_count", 0)),
            "avg_degree": stats.get("avg_degree", stats.get("average_degree", 0.0)),
        }

    @mcp.tool(
        name="graph_type_counts",
        title="Entity counts by type",
        description="Return the number of entities grouped by their type/label.",
    )
    def graph_type_counts() -> dict[str, int]:
        return db.get_type_counts()

    @mcp.tool(
        name="graph_video_ids",
        title="Known video IDs",
        description="Return the unique sorted list of video IDs referenced in the graph.",
    )
    def graph_video_ids() -> str:
        return json.dumps(db.get_video_ids())

    @mcp.tool(
        name="graph_entities",
        title="Knowledge entities",
        description=(
            "Return color-coded knowledge entities shared across intelligence "
            "domains. Optionally pass `exclude_types` to hide a specific "
            "domain's marker nodes. Paginated via `limit`/`offset`."
        ),
    )
    def graph_entities(
        exclude_types: Optional[list[str]] = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> str:
        return json.dumps(_clamp(
            db.get_knowledge_entities(exclude_types=exclude_types),
            limit=limit,
            offset=offset,
        ))

    @mcp.tool(
        name="graph_entities_by_domain",
        title="Entities extracted by a domain",
        description=(
            "Return intelligence entities extracted by a specific domain "
            "(e.g. 'competitive', 'compliance') with video provenance. "
            "Paginated via `limit`/`offset`."
        ),
    )
    def graph_entities_by_domain(
        domain_name: str,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> str:
        return json.dumps(_clamp(
            db.get_entities_by_domain(domain_name),
            limit=limit,
            offset=offset,
        ))

    @mcp.tool(
        name="graph_triplets",
        title="Semantic triplets",
        description=(
            "Return semantic triplets subject-relation-object with optional "
            "filters on subject, relation, object, or video_id. Paginated via "
            "`limit`/`offset`."
        ),
    )
    def graph_triplets(
        subject: Optional[str] = None,
        relation: Optional[str] = None,
        obj: Optional[str] = None,
        video_id: Optional[str] = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> str:
        return json.dumps(_clamp(
            db.get_triplets(
                subject=subject,
                relation=relation,
                obj=obj,
                video_id=video_id,
            ),
            limit=limit,
            offset=offset,
        ))
