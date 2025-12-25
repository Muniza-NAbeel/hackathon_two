"""
Console Menu and Input Handlers - Phase I Todo Application

Provides the console UI including menu display, input validation,
and display formatting for the Todo application.
Use UV virtual environment for Python 3.13+ dependencies.

Maps to:
    - FR-001: Display interactive main menu with numbered options
    - FR-007: Display tasks with visual status indicators
    - FR-009: Handle invalid inputs with clear error messages
    - FR-010: Allow return to main menu after each operation
    - FR-011: Confirm before permanently deleting a task
    - FR-012: Trim leading and trailing whitespace from inputs
    - FR-013: Prevent creating tasks with empty titles
    - FR-014: Display friendly message when viewing empty task list
"""

from datetime import datetime

from src import MAX_TITLE_LENGTH, MAX_DESCRIPTION_LENGTH
from src.models import Task, Priority, Recurrence, VALID_TAGS
from src.storage import TaskStorage
from src.ui import (
    console,
    display_menu,
    print_error,
    print_warning,
    print_success,
    print_info,
    print_section_header,
    print_tasks_table,
    print_task_details,
    print_no_tasks,
    print_stats,
    prompt_input,
    prompt_confirm,
    wait_for_enter,
    display_priority_menu,
    display_tags_menu,
    display_filter_menu,
    display_sort_menu,
    display_status_filter_menu,
    print_search_results,
    print_filter_results,
    print_sort_results,
    display_recurrence_menu,
    display_due_date_prompt,
    print_reminders_panel,
    print_recurring_task_created,
)
from src.voice import (
    parse_voice_command,
    validate_voice_command,
    check_voice_available,
)


# =============================================================================
# Input Validation Helpers (T006)
# =============================================================================


# Re-export display_menu and wait_for_enter for backwards compatibility
__all__ = [
    "display_menu",
    "wait_for_enter",
    "get_menu_choice",
    "handle_view_tasks",
    "handle_add_task",
    "handle_toggle_completion",
    "handle_update_task",
    "handle_delete_task",
    "handle_search_tasks",
    "handle_filter_tasks",
    "handle_sort_tasks",
    "handle_add_task_with_options",
    "handle_reminders",
    "handle_toggle_with_recurrence",
    "handle_voice_command",
]


def validate_menu_choice(choice: str) -> tuple[bool, str]:
    """
    Validate menu choice input is a number 0-9 or 'V' for voice.

    Args:
        choice: The user's menu input (string).

    Returns:
        Tuple of (is_valid, error_message).
        If valid: (True, "")
        If invalid: (False, "error description")

    Maps to: FR-001, FR-009, VFR-001
    """
    choice = choice.strip().upper()
    if not choice:
        return False, "Please enter a choice (0-9 or V)."
    # Accept 'V' for voice command
    if choice == "V":
        return True, ""
    if not choice.isdigit():
        return False, "Please enter a number (0-9) or V for voice."
    if int(choice) < 0 or int(choice) > 9:
        return False, "Please enter a number between 0 and 9."
    return True, ""


def validate_task_id(input_str: str) -> tuple[bool, int, str]:
    """
    Validate task ID input is a positive integer.

    Args:
        input_str: The user's task ID input (string).

    Returns:
        Tuple of (is_valid, task_id, error_message).
        If valid: (True, parsed_id, "")
        If invalid: (False, 0, "error description")

    Maps to: FR-008, FR-009
    """
    input_str = input_str.strip()
    if not input_str:
        return False, 0, "Please enter a task ID."
    try:
        task_id = int(input_str)
        if task_id < 1:
            return False, 0, "Task ID must be a positive number."
        return True, task_id, ""
    except ValueError:
        return False, 0, "Please enter a valid number for task ID."


def sanitize_title(title: str) -> tuple[str, str]:
    """
    Sanitize title input by trimming whitespace and truncating.

    Args:
        title: The raw title input.

    Returns:
        Tuple of (sanitized_title, warning_message).
        warning_message is empty if no truncation occurred.

    Maps to: FR-005, FR-012
    """
    title = title.strip()
    warning = ""
    if len(title) > MAX_TITLE_LENGTH:
        title = title[:MAX_TITLE_LENGTH]
        warning = f"Title truncated to {MAX_TITLE_LENGTH} characters."
    return title, warning


