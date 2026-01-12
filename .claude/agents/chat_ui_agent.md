# Chat UI Agent Specification (T147)

**Primary Responsibility:** ChatKit integration, message rendering, and real-time UI updates

## Overview

The Chat UI Agent manages the frontend chatbot interface using ChatKit. It handles message rendering, user input, real-time updates, loading states, error display, and authentication integration. This agent operates in the browser and provides a polished chat experience.

## Responsibilities

### 1. ChatKit Integration
- Integrate ChatKit UI components (chat container, message list, input field)
- Configure ChatKit styling and layout
- Handle ChatKit events (message send, scroll, etc.)
- Customize ChatKit appearance to match app design
- Ensure responsive design (mobile, tablet, desktop)

### 2. Message Rendering
- Display user messages (right-aligned, blue background)
- Display assistant messages (left-aligned, gray background)
- Format message timestamps
- Render message content with markdown support
- Display tool call results (collapsible accordions)
- Handle long messages (scrolling, word wrap)

### 3. Real-Time UI Updates
- Show loading indicator when AI is processing
- Display "AI is typing..." animation
- Update message list as new messages arrive
- Scroll to bottom on new message
- Handle optimistic UI updates (show message immediately, update on response)

### 4. Authentication Integration
- Attach JWT token to all API requests
- Handle 401 errors (token expired → redirect to login)
- Display authentication errors to user
- Refresh token if needed (future enhancement)

### 5. Error Handling and Display
- Display error messages in chat UI
- Show retry button on failures
- Handle network errors gracefully
- Display rate limit errors with countdown timer

## Inputs

### Component Props
```typescript
interface ChatUIProps {
    conversationId?: number;  // Optional - creates new if omitted
    userId: number;           // From authentication context
    jwtToken: string;         // From localStorage or auth context
}
```

### API Response (from Chat API)
```typescript
interface ChatResponse {
    conversation_id: number;
    message_id: number;
    response: string;
    tool_calls: ToolCall[];
    created_at: string;
}

interface ToolCall {
    tool_name: string;
    arguments: Record<string, any>;
    result: Record<string, any> | null;
    error: string | null;
}
```

### Error Response
```typescript
interface ErrorResponse {
    detail: {
        error: string;
        message: string;
        retry_after?: number;
        field?: string;
    }
}
```

## Outputs

### UI State
```typescript
interface ChatUIState {
    messages: Message[];           // All messages in conversation
    isLoading: boolean;            // AI is processing
    error: string | null;          // Current error message
    conversationId: number | null; // Current conversation ID
    inputValue: string;            // User input field value
}

interface Message {
    id: number;
    role: "user" | "assistant";
    content: string;
    created_at: string;
    tool_calls?: ToolCall[];
}
```

### UI Events
- `onMessageSend`: User sends message → API request
- `onMessageReceived`: API response → update UI
- `onError`: Error occurred → display error
- `onRetry`: User clicks retry → resend request

## Constraints

### Performance Constraints
- **Initial Load Time:** < 1 second
- **Message Render Time:** < 50ms per message
- **Scroll Performance:** 60 FPS on mobile devices
- **Memory Usage:** < 50MB for 100 messages

### Functional Constraints
- **Message Limit:** Display last 50 messages (pagination for older)
- **Input Length:** 1-2000 characters
- **Auto-scroll:** Scroll to bottom on new message (unless user scrolled up)
- **Offline Handling:** Show "offline" message, queue messages (future)

### UI/UX Constraints
- **Responsive Design:** Support 320px - 4K screens
- **Accessibility:** ARIA labels, keyboard navigation, screen reader support
- **Loading States:** Always show loading indicator during API calls
- **Error States:** Clear error messages with actionable next steps

## Architecture

### Component Structure

```
ChatUI (Container)
    ├─ ChatHeader (conversation title, user info)
    ├─ MessageList (scrollable message container)
    │   ├─ UserMessage (right-aligned, blue)
    │   ├─ AssistantMessage (left-aligned, gray)
    │   │   └─ ToolCallsAccordion (collapsible tool results)
    │   └─ LoadingIndicator ("AI is typing...")
    ├─ ChatInputField (text input + send button)
    └─ ErrorDisplay (error messages + retry button)
```

### React Component Implementation

