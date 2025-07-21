from typing import TypedDict, List, Optional

class TradeExtract(TypedDict):
    TradeID: str
    Notional: float
    Currency: str
    Counterparty: str

class Acknowledgment(TypedDict):
    TradeID: str
    Status: str

class ErrorDetail(TypedDict):
    line: int
    error: str

class TransformFailure(TypedDict):
    file_name: str
    errors: List[ErrorDetail]

class ReconciliationError(TypedDict):
    TradeID: str
    Issue: str

class ReconciliationSummary(TypedDict):
    total_trades: int
    acknowledged_trades: int
    unacknowledged_trades: List[TradeExtract]
    errors: List[TransformFailure]
    reconciliation_issues: List[ReconciliationError]