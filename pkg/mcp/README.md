# Time Series MCP Server

This MCP (Model Context Protocol) server provides tools for processing time series data from multiple databases including Prometheus and InfluxDB. It includes data aggregation, joining, and anomaly detection capabilities.

## Features

- **Multi-database support**: Query both Prometheus and InfluxDB
- **Data aggregation**: Join and aggregate time series data from multiple sources
- **Anomaly detection**: Detect anomalies using statistical methods (Z-score, IQR)
- **Flexible querying**: Support for both instant and range queries
- **Statistical analysis**: Calculate metrics and summaries

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your databases by editing the config files:
   - `config/prometheus_config.yaml` - Prometheus connection settings
   - `config/influxdb_config.yaml` - InfluxDB connection settings

## Usage

### Starting the Server

```bash
python pkg/mcp/server.py
```

The server will run on `ws://localhost:8000` by default.

### Using the Client

```python
import asyncio
from pkg.mcp.client import TimeSeriesClient

async def main():
    async with TimeSeriesClient() as client:
        # Query Prometheus
        result = await client.query_prometheus("up", start_time="1h")
        print(result)
        
        # Aggregate data from both sources
        agg_result = await client.aggregate_time_series(
            prometheus_query="cpu_usage",
            influxdb_query='from(bucket: "metrics") |> range(start: -1h)',
            join_type="outer",
            aggregation_freq="5m"
        )
        print(agg_result)

asyncio.run(main())
```

## Available Tools

### Database Query Tools

- `query_prometheus(query, start_time, end_time, step)` - Query Prometheus with PromQL
- `query_influxdb(query, bucket, org)` - Query InfluxDB with Flux
- `list_prometheus_metrics()` - List available Prometheus metrics
- `list_influxdb_measurements(bucket)` - List available InfluxDB measurements

### Data Processing Tools

- `aggregate_time_series(...)` - Aggregate and join data from multiple sources
- `detect_anomalies(...)` - Detect anomalies in time series data
- `get_metrics_summary(...)` - Get statistical summary of metrics

### Aggregation Options

- **Join types**: `inner`, `outer`, `left`, `right`, `asof`
- **Aggregation functions**: `mean`, `sum`, `max`, `min`, `count`
- **Time frequencies**: `1s`, `1m`, `5m`, `1h`, `1d`, etc.
- **Anomaly detection methods**: `zscore`, `iqr`

## Configuration

### Prometheus Config (`config/prometheus_config.yaml`)

```yaml
base_url: "http://localhost:9090"
headers: {}
disable_ssl: false
```

### InfluxDB Config (`config/influxdb_config.yaml`)

```yaml
url: "http://localhost:8086"
token: "your-influxdb-token"
org: "your-org"
bucket: "your-bucket"
```

## Architecture

- **server.py**: Main MCP server with tool endpoints
- **aggregator.py**: Data processing and aggregation logic
- **client.py**: Client wrapper for easy interaction
- **config/**: Configuration files for database connections

## Error Handling

All tools return error information in the response if something goes wrong:

```json
{
  "error": "Description of the error"
}
```

## Examples

### Basic Prometheus Query

```python
result = await client.query_prometheus("up", start_time="1h")
```

### Cross-Database Aggregation

```python
result = await client.aggregate_time_series(
    prometheus_query="cpu_usage_percent",
    influxdb_query='from(bucket: "system") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "memory")',
    join_type="outer",
    time_tolerance="30s",
    aggregation_freq="5m",
    agg_function="mean"
)
```

### Anomaly Detection

```python
anomalies = await client.detect_anomalies(
    prometheus_query="response_time_seconds",
    method="zscore",
    threshold=2.5
)
```
