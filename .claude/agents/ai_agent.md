# AI Agent Specification (T143)

**Primary Responsibility:** Natural language understanding, intent detection, tool selection, and response generation

## Overview

The AI Agent is the core intelligence component of Phase 3's conversational interface. It processes natural language input from users, determines intent, selects appropriate MCP tools, extracts parameters, invokes tools, and generates human-friendly responses.

## Responsibilities

### 1. Natural Language Understanding (NLU)
- Parse user messages to understand intent
- Handle ambiguous or incomplete requests
- Identify entities (task titles, due dates, priorities)
- Maintain conversation context across multiple turns

### 2. Intent Detection
- Classify user intent into action categories:
  - `add_task` - "Add buy milk to my list"
  - `list_tasks` - "Show me my tasks" / "What's on my todo list?"
  - `complete_task` - "Mark groceries as done"
  - `update_task` - "Change the due date to tomorrow"
  - `delete_task` - "Remove the meeting task"
  - `general_conversation` - Greetings, questions, clarifications
- Handle multi-intent requests ("Add task and show my list")
- Detect out-of-scope requests

### 3. Tool Selection and Parameter Extraction
- Map detected intent to MCP tool name
- Extract required parameters from natural language:
  - `user_id` (from JWT context)
  - `title` - task description
  - `task_id` - task identifier (by title or position)
  - `completed` - boolean status
  - `priority`, `due_date`, `description` - optional attributes
- Validate parameter completeness before tool invocation
- Request clarification if parameters are missing or ambiguous

### 4. Tool Invocation
- Call MCP tools via `invoke_mcp_tool()` skill
- Handle tool execution errors gracefully
- Retry transient failures with exponential backoff
- Map technical errors to user-friendly messages

### 5. Response Generation
- Generate natural, conversational responses
- Confirm successful actions ("I've added 'buy milk' to your list")
- Provide helpful feedback on errors ("I couldn't find that task. Can you describe it differently?")
- Maintain consistent tone and personality
- Use conversational patterns (avoid robotic responses)

## Inputs

### Request Input
```python
{
    "message": str,           # User's natural language input
    "conversation_id": int,   # Conversation identifier
    "user_id": int,          # User identifier (from JWT)
    "history": List[Dict],   # Conversation history (last N messages)
}
```

### Conversation History Format
```python
[
    {"role": "user", "content": "Add buy milk"},
    {"role": "assistant", "content": "I've added 'buy milk' to your task list."},
    {"role": "user", "content": "What's on my list?"},
]
```

## Outputs

### Response Output
```python
{
    "response": str,              # Natural language response
    "tool_calls": List[Dict],     # MCP tools invoked
    "intent": str,                # Detected intent
    "confidence": float,          # Intent confidence (0-1)
    "requires_clarification": bool,
    "clarification_prompt": str | None,
}
```

### Tool Call Format
```python
{
    "tool_name": str,        # MCP tool name
    "arguments": Dict,       # Tool arguments
    "result": Dict | None,   # Tool execution result
    "error": str | None,     # Error message if failed
}
```

## Constraints

### Performance Constraints
- **Response Time:** < 2 seconds (p95 latency)
  - LLM call: < 1.5 seconds
  - MCP tool invocation: < 500ms
  - Total: < 2 seconds end-to-end
- **Token Budget:** < 4000 tokens per request (input + output)
- **Conversation History:** Last 10 messages maximum (context window management)

### Functional Constraints
- **Stateless Operation:** No server-side state between requests
  - All context from conversation history (database)
  - No in-memory conversation tracking
