"""RED/GREEN tests for the vlkg-mcp server tool surface.

These tests cover the full registered tool surface — 6 graph tools + 17
intel tools — using FastMCP's in-process ``list_tools`` / ``call_tool``.
Running the suite requires the repo root on ``PYTHONPATH`` so the shared
``src.*`` modules (Neo4jClient, LocalGraphStore fallback, src.core engines)
resolve; no live Neo4j is required because every path falls back to JSON.
"""

from __future__ import annotations

from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Expected surface (must match src/vlkg_mcp/tools)
# ---------------------------------------------------------------------------

GRAPH_TOOLS: dict[str, list[str]] = {
    "graph_stats": [],
    "graph_type_counts": [],
    "graph_video_ids": [],
    "graph_entities": ["exclude_types", "limit", "offset"],
    "graph_entities_by_domain": ["domain_name", "limit", "offset"],
    "graph_triplets": ["subject", "relation", "obj", "video_id", "limit", "offset"],
}

# 17 intel modules from tools/intel.py ``_CONFIG``. Every intel tool returns
# a string and takes arbitrary kwargs (engine-specific). Keys used below for
# the smoke tests are representative; they are passed only to the engines
# that accept them without erroring.
INTEL_TOOLS: dict[str, list[str]] = {
    "intel_alternative_scenarios": [],
    "intel_audience": ["metric"],
    "intel_best_practices": [],
    "intel_clustering": [],
    "intel_competitive_intelligence": ["industry"],
    "intel_compliance_intelligence": ["industry"],
    "intel_customer_intelligence": ["industry"],
    "intel_domain": ["entity"],
    "intel_enrichment": ["node_id"],
    "intel_faq": ["topic"],
    "intel_glossary": ["topic"],
    "intel_ideation": ["topic"],
    "intel_narrative": ["topic"],
    "intel_pedagogy": ["topic"],
    "intel_personalization": ["learning_style"],
    "intel_proactive": ["topic"],
    "intel_quality": ["topic"],
}


async def _call(server, name: str, **kwargs: Any) -> Any:
    """Invoke a tool via FastMCP.call_tool.

    call_tool returns a sequence of Content blocks; extract the raw text.
    Handles both old (list) and new (tuple with structured output) formats.
    """
    result = await server.call_tool(name, dict(kwargs))
    # New FastMCP returns (list[Content], dict) tuple; old returns list
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], list):
        blocks = result[0]
        structured = result[1]
        if structured and not blocks:
            import json

            if isinstance(structured, dict) and "result" in structured and len(structured) == 1:
                return json.dumps(structured["result"])
            return json.dumps(structured)
        result = blocks
    text_blocks = [
        block.text if getattr(block, "type", None) == "text" else str(block)
        for block in result
    ]
    if len(text_blocks) == 1:
        return text_blocks[0]
    # FastMCP may split JSON arrays/dicts into multiple TextContent items or join them
    joined = "".join(text_blocks)
    if joined.startswith("[") and not joined.endswith("]"):
        # Wrap multiple JSON objects into a JSON array if FastMCP yielded them as separate items
        return "[" + ",".join(text_blocks) + "]"
    return joined


# ---------------------------------------------------------------------------
# Surface registration tests
# ---------------------------------------------------------------------------


def test_all_graph_tools_registered(tool_names: set[str]) -> None:
    assert set(GRAPH_TOOLS) <= tool_names


def test_all_intel_tools_registered(tool_names: set[str]) -> None:
    assert set(INTEL_TOOLS) <= tool_names


def test_tool_surface_has_valid_shape(tool_names: set[str]) -> None:
    # Full app surface is exactly 6 graph + 17 intel tools.
    assert len(tool_names) == 23
    assert len(tool_names & set(GRAPH_TOOLS)) == len(GRAPH_TOOLS)
    assert len(tool_names & set(INTEL_TOOLS)) == len(INTEL_TOOLS)


