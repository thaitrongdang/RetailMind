"""Show invoice-line granularity and a strict prediction cutoff."""

from datetime import datetime


CUTOFF = datetime.fromisoformat("2011-09-01T00:00:00")
ROWS = [
    ("A100", "C1", "SKU-A", "2011-08-31T23:00:00"),
    ("A100", "C1", "SKU-B", "2011-08-31T23:00:00"),
    ("A101", "C1", "SKU-A", "2011-08-31T23:30:00"),
    ("A102", "C2", "SKU-C", "2011-09-01T00:00:00"),
    ("A103", "C1", "SKU-B", "2011-09-05T10:00:00"),
]


def main() -> None:
    history = [row for row in ROWS if datetime.fromisoformat(row[3]) < CUTOFF]
    outcomes = [row for row in ROWS if datetime.fromisoformat(row[3]) >= CUTOFF]
    invoices = {row[0] for row in history}
    customers = {row[1] for row in history}
    interactions = {(row[1], row[2]) for row in history}

    print(f"History lines: {len(history)}")
    print(f"History invoices: {len(invoices)}")
    print(f"History customers: {len(customers)}")
    print(f"Distinct customer-product interactions: {len(interactions)}")
    print(f"Future lines at or after cutoff: {len(outcomes)}")
    print(f"C1 previously bought SKU-B: {('C1', 'SKU-B') in interactions}")


if __name__ == "__main__":
    main()
