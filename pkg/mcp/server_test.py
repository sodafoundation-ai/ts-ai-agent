
import pytest
from fastmcp import Client


client = Client("http://localhost:8001/mcp")

example_pods = ["lowcpu-node-b7cb445d9-5pccv"]

# Define tools with parameters
tools = [
    ("current_metric_for_pods", {"pod_names": example_pods}),
    ("top_n_pods_by_metric", {"metric_name": "container_cpu_usage_seconds_total", "top_n": 5}),
    ("pod_network_io", {"pod_names": example_pods}),
    ("pods_exceeding_cpu", {"threshold": 0.8}),
    ("pod_status_summary", {}),
    ("recent_pod_events", {"limit": 10}),
    ("node_disk_usage", {}),
    ("describe_cluster_health", {}),
    ("top_disk_pressure_nodes", {"threshold": 80, "top_n": 5}),
    ("pod_restart_trend", {"window": "30m", "top_n": 5}),
    ("detect_pod_anomalies", {"metric_name": "container_cpu_usage_seconds_total", "z_threshold": 3.0}),
    ("namespace_resource_summary", {"resource": "cpu", "window": "5m"}),
    ("detect_crashloop_pods", {"window": "10m", "threshold": 2}),
    ("correlate_metrics", {"metric_a": "container_cpu_usage_seconds_total", "metric_b": "container_network_receive_bytes_total", "window": "10m"}),
    ("pod_event_timeline", {"pod_name": example_pods[0], "window": "30m"}),
    ("node_condition_summary", {})
]

@pytest.mark.asyncio
@pytest.mark.parametrize("tool_name,params", tools)
async def test_mcp_tools(tool_name, params):
    
    async with Client("http://localhost:8001/mcp") as client:
        result = await client.call_tool(tool_name, params)
        print(result.data)
        assert isinstance(result.data, dict), f"{tool_name} did not return a dict"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