def sanitize_description(description: str) -> tuple[str, str]:
    """
    Sanitize description input by trimming whitespace and truncating.

    Args:
        description: The raw description input.

    Returns:
        Tuple of (sanitized_description, warning_message).
        warning_message is empty if no truncation occurred.

    Maps to: FR-005, FR-012
    """
    description = description.strip()
    warning = ""
    if len(description) > MAX_DESCRIPTION_LENGTH:
        description = description[:MAX_DESCRIPTION_LENGTH]
        warning = f"Description truncated to {MAX_DESCRIPTION_LENGTH} characters."
    return description, warning


# =============================================================================
# Menu Display (T008)
# =============================================================================


def get_menu_choice() -> str:
    """
    Prompt for and validate menu choice.

    Re-prompts until valid input (0-9 or V) is received.

    Returns:
        Valid menu choice as string ("0" through "9" or "V").

    Maps to: FR-001, FR-009, VFR-001
    """
    while True:
        choice = prompt_input("Enter your choice (0-9 or V):")
        is_valid, error = validate_menu_choice(choice)
        if is_valid:
            return choice.strip().upper()
        print_error(error)


def get_priority_choice() -> Priority:
    """
    Prompt user to select a priority level.

    Returns:
        Selected Priority enum value.
    """
    display_priority_menu()
    while True:
        choice = prompt_input("Select priority (1-3, default=2):")
        if not choice:
            return Priority.MEDIUM
        if choice == "1":
            return Priority.HIGH
        elif choice == "2":
            return Priority.MEDIUM
        elif choice == "3":
            return Priority.LOW
        else:
            print_error("Please enter 1, 2, or 3.")


def get_tags_input() -> list[str]:
    """
    Prompt user to enter tags.

    Returns:
        List of valid tag strings.
    """
    display_tags_menu()
    tags_input = prompt_input("Enter tags (comma-separated, or Enter to skip):")
    if not tags_input.strip():
        return []

    # Parse and validate tags
    tags = [tag.strip().capitalize() for tag in tags_input.split(",")]
    valid_tags = [tag for tag in tags if tag in VALID_TAGS]
    invalid_tags = [tag for tag in tags if tag and tag not in VALID_TAGS]

    if invalid_tags:
        print_warning(f"Ignored invalid tags: {', '.join(invalid_tags)}")

    return valid_tags


def get_recurrence_choice() -> Recurrence:
    """
    Prompt user to select a recurrence pattern.

    Returns:
        Selected Recurrence enum value.

    Maps to: AFR-001
    """
    display_recurrence_menu()
    while True:
        choice = prompt_input("Select recurrence (1-4, default=1):")
        if not choice:
            return Recurrence.NONE
        if choice == "1":
            return Recurrence.NONE
        elif choice == "2":
            return Recurrence.DAILY
        elif choice == "3":
            return Recurrence.WEEKLY
        elif choice == "4":
            return Recurrence.MONTHLY
        else:
            print_error("Please enter 1, 2, 3, or 4.")


def get_due_date_input() -> datetime | None:
    """
    Prompt user to enter a due date.

    Returns:
        datetime object if valid date entered, None if skipped.

    Maps to: AFR-002
    """
    display_due_date_prompt()
    while True:
        date_input = prompt_input("Enter due date (or Enter to skip):")
        if not date_input.strip():
            return None

        # Try parsing with time
        try:
            due_date = datetime.strptime(date_input.strip(), "%Y-%m-%d %H:%M")
            return due_date
        except ValueError:
            pass

        # Try parsing date only (set time to end of day)
        try:
            due_date = datetime.strptime(date_input.strip(), "%Y-%m-%d")
            due_date = due_date.replace(hour=23, minute=59)
            return due_date
        except ValueError:
            pass

        print_error("Invalid date format. Use YYYY-MM-DD HH:MM or YYYY-MM-DD.")


# =============================================================================
# Task Operation Handlers (T013, T016, T020, T023, T026)
# =============================================================================


