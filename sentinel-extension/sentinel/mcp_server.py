import asyncio
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
import mcp.types as types
from .engine import SentinelEngine

# Initialize the Sentinel Engine
engine = SentinelEngine()

server = Server("security-sentinel")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available security tools."""
    return [
        types.Tool(
            name="sentinel_scan",
            description="Scan a file or directory for secrets",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to scan (defaults to project root)"},
                },
            },
        ),
        types.Tool(
            name="sentinel_status",
            description="Get a summary of new secrets detected",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls from the agent."""
    if name == "sentinel_scan":
        path = (arguments or {}).get("path")
        findings = engine.scan(path=path)
        return [types.TextContent(type="text", text=str(findings))]
    
    elif name == "sentinel_status":
        findings = engine.scan()
        new_count = findings["summary"]["new_secrets_count"]
        if new_count == 0:
            return [types.TextContent(type="text", text="✅ No new secrets detected.")]
        else:
            return [types.TextContent(type="text", text=f"🚨 Found {new_count} new secret(s)!\n{findings['results']}")]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    # Run the server using stdin/stdout streams
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="security-sentinel",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
