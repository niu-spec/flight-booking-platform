# -*- coding: utf-8 -*-
"""Render PlantUML sequence diagram to PNG."""
from pathlib import Path

from plantuml import PlantUML

ROOT = Path(__file__).resolve().parent.parent
PUML = ROOT / "docs" / "支付并出票顺序图.puml"
OUT = ROOT / "docs" / "支付并出票顺序图.png"


def render_via_server(source: str, out_path: Path) -> None:
    server = PlantUML(url="http://www.plantuml.com/plantuml/img/")
    png_bytes = server.processes(source)
    out_path.write_bytes(png_bytes)


def main():
    if not PUML.is_file():
        raise SystemExit(f"Missing source: {PUML}")
    source = PUML.read_text(encoding="utf-8")
    render_via_server(source, OUT)
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
