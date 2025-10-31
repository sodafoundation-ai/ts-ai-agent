# Prometheus Data Generator for Kubernetes Clusters
Prometheus High-Cardinality Data Generator for Kubernetes Clusters
This script generates and pushes high-cardinality time-series data to Prometheus
simulating multiple Kubernetes clusters with one year of historical data.

## Key feature
The script simulates multiple Kubernetes clusters with realistic high-cardinality metrics including CPU usage, memory consumption, network traffic, disk I/O, pod status, and node metrics. It uses the Prometheus Remote Write API protocol for efficient data transmission.​

## Prerequisite
1. The remote-write needs to enabled in prometheus. To enable the remote-write in prometheus instance make sure it is configured at run time using ```--web.enable-remote-write-receiver```
2. TSDB out of order time window: Prometheus consider only 1-2 hour maximum of out of order time series data. Since the range of data push in our case vary, increase the out of order time window to match days of history. Config parameter to be changed:
```yaml
storage:
  tsdb:
    out_of_order_time_window: 15d
```

## Installation
First, install the required dependency:

```bash
pip install prometheus-remote-writer
```

## Usage Options
Command-Line Arguments

``` bash
# Basic usage
python prometheus_data_pusher.py --url http://localhost:9090/api/v1/write
```

```bash
# With custom parameters
python prometheus_data_pusher.py \
    --url http://localhost:9090/api/v1/write \
    --clusters 10 \
    --days 365 \
    --batch-size 1000 \
    --scrape-interval 30
```

Run with config file:

```bash
python prometheus_data_pusher.py --config config.json
```

## Generated Metrics
The script generates 15+ metric types per container:​

##### Container Metrics:

```
container_cpu_usage_seconds_total - CPU usage tracking

container_cpu_cfs_throttled_seconds_total - CPU throttling events

container_memory_usage_bytes - Memory consumption

container_memory_working_set_bytes - Active memory

container_memory_cache - Cached memory

container_network_receive_bytes_total - Network ingress

container_network_transmit_bytes_total - Network egress

container_network_receive_errors_total - Network errors

container_fs_reads_bytes_total - Disk reads

container_fs_writes_bytes_total - Disk writes
```

#### Pod Metrics:

```
kube_pod_status_phase - Pod lifecycle status

kube_pod_container_status_restarts_total - Container restart count
```

#### Node Metrics:

```
kube_node_status_capacity_cpu_cores - Node CPU capacity

kube_node_status_capacity_memory_bytes - Node memory capacity

kube_node_status_condition - Node health status
```

#### High Cardinality Labels
Each metric includes multiple labels to simulate real-world high-cardinality scenarios:​

```
cluster - Cluster identifier (e.g., k8s-cluster-001)

namespace - Kubernetes namespace

pod - Unique pod name with random identifier

container - Container name

node - Node hostname

region - Cloud region (us-east-1, eu-west-1, etc.)

environment - Environment type (production, staging, development)

app - Application name

version - Application version (semantic versioning)

instance_type - Node instance type (t3.large, m5.xlarge, etc.)
```

Cardinality Estimation
With default configuration, the script generates approximately 13.5 million unique time series:

```
10 clusters × 50 nodes × 20 namespaces × 30 pods × 3 containers × 15 metrics = ~13,500,000 time series
```

## Quickstart
```bash
# Setup environment

python -m venv .venv
. .venv/bin/activate
pip install prometheus-remote-writer

# Running local prometheus server
docker volume create prometheus-data

--prometheus.yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

remote_write:
  - url: "http://localhost:9090/api/v1/write" # Replace with your actual remote write endpoint
    queue_config:
      max_samples_per_send: 100000
      capacity: 100000

storage:
  tsdb:
    out_of_order_time_window: 15d


docker run -d \
  --name prometheus-remote-write \
  -p 9090:9090 \
  -v prometheus-data:/prometheus \
  -v ./prometheus.yaml:/etc/prometheus/prometheus.yaml \
  --memory="4g" \
  --cpus="3" \
  prom/prometheus \
  --config.file=/etc/prometheus/prometheus.yaml \
  --web.enable-remote-write-receiver

python prometheus_data_pusher.py --config config.json
```
