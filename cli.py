"""Command-line interface for the expense tracker.

Examples:
    python cli.py add 12.50 food "Lunch with team"
    python cli.py list --month 2026-10
    python cli.py summary --month 2026-10
    python cli.py delete 3
"""

from __future__ import annotations

import argparse
import sys
from datetime import date

from expense_tracker import ExpenseTracker


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track your spending from the terminal.")
    parser.add_argument("--db", default="expenses.db", help="database file (default: expenses.db)")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="record an expense")
    add.add_argument("amount", help="e.g. 12.50")
    add.add_argument("category", help="e.g. food, transport, rent")
    add.add_argument("description", nargs="?", default="")
    add.add_argument("--date", type=date.fromisoformat, help="YYYY-MM-DD (default: today)")

    lst = sub.add_parser("list", help="show expenses")
    lst.add_argument("--month", help="YYYY-MM")
    lst.add_argument("--category")

    summ = sub.add_parser("summary", help="totals per category for a month")
    summ.add_argument("--month", default=date.today().strftime("%Y-%m"), help="YYYY-MM (default: this month)")

    dele = sub.add_parser("delete", help="remove an expense by id")
    dele.add_argument("id", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    with ExpenseTracker(args.db) as tracker:
        try:
            if args.command == "add":
                new_id = tracker.add(args.amount, args.category, args.description, args.date)
                print(f"Added expense #{new_id}")

            elif args.command == "list":
                expenses = tracker.list(args.month, args.category)
                if not expenses:
                    print("No expenses found.")
                for e in expenses:
                    print(f"#{e.id:<4} {e.spent_on}  £{e.amount:>8.2f}  {e.category:<12} {e.description}")

            elif args.command == "summary":
                totals = tracker.summary(args.month)
                if not totals:
                    print(f"No expenses in {args.month}.")
                    return 0
                width = max(len(c) for c in totals)
                biggest = max(totals.values())
                print(f"Spending for {args.month}\n")
                for cat, total in totals.items():
                    bar = "█" * max(1, int(20 * total / biggest))
                    print(f"{cat:<{width}}  £{total:>8.2f}  {bar}")
                print(f"\n{'TOTAL':<{width}}  £{sum(totals.values()):>8.2f}")

            elif args.command == "delete":
                if tracker.delete(args.id):
                    print(f"Deleted expense #{args.id}")
                else:
                    print(f"No expense with id {args.id}", file=sys.stderr)
                    return 1
        except ValueError as err:
            print(f"Error: {err}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
