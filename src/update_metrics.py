import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS_FILE = ROOT / "data" / "metrics" / "summary.csv"


def append_row(date_str: str,
               course: str,
               time_str: str,
               horse: str,
               odds_decimal: float,
               result_str: str,
               profit_units: float):
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Ensure header exists and read previous rows
    bets_so_far = 0
    prev_cum = 0.0

    if METRICS_FILE.exists():
        with METRICS_FILE.open("r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        if rows:
            header = rows[0]
            data_rows = rows[1:]
            if data_rows:
                last = data_rows[-1]
                try:
                    prev_cum = float(last[7])
                except (ValueError, IndexError):
                    prev_cum = 0.0
                bets_so_far = len(data_rows)
    else:
        # create file with header
        with METRICS_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "date",
                "course",
                "time",
                "horse",
                "odds_decimal",
                "result",
                "profit_units",
                "cum_profit_units",
                "roi_total",
            ])

    new_cum = prev_cum + float(profit_units)
    new_count = bets_so_far + 1 if bets_so_far is not None else 1
    roi_total = new_cum / new_count if new_count > 0 else 0.0

    with METRICS_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            date_str,
            course,
            time_str,
            horse,
            f"{float(odds_decimal):.4f}",
            result_str,
            f"{float(profit_units):.4f}",
            f"{new_cum:.4f}",
            f"{roi_total:.4f}",
        ])


if __name__ == "__main__":
    print(
        "This module is normally called from fetch_results.py\n"
        "It does not do anything useful when run directly."
    )