def handle_view_tasks(storage: TaskStorage) -> None:
    """
    Handle the View Tasks menu option.

    Displays all tasks with status indicators, or a friendly message
    if no tasks exist.

    Args:
        storage: The TaskStorage instance.

    Maps to: FR-007, FR-014
    """
    # Import here to avoid circular imports
    from src.task_manager import list_tasks

    tasks = list_tasks(storage)

    if not tasks:
        print_no_tasks()
        return

    print_tasks_table(tasks)

    completed_count = sum(1 for task in tasks if task.is_completed)
    incomplete_count = len(tasks) - completed_count
    print_stats(len(tasks), completed_count, incomplete_count)


def handle_add_task(storage: TaskStorage) -> None:
    """
    Handle the Add Task menu option.

    Prompts for title (required) and description (optional),
    validates input, and creates the task.

    Args:
        storage: The TaskStorage instance.

    Maps to: FR-002, FR-004, FR-005, FR-012, FR-013
    """
    from src.task_manager import add_task

    print_section_header("ADD NEW TASK")

    # Get title (required)
    while True:
        title = prompt_input("Enter task title (required):")
        title, warning = sanitize_title(title)
        if warning:
            print_warning(warning)
        if not title:
            print_error("Title cannot be empty. Please enter a title.")
            continue
        break

    # Get description (optional)
    description = prompt_input("Enter description (optional, Enter to skip):")
    description, warning = sanitize_description(description)
    if warning:
        print_warning(warning)

    # Create the task
    task = add_task(storage, title, description)
    print_success(f"Task #{task.id} created successfully!")
    print_task_details(task)


def handle_toggle_completion(storage: TaskStorage) -> None:
    """
    Handle the Toggle Complete/Incomplete menu option.

    Prompts for task ID and toggles its completion status.

    Args:
        storage: The TaskStorage instance.

    Maps to: FR-006, FR-008, FR-009
    """
    from src.task_manager import toggle_completion, list_tasks

    # Check if there are any tasks
    if storage.is_empty():
        print_error("No tasks to toggle. Add a task first.")
        return

    print_section_header("TOGGLE TASK STATUS")

    # Show current tasks for reference
    print_info("Current tasks:")
    print_tasks_table(list_tasks(storage))

    # Get task ID
    while True:
        task_id_input = prompt_input("Enter task ID to toggle:")
        is_valid, task_id, error = validate_task_id(task_id_input)
        if not is_valid:
            print_error(error)
            continue
        break

    # Toggle the task
    task = toggle_completion(storage, task_id)
    if task is None:
        print_error(f"Task #{task_id} not found.")
    else:
        new_status = "Complete" if task.is_completed else "Incomplete"
        print_success(f"Task #{task_id} is now marked as {new_status}.")
        print_task_details(task)


def handle_update_task(storage: TaskStorage) -> None:
    """
    Handle the Update Task menu option.

    Prompts for task ID and new values for title and/or description.
    Supports partial updates (leaving a field empty keeps current value).

    Args:
        storage: The TaskStorage instance.

    Maps to: FR-008, FR-012, FR-015
    """
    from src.task_manager import get_task, update_task, list_tasks

    # Check if there are any tasks
    if storage.is_empty():
        print_error("No tasks to update. Add a task first.")
        return

    print_section_header("UPDATE TASK")

    # Show current tasks for reference
    print_info("Current tasks:")
    print_tasks_table(list_tasks(storage))

    # Get task ID
    while True:
        task_id_input = prompt_input("Enter task ID to update:")
        is_valid, task_id, error = validate_task_id(task_id_input)
        if not is_valid:
            print_error(error)
            continue

        # Verify task exists
        task = get_task(storage, task_id)
        if task is None:
            print_error(f"Task #{task_id} not found.")
            continue
        break

    # Show current task details
    print_info("Current task details:")
    print_task_details(task)

    # Get new values (empty = keep current)
    print_info("(Press Enter to keep current value)")

    new_title = prompt_input(f"New title [{task.title}]:")
    new_title, warning = sanitize_title(new_title)
    if warning:
        print_warning(warning)

    new_description = prompt_input(f"New description [{task.description or '(none)'}]:")
    new_description, warning = sanitize_description(new_description)
    if warning:
        print_warning(warning)

    # Update the task
    updated_task = update_task(
        storage,
        task_id,
        title=new_title if new_title else None,
        description=new_description if new_description else None,
    )

    if updated_task:
        print_success(f"Task #{task_id} updated successfully!")
        print_task_details(updated_task)
    else:
        print_error(f"Failed to update task #{task_id}.")


