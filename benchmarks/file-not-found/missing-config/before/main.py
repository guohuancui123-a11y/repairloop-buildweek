from pathlib import Path

print(Path("generated/config.txt").read_text(encoding="utf-8"))
