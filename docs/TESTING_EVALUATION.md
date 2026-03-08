# Testing and Evaluation

Prometheus is optional. Even without it, the controller already exposes flow count and bandwidth-derived metrics using OpenFlow port statistics. Prometheus adds CPU and memory utilization per backend when you map exporter instances in `config.controller.yaml`.
