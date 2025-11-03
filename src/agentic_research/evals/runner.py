from __future__ import annotations
import time, statistics
from typing import Callable, Dict, Any, List

def timed(fn: Callable[..., Any]) -> tuple[Any, float]:
    t0 = time.perf_counter()
    out = fn()
    dt = time.perf_counter() - t0
    return out, dt

def simple_eval(runs: List[float]) -> dict:
    return {
        "count": len(runs),
        "mean_s": statistics.mean(runs) if runs else 0.0,
        "p95_s": statistics.quantiles(runs, n=20)[-1] if len(runs) >= 20 else max(runs) if runs else 0.0
    }
