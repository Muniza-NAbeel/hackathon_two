---
name: task-chatbot
description: Design and integrate an AI chatbot that understands natural language and interacts with tasks. Trigger when user asks about chatbot design, AI integration, natural language processing, conversation flow, MCP tools, or voice input.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# Task Chatbot Skill

Expert guidance for designing and integrating the AI-powered chatbot for natural language task management.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  ChatInterface  │  │   VoiceInput    │  │  Messages   │ │
│  └────────┬────────┘  └────────┬────────┘  └─────────────┘ │
└───────────┼─────────────────────┼───────────────────────────┘
            │                     │
            ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │  Chat Endpoint  │──│  AgentRunner    │                   │
│  │  /api/chat      │  │  (Gemini AI)    │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
└───────────┼─────────────────────┼───────────────────────────┘
            │                     │
            ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ add_task │ │list_tasks│ │ complete │ │ delete   │ ...   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│              Neon PostgreSQL Database                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
phase_3/
├── frontend/
│   ├── components/chat/
│   │   ├── ChatInterface.tsx    # Main chat component
│   │   ├── VoiceInput.tsx       # Voice recognition
│   │   └── AIChatPanel.tsx      # Chat panel wrapper
│   └── lib/api/
│       └── chat.ts              # Chat API client
│
└── backend/
    ├── app/
    │   ├── routers/
    │   │   └── chat.py          # Chat API endpoint
    │   └── services/
    │       ├── agent_runner.py  # AI agent logic
    │       └── mcp_server.py    # MCP tools
    └── tests/
        └── test_chat.py
```

---

## 1. AI Integration (Google Gemini)

### Configuration

```python
# backend/app/services/agent_runner.py
from openai import OpenAI

