.PHONY: test controller dataplane dashboard exporter

test:
	python3 -m pytest

controller:
	cd vm-a1-controller && ./run_controller.sh

dataplane:
	cd vm-a2-dataplane && ./run_mininet.sh

dashboard:
	python3 -m dashboard.app

exporter:
	python3 monitoring/controller_exporter.py --controller-url http://127.0.0.1:8080 --listen-port 9108
