---
name: advanced-tasks
description: Handle intermediate and advanced task features like priority, tags, sorting, recurring tasks, due dates, bulk operations, and notes. Trigger when user asks about priority levels, task tags, sorting tasks, recurring schedules, due dates, or bulk task actions.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# Advanced Tasks Skill

Expert guidance for implementing and managing advanced task features in the Todo Full-Stack Web Application.

## Available Features

| Feature | Description | Status |
|---------|-------------|--------|
| Priority | low, medium, high, urgent | ✅ Implemented |
| Tags | Category labels (Work, Home, etc.) | ✅ Implemented |
| Due Dates | Deadline with date/time | ✅ Implemented |
| Recurrence | daily, weekly, monthly | ✅ Implemented |
| Notes | Task comments/attachments | ✅ Implemented |
| Bulk Operations | Multi-task actions | ✅ Implemented |
| Search/Filter | Advanced filtering | ✅ Implemented |

---

## 1. Priority System

### Priority Levels

```python
# Backend: app/models/task.py
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"      # Default
    HIGH = "high"
    URGENT = "urgent"
```

### Priority Colors (Frontend)

```tsx
// components/tasks/EnhancedTaskCard.tsx
const priorityConfig = {
  low: {
    strip: 'bg-gray-500',
    badge: 'bg-gray-500/20 text-gray-300',
    icon: '⬇️'
  },
  medium: {
    strip: 'bg-blue-500',
    badge: 'bg-blue-500/20 text-blue-300',
    icon: '➡️'
  },
  high: {
    strip: 'bg-orange-500',
    badge: 'bg-orange-500/20 text-orange-300',
    icon: '⬆️'
  },
  urgent: {
    strip: 'bg-red-500',
    badge: 'bg-red-500/20 text-red-300',
    icon: '🔥'
  }
}
```

### MCP Tool: set_priority

```python
# Backend MCP tool
async def set_priority(user_id: str, task_id: int, priority: str):
    """Set task priority level"""
    # Valid: low, medium, high, urgent
```

### Natural Language Examples

```
"Add buy milk with high priority"
"Set task 5 priority to urgent"
"Make the report task high priority"
```

---

## 2. Tags System

### Available Tags

```python
AVAILABLE_TAGS = [
    "Work",
    "Home",
    "Personal",
    "Shopping",
    "Health",
    "Finance",
    "Learning"
]
```

### Database Schema

```python
# Task model
tags: List[str] | None = Field(default=None)  # JSON array in DB
```

### MCP Tools

```python
# Add tags
async def add_tags(user_id: str, task_id: int, tags: List[str]):
    """Add tags to a task"""

# Remove tags
async def remove_tags(user_id: str, task_id: int, tags: List[str]):
    """Remove tags from a task"""
```

### Frontend Display

```tsx
// Tag badge styling
{task.tags?.map((tag) => (
  <span className="px-2.5 py-1 rounded-md bg-indigo-500/20 text-indigo-300 text-xs">
    🏷 {tag}
  </span>
))}
```

### Natural Language Examples

```
"Add work tag to task 5"
"Tag the meeting task as Work and Finance"
"Remove shopping tag from task 3"
```

---

## 3. Due Dates

### Date Format

```python
# ISO 8601 format
due_date: datetime | None  # "2026-01-15T14:30:00"
```

### Supported Input Formats

```python
# Natural language (agent_runner.py)
DATE_KEYWORDS = {
    "today": 0,
    "tomorrow": 1,
    "kal": 1,          # Urdu
    "aaj": 0,          # Urdu
    "parson": 2,       # Urdu (day after tomorrow)
    "next week": 7,
    "next month": 30
}

# Explicit formats
"2026-01-15"           # Date only
"2026-01-15T14:30:00"  # Date + time
"Jan 15, 2026"         # Human readable
```

### MCP Tools

```python
# Set due date
async def set_due_date(user_id: str, task_id: int, due_date: str):
    """Set task due date"""

# Remove due date
async def remove_due_date(user_id: str, task_id: int):
    """Clear task due date"""
```

### Overdue Detection

```tsx
// Frontend: EnhancedTaskCard.tsx
const isOverdue = task.due_date &&
                  new Date(task.due_date) < new Date() &&
                  task.status !== 'completed'

// Overdue styling
className={isOverdue ? 'ring-1 ring-red-500/30' : ''}
```

### Natural Language Examples

```
"Add meeting tomorrow at 2pm"
"Set due date for task 5 to next week"
"Kal mujhy doctor jana hai"  # Urdu: tomorrow
```

---

## 4. Recurrence System

### Recurrence Types

```python
class Recurrence(str, Enum):
    NONE = "none"       # Default
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
```