# Gemini via OpenAI SDK compatibility
openai_client = OpenAI(
    api_key=settings.GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
```

### Environment Variables

```env
# .env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Model Selection

```python
# Available models
"gemini-2.0-flash"      # Fast, good for chat
"gemini-1.5-pro"        # Better quality, slower
"gemini-2.5-flash"      # Latest flash model
```

---

## 2. System Prompt Design

### Personality & Identity

```python
SYSTEM_PROMPT = """You are TaskFlow AI 🤖, the intelligent assistant for TaskFlow.

## YOUR IDENTITY
- Name: TaskFlow AI (or simply "TaskFlow")
- NEVER say: "I don't have a name" or "I am an AI assistant"
- ALWAYS introduce yourself as: "Hi! I'm TaskFlow 🤖, your task assistant."

## PERSONALITY & TONE
- Warm, friendly, confident, and human-like
- Keep responses short, clear, and natural
- Sound like a premium task management assistant
"""
```

### Critical Rules

```python
"""
## CRITICAL RULES (MUST FOLLOW)

1. LANGUAGE MATCHING:
   - Support Urdu (اردو), Roman Urdu, and English
   - If user speaks Urdu/Roman Urdu, respond in SAME language
   - Detect date words: aaj, kal, parson, today, tomorrow

2. NEVER EXPOSE BACKEND:
   - NEVER show code, function calls, or API syntax
   - NEVER say: "Calling add_task()" or "print(task)"
   - Users should NEVER see technical details

3. NATURAL RESPONSES:
   WRONG ❌: "Calling add_task(title='Go to store')"
   CORRECT ✅: "Done 👍 I've added 'Go to store' to your tasks."
"""
```

---

## 3. Intent Detection

### Supported Intents

```python
# backend/app/services/agent_runner.py

def detect_intent(message: str) -> str:
    """Detect user intent from message"""

    # Task creation
    add_keywords = [
        'add', 'create', 'new task', 'remind me',
        'mujhy', 'mujhe', 'karna hai', 'jana hai'  # Urdu
    ]

    # Task listing
    list_keywords = [
        'show', 'list', 'display', 'view', 'my tasks',
        'dikhao', 'batao', 'mere tasks'  # Urdu
    ]

    # Task completion
    complete_keywords = ['complete', 'done', 'finished', 'mark']

    # Task update
    update_keywords = ['update', 'change', 'modify', 'edit']

    # Task deletion
    delete_keywords = ['delete', 'remove', 'cancel']

    return intent  # 'add_task', 'list_tasks', 'complete_task', etc.
```

### Adding New Intent

```python
# 1. Add keywords to detect_intent()
new_keywords = ['keyword1', 'keyword2']

# 2. Add handler in AgentRunner.run()
elif intent == "new_intent":
    # Extract info
    # Call MCP tool
    # Generate response

# 3. Update SYSTEM_PROMPT with new capability
```

---

## 4. MCP Tools Integration

### Available Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `add_task` | Create task | user_id, title, description, priority |
| `list_tasks` | Get tasks | user_id, status |
| `complete_task` | Mark complete | user_id, task_id |
| `update_task` | Update task | user_id, task_id, title, description |
| `delete_task` | Remove task | user_id, task_id |
| `set_priority` | Set priority | user_id, task_id, priority |
| `add_tags` | Add tags | user_id, task_id, tags |
| `set_due_date` | Set deadline | user_id, task_id, due_date |
| `search_tasks` | Search | user_id, query, filters |

### Calling MCP Tools

```python
# In AgentRunner
if self.mcp_client:
    mcp_response = await self.mcp_client.call_tool(
        "add_task",
        {
            "user_id": str(self.user_id),
            "title": task_info["title"],
            "description": task_info["description"],
            "priority": priority
        }
    )

    # Extract result
    if isinstance(mcp_response, dict) and "data" in mcp_response:
        tool_result = mcp_response["data"]
```

### MCP Response Format

```python
# Success
{
    "success": True,
    "message": "Task created successfully",
    "data": {
        "task_id": 123,
        "title": "Buy groceries",
        "status": "pending"
    }
}

# Error
{
    "success": False,
    "error": "Task not found"
}
```

---

## 5. Conversation Management

### Message Structure

```python
# Conversation history format
messages = [
    {"role": "user", "content": "Add buy milk"},
    {"role": "assistant", "content": "Done! I've added 'buy milk' to your tasks."},
    {"role": "user", "content": "Show my tasks"},
    {"role": "assistant", "content": "Here are your tasks:\n1. Buy milk"}
]
```

### Persistence

```python
# Frontend: lib/utils/storage.ts
export function getConversationId(): string | null
export function setConversationId(id: string): void
export function clearConversationId(): void

# Backend: stores conversation in database
# Loads history on page refresh
```

### New Conversation

```typescript
// Frontend: ChatInterface.tsx
const handleNewConversation = () => {
    clearConversationId()
    setMessages([])
}
```

---

## 6. Frontend Chat Component

### ChatInterface Structure

```tsx
// components/chat/ChatInterface.tsx
export function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([])
    const [inputValue, setInputValue] = useState('')
    const [isLoading, setIsLoading] = useState(false)

    // Send message
    const handleSend = async (text: string) => {
        // Add user message
        setMessages(prev => [...prev, { role: 'user', content: text }])

        // Call API
        const response = await sendMessage(text, conversationId, token)

        // Add assistant response
        setMessages(prev => [...prev, { role: 'assistant', content: response.response }])

        // Handle tool calls (refresh task list if modified)
        if (response.tool_calls?.length > 0) {
            window.dispatchEvent(new CustomEvent('taskModified'))
        }
    }

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            {/* Messages */}
            {/* Input area */}
        </div>
    )
}
```

### Message Styling

```tsx
// User message
<div className="bg-neon-cyan/10 border border-neon-cyan/30 rounded-lg px-4 py-3">
    {message.content}
</div>

// Assistant message
<div className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3">
    {message.content}
</div>

// Loading indicator
<div className="flex gap-1">
    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
</div>
```

---

## 7. Voice Input

### Web Speech API

```tsx
// components/chat/VoiceInput.tsx
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

const recognition = new SpeechRecognition()
recognition.continuous = false
recognition.interimResults = false
recognition.lang = 'en-US'  // or 'ur-PK' for Urdu

recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript
    onTranscript(transcript)
}

recognition.start()
```

### Supported Languages

```tsx
const languages = [
    { code: 'en-US', label: 'English', flag: '🇺🇸' },
    { code: 'ur-PK', label: 'Urdu', flag: '🇵🇰' }
]
```

---

## 8. API Endpoint

### Chat Endpoint

```python
# backend/app/routers/chat.py
@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Process chat message with AI agent"""

    # Load conversation history
    history = await load_conversation_history(request.conversation_id, db)

    # Run agent
    agent = AgentRunner(user_id=current_user.id, mcp_client=mcp_client)
    result = await agent.run(request.message, history)

    # Save messages
    await save_messages(conversation_id, request.message, result["response"], db)

    return {
        "response": result["response"],
        "conversation_id": conversation_id,
        "tool_calls": result["tool_calls"]
    }
```

### Request/Response Format

```typescript
// Request
interface ChatRequest {
    message: string
    conversation_id?: string
}

// Response
interface ChatResponse {
    response: string
    conversation_id: string
    tool_calls: Array<{
        tool: string
        arguments: object
        result: object
    }>
}
```

---

## 9. Error Handling

### Retry Logic

```python
# Exponential backoff for API calls
def retry_with_exponential_backoff(func, max_retries=3):
    delay = 1.0
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                raise
            delay = min(delay * 2, 10.0)
            time.sleep(delay)
```

### User-Friendly Errors

```typescript
// Frontend error handling
if (err.response?.status === 401) {
    setError('Session expired. Please log in again.')
} else if (err.response?.status === 500) {
    setError('AI service temporarily unavailable. Try again.')
} else {
    setError('Failed to send message. Check your connection.')
}
```

---

## 10. Multi-Language Support

### Language Detection

```python
# Urdu keywords for intent detection
urdu_add = ['mujhy', 'mujhe', 'karna hai', 'jana hai', 'banana hai']
urdu_list = ['dikhao', 'batao', 'mere tasks']
urdu_dates = ['aaj', 'kal', 'parson']  # today, tomorrow, day after
```

### Response Examples

```python
# English
"Done 👍 I've added 'Buy groceries' for tomorrow."

# Roman Urdu
"Theek hai 😊 Main ne 'Ammi ke ghar jana' kal ke liye add kar diya."
```

---

## 11. Testing

### Backend Tests

```python
# tests/test_chat.py
@pytest.mark.asyncio
async def test_add_task_intent():
    agent = AgentRunner(user_id=test_user_id)
    result = await agent.run("Add buy milk", [])

    assert "buy milk" in result["response"].lower()
    assert len(result["tool_calls"]) == 1
    assert result["tool_calls"][0]["tool"] == "add_task"
```

### Frontend Testing

```bash
# Manual testing
1. Open chat interface
2. Type "Add buy groceries"
3. Verify task appears in list
4. Type "Show my tasks"
5. Verify list is displayed
```

---

## Common Tasks

### Add New Tool to Chatbot

1. Create MCP tool in `mcp_server.py`
2. Add intent keywords in `agent_runner.py`
3. Add handler in `AgentRunner.run()`
4. Update `SYSTEM_PROMPT`
5. Test with natural language

### Improve Response Quality

1. Edit `SYSTEM_PROMPT` personality
2. Update `generate_confirmation()` messages
3. Add more intent keywords
4. Test with various phrasings

### Add New Language

1. Add keywords to intent detection
2. Update `SYSTEM_PROMPT` with language rules
3. Add response examples
4. Add to VoiceInput languages