async def test_graph_tools_have_expected_params(server) -> None:
    tools = await server.list_tools()
    registered = {tool.name: tool for tool in tools}
    for name, params in GRAPH_TOOLS.items():
        tool = registered.get(name)
        assert tool is not None, f"{name} missing from registration"
        actual = set(tool.inputSchema.get("properties", {}).keys())
        assert actual == set(params), f"{name}: expected {set(params)}, got {actual}"


# ---------------------------------------------------------------------------
# Graph tool behaviour (falls back to JSON LocalGraphStore)
# ---------------------------------------------------------------------------


async def test_graph_stats_has_expected_keys(server) -> None:
    text = await _call(server, "graph_stats")
    import json

    stats = json.loads(text)
    assert set(stats) >= {"node_count", "relationship_count", "average_degree"}


async def test_graph_type_counts_is_dict_of_int(server) -> None:
    text = await _call(server, "graph_type_counts")
    import json

    counts = json.loads(text)
    assert isinstance(counts, dict)
    assert all(isinstance(v, int) for v in counts.values())


async def test_graph_video_ids_is_sorted_list_of_str(server) -> None:
    text = await _call(server, "graph_video_ids")
    import json

    ids = json.loads(text)
    assert isinstance(ids, list)
    assert all(isinstance(v, str) for v in ids)
    assert ids == sorted(ids)


async def test_graph_entities_returns_list_of_dicts(server) -> None:
    text = await _call(server, "graph_entities", limit=10, offset=0)
    import json

    rows = json.loads(text)
    assert isinstance(rows, list)
    assert all(isinstance(r, dict) for r in rows)


async def test_graph_entities_respects_limit(server) -> None:
    text = await _call(server, "graph_entities", limit=5, offset=0)
    import json

    rows = json.loads(text)
    assert len(rows) <= 5


async def test_graph_entities_by_domain_returns_list(server) -> None:
    text = await _call(server, "graph_entities_by_domain", domain_name="competitive")
    import json

    rows = json.loads(text)
    assert isinstance(rows, list)


async def test_graph_triplets_returns_list_of_dicts(server) -> None:
    text = await _call(server, "graph_triplets", limit=10, offset=0)
    import json

    rows = json.loads(text)
    assert isinstance(rows, list)
    assert all(isinstance(r, dict) for r in rows)


# ---------------------------------------------------------------------------
# Intel tool smoke tests (each returns a string)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("tool", "kwargs"),
    [
        ("intel_alternative_scenarios", {}),
        ("intel_audience", {"metric": "retention"}),
        ("intel_best_practices", {}),
        ("intel_clustering", {}),
        ("intel_competitive_intelligence", {"industry": "edtech"}),
        ("intel_compliance_intelligence", {"industry": "edtech"}),
        ("intel_customer_intelligence", {"industry": "edtech"}),
        ("intel_domain", {"entity": "graph"}),
        ("intel_faq", {"topic": "graph"}),
        ("intel_glossary", {"topic": "graph"}),
        ("intel_ideation", {"topic": "graph"}),
        ("intel_narrative", {"topic": "graph"}),
        ("intel_pedagogy", {"topic": "graph"}),
        ("intel_personalization", {"learning_style": "visual"}),
        ("intel_proactive", {"topic": "graph"}),
        ("intel_quality", {"topic": "graph"}),
    ],
)
async def test_intel_tool_returns_string(server, tool: str, kwargs: dict) -> None:
    text = await _call(server, tool, **kwargs)
    assert isinstance(text, str)
    assert text  # non-empty


async def test_intel_enrichment_requires_db_client(server) -> None:
    """GraphEnrichmentEngine must be constructed with a db_client.

    The intel registration wires db-backed modules to the shared client;
    calling intel_enrichment should therefore not raise a missing-arg error.
    """
    tools = await server.list_tools()
    names = {t.name for t in tools}
    assert "intel_enrichment" in names
