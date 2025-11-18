import json
from datetime import date
from pathlib import Path

from update_metrics import append_row

ROOT = Path(__file__).resolve().parents[1]


def main():
    today_str = date.today().isoformat()
    inp = input(f"Date of bet to record (YYYY-MM-DD) [{today_str}]: ").strip()
    target_date = inp or today_str

    pred_path = ROOT / "data" / "predictions" / f"{target_date}.json"
    if not pred_path.exists():
        print(f"No prediction file found for {target_date} at {pred_path}")
        return

    with pred_path.open("r", encoding="utf-8") as f:
        pred = json.load(f)

    sel = pred.get("selection", {})
    course = sel.get("course")
    time_str = sel.get("time")
    horse = sel.get("horse")
    odds_decimal = float(sel.get("odds_decimal", 0))

    if not all([course, time_str, horse, odds_decimal]):
        print("Prediction file is missing some selection fields.")
        return

    print(f"Selection for {target_date}: {course} {time_str} - {horse} @ {odds_decimal}")
    yn = input("Did it win? (y/n): ").strip().lower()
    if yn not in ("y", "n"):
        print("Please answer 'y' or 'n'.")
        return

    won = yn == "y"

    sp_in = input(f"SP decimal odds (press Enter to use {odds_decimal}): ").strip()
    if sp_in:
        try:
            sp_decimal = float(sp_in)
        except ValueError:
            print("Invalid number for SP odds.")
            return
    else:
        sp_decimal = odds_decimal

    stake = 1.0
    profit = sp_decimal - 1.0 if won else -stake
    result_str = "win" if won else "lose"

    result_data = {
        "date": target_date,
        "selection": sel,
        "reasoning": pred.get("reasoning", ""),
        "result": {
            "won": won,
            "sp_decimal": sp_decimal,
            "stake_units": stake,
            "profit_units": profit,
        },
    }

    out_path = ROOT / "data" / "results" / f"{target_date}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2)

    append_row(
        date_str=target_date,
        course=course,
        time_str=time_str,
        horse=horse,
        odds_decimal=sp_decimal,
        result_str=result_str,
        profit_units=profit,
    )

    print("\n--- Result saved and metrics updated ---")
    print(f"Results file: {out_path}")
    print("Check data/metrics/summary.csv for updated ROI.")


if __name__ == "__main__":
    main()
