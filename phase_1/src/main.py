"""
Main Entry Point - Phase I Todo Application

Application entry point that initializes storage and runs the main menu loop.
Use UV virtual environment for Python 3.13+ dependencies.

Usage:
    cd phase_1
    python -m src.main

Maps to:
    - FR-001: Display interactive main menu
    - FR-010: Allow return to main menu after each operation
    - T010, T014, T017, T021, T024, T027, T028
    - IFR-001 to IFR-005: Intermediate features (priority, tags, search, filter, sort)
    - AFR-001 to AFR-003: Advanced features (recurring tasks, due dates, reminders)
    - VFR-001 to VFR-003: Voice commands (natural language parsing, validation, fallback)
"""

import sys

from src.storage import TaskStorage
from src.task_manager import get_reminders
from src.menu import (
    display_menu,
    get_menu_choice,
    wait_for_enter,
    handle_view_tasks,
    handle_add_task_with_options,
    handle_toggle_with_recurrence,
    handle_update_task,
    handle_delete_task,
    handle_search_tasks,
    handle_filter_tasks,
    handle_sort_tasks,
    handle_reminders,
    handle_voice_command,
)
from src.ui import (
    print_welcome,
    print_goodbye,
    print_startup_reminders,
    console,
)


def main() -> None:
    """
    Main application entry point.

    Initializes storage and runs the main menu loop.
    Routes menu choices to appropriate handlers.

    Maps to: FR-001, FR-010, T010, AFR-003
    """
    # Initialize storage
    storage = TaskStorage()

    # Display welcome
    print_welcome()

    # Show startup reminders if any tasks are overdue or due today (AFR-003)
    reminders = get_reminders(storage)
    print_startup_reminders(reminders)

    # Main loop
    try:
        while True:
            display_menu()
            choice = get_menu_choice()

            if choice == "1":
                # Add Task with priority, tags, due date, recurrence (T017, IFR, AFR)
                handle_add_task_with_options(storage)
                wait_for_enter()

            elif choice == "2":
                # View Tasks (T014)
                handle_view_tasks(storage)
                wait_for_enter()

            elif choice == "3":
                # Update Task (T024)
                handle_update_task(storage)
                wait_for_enter()

            elif choice == "4":
                # Delete Task (T027)
                handle_delete_task(storage)
                wait_for_enter()

            elif choice == "5":
                # Toggle Complete/Incomplete with recurring task support (T021, AFR-001)
                handle_toggle_with_recurrence(storage)
                wait_for_enter()

            elif choice == "6":
                # Search Tasks (IFR-003)
                handle_search_tasks(storage)
                wait_for_enter()

            elif choice == "7":
                # Filter Tasks (IFR-004)
                handle_filter_tasks(storage)
                wait_for_enter()

            elif choice == "8":
                # Sort Tasks (IFR-005)
                handle_sort_tasks(storage)
                wait_for_enter()

            elif choice == "9":
                # Reminders - View due/overdue tasks (AFR-003)
                handle_reminders(storage)
                wait_for_enter()

            elif choice == "V":
                # Voice Command - Natural language input (VFR-001, VFR-002, VFR-003)
                handle_voice_command(storage)
                wait_for_enter()

            elif choice == "0":
                # Exit
                print_goodbye()
                break

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n")
        print_goodbye()
        sys.exit(0)


if __name__ == "__main__":
    main()