- **User Isolation:** Only access tasks belonging to authenticated user
- **Idempotency:** Same input → same output (within reason for LLM stochasticity)
- **Graceful Degradation:** If MCP server unavailable, inform user (don't crash)

### Security Constraints
- **No Direct Database Access:** Only via MCP tools
- **JWT Verification Required:** user_id must be authenticated
- **Input Sanitization:** Validate all user inputs before processing
- **No PII Logging:** Don't log message content with user identifiers

### Model Constraints
- **Model:** OpenAI GPT-4 (or compatible)
- **Temperature:** 0.7 (balanced creativity/consistency)
- **Max Tokens:** 500 (response generation)
- **System Prompt:** Fixed template (version controlled)

## Architecture

### Component Integration

```
User Input
    ↓
Chat API Endpoint (FastAPI)
    ↓
JWT Verification (get_current_user_id)
    ↓
Conversation History Loader (load last 10 messages)
    ↓
AI Agent Runner
    ↓
    ├─→ OpenAI API (intent detection, NLU)
    ├─→ MCP Tool Invocation (execute actions)
    └─→ Response Generator (create user response)
    ↓
Save Message to Database
    ↓
Return Response to User
```

### Agent Runner Implementation Pattern

```python
from openai import AsyncOpenAI
from app.skills.mcp_tool_invocation import invoke_mcp_tool
from app.skills.conversation_history_loader import load_conversation_history

class AIAgentRunner:
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.system_prompt = self._load_system_prompt()

    async def run(
        self,
        message: str,
        conversation_id: int,
        user_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """
        Process user message and generate response.

        Flow:
        1. Load conversation history
        2. Call OpenAI for intent detection + tool selection
        3. Invoke MCP tools if needed
        4. Generate final response
        5. Return result
        """
        # Load history
        history = load_conversation_history(
            conversation_id=conversation_id,
            user_id=user_id,
            db=db,
            limit=10
        )

        # Build messages
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + history + [
            {"role": "user", "content": message}
        ]

        # Call OpenAI with tools
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=self._get_mcp_tool_definitions(),
            temperature=0.7,
            max_tokens=500
        )

        # Process tool calls
        tool_calls = []
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                # Inject user_id
                arguments["user_id"] = user_id

                # Invoke MCP tool
                try:
                    result = await invoke_mcp_tool(tool_name, arguments)
                    tool_calls.append({
                        "tool_name": tool_name,
                        "arguments": arguments,
                        "result": result,
                        "error": None
                    })
                except Exception as e:
                    tool_calls.append({
                        "tool_name": tool_name,
                        "arguments": arguments,
                        "result": None,
                        "error": str(e)
                    })

        # Generate final response
        final_response = response.choices[0].message.content

        return {
            "response": final_response,
            "tool_calls": tool_calls,
            "intent": self._detect_intent(message),
            "confidence": 0.95,  # From OpenAI response metadata
            "requires_clarification": False,
        }

    def _get_mcp_tool_definitions(self) -> List[Dict]:
        """Return OpenAI function definitions for MCP tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Add a new task to the user's todo list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Task title"},
                            "description": {"type": "string"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                            "due_date": {"type": "string", "format": "date"},
                        },
                        "required": ["title"]
                    }
                }
            },
            # ... other tools (list_tasks, complete_task, etc.)
        ]
```

## System Prompt Template

```
You are a helpful AI assistant for a todo list application. Your job is to help users manage their tasks through natural conversation.

Capabilities:
- Add tasks to the user's list
- Show tasks (all, pending, or completed)
- Mark tasks as complete
- Update task details (title, priority, due date)
- Delete tasks

Guidelines:
1. Be conversational and friendly
2. Confirm actions clearly ("I've added 'buy milk' to your list")
3. If a request is ambiguous, ask for clarification
4. Use the provided tools to perform actions
5. Always inject user_id from context (don't ask user for it)
6. If you can't help with something, be honest and helpful

Examples:
User: "Add buy milk to my list"
Assistant: [Calls add_task with title="buy milk"] "I've added 'buy milk' to your task list."

User: "What do I need to do?"
Assistant: [Calls list_tasks] "You have 3 tasks: 1. Buy milk, 2. Call dentist, 3. Finish report"

User: "I finished the milk task"
Assistant: [Calls complete_task] "Great! I've marked 'buy milk' as complete."
```

## Error Handling

### LLM Errors
- **Rate Limit:** Retry with exponential backoff (3 attempts)
- **Timeout:** Return error after 5 seconds
- **Invalid Response:** Log and return generic error message

### MCP Tool Errors
- **Tool Not Found:** "I don't know how to do that yet"
- **Invalid Parameters:** "I need more information. Can you provide [missing param]?"
- **Execution Failure:** "I encountered an error: [user-friendly message]"
- **Circuit Breaker Open:** "The task service is temporarily unavailable"

### Conversation Errors
- **History Load Failure:** Proceed without history (fresh conversation)
- **Permission Error:** "You don't have access to that conversation"

## Testing Strategy

### Unit Tests
- Intent detection accuracy (test cases for each intent)
- Parameter extraction correctness
- Tool selection logic
- Error handling paths

### Integration Tests
- End-to-end conversation flows
- MCP tool invocation with mocked responses
- Error scenarios (tool failures, timeouts)

### Acceptance Tests
- User stories validation:
  - User says "Add buy milk" → task created
  - User says "Show my tasks" → tasks listed
  - User says "Mark milk as done" → task completed

### Performance Tests
- Response time < 2 seconds (p95)
- Token usage < 4000 per request
- Handle 10 concurrent requests

## Metrics and Monitoring

### Key Metrics
- **Intent Detection Accuracy:** % of correctly identified intents
- **Tool Invocation Success Rate:** % of successful tool calls
- **Response Time:** p50, p95, p99 latency
- **Error Rate:** % of requests resulting in errors
- **Token Usage:** Average tokens per request

### Alerts
- Response time > 5 seconds (p95)
- Error rate > 5%
- OpenAI API errors > 10/minute

## Related Documentation

- [MCP Tool Invocation Skill](../skills/mcp_tool_invocation.md) - Tool calling patterns
- [Conversation History Loader](../skills/conversation_history_loader.md) - History loading
- [Error Response Formatter](../skills/error_response_formatter.md) - Error handling
- [Chat API Agent](./chat_api_agent.md) - Request orchestration
- [Architecture](../docs/architecture.md) - System design

---

**Agent Owner:** Backend Team
**Dependencies:** OpenAI API, MCP Server, PostgreSQL
**Security Level:** High (handles user data, requires JWT)
**Deployment:** Stateless, horizontally scalable
**Performance Target:** < 2s response time (p95), < 4000 tokens/request
