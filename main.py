#!/usr/bin/env python3
"""
Simple console task manager.
Commands: add, list, done, rm, clear
"""

import json
import os
import sys
from datetime import datetime
from argparse import ArgumentParser
from colorama import init, Fore, Style

# Initialize colorama for Windows/Linux/Mac
init(autoreset=True)

TASKS_FILE = "tasks.json"


class TaskManager:
    def __init__(self):
        self.tasks = self._load_tasks()

    def _load_tasks(self):
        """Load tasks from JSON file"""
        if not os.path.exists(TASKS_FILE):
            return []
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _save_tasks(self):
        """Save tasks to JSON file"""
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)

    def _get_next_id(self):
        """Return the next available ID"""
        if not self.tasks:
            return 1
        return max(task["id"] for task in self.tasks) + 1

    def add(self, description):
        """Add a new task"""
        if not description:
            print(f"{Fore.RED}Error: task description cannot be empty{Style.RESET_ALL}")
            return

        task = {
            "id": self._get_next_id(),
            "description": description,
            "status": "pending",  # pending or done
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        self.tasks.append(task)
        self._save_tasks()
        print(f"{Fore.GREEN}Task added (ID: {task['id']}){Style.RESET_ALL}")

    def list_tasks(self, show_all=True):
        """Display the task list"""
        if not self.tasks:
            print(f"{Fore.YELLOW}Task list is empty. Use 'add' to add tasks.{Style.RESET_ALL}")
            return

        # Group by status
        pending = [t for t in self.tasks if t["status"] == "pending"]
        done = [t for t in self.tasks if t["status"] == "done"]

        if show_all or pending:
            if pending:
                print(f"\n{Fore.CYAN}Active tasks:{Style.RESET_ALL}")
                for task in pending:
                    self._print_task(task)
            else:
                print(f"{Fore.GREEN}No active tasks!{Style.RESET_ALL}")

        if show_all and done:
            print(f"\n{Fore.MAGENTA}Completed tasks:{Style.RESET_ALL}")
            for task in done:
                self._print_task(task, done=True)

    def _print_task(self, task, done=False):
        """Format and print a single task"""
        status_icon = f"{Fore.GREEN}[x]{Style.RESET_ALL}" if done else f"{Fore.YELLOW}[ ]{Style.RESET_ALL}"
        desc = task["description"]
        if len(desc) > 60:
            desc = desc[:57] + "..."

        task_str = f"  [{task['id']:3}] {status_icon} {desc}"
        print(task_str)

    def mark_done(self, task_id):
        """Mark a task as completed"""
        for task in self.tasks:
            if task["id"] == task_id:
                if task["status"] == "done":
                    print(f"{Fore.YELLOW}Task already marked as completed{Style.RESET_ALL}")
                    return
                task["status"] = "done"
                task["completed_at"] = datetime.now().isoformat()
                self._save_tasks()
                print(f"{Fore.GREEN}Task #{task_id} marked as completed{Style.RESET_ALL}")
                return
        print(f"{Fore.RED}Task with ID {task_id} not found{Style.RESET_ALL}")

    def remove(self, task_id):
        """Delete a task"""
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                removed = self.tasks.pop(i)
                self._save_tasks()
                print(f"{Fore.RED}Task #{task_id} deleted: \"{removed['description']}\"{Style.RESET_ALL}")
                return
        print(f"{Fore.RED}Task with ID {task_id} not found{Style.RESET_ALL}")

    def clear_all(self):
        """Delete all tasks (with confirmation)"""
        if not self.tasks:
            print(f"{Fore.YELLOW}Task list is already empty{Style.RESET_ALL}")
            return

        print(f"{Fore.RED}Are you sure? This will delete all {len(self.tasks)} task(s).{Style.RESET_ALL}")
        confirm = input("Type 'yes' to confirm: ").lower()
        if confirm == 'yes':
            self.tasks = []
            self._save_tasks()
            print(f"{Fore.GREEN}All tasks deleted{Style.RESET_ALL}")
        else:
            print("Operation cancelled")


def main():
    parser = ArgumentParser(description="Console Task Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # add
    parser_add = subparsers.add_parser("add", help="Add a task")
    parser_add.add_argument("description", nargs="+", help="Task description")

    # list
    parser_list = subparsers.add_parser("list", help="Show all tasks")
    parser_list.add_argument("--pending", action="store_true", help="Show only active tasks")

    # done
    parser_done = subparsers.add_parser("done", help="Mark a task as completed")
    parser_done.add_argument("id", type=int, help="Task ID")

    # rm
    parser_rm = subparsers.add_parser("rm", help="Delete a task")
    parser_rm.add_argument("id", type=int, help="Task ID")

    # clear
    subparsers.add_parser("clear", help="Delete ALL tasks")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    manager = TaskManager()

    if args.command == "add":
        description = " ".join(args.description)
        manager.add(description)
    elif args.command == "list":
        manager.list_tasks(show_all=not args.pending)
    elif args.command == "done":
        manager.mark_done(args.id)
    elif args.command == "rm":
        manager.remove(args.id)
    elif args.command == "clear":
        manager.clear_all()


if __name__ == "__main__":
    main()