```typescript
"use client";

import { useState, useEffect, useRef } from "react";
import { Message, ChatResponse, ErrorResponse } from "@/types/chat";

interface ChatUIProps {
    conversationId?: number;
    userId: number;
    jwtToken: string;
}

export default function ChatUI({ conversationId, userId, jwtToken }: ChatUIProps) {
    // State
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [currentConversationId, setCurrentConversationId] = useState<number | null>(
        conversationId || null
    );

    // Refs
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Auto-scroll to bottom
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Load conversation history on mount
    useEffect(() => {
        if (currentConversationId) {
            loadHistory(currentConversationId);
        }
    }, [currentConversationId]);

    // Load conversation history
    const loadHistory = async (convId: number) => {
        try {
            const response = await fetch(`/api/conversations/${convId}/history`, {
                headers: {
                    Authorization: `Bearer ${jwtToken}`,
                },
            });

            if (response.status === 401) {
                // Token expired - redirect to login
                localStorage.removeItem("jwt_token");
                window.location.href = "/login";
                return;
            }

            if (!response.ok) {
                throw new Error("Failed to load conversation history");
            }

            const data = await response.json();
            setMessages(data.messages.map((msg: any) => ({
                id: msg.id,
                role: msg.role,
                content: msg.content,
                created_at: msg.created_at,
            })));
        } catch (err) {
            console.error("Failed to load history:", err);
            setError("Failed to load conversation history");
        }
    };

    // Send message
    const sendMessage = async () => {
        if (!inputValue.trim()) return;

        // Clear error
        setError(null);

        // Optimistic UI update (add user message immediately)
        const userMessage: Message = {
            id: Date.now(),  // Temporary ID
            role: "user",
            content: inputValue,
            created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, userMessage]);

        // Clear input and set loading
        setInputValue("");
        setIsLoading(true);

        try {
            // Call chat API
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${jwtToken}`,
                },
                body: JSON.stringify({
                    message: userMessage.content,
                    conversation_id: currentConversationId,
                }),
            });

            // Handle authentication errors
            if (response.status === 401) {
                const errorData: ErrorResponse = await response.json();
                if (errorData.detail.error === "token_expired") {
                    localStorage.removeItem("jwt_token");
                    window.location.href = "/login";
                }
                throw new Error(errorData.detail.message);
            }

            // Handle rate limiting
            if (response.status === 429) {
                const errorData: ErrorResponse = await response.json();
                setError(
                    `${errorData.detail.message} (${errorData.detail.retry_after}s remaining)`
                );
                return;
            }

            // Handle other errors
            if (!response.ok) {
                const errorData: ErrorResponse = await response.json();
                throw new Error(errorData.detail.message || "Failed to send message");
            }

            // Success - add assistant response
            const data: ChatResponse = await response.json();

            // Update conversation ID if new conversation
            if (!currentConversationId) {
                setCurrentConversationId(data.conversation_id);
            }

            // Add assistant message
            const assistantMessage: Message = {
                id: data.message_id,
                role: "assistant",
                content: data.response,
                created_at: data.created_at,
                tool_calls: data.tool_calls,
            };
            setMessages((prev) => [...prev, assistantMessage]);

        } catch (err: any) {
            console.error("Failed to send message:", err);
            setError(err.message || "Failed to send message. Please try again.");
        } finally {
            setIsLoading(false);
            inputRef.current?.focus();
        }
    };

    // Handle Enter key
    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white border-b px-4 py-3 shadow-sm">
                <h1 className="text-lg font-semibold text-gray-800">
                    Todo Assistant
                </h1>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex ${
                            message.role === "user" ? "justify-end" : "justify-start"
                        }`}
                    >
                        <div
                            className={`max-w-[70%] rounded-lg px-4 py-2 ${
                                message.role === "user"
                                    ? "bg-blue-500 text-white"
                                    : "bg-gray-200 text-gray-800"
                            }`}
                        >
                            <p className="whitespace-pre-wrap">{message.content}</p>

                            {/* Tool calls (if any) */}
                            {message.tool_calls && message.tool_calls.length > 0 && (
                                <details className="mt-2 text-sm">
                                    <summary className="cursor-pointer opacity-75 hover:opacity-100">
                                        View tool calls ({message.tool_calls.length})
                                    </summary>
                                    <div className="mt-2 space-y-2">
                                        {message.tool_calls.map((call, idx) => (
                                            <div key={idx} className="bg-gray-100 rounded p-2">
                                                <div className="font-semibold">{call.tool_name}</div>
                                                {call.result && (
                                                    <pre className="text-xs mt-1 overflow-auto">
                                                        {JSON.stringify(call.result, null, 2)}
                                                    </pre>
                                                )}
                                                {call.error && (
                                                    <div className="text-red-600 text-xs mt-1">
                                                        Error: {call.error}
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </details>
                            )}

                            <div className="text-xs opacity-75 mt-1">
                                {new Date(message.created_at).toLocaleTimeString()}
                            </div>
                        </div>
                    </div>
                ))}

                {/* Loading indicator */}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-200 rounded-lg px-4 py-2 text-gray-600">
                            <div className="flex items-center space-x-2">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Error display */}
                {error && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-800">
                        <p>{error}</p>
                        <button
                            onClick={() => setError(null)}
                            className="mt-2 text-sm underline hover:no-underline"
                        >
                            Dismiss
                        </button>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="bg-white border-t px-4 py-3">
                <div className="flex space-x-2">
                    <input
                        ref={inputRef}
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Type a message..."
                        className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={isLoading}
                        maxLength={2000}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={isLoading || !inputValue.trim()}
                        className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                    >
                        Send
                    </button>
                </div>
            </div>
        </div>
    );
}
```

