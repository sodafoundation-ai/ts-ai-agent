# mcp_server.py
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import yaml
import os

from fastmcp import FastMCP
from prometheus_api_client import PrometheusConnect
from influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi

from aggregator import TimeSeriesAggregator

app = FastMCP("TimeSeriesServer")

# Global instances
prometheus_client = None
influxdb_client = None
aggregator = TimeSeriesAggregator()

def load_config():
    """Load configuration from YAML files"""
    config_dir = "/home/rohith/ts-ai-agent/config"
    
    # Load Prometheus config
    prom_config_path = os.path.join(config_dir, "prometheus_config.yaml")
    prom_config = {}
    if os.path.exists(prom_config_path):
        with open(prom_config_path, 'r') as f:
            prom_config = yaml.safe_load(f)
    
    # Load InfluxDB config
    influx_config_path = os.path.join(config_dir, "influxdb_config.yaml")
    influx_config = {
        "url": "http://localhost:8086",
        "token": None,
        "org": "default",
        "bucket": "default"
    }
    if os.path.exists(influx_config_path):
        with open(influx_config_path, 'r') as f:
            influx_config.update(yaml.safe_load(f))
    
    return prom_config, influx_config

def initialize_clients():
    global prometheus_client, influxdb_client
    
    prom_config, influx_config = load_config()
    
    # Initialize Prometheus client
    if prom_config.get('base_url'):
        try:
            prometheus_client = PrometheusConnect(
                url=prom_config['base_url'],
                headers=prom_config.get('headers', {}),
                disable_ssl=prom_config.get('disable_ssl', False)
            )
        except Exception as e:
            print(f"Failed to initialize Prometheus client: {e}")
    

    if influx_config.get('url'):
        try:
            influxdb_client = InfluxDBClient(
                url=influx_config['url'],
                token=influx_config.get('token'),
                org=influx_config.get('org', 'default')
            )
        except Exception as e:
            print(f"Failed to initialize InfluxDB client: {e}")

initialize_clients()

# -------------------
# Discovery Tools
# -------------------
@app.tool()
def list_prometheus_metrics() -> Dict[str, Any]:
    """List available Prometheus metrics"""
    if not prometheus_client:
        return {"error": "Prometheus client not initialized"}
    try:
        metrics = prometheus_client.all_metrics()
        return {"metrics": list(metrics), "count": len(metrics), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"error": str(e)}

@app.tool()
def list_label_values(metric_name: str, label_name: str) -> Dict[str, Any]:
    """Return all possible values for a given metric label"""
    if not prometheus_client:
        return {"error": "Prometheus client not initialized"}
    try:
        values = prometheus_client.get_label_values(label_name, metric_name=metric_name)
        return {"values": values, "count": len(values), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"error": str(e)}

# -------------------
# Basic Metric Queries
# -------------------
@app.tool()
def get_current_value(metric_name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Get latest value of a metric"""
    if not prometheus_client:
        return {"error": "Prometheus client not initialized"}
    try:
        result = prometheus_client.get_current_metric_value(metric_name, label_config=labels or {})
        return {"metric": metric_name, "value": result, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"error": str(e)}

@app.tool()
def avg_over_time(metric_name: str, window: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Return average value of a metric over a time window"""
    if not prometheus_client:
        return {"error": "Prometheus client not initialized"}
    try:
        # Precompute label string to avoid f-string backslash issues
        label_query = ",".join([f'{k}="{v}"' for k,v in (labels or {}).items()])
        label_query_str = f"{{{label_query}}}" if label_query else ""
        query = f"avg_over_time({metric_name}{label_query_str}[{window}])"
        result = prometheus_client.custom_query(query=query)
        return {"metric": metric_name, "avg_value": result, "window": window, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"error": str(e)}

# -------------------
# Comparative / Ranking Tools
# -------------------
@app.tool()
def top_n_instances(metric_name: str, n: int = 5, window: str = "5m") -> Dict[str, Any]:
    """Return top N instances by metric value over a window"""
    if not prometheus_client:
        return {"error": "Prometheus client not initialized"}
    try:
        query = f"topk({n}, avg_over_time({metric_name}[{window}]))"
        result = prometheus_client.custom_query(query=query)
        return {"metric": metric_name, "top_n": result, "window": window, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"error": str(e)}

# -------------------
# Anomaly Detection
# -------------------
@app.tool()
def detect_threshold_violation(metric_name: str, threshold: float, window: str = "5m", labels: Optional[Dict[str,str]] = None) -> Dict[str, Any]:
    """Detect instances where metric exceeds a threshold"""
    if not prometheus_client:
        return {"error": "Prometheus client not initialized"}
    try:
        label_query = ",".join([f'{k}="{v}"' for k,v in (labels or {}).items()])
        label_query_str = f"{{{label_query}}}" if label_query else ""
        query = f"avg_over_time({metric_name}{label_query_str}[{window}]) > {threshold}"
        result = prometheus_client.custom_query(query=query)
        return {"metric": metric_name, "violations": result, "threshold": threshold, "window": window, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"error": str(e)}

# -------------------
# Workflow Utility
# -------------------
@app.tool()
def top_n_then_avg(metric_name: str, n: int = 5, window: str = "5m") -> Dict[str, Any]:
    """Workflow: get top N instances by metric and then compute their average"""
    top_result = top_n_instances(metric_name, n=n, window=window)
    if "error" in top_result:
        return top_result
    
    try:
        # Extract values safely
        values = [float(i['value'][1]) for i in top_result.get("top_n", [])]
        avg_value = sum(values)/len(values) if values else 0.0
        return {"metric": metric_name, "top_n_avg": avg_value, "top_n_values": values, "window": window, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run()
