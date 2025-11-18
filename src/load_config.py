from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_model_config():
    config_path = ROOT / "config" / "model.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_prompt(prompt_file: str) -> str:
    prompt_path = ROOT / prompt_file
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    with prompt_path.open("r", encoding="utf-8") as f:
        return f.read()
