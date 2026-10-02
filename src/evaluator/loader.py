from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


CALLERS = {
    "atlas-employee-01": {"tenant": "Atlas", "role": "employee"},
    "atlas-contractor-01": {"tenant": "Atlas", "role": "contractor"},
    "boreal-employee-01": {"tenant": "Boreal", "role": "employee"},
}


class InputError(ValueError):
    pass


def read_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError(f"Cannot load {path}: {exc}") from exc


def load_pack(data_dir: Path) -> tuple[dict[str, dict], list[dict], dict]:
    corpus_rows = read_json(data_dir / "corpus.json")
    recording_data = read_json(data_dir / "recordings.json")
    expected_data = read_json(data_dir / "expected_results.json")

    corpus = {row["chunk_id"]: row for row in corpus_rows}
    if len(corpus) != len(corpus_rows):
        raise InputError("Corpus contains duplicate chunk_id values")

    expected_by_id = expected_data.get("recordings", {})
    recordings = [
        expand_recording(item, recording_data["defaults"], corpus)
        for item in recording_data["recordings"]
    ]
    recording_ids = {item["recording_id"] for item in recordings}
    if recording_ids != set(expected_by_id):
        raise InputError("Recording IDs and expected-result IDs do not match")

    return corpus, recordings, expected_data


def expand_recording(raw: dict, defaults: dict, corpus: dict[str, dict]) -> dict:
    recording = {
        "recording_id": raw["recording_id"],
        "request": copy.deepcopy(defaults["request"]),
        "observed": copy.deepcopy(raw["observed"]),
        "trace": copy.deepcopy(defaults["trace"]),
    }
    recording["request"].update(raw.get("request_overrides", {}))
    recording["trace"].update(raw.get("trace_overrides", {}))

    body = recording["observed"].get("body", {})
    for citation in body.get("citations", []):
        if citation.pop("quote_from_corpus", False):
            chunk_id = citation.get("chunk_id")
            if chunk_id not in corpus:
                raise InputError(
                    f"Recording {recording['recording_id']} cites unknown {chunk_id}"
                )
            citation["quote"] = corpus[chunk_id]["text"]
    return recording
