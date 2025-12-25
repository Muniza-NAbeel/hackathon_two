"""
Voice Command Module - Phase I Todo Application

Provides voice command parsing and validation for natural language task operations.
Pure function implementations - no direct CLI I/O, uses regex for robust parsing.

Skills:
    - parse_voice_command: Convert spoken text to structured task action
    - validate_voice_command: Validate parsed commands and ensure required args

Maps to:
    - VFR-001: Natural language command parsing
    - VFR-002: Support for basic, intermediate, and advanced voice commands
    - VFR-003: Graceful fallback when voice recognition unavailable
"""

import re
from datetime import datetime, timedelta
from typing import Any

from src.models import Priority, Recurrence, VALID_TAGS


# =============================================================================
# Constants: Filler Words and Natural Date Patterns
# =============================================================================

FILLER_WORDS = {
    "um", "uh", "like", "please", "can you", "could you",
    "i want to", "i need to", "i'd like to", "let's"
}

NATURAL_DATE_PATTERNS = {
    "tomorrow": timedelta(days=1),
    "today": timedelta(days=0),
    "next week": timedelta(weeks=1),
    "next month": timedelta(days=30),
}


# =============================================================================
# Skill 1: parse_voice_command
# =============================================================================

def parse_voice_command(command_str: str) -> tuple[str, dict[str, Any]]:
    """
    Convert raw spoken text into a structured task action and arguments.

    This is a pure function - no CLI I/O, only parsing logic.
    Handles basic, intermediate, and advanced voice commands.

    Args:
        command_str: The raw voice command string (e.g., "Add task Buy milk with High priority")

    Returns:
        Tuple of (action: str, args: dict) where:
        - action: One of "add", "complete", "delete", "list", "search", "sort",
                  "filter", "update_priority", "update_tags", "update_due_date",
                  "update_recurrence", "unknown"
        - args: Dictionary of parsed arguments for the action

    Supported Commands:
        Basic:
            - "Add task [title]"
            - "Mark task [id] complete" / "Complete task [id]"
            - "Delete task [id]"
            - "List tasks" / "Show tasks" / "Show all tasks"

        Intermediate:
            - "Add task [title] with [High/Medium/Low] priority"
            - "Add task [title] in [tag]" / "Add task [title] tagged [tag]"
            - "Search tasks [keyword]" / "Find tasks [keyword]"
            - "Sort tasks by [priority/title/created/status]"
            - "Filter tasks by status [complete/incomplete]"
            - "Filter tasks by priority [High/Medium/Low]"
            - "Filter tasks by tag [tag]"
            - "Update task [id] priority to [High/Medium/Low]"
            - "Update task [id] tags to [tag1, tag2]"

        Advanced:
            - "Add recurring task [title] [daily/weekly/monthly]"
            - "Set due date for task [id] as [YYYY-MM-DD HH:MM]"
            - "Set due date for task [id] as [tomorrow/next week/in 3 days]"
            - "Update task [id] recurrence to [daily/weekly/monthly/none]"

    Examples:
        >>> parse_voice_command("Add task Buy groceries")
        ('add', {'title': 'Buy groceries'})

        >>> parse_voice_command("Add task Meeting with High priority in Work")
        ('add', {'title': 'Meeting', 'priority': <Priority.HIGH: 1>, 'tags': ['Work']})

        >>> parse_voice_command("Mark task 5 complete")
        ('complete', {'task_id': 5})

        >>> parse_voice_command("Search tasks groceries")
        ('search', {'keyword': 'groceries'})

        >>> parse_voice_command("Add recurring task Exercise weekly")
        ('add', {'title': 'Exercise', 'recurrence': <Recurrence.WEEKLY: 7>})

        >>> parse_voice_command("Set due date for task 3 as tomorrow")
        ('update_due_date', {'task_id': 3, 'due_date': <datetime object>})

    Maps to: VFR-001, VFR-002
    """
    # Normalize and clean the command
    command = _clean_command(command_str)

    if not command:
        return ("unknown", {})

    # Try each command pattern in order of specificity (most specific first)

    # 1. Advanced: Set due date with natural language
    match = re.search(r"set due date (?:for )?task (\d+) (?:as |to )(.+)", command, re.IGNORECASE)
    if match:
        task_id = int(match.group(1))
        date_str = match.group(2).strip()
        due_date = _parse_natural_date(date_str)
        return ("update_due_date", {"task_id": task_id, "due_date": due_date})

    # 2. Advanced: Update task recurrence
    match = re.search(r"update task (\d+) recurrence to (daily|weekly|monthly|none)", command, re.IGNORECASE)
    if match:
        task_id = int(match.group(1))
        recurrence_str = match.group(2).lower()
        recurrence = _parse_recurrence(recurrence_str)
        return ("update_recurrence", {"task_id": task_id, "recurrence": recurrence})

    # 3. Intermediate: Update task priority
    match = re.search(r"update task (\d+) priority to (high|medium|low)", command, re.IGNORECASE)
    if match:
        task_id = int(match.group(1))
        priority_str = match.group(2)
        priority = _parse_priority(priority_str)
        return ("update_priority", {"task_id": task_id, "priority": priority})

    # 4. Intermediate: Update task tags
    match = re.search(r"update task (\d+) tags? to (.+)", command, re.IGNORECASE)
    if match:
        task_id = int(match.group(1))
        tags_str = match.group(2).strip()
        tags = _parse_tags(tags_str)
        return ("update_tags", {"task_id": task_id, "tags": tags})

    # 5. Advanced: Add recurring task
    match = re.search(r"add recurring task (.+?) (daily|weekly|monthly)", command, re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        recurrence_str = match.group(2).lower()
        recurrence = _parse_recurrence(recurrence_str)
        return ("add", {"title": title, "recurrence": recurrence})

    # 6. Intermediate: Add task with priority and/or tags
    # Pattern: "Add task [title] with [priority] priority in/tagged [tags]"
    match = re.search(
        r"add task (.+?)(?:\s+with\s+(high|medium|low)\s+priority)?(?:\s+(?:in|tagged)\s+(.+))?$",
        command,
        re.IGNORECASE
    )
    if match and match.group(1):
        title = match.group(1).strip()
        args = {"title": title}

        # Extract priority if present
        if match.group(2):
            args["priority"] = _parse_priority(match.group(2))

        # Extract tags if present
        if match.group(3):
            args["tags"] = _parse_tags(match.group(3))

        return ("add", args)

    # 7. Basic: Add task (simple)
    match = re.search(r"add task (.+)", command, re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        return ("add", {"title": title})

    # 8. Basic: Complete/Mark task as done
    match = re.search(r"(?:mark task|complete task|task) (\d+) (?:complete|done|as complete|as done)", command, re.IGNORECASE)
    if match:
        task_id = int(match.group(1))
        return ("complete", {"task_id": task_id})

    # 9. Basic: Delete task
    match = re.search(r"delete task (\d+)", command, re.IGNORECASE)
    if match:
        task_id = int(match.group(1))
        return ("delete", {"task_id": task_id})

    # 10. Intermediate: Search/Find tasks
    match = re.search(r"(?:search|find) tasks? (.+)", command, re.IGNORECASE)
    if match:
        keyword = match.group(1).strip()
        return ("search", {"keyword": keyword})

    # 11. Intermediate: Sort tasks
    match = re.search(r"sort tasks? by (priority|title|created|status)", command, re.IGNORECASE)
    if match:
        sort_by = match.group(1).lower()
        return ("sort", {"by": sort_by})

    # 12. Intermediate: Filter tasks by status
    match = re.search(r"filter tasks? by status (complete|incomplete)", command, re.IGNORECASE)
    if match:
        status_str = match.group(1).lower()
        status = True if status_str == "complete" else False
        return ("filter", {"status": status})

    # 13. Intermediate: Filter tasks by priority
    match = re.search(r"filter tasks? by priority (high|medium|low)", command, re.IGNORECASE)
    if match:
        priority = _parse_priority(match.group(1))
        return ("filter", {"priority": priority})

    # 14. Intermediate: Filter tasks by tag
    match = re.search(r"filter tasks? by tag (.+)", command, re.IGNORECASE)
    if match:
        tag = match.group(1).strip().capitalize()
        return ("filter", {"tag": tag})

    # 15. Basic: List/Show tasks
    if re.search(r"(?:list|show)(?: all)? tasks?", command, re.IGNORECASE):
        return ("list", {})

    # Unknown command
    return ("unknown", {})


# =============================================================================
# Skill 2: validate_voice_command
# =============================================================================

def validate_voice_command(action: str, args: dict[str, Any]) -> tuple[bool, str | None]:
    """
    Validate parsed voice commands and ensure required arguments exist.

    This is a pure function - no CLI I/O, only validation logic.

    Args:
        action: The parsed action (e.g., "add", "complete", "delete")
        args: The parsed arguments dictionary

    Returns:
        Tuple of (is_valid: bool, error_message: str | None)
        - is_valid: True if command is valid, False otherwise
        - error_message: None if valid, descriptive error message if invalid

    Validation Rules:
        - "add": Requires 'title' (non-empty string)
        - "complete": Requires 'task_id' (positive integer)
        - "delete": Requires 'task_id' (positive integer)
        - "search": Requires 'keyword' (non-empty string)
        - "update_priority": Requires 'task_id' and 'priority'
        - "update_tags": Requires 'task_id' and 'tags'
        - "update_due_date": Requires 'task_id' and 'due_date'
        - "update_recurrence": Requires 'task_id' and 'recurrence'
        - "list", "sort", "filter": No required args (optional filters)
        - "unknown": Always invalid

    Examples:
        >>> validate_voice_command("add", {"title": "Buy milk"})
        (True, None)

        >>> validate_voice_command("add", {})
        (False, "Missing required argument: 'title'")

        >>> validate_voice_command("complete", {"task_id": 5})
        (True, None)

        >>> validate_voice_command("complete", {})
        (False, "Missing required argument: 'task_id'")

        >>> validate_voice_command("unknown", {})
        (False, "Unknown action: 'unknown'")

    Maps to: VFR-001
    """
    # Unknown action is always invalid
    if action == "unknown":
        return (False, "Unknown action: 'unknown'. Could not parse command.")

    # Validate based on action type
    if action == "add":
        if "title" not in args:
            return (False, "Missing required argument: 'title'")
        if not args["title"] or not args["title"].strip():
            return (False, "Task title cannot be empty")
        return (True, None)

    elif action == "complete":
        if "task_id" not in args:
            return (False, "Missing required argument: 'task_id'")
        if not isinstance(args["task_id"], int) or args["task_id"] <= 0:
            return (False, "Task ID must be a positive integer")
        return (True, None)

    elif action == "delete":
        if "task_id" not in args:
            return (False, "Missing required argument: 'task_id'")
        if not isinstance(args["task_id"], int) or args["task_id"] <= 0:
            return (False, "Task ID must be a positive integer")
        return (True, None)

    elif action == "search":
        if "keyword" not in args:
            return (False, "Missing required argument: 'keyword'")
        if not args["keyword"] or not args["keyword"].strip():
            return (False, "Search keyword cannot be empty")
        return (True, None)

    elif action == "update_priority":
        if "task_id" not in args:
            return (False, "Missing required argument: 'task_id'")
        if "priority" not in args:
            return (False, "Missing required argument: 'priority'")
        if not isinstance(args["task_id"], int) or args["task_id"] <= 0:
            return (False, "Task ID must be a positive integer")
        if not isinstance(args["priority"], Priority):
            return (False, "Priority must be a valid Priority enum value")
        return (True, None)

    elif action == "update_tags":
        if "task_id" not in args:
            return (False, "Missing required argument: 'task_id'")
        if "tags" not in args:
            return (False, "Missing required argument: 'tags'")
        if not isinstance(args["task_id"], int) or args["task_id"] <= 0:
            return (False, "Task ID must be a positive integer")
        if not isinstance(args["tags"], list):
            return (False, "Tags must be a list")
        return (True, None)

    elif action == "update_due_date":
        if "task_id" not in args:
            return (False, "Missing required argument: 'task_id'")
        if "due_date" not in args:
            return (False, "Missing required argument: 'due_date'")
        if not isinstance(args["task_id"], int) or args["task_id"] <= 0:
            return (False, "Task ID must be a positive integer")
        # due_date can be None or datetime
        if args["due_date"] is not None and not isinstance(args["due_date"], datetime):
            return (False, "Due date must be a datetime object or None")
        return (True, None)

    elif action == "update_recurrence":
        if "task_id" not in args:
            return (False, "Missing required argument: 'task_id'")
        if "recurrence" not in args:
            return (False, "Missing required argument: 'recurrence'")
        if not isinstance(args["task_id"], int) or args["task_id"] <= 0:
            return (False, "Task ID must be a positive integer")
        if not isinstance(args["recurrence"], Recurrence):
            return (False, "Recurrence must be a valid Recurrence enum value")
        return (True, None)

    elif action in ("list", "sort", "filter"):
        # These actions have optional arguments, so always valid
        return (True, None)

    # Unrecognized action (shouldn't happen if parse_voice_command is correct)
    return (False, f"Unsupported action: '{action}'")


# =============================================================================
# Helper Functions (Internal)
# =============================================================================

def _clean_command(command_str: str) -> str:
    """
    Clean and normalize a voice command string.

    Removes filler words, extra whitespace, and normalizes case.

    Args:
        command_str: Raw voice command string

    Returns:
        Cleaned command string in lowercase

    Example:
        >>> _clean_command("Um, please add task, like, Buy milk")
        'add task buy milk'
    """
    if not command_str:
        return ""

    # Convert to lowercase
    command = command_str.lower().strip()

    # Remove filler words (case-insensitive)
    for filler in FILLER_WORDS:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(filler) + r'\b'
        command = re.sub(pattern, '', command, flags=re.IGNORECASE)

    # Remove extra whitespace and commas
    command = re.sub(r'[,;]+', ' ', command)
    command = re.sub(r'\s+', ' ', command).strip()

    return command


def _parse_priority(priority_str: str) -> Priority:
    """
    Parse a priority string into a Priority enum.

    Args:
        priority_str: Priority string ("high", "medium", "low", case-insensitive)

    Returns:
        Priority enum value

    Example:
        >>> _parse_priority("high")
        <Priority.HIGH: 1>
        >>> _parse_priority("Medium")
        <Priority.MEDIUM: 2>
    """
    priority_map = {
        "high": Priority.HIGH,
        "medium": Priority.MEDIUM,
        "low": Priority.LOW,
    }
    return priority_map.get(priority_str.lower(), Priority.MEDIUM)


def _parse_recurrence(recurrence_str: str) -> Recurrence:
    """
    Parse a recurrence string into a Recurrence enum.

    Args:
        recurrence_str: Recurrence string ("daily", "weekly", "monthly", "none", case-insensitive)

    Returns:
        Recurrence enum value

    Example:
        >>> _parse_recurrence("weekly")
        <Recurrence.WEEKLY: 7>
        >>> _parse_recurrence("none")
        <Recurrence.NONE: 0>
    """
    recurrence_map = {
        "none": Recurrence.NONE,
        "daily": Recurrence.DAILY,
        "weekly": Recurrence.WEEKLY,
        "monthly": Recurrence.MONTHLY,
    }
    return recurrence_map.get(recurrence_str.lower(), Recurrence.NONE)


def _parse_tags(tags_str: str) -> list[str]:
    """
    Parse a tags string into a list of valid tags.

    Args:
        tags_str: Tags string (comma or space separated)

    Returns:
        List of valid, capitalized tags

    Example:
        >>> _parse_tags("work, home")
        ['Work', 'Home']
        >>> _parse_tags("Shopping Health Finance")
        ['Shopping', 'Health', 'Finance']
        >>> _parse_tags("invalid work")
        ['Work']
    """
    # Split by comma or whitespace
    tag_candidates = re.split(r'[,\s]+', tags_str)

    # Validate and capitalize
    valid_tags = []
    for tag in tag_candidates:
        tag = tag.strip().capitalize()
        if tag in VALID_TAGS:
            valid_tags.append(tag)

    return valid_tags


def _parse_natural_date(date_str: str) -> datetime | None:
    """
    Parse a natural language date string into a datetime object.

    Supports:
        - Natural language: "tomorrow", "today", "next week", "next month"
        - Relative: "in 3 days", "in 2 weeks", "in 5 hours"
        - Absolute: "YYYY-MM-DD", "YYYY-MM-DD HH:MM"

    Args:
        date_str: Date string to parse

    Returns:
        Datetime object or None if parsing fails

    Examples:
        >>> _parse_natural_date("tomorrow")
        <datetime for tomorrow>
        >>> _parse_natural_date("in 3 days")
        <datetime 3 days from now>
        >>> _parse_natural_date("2025-12-25")
        <datetime for 2025-12-25>
        >>> _parse_natural_date("2025-12-25 14:30")
        <datetime for 2025-12-25 14:30>
    """
    date_str = date_str.lower().strip()

    # 1. Natural language patterns
    if date_str in NATURAL_DATE_PATTERNS:
        delta = NATURAL_DATE_PATTERNS[date_str]
        return datetime.now() + delta

    # 2. Relative patterns: "in X days/weeks/hours/minutes"
    match = re.match(r"in (\d+) (day|days|week|weeks|hour|hours|minute|minutes)", date_str)
    if match:
        value = int(match.group(1))
        unit = match.group(2).rstrip('s')  # Remove plural 's'

        if unit == "day":
            return datetime.now() + timedelta(days=value)
        elif unit == "week":
            return datetime.now() + timedelta(weeks=value)
        elif unit == "hour":
            return datetime.now() + timedelta(hours=value)
        elif unit == "minute":
            return datetime.now() + timedelta(minutes=value)

    # 3. Absolute date formats
    # Try "YYYY-MM-DD HH:MM" first
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except ValueError:
        pass

    # Try "YYYY-MM-DD" (date only, time defaults to 00:00)
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        pass

    # Could not parse
    return None


# =============================================================================
# Additional Functions (Voice Input Placeholders)
# =============================================================================

def listen_command() -> str:
    """
    Placeholder for voice input functionality.

    In a full implementation, this would use speech recognition libraries
    (e.g., SpeechRecognition, Google Speech API, etc.) to capture voice input.

    For now, falls back to text input.

    Returns:
        Voice command as text string

    Maps to: VFR-003
    """
    # Graceful fallback to text input when voice recognition is unavailable
    print("Voice recognition unavailable. Using text input fallback.")
    print("Enter your command: ", end="")
    return input().strip()


def check_voice_available() -> bool:
    """
    Check if speech recognition capabilities are available.

    In a full implementation, this would check for:
        - Microphone hardware availability
        - Speech recognition library installation
        - Required permissions

    Returns:
        True if voice recognition is available, False otherwise

    Maps to: VFR-003
    """
    try:
        # Try to import speech recognition library
        import speech_recognition as sr

        # Try to initialize recognizer
        recognizer = sr.Recognizer()

        # Try to access microphone
        with sr.Microphone() as source:
            pass

        return True
    except (ImportError, OSError, AttributeError):
        # Library not installed, microphone not available, or other error
        return False
