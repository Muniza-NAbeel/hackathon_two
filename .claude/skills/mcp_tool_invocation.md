# MCP Tool Invocation Skill (T141)

**Pattern for calling MCP tools with retry logic and error mapping**

## Overview

Provides reliable invocation of MCP tools with circuit breaker protection, retry logic, and user-friendly error mapping.

## Core Implementation

```python
from app.services.mcp_client import get_mcp_client, CircuitBreakerError

async def invoke_mcp_tool(
    tool_name: str,
    arguments: dict,
    max_retries: int = 2
) -> dict:
    """
    Invoke MCP tool with error handling and retries.

    Args:
        tool_name: Name of MCP tool (add_task, list_tasks, etc.)
        arguments: Tool arguments (user_id, title, etc.)
        max_retries: Maximum retry attempts (default: 2)

    Returns:
        Tool execution result

    Raises:
        CircuitBreakerError: If MCP server is down
        ValueError: If tool validation fails
        Exception: For other errors
    """
    mcp_client = get_mcp_client()

    for attempt in range(max_retries + 1):
        try:
            result = await mcp_client.call_tool(tool_name, arguments)
            return result

        except CircuitBreakerError:
            # Circuit breaker open - don't retry
            raise

        except Exception as e:
            if attempt == max_retries:
                # Final attempt failed
                raise

            # Retry on transient errors
            logger.warning(f"MCP tool {tool_name} attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(0.5 * (attempt + 1))  # Incremental backoff

    raise Exception(f"Failed to invoke {tool_name} after {max_retries + 1} attempts")
```

## Error Mapping

```python
def map_mcp_error_to_user_message(error: Exception, tool_name: str) -> str:
    """Map technical MCP errors to user-friendly messages."""

    error_str = str(error).lower()

    if isinstance(error, CircuitBreakerError):
        return "The task service is temporarily unavailable. Please try again in a moment."

    if "not found" in error_str:
        if tool_name in ["complete_task", "update_task", "delete_task"]:
            return "I couldn't find that task. It may have been deleted or doesn't belong to you."
        return "Resource not found."

    if "validation" in error_str or "invalid" in error_str:
        return f"Invalid input: {error}"

    if "timeout" in error_str:
        return "The request took too long. Please try again."

    return "I encountered an error processing your request. Please try again."
```

## Usage in Agent

```python
class AgentRunner:
    async def execute_tool_call(self, tool_name: str, args: dict) -> dict:
        """Execute MCP tool with comprehensive error handling."""

        try:
            # Invoke tool
            result = await invoke_mcp_tool(tool_name, args)

            # Generate confirmation message
            confirmation = self.generate_confirmation(result, tool_name)

            return {
                "success": True,
                "result": result,
                "message": confirmation
            }

        except CircuitBreakerError as e:
            return {
                "success": False,
                "error": "service_unavailable",
                "message": map_mcp_error_to_user_message(e, tool_name)
            }

        except ValueError as e:
            return {
                "success": False,
                "error": "validation_error",
                "message": map_mcp_error_to_user_message(e, tool_name)
            }

        except Exception as e:
            logger.error(f"MCP tool {tool_name} failed: {e}")
            return {
                "success": False,
                "error": "unknown_error",
                "message": map_mcp_error_to_user_message(e, tool_name)
            }
```

## Testing

```python
@pytest.mark.asyncio
async def test_invoke_mcp_tool_success():
    result = await invoke_mcp_tool(
        "add_task",
        {"user_id": 123, "title": "Test task"}
    )
    assert result["status"] == "created"

@pytest.mark.asyncio
async def test_invoke_mcp_tool_circuit_breaker():
    # Simulate circuit breaker open
    with pytest.raises(CircuitBreakerError):
        await invoke_mcp_tool("add_task", {})
```

## Related Documentation

- [MCP Client](../backend/app/services/mcp_client.py) - Circuit breaker implementation
- [MCP Tools](../docs/mcp_tools.md) - Tool specifications
- [AI Agent Spec](../agents/ai_agent.md) - Agent responsibilities

---

**Skill Owner:** AI Agent
**Dependencies:** MCP Client, Circuit Breaker
**Retry Strategy:** 2 retries with incremental backoff (0.5s, 1s)
**Performance Target:** < 100ms (excluding network time)
