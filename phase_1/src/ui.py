"""
Rich Console UI Module - Phase I Todo Application

Provides beautiful console UI using the Rich library.
Includes styled panels, tables, and formatted output.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich.box import ROUNDED, DOUBLE, HEAVY
from rich.align import Align
from rich import box

from datetime import datetime
from src.models import Task, Priority, Recurrence, VALID_TAGS

# Initialize console
console = Console()

# Styles
STYLE_SUCCESS = Style(color="green", bold=True)
STYLE_ERROR = Style(color="red", bold=True)
STYLE_WARNING = Style(color="yellow", bold=True)
STYLE_INFO = Style(color="cyan")
STYLE_HEADER = Style(color="blue", bold=True)
STYLE_COMPLETE = Style(color="green")
STYLE_INCOMPLETE = Style(color="yellow")


def clear_screen() -> None:
    """Clear the console screen."""
    console.clear()


def print_welcome() -> None:
    """Display beautiful welcome banner."""
    banner = """
╔╦╗╔═╗╔╦╗╔═╗  ╔═╗╔═╗╔═╗
 ║ ║ ║ ║║║ ║  ╠═╣╠═╝╠═╝
 ╩ ╚═╝═╩╝╚═╝  ╩ ╩╩  ╩
    """

    welcome_panel = Panel(
        Align.center(
            Text(banner, style="bold cyan") +
            Text("\n\nWelcome to the Todo Application!", style="bold white") +
            Text("\nManage your tasks with ease.", style="dim white")
        ),
        box=DOUBLE,
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(welcome_panel)


def print_goodbye() -> None:
    """Display goodbye message."""
    goodbye_panel = Panel(
        Align.center(
            Text("Thank you for using Todo App!", style="bold cyan") +
            Text("\nGoodbye! ", style="white")
        ),
        box=ROUNDED,
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(goodbye_panel)


def display_menu() -> None:
    """Display the main menu with styled options."""
    menu_text = Text()
    menu_text.append("\n")

    options = [
        ("1", "Add Task", "Create a new task"),
        ("2", "View Tasks", "See all your tasks"),
        ("3", "Update Task", "Edit an existing task"),
        ("4", "Delete Task", "Remove a task"),
        ("5", "Toggle Status", "Complete/Incomplete"),
        ("6", "Search", "Find tasks by keyword"),
        ("7", "Filter", "Filter by status/priority/tag"),
        ("8", "Sort", "Sort by priority/title/date"),
        ("9", "Reminders", "View due/overdue tasks"),
        ("V", "Voice Command", "Speak or type naturally"),
        ("0", "Exit", "Close the application"),
    ]

    table = Table(
        show_header=False,
        box=None,
        padding=(0, 2),
        expand=False,
    )
    table.add_column("Num", style="bold cyan", width=4)
    table.add_column("Option", style="bold white", width=15)
    table.add_column("Desc", style="dim", width=25)

    for num, option, desc in options:
        table.add_row(f"[{num}]", option, desc)

    menu_panel = Panel(
        Align.center(table),
        title="[bold cyan]TODO APPLICATION[/bold cyan]",
        box=ROUNDED,
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(menu_panel)


def print_error(message: str) -> None:
    """Display styled error message."""
    console.print(f"[bold red]  {message}[/bold red]")


def print_warning(message: str) -> None:
    """Display styled warning message."""
    console.print(f"[bold yellow]  {message}[/bold yellow]")


def print_success(message: str) -> None:
    """Display styled success message."""
    console.print(f"[bold green]  {message}[/bold green]")


def print_info(message: str) -> None:
    """Display styled info message."""
    console.print(f"[cyan]  {message}[/cyan]")


def print_section_header(title: str) -> None:
    """Display a section header."""
    console.print(Panel(
        Align.center(Text(title, style="bold white")),
        box=ROUNDED,
        border_style="blue",
        padding=(0, 2),
    ))


def print_tasks_table(tasks: list[Task], title: str = "Your Tasks") -> None:
    """Display tasks in a beautiful table with priority, tags, due date, and recurrence."""
    table = Table(
        title=title,
        box=ROUNDED,
        header_style="bold cyan",
        border_style="cyan",
        show_lines=True,
        padding=(0, 1),
    )

    table.add_column("#", style="dim", width=4, justify="center")
    table.add_column("Status", width=8, justify="center")
    table.add_column("Priority", width=8, justify="center")
    table.add_column("Title", style="bold", min_width=15)
    table.add_column("Due Date", width=12, justify="center")
    table.add_column("Recurrence", width=10, justify="center")
    table.add_column("Tags", style="magenta", width=12)

    now = datetime.now()

    for task in tasks:
        # Status styling
        if task.is_completed:
            status = Text("Done", style="bold green")
        else:
            status = Text("Pending", style="bold yellow")

        # Priority styling
        priority_styles = {
            Priority.HIGH: ("High", "bold red"),
            Priority.MEDIUM: ("Medium", "bold yellow"),
            Priority.LOW: ("Low", "bold green"),
        }
        priority_text, priority_style = priority_styles.get(
            task.priority, ("Medium", "bold yellow")
        )
        priority = Text(priority_text, style=priority_style)

        # Due date formatting with urgency styling
        if task.due_date:
            due_str = task.due_date.strftime("%m/%d %H:%M")
            if not task.is_completed:
                if task.due_date < now:
                    due_date = Text(due_str, style="bold red")  # Overdue
                elif task.due_date.date() == now.date():
                    due_date = Text(due_str, style="bold yellow")  # Due today
                else:
                    due_date = Text(due_str, style="cyan")  # Future
            else:
                due_date = Text(due_str, style="dim")
        else:
            due_date = Text("-", style="dim")

        # Recurrence formatting
        recurrence_styles = {
            Recurrence.NONE: ("-", "dim"),
            Recurrence.DAILY: ("Daily", "bold magenta"),
            Recurrence.WEEKLY: ("Weekly", "bold blue"),
            Recurrence.MONTHLY: ("Monthly", "bold cyan"),
        }
        recur_text, recur_style = recurrence_styles.get(
            task.recurrence, ("-", "dim")
        )
        recurrence = Text(recur_text, style=recur_style)

        # Tags formatting
        tags_str = ", ".join(task.tags) if task.tags else "-"

        table.add_row(
            str(task.id),
            status,
            priority,
            task.title,
            due_date,
            recurrence,
            tags_str,
        )

    console.print(table)


def print_task_details(task: Task) -> None:
    """Display detailed task information in a panel."""
    status_style = "green" if task.is_completed else "yellow"
    status_icon = "" if task.is_completed else ""
    status_text = "Complete" if task.is_completed else "Incomplete"

    # Priority styling
    priority_styles = {
        Priority.HIGH: ("High", "red"),
        Priority.MEDIUM: ("Medium", "yellow"),
        Priority.LOW: ("Low", "green"),
    }
    priority_text, priority_style = priority_styles.get(
        task.priority, ("Medium", "yellow")
    )

    # Recurrence styling
    recurrence_styles = {
        Recurrence.NONE: ("One-time", "dim"),
        Recurrence.DAILY: ("Daily", "magenta"),
        Recurrence.WEEKLY: ("Weekly", "blue"),
        Recurrence.MONTHLY: ("Monthly", "cyan"),
    }
    recurrence_text, recurrence_style = recurrence_styles.get(
        task.recurrence, ("One-time", "dim")
    )

    # Due date formatting
    now = datetime.now()
    if task.due_date:
        due_str = task.due_date.strftime('%Y-%m-%d %H:%M')
        if not task.is_completed and task.due_date < now:
            due_style = "bold red"
            due_str += " (OVERDUE)"
        elif not task.is_completed and task.due_date.date() == now.date():
            due_style = "bold yellow"
            due_str += " (Due Today)"
        else:
            due_style = "cyan"
    else:
        due_str = "(no deadline)"
        due_style = "dim"

    details = Text()
    details.append(f"  ID:          ", style="dim")
    details.append(f"#{task.id}\n", style="bold cyan")
    details.append(f"  Title:       ", style="dim")
    details.append(f"{task.title}\n", style="bold white")
    details.append(f"  Description: ", style="dim")
    details.append(f"{task.description or '(none)'}\n", style="white")
    details.append(f"  Priority:    ", style="dim")
    details.append(f"{priority_text}\n", style=f"bold {priority_style}")
    details.append(f"  Tags:        ", style="dim")
    details.append(f"{', '.join(task.tags) if task.tags else '(none)'}\n", style="magenta")
    details.append(f"  Due Date:    ", style="dim")
    details.append(f"{due_str}\n", style=due_style)
    details.append(f"  Recurrence:  ", style="dim")
    details.append(f"{recurrence_text}\n", style=f"bold {recurrence_style}")
    details.append(f"  Status:      ", style="dim")
    details.append(f"{status_icon} {status_text}\n", style=f"bold {status_style}")
    details.append(f"  Created:     ", style="dim")
    details.append(f"{task.created_at.strftime('%Y-%m-%d %H:%M:%S')}", style="cyan")

    console.print(Panel(
        details,
        title="[bold]Task Details[/bold]",
        box=ROUNDED,
        border_style=status_style,
        padding=(0, 1),
    ))


def print_no_tasks() -> None:
    """Display friendly message when no tasks exist."""
    empty_panel = Panel(
        Align.center(
            Text("No tasks yet!", style="bold yellow") +
            Text("\n\nUse ", style="dim") +
            Text("[1] Add Task", style="bold cyan") +
            Text(" to create your first task.", style="dim")
        ),
        box=ROUNDED,
        border_style="yellow",
        padding=(1, 2),
    )
    console.print(empty_panel)


def print_stats(total: int, completed: int, incomplete: int) -> None:
    """Display task statistics."""
    stats = Table(box=None, show_header=False, padding=(0, 2))
    stats.add_column("Label", style="dim")
    stats.add_column("Value", style="bold")

    stats.add_row("Total:", f"[cyan]{total}[/cyan]")
    stats.add_row("Completed:", f"[green]{completed}[/green]")
    stats.add_row("Pending:", f"[yellow]{incomplete}[/yellow]")

    console.print(Panel(stats, box=ROUNDED, border_style="dim", padding=(0, 1)))


def prompt_input(prompt: str) -> str:
    """Get styled input from user."""
    return console.input(f"[bold cyan]{prompt}[/bold cyan] ")


def prompt_confirm(message: str) -> bool:
    """Get yes/no confirmation from user."""
    while True:
        response = console.input(f"[yellow]{message} (y/n): [/yellow]").strip().lower()
        if response == "y":
            return True
        elif response == "n":
            return False
        print_error("Please enter 'y' for yes or 'n' for no.")


def wait_for_enter() -> None:
    """Pause and wait for Enter key."""
    console.input("\n[dim]Press Enter to continue...[/dim]")


# =============================================================================
# Intermediate Features UI Helpers
# =============================================================================


def display_priority_menu() -> None:
    """Display priority selection menu."""
    console.print("\n[bold cyan]Select Priority:[/bold cyan]")
    console.print("  [1] [bold red]High[/bold red]   - Urgent, needs immediate attention")
    console.print("  [2] [bold yellow]Medium[/bold yellow] - Normal priority (default)")
    console.print("  [3] [bold green]Low[/bold green]    - Can be deferred")


def display_tags_menu() -> None:
    """Display available tags for selection."""
    console.print("\n[bold cyan]Available Tags:[/bold cyan]")
    tags_list = sorted(VALID_TAGS)
    for i, tag in enumerate(tags_list, 1):
        console.print(f"  [{i}] [magenta]{tag}[/magenta]")
    console.print("\n[dim]Enter tag names separated by commas (e.g., Work, Home)[/dim]")


def display_filter_menu() -> None:
    """Display filter options menu."""
    console.print("\n[bold cyan]Filter Options:[/bold cyan]")
    console.print("  [1] By Status (Complete/Incomplete)")
    console.print("  [2] By Priority (High/Medium/Low)")
    console.print("  [3] By Tag")
    console.print("  [4] Clear All Filters (show all tasks)")


def display_sort_menu() -> None:
    """Display sort options menu."""
    console.print("\n[bold cyan]Sort Options:[/bold cyan]")
    console.print("  [1] By Priority (High -> Low)")
    console.print("  [2] By Title (A -> Z)")
    console.print("  [3] By Created Date (Oldest first)")
    console.print("  [4] By Status (Incomplete first)")


def display_status_filter_menu() -> None:
    """Display status filter options."""
    console.print("\n[bold cyan]Filter by Status:[/bold cyan]")
    console.print("  [1] [bold yellow]Incomplete[/bold yellow] - Pending tasks only")
    console.print("  [2] [bold green]Complete[/bold green]   - Done tasks only")


def print_search_results(tasks: list[Task], keyword: str) -> None:
    """Display search results with keyword highlighted."""
    if not tasks:
        console.print(Panel(
            Align.center(
                Text(f"No tasks found matching '{keyword}'", style="bold yellow")
            ),
            box=ROUNDED,
            border_style="yellow",
            padding=(1, 2),
        ))
    else:
        print_tasks_table(tasks, title=f"Search Results for '{keyword}'")
        console.print(f"\n[dim]Found {len(tasks)} task(s)[/dim]")


def print_filter_results(
    tasks: list[Task],
    status: bool | None = None,
    priority: Priority | None = None,
    tag: str | None = None,
) -> None:
    """Display filter results with active filters shown."""
    # Build filter description
    filters = []
    if status is not None:
        filters.append(f"Status: {'Complete' if status else 'Incomplete'}")
    if priority is not None:
        filters.append(f"Priority: {priority}")
    if tag is not None:
        filters.append(f"Tag: {tag}")

    filter_desc = " | ".join(filters) if filters else "None"

    if not tasks:
        console.print(Panel(
            Align.center(
                Text("No tasks match the selected filters", style="bold yellow") +
                Text(f"\n\nFilters: {filter_desc}", style="dim")
            ),
            box=ROUNDED,
            border_style="yellow",
            padding=(1, 2),
        ))
    else:
        print_tasks_table(tasks, title=f"Filtered Tasks ({filter_desc})")
        console.print(f"\n[dim]Found {len(tasks)} task(s)[/dim]")


def print_sort_results(tasks: list[Task], sort_by: str) -> None:
    """Display sorted tasks with sort criteria shown."""
    sort_labels = {
        "priority": "Priority",
        "title": "Title",
        "created": "Created Date",
        "status": "Status",
    }
    sort_label = sort_labels.get(sort_by, sort_by.capitalize())

    if not tasks:
        print_no_tasks()
    else:
        print_tasks_table(tasks, title=f"Tasks Sorted by {sort_label}")


def print_no_results(message: str = "No matching tasks found") -> None:
    """Display a message when no results are found."""
    console.print(Panel(
        Align.center(Text(message, style="bold yellow")),
        box=ROUNDED,
        border_style="yellow",
        padding=(1, 2),
    ))


# =============================================================================
# Advanced Features UI Helpers (Recurrence, Due Date, Reminders)
# =============================================================================


def display_recurrence_menu() -> None:
    """Display recurrence pattern selection menu."""
    console.print("\n[bold cyan]Select Recurrence Pattern:[/bold cyan]")
    console.print("  [1] [dim]One-time[/dim]  - Task does not repeat (default)")
    console.print("  [2] [bold magenta]Daily[/bold magenta]    - Repeats every day")
    console.print("  [3] [bold blue]Weekly[/bold blue]   - Repeats every week")
    console.print("  [4] [bold cyan]Monthly[/bold cyan]  - Repeats every month")


def display_due_date_prompt() -> None:
    """Display prompt for due date input."""
    console.print("\n[bold cyan]Set Due Date:[/bold cyan]")
    console.print("[dim]Format: YYYY-MM-DD HH:MM (e.g., 2025-12-31 14:00)[/dim]")
    console.print("[dim]Press Enter to skip (no deadline)[/dim]")


def print_reminders_panel(reminders: dict[str, list[Task]]) -> None:
    """
    Display reminders panel with overdue, due today, and due soon tasks.

    Args:
        reminders: Dictionary with 'overdue', 'due_today', and 'due_soon' keys.
    """
    overdue = reminders.get('overdue', [])
    due_today = reminders.get('due_today', [])
    due_soon = reminders.get('due_soon', [])

    has_reminders = overdue or due_today or due_soon

    if not has_reminders:
        console.print(Panel(
            Align.center(
                Text("No upcoming deadlines!", style="bold green") +
                Text("\n\nAll your tasks are on track.", style="dim")
            ),
            title="[bold green]Reminders[/bold green]",
            box=ROUNDED,
            border_style="green",
            padding=(1, 2),
        ))
        return

    content = Text()

    # Overdue tasks (highest priority)
    if overdue:
        content.append("  OVERDUE TASKS\n", style="bold red")
        for task in overdue:
            days_overdue = (datetime.now() - task.due_date).days
            content.append(f"    #{task.id} ", style="dim")
            content.append(f"{task.title}", style="bold white")
            content.append(f" - {days_overdue} day(s) overdue\n", style="red")
        content.append("\n")

    # Due today
    if due_today:
        content.append("  DUE TODAY\n", style="bold yellow")
        for task in due_today:
            time_str = task.due_date.strftime("%H:%M")
            content.append(f"    #{task.id} ", style="dim")
            content.append(f"{task.title}", style="bold white")
            content.append(f" - at {time_str}\n", style="yellow")
        content.append("\n")

    # Due soon (next 3 days)
    if due_soon:
        content.append("  DUE SOON (next 3 days)\n", style="bold cyan")
        for task in due_soon:
            due_str = task.due_date.strftime("%m/%d %H:%M")
            content.append(f"    #{task.id} ", style="dim")
            content.append(f"{task.title}", style="bold white")
            content.append(f" - {due_str}\n", style="cyan")

    # Summary
    total = len(overdue) + len(due_today) + len(due_soon)
    content.append(f"\n  Total: {total} task(s) need attention", style="dim")

    border_style = "red" if overdue else ("yellow" if due_today else "cyan")
    console.print(Panel(
        content,
        title="[bold]Task Reminders[/bold]",
        box=ROUNDED,
        border_style=border_style,
        padding=(1, 1),
    ))


def print_recurring_task_created(original: Task, new_task: Task) -> None:
    """Display message when a recurring task creates a new instance."""
    content = Text()
    content.append("  Recurring task completed!\n\n", style="bold green")
    content.append("  Completed: ", style="dim")
    content.append(f"#{original.id} {original.title}\n", style="white")
    content.append("  New instance: ", style="dim")
    content.append(f"#{new_task.id} ", style="bold cyan")
    content.append(f"Due: {new_task.due_date.strftime('%Y-%m-%d %H:%M')}\n", style="cyan")
    content.append(f"  Recurrence: {new_task.recurrence}", style="magenta")

    console.print(Panel(
        content,
        title="[bold magenta]Recurring Task[/bold magenta]",
        box=ROUNDED,
        border_style="magenta",
        padding=(0, 1),
    ))


def print_startup_reminders(reminders: dict[str, list[Task]]) -> None:
    """
    Display compact reminder notification at startup.

    Args:
        reminders: Dictionary with 'overdue', 'due_today', and 'due_soon' keys.
    """
    overdue = reminders.get('overdue', [])
    due_today = reminders.get('due_today', [])

    if not overdue and not due_today:
        return

    content = Text()

    if overdue:
        content.append(f"  {len(overdue)} overdue task(s)!", style="bold red")
        if due_today:
            content.append(" | ")

    if due_today:
        content.append(f"  {len(due_today)} task(s) due today", style="bold yellow")

    content.append("\n  [dim]Use option [9] Reminders to view details[/dim]")

    console.print(Panel(
        content,
        title="[bold]Reminder[/bold]",
        box=ROUNDED,
        border_style="red" if overdue else "yellow",
        padding=(0, 1),
    ))