### MCP Tool

```python
async def set_recurrence(user_id: str, task_id: int, recurrence: str):
    """Set task recurrence pattern"""
    # Valid: none, daily, weekly, monthly
```

### Frontend Display

```tsx
{task.recurrence && task.recurrence !== 'none' && (
  <span className="px-2.5 py-1 rounded-md bg-purple-500/20 text-purple-300 text-xs">
    🔄 {task.recurrence}
  </span>
)}
```

### Natural Language Examples

```
"Make buy groceries a weekly task"
"Set daily recurrence for exercise"
"Remove recurrence from task 5"
```

---

## 5. Notes System

### Note Structure

```python
# Task model
notes: List[Dict[str, str]] | None
# Format: [{"text": "Note content", "timestamp": "2026-01-10T10:30:00"}]
```

### MCP Tools

```python
# Add note
async def add_note(user_id: str, task_id: int, note: str):
    """Add a note/comment to task"""

# List notes
async def list_notes(user_id: str, task_id: int):
    """Get all notes for a task"""

# Delete note
async def delete_note(user_id: str, task_id: int, note_index: int):
    """Delete note by index"""
```

### Natural Language Examples

```
"Add note to task 5: Remember to bring documents"
"Show notes for the meeting task"
"Delete first note from task 3"
```

---

## 6. Bulk Operations

### Available Bulk Actions

```python
# Bulk complete
async def bulk_complete(user_id: str, task_ids: List[int]):
    """Mark multiple tasks as completed"""

# Bulk delete
async def bulk_delete(user_id: str, task_ids: List[int]):
    """Delete multiple tasks"""

# Bulk update priority
async def bulk_update_priority(user_id: str, task_ids: List[int], priority: str):
    """Update priority for multiple tasks"""

# Bulk add tags
async def bulk_add_tags(user_id: str, task_ids: List[int], tags: List[str]):
    """Add tags to multiple tasks"""
```

### Natural Language Examples

```
"Complete tasks 1, 3, and 5"
"Delete all completed tasks"
"Set high priority for tasks 2 and 4"
"Add Work tag to tasks 1, 2, 3"
```

---

## 7. Search & Filter

### Search Tool

```python
async def search_tasks(
    user_id: str,
    query: str = None,           # Text search in title/description
    status: str = None,          # pending, in_progress, completed
    priority: str = None,        # low, medium, high, urgent
    tags: List[str] = None,      # Filter by tags
    due_before: str = None,      # Due date before
    due_after: str = None        # Due date after
):
    """Advanced task search with filters"""
```

### Sorting Options

```python
SORT_OPTIONS = {
    "title": "Alphabetical",
    "created_at": "Creation date",
    "due_date": "Due date",
    "priority": "Priority level"
}

SORT_ORDER = ["asc", "desc"]
```

### Natural Language Examples

```
"Show high priority tasks"
"Find tasks due this week"
"Search for tasks with Work tag"
"List overdue tasks"
"Show pending tasks sorted by due date"
```

---

## 8. Backend API Endpoints

### Task CRUD

```
POST   /api/tasks              # Create task
GET    /api/tasks              # List tasks (with filters)
GET    /api/tasks/{id}         # Get single task
PUT    /api/tasks/{id}         # Update task
DELETE /api/tasks/{id}         # Delete task
PATCH  /api/tasks/{id}/toggle  # Toggle completion
```

### Query Parameters

```
GET /api/tasks?status=pending&priority=high&sort_by=due_date&sort_order=asc
```

---

## 9. Frontend Type Definitions

```typescript
// types/index.ts
interface Task {
  id: number
  user_id: string
  title: string
  description: string | null
  status: 'pending' | 'in_progress' | 'completed'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  completed: boolean
  due_date: string | null
  tags: string[] | null
  recurrence: 'none' | 'daily' | 'weekly' | 'monthly'
  notes: Array<{ text: string; timestamp: string }> | null
  created_at: string
  updated_at: string
}
```

---

## Common Implementation Patterns

### Adding New Feature to Task

1. **Backend:**
   - Update Task model in `app/models/task.py`
   - Add MCP tool in `app/services/mcp_server.py`
   - Update API schemas in `app/schemas/task.py`

2. **Frontend:**
   - Update Task type in `types/index.ts`
   - Add UI in `EnhancedTaskCard.tsx`
   - Add form field in `EnhancedTaskForm.tsx`

3. **Chatbot:**
   - Add intent detection in `agent_runner.py`
   - Update SYSTEM_PROMPT with new feature
   - Add tool to available tools list

### Testing Features

```bash
# Backend tests
cd phase_3/backend
pytest tests/ -v

# Test MCP tools
python -m app.services.mcp_server
```
