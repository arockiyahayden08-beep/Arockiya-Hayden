"""Quick local verification for ComicCraft."""
from pathlib import Path
import compileall

ROOT = Path(__file__).resolve().parent
required = [
    "app/main.py", "app/routes.py", "app/schemas.py",
    "app/services/workflow.py", "app/services/image_generator.py",
    "templates/index.html", "templates/comic_preview.html",
    "static/css/app.css", "requirements.txt", ".env.example",
]
missing = [p for p in required if not (ROOT / p).exists()]
if missing:
    raise SystemExit("Missing files: " + ", ".join(missing))
if not compileall.compile_dir(str(ROOT / "app"), quiet=1):
    raise SystemExit("Python compilation failed")
print("ComicCraft project structure and Python compilation: OK")
