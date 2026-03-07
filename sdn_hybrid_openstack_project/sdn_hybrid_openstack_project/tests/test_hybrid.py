from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from sdn_hybrid_lb.algorithms.hybrid import HybridLoadBalancer
from sdn_hybrid_lb.utils.config import load_config


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'vm-a1-controller' / 'config.controller.yaml'


def build_lb() -> HybridLoadBalancer:
    return HybridLoadBalancer(load_config(str(CONFIG)))


def test_existing_flow_is_sticky() -> None:
    lb = build_lb()
    flow = ('10.0.0.1', 12345, 8000, 6)
    first = lb.choose_backend(flow)
    second = lb.choose_backend(flow)
    assert first is not None
    assert second is not None
    assert first.name == second.name


def test_connection_capacity_prevents_false_overload() -> None:
    lb = build_lb()
    b = lb.backends[0]
    b.capacity = replace(b.capacity, max_connections=200)
    b.metrics.active_connections = 1
    assert b.connection_util() < 0.90
    assert lb._is_eligible(b) is True


def test_ga_weights_sum_to_one() -> None:
    lb = build_lb()
    for idx, backend in enumerate(lb.backends):
        backend.metrics.cpu_util = 0.2 + idx * 0.1
        backend.metrics.mem_util = 0.1 + idx * 0.1
        backend.metrics.bw_util = 0.05 + idx * 0.05
        backend.metrics.latency_ms = 20 + idx * 10
        backend.metrics.active_connections = idx * 3
    weights = lb.force_ga()
    assert abs(sum(weights.values()) - 1.0) < 1e-6
    assert set(weights) == {b.name for b in lb.backends}
