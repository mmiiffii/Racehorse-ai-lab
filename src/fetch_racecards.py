import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    today_str = date.today().isoformat()
    src = ROOT / "data" / "raw" / "racecards" / "example_candidates.json"
    dst = ROOT / "data" / "raw" / "racecards" / f"{today_str}.json"

    if not src.exists():
        raise FileNotFoundError(f"Example candidates file not found: {src}")

    if dst.exists():
        print(f"Candidate file for today already exists: {dst}")
        print("Open it in the editor and update the horses for today's races.")
        return

    with src.open("r", encoding="utf-8") as f:
        data = json.load(f)

    data["date"] = today_str

    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Created {dst}")
    print("Now open this file in the Codespaces editor and replace the example horses")
    print("with today's real horses, odds and notes. Keep the structure the same.")


if __name__ == "__main__":
    main()
