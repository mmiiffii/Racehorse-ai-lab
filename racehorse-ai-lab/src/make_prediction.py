import json
import os
from datetime import date, datetime
from pathlib import Path

from openai import OpenAI

from load_config import load_model_config, load_prompt

ROOT = Path(__file__).resolve().parents[1]


def load_candidates(date_str: str):
    path = ROOT / "data" / "raw" / "racecards" / f"{date_str}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"No candidates file for {date_str} found at {path}.\n"
            f"Run `python src/fetch_racecards.py` first, then edit the file."
        )
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if "candidates" not in data or not data["candidates"]:
        raise ValueError(f"File {path} has no 'candidates' list or it's empty.")

    return data, path


def validate_selection(selection, candidates):
    required_keys = {"course", "time", "horse", "odds_decimal"}
    missing = required_keys - set(selection.keys())
    if missing:
        raise ValueError(f"Model selection is missing keys: {missing}")

    # Ensure the model picked one of the supplied candidates
    for c in candidates:
        if (
            c.get("course") == selection["course"]
            and c.get("time") == selection["time"]
            and c.get("horse") == selection["horse"]
        ):
            return

    raise ValueError(
        "Model selected a horse that is not in the candidates list. "
        "This run will not be saved to avoid fake data."
    )


def main():
    # Ask user for date (default = today)
    today_str = date.today().isoformat()
    inp = input(f"Date for prediction (YYYY-MM-DD) [{today_str}]: ").strip()
    target_date = inp or today_str

    candidates_data, candidates_path = load_candidates(target_date)
    candidates = candidates_data["candidates"]

    config = load_model_config()
    prompt = load_prompt(config["prompt_file"])

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not set.\n"
            "In Codespaces, run: export OPENAI_API_KEY=your_key_here"
        )

    client = OpenAI(api_key=api_key)

    system_msg = (
        "You are an expert UK horse-racing analyst. "
        "You must choose exactly one value bet of the day from the candidate bets. "
        "Do not invent new horses or races. Only choose from the candidates JSON."
    )

    user_content = (
        prompt.strip()
        + "\n\n"
        + f"Today's date is {target_date}.\n\n"
        + "Here is today's candidate bets JSON:\n"
        + json.dumps(candidates_data, indent=2)
    )

    print("\nCalling OpenAI API...")

    completion = client.chat.completions.create(
        model=config["model_name"],
        temperature=float(config.get("temperature", 0.2)),
        max_tokens=int(config.get("max_tokens", 600)),
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_content},
        ],
    )

    content = completion.choices[0].message.content
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        print("Model did not return valid JSON. Raw content was:")
        print(content)
        raise e

    # Force the date to match our target date for consistency
    parsed["date"] = target_date

    selection = parsed.get("selection")
    reasoning = parsed.get("reasoning", "").strip()

    if not selection:
        raise ValueError("Model response has no 'selection' field.")

    validate_selection(selection, candidates)

    # Save prediction
    out_path = ROOT / "data" / "predictions" / f"{target_date}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    output = {
        "date": target_date,
        "candidates_file": str(candidates_path.relative_to(ROOT)),
        "selection": selection,
        "reasoning": reasoning,
        "meta": {
            "model": completion.model,
            "temperature": config.get("temperature", 0.2),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "prompt_file": config["prompt_file"],
        },
    }

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("\n--- Prediction saved ---")
    print(f"File: {out_path}")
    print(
        f"Selection for {target_date}: "
        f"{selection['course']} {selection['time']} - "
        f"{selection['horse']} @ {selection['odds_decimal']}"
    )
    print("\nReasoning:")
    print(reasoning)


if __name__ == "__main__":
    main()