def handle_delete_task(storage: TaskStorage) -> None:
    """
    Handle the Delete Task menu option.

    Prompts for task ID and confirmation before deleting.

    Args:
        storage: The TaskStorage instance.

    Maps to: FR-008, FR-011
    """
    from src.task_manager import get_task, delete_task, list_tasks

    # Check if there are any tasks
    if storage.is_empty():
        print_error("No tasks to delete. Add a task first.")
        return

    print_section_header("DELETE TASK")

    # Show current tasks for reference
    print_info("Current tasks:")
    print_tasks_table(list_tasks(storage))

    # Get task ID
    while True:
        task_id_input = prompt_input("Enter task ID to delete:")
        is_valid, task_id, error = validate_task_id(task_id_input)
        if not is_valid:
            print_error(error)
            continue

        # Verify task exists
        task = get_task(storage, task_id)
        if task is None:
            print_error(f"Task #{task_id} not found.")
            continue
        break

    # Show task to be deleted
    print_warning("Task to delete:")
    print_task_details(task)

    # Confirm deletion (FR-011)
    if prompt_confirm("Are you sure you want to delete this task?"):
        if delete_task(storage, task_id):
            print_success(f"Task #{task_id} deleted successfully.")
        else:
            print_error(f"Failed to delete task #{task_id}.")
    else:
        print_info("Deletion cancelled.")


# =============================================================================
# Intermediate Feature Handlers (Search, Filter, Sort)
# =============================================================================


def handle_search_tasks(storage: TaskStorage) -> None:
    """
    Handle the Search Tasks menu option.

    Prompts for a keyword and displays matching tasks.

    Args:
        storage: The TaskStorage instance.

    Maps to: IFR-003
    """
    from src.task_manager import search_tasks

    if storage.is_empty():
        print_error("No tasks to search. Add a task first.")
        return

    print_section_header("SEARCH TASKS")

    keyword = prompt_input("Enter search keyword:")
    if not keyword.strip():
        print_warning("No keyword entered. Showing all tasks.")
        from src.task_manager import list_tasks
        tasks = list_tasks(storage)
    else:
        tasks = search_tasks(storage, keyword)

    print_search_results(tasks, keyword or "(all)")


def handle_filter_tasks(storage: TaskStorage) -> None:
    """
    Handle the Filter Tasks menu option.

    Prompts for filter criteria and displays matching tasks.

    Args:
        storage: The TaskStorage instance.

    Maps to: IFR-004
    """
    from src.task_manager import filter_tasks, list_tasks

    if storage.is_empty():
        print_error("No tasks to filter. Add a task first.")
        return

    print_section_header("FILTER TASKS")
    display_filter_menu()

    choice = prompt_input("Select filter type (1-4):")

    status_filter: bool | None = None
    priority_filter: Priority | None = None
    tag_filter: str | None = None

    if choice == "1":
        # Filter by status
        display_status_filter_menu()
        status_choice = prompt_input("Select status (1-2):")
        if status_choice == "1":
            status_filter = False  # Incomplete
        elif status_choice == "2":
            status_filter = True  # Complete
        else:
            print_error("Invalid choice. Showing all tasks.")

    elif choice == "2":
        # Filter by priority
        display_priority_menu()
        priority_choice = prompt_input("Select priority (1-3):")
        if priority_choice == "1":
            priority_filter = Priority.HIGH
        elif priority_choice == "2":
            priority_filter = Priority.MEDIUM
        elif priority_choice == "3":
            priority_filter = Priority.LOW
        else:
            print_error("Invalid choice. Showing all tasks.")

    elif choice == "3":
        # Filter by tag
        display_tags_menu()
        tag_input = prompt_input("Enter tag name:")
        if tag_input.strip():
            tag_filter = tag_input.strip()
        else:
            print_warning("No tag entered. Showing all tasks.")

    elif choice == "4":
        # Show all tasks (clear filters)
        print_info("Showing all tasks (no filters).")

    else:
        print_error("Invalid choice. Showing all tasks.")

    # Apply filters
    tasks = filter_tasks(
        storage,
        status=status_filter,
        priority=priority_filter,
        tag=tag_filter,
    )

    print_filter_results(tasks, status_filter, priority_filter, tag_filter)


