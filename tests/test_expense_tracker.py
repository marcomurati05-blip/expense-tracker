import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from expense_tracker import ExpenseTracker, parse_amount  # noqa: E402


class ParseAmountTests(unittest.TestCase):
    def test_converts_pounds_to_pence(self):
        self.assertEqual(parse_amount("12.50"), 1250)
        self.assertEqual(parse_amount("£3"), 300)
        self.assertEqual(parse_amount("1,200.99"), 120099)

    def test_rejects_bad_amounts(self):
        for bad in ["abc", "0", "-5", "1.999"]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                parse_amount(bad)


class ExpenseTrackerTests(unittest.TestCase):
    def setUp(self):
        self.tracker = ExpenseTracker(":memory:")
        self.tracker.add("10.00", "Food", "Lunch", date(2026, 10, 1))
        self.tracker.add("2.50", "transport", "Bus", date(2026, 10, 2))
        self.tracker.add("5.25", "food", "Coffee", date(2026, 10, 3))
        self.tracker.add("100", "rent", "Old month", date(2026, 9, 30))

    def tearDown(self):
        self.tracker.close()

    def test_list_filters_by_month(self):
        october = self.tracker.list(month="2026-10")
        self.assertEqual([e.description for e in october], ["Lunch", "Bus", "Coffee"])

    def test_category_is_case_insensitive(self):
        food = self.tracker.list(category="FOOD")
        self.assertEqual(len(food), 2)

    def test_summary_groups_and_sorts(self):
        summary = self.tracker.summary("2026-10")
        self.assertEqual(list(summary), ["food", "transport"])
        self.assertEqual(summary["food"], Decimal("15.25"))

    def test_delete(self):
        first_id = self.tracker.list()[0].id
        self.assertTrue(self.tracker.delete(first_id))
        self.assertFalse(self.tracker.delete(first_id))

    def test_empty_category_rejected(self):
        with self.assertRaises(ValueError):
            self.tracker.add("1", "   ")


if __name__ == "__main__":
    unittest.main()
