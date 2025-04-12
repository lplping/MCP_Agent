""""
输出工具结果
"""
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ping
# datetime:2025/4/8 10:40
import json
from pydantic import BaseModel
from typing import Optional
from contextlib import AsyncExitStack
import logging
from mcp import ClientSession
from mcp.client.sse import sse_client
logger=logging.getLogger("client_log.log")

from fastapi import FastAPI, HTTPException


# Define FastAPI app
app = FastAPI()



class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self._session_context = None
        self._streams_context = None

    async def connect_to_sse_server(self, server_url: str):
        """Connect to an MCP server running with SSE transport"""
        self._streams_context = sse_client(url=server_url)
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session: ClientSession = await self._session_context.__aenter__()

        # Initialize
        await self.session.initialize()

        # List available tools to verify connection
        logger.info("初始化 SSE 客户端...")
        response = await self.session.list_tools()
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in response.tools]
        print("available_tools",available_tools)
        tools = response.tools
        logger.info("\n已连接到服务器，支持以下工具: {}".format([tool.name for tool in tools]))

    async def cleanup(self):
        """Properly clean up the session and streams"""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)


    async def call_tools(self, tool_name: str,tool_args) -> str:
        """Process a query using OpenAI API and available tools"""
        if self.session is None:
            raise HTTPException(status_code=500, detail="Session not initialized.")
        print("tool_name",tool_name)
        print("tool_args", tool_args)

        tool_args = json.loads(tool_args)


        # Execute tool call
        result = await self.session.call_tool(tool_name, tool_args)
        content = result.content[0].text

        logger.info(f"调用工具: {tool_name}")
        logger.info(f"工具参数: {tool_args}")
        logger.info(f"工具执行结果: {content}")

        return content

class ToolCallRequest(BaseModel):
    tool_name: str
    tool_args: str  # 注意是字符串格式的 JSON

# Create an instance of the client
client = MCPClient()


@app.on_event("startup")
async def startup():
    # Initialize the connection when the app starts
    server_url = "http://0.0.0.0:18376/sse"  # Change to your server URL
    try:
        await client.connect_to_sse_server(server_url)
    except Exception as e:
        logger.error(f"Error connecting to server: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to SSE server.")


@app.post("/call_tools/")
async def call_tools(request: ToolCallRequest):
    result = await client.call_tools(request.tool_name, request.tool_args)
    return {"result": result}
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=18475)