def handle_sort_tasks(storage: TaskStorage) -> None:
    """
    Handle the Sort Tasks menu option.

    Prompts for sort criteria and displays sorted tasks.

    Args:
        storage: The TaskStorage instance.

    Maps to: IFR-005
    """
    from src.task_manager import sort_tasks

    if storage.is_empty():
        print_error("No tasks to sort. Add a task first.")
        return

    print_section_header("SORT TASKS")
    display_sort_menu()

    choice = prompt_input("Select sort option (1-4):")

    sort_by = "priority"  # Default
    if choice == "1":
        sort_by = "priority"
    elif choice == "2":
        sort_by = "title"
    elif choice == "3":
        sort_by = "created"
    elif choice == "4":
        sort_by = "status"
    else:
        print_warning("Invalid choice. Sorting by priority.")

    tasks = sort_tasks(storage, by=sort_by)
    print_sort_results(tasks, sort_by)


def handle_add_task_with_options(storage: TaskStorage) -> None:
    """
    Handle the Add Task menu option with priority, tags, due date, and recurrence.

    Prompts for title (required), description (optional),
    priority, tags, due date, and recurrence, then creates the task.

    Args:
        storage: The TaskStorage instance.

    Maps to: FR-002, FR-004, FR-005, FR-012, FR-013, IFR-001, IFR-002, AFR-001, AFR-002
    """
    from src.task_manager import add_task

    print_section_header("ADD NEW TASK")

    # Get title (required)
    while True:
        title = prompt_input("Enter task title (required):")
        title, warning = sanitize_title(title)
        if warning:
            print_warning(warning)
        if not title:
            print_error("Title cannot be empty. Please enter a title.")
            continue
        break

    # Get description (optional)
    description = prompt_input("Enter description (optional, Enter to skip):")
    description, warning = sanitize_description(description)
    if warning:
        print_warning(warning)

    # Get priority
    priority = get_priority_choice()

    # Get tags
    tags = get_tags_input()

    # Get due date (AFR-002)
    due_date = get_due_date_input()

    # Get recurrence (AFR-001)
    recurrence = get_recurrence_choice()

    # Create the task
    task = add_task(
        storage,
        title,
        description,
        priority=priority,
        tags=tags,
        due_date=due_date,
        recurrence=recurrence,
    )
    print_success(f"Task #{task.id} created successfully!")
    print_task_details(task)


# =============================================================================
# Advanced Feature Handlers (Recurring Tasks, Reminders)
# =============================================================================


def handle_reminders(storage: TaskStorage) -> None:
    """
    Handle the Reminders menu option.

    Displays tasks categorized by urgency (overdue, due today, due soon).

    Args:
        storage: The TaskStorage instance.

    Maps to: AFR-003
    """
    from src.task_manager import get_reminders

    print_section_header("TASK REMINDERS")

    reminders = get_reminders(storage)
    print_reminders_panel(reminders)


