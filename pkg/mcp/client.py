import asyncio
from fastmcp import Client


client = Client("http://localhost:8001/mcp")

async def call_tool(tool_name: str, **params):
    async with client:
        result = await client.call_tool(tool_name, params)
        print(f"Tool '{tool_name}' result:", result)
        return result


async def main():
   
    await call_tool("list_prometheus_metrics")
    
    await call_tool("get_metrics_summary",
                   prometheus_query="up")

if __name__ == "__main__":
    asyncio.run(main())
