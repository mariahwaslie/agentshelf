"""Enumerations used across the contracts. Values are what the browser sees."""

from enum import StrEnum


class AppMode(StrEnum):
    LIVE = "live"
    REPLAY = "replay"


class Service(StrEnum):
    PAYPAL = "paypal"
    CHANNEL3 = "channel3"
    LLM = "llm"
    EMBEDDINGS = "embeddings"


class ServiceState(StrEnum):
    CONFIGURED = "configured"
    MISSING_KEYS = "missing_keys"
    REPLAY = "replay"
    LOCAL = "local"


class QuerySplit(StrEnum):
    TRAIN = "train"
    HELDOUT = "heldout"


class ItemOwner(StrEnum):
    MERCHANT = "merchant"
    COMPETITOR = "competitor"


class FixKind(StrEnum):
    MISSING_ATTRIBUTE = "missing_attribute"
    THIN_DESCRIPTION = "thin_description"
    PRICE_OUTLIER = "price_outlier"
    AVAILABILITY = "availability"


class SourceField(StrEnum):
    """Product text an enrichment proposal is allowed to cite."""

    TITLE = "title"
    DESCRIPTION = "description"
    NOTES = "notes"


class ProposalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalDecision(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"


class OrderStatus(StrEnum):
    """Mirrors PayPal Orders v2 order statuses."""

    CREATED = "CREATED"
    SAVED = "SAVED"
    APPROVED = "APPROVED"
    PAYER_ACTION_REQUIRED = "PAYER_ACTION_REQUIRED"
    VOIDED = "VOIDED"
    COMPLETED = "COMPLETED"


class CaptureStatus(StrEnum):
    """Mirrors PayPal capture statuses. An order can be COMPLETED while its capture is PENDING."""

    COMPLETED = "COMPLETED"
    PENDING = "PENDING"
    DECLINED = "DECLINED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"


class OrderSource(StrEnum):
    AGENT = "agent"


class Confirmation(StrEnum):
    """How a capture was confirmed: the webhook, or the order-status polling fallback."""

    WEBHOOK = "webhook"
    POLLING = "polling"


class CacheOutcome(StrEnum):
    HIT = "hit"
    MISS = "miss"
    RECORDED = "recorded"
    REPLAYED = "replayed"
    LIVE = "live"
