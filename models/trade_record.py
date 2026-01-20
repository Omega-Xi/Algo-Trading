from dataclasses import dataclass,field
from typing import Optional
from datetime import datetime

@dataclass
class Trade:
    trade_id: int = field(init=False)
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

    _id_counter: int = 0

    def __post_init__(self):
        type(self)._id_counter += 1
        self.trade_id = type(self)._id_counter
