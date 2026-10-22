import re

from app.cache.keys import fixture_key, http_operation, normalize_body, normalize_query

ORDERS = http_operation("post", "/v2/checkout/orders")


def test_same_request_gives_same_key() -> None:
    body = normalize_body(b'{"intent": "CAPTURE", "amount": 11900}')
    assert fixture_key("paypal", ORDERS, body=body) == fixture_key("paypal", ORDERS, body=body)


def test_json_key_order_does_not_matter() -> None:
    first = normalize_body(b'{"a": 1, "b": {"c": 2, "d": 3}}')
    second = normalize_body(b'{"b": {"d": 3, "c": 2}, "a": 1}')
    assert fixture_key("paypal", ORDERS, body=first) == fixture_key("paypal", ORDERS, body=second)


def test_different_body_gives_different_key() -> None:
    first = fixture_key("paypal", ORDERS, body={"amount": 11900})
    second = fixture_key("paypal", ORDERS, body={"amount": 12000})
    assert first.digest != second.digest


def test_service_and_operation_separate_keys() -> None:
    base = fixture_key("paypal", ORDERS)
    assert fixture_key("channel3", ORDERS).digest != base.digest
    assert fixture_key("paypal", http_operation("GET", "/v2/checkout/orders")).digest != base.digest


def test_secret_query_params_are_ignored() -> None:
    with_key = fixture_key("llm", "POST /generate", query={"key": "secret", "alt": "json"})
    without_key = fixture_key("llm", "POST /generate", query={"alt": "json"})
    assert with_key == without_key
    assert normalize_query({"api_key": "secret", "q": "boots"}) == [("q", "boots")]


def test_repeated_query_params_are_kept() -> None:
    one = fixture_key("channel3", "GET /v1/search", query=[("tag", "boots")])
    two = fixture_key("channel3", "GET /v1/search", query=[("tag", "boots"), ("tag", "wide")])
    assert one != two


def test_volatile_body_fields_can_be_ignored() -> None:
    first = {"purchase_units": [{"amount": 11900, "invoice_id": "inv-1730000000"}]}
    second = {"purchase_units": [{"amount": 11900, "invoice_id": "inv-1730000999"}]}
    assert fixture_key("paypal", ORDERS, body=first) != fixture_key("paypal", ORDERS, body=second)
    assert fixture_key("paypal", ORDERS, body=first, ignore_fields={"invoice_id"}) == fixture_key(
        "paypal", ORDERS, body=second, ignore_fields={"invoice_id"}
    )


def test_secrets_in_form_bodies_do_not_affect_the_key() -> None:
    assert normalize_body(b"grant_type=client_credentials&client_secret=abc") == [
        ["grant_type", "client_credentials"]
    ]


def test_query_order_does_not_matter() -> None:
    first = fixture_key("channel3", "GET /v1/search", query={"q": "boots", "limit": "10"})
    second = fixture_key("channel3", "GET /v1/search", query={"limit": "10", "q": "boots"})
    assert first == second


def test_form_bodies_normalize_to_sorted_pairs() -> None:
    assert normalize_body(b"scope=x&grant_type=client_credentials") == [
        ["grant_type", "client_credentials"],
        ["scope", "x"],
    ]


def test_empty_body_is_none() -> None:
    assert normalize_body(b"") is None


def test_embeddings_use_the_same_scheme() -> None:
    key = fixture_key("embeddings", "embed:bge-small-en-v1.5", body=["waterproof boots"])
    assert key.relative_path.parent.name == "embeddings"


def test_fixture_path_is_readable() -> None:
    path = str(fixture_key("paypal", ORDERS).relative_path)
    assert re.fullmatch(r"paypal/POST_v2_checkout_orders__[0-9a-f]{16}\.json", path)
