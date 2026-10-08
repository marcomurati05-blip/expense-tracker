# Expense Tracker (CLI)

A small command-line tool for tracking personal spending, built with Python and SQLite. It records expenses, filters them by month or category, and prints a monthly summary with a simple bar chart in the terminal.

```
$ python cli.py summary --month 2026-10
Spending for 2026-10

rent        £  650.00  ████████████████████
food        £  142.30  ████
transport   £   48.60  █

TOTAL       £  840.90
```

## Why I built it

I wanted a quick way to see where my money goes each month without a spreadsheet or a third-party app, and a project to practise working with databases, a clean CLI, and tests.

## Features

- Add, list, and delete expenses
- Filter by month (`YYYY-MM`) and category
- Monthly summary per category with a terminal bar chart
- Amounts stored as integer pence, so there are no floating-point rounding errors
- Input validation with clear error messages
- No third-party dependencies (uses only the Python standard library)

## Getting started

Requires Python 3.10+.

```bash
git clone https://github.com/marcomurati05-blip/expense-tracker.gitcd expense-tracker

python cli.py add 12.50 food "Lunch with team"
python cli.py add 2.80 transport "Bus" --date 2026-10-01
python cli.py list --month 2026-10
python cli.py summary
python cli.py delete 1
```

Data is saved to `expenses.db` in the current folder (change it with `--db path/to/file.db`).

## Running the tests

```bash
python -m unittest discover tests
```

## Project structure

```
expense_tracker.py   core logic (database, validation, queries)
cli.py               command-line interface (argparse)
tests/               unit tests
```

## What I learned

- Designing a small SQLite schema and writing parameterised queries (safe from SQL injection)
- Why money should never be stored as a float
- Separating core logic from the interface so it is easy to test

## Possible next steps

- Export to CSV
- Monthly budgets with warnings when you go over
- A small web front end
