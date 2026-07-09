"""Generate workflow visualization artifacts from the compiled LangGraph."""

import argparse
from pathlib import Path

from content_agents.graph.workflow import app

DEFAULT_OUTPUT = Path("docs/assets/workflow.mmd")


def export_workflow_mermaid(output_path: Path = DEFAULT_OUTPUT) -> str:
    """Export the compiled workflow graph as Mermaid text."""
    mermaid = app.get_graph().draw_mermaid()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(mermaid, encoding="utf-8")
    return mermaid


def export_workflow_png(output_path: Path) -> bool:
    """Best-effort PNG export. Returns False if rendering is unavailable."""
    try:
        png_bytes = app.get_graph().draw_mermaid_png()
    except Exception:
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(png_bytes)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate workflow visualization artifacts from the compiled graph."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Mermaid output path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--png",
        type=Path,
        default=None,
        help="Optional PNG output path (best-effort; may fail without render deps)",
    )
    args = parser.parse_args()

    mermaid = export_workflow_mermaid(args.output)
    print(f"Wrote Mermaid graph to {args.output} ({len(mermaid)} bytes)")

    if args.png is not None:
        if export_workflow_png(args.png):
            print(f"Wrote PNG graph to {args.png}")
        else:
            print("PNG export skipped (render dependencies unavailable)")


if __name__ == "__main__":
    main()
