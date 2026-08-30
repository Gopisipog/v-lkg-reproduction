"""Shared database access layer for the VLKG MCP server.

Wraps the application's ``Neo4jClient`` which already encapsulates the
Neo4j <-> LocalGraphStore (JSON) fallback decision. This module exposes a
single module-level accessor so every tool reaches the *same* client
instance (authoritative data, no divergent copies).
"""

from __future__ import annotations

from typing import Any, Optional

# The app's own client already handles connectivity + local fallback.
from src.database.neo4j_client import Neo4jClient


_client: Optional[Neo4jClient] = None


def get_client() -> Neo4jClient:
    """Return the shared :class:`Neo4jClient` instance (created lazily).

    The first call constructs the client, which attempts a real Neo4j
    connection and transparently routes to the JSON-based
    ``LocalGraphStore`` backend when Neo4j is unreachable. Subsequent
    calls reuse the same instance.
    """
    global _client
    if _client is None:
        _client = Neo4jClient()
    return _client


def get_stats() -> dict[str, Any]:
    """Graph statistics: node count, relationship count, average degree."""
    return get_client().get_stats()


def get_type_counts() -> dict[str, int]:
    """Count of entities grouped by type."""
    return get_client().get_type_counts()


def get_video_ids() -> list[str]:
    return get_client().get_video_ids()


def get_knowledge_entities(exclude_types: Optional[list[str]] = None) -> list[dict[str, Any]]:
    """All color-coded knowledge entities, optionally excluding types."""
    return get_client().get_knowledge_entities(exclude_types=exclude_types)


def get_entities_by_domain(domain_name: str) -> list[dict[str, Any]]:
    """Entities extracted by a specific intelligence domain, with provenance."""
    return get_client().get_entities_by_domain(domain_name)


def get_entities(type_filter: Optional[str] = None) -> list[dict[str, Any]]:
    """All entities, optionally filtered by type."""
    return get_client().get_entities(type_filter=type_filter)


def get_triplets(
    subject: Optional[str] = None,
    relation: Optional[str] = None,
    obj: Optional[str] = None,
    video_id: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Filterable triplets (Subject -[Relation]-> Object)."""
    return get_client().get_triplets(
        subject=subject, relation=relation, obj=obj, video_id=video_id
    )