## Error Handling

### Authentication Errors (401)
- **Token Expired:** Clear localStorage, redirect to login
- **Token Invalid:** Clear localStorage, redirect to login
- Display: "Your session has expired. Redirecting to login..."

### Rate Limiting Errors (429)
- Display: "Too many requests. Please wait [X] seconds."
- Show countdown timer
- Disable input during countdown
- Auto-retry when countdown finishes (optional)

### Network Errors
- Display: "Network error. Please check your connection."
- Show retry button
- Indicate offline status

### Validation Errors (400)
- Display error message from API
- Highlight problematic field (if applicable)
- Keep user input so they can correct it

### Service Errors (503)
- Display: "Service temporarily unavailable. Please try again in a moment."
- Show retry button
- Auto-retry after 5 seconds (up to 3 attempts)

## Testing Strategy

### Unit Tests
- Message rendering (user vs assistant)
- Input validation (empty, too long)
- Error display (various error types)
- Auto-scroll behavior

### Integration Tests
- Send message → API call → response displayed
- Authentication error → redirect to login
- Rate limit error → countdown displayed
- Tool calls → accordion display

### E2E Tests (Playwright)
- User types message → clicks send → sees response
- Page reload → conversation persists (if conversation_id set)
- Expired token → redirected to login
- Network offline → error displayed with retry

### Accessibility Tests
- Keyboard navigation (Tab, Enter)
- Screen reader announcements
- ARIA labels and roles
- Focus management

## Accessibility (A11y)

### ARIA Labels
```tsx
<div role="log" aria-live="polite" aria-atomic="false">
    {/* Messages */}
</div>

<input
    type="text"
    aria-label="Chat message input"
    aria-describedby="char-count"
/>

<button
    onClick={sendMessage}
    aria-label="Send message"
    aria-disabled={isLoading}
>
    Send
</button>
```

### Keyboard Support
- **Enter:** Send message
- **Shift+Enter:** New line in message
- **Escape:** Clear error message
- **Tab:** Navigate between input and buttons

### Screen Reader Support
- Announce new messages as they arrive
- Announce loading state ("AI is typing")
- Announce errors clearly

## Related Documentation

- [Chat API Agent](./chat_api_agent.md) - Backend API
- [AI Agent](./ai_agent.md) - Message processing
- [JWT Verification](../skills/jwt_verification.md) - Authentication
- [Error Response Formatter](../skills/error_response_formatter.md) - Error handling
- [ChatKit Documentation](https://chatkit.io) - UI library (if using external)

---

**Agent Owner:** Frontend Team
**Dependencies:** React, Next.js, Tailwind CSS, ChatKit (optional)
**Security Level:** Medium (handles JWT, user input)
**Deployment:** Client-side React component
**Performance Target:** < 1s initial load, < 50ms message render, 60 FPS scroll
**Accessibility:** WCAG 2.1 AA compliant
