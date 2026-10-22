"""Fixture keys for the record/replay cache.

The same logical request always maps to the same fixture file, so replay mode is deterministic.
Key = sha256(service, operation, normalized query, normalized body). Headers never take part:
they carry auth and per-request IDs, not meaning.

Request bodies should be built from seeded or otherwise deterministic values. When a field is
unavoidably volatile (a timestamp, a generated invoice_id), the client names it in
`ignore_fields` so it doesn't change the key.
"""

import hashlib
import json
import re
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass
from pathlib import PurePosixPath
from urllib.parse import parse_qsl

from pydantic import JsonValue

# Names that can carry credentials (Gemini's ?key=, OAuth form fields). Dropped from queries and
# form bodies so a credential never influences, or appears in, a fixture.
SECRET_PARAMS = frozenset({"key", "api_key", "apikey", "access_token", "client_secret"})

DIGEST_LENGTH = 16
_SLUG_MAX = 60

QueryParams = Mapping[str, str] | Sequence[tuple[str, str]]


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


def normalize_query(params: QueryParams) -> list[tuple[str, str]]:
    """Sorted pairs; repeated parameters are kept, credential-bearing ones dropped."""
    pairs = params.items() if isinstance(params, Mapping) else params
    return sorted((k, v) for k, v in pairs if k.lower() not in SECRET_PARAMS)


def normalize_body(content: bytes) -> JsonValue:
    """JSON bodies compare by meaning (key order ignored); anything else as sorted form pairs."""
    if not content:
        return None
    text = content.decode("utf-8", errors="replace")
    try:
        parsed: JsonValue = json.loads(text)
    except json.JSONDecodeError:
        pairs = normalize_query(parse_qsl(text, keep_blank_values=True))
        return [[k, v] for k, v in pairs]
    return parsed


def drop_fields(value: JsonValue, names: Collection[str]) -> JsonValue:
    """Remove the named keys at any depth."""
    if isinstance(value, dict):
        return {k: drop_fields(v, names) for k, v in value.items() if k not in names}
    if isinstance(value, list):
        return [drop_fields(item, names) for item in value]
    return value


def fixture_key(
    service: str,
    operation: str,
    *,
    query: QueryParams | None = None,
    body: JsonValue = None,
    ignore_fields: Collection[str] = (),
) -> FixtureKey:
    """Build the key for one request. Non-HTTP clients (embeddings) pass their own operation."""
    payload: JsonValue = {
        "service": service,
        "operation": operation,
        "query": [list(pair) for pair in normalize_query(query or {})],
        "body": drop_fields(body, ignore_fields) if ignore_fields else body,
    }
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return FixtureKey(service=service, operation=operation, digest=digest[:DIGEST_LENGTH])


def _slug(operation: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", operation).strip("_")[:_SLUG_MAX]
