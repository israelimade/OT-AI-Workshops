import argparse
from pathlib import Path
from datetime import date as _date

SECTION_KEYS = {
    "presenting": "PRESENTING_CONCERNS",
    "history": "HISTORY",
    "observations": "OBSERVATIONS",
    "functional": "FUNCTIONAL",
    "cognitive": "COGNITIVE",
    "environment": "ENVIRONMENT",
    "risks": "RISKS",
    "reasoning": "REASONING",
    "recommendations": "RECOMMENDATIONS",
    "goals": "GOALS",
    "plan": "PLAN",
}

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def parse_notes(raw: str) -> dict:
    """
    Very simple parser:
    Lines like 'presenting: ...' map to the template section 'PRESENTING_CONCERNS'.
    Everything else is ignored. This keeps privacy and governance simple.
    """
    data = {v: "" for v in SECTION_KEYS.values()}
    for line in raw.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip().lower()
        val = val.strip()
        mapped = SECTION_KEYS.get(key)
        if mapped:
            # Preserve bullet feel if multiple lines per section
            if data[mapped]:
                data[mapped] += "\n- " + val
            else:
                data[mapped] = "- " + val if val else ""
    return data

def fill_template(template: str, fields: dict) -> str:
    out = template
    for k, v in fields.items():
        out = out.replace("{{" + k + "}}", v if v else "To be completed")
    return out

def todays_iso() -> str:
    return _date.today().isoformat()

def main():
    parser = argparse.ArgumentParser(description="Generate a first-draft OT report from notes.")
    parser.add_argument("--input", required=True, help="Path to notes txt file")
    parser.add_argument("--output", required=True, help="Path to output report md")
    parser.add_argument("--template", required=True, help="Path to template md")
    parser.add_argument("--patient", required=True, help="Patient initials or code")
    parser.add_argument("--date", default=todays_iso(), help="Report date ISO, default is today")
    parser.add_argument("--therapist", required=True, help="Therapist name")
    parser.add_argument("--service", required=True, help="Service name")
    args = parser.parse_args()

    raw_notes = read_text(Path(args.input))
    template = read_text(Path(args.template))

    sections = parse_notes(raw_notes)

    fields = {
        "PATIENT": args.patient,
        "DATE": args.date,
        "THERAPIST": args.therapist,
        "SERVICE": args.service,
        **sections,
    }

    report = fill_template(template, fields)
    write_text(Path(args.output), report)
    print(f"Report written to {args.output}")

if __name__ == "__main__":
    main()
