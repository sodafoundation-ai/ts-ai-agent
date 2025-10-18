# host.py
import asyncio
import json
import httpx
from fastmcp import Client
import re

client = Client("http://localhost:8001/mcp")


OLLAMA_API_URL = "http://localhost:11434"
MODEL_NAME = "qwen2.5-coder:14b"  # replace with your model


import httpx

async def ask_ollama_stream(prompt: str):
    """
    Async generator that yields only the text content from Ollama streaming.
    """
    async with httpx.AsyncClient(timeout=None) as session:
        async with session.stream(
            "POST",
            f"{OLLAMA_API_URL}/v1/completions",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "max_tokens": 1000,
                "temperature": 0.0,
                "stream": True
            },
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunk = line[6:]
                    if chunk != "[DONE]":
                        try:
                            data = json.loads(chunk)
                            text = data.get("choices", [{}])[0].get("text", "")
                            if text:
                                yield text
                        except json.JSONDecodeError:
                            continue


async def ask_ollama(prompt: str) -> str:
    """Send prompt to Ollama LLM and return completion"""
    async with httpx.AsyncClient(timeout=300.0) as session:  # <- increased timeout
        resp = await session.post(
            f"{OLLAMA_API_URL}/v1/completions",
            json={
                "model": "qwen2.5-coder:14b",
                "prompt": prompt,
                "max_tokens": 1000,
                "temperature": 0.0
            }
        )
        resp.raise_for_status()
        
        data = resp.json()
        
        return data["choices"][0]["text"]
    


async def llm_to_tool_call(nl_query: str) -> dict:
    
    prompt = (
        "You are an assistant that converts natural language queries into MCP tool calls. "
        "Respond ONLY in JSON format with keys 'tool_name' and 'params'.\n Available Tools - list_prometheus_metrics(), current_cpu_for_pods(metric_name: str = 'container_cpu_usage_seconds_total', pods: Optional[List[str]] = None),  top_n_pods_by_cpu(metric_name: str = 'container_cpu_usage_seconds_total', top_n: int = 2, window: str = '5m')\n"
        f"NL query: {nl_query}"
    )
    llm_response = await ask_ollama(prompt)
    llm_response = re.sub(r"```(?:json)?", "", llm_response.strip())
    try:
        return json.loads(llm_response)
        print("Json Call Loaded")
    except json.JSONDecodeError:
        return {"tool_name": nl_query.strip(), "params": {}}


async def run_query(nl_query: str):
    
    tool_call = await llm_to_tool_call(nl_query)
    tool_name = tool_call.get("tool_name")
    print("Tool Name:", tool_name)
    params = tool_call.get("params", {})

    # 2. Call MCP tool
    async with client:
        try:
            result = await client.call_tool(tool_name, params)
        except Exception as e:
            return {"error": f"Tool call failed: {e}"}

    
    summary_prompt = "Infer from the output, and give the final result with neat and minimal formatting to the user. remove unwanted spaces and characters."
    full_summary = ""
    async for chunk in ask_ollama_stream(summary_prompt):
        print(chunk, end="", flush=True)  # live summary
        full_summary += chunk
    print("\n")
    return full_summary, result


if __name__ == "__main__":

    context = ""

    while True:
        print("Current Context:", context)

        query = str(input("\n\nEnter your query: "))
        print("\n")

        if(query == "exit"):
            break

    
        summary, result = asyncio.run(run_query(context + query))
        
