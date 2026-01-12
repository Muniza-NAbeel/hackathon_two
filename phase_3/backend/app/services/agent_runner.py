"""
AI Agent Runner Service

Integrates Google Gemini AI (via OpenAI SDK compatibility) to power natural language task management.

Features:
- Intent-to-tool mapping for task operations
- Title and description extraction from natural language
- Confirmation message generation
- MCP tool orchestration
- Exponential backoff retry logic for API failures
"""

import os
import re
import time
from typing import List, Dict, Any, Optional
from uuid import UUID
from openai import OpenAI
import logging
from app.config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# Gemini Client Initialization (using OpenAI SDK compatibility)
# ============================================================================

openai_client = OpenAI(
    api_key=settings.GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


# ============================================================================
# Retry Logic with Exponential Backoff (T128)
# ============================================================================

def retry_with_exponential_backoff(
    func,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
):
    """
    Retry a function with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 10.0)
        exponential_base: Base for exponential calculation (default: 2.0)

    Returns:
        Result from successful function call

    Raises:
        Last exception if all retries fail
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e

            if attempt == max_retries:
                # Final attempt failed
                logger.error(f"All {max_retries} retry attempts failed: {str(e)}")
                raise last_exception

            # Calculate delay with exponential backoff
            delay = min(initial_delay * (exponential_base ** attempt), max_delay)

            logger.warning(
                f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. "
                f"Retrying in {delay:.2f} seconds..."
            )

            time.sleep(delay)

    # Should not reach here, but just in case
    raise last_exception


# ============================================================================
# Agent Configuration
# ============================================================================

SYSTEM_PROMPT = """You are TaskFlow AI 🤖, the intelligent assistant for the TaskFlow AI Todo application.

## YOUR IDENTITY
- Name: TaskFlow AI (or simply "TaskFlow")
- NEVER say: "I don't have a name" or "I am an AI assistant"
- ALWAYS introduce yourself as: "Hi! I'm TaskFlow 🤖, your task assistant."

## PERSONALITY & TONE
- Warm, friendly, confident, and human-like
- Product-quality (NOT a demo or generic chatbot)
- Helpful assistant mindset
- Keep responses short, clear, and natural
- Sound like a premium task management assistant

## CRITICAL RULES (MUST FOLLOW)
1. LANGUAGE MATCHING:
   - Support Urdu (اردو), Roman Urdu, and English
   - If user speaks Urdu/Roman Urdu, respond in the SAME language
   - Never switch to English unless user uses English
   - Detect date words in all languages (aaj, kal, parson, today, tomorrow)

2. NEVER EXPOSE BACKEND:
   - NEVER show code, function calls, Python, JavaScript, or API syntax
   - NEVER say things like: "Calling add_task()" or "print(task)"
   - NEVER expose technical implementation details
   - Users should NEVER see how tools work internally

3. NATURAL TASK CREATION:
   When user says: "kal mujhy ammi k ghr jana hai" or "tomorrow I need to go to mother's house"

   WRONG ❌: "Calling add_task(title='Go to mother's house')"
   CORRECT ✅: "Theek hai 😊 Main ne 'Ammi ke ghar jana' task kal ke liye add kar diya hai."
   CORRECT ✅: "Done 👍 I've added 'Go to mother's house' for tomorrow."

## AVAILABLE TOOLS (Use silently in backend)
📋 BASIC OPERATIONS:
- add_task: Create tasks with title and optional description
- list_tasks: View all tasks, filtered by status
- complete_task: Mark tasks as completed
- update_task: Update task details
- delete_task: Remove tasks

⭐ ADVANCED FEATURES:
- set_priority: Set priority (low, medium, high, urgent)
- add_tags/remove_tags: Category tags (Work, Home, Personal, Shopping, Health, Finance, Learning)
- set_due_date/remove_due_date: Deadlines (supports: tomorrow, next week, YYYY-MM-DD, kal, aaj, parson)
- search_tasks: Advanced search with filters
- bulk operations: bulk_complete, bulk_delete, bulk_update_priority, bulk_add_tags
- add_note/list_notes/delete_note: Task comments
- set_recurrence: Recurring tasks (none, daily, weekly, monthly)

## RESPONSE EXAMPLES

English:
- "Done 👍 I've added 'Buy groceries' for tomorrow."
- "Great job! I've marked 'Finish report' as completed. ✅"
- "You now have 5 pending tasks."

Urdu/Roman Urdu:
- "Theek hai 😊 Main ne 'Ammi ke ghar jana' kal ke liye add kar diya."
- "Shabash! 'Report khatam karna' complete ho gaya hai. ✅"
- "Aap ke paas 5 pending tasks hain."

## SMART FOLLOW-UPS (Optional, max ONE question)
After confirmation, you MAY ask:
- "Kya is ke liye reminder set karna hai?"
- "Should I set a reminder for this?"
- "Is task ki priority kya rakhein?"
- "What priority should I set?"

Remember: You are a premium, production-grade assistant. Every interaction should feel natural, warm, and intelligent. NEVER break character by showing technical details."""


# ============================================================================
# Intent Recognition
# ============================================================================

def detect_intent(message: str) -> str:
    """
    Detect user intent from natural language message.

    Args:
        message: User's message

    Returns:
        Intent string: 'add_task', 'list_tasks', 'update_task', 'general', etc.
    """
    message_lower = message.lower().strip()

    # Task creation keywords (English + Roman Urdu)
    add_keywords = [
        'add', 'create', 'new task', 'remember to', 'remind me to', 'i need to',
        'task add', 'task create', 'make',  # Added 'make' for commands like "make dinner"
        'mujhy', 'mujhe', 'mujhay', 'main', 'hum',  # Roman Urdu: I need, I have to
        'karna hai', 'jana hai', 'lana hai', 'banana hai',  # Roman Urdu: need to do, need to go, need to bring, need to make
    ]

    for keyword in add_keywords:
        if keyword in message_lower:
            return 'add_task'

    # Task listing keywords (English + Roman Urdu)
    list_keywords = [
        'show', 'list', 'what are', 'display', 'view', 'see my', 'get my', 'my tasks',
        'tasks list', 'task list',
        'dikhao', 'dikha', 'dekhao', 'dekho',  # Roman Urdu: show
        'batao', 'bata',  # Roman Urdu: tell
        'mere tasks', 'mery tasks', 'meray tasks',  # Roman Urdu: my tasks
    ]

    for keyword in list_keywords:
        if keyword in message_lower:
            return 'list_tasks'

    # Task completion keywords
    complete_keywords = ['complete', 'done', 'finished', 'mark complete', 'mark as done', 'mark as complete', 'finish']

    for keyword in complete_keywords:
        if keyword in message_lower:
            return 'complete_task'

    # Priority update keywords - check BEFORE general update
    priority_keywords = ['priority', 'urgent', 'high priority', 'low priority', 'medium priority']
    priority_values = ['urgent', 'high', 'medium', 'low']

    # Check if message mentions priority
    has_priority_keyword = any(kw in message_lower for kw in priority_keywords)
    has_priority_value = any(pv in message_lower for pv in priority_values)

    # If message has task reference + priority keyword/value, it's a priority update
    # Supports: task #23, task 23, task num 23, task number 23, #23
    task_pattern = r'task\s*(?:#|num|number|no\.?)?\s*\d+|#\d+'
    if (has_priority_keyword or has_priority_value) and re.search(task_pattern, message_lower):
        return 'set_priority'

    # Task update keywords
    update_keywords = ['update', 'change', 'modify', 'edit', 'rename', 'revise']

    for keyword in update_keywords:
        if keyword in message_lower:
            # Check if this is actually a priority update
            if has_priority_keyword or has_priority_value:
                return 'set_priority'
            return 'update_task'

    # Task deletion keywords
    delete_keywords = ['delete', 'remove', 'cancel', 'get rid of', 'discard', 'drop']

    for keyword in delete_keywords:
        if keyword in message_lower:
            return 'delete_task'

    # Default to general conversation
    return 'general'


# ============================================================================
# Title and Description Extraction
# ============================================================================

def extract_task_info(message: str) -> Dict[str, Optional[str]]:
    """
    Extract task title and description from natural language.

    Args:
        message: User's message

    Returns:
        Dictionary with 'title' and 'description' keys

    Examples:
        >>> extract_task_info("Add buy groceries")
        {'title': 'buy groceries', 'description': None}

        >>> extract_task_info("Create task to call dentist tomorrow at 2pm")
        {'title': 'call dentist', 'description': 'tomorrow at 2pm'}
    """
    message_lower = message.lower().strip()

    # Remove common task creation prefixes (English + Roman Urdu)
    prefixes = [
        'add task to ',
        'add task ',
        'add a task to ',
        'add a task ',
        'add ',
        'create task to ',
        'create task ',
        'create a task to ',
        'create a task ',
        'create ',
        'new task: ',
        'new task ',
        'remember to ',
        'remind me to ',
        'i need to ',
        'mujhy ',
        'mujhe ',
        'mujhay ',
        'main ',
        'hum ',
        'humein ',
        'hamen ',
    ]

    cleaned_message = message_lower
    for prefix in prefixes:
        if cleaned_message.startswith(prefix):
            cleaned_message = cleaned_message[len(prefix):]
            break

    # Remove common Roman Urdu suffixes that don't add meaning
    suffixes = [
        ' hai',
        ' hy',
        ' hain',
        ' han',
        ' ho',
    ]

    for suffix in suffixes:
        if cleaned_message.endswith(suffix):
            cleaned_message = cleaned_message[:-len(suffix)]
            break

    # Clean up extra spaces
    cleaned_message = ' '.join(cleaned_message.split())

    # Check for description indicators (with, for, about, etc.)
    description_patterns = [
        r'^(.+?)\s+with\s+(.+)$',
        r'^(.+?)\s+for\s+(.+)$',
        r'^(.+?)\s+about\s+(.+)$',
        r'^(.+?)\s+regarding\s+(.+)$',
        r'^(.+?)\s+on\s+(.+)$',
    ]

    for pattern in description_patterns:
        match = re.match(pattern, cleaned_message)
        if match:
            title = match.group(1).strip()
            description = match.group(2).strip()
            return {'title': title, 'description': description}

    # No description found - entire cleaned message is the title
    return {'title': cleaned_message.strip(), 'description': None}


# ============================================================================
# Task Identifier Extraction
# ============================================================================

def extract_task_identifier(message: str) -> Dict[str, Any]:
    """
    Extract task identifier (ID or title) from natural language message.

    Args:
        message: User's message

    Returns:
        Dictionary with 'type' ('id' or 'title') and 'value'

    Examples:
        >>> extract_task_identifier("Mark task 5 as done")
        {'type': 'id', 'value': 5}

        >>> extract_task_identifier("Complete buy groceries")
        {'type': 'title', 'value': 'buy groceries'}

        >>> extract_task_identifier("Finish the presentation task")
        {'type': 'title', 'value': 'presentation'}
    """
    message_lower = message.lower().strip()

    # Try to extract task ID (number)
    # Patterns: "task 5", "task #5", "id 5", "#5", "number 5"
    id_patterns = [
        r'task\s+#?(\d+)',
        r'task\s+id\s+(\d+)',
        r'id\s+(\d+)',
        r'#(\d+)',
        r'number\s+(\d+)',
    ]

    for pattern in id_patterns:
        match = re.search(pattern, message_lower)
        if match:
            task_id = int(match.group(1))
            return {'type': 'id', 'value': task_id}

    # No ID found - try to extract task title
    # Remove completion keywords and common prefixes
    prefixes = [
        'complete task ',
        'complete the task ',
        'complete ',
        'mark task ',
        'mark the task ',
        'mark ',
        'mark as done ',
        'mark as complete ',
        'done with ',
        'finished with ',
        'finished ',
        'finish task ',
        'finish the task ',
        'finish ',
    ]

    cleaned_message = message_lower
    for prefix in prefixes:
        if cleaned_message.startswith(prefix):
            cleaned_message = cleaned_message[len(prefix):]
            break

    # Remove trailing "as done", "as complete", etc.
    suffixes = [
        ' as done',
        ' as complete',
        ' as completed',
        ' task',
        ' please',
    ]

    for suffix in suffixes:
        if cleaned_message.endswith(suffix):
            cleaned_message = cleaned_message[:-len(suffix)]

    # Extract the remaining text as title
    title = cleaned_message.strip()

    if title:
        return {'type': 'title', 'value': title}

    # No identifier found
    return {'type': 'unknown', 'value': None}


# ============================================================================
# Update Information Extraction
# ============================================================================

def extract_update_info(message: str) -> Dict[str, Any]:
    """
    Extract update information from natural language message.

    Args:
        message: User's message

    Returns:
        Dictionary with:
            - task_identifier: Dict with 'type' and 'value'
            - field_updates: Dict with 'title' and/or 'description' updates

    Examples:
        >>> extract_update_info("Update task 5 to buy almond milk")
        {
            'task_identifier': {'type': 'id', 'value': 5},
            'field_updates': {'title': 'buy almond milk', 'description': None}
        }

        >>> extract_update_info("Change the groceries task description to get organic items")
        {
            'task_identifier': {'type': 'title', 'value': 'groceries'},
            'field_updates': {'title': None, 'description': 'get organic items'}
        }
    """
    message_lower = message.lower().strip()

    # Extract task identifier first
    task_identifier = extract_task_identifier(message)

    # Determine what field is being updated
    field_updates = {'title': None, 'description': None}

    # Check if description is being updated
    description_patterns = [
        r'description to (.+)',
        r'description: (.+)',
        r'details to (.+)',
        r'add details? (.+)',
    ]

    for pattern in description_patterns:
        match = re.search(pattern, message_lower)
        if match:
            field_updates['description'] = match.group(1).strip()
            return {
                'task_identifier': task_identifier,
                'field_updates': field_updates
            }

    # Check for title update patterns
    title_patterns = [
        r'(?:update|change|modify|edit|rename)\s+(?:task\s+#?\d+|task|the\s+\w+\s+task)\s+to\s+(.+)',
        r'(?:update|change|modify|edit|rename)\s+(.+?)\s+to\s+(.+)',
    ]

    for pattern in title_patterns:
        match = re.search(pattern, message_lower)
        if match:
            # Extract the new title (last group)
            if match.lastindex >= 2:
                field_updates['title'] = match.group(2).strip()
            else:
                field_updates['title'] = match.group(1).strip()
            return {
                'task_identifier': task_identifier,
                'field_updates': field_updates
            }

    # Default: assume title update if no specific field mentioned
    # Extract content after update keyword
    update_keywords_pattern = r'(?:update|change|modify|edit|rename)\s+'
    rest_of_message = re.sub(update_keywords_pattern, '', message_lower, count=1)

    # Remove task identifier from rest of message
    if task_identifier['type'] == 'id':
        rest_of_message = re.sub(r'task\s+#?\d+', '', rest_of_message)
    elif task_identifier['type'] == 'title' and task_identifier['value']:
        rest_of_message = rest_of_message.replace(task_identifier['value'], '')

    # Remove common connectors
    rest_of_message = re.sub(r'^\s*(?:to|as|with)\s+', '', rest_of_message)
    rest_of_message = rest_of_message.strip()

    if rest_of_message:
        field_updates['title'] = rest_of_message

    return {
        'task_identifier': task_identifier,
        'field_updates': field_updates
    }


def extract_priority_update_info(message: str) -> Dict[str, Any]:
    """
    Extract task ID and new priority from a priority update message.

    Args:
        message: User's message like "Task #32 urgent priority" or "set task 5 to high"

    Returns:
        Dictionary with:
            - task_id: int or None
            - priority: str (low, medium, high, urgent)

    Examples:
        >>> extract_priority_update_info("Task #32 urgent priority")
        {'task_id': 32, 'priority': 'urgent'}

        >>> extract_priority_update_info("set task 5 priority to high")
        {'task_id': 5, 'priority': 'high'}
    """
    message_lower = message.lower().strip()

    # Extract task ID
    # Supports: task #23, task 23, task num 23, task number 23, task no 23, #23
    task_id = None
    task_id_match = re.search(r'task\s*(?:#|num|number|no\.?)?\s*(\d+)|#(\d+)', message_lower)
    if task_id_match:
        task_id = int(task_id_match.group(1) or task_id_match.group(2))

    # Extract priority
    priority = 'medium'  # default

    if 'urgent' in message_lower or 'asap' in message_lower:
        priority = 'urgent'
    elif 'high' in message_lower:
        priority = 'high'
    elif 'low' in message_lower:
        priority = 'low'
    elif 'medium' in message_lower:
        priority = 'medium'

    return {
        'task_id': task_id,
        'priority': priority
    }


# ============================================================================
# Priority Extraction
# ============================================================================

def extract_priority(message: str) -> str:
    """
    Extract priority level from natural language message.

    Args:
        message: User's message

    Returns:
        Priority level: "low", "medium", "high", or "urgent" (default: "medium")

    Examples:
        >>> extract_priority("Add buy milk - high priority")
        'high'

        >>> extract_priority("urgent: finish report by tomorrow")
        'urgent'

        >>> extract_priority("low priority task to clean desk")
        'low'
    """
    message_lower = message.lower().strip()

    # Check for urgent keywords
    urgent_keywords = ['urgent', 'asap', 'immediately', 'فوری', 'fori', 'zaruri']
    for keyword in urgent_keywords:
        if keyword in message_lower:
            return 'urgent'

    # Check for high priority keywords
    high_keywords = ['high priority', 'high', 'important', 'ضروری', 'zaroori', 'important hai']
    for keyword in high_keywords:
        if keyword in message_lower:
            return 'high'

    # Check for low priority keywords
    low_keywords = ['low priority', 'low', 'not urgent', 'kam zaroori', 'کم ضروری']
    for keyword in low_keywords:
        if keyword in message_lower:
            return 'low'

    # Default to medium if no priority mentioned
    return 'medium'


# ============================================================================
# Status Filter Extraction
# ============================================================================

def extract_status_filter(message: str) -> Optional[str]:
    """
    Extract status filter from natural language message.

    Args:
        message: User's message

    Returns:
        "completed", "pending", or None

    Examples:
        >>> extract_status_filter("Show my pending tasks")
        'pending'

        >>> extract_status_filter("List completed tasks")
        'completed'

        >>> extract_status_filter("Show all my tasks")
        None
    """
    message_lower = message.lower().strip()

    # Check for completed/done keywords
    completed_keywords = ['completed', 'done', 'finished', "what i've done", 'accomplished']
    for keyword in completed_keywords:
        if keyword in message_lower:
            return 'completed'

    # Check for pending/incomplete keywords
    pending_keywords = ['pending', 'incomplete', 'unfinished', 'todo', 'to do', 'not done', 'active']
    for keyword in pending_keywords:
        if keyword in message_lower:
            return 'pending'

    # No filter - return all tasks
    return None


# ============================================================================
# Task List Formatting
# ============================================================================

def format_task_list(tasks: List[Dict[str, Any]], status_filter: Optional[str] = None) -> str:
    """
    Format a list of tasks as a readable message with rich details.

    Args:
        tasks: List of task dictionaries
        status_filter: Optional status filter that was applied

    Returns:
        Formatted task list message with priority, descriptions, and dates

    Examples:
        >>> tasks = [{"id": 1, "title": "Buy milk", "completed": False, "priority": "high"}]
        >>> print(format_task_list(tasks))
        "Here are your tasks:\n1. ⭕ Buy milk 🔴 High"
    """
    from datetime import datetime

    if not tasks:
        if status_filter == "completed":
            return "You don't have any completed tasks yet."
        elif status_filter == "pending":
            return "You don't have any pending tasks. Great job! 🎉"
        else:
            return "You don't have any tasks yet. You can create one by saying 'Add task [description]'."

    # Build header
    if status_filter == "completed":
        header = "Here are your completed tasks:"
    elif status_filter == "pending":
        header = "Here are your pending tasks:"
    else:
        header = "Here are all your tasks:"

    # Format task list with rich details
    formatted_tasks = []
    for task in tasks:
        task_id = task.get("id")
        title = task.get("title", "Untitled")
        completed = task.get("completed", False)
        description = task.get("description")
        priority = task.get("priority", "medium")
        due_date = task.get("due_date")
        created_at = task.get("created_at")

        # Priority emoji
        priority_emoji = {
            "high": "🔴 High",
            "medium": "🟡 Medium",
            "low": "🟢 Low",
            "urgent": "🔥 Urgent"
        }.get(priority.lower() if isinstance(priority, str) else "medium", "🟡 Medium")

        # Build task string with actual task ID
        task_str = f"[#{task_id}] {title} — {priority_emoji}"

        # Add completion status only if completed
        if completed:
            task_str += " ✅"

        # Add description if available
        if description:
            task_str += f"\n   📝 {description}"

        # Add due date if available
        if due_date:
            try:
                if isinstance(due_date, str):
                    # Parse ISO format date
                    due_dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    due_str = due_dt.strftime("%b %d, %Y")
                else:
                    due_str = due_date.strftime("%b %d, %Y") if hasattr(due_date, 'strftime') else str(due_date)
                task_str += f"\n   📅 Due: {due_str}"
            except:
                pass

        # Add created date if available
        if created_at:
            try:
                if isinstance(created_at, str):
                    # Parse ISO format date
                    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    created_str = created_dt.strftime("%b %d, %Y")
                else:
                    created_str = created_at.strftime("%b %d, %Y") if hasattr(created_at, 'strftime') else str(created_at)
                task_str += f"\n   🕐 Created: {created_str}"
            except:
                pass

        formatted_tasks.append(task_str)

    return f"{header}\n\n" + "\n\n".join(formatted_tasks)


# ============================================================================
# Task Matching
# ============================================================================

def find_task_by_title(tasks: List[Dict[str, Any]], query_title: str) -> Optional[Dict[str, Any]]:
    """
    Find a task by title using fuzzy matching.

    Args:
        tasks: List of task dictionaries
        query_title: Title to search for (case-insensitive)

    Returns:
        Matching task or None if not found

    Examples:
        >>> tasks = [{"id": 1, "title": "Buy groceries", "completed": False}]
        >>> find_task_by_title(tasks, "groceries")
        {"id": 1, "title": "Buy groceries", "completed": False}
    """
    query_lower = query_title.lower().strip()

    # Try exact match first
    for task in tasks:
        task_title_lower = task.get("title", "").lower()
        if task_title_lower == query_lower:
            return task

    # Try partial match (query contains task title or vice versa)
    for task in tasks:
        task_title_lower = task.get("title", "").lower()
        if query_lower in task_title_lower or task_title_lower in query_lower:
            return task

    # No match found
    return None


# ============================================================================
# Confirmation Message Generation
# ============================================================================

def generate_confirmation(tool_result: Dict[str, Any], tool_name: str, tool_arguments: Dict[str, Any] = None) -> str:
    """
    Generate friendly TaskFlow AI confirmation message after tool execution.

    Args:
        tool_result: Result from MCP tool execution
        tool_name: Name of the tool that was executed
        tool_arguments: Original arguments passed to the tool (for priority, etc.)

    Returns:
        Friendly confirmation message (TaskFlow AI style)
    """
    if tool_name == "add_task":
        title = tool_result.get("title", "your task")
        task_id = tool_result.get("task_id", "")

        # Get priority from arguments
        priority = None
        if tool_arguments:
            priority = tool_arguments.get("priority", "medium")

        # Priority emoji mapping
        priority_emoji = {
            "urgent": "🔴",
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }.get(priority.lower() if priority else "medium", "🟡")

        # Build response with priority if not medium (default)
        if priority and priority.lower() != "medium":
            return f"Done 👍 I've added '{title}' {priority_emoji} with {priority.upper()} priority to your tasks."
        else:
            return f"Done 👍 I've added '{title}' to your tasks."

    elif tool_name == "complete_task":
        title = tool_result.get("title", "the task")
        task_id = tool_result.get("task_id", "")

        return f"Great job! I've marked '{title}' as completed. ✅"

    elif tool_name == "update_task":
        title = tool_result.get("title", "the task")
        task_id = tool_result.get("task_id", "")

        return f"Perfect! I've updated '{title}' successfully. 👌"

    elif tool_name == "delete_task":
        title = tool_result.get("title", "the task")
        task_id = tool_result.get("task_id", "")

        return f"Got it! I've removed '{title}' from your task list. 🗑️"

    # Default confirmation
    return f"All set! Task operation completed successfully. ✅"


# ============================================================================
# Agent Runner
# ============================================================================

class AgentRunner:
    """
    Agent runner for processing natural language task management requests.

    Integrates Gemini AI (via OpenAI SDK compatibility) with MCP tools for stateless conversation processing.
    """

    def __init__(self, user_id: UUID, mcp_client=None):
        """
        Initialize agent runner.

        Args:
            user_id: UUID of the user for this agent session
            mcp_client: Optional MCP client for tool execution
        """
        self.user_id = user_id
        self.mcp_client = mcp_client

    async def run(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Run agent to process user message with conversation history.

        Args:
            message: User's new message
            conversation_history: Previous messages in conversation
                                 (list of {role, content} dicts)

        Returns:
            Dictionary with:
                - response: AI assistant's response text
                - tool_calls: List of tool calls made (if any)

        Example:
            >>> agent = AgentRunner(user_id=123)
            >>> result = await agent.run(
            ...     message="Add buy milk",
            ...     conversation_history=[]
            ... )
            >>> print(result)
            {
                'response': "I've added 'buy milk' to your task list. Task ID: 1.",
                'tool_calls': [
                    {
                        'tool': 'add_task',
                        'arguments': {'user_id': 123, 'title': 'buy milk', 'description': None},
                        'result': {'task_id': 1, 'status': 'created', 'title': 'buy milk'}
                    }
                ]
            }
        """
        # Detect intent
        intent = detect_intent(message)

        tool_calls = []
        response_text = ""

        # Handle add_task intent
        if intent == "add_task":
            # Extract task information
            task_info = extract_task_info(message)

            # Extract priority from message
            priority = extract_priority(message)

            # Build tool call
            tool_arguments = {
                "user_id": str(self.user_id),  # Convert UUID to string for MCP
                "title": task_info["title"],
                "description": task_info["description"],
                "priority": priority,
            }

            # Execute tool (if MCP client available)
            if self.mcp_client:
                try:
                    logger.info(f"🔧 Calling MCP add_task with user_id: {self.user_id}, title: {task_info['title']}")
                    mcp_response = await self.mcp_client.call_tool(
                        "add_task",
                        tool_arguments
                    )
                    logger.info(f"✅ MCP Response: {mcp_response}")
                    # Extract data from MCP response structure: {success, message, data}
                    if isinstance(mcp_response, dict) and "data" in mcp_response:
                        tool_result = mcp_response["data"]
                    else:
                        tool_result = mcp_response
                    logger.info(f"📦 Extracted tool_result: {tool_result}")
                except Exception as e:
                    logger.error(f"❌ MCP call failed: {str(e)}")
                    tool_result = {
                        "error": str(e),
                        "status": "failed"
                    }
            else:
                # Mock result for testing without MCP client
                tool_result = {
                    "task_id": 1,
                    "status": "created",
                    "title": task_info["title"],
                }

            # Record tool call
            tool_calls.append({
                "tool": "add_task",
                "arguments": tool_arguments,
                "result": tool_result,
            })

            # Generate confirmation with tool_arguments for priority info
            response_text = generate_confirmation(tool_result, "add_task", tool_arguments)

        # Handle list_tasks intent
        elif intent == "list_tasks":
            # Extract status filter
            status_filter = extract_status_filter(message)

            # Build tool call
            tool_arguments = {
                "user_id": str(self.user_id),  # Convert UUID to string for MCP
                "status": status_filter,
            }

            # Execute tool (if MCP client available)
            if self.mcp_client:
                try:
                    tool_result = await self.mcp_client.call_tool(
                        "list_tasks",
                        tool_arguments
                    )
                except Exception as e:
                    tool_result = {
                        "error": str(e),
                        "status": "failed",
                        "tasks": []
                    }
            else:
                # Mock result for testing without MCP client
                tool_result = {
                    "status": "success",
                    "tasks": [],
                }

            # Record tool call
            tool_calls.append({
                "tool": "list_tasks",
                "arguments": tool_arguments,
                "result": tool_result,
            })

            # Format task list
            # MCP server returns tasks inside "data" object: {"success": true, "data": {"tasks": [...]}}
            data = tool_result.get("data", {})
            tasks = data.get("tasks", []) if isinstance(data, dict) else []
            response_text = format_task_list(tasks, status_filter)

        # Handle complete_task intent
        elif intent == "complete_task":
            # Extract task identifier
            task_identifier = extract_task_identifier(message)

            task_id = None

            # If identifier is task ID, use it directly
            if task_identifier["type"] == "id":
                task_id = task_identifier["value"]

            # If identifier is title, search for matching task
            elif task_identifier["type"] == "title":
                # First, list all pending tasks
                list_arguments = {
                    "user_id": str(self.user_id),  # Convert UUID to string for MCP
                    "status": "pending",  # Only search in pending tasks
                }

                # Execute list_tasks to find matching task
                if self.mcp_client:
                    try:
                        list_result = await self.mcp_client.call_tool(
                            "list_tasks",
                            list_arguments
                        )
                        # MCP server returns tasks inside "data" object
                        data = list_result.get("data", {})
                        tasks = data.get("tasks", []) if isinstance(data, dict) else []
                    except Exception as e:
                        tasks = []
                else:
                    tasks = []

                # Find matching task by title
                matching_task = find_task_by_title(tasks, task_identifier["value"])

                if matching_task:
                    task_id = matching_task.get("id")
                else:
                    # Task not found by title
                    response_text = f"I couldn't find a pending task matching '{task_identifier['value']}'. Please check your task list."

            # Unknown identifier type
            else:
                response_text = "I'm not sure which task you want to mark as complete. Please specify a task ID (e.g., 'task 5') or task title (e.g., 'buy groceries')."

            # If we have a task_id, complete the task
            if task_id:
                # Build tool call
                tool_arguments = {
                    "user_id": str(self.user_id),  # Convert UUID to string for MCP
                    "task_id": task_id,
                }

                # Execute tool (if MCP client available)
                if self.mcp_client:
                    try:
                        mcp_response = await self.mcp_client.call_tool(
                            "complete_task",
                            tool_arguments
                        )
                        # Extract data from MCP response structure: {success, message, data}
                        if isinstance(mcp_response, dict) and "data" in mcp_response:
                            tool_result = mcp_response["data"]
                        else:
                            tool_result = mcp_response
                    except Exception as e:
                        # Handle task not found or other errors
                        error_msg = str(e)
                        if "not found" in error_msg.lower():
                            tool_result = {
                                "error": "Task not found",
                                "status": "failed"
                            }
                            response_text = f"I couldn't find task #{task_id}. It may have been deleted or doesn't belong to you."
                        else:
                            tool_result = {
                                "error": error_msg,
                                "status": "failed"
                            }
                            response_text = f"I encountered an error completing the task: {error_msg}"
                else:
                    # Mock result for testing without MCP client
                    tool_result = {
                        "task_id": task_id,
                        "status": "completed",
                        "title": "Sample task",
                    }

                # Record tool call
                tool_calls.append({
                    "tool": "complete_task",
                    "arguments": tool_arguments,
                    "result": tool_result,
                })

                # Generate confirmation if successful
                if tool_result.get("status") != "failed" and not response_text:
                    response_text = generate_confirmation(tool_result, "complete_task")

        # Handle update_task intent
        elif intent == "update_task":
            # Extract update information
            update_info = extract_update_info(message)
            task_identifier = update_info["task_identifier"]
            field_updates = update_info["field_updates"]

            task_id = None

            # If identifier is task ID, use it directly
            if task_identifier["type"] == "id":
                task_id = task_identifier["value"]

            # If identifier is title, search for matching task
            elif task_identifier["type"] == "title":
                # First, list all tasks
                list_arguments = {
                    "user_id": str(self.user_id),  # Convert UUID to string for MCP
                    "status": None,  # Search all tasks
                }

                # Execute list_tasks to find matching task
                if self.mcp_client:
                    try:
                        list_result = await self.mcp_client.call_tool(
                            "list_tasks",
                            list_arguments
                        )
                        # MCP server returns tasks inside "data" object
                        data = list_result.get("data", {})
                        tasks = data.get("tasks", []) if isinstance(data, dict) else []
                    except Exception as e:
                        tasks = []
                else:
                    tasks = []

                # Find matching task by title
                matching_task = find_task_by_title(tasks, task_identifier["value"])

                if matching_task:
                    task_id = matching_task.get("id")
                else:
                    # Task not found by title
                    response_text = f"I couldn't find a task matching '{task_identifier['value']}'. Please check your task list."

            # Unknown identifier type
            else:
                response_text = "I'm not sure which task you want to update. Please specify a task ID (e.g., 'task 5') or task title (e.g., 'groceries')."

            # Check if we have updates to apply
            if not field_updates.get("title") and not field_updates.get("description"):
                response_text = "I'm not sure what you want to update. Please specify a new title or description."

            # If we have a task_id and updates, perform the update
            if task_id and (field_updates.get("title") or field_updates.get("description")):
                # Build tool call
                tool_arguments = {
                    "user_id": str(self.user_id),  # Convert UUID to string for MCP
                    "task_id": task_id,
                    "title": field_updates.get("title"),
                    "description": field_updates.get("description"),
                }

                # Execute tool (if MCP client available)
                if self.mcp_client:
                    try:
                        mcp_response = await self.mcp_client.call_tool(
                            "update_task",
                            tool_arguments
                        )
                        # Extract data from MCP response structure: {success, message, data}
                        if isinstance(mcp_response, dict) and "data" in mcp_response:
                            tool_result = mcp_response["data"]
                        else:
                            tool_result = mcp_response
                    except Exception as e:
                        # Handle task not found or other errors
                        error_msg = str(e)
                        if "not found" in error_msg.lower():
                            tool_result = {
                                "error": "Task not found",
                                "status": "failed"
                            }
                            response_text = f"I couldn't find task #{task_id}. It may have been deleted or doesn't belong to you."
                        elif "no changes" in error_msg.lower():
                            tool_result = {
                                "error": "No changes",
                                "status": "failed"
                            }
                            response_text = "No changes were specified. Please provide a new title or description."
                        else:
                            tool_result = {
                                "error": error_msg,
                                "status": "failed"
                            }
                            response_text = f"I encountered an error updating the task: {error_msg}"
                else:
                    # Mock result for testing without MCP client
                    tool_result = {
                        "task_id": task_id,
                        "status": "updated",
                        "title": field_updates.get("title") or "Sample task",
                    }

                # Record tool call
                tool_calls.append({
                    "tool": "update_task",
                    "arguments": tool_arguments,
                    "result": tool_result,
                })

                # Generate confirmation if successful
                if tool_result.get("status") != "failed" and not response_text:
                    response_text = generate_confirmation(tool_result, "update_task")

        # Handle set_priority intent
        elif intent == "set_priority":
            # Extract priority update info
            priority_info = extract_priority_update_info(message)
            task_id = priority_info["task_id"]
            new_priority = priority_info["priority"]

            if not task_id:
                response_text = "I'm not sure which task you want to update. Please specify a task ID like 'Task #5 high priority'."
            else:
                # Build tool call for update_task with priority
                tool_arguments = {
                    "user_id": str(self.user_id),
                    "task_id": task_id,
                    "priority": new_priority,
                }

                # Execute tool (if MCP client available)
                if self.mcp_client:
                    try:
                        mcp_response = await self.mcp_client.call_tool(
                            "update_task",
                            tool_arguments
                        )
                        # Extract data from MCP response
                        if isinstance(mcp_response, dict) and "data" in mcp_response:
                            tool_result = mcp_response["data"]
                        else:
                            tool_result = mcp_response
                    except Exception as e:
                        error_msg = str(e)
                        tool_result = {
                            "error": error_msg,
                            "status": "failed"
                        }
                        response_text = f"I couldn't update the priority: {error_msg}"
                else:
                    # Mock result for testing
                    tool_result = {
                        "task_id": task_id,
                        "status": "updated",
                        "priority": new_priority,
                    }

                # Record tool call
                tool_calls.append({
                    "tool": "update_task",
                    "arguments": tool_arguments,
                    "result": tool_result,
                })

                # Generate confirmation if successful
                if tool_result.get("status") != "failed" and not response_text:
                    priority_emoji = {
                        "urgent": "🔥",
                        "high": "🔴",
                        "medium": "🟡",
                        "low": "🟢"
                    }.get(new_priority, "🟡")
                    response_text = f"Done! Task #{task_id} priority updated to {priority_emoji} {new_priority.capitalize()}."

        # Handle delete_task intent
        elif intent == "delete_task":
            # Extract task identifier
            task_identifier = extract_task_identifier(message)

            task_id = None

            # If identifier is task ID, use it directly
            if task_identifier["type"] == "id":
                task_id = task_identifier["value"]

            # If identifier is title, search for matching task
            elif task_identifier["type"] == "title":
                # First, list all tasks
                list_arguments = {
                    "user_id": str(self.user_id),  # Convert UUID to string for MCP
                    "status": None,  # Search all tasks
                }

                # Execute list_tasks to find matching task
                if self.mcp_client:
                    try:
                        list_result = await self.mcp_client.call_tool(
                            "list_tasks",
                            list_arguments
                        )
                        # MCP server returns tasks inside "data" object
                        data = list_result.get("data", {})
                        tasks = data.get("tasks", []) if isinstance(data, dict) else []
                    except Exception as e:
                        tasks = []
                else:
                    tasks = []

                # Find matching task by title
                matching_task = find_task_by_title(tasks, task_identifier["value"])

                if matching_task:
                    task_id = matching_task.get("id")
                else:
                    # Task not found by title
                    response_text = f"I couldn't find a task matching '{task_identifier['value']}'. Please check your task list."

            # Unknown identifier type
            else:
                response_text = "I'm not sure which task you want to delete. Please specify a task ID (e.g., 'task 5') or task title (e.g., 'groceries')."

            # If we have a task_id, delete the task
            if task_id:
                # Build tool call
                tool_arguments = {
                    "user_id": str(self.user_id),  # Convert UUID to string for MCP
                    "task_id": task_id,
                }

                # Execute tool (if MCP client available)
                if self.mcp_client:
                    try:
                        mcp_response = await self.mcp_client.call_tool(
                            "delete_task",
                            tool_arguments
                        )
                        # Extract data from MCP response structure: {success, message, data}
                        if isinstance(mcp_response, dict) and "data" in mcp_response:
                            tool_result = mcp_response["data"]
                        else:
                            tool_result = mcp_response
                    except Exception as e:
                        # Handle task not found or other errors
                        error_msg = str(e)
                        if "not found" in error_msg.lower():
                            tool_result = {
                                "error": "Task not found",
                                "status": "failed"
                            }
                            response_text = f"I couldn't find task #{task_id}. It may have been deleted or doesn't belong to you."
                        else:
                            tool_result = {
                                "error": error_msg,
                                "status": "failed"
                            }
                            response_text = f"I encountered an error deleting the task: {error_msg}"
                else:
                    # Mock result for testing without MCP client
                    tool_result = {
                        "task_id": task_id,
                        "status": "deleted",
                        "title": "Sample task",
                    }

                # Record tool call
                tool_calls.append({
                    "tool": "delete_task",
                    "arguments": tool_arguments,
                    "result": tool_result,
                })

                # Generate confirmation if successful
                if tool_result.get("status") != "failed" and not response_text:
                    response_text = generate_confirmation(tool_result, "delete_task")

        else:
            # General conversation - use OpenAI API
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]

            # Add conversation history
            for msg in conversation_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            # Add new user message
            messages.append({
                "role": "user",
                "content": message
            })

            try:
                # Call Gemini API via OpenAI SDK compatibility with retry logic (T128)
                def make_openai_call():
                    return openai_client.chat.completions.create(
                        model="gemini-2.5-flash",  # or gemini-1.5-pro for better quality
                        messages=messages,
                        temperature=0.7,
                        max_tokens=500,
                    )

                completion = retry_with_exponential_backoff(make_openai_call)
                response_text = completion.choices[0].message.content

            except Exception as e:
                logger.error(f"Gemini API call failed after retries: {str(e)}")
                response_text = "I'm sorry, I encountered an error processing your request. Please try again."

        return {
            "response": response_text,
            "tool_calls": tool_calls,
        }


# ============================================================================
# Convenience Functions
# ============================================================================

async def process_message(
    user_id: int,
    message: str,
    conversation_history: List[Dict[str, str]],
    mcp_client=None,
) -> Dict[str, Any]:
    """
    Process a user message through the AI agent.

    Convenience function for creating and running an agent in one call.

    Args:
        user_id: ID of the user
        message: User's message
        conversation_history: Previous conversation messages
        mcp_client: Optional MCP client

    Returns:
        Agent response with 'response' and 'tool_calls'
    """
    agent = AgentRunner(user_id=user_id, mcp_client=mcp_client)
    return await agent.run(message, conversation_history)