def handle_toggle_with_recurrence(storage: TaskStorage) -> None:
    """
    Handle toggling task completion with recurring task support.

    When a recurring task is marked complete, automatically creates
    the next instance with updated due date.

    Args:
        storage: The TaskStorage instance.

    Maps to: AFR-001
    """
    from src.task_manager import get_task, complete_recurring_task, toggle_completion, list_tasks

    # Check if there are any tasks
    if storage.is_empty():
        print_error("No tasks to toggle. Add a task first.")
        return

    print_section_header("TOGGLE TASK STATUS")

    # Show current tasks for reference
    print_info("Current tasks:")
    print_tasks_table(list_tasks(storage))

    # Get task ID
    while True:
        task_id_input = prompt_input("Enter task ID to toggle:")
        is_valid, task_id, error = validate_task_id(task_id_input)
        if not is_valid:
            print_error(error)
            continue
        break

    # Get the task first to check if it's recurring
    task = get_task(storage, task_id)
    if task is None:
        print_error(f"Task #{task_id} not found.")
        return

    # If task is incomplete and recurring, use complete_recurring_task
    if not task.is_completed and task.recurrence != Recurrence.NONE:
        completed, new_task = complete_recurring_task(storage, task_id)
        if completed:
            if new_task:
                print_recurring_task_created(completed, new_task)
            else:
                print_success(f"Task #{task_id} marked as complete.")
                print_task_details(completed)
    else:
        # Regular toggle for non-recurring or already completed tasks
        updated_task = toggle_completion(storage, task_id)
        if updated_task:
            new_status = "Complete" if updated_task.is_completed else "Incomplete"
            print_success(f"Task #{task_id} is now marked as {new_status}.")
            print_task_details(updated_task)
        else:
            print_error(f"Failed to toggle task #{task_id}.")


# =============================================================================
# Voice Command Handler (VFR-001, VFR-002, VFR-003)
# =============================================================================


