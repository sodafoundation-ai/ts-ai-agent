# my_client.py - Simple Time Series MCP Client
import asyncio
from fastmcp import Client

# Connect to your Time Series MCP server
client = Client("http://localhost:8001/mcp")

async def call_tool(tool_name: str, **params):
    """Call any tool on the Time Series MCP server"""
    async with client:
        result = await client.call_tool(tool_name, params)
        print(f"Tool '{tool_name}' result:", result)
        return result

# Example calls to your Time Series server
async def main():
    
    # Call 1: List Prometheus metrics
    await call_tool("list_prometheus_metrics")
    
    # Call 5: Get metrics summary
    await call_tool("get_metrics_summary",
                   prometheus_query="up")

if __name__ == "__main__":
    asyncio.run(main())
