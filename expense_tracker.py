"""Core logic for a small SQLite-backed expense tracker."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    spent_on    TEXT    NOT NULL,          -- ISO date, e.g. 2026-10-08
    amount_p    INTEGER NOT NULL CHECK (amount_p > 0),  -- stored in pence
    category    TEXT    NOT NULL,
    description TEXT    NOT NULL DEFAULT ''
);
"""


@dataclass(frozen=True)
class Expense:
    id: int
    spent_on: date
    amount: Decimal
    category: str
    description: str


def parse_amount(text: str) -> int:
    """Turn a string like '12.50' or '£3' into whole pence.

    Money is stored as integer pence to avoid floating-point rounding errors.
    """
    cleaned = text.strip().lstrip("£").replace(",", "")
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        raise ValueError(f"Not a valid amount: {text!r}") from None
    if value <= 0:
        raise ValueError("Amount must be greater than zero")
    if value.as_tuple().exponent < -2:
        raise ValueError("Amount can have at most two decimal places")
    return int(value * 100)


class ExpenseTracker:
    def __init__(self, db_path: str | Path = "expenses.db") -> None:
        self.conn = sqlite3.connect(str(db_path))
        self.conn.execute(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "ExpenseTracker":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def add(self, amount: str, category: str, description: str = "",
            spent_on: date | None = None) -> int:
        """Record an expense and return its id."""
        pence = parse_amount(amount)
        category = category.strip().lower()
        if not category:
            raise ValueError("Category cannot be empty")
        spent_on = spent_on or date.today()
        cur = self.conn.execute(
            "INSERT INTO expenses (spent_on, amount_p, category, description) "
            "VALUES (?, ?, ?, ?)",
            (spent_on.isoformat(), pence, category, description.strip()),
        )
        self.conn.commit()
        return cur.lastrowid

    def delete(self, expense_id: int) -> bool:
        cur = self.conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.conn.commit()
        return cur.rowcount == 1

    def list(self, month: str | None = None, category: str | None = None) -> list[Expense]:
        """List expenses, optionally filtered by month ('YYYY-MM') and category."""
        query = "SELECT id, spent_on, amount_p, category, description FROM expenses WHERE 1=1"
        params: list[str] = []
        if month:
            query += " AND substr(spent_on, 1, 7) = ?"
            params.append(month)
        if category:
            query += " AND category = ?"
            params.append(category.strip().lower())
        query += " ORDER BY spent_on, id"
        return [
            Expense(row[0], date.fromisoformat(row[1]), Decimal(row[2]) / 100, row[3], row[4])
            for row in self.conn.execute(query, params)
        ]

    def summary(self, month: str) -> dict[str, Decimal]:
        """Total spent per category for a month, largest first."""
        rows = self.conn.execute(
            "SELECT category, SUM(amount_p) FROM expenses "
            "WHERE substr(spent_on, 1, 7) = ? GROUP BY category ORDER BY SUM(amount_p) DESC",
            (month,),
        )
        return {cat: Decimal(total) / 100 for cat, total in rows}