def handle_voice_command(storage: TaskStorage) -> None:
    """
    Handle voice command input with text fallback.

    Uses the voice-command-agent skills:
    - parse_voice_command: Parse natural language into action + args
    - validate_voice_command: Validate the parsed command

    Workflow:
    1. Check if voice recognition is available
    2. Get voice/text input from user
    3. Parse command using parse_voice_command skill
    4. Validate using validate_voice_command skill
    5. Show recognized command and ask for confirmation
    6. Execute the corresponding task_manager function

    Args:
        storage: The TaskStorage instance.

    Maps to: VFR-001, VFR-002, VFR-003
    """
    from src.task_manager import (
        add_task,
        toggle_completion,
        complete_recurring_task,
        delete_task,
        search_tasks,
        sort_tasks,
        filter_tasks,
        update_task_priority,
        update_task_tags,
        update_task_due_date,
        update_task_recurrence,
        list_tasks,
        get_task,
    )

    print_section_header("VOICE COMMAND")

    # Check voice availability and inform user
    voice_available = check_voice_available()
    if voice_available:
        print_info("Voice recognition is available.")
        print_info("Speak your command...")
    else:
        print_warning("Voice recognition unavailable. Using text input.")
        print_info("Type your command in natural language.")

    # Display example commands
    console.print("\n[dim]Example commands:[/dim]")
    console.print("  [cyan]'Add task Buy milk with High priority in Shopping'[/cyan]")
    console.print("  [cyan]'Mark task 2 complete'[/cyan]")
    console.print("  [cyan]'Delete task 3'[/cyan]")
    console.print("  [cyan]'Search tasks groceries'[/cyan]")
    console.print("  [cyan]'Sort tasks by priority'[/cyan]")
    console.print("  [cyan]'Add recurring task Gym weekly'[/cyan]")
    console.print("  [cyan]'Set due date for task 1 as tomorrow'[/cyan]")
    console.print()

    # Get command input (voice or text fallback)
    command_str = prompt_input("Your command:")

    if not command_str.strip():
        print_error("No command entered.")
        return

    # Using skill: parse_voice_command
    print_info("Using skill: parse_voice_command")
    action, args = parse_voice_command(command_str)

    # Using skill: validate_voice_command
    print_info("Using skill: validate_voice_command")
    is_valid, error_message = validate_voice_command(action, args)

    if not is_valid:
        print_error(f"Invalid command: {error_message}")
        print_info("Please try again with a clearer command.")
        return

    # Display recognized command for confirmation
    console.print(f"\n[bold cyan]Recognized:[/bold cyan]")
    console.print(f"  Action: [bold]{action}[/bold]")
    if args:
        console.print(f"  Arguments: [bold]{args}[/bold]")

    # Confirm before executing
    if not prompt_confirm("Execute this command?"):
        print_info("Command cancelled.")
        return

    # Execute the command based on action
    try:
        if action == "add":
            title = args.get("title", "")
            priority = args.get("priority", Priority.MEDIUM)
            tags = args.get("tags", [])
            recurrence = args.get("recurrence", Recurrence.NONE)
            due_date = args.get("due_date")

            task = add_task(
                storage,
                title,
                priority=priority,
                tags=tags,
                due_date=due_date,
                recurrence=recurrence,
            )
            print_success(f"Task #{task.id} created successfully!")
            print_task_details(task)

        elif action == "complete":
            task_id = args.get("task_id")
            task = get_task(storage, task_id)
            if task is None:
                print_error(f"Task #{task_id} not found.")
                return

            # Check if recurring
            if not task.is_completed and task.recurrence != Recurrence.NONE:
                completed, new_task = complete_recurring_task(storage, task_id)
                if completed:
                    if new_task:
                        print_recurring_task_created(completed, new_task)
                    else:
                        print_success(f"Task #{task_id} marked as complete.")
                        print_task_details(completed)
            else:
                updated_task = toggle_completion(storage, task_id)
                if updated_task:
                    new_status = "Complete" if updated_task.is_completed else "Incomplete"
                    print_success(f"Task #{task_id} is now marked as {new_status}.")
                    print_task_details(updated_task)
                else:
                    print_error(f"Failed to toggle task #{task_id}.")

        elif action == "delete":
            task_id = args.get("task_id")
            task = get_task(storage, task_id)
            if task is None:
                print_error(f"Task #{task_id} not found.")
                return

            print_warning("Task to delete:")
            print_task_details(task)

            if prompt_confirm("Are you sure you want to delete this task?"):
                if delete_task(storage, task_id):
                    print_success(f"Task #{task_id} deleted successfully.")
                else:
                    print_error(f"Failed to delete task #{task_id}.")
            else:
                print_info("Deletion cancelled.")

        elif action == "list":
            tasks = list_tasks(storage)
            if not tasks:
                print_no_tasks()
            else:
                print_tasks_table(tasks)
                completed_count = sum(1 for t in tasks if t.is_completed)
                incomplete_count = len(tasks) - completed_count
                print_stats(len(tasks), completed_count, incomplete_count)

        elif action == "search":
            keyword = args.get("keyword", "")
            tasks = search_tasks(storage, keyword)
            print_search_results(tasks, keyword)

        elif action == "sort":
            sort_by = args.get("by", "priority")
            tasks = sort_tasks(storage, by=sort_by)
            print_sort_results(tasks, sort_by)

        elif action == "filter":
            status = args.get("status")
            priority = args.get("priority")
            tag = args.get("tag")
            tasks = filter_tasks(storage, status=status, priority=priority, tag=tag)
            print_filter_results(tasks, status, priority, tag)

        elif action == "update_priority":
            task_id = args.get("task_id")
            priority = args.get("priority")
            task = update_task_priority(storage, task_id, priority)
            if task:
                print_success(f"Task #{task_id} priority updated to {priority}.")
                print_task_details(task)
            else:
                print_error(f"Task #{task_id} not found.")

        elif action == "update_tags":
            task_id = args.get("task_id")
            tags = args.get("tags", [])
            task = update_task_tags(storage, task_id, tags)
            if task:
                print_success(f"Task #{task_id} tags updated.")
                print_task_details(task)
            else:
                print_error(f"Task #{task_id} not found.")

        elif action == "update_due_date":
            task_id = args.get("task_id")
            due_date = args.get("due_date")
            task = update_task_due_date(storage, task_id, due_date)
            if task:
                if due_date:
                    print_success(f"Task #{task_id} due date set to {due_date.strftime('%Y-%m-%d %H:%M')}.")
                else:
                    print_success(f"Task #{task_id} due date removed.")
                print_task_details(task)
            else:
                print_error(f"Task #{task_id} not found.")

        elif action == "update_recurrence":
            task_id = args.get("task_id")
            recurrence = args.get("recurrence")
            task = update_task_recurrence(storage, task_id, recurrence)
            if task:
                print_success(f"Task #{task_id} recurrence updated to {recurrence}.")
                print_task_details(task)
            else:
                print_error(f"Task #{task_id} not found.")

        else:
            print_error(f"Unknown action: {action}")

    except Exception as e:
        print_error(f"Error executing command: {str(e)}")
