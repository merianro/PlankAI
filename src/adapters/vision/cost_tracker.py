"""API cost tracking — log token usage and costs per request."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# Pricing per 1M tokens (gpt-5.6-luna standard)
MODEL_PRICING: dict[str, dict[str, float]] = {
    "gpt-5.6-luna": {"input": 0.20, "output": 1.20},
    "gpt-5.6-terra": {"input": 2.00, "output": 12.00},
    "gpt-5.6-sol": {"input": 4.00, "output": 20.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
}


@dataclass
class UsageRecord:
    """Single API call usage record."""

    timestamp: str
    model: str
    operation: str
    input_tokens: int
    output_tokens: int
    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float
    duration_ms: int
    image_size_bytes: int = 0


@dataclass
class CostTracker:
    """Track API costs across a session."""

    model: str
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_usd: float = 0.0
    request_count: int = 0
    records: list[UsageRecord] = field(default_factory=list)

    def record_request(
        self,
        operation: str,
        input_tokens: int,
        output_tokens: int,
        duration_ms: int,
        image_size_bytes: int = 0,
    ) -> UsageRecord:
        """Record a single API request and return the usage record."""
        pricing = MODEL_PRICING.get(self.model, {"input": 0.20, "output": 1.20})
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost_usd += total_cost
        self.request_count += 1

        record = UsageRecord(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            model=self.model,
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost_usd=round(input_cost, 6),
            output_cost_usd=round(output_cost, 6),
            total_cost_usd=round(total_cost, 6),
            duration_ms=duration_ms,
            image_size_bytes=image_size_bytes,
        )
        self.records.append(record)

        logger.info(
            "API request completed",
            extra={
                "model": self.model,
                "operation": operation,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": round(total_cost, 6),
                "duration_ms": duration_ms,
            },
        )

        return record

    def summary(self) -> str:
        """Return a human-readable cost summary."""
        return (
            f"API Usage Summary ({self.model})\n"
            f"  Requests:       {self.request_count}\n"
            f"  Input tokens:   {self.total_input_tokens:,}\n"
            f"  Output tokens:  {self.total_output_tokens:,}\n"
            f"  Total cost:     ${self.total_cost_usd:.4f} USD"
        )

    def save_log(self, path: str = "data/api_usage.jsonl") -> None:
        """Append usage records to a JSONL log file."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as f:
            for record in self.records:
                f.write(json.dumps(record.__dict__) + "\n")
        self.records.clear()
