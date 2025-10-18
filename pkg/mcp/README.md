# Prometheus-Powered MCP AI Observability Agent

This project implements a **Model Context Protocol (MCP)** that provides intelligent, real-time observability over Kubernetes clusters using **Prometheus metrics** and **LLM-based reasoning**.  

It exposes monitoring tools (like CPU usage, pod anomalies, and disk pressure) as callable APIs that an **AI assistant** or **chatbot** can query using natural language.

---

## 🚀 Features

- 🌐 Supports **multiple Prometheus instances** (multi-cluster setup)
- 🤖 Integrated with **Ollama LLMs** (e.g., `qwen2.5-coder:14b`)
- ⚙️ Built on **FastMCP** for tool registration and invocation
- 📊 Provides tools for:
  - Pod and node metric summaries
  - CrashLoop detection
  - Disk pressure alerts
  - CPU/memory anomaly detection
  - Correlated metric analysis
  - Event timelines and trend detection
- 🧩 Ready for integration with any monitoring chatbot

---

## ⚙️ Prerequisites

You’ll need the following installed:

- **Python 3.9+**
- **Minikube** (for running Kubernetes clusters)
- **Prometheus** (deployed on each cluster)
- **Ollama** (for local LLM inference)
- **FastMCP** Python package

---

## 🧰 Configuration

Edit `config/{}_config.yaml` as follows:

```yaml
# Server Config
mcp_server_url: "http://localhost:8001/mcp"


# LLM Configuration
ollama_url: "http://localhost:11434"
ollama_model: "qwen2.5-coder:14b"

# Prometheus Instances
prometheus_instances:
  - name: prometheus_1
    base_url: "http://localhost:9090"
    headers: {}
    disable_ssl: false

  - name: prometheus_2
    base_url: "http://localhost:9091"
    headers: {}
    disable_ssl: false
```

##  Setting Up Prometheus on Two Minikube Clusters

You can simulate a multi-cluster environment using two Minikube clusters:

```yaml
# Create two clusters
minikube start -p minikube1
minikube start -p minikube2

Enable Prometheus in both clusters:

kubectl create namespace monitoring
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml

Forward ports locally:

# Cluster 1
kubectl --context=minikube1 -n monitoring port-forward svc/prometheus-operated 9090:9090

# Cluster 2
kubectl --context=minikube2 -n monitoring port-forward svc/prometheus-operated 9091:9090
```

Prometheus instances are now accessible at:

    http://localhost:9090 (Cluster 1)

    http://localhost:9091 (Cluster 2)

## 🚀 Running the MCP Server

Start the MCP server: 

```bash
fastmcp run server.py:app --transport http --port 8001
```

Run the client

```bash
python3 client_dynamic.py
```

## 🧪 Running Tests

Validate all MCP tools using the provided integration test suite:

```bash
pytest -v test_mcp_tools.py
```

This test suite:

Iterates through all MCP tools

Calls each tool via the MCP API

Verifies each tool returns a valid JSON response