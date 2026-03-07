from __future__ import annotations

from monitoring.controller_exporter import apply_status


def test_apply_status_accepts_controller_payload() -> None:
    status = {
        'active_flows': 2,
        'weights': {'srv1': 0.6, 'srv2': 0.4},
        'backends': [
            {
                'name': 'srv1',
                'healthy': True,
                'connection_util': 0.05,
                'metrics': {
                    'cpu_util': 0.2,
                    'mem_util': 0.3,
                    'bw_util': 0.1,
                    'active_connections': 10,
                    'latency_ms': 25,
                    'throughput_mbps': 100,
                },
            },
            {
                'name': 'srv2',
                'healthy': False,
                'connection_util': 0.0,
                'metrics': {
                    'cpu_util': 0.0,
                    'mem_util': 0.0,
                    'bw_util': 0.0,
                    'active_connections': 0,
                    'latency_ms': 0,
                    'throughput_mbps': 0,
                },
            },
        ],
    }
    apply_status(status)
