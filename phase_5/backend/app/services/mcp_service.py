"""
MCP Service (Integrated - Direct Tool Calls)

This service provides the same interface as the old HTTP client,
but calls MCP tools directly within the backend process.

Architecture (PDF Compliant):
    FastAPI Server
    └── Chat Endpoint
        └── AI Agent
            └── MCP Service (this) ──> MCP Tools ──> Database

Replaces: mcp_http_client.py (HTTP calls to port 8001)
"""

import logging
from typing import Dict, Any

from app.mcp_server import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
)

logger = logging.getLogger(__name__)


class MCPService:
    """
    MCP Service for direct tool invocation.

    Provides the same interface as MCPHTTPClient but calls
    tools directly without HTTP overhead.
    """

    def __init__(self):
        """Initialize MCP Service"""
        logger.info("🔧 MCP Service initialized (integrated mode)")

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool directly.

        Args:
            tool_name: Name of the MCP tool (add_task, list_tasks, etc.)
            arguments: Tool arguments

        Returns:
            Tool execution result as dictionary

        Raises:
            Exception: If tool execution fails
        """
        logger.info(f"📞 MCP Service calling tool: {tool_name}")

        try:
            # Route to appropriate tool
            if tool_name == "add_task":
                result = await add_task(
                    user_id=arguments.get("user_id"),
                    title=arguments.get("title"),
                    description=arguments.get("description"),
                    priority=arguments.get("priority"),
                    tags=arguments.get("tags"),
                    due_date=arguments.get("due_date"),
                )

            elif tool_name == "list_tasks":
                result = await list_tasks(
                    user_id=arguments.get("user_id"),
                    status=arguments.get("status"),
                )

            elif tool_name == "complete_task":
                result = await complete_task(
                    user_id=arguments.get("user_id"),
                    task_id=arguments.get("task_id"),
                )

            elif tool_name == "delete_task":
                result = await delete_task(
                    user_id=arguments.get("user_id"),
                    task_id=arguments.get("task_id"),
                )

            elif tool_name == "update_task":
                result = await update_task(
                    user_id=arguments.get("user_id"),
                    task_id=arguments.get("task_id"),
                    title=arguments.get("title"),
                    description=arguments.get("description"),
                    status=arguments.get("status"),
                    priority=arguments.get("priority"),
                )

            else:
                raise ValueError(f"Unknown MCP tool: {tool_name}")

            # Convert MCPResponse to dict
            response_dict = {
                "success": result.success,
                "message": result.message,
                "data": result.data,
            }

            logger.info(f"✅ MCP tool {tool_name} completed: {result.message}")
            return response_dict

        except Exception as e:
            logger.error(f"❌ MCP tool {tool_name} failed: {e}")
            raise

    async def close(self):
        """Close MCP service (no-op for integrated service)"""
        logger.info("🔌 MCP Service closed")

    def get_status(self) -> Dict[str, Any]:
        """Get MCP service status"""
        return {
            "state": "integrated",
            "type": "direct",
            "message": "MCP tools running within FastAPI backend (PDF compliant)",
            "tools": ["add_task", "list_tasks", "complete_task", "delete_task", "update_task"],
        }


# ============================================================================
# Singleton Instance
# ============================================================================

_mcp_service_instance: MCPService | None = None


def get_mcp_service() -> MCPService:
    """
    Get singleton MCP service instance.

    Returns:
        MCPService instance
    """
    global _mcp_service_instance

    if _mcp_service_instance is None:
        _mcp_service_instance = MCPService()
        logger.info("✨ Initialized MCP Service (integrated mode)")

    return _mcp_service_instance


async def close_mcp_service():
    """Close the singleton MCP service"""
    global _mcp_service_instance

    if _mcp_service_instance is not None:
        await _mcp_service_instance.close()
        _mcp_service_instance = None
        logger.info("🔌 MCP Service closed")
