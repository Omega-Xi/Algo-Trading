from dataclasses import dataclass,field
from typing import Optional
from datetime import datetime

@dataclass
class Trade:
    trade_id: int
    instrument: str
    type: str
    entry_time: datetime
    entry_price: float
    quantity: int
    trigger_price: float
    target_price: float
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    pnl: float = 0.0
    status: str = "ACTIVE"
    exit_reason: Optional[str] = None
    gross_pnl: float = 0.0
    net_pnl: float = 0.0
    charges: float = 0.0