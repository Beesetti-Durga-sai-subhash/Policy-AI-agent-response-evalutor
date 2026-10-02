from __future__ import annotations

from datetime import date

from .loader import CALLERS


def eligible_chunk_ids(recording: dict, corpus: dict[str, dict]) -> set[str] | None:
    request = recording["request"]
    identity = CALLERS.get(request.get("caller_id"))
    if identity is None:
        return None

    try:
        as_of = date.fromisoformat(request["as_of"])
    except (KeyError, TypeError, ValueError):
        return None

    return {
        chunk_id
        for chunk_id, passage in corpus.items()
        if passage["state"] == "Approved"
        and passage["tenant"] == identity["tenant"]
        and passage["role"] == identity["role"]
        and date.fromisoformat(passage["effective_from"])
        <= as_of
        < date.fromisoformat(passage["effective_to"])
    }
