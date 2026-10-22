"""Fixture keys for the record/replay cache.

The same logical request always maps to the same fixture file, so replay mode is deterministic.
Key = sha256(service, operation, normalized query, normalized body). Headers never take part:
they carry auth and per-request IDs, not meaning.
"""

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import PurePosixPath
from urllib.parse import parse_qsl

from pydantic import JsonValue

# Query parameters that can carry credentials (e.g. Gemini's ?key=). Dropped so a key never
# influences, or appears in, a fixture.
SECRET_QUERY_PARAMS = frozenset({"key", "api_key", "apikey", "access_token", "client_secret"})

DIGEST_LENGTH = 16
_SLUG_MAX = 60


@dataclass(frozen=True)
class FixtureKey:
    service: str
    operation: str
    digest: str

    @property
    def relative_path(self) -> PurePosixPath:
        """Readable on disk, e.g. paypal/POST_v2_checkout_orders__3f9a….json."""
        return PurePosixPath(self.service) / f"{_slug(self.operation)}__{self.digest}.json"


def http_operation(method: str, path: str) -> str:
    return f"{method.upper()} {path}"


def canonical_json(value: JsonValue) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def normalize_query(params: Mapping[str, str]) -> list[tuple[str, str]]:
    return sorted((k, v) for k, v in params.items() if k.lower() not in SECRET_QUERY_PARAMS)


def normalize_body(content: bytes) -> JsonValue:
    """JSON bodies compare by meaning (key order ignored); anything else as sorted form pairs."""
    if not content:
        return None
    text = content.decode("utf-8", errors="replace")
    try:
        parsed: JsonValue = json.loads(text)
    except json.JSONDecodeError:
        return [[k, v] for k, v in sorted(parse_qsl(text, keep_blank_values=True))]
    return parsed


def fixture_key(
    service: str,
    operation: str,
    *,
    query: Mapping[str, str] | None = None,
    body: JsonValue = None,
) -> FixtureKey:
    """Build the key for one request. Non-HTTP clients (embeddings) pass their own operation."""
    payload: JsonValue = {
        "service": service,
        "operation": operation,
        "query": [list(pair) for pair in normalize_query(query or {})],
        "body": body,
    }
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return FixtureKey(service=service, operation=operation, digest=digest[:DIGEST_LENGTH])


def _slug(operation: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", operation).strip("_")[:_SLUG_MAX]